# Lab Assignment — Supervisor-Workers Pattern

Cải tiến hệ thống tư vấn pháp lý từ **single agent** (Day08) sang **Supervisor-Workers** với 3 workers chuyên môn.

## Workers

| Worker | Chuyên môn |
|---|---|
| `contract_worker` | Hợp đồng, vi phạm, trách nhiệm dân sự, bồi thường |
| `tax_worker` | Thuế, IRS, FBAR/FATCA, hình phạt hình sự/dân sự |
| `compliance_worker` | SEC, SOX, GDPR, FCPA, AML |

## Chạy

```bash
# Từ thư mục gốc dự án (cần OPENROUTER_API_KEY trong .env)
uv run python Lab_Assignment/main.py
```

## So sánh với Day08 (Single Agent)

| | Day08 Single Agent | Lab Assignment Supervisor-Workers |
|---|---|---|
| Agents | 1 LLM làm tất cả | 1 Supervisor + 3 Workers |
| Chuyên môn | Prompt chung | Prompt riêng từng domain |
| Thực thi | Tuần tự | Workers chạy **song song** |
| Chất lượng | Tổng quát | Sâu hơn từng lĩnh vực |
| Pattern | ReAct / direct LLM | Supervisor-Workers (LangGraph Send) |

## Files

- `supervisor_graph.py` — StateGraph, supervisor node, 3 workers, aggregate
- `main.py` — Entry point demo