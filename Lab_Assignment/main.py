"""Lab Assignment: Supervisor-Workers Legal Advisory System.

Cải tiến từ single-agent (Day08) sang Supervisor-Workers với 3 workers chuyên môn.

Chạy:
    uv run python Lab_Assignment/main.py
"""

from __future__ import annotations

import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

from Lab_Assignment.supervisor_graph import create_supervisor_graph

QUESTION = (
    "If a company breaks a contract and avoids taxes on overseas revenue, "
    "what are the legal, tax, and regulatory consequences?"
)


async def main() -> None:
    load_dotenv()

    print("=" * 70)
    print("LAB ASSIGNMENT: Supervisor-Workers Pattern")
    print("=" * 70)
    print()
    print("[Architecture]")
    print("  Supervisor → dispatch parallel workers:")
    print("    • ContractWorker  (contract & tort law)")
    print("    • TaxWorker       (IRS, tax penalties)")
    print("    • ComplianceWorker (SEC, SOX, GDPR)")
    print("  → Aggregate → Final report")
    print()
    print(f"Question: {QUESTION}")
    print("-" * 70)

    graph = create_supervisor_graph()

    start = time.perf_counter()
    result = await graph.ainvoke({
        "question": QUESTION,
        "supervisor_plan": "",
        "needs_contract": False,
        "needs_tax": False,
        "needs_compliance": False,
        "contract_result": "",
        "tax_result": "",
        "compliance_result": "",
        "final_answer": "",
    })
    elapsed = time.perf_counter() - start

    print(f"\nSupervisor plan: {result.get('supervisor_plan', 'N/A')}")
    print("\n" + "=" * 70)
    print("FINAL ANSWER")
    print("=" * 70)
    print(result["final_answer"])
    print("-" * 70)
    print(f"Total latency: {elapsed:.1f}s")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())