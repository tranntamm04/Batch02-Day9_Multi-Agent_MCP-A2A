## Trace Flow

Quá trình xử lý request diễn ra như sau:

1. User gửi câu hỏi.
2. Customer Agent nhận request.
3. Customer Agent chuyển tiếp (delegate) sang Law Agent.
4. Law Agent thực hiện:
   - `analyze_law`
   - `check_routing`
5. Law Agent gửi các tác vụ chuyên biệt đến:
   - Tax Agent
   - Compliance Agent
6. Hai agent xử lý song song và trả kết quả về Law Agent.
7. Law Agent tổng hợp kết quả (`aggregate`).
8. Kết quả được trả lại Customer Agent.
9. Customer Agent phản hồi cho User.

---

## Sequence Diagram

```mermaid
sequenceDiagram
    actor User

    participant CA as Customer Agent<br/>(10100)
    participant LA as Law Agent<br/>(10101)
    participant TA as Tax Agent<br/>(10102)
    participant CO as Compliance Agent<br/>(10103)

    User->>CA: Question

    CA->>LA: delegate_to_legal_agent()

    Note over LA: analyze_law
    Note over LA: check_routing

    par Tax Analysis
        LA->>TA: Tax-related request
        TA-->>LA: Tax result
    and Compliance Analysis
        LA->>CO: Compliance request
        CO-->>LA: Compliance result
    end

    Note over LA: aggregate results

    LA-->>CA: Final legal response

    CA-->>User: Answer
```

---

## Flow Diagram (Simple View)

```text
User
 |
 | Question
 v
Customer Agent (10100)
 |
 | delegate_to_legal_agent()
 v
Law Agent (10101)
 |
 | analyze_law
 |
 | check_routing
 |
 +------------------+
 |                  |
 v                  v
Tax Agent       Compliance Agent
(10102)         (10103)
 |                  |
 +--------+---------+
          |
          v
      Law Agent
      aggregate
          |
          v
   Customer Agent
          |
          v
        User
```

---

## Kết luận

Request được tiếp nhận bởi **Customer Agent (10100)**, sau đó được chuyển sang **Law Agent (10101)** để phân tích và điều phối. Law Agent gọi đồng thời **Tax Agent (10102)** và **Compliance Agent (10103)** để xử lý các nghiệp vụ chuyên biệt. Sau khi tổng hợp kết quả, Law Agent trả phản hồi về Customer Agent và cuối cùng gửi kết quả đến User.