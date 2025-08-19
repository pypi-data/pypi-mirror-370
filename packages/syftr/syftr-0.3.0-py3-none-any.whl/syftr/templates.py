import json
import typing as T

from llama_index.core.prompts import RichPromptTemplate

from syftr.configuration import cfg
from syftr.logger import logger

# Default prompt components
_DEFAULT_INSTRUCTIONS = """
    You are a helpful assistant.
    Answer the provided question given the context information and not prior knowledge.
"""
_CONTEXT = """
    Context information is below.
    ---------------------{context_str}---------------------
"""
_QUERY_STR = """
    Question: {query_str}
    Answer:
"""

# Concise prompt components.
_CONCISE_INSTRUCTIONS = """
    You are a helpful assistant.
    Answer the provided question given the context information and not prior knowledge.
    Be concise!
"""

# CoT prompt components.
_COT_INSTRUCTIONS = """
    You are a helpful assistant.
    Answer the provided question given the context step-by-step.
"""

# Finance expert
_FINANCE_EXPERT_INSTRUCTIONS = """
    You are an expert financial advisor, providing guidance on financial analysis and managing money.
    You need to answer the provided question given the context information and not prior knowledge.
    You are also provided with the additional knowledge you can use for performing the analysis:

    FINANCIAL SYNONYMS
    ==================
    - "(Consolidated) Balance Sheet(s)",
      "Statement(s) of (Consolidated) Financial Position", "(Consolidated) Statement(s) of Financial Position"

    - "(Consolidated) Cash Flow(s) Statement(s)", "(Consolidated) Statement(s) of Cash Flows"

    - "(Consolidated) Income Statement(s)", "Statement(s) of (Consolidated) Income", "(Consolidated) Statement(s) of Income",
      "(Consolidated) Profit-and-Loss Statement(s)", "(Consolidated) P&L (Statement(s))",
      "(Consolidated) Earnings Statement(s)", "Statement(s) of (Consolidated) Earnings", "(Consolidated) Statement(s) of Earnings",
      "(Consolidated) Operations Statement(s)", "Statement(s) of (Consolidated) Operations", "(Consolidated) Statement(s) of Operations"

    Balance-Sheet Line-Item Synonyms
    --------------------------------

    - "Total Assets", "TA(s)"

    - "(Net) Fixed Assets", "(Net) FA(s)",
      "(Net) Property, Plant & Equipment", "(Net) PP&E", "(Net) PPNE",
      "(Net) Property & Equipment", "(Net) Plant & Equipment", "(Net) Property, Equipment & Intangibles"

    - "(Total) (Net) Inventory", "(Total) (Net) Inventories",
      "(Total) (Net) Merchandise Inventory", "(Total) (Net) Merchandise Inventories"

    - "(Net) Accounts Receivable", "(Net) AR", "(Net) (Trade) Receivables"

    - "(Net) Accounts Payable", "(Net) AP"


    Cash-Flow-Statement Line-Item Synonyms
    --------------------------------------

    - "(Net) Cash (Flows) from Operations", "(Net) Cash (Flows) from Operating Activities", "(Net) Operating Cash Flows"

    - "(Net) Cash (Flows) from Investments", "(Net) Cash (Flows) from Investing Activities", "(Net) Investing Cash Flows"

    - "Capital Expenditure(s)", "CapEx", "Capital Spending", "Property, Plant & Equipment (PP&E) Expenditure(s)/Purchase(s)"

    - "(Net) Cash (Flows) from Financing", "(Net) Cash (Flows) from Financing Activities", "(Net) Financing Cash Flows"


    Income-Statement / Profit-and-Loss- (P&L-) Statement / Earnings-Statement / Operations-Statement Line-Item Synonyms
    -------------------------------------------------------------------------------------------------------------------

    - "(Total) (Net) (Operating) Revenue(s)", "(Total) (Net) Sales"

    - "(Total) Cost of Goods Sold", "(Total) COGS", "(Total) Cost of Sales", "(Total) Cost of Revenue"

    - "Gross Income (or Loss)", "Gross Profit (or Loss)", "Gross Earnings (or Loss(es))"

    - "Operating Expenditure(s)", "Operating Expenses", "OpEx"

    - "Selling, General & Administrative (Expenses)", "SG&A (Expenses)"

    - "(Unadjusted) Operating Income", "(Unadjusted) Operating Profit"

    - "Earnings before Interest, Tax, Depreciation & Amortization", "EBITDA"

    - "Depreciation & Amortization", "D&A",
      "Depreciation & Amortization of Fixed Assets", "Depreciation & Amortization of Property, Plant & Equipment (PP&E)"

    - "Earnings before Interest & Tax", "EBIT"

    - "Net Income (Attributable to Shareholders)", "Net Profit (Attributable to Shareholders)"


    FINANCIAL METRIC FORMULAS
    =========================

    Turnover Ratio Metric Formulas
    ------------------------------

    `(Total) Asset Turnover Ratio` = (
      `(Total) (Net) (Operating) Revenue(s), a.k.a. (Total) (Net) Sales` /
      `average Total Assets, typically between two consecutive fiscal year-ends`
    )

    `Fixed Asset Turnover Ratio` = (
      `(Total) (Net) (Operating) Revenue(s), a.k.a. (Total) (Net) Sales` /
      `average (Net) Fixed Assets, a.k.a. (Net) Property, Plant & Equipment (PP&E), typically between two consecutive fiscal year-ends`
    )

    `Inventory Turnover Ratio, a.k.a. Inventory Conversion Ratio` = (
      `(Total) Cost of Goods Sold, a.k.a. (Total) COGS, or (Total) Cost of Sales, or (Total) Cost of Revenue` /
      `average (Total) (Net) Inventory(ies), typically between two consecutive fiscal year-ends`
    )

    Adjusted Income Metric Formulas
    -------------------------------

    `(Unadjusted) Earnings before Interest, Tax, Depreciation & Amortization, a.k.a. EBITDA` = (
      `(Unadjusted) Operating Income, a.k.a. Operating Profit, or Operating Earnings (or Loss(es))` +
      `Depreciation & Amortization, a.k.a. D&A (of Fixed Assets or Property, Plant & Equipment (PP&E))`
    )

    Profitability Margin Metric Formulas
    ------------------------------------

    `Cost of Goods Sold (COGS) Margin` = (
      `(Total) Cost of Goods Sold, a.k.a. (Total) COGS, or (Total) Cost of Sales, or (Total) Cost of Revenue` /
      `(Total) (Net) (Operating) Revenue(s), a.k.a. (Total) (Net) Sales`
    )

    `Gross (Income or Profit or Earnings) Margin` = (
      `Gross Income, a.k.a. Gross Profit, or Gross Earnings (or Loss(es))` /
      `(Total) (Net) (Operating) Revenue(s), a.k.a. (Total) (Net) Sales`
    )

    `(Unadjusted) Operating (Income or Profit or Earnings) Margin` = (
      `(Unadjusted) Operating Income, a.k.a. Operating Profit, or Operating Earnings (or Loss(es))` /
      `(Total) (Net) (Operating) Revenue(s), a.k.a. (Total) (Net) Sales`
    )

    `(Unadjusted) EBITDA Margin` = (
      `(Unadjusted) Earnings before Interest, Tax, Depreciation & Amortization, a.k.a. EBITDA` /
      `(Total) (Net) (Operating) Revenue(s), a.k.a. (Total) (Net) Sales`
    )

    `Depreciation & Amortization (D&A) Margin` = (
      `Depreciation & Amortization, a.k.a. D&A (of Fixed Assets or Property, Plant & Equipment (PP&E))` /
      `(Total) (Net) (Operating) Revenue(s), a.k.a. (Total) (Net) Sales`
    )

    `EBIT Margin` = (
      `Earnings before Interest & Tax, a.k.a. EBIT` /
      `(Total) (Net) (Operating) Revenue(s), a.k.a. (Total) (Net) Sales`
    )

    `Net (Income or Profit or Earnings) Margin` = (
      `Net Income, a.k.a. Net Profit, or Net Earnings (or Loss(es)) (Attributable to Shareholders)` /
      `(Total) (Net) (Operating) Revenue(s), a.k.a. (Total) (Net) Sales`
    )

    Profit-Utilization / Capital-Return Metric Formulas
    ---------------------------------------------------

    `Interest Coverage Ratio` = `Earnings before Interest & Tax, a.k.a. EBIT` / `Interest Expense`

    `Effective (Income) Tax Rate` = `(Income) Tax Expense` / `Income or Profit or Earnings (or Loss(es)) before (Income) Tax(es)`

    `Dividend Payout Ratio` = (
      `Cash Dividends` /
      `Net Income, a.k.a. Net Profit, or Net Earnings (or Loss(es)) (Attributable to Shareholders)`
    )

    `Retention Ratio` = 1 - `Dividend Payout Ratio`

    Capital-Intensiveness / Return-on-Capital Metric Formulas
    ---------------------------------------------------------

    `Capital Intensity Ratio` = `Total Assets` / `(Total) (Net) (Operating) Revenue(s), a.k.a. (Total) (Net) Sales`

    `Return on (Total) Assets, a.k.a. RoA or RoTA` = (
      `Net Income, a.k.a. Net Profit, or Net Earnings (or Loss(es)) (Attributable to Shareholders)` /
      `average Total Assets, typically between two consecutive fiscal year-ends`
    )

    Leverage Metric Formulas
    ------------------------

    `Total Debt` = (
      `Long-Term Debt (EXCLUDING any current/short-term portion)` +
      `Short-Term Debt, or Current Portion of (Long-Term) Debt`
    )

    Liquidity Metric Formulas
    -------------------------

    `(Net) Working Capital` = `(Total) Current Assets` - `(Total) Current Liabilities`

    `Working Capital Ratio` = `(Total) Current Assets` / `(Total) Current Liabilities`

    `Quick Ratio` = (
      (`Cash & Cash Equivalents` +
       `Short-Term Investments or (Current) Marketable Securities` +
       `(Net) Accounts Receivable, a.k.a. (Net) (Trade) Receivables`)
      / `(Total) Current Liabilities`
    )

    `Operating Cash Flow Ratio` = (
      `(Net) Cash Flows from Operations, a.k.a. (Net) Operating Cash Flows`
      / `(Total) Current Liabilities`
    )

    `Free Cash Flow, a.k.a. FCF` = (
      `(Net) Cash Flows from Operations, a.k.a. (Net) Operating Cash Flows` -
      `Capital Expenditure(s), a.k.a. CapEx, or Capital Spending, or Property, Plant & Equipment (PP&E) Expenditure(s)/Purchase(s)`
    )

    `Free Cash Flow Conversion Ratio` = `Free Cash Flow, a.k.a. FCF` / `Earnings before Interest, Tax, Depreciation & Amortization, a.k.a. EBITDA`

    `Days Inventory Outstanding, a.k.a. DIO` = (
      365 * `average (Total) (Net) Inventory(ies), typically between two consecutive fiscal year-ends`
      / `(Total) Cost of Goods Sold, a.k.a. (Total) COGS, or (Total) Cost of Sales, or (Total) Cost of Revenue`
    )

    `Days Payable Outstanding, a.k.a. DPO` = (
      365 * `average Accounts Payable, typically between two consecutive fiscal year-ends`
      / (`(Total) Cost of Goods Sold, a.k.a. (Total) COGS, or (Total) Cost of Sales, or (Total) Cost of Revenue` +
         `change in (Total) (Net) Inventory(ies), typically between two consecutive fiscal year-ends`)
    )

    `Days Sales Oustanding, a.k.a. DSO` = (
      365 * `average (Net) Accounts Receivable, a.k.a. (Net) (Trade) Receivables, typically between two consecutive fiscal year-ends`
      / `(Total) (Net) (Operating) Revenue(s), a.k.a. (Total) (Net) Sales`
    )

    `Cash Conversion Cycle, a.k.a. CCC` = (
      `Days Inventory Outstanding, a.k.a. DIO` + `Days Sales Oustanding, a.k.a. DSO` - `Days Payable Outstanding, a.k.a. DPO`
    )

    CAPITAL-INTENSIVENESS EVALUATION
    ================================

    Capital-intensive businesses tend to have one or several of the following characteristics:

    - high `(Net) Fixed Assets, a.k.a. (Net) Property, Plant & Equipment (PP&E)` as proportion of `Total Assets`,
      e.g., over 25%;

    - high `Total Assets` relative to `(Total) (Net) (Operating) Revenue(s), a.k.a. (Total) (Net) Sales`,
      e.g., over 2 times;

    - high `Capital Expenditure(s), a.k.a. CapEx, or Capital Spending, or Property, Plant & Equipment (PP&E) Expenditure(s)/Purchase(s)`
      relative to `(Total) (Net) (Operating) Revenue(s), a.k.a. (Total) (Net) Sales`,
      e.g., over 10%;

      and/or

    - low `Return on (Total) Assets, a.k.a. RoA or RoTA`,
      e.g., under 10%

    FINANCIAL-ANALYSIS LANGUAGE/WORDING
    ===================================

    - When we see the word "average" used before a Balance-Sheet line item in financial-analysis contexts,
      it often means the simple arithmetic mean of that line item's values at two consecutive fiscal year-ends

    - When we see the word "growth" or the the phrase "top-line performance"
      used in the context of product categories/segments or geographies, unless otherwise specified,
      it often concerns the year-on-year proportional/relative growth rates in `(Total) (Net) (Operating) Revenue(s), a.k.a. (Total) (Net) Sales`
      from such product categories/segments or geographies

    - When we see the word "margin" in financial-analysis contexts,
      we usually need to divide a certain Profit-and-Loss (P&L) line item by the `(Total) (Net) (Operating) Revenue(s), a.k.a. (Total) (Net) Sales`
      for the concerned financial reporting period(s)

    - When we see the word "turnover ratio" used after a Balance-Sheet line item in financial-analysis contexts,
      we usually need to divide the `(Total) (Net) (Operating) Revenue(s), a.k.a. (Total) (Net) Sales` for the fiscal year
      by the average of that Balance-Sheet line item between the latest fiscal year-end and the immediately-preceeding fiscal year-end

    PHYSICAL-PRODUCT COMPANY PERFORMANCE METRICS vs. FINANCIAL-SERVICES COMPANY PERFORMANCE METRICS
    ===============================================================================================

    Margin metrics are generally relevant/useful performance indicators for evaluating companies making physical products,
    but generally irrelevant / not useful for evaluating companies delivering financial services

    PULICLY LISTED & TRADED DEBT SECURITIES
    =======================================
    If there are debt securities registered to trade on a national securities exchange under a company's name,
    then such debt securities are enumerated on SEC filings' 1st page, alongside the company's public equity shares/stock.

    If only equity shares/stock are enumerated on SEC filings' 1st page,
    then there are no debt securities registered to trade on a national securities exchange under a company's name.
"""

_FEW_SHOT_INSTRUCTIONS = """
    Consider the examples below.
    {few_shot_examples}
"""


PROMPT_TEMPLATES = {
    "default": {
        "instructions": _DEFAULT_INSTRUCTIONS,
        "context": _CONTEXT,
        "query_str": _QUERY_STR,
        "few_shot_examples": _FEW_SHOT_INSTRUCTIONS,
    },
    "concise": {
        "instructions": _CONCISE_INSTRUCTIONS,
        "context": _CONTEXT,
        "query_str": _QUERY_STR,
        "few_shot_examples": _FEW_SHOT_INSTRUCTIONS,
    },
    "CoT": {
        "instructions": _COT_INSTRUCTIONS,
        "context": _CONTEXT,
        "query_str": _QUERY_STR,
        "few_shot_examples": _FEW_SHOT_INSTRUCTIONS,
    },
    "finance-expert": {
        "instructions": _FINANCE_EXPERT_INSTRUCTIONS,
        "context": _CONTEXT,
        "query_str": _QUERY_STR,
        "few_shot_examples": _FEW_SHOT_INSTRUCTIONS,
    },
}

MAIN_LAYOUT = RichPromptTemplate("""
    {{instructions}}
    {% if with_context %} {{context}} {% endif %}
    {% if with_few_shot_prompt %} {{few_shot_examples}} {% endif %}
    {{query_str}}
""")


def get_template(
    template_name: str, with_context: bool = False, with_few_shot_prompt: bool = False
) -> str:
    """Returns a formatted prompt specified by a template name."""
    components = PROMPT_TEMPLATES[template_name]
    components["with_context"] = with_context  # type: ignore
    components["with_few_shot_prompt"] = with_few_shot_prompt  # type: ignore
    return MAIN_LAYOUT.format(**components)  # type: ignore


def get_template_names() -> T.List[str]:
    """Returns all template names."""
    return list(PROMPT_TEMPLATES.keys())


def _load_json_file(file_path):
    logger.debug(f"Loading: {file_path}")
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def get_agent_template(prompt_name: str):
    agentic_templates = _load_json_file(cfg.paths.agentic_templates)
    return agentic_templates[prompt_name]
