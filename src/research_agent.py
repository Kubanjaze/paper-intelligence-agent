"""
research_agent.py — Phase B: Agent SDK research loop.

Feeds extracted compound data to an agent equipped with WebSearch, WebFetch,
and Write. The agent searches the live literature and writes report.md to the
output directory.
"""
import os
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


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
    abs_output_dir = os.path.abspath(output_dir)

    prompt = f"""\
You are a drug discovery analyst. You have been given a structured extraction from a research paper.

CRITICAL INSTRUCTIONS:
1. Your FIRST action must be a WebSearch to gather context on the paper and compounds.
2. Your FINAL action must be to call the Write tool to write "report.md" in the current directory.
   Do NOT end without writing this file.

Here is the structured extraction from the paper:

{extraction_json}

Search strategy:
- Search compound names + target for recent publications, clinical data, and patent filings
- For clinical compounds: search ClinicalTrials.gov for phase and outcome
- For each SAR trend: look for supporting or contradicting evidence in the literature
- Note structural alerts, toxicity signals, or off-target effects

After completing your searches, use the Write tool to write report.md.
The report must include:
1. Paper summary (target, scope, key message)
2. Compound table (name, activity, assay conditions from extraction)
3. SAR narrative (what structural changes improve/worsen activity and why)
4. Post-publication context for key compounds (from your searches)
5. Consistency assessment: do the paper's claims hold up against the broader literature?
6. Recommendations: which compounds are worth further investigation?

You MUST end by calling Write to create report.md. This is required.\
"""

    result_text = None
    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            cwd=abs_output_dir,
            allowed_tools=["WebSearch", "WebFetch", "Write"],
            permission_mode="acceptEdits",
            model=model,
        ),
    ):
        if isinstance(message, ResultMessage):
            print(f"  Agent complete. Stop reason: {message.stop_reason}")
            result_text = message.result

    # Fallback: if the agent never used Write, save its text response as report.md
    report_path = os.path.join(abs_output_dir, "report.md")
    if not os.path.exists(report_path) and result_text:
        print("  Agent did not use Write tool — saving result text as report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(result_text)
        print(f"  Saved fallback report to {report_path}")
