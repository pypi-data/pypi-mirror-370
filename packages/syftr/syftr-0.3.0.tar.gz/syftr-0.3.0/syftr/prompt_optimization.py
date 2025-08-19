import argparse
import asyncio
import json
import os
import typing as T

import litellm
import llama_index.core.instrumentation as instrument
import optuna
import ray
from aiolimiter import AsyncLimiter
from llama_index.core.evaluation import CorrectnessEvaluator
from llama_index.core.llms.function_calling import FunctionCallingLLM
from openai import AzureOpenAI
from opto.optimizers import OptoPrime
from opto.trace.bundle import bundle
from opto.trace.nodes import ParameterNode

from syftr import flows
from syftr.configuration import cfg
from syftr.core import QAPair
from syftr.evaluation import evaluation
from syftr.llm import get_llm
from syftr.logger import logger
from syftr.optuna_helper import get_pareto_df
from syftr.ray.utils import ray_init
from syftr.studies import StudyConfig, get_default_study_name
from syftr.tuner.qa_tuner import build_flow, eval_dataset

dispatcher = instrument.get_dispatcher()
CorrectnessEvaluator.evaluate = dispatcher.span(CorrectnessEvaluator.evaluate)  # type: ignore
CorrectnessEvaluator.aevaluate = dispatcher.span(CorrectnessEvaluator.aevaluate)  # type: ignore

EVAL_LLM = "gpt-4o-mini"
OPTIMIZER_LLM = "gpt-4o-std"
PARAMS_TO_OPTMIZE = [
    "template",
    "dataset_description",
]


async def quick_eval(
    flow: flows.Flow,
    eval_llm: FunctionCallingLLM,
    dataset: T.List[QAPair],
    rate_limiter: AsyncLimiter,
) -> T.Tuple[float, str]:
    """Evaluates selected flow using eval_llm on a dataset of choice.
    A lightweight evaluation function to be used within the prompt optimization loop.
    """
    evaluator = CorrectnessEvaluator(eval_llm)
    raw_responses = await asyncio.gather(
        *[evaluation.agenerate_pair(qa_pair, flow, rate_limiter) for qa_pair in dataset]
    )
    responses = [raw_response[0] for raw_response in raw_responses]
    eval_results = await asyncio.gather(
        *[
            evaluation.aevaluate_pair(
                qa_pair=qa_pair,
                response=response,  # type: ignore
                evaluator=evaluator,
                rate_limiter=rate_limiter,
            )
            for qa_pair, response in zip(dataset, responses)
            if response
        ]
    )
    results = [
        int(res[0].passing)  # type: ignore
        for res in eval_results
        if res[0].passing is not None  # type: ignore
    ]
    evals = [res[0].feedback for res in eval_results if not res[0].passing]  # type: ignore
    if results:
        return sum(results) / len(results), "\n".join(evals)  # type: ignore
    return 0.0, "The evluation has failed, the results are incorrect."


class TracedFlow:
    def __init__(self, flow):
        object.__setattr__(self, "_flow", flow)
        self.template = ParameterNode(
            self._flow.template,
            description="A prompt for Q&A bot with instructions for complete and accurate answers",
        )
        self.dataset_description = ParameterNode(
            self._flow.dataset_description,
            description="A description of the dataset with the grounding data",
        )

    def __getattr__(self, name):
        return getattr(self._flow, name)


def optimize_prompt(
    flow: flows.Flow,
    optimizer_llm: str,
    eval_llm: str,
    train: T.List[QAPair],
    test: T.List[QAPair],
    rate_limiter: AsyncLimiter,
    num_epochs: int = 5,
) -> flows.Flow:
    """The main prompt optimization function for a flow.
    Uses Trace library with an optimizer LLM to get better prompts using train and test datasets.
    """
    llm = get_llm(optimizer_llm)
    assert isinstance(llm, AzureOpenAI), (
        "Prompt optimization only supports Azure OpenAI"
    )
    evaluator_llm = get_llm(eval_llm)
    logger.info("Evaluating pareto flow on test dataset before optimization...")
    pre_test_acc, _ = asyncio.run(quick_eval(flow, evaluator_llm, test, rate_limiter))
    logger.info("Pre-optimization accuracy on test: %f", pre_test_acc)
    os.environ["AZURE_API_KEY"] = llm.api_key
    os.environ["AZURE_API_BASE"] = llm.azure_endpoint  # type: ignore
    os.environ["AZURE_API_VERSION"] = llm.api_version  # type: ignore
    litellm_model = f"azure/{llm.model}"  # type: ignore
    os.environ["TRACE_LITELLM_MODEL"] = litellm_model

    @bundle()
    def merge_nodes(*args):
        """This function connects Trace nodes that are specified in args.
        For some reason Trace does not catch the usage of annotated templates inside
        our evaluation function and this function takes precomputed accuracy and connects
        specified nodes for optmization.
        """
        for arg in args:
            _ = arg
        nonlocal curr_accuracy
        return curr_accuracy

    tflow = TracedFlow(flow)
    existing_flow_attrs = [arg for arg in PARAMS_TO_OPTMIZE if hasattr(flow, arg)]
    opt_args = [getattr(tflow, arg) for arg in existing_flow_attrs]
    optimizer = OptoPrime(opt_args)
    param_results = []
    for n_epoch in range(1, num_epochs + 1):
        logger.info("Starting optimization epoch %d", n_epoch)
        curr_accuracy, evals = asyncio.run(
            quick_eval(flow, evaluator_llm, train, rate_limiter)
        )
        output = merge_nodes(*opt_args)
        logger.info("Accuracy on epoch %d: %f", n_epoch, curr_accuracy)
        raw_summary = litellm.completion(
            model=litellm_model,
            messages=[
                {
                    "content": f"You are presented with a feedback from a question answering session. Summarize it briefly: {evals}",
                    "role": "user",
                }
            ],
        )
        eval_summary = raw_summary.choices[0].message.content
        feedback = (
            f"The accuracy of question answering session is {curr_accuracy}."
            f"Evaluation summary of question answering session is '{eval_summary}'"
            f"Modify the prompts to help the LLM produce more accurate answers to the provided questions."
            f"Make sure template arguments are in place."
        )
        optimizer.zero_feedback()
        optimizer.backward(output, feedback)
        try:
            logger.info("Generating a new prompt on epoch %s", n_epoch)
            optimizer.step(verbose=True)
        except litellm.exceptions.ContentPolicyViolationError:
            logger.exception("Prompt optimizer hit content policy violation error")
            continue

        for attr in existing_flow_attrs:
            setattr(flow, attr, getattr(tflow, attr).data)

        param_results.append((curr_accuracy, flow))

    _, argmax_flow = max(param_results, key=lambda x: x[0])
    logger.info("Evaluating pareto flow on test dataset after optimization...")

    post_test_acc, _ = asyncio.run(
        quick_eval(argmax_flow, evaluator_llm, test, rate_limiter)
    )
    logger.info("Post-optimiation accuracy on test: %f", post_test_acc)
    return argmax_flow


def opt_flow(
    flow_params: T.Dict[str, T.Any],
    study_config: StudyConfig,
    new_study: optuna.Study,
    parent_number: int,
):
    """Prompt optimization workflow function.
    Gets a pareto flow specified by flow_params, runs prompt optimization and saves it
    in a new study.
    """
    logger.info("Loading training and test datasets for %s", study_config.name)
    train = list(study_config.dataset.iter_examples(partition="train"))
    train = train[: study_config.optimization.num_prompt_optimization_batch]
    test = list(study_config.dataset.iter_examples(partition="test"))
    test = test[: study_config.optimization.num_prompt_optimization_batch]
    logger.info(
        "Training subset size: %d, test subset size: %s",
        len(train),
        len(test),
    )
    rate_limiter = AsyncLimiter(
        study_config.optimization.rate_limiter_max_coros,
        study_config.optimization.rate_limiter_period,
    )
    logger.info("Building pareto flow from params: %s", flow_params)
    try:
        flow = build_flow(study_config=study_config, params=flow_params)
    except Exception:
        logger.exception("Failed to build flow from %s", flow_params)
        return
    logger.info("Optimizing the prompt...")
    try:
        flow = optimize_prompt(
            flow, OPTIMIZER_LLM, EVAL_LLM, train, test, rate_limiter, num_epochs=2
        )
    except Exception:
        logger.exception("Failed to optimize prompt for flow %s", flow)
        return
    logger.info("Resulting optimized flow: %s", flow)
    logger.info("Evaluating updated flow and attaching it to the trial...")
    try:
        eval_results = eval_dataset(
            study_config, study_config.dataset, flow, study_config.evaluation.mode
        )
    except Exception:
        logger.exception("Failed to evaluate resulting flow %s", flow)
        return
    obj1 = eval_results[study_config.optimization.objective_1_name]
    obj2 = eval_results[study_config.optimization.objective_2_name]
    distributions = study_config.search_space.build_distributions(params=flow_params)
    logger.info("Saving optimized prompt...")
    if "enforce_full_evaluation" in flow_params:
        flow_params.pop("enforce_full_evaluation")
    new_trial = optuna.create_trial(
        values=[obj1, obj2],
        params=flow_params,
        distributions=distributions,
        state=optuna.trial.TrialState.COMPLETE,
    )
    new_trial.set_user_attr("parent_number", parent_number)
    for param in PARAMS_TO_OPTMIZE:
        new_trial.set_user_attr(f"optimized_{param}", getattr(flow, param))
    new_study.add_trial(new_trial)
    logger.info("Done optimizing prompt for %s", flow_params)


@ray.remote
def opt_flow_remote(
    flow_params: T.Dict[str, T.Any],
    study_config: StudyConfig,
    new_study: optuna.Study,
    parent_number: int,
):
    """A wrapper for running prompt optimization on a Ray cluster."""
    return opt_flow(flow_params, study_config, new_study, parent_number)


def run_pareto_flows_prompt_optimization(study_path: str, remote: bool = False):
    """
    Main prompt optimzation workflow function.

    Reads study config from a path and initiates a remote or local mode of prompt optmization.
    """
    logger.info("Loading study config from file %s", study_path)
    study_config = StudyConfig.from_file(study_path)
    logger.info("Loading pareto flows for study %s", study_config.name)
    storage = cfg.database.get_optuna_storage()
    study = optuna.load_study(
        study_name=study_config.name,
        storage=storage,
    )
    df_pareto = get_pareto_df(study_config, success_rate=0.5)
    new_study_name = f"{study_config.name}_prompt_optimization"
    logger.info("Creating new study %s for optimized prompts...", new_study_name)
    po_study = optuna.create_study(
        study_name=new_study_name,
        directions=study.directions,
        storage=storage,
        load_if_exists=True,
    )
    logger.info("Running prompt optimization...")
    if remote:
        opts: T.List[T.Any] = []
        for _, row in df_pareto.iterrows():
            flow_params = json.loads(row["user_attrs_flow"])
            parent_number = row["number"]
            opts.append(
                opt_flow_remote.remote(
                    flow_params, study_config, po_study, parent_number
                )
            )
        ray.get(opts)
    else:
        for _, row in df_pareto.iterrows():
            parent_number = row["number"]
            flow_params = json.loads(row["user_attrs_flow"])
            opt_flow(flow_params, study_config, po_study, parent_number)
    logger.info("Done")


def run_opt(study_path: str, remote: bool):
    """Main workflow wrapper."""
    if remote:
        ray_init()
    run_pareto_flows_prompt_optimization(study_path, remote=remote)


def main():
    """An argument parser."""
    parser = argparse.ArgumentParser()
    default = get_default_study_name()
    parser.add_argument(
        "--study-config",
        help=f"Path to study config yaml (default: {default})",
        default=default,
    )
    parser.add_argument(
        "--remote",
        help="Run the optimization remotely",
        default=False,
        action="store_true",
    )
    args = parser.parse_args()
    run_opt(
        study_path=args.study_config,
        remote=args.remote,
    )


if __name__ == "__main__":
    main()
