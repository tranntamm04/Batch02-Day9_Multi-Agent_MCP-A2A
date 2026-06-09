# Lab Solution — Day09 Multi-Agent A2A Codelab

**Sinh viên:** Trần Đức Tâm
**Dự án:** Legal Multi-Agent System with A2A Protocol

---

# Phần 1: Direct LLM Calling (Stage 1)

## Bài 1.1 — Thay đổi câu hỏi

Đã thay đổi biến `QUESTION` trong:

```python
stages/stage_1_direct_llm/main.py
```

Ví dụ:

```python
QUESTION = "Nếu bên thuê nhà chậm thanh toán tiền thuê thì hậu quả pháp lý là gì?"
```

---

## Bài 1.2 — Temperature Control

Đã chỉnh sửa:

```python
common/llm.py
```

Thêm:

```python
temperature=0.3
```

Ví dụ:

```python
return ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4-5"),
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.3,
)
```

### Ý nghĩa

* Giảm tính ngẫu nhiên
* Kết quả pháp lý ổn định hơn
* Dễ debug hơn

---

# Phần 2: LLM + RAG & Tools (Stage 2)

## Bài 2.1 — Thêm Knowledge Base

Đã thêm entry:

```python
{
    "id": "labor_law",
    "keywords": [
        "lao động",
        "sa thải",
        "hợp đồng lao động",
        "labor",
        "termination"
    ],
    "text": "..."
}
```

---

## Bài 2.2 — Tool mới

Đã tạo:

```python
@tool
def check_statute_of_limitations(case_type: str) -> str:
```

Dùng để tra cứu thời hiệu khởi kiện.

```python
limits = {
    "contract": "4 năm (UCC § 2-725)",
    "tort": "2-3 năm tùy bang",
    "property": "5 năm",
}
```

Đã thêm vào:

```python
TOOLS = [
    search_legal_database,
    calculate_damages,
    check_statute_of_limitations,
]
```

---

# Phần 3: Single Agent ReAct (Stage 3)

## Bài 3.1 — Tool Search Case Law

Đã thêm:

```python
@tool
def search_case_law(keywords: str) -> str:
```

Các án lệ:

### Breach

```text
Hadley v. Baxendale (1854)
```

### Negligence

```text
Donoghue v. Stevenson (1932)
```

### Contract

```text
Carlill v. Carbolic Smoke Ball Co (1893)
```

---

## Bài 3.2 — Debug Agent

Stage 3 sử dụng:

```python
graph.astream(..., stream_mode="updates")
```

để hiển thị:

```text
Think
↓
Act
↓
Observe
↓
Final Answer
```

---

# Phần 4: Multi-Agent In-Process (Stage 4)

## Bài 4.1 — Privacy Agent

Đã thêm:

```python
call_privacy_specialist()
```

Chuyên xử lý:

* GDPR
* CCPA
* Data Privacy
* User Consent
* Data Breach

---

## Bài 4.2 — Conditional Routing

Đã thêm:

```python
needs_privacy
```

Routing:

```python
data
privacy
gdpr
dữ liệu
consent
```

Khi phát hiện keyword sẽ gọi:

```text
Privacy Agent
```

---

## Graph Topology

```text
analyze_law
      |
      v
check_routing
      |
      +-------------+
      |             |
      v             v
Tax Agent     Compliance Agent
      |
      v
Privacy Agent
      |
      v
Aggregate
      |
      v
END
```

---

# Phần 5: Distributed A2A System (Stage 5)

## Bài 5.1 — Trace Request Flow

```text
User
 |
 v
Customer Agent (10100)
 |
 v
Law Agent (10101)
 |
 +----------------------+
 |                      |
 v                      v
Tax Agent         Compliance Agent
(10102)              (10103)
 |
 +-----------+
             |
             v
         Aggregate
             |
             v
       Customer Agent
             |
             v
            User
```

---

## Trace Metadata

Hệ thống sử dụng:

```python
trace_id
context_id
delegation_depth
```

### trace_id

Theo dõi request xuyên suốt hệ thống.

### context_id

Xác định phiên hội thoại.

### delegation_depth

Ngăn vòng lặp delegate vô hạn.

---

## Bài 5.2 — Dynamic Discovery

Đã test:

### Bước 1

Tắt:

```text
Tax Agent
```

### Bước 2

Chạy:

```bash
uv run python test_client.py
```

### Kết quả

Law Agent vẫn hoạt động:

```text
[Tax analysis unavailable: ...]
```

Hệ thống degrade gracefully.

---

## Bài 5.3 — Modify Tax Agent

Đã chỉnh:

```python
tax_agent/graph.py
```

Prompt:

```text
Answer in under 120 words.
Use bullet points.
Focus only on key tax consequences.
```

Mục tiêu:

* Trả lời nhanh hơn
* Giảm token
* Giảm latency

---
## Bài Tập Files

| File | Trạng thái |
|---|---|
| `exercises/exercise_2_tools.py` | ✅ Hoàn thành |
| `exercises/exercise_4_multiagent.py` | ✅ Hoàn thành |

---

## Lab Assignment — Supervisor-Workers

**Folder:** `Lab_Assignment/`

Cải tiến từ single agent (Day08) sang **Supervisor-Workers** với 3 workers:

| Worker | Vai trò |
|---|---|
| `contract_worker` | Hợp đồng, tort, bồi thường |
| `tax_worker` | Thuế, IRS, penalties |
| `compliance_worker` | SEC, SOX, GDPR, AML |

**Supervisor** phân tích câu hỏi → JSON routing → dispatch song song qua LangGraph `Send`.

**Chạy:**
```bash
uv run python Lab_Assignment/main.py
```

---


# Web Chat Demo (Bonus)

## Mục tiêu

Xây dựng giao diện web chat cho hệ thống Multi-Agent.

---

## Danh sách Agents hiển thị

```text
Registry
Customer Agent
Law Agent
Tax Agent
Compliance Agent
```

---

## Chạy Demo

### Chạy Agents

```bash
uv run python -m registry
uv run python -m tax_agent
uv run python -m compliance_agent
uv run python -m law_agent
uv run python -m customer_agent
```

### Chạy Web

```bash
uv run uvicorn web_chat:app --host 0.0.0.0 --port 8000 --reload
```

Mở:

```text
http://localhost:8000
```

---

# Câu Hỏi Ôn Tập

## Khi nào dùng Single Agent?

* Một domain
* Workflow đơn giản
* Không cần parallel

---

## Khi nào dùng Multi-Agent?

* Nhiều domain chuyên môn
* Cần chia nhỏ nhiệm vụ
* Cần chạy song song

---

## Ưu điểm A2A

* Chuẩn giao tiếp agent
* Dynamic discovery
* Scale độc lập
* Tách biệt service

---

## Chống vòng lặp vô hạn

```python
MAX_DELEGATION_DEPTH = 3
```

---

## Tại sao cần Registry?

Không hard-code URL.

Cho phép:

```text
discover()
```

tìm agent động theo capability.

---
