"""Tax Agent LangGraph definition.

Uses create_react_agent with a tax-specialised system prompt.
No tools — it answers purely from LLM knowledge.
"""

from __future__ import annotations

from langgraph.prebuilt import create_react_agent

from common.llm import get_llm

TAX_SYSTEM_PROMPT = """
You are a specialist tax attorney.

Rules:
- Answer in under 120 words.
- Focus only on the key tax consequences.
- Use bullet points.
- Mention civil penalties separately from criminal penalties.
- Avoid long explanations.
- End with a one-line disclaimer.

Educational purposes only.
"""

def create_graph():
    """Return a compiled LangGraph create_react_agent for tax questions."""
    llm = get_llm()
    graph = create_react_agent(
        model=llm,
        tools=[],
        prompt=TAX_SYSTEM_PROMPT,
    )
    return graph