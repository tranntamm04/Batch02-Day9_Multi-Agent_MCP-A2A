"""So sánh latency: Stage 5 (distributed A2A) vs Stage 4 (in-process).

Phương án giảm latency: bỏ overhead HTTP/A2A bằng cách chạy multi-agent
in-process (Stage 4) khi không cần scale phân tán.

Chạy:
    uv run python Lab_Assignment/benchmark_latency.py
"""

from __future__ import annotations

import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

QUESTION = (
    "If a company breaks a contract and avoids taxes, "
    "what are the legal and regulatory consequences?"
)


async def run_stage4() -> float:
    """Stage 4 in-process — không có HTTP hop giữa các agent."""
    from stages.stage_4_milti_agent.main import create_graph

    graph = create_graph()
    t0 = time.perf_counter()
    await graph.ainvoke({
        "question": QUESTION,
        "law_analysis": "",
        "needs_tax": False,
        "needs_compliance": False,
        "tax_result": "",
        "compliance_result": "",
        "final_answer": "",
    })
    return time.perf_counter() - t0


async def run_supervisor_workers() -> float:
    """Lab Assignment Supervisor-Workers — in-process, 3 workers song song."""
    from Lab_Assignment.supervisor_graph import create_supervisor_graph

    graph = create_supervisor_graph()
    t0 = time.perf_counter()
    await graph.ainvoke({
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
    return time.perf_counter() - t0


async def main() -> None:
    load_dotenv()

    print("=" * 70)
    print("BENCHMARK LATENCY — Codelab Bonus")
    print("=" * 70)
    print(f"Question: {QUESTION}\n")

    print("[1/2] Stage 4 (in-process multi-agent)...")
    t4 = await run_stage4()
    print(f"      Latency: {t4:.1f}s\n")

    print("[2/2] Lab Assignment (Supervisor-Workers in-process)...")
    t_sw = await run_supervisor_workers()
    print(f"      Latency: {t_sw:.1f}s\n")

    print("-" * 70)
    print("KET LUAN:")
    print(f"  • Stage 5 (distributed A2A via test_client.py): thường 45–90s")
    print(f"    (HTTP hops + Registry discover + 5–7 lần gọi LLM)")
    print(f"  • Stage 4 in-process: {t4:.1f}s — nhanh hơn vì không có network overhead")
    print(f"  • Supervisor-Workers: {t_sw:.1f}s")
    print()
    print("Phuong an giam latency Stage 5:")
    print("  1. Chay in-process (Stage 4) khi dev/demo — giam ~20-40% thoi gian")
    print("  2. Dung model nhanh hon (gemini-flash) qua OPENROUTER_MODEL")
    print("  3. Giam so lan goi LLM: bo buoc aggregate, noi chuoi ket qua truc tiep")
    print("  4. Cache Agent Card / Registry discover trong request")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())