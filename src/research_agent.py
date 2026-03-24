"""
research_agent.py — Phase B: Agent SDK research loop.

Feeds extracted compound data to an agent equipped with WebSearch, WebFetch,
and Write. The agent searches the live literature and writes report.md to the
output directory.
"""
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

RESEARCH_SYSTEM_PROMPT = """\
You are a drug discovery analyst. You have been given a structured extraction from a research paper.
Your job is to contextualize each compound by searching the literature, then write a comprehensive
analyst report.

Search strategy:
- For compound names and basic properties: use open web search
- For clinical trial outcomes, safety signals, and regulatory history: prefer
  PubMed (pubmed.ncbi.nlm.nih.gov), ClinicalTrials.gov (clinicaltrials.gov),
  and ChEMBL (chembl.ebi.ac.uk)
- For each compound found in clinical development: search for Phase and outcome
- Note any structural alerts, toxicity signals, or off-target effects found

Write the final report to report.md in the working directory.
The report must include:
1. Paper summary (target, scope, key message)
2. Compound table (name, activity, assay conditions)
3. SAR narrative (what structural changes improve/worsen activity and why)
4. For each compound: post-publication context from your searches
5. Consistency assessment: do the paper's claims hold up?
6. Recommendations: which compounds are worth further investigation?\
"""


async def run_research_agent(
    extraction_json: str,
    output_dir: str,
    model: str = "claude-opus-4-6",
) -> None:
    """
    Phase B: feed extraction results to an agent that searches the literature
    and writes report.md to output_dir.

    Args:
        extraction_json: JSON string of the ExtractionResult (from Phase A).
        output_dir:      Directory where report.md will be written.
        model:           Model for the agent. Defaults to claude-opus-4-6.
    """
    prompt = f"""{RESEARCH_SYSTEM_PROMPT}

Here is the structured extraction from the paper:

{extraction_json}

Search the literature for context on each compound, then write report.md."""

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            cwd=output_dir,
            allowed_tools=["WebSearch", "WebFetch", "Write"],
            permission_mode="acceptEdits",
            model=model,
        ),
    ):
        if isinstance(message, ResultMessage):
            print(f"  Agent complete. Stop reason: {message.stop_reason}")
