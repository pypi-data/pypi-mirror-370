from syftr.studies import SearchSpace
from syftr.validation import (
    has_valid_additional_context_params,
    has_valid_base_rag_params,
    has_valid_few_shot_params,
    has_valid_hyde_params,
    has_valid_minimum_params,
    has_valid_rag_embedding_model_params,
    has_valid_rag_fusion_params,
    has_valid_rag_reranker_params,
    has_valid_splitter_params,
    has_valid_unique_params,
)


def test_params():
    """Simple unit test that must be updated whenever params update.

    Serves as tested documentation
    """
    ss = SearchSpace()
    params = ss.param_names()
    for param in sorted(params):
        print(f'"{param}",')
    assert sorted(params) == sorted(
        [
            "additional_context_enabled",
            "additional_context_num_nodes",
            "coa_enable_calculator",
            "critique_agent_llm_name",
            "critique_agent_llm_temperature",
            "critique_agent_llm_top_p",
            "critique_agent_llm_use_reasoning",
            "few_shot_embedding_model",
            "few_shot_enabled",
            "few_shot_top_k",
            "hyde_enabled",
            "hyde_llm_name",
            "hyde_llm_temperature",
            "hyde_llm_top_p",
            "hyde_llm_use_reasoning",
            "lats_max_rollouts",
            "lats_num_expansions",
            "rag_embedding_model",
            "rag_fusion_mode",
            "rag_hybrid_bm25_weight",
            "rag_method",
            "rag_mode",
            "rag_query_decomposition_enabled",
            "rag_query_decomposition_llm_name",
            "rag_query_decomposition_llm_temperature",
            "rag_query_decomposition_llm_top_p",
            "rag_query_decomposition_llm_use_reasoning",
            "rag_query_decomposition_num_queries",
            "rag_top_k",
            "reflection_agent_llm_name",
            "reflection_agent_llm_temperature",
            "reflection_agent_llm_top_p",
            "reflection_agent_llm_use_reasoning",
            "reranker_enabled",
            "reranker_llm_name",
            "reranker_llm_temperature",
            "reranker_llm_top_p",
            "reranker_llm_use_reasoning",
            "reranker_top_k",
            "response_synthesizer_llm_name",
            "response_synthesizer_llm_temperature",
            "response_synthesizer_llm_top_p",
            "response_synthesizer_llm_use_reasoning",
            "splitter_chunk_exp",
            "splitter_chunk_overlap_frac",
            "splitter_method",
            "subquestion_engine_llm_name",
            "subquestion_engine_llm_temperature",
            "subquestion_engine_llm_top_p",
            "subquestion_engine_llm_use_reasoning",
            "subquestion_response_synthesizer_llm_name",
            "subquestion_response_synthesizer_llm_temperature",
            "subquestion_response_synthesizer_llm_top_p",
            "subquestion_response_synthesizer_llm_use_reasoning",
            "template_name",
        ]
    )


def test_minimum_params(search_space_and_trial_params):
    assert has_valid_minimum_params(*search_space_and_trial_params), (
        "Minimum parameters required are invalid"
    )


def test_few_shot_params(search_space_and_trial_params):
    assert has_valid_few_shot_params(*search_space_and_trial_params), (
        "Few shot parameters are invalid"
    )


def test_base_rag_params(search_space_and_trial_params):
    assert has_valid_base_rag_params(*search_space_and_trial_params), (
        "Base RAG parameters are invalid"
    )


def test_rag_embedding_model_params(search_space_and_trial_params):
    assert has_valid_rag_embedding_model_params(*search_space_and_trial_params), (
        "RAG embedding model parameters are invalid"
    )


def test_fusion_params(search_space_and_trial_params):
    assert has_valid_rag_fusion_params(*search_space_and_trial_params), (
        "Fusion parameters are invalid"
    )


def test_reranker_params(search_space_and_trial_params):
    assert has_valid_rag_reranker_params(*search_space_and_trial_params), (
        "Reranker parameters are invalid"
    )


def test_hyde_params(search_space_and_trial_params):
    assert has_valid_hyde_params(*search_space_and_trial_params), (
        "Hyde params are invalid"
    )


def test_splitter_params(search_space_and_trial_params):
    assert has_valid_splitter_params(*search_space_and_trial_params), (
        "Splitter params are invalid"
    )


def test_out_of_distribution_rag_top_k(search_space_and_trial_params):
    search_space_and_trial_params[1]["rag_top_k"] = int(1e6)
    is_valid = has_valid_rag_embedding_model_params(*search_space_and_trial_params)
    assert (
        is_valid
        if search_space_and_trial_params[1]["rag_mode"] == "no_rag"
        else not is_valid
    ), "Out-of-distribution check for 'rag_top_k' failed"


def test_additional_context_params(search_space_and_trial_params):
    assert has_valid_additional_context_params(*search_space_and_trial_params), (
        "Additional context params are invalid"
    )


def test_has_valid_unique_params(
    search_space_and_trial_params,
):
    assert has_valid_unique_params(
        *search_space_and_trial_params,
        "critique_rag_agent",
        [
            "critique_agent_llm_name",
            "reflection_agent_llm_name",
        ],
    ), (
        f"Parameters for RAG mode {search_space_and_trial_params[1]['rag_mode']} are in conflict with CritiqueRAG"
    )

    assert has_valid_unique_params(
        *search_space_and_trial_params,
        "lats_rag_agent",
        [
            "lats_max_rollouts",
            "lats_num_expansions",
        ],
    ), (
        f"Parameters for RAG mode {search_space_and_trial_params[1]['rag_mode']} are in conflict with LATS"
    )
