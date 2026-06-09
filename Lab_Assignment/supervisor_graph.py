"""Supervisor-Workers pattern — Legal Advisory System.

Supervisor phân tích câu hỏi và điều phối 3 workers chuyên môn chạy song song:
  - ContractWorker  — hợp đồng, trách nhiệm dân sự
  - TaxWorker       — thuế, IRS, penalties
  - ComplianceWorker — SEC, SOX, GDPR, tuân thủ

Topology:
    START → supervisor → [Send workers in parallel] → aggregate → END
"""

from __future__ import annotations

import json
import logging
from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph

from common.llm import get_llm

logger = logging.getLogger(__name__)


def _last_wins(a: str, b: str) -> str:
    return b if b else a


class SupervisorState(TypedDict):
    question: str
    supervisor_plan: str
    needs_contract: bool
    needs_tax: bool
    needs_compliance: bool
    contract_result: Annotated[str, _last_wins]
    tax_result: Annotated[str, _last_wins]
    compliance_result: Annotated[str, _last_wins]
    final_answer: str


async def supervisor_node(state: SupervisorState) -> dict:
    """Supervisor: phân tích câu hỏi và quyết định workers nào cần chạy."""
    llm = get_llm()
    question = state["question"]

    messages = [
        SystemMessage(
            content=(
                "You are a legal case supervisor. Analyze the question and decide which "
                "specialist workers are needed.\n"
                "Reply with ONLY valid JSON:\n"
                '{"needs_contract": <bool>, "needs_tax": <bool>, "needs_compliance": <bool>, '
                '"plan": "<one sentence routing plan>"}\n\n'
                "needs_contract → contract law, breach, liability, tort\n"
                "needs_tax → tax, IRS, evasion, penalties, FBAR\n"
                "needs_compliance → SEC, SOX, GDPR, regulatory, AML"
            )
        ),
        HumanMessage(content=question),
    ]
    result = await llm.ainvoke(messages)
    raw = result.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Supervisor returned non-JSON, defaulting all workers on")
        parsed = {
            "needs_contract": True,
            "needs_tax": True,
            "needs_compliance": True,
            "plan": "Route to all specialists for comprehensive analysis.",
        }

    return {
        "supervisor_plan": parsed.get("plan", ""),
        "needs_contract": bool(parsed.get("needs_contract", True)),
        "needs_tax": bool(parsed.get("needs_tax", True)),
        "needs_compliance": bool(parsed.get("needs_compliance", True)),
    }


def dispatch_workers(state: SupervisorState) -> list[Send]:
    """Supervisor routing: dispatch parallel Send to selected workers."""
    sends: list[Send] = []
    if state.get("needs_contract"):
        sends.append(Send("contract_worker", state))
    if state.get("needs_tax"):
        sends.append(Send("tax_worker", state))
    if state.get("needs_compliance"):
        sends.append(Send("compliance_worker", state))
    if not sends:
        sends.append(Send("aggregate", state))
    return sends


async def contract_worker(state: SupervisorState) -> dict:
    """Worker 1: Contract & tort law specialist."""
    llm = get_llm()
    messages = [
        SystemMessage(
            content=(
                "You are a contract and tort law specialist. Analyze contract breach, "
                "civil liability, remedies, and damages. Keep response under 250 words."
            )
        ),
        HumanMessage(content=state["question"]),
    ]
    result = await llm.ainvoke(messages)
    return {"contract_result": result.content}


async def tax_worker(state: SupervisorState) -> dict:
    """Worker 2: Tax law specialist."""
    llm = get_llm()
    messages = [
        SystemMessage(
            content=(
                "You are a tax law specialist (IRS, IRC, FBAR/FATCA). Analyze tax "
                "consequences, penalties, and criminal exposure. Keep response under 250 words."
            )
        ),
        HumanMessage(content=state["question"]),
    ]
    result = await llm.ainvoke(messages)
    return {"tax_result": result.content}


async def compliance_worker(state: SupervisorState) -> dict:
    """Worker 3: Regulatory compliance specialist."""
    llm = get_llm()
    messages = [
        SystemMessage(
            content=(
                "You are a regulatory compliance specialist (SEC, SOX, GDPR, FCPA, AML). "
                "Analyze regulatory violations and enforcement. Keep response under 250 words."
            )
        ),
        HumanMessage(content=state["question"]),
    ]
    result = await llm.ainvoke(messages)
    return {"compliance_result": result.content}


async def aggregate(state: SupervisorState) -> dict:
    """Supervisor aggregates worker outputs into final report."""
    llm = get_llm()

    sections: list[str] = []
    if state.get("supervisor_plan"):
        sections.append(f"## Routing Plan\n{state['supervisor_plan']}")
    if state.get("contract_result"):
        sections.append(f"## Contract & Tort Analysis\n{state['contract_result']}")
    if state.get("tax_result"):
        sections.append(f"## Tax Analysis\n{state['tax_result']}")
    if state.get("compliance_result"):
        sections.append(f"## Compliance Analysis\n{state['compliance_result']}")

    combined = "\n\n---\n\n".join(sections) if sections else state["question"]

    messages = [
        SystemMessage(
            content=(
                "You are senior legal counsel. Synthesize the worker analyses into one "
                "cohesive client report with clear sections. Under 400 words. "
                "End with an educational disclaimer."
            )
        ),
        HumanMessage(content=combined),
    ]
    result = await llm.ainvoke(messages)
    return {"final_answer": result.content}


def create_supervisor_graph():
    """Build Supervisor-Workers StateGraph."""
    graph = StateGraph(SupervisorState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("contract_worker", contract_worker)
    graph.add_node("tax_worker", tax_worker)
    graph.add_node("compliance_worker", compliance_worker)
    graph.add_node("aggregate", aggregate)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        dispatch_workers,
        ["contract_worker", "tax_worker", "compliance_worker", "aggregate"],
    )
    graph.add_edge("contract_worker", "aggregate")
    graph.add_edge("tax_worker", "aggregate")
    graph.add_edge("compliance_worker", "aggregate")
    graph.add_edge("aggregate", END)

    return graph.compile()