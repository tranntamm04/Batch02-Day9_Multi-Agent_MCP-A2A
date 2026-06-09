import os
from uuid import uuid4

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

load_dotenv()

CUSTOMER_AGENT_URL = os.getenv("CUSTOMER_AGENT_URL", "http://localhost:10100")

app = FastAPI(title="Multi-Agent Legal Chat")


class ChatRequest(BaseModel):
    message: str


async def ask_customer_agent(question: str) -> str:
    async with httpx.AsyncClient(timeout=300.0) as http_client:
        card_url = f"{CUSTOMER_AGENT_URL}/.well-known/agent.json"
        card_resp = await http_client.get(card_url)
        card_resp.raise_for_status()

        from a2a.types import AgentCard, Message, Part, Role, TextPart
        from a2a.types import SendMessageRequest, MessageSendParams
        from a2a.client import A2AClient

        agent_card = AgentCard.model_validate(card_resp.json())
        client = A2AClient(httpx_client=http_client, agent_card=agent_card)

        message = Message(
            role=Role.user,
            parts=[Part(root=TextPart(text=question))],
            message_id=str(uuid4()),
        )

        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(message=message),
        )

        response = await client.send_message(request)

        result_text = ""

        if hasattr(response, "root"):
            root = response.root
            if hasattr(root, "result"):
                result = root.result

                if hasattr(result, "artifacts") and result.artifacts:
                    for artifact in result.artifacts:
                        for part in artifact.parts:
                            p = part.root if hasattr(part, "root") else part
                            if hasattr(p, "text"):
                                result_text += p.text

                elif hasattr(result, "parts") and result.parts:
                    for part in result.parts:
                        p = part.root if hasattr(part, "root") else part
                        if hasattr(p, "text"):
                            result_text += p.text

        return result_text or "Không nhận được phản hồi từ hệ thống Multi-Agent."


@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        answer = await ask_customer_agent(req.message)
        return {"ok": True, "answer": answer}
    except Exception as e:
        return {"ok": False, "answer": f"Lỗi: {e}"}


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <title>Legal Multi-Agent Chat</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <style>
    :root {
      --bg: #f4f7fb;
      --card: #ffffff;
      --text: #172033;
      --muted: #6b7280;
      --line: #e5e7eb;
      --primary: #2563eb;
      --primary-dark: #1d4ed8;
      --primary-light: #eff6ff;
      --success: #16a34a;
      --shadow: 0 20px 60px rgba(15, 23, 42, 0.10);
      --radius: 24px;
    }

    * {
      box-sizing: border-box;
      font-family: Inter, "Segoe UI", Arial, sans-serif;
    }

    body {
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top left, rgba(37, 99, 235, 0.12), transparent 35%),
        linear-gradient(135deg, #f8fafc, #eef4ff);
      color: var(--text);
      padding: 24px;
    }

    .page {
      max-width: 1180px;
      height: calc(100vh - 48px);
      margin: 0 auto;
      display: grid;
      grid-template-columns: 340px 1fr;
      gap: 20px;
    }

    .sidebar,
    .chat {
      background: rgba(255, 255, 255, 0.92);
      border: 1px solid rgba(226, 232, 240, 0.9);
      box-shadow: var(--shadow);
      border-radius: var(--radius);
      overflow: hidden;
    }

    .sidebar {
      padding: 26px;
      display: flex;
      flex-direction: column;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 14px;
      margin-bottom: 22px;
    }

    .logo {
      width: 54px;
      height: 54px;
      border-radius: 18px;
      background: linear-gradient(135deg, #2563eb, #60a5fa);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 26px;
      box-shadow: 0 12px 30px rgba(37, 99, 235, 0.25);
    }

    h1 {
      font-size: 22px;
      margin: 0;
      line-height: 1.2;
    }

    .subtitle {
      margin: 4px 0 0;
      color: var(--muted);
      font-size: 13px;
    }

    .intro {
      background: var(--primary-light);
      border: 1px solid #dbeafe;
      color: #1e3a8a;
      padding: 16px;
      border-radius: 18px;
      line-height: 1.65;
      font-size: 14px;
      margin-bottom: 20px;
    }

    .section-title {
      font-weight: 700;
      font-size: 14px;
      margin: 10px 0 12px;
    }

    .agent-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-bottom: 20px;
    }

    .agent {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: #fff;
    }

    .agent-left {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 14px;
      font-weight: 600;
    }

    .dot {
      width: 9px;
      height: 9px;
      border-radius: 999px;
      background: var(--success);
      box-shadow: 0 0 0 4px rgba(22, 163, 74, 0.12);
    }

    .port {
      color: var(--muted);
      font-size: 12px;
    }

    .suggestions {
      margin-top: auto;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .chip {
      border: 1px solid var(--line);
      background: #fff;
      color: #334155;
      padding: 12px 14px;
      border-radius: 16px;
      cursor: pointer;
      font-size: 13px;
      line-height: 1.4;
      transition: 0.18s;
      text-align: left;
    }

    .chip:hover {
      border-color: #93c5fd;
      background: #f8fbff;
      transform: translateY(-1px);
    }

    .chat {
      display: flex;
      flex-direction: column;
      min-width: 0;
    }

    .topbar {
      height: 76px;
      padding: 0 26px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #ffffff;
    }

    .top-title {
      font-size: 18px;
      font-weight: 800;
    }

    .top-desc {
      color: var(--muted);
      font-size: 13px;
      margin-top: 3px;
    }

    .status {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 9px 13px;
      border-radius: 999px;
      background: #ecfdf5;
      color: #166534;
      border: 1px solid #bbf7d0;
      font-size: 13px;
      font-weight: 700;
    }

    .messages {
      flex: 1;
      overflow-y: auto;
      padding: 26px;
      background:
        linear-gradient(#f8fafc 1px, transparent 1px),
        linear-gradient(90deg, #f8fafc 1px, transparent 1px);
      background-size: 28px 28px;
    }

    .msg-row {
      display: flex;
      gap: 10px;
      margin-bottom: 18px;
      animation: fadeIn 0.22s ease;
    }

    .msg-row.user-row {
      justify-content: flex-end;
    }

    .avatar {
      width: 34px;
      height: 34px;
      border-radius: 12px;
      flex: 0 0 auto;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #e0ecff;
      color: var(--primary);
      font-weight: 800;
    }

    .bubble {
      max-width: min(760px, 78%);
      padding: 15px 17px;
      border-radius: 20px;
      line-height: 1.7;
      font-size: 15px;
      white-space: pre-wrap;
      word-wrap: break-word;
    }

    .bot-bubble {
      background: #ffffff;
      border: 1px solid var(--line);
      color: #1f2937;
      border-top-left-radius: 8px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    }

    .user-bubble {
      background: linear-gradient(135deg, #2563eb, #3b82f6);
      color: white;
      border-top-right-radius: 8px;
      box-shadow: 0 10px 28px rgba(37, 99, 235, 0.22);
    }

    .typing {
      display: none;
      padding: 0 26px 12px;
      color: var(--muted);
      font-size: 14px;
    }

    .typing span {
      display: inline-flex;
      gap: 5px;
      align-items: center;
      background: #fff;
      border: 1px solid var(--line);
      padding: 10px 14px;
      border-radius: 999px;
    }

    .typing i {
      width: 6px;
      height: 6px;
      background: #94a3b8;
      border-radius: 999px;
      display: block;
      animation: blink 1s infinite ease-in-out;
    }

    .typing i:nth-child(2) { animation-delay: 0.15s; }
    .typing i:nth-child(3) { animation-delay: 0.3s; }

    .composer {
      padding: 18px 26px 24px;
      border-top: 1px solid var(--line);
      background: #fff;
    }

    .input-wrap {
      display: flex;
      gap: 12px;
      align-items: flex-end;
      background: #f8fafc;
      border: 1px solid #dbe3ef;
      border-radius: 22px;
      padding: 10px;
      transition: 0.18s;
    }

    .input-wrap:focus-within {
      border-color: #93c5fd;
      box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.08);
      background: #fff;
    }

    textarea {
      flex: 1;
      border: none;
      outline: none;
      resize: none;
      background: transparent;
      min-height: 46px;
      max-height: 140px;
      padding: 12px 10px;
      color: var(--text);
      font-size: 15px;
      line-height: 1.5;
    }

    button {
      height: 46px;
      min-width: 104px;
      border: none;
      border-radius: 16px;
      background: var(--primary);
      color: white;
      font-weight: 800;
      font-size: 14px;
      cursor: pointer;
      transition: 0.18s;
    }

    button:hover {
      background: var(--primary-dark);
      transform: translateY(-1px);
    }

    button:disabled {
      opacity: 0.55;
      cursor: not-allowed;
      transform: none;
    }

    .hint {
      color: var(--muted);
      font-size: 12px;
      margin: 9px 4px 0;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes blink {
      0%, 80%, 100% { opacity: 0.35; transform: translateY(0); }
      40% { opacity: 1; transform: translateY(-2px); }
    }

    @media (max-width: 900px) {
      body {
        padding: 12px;
      }

      .page {
        height: calc(100vh - 24px);
        grid-template-columns: 1fr;
      }

      .sidebar {
        display: none;
      }

      .bubble {
        max-width: 88%;
      }

      .topbar {
        padding: 0 18px;
      }

      .messages {
        padding: 18px;
      }

      .composer {
        padding: 14px 18px 18px;
      }
    }
  </style>
</head>

<body>
  <div class="page">
    <aside class="sidebar">
      <div class="brand">
        <div class="logo">⚖️</div>
        <div>
          <h1>Legal Multi-Agent</h1>
          <p class="subtitle">A2A Protocol Demo</p>
        </div>
      </div>

      <div class="intro">
        Hệ thống gồm nhiều agent chuyên môn phối hợp với nhau để phân tích câu hỏi pháp lý:
        Customer Agent → Law Agent → Tax / Compliance Agent.
      </div>

      <div class="section-title">Trạng thái dịch vụ</div>

      <div class="agent-list">
        <div class="agent">
          <div class="agent-left"><div class="dot"></div>Registry</div>
          <div class="port">10000</div>
        </div>
        <div class="agent">
          <div class="agent-left"><div class="dot"></div>Customer Agent</div>
          <div class="port">10100</div>
        </div>
        <div class="agent">
          <div class="agent-left"><div class="dot"></div>Law Agent</div>
          <div class="port">10101</div>
        </div>
        <div class="agent">
          <div class="agent-left"><div class="dot"></div>Tax Agent</div>
          <div class="port">10102</div>
        </div>
        <div class="agent">
          <div class="agent-left"><div class="dot"></div>Compliance Agent</div>
          <div class="port">10103</div>
        </div>
      </div>

      <div class="section-title">Câu hỏi mẫu</div>

      <div class="suggestions">
        <button class="chip" onclick="fillQuestion('If a company breaks a contract and avoids taxes, what are the legal and regulatory consequences?')">
          Công ty vi phạm hợp đồng và trốn thuế
        </button>
        <button class="chip" onclick="fillQuestion('What happens if a startup shares user data without consent?')">
          Startup chia sẻ dữ liệu người dùng không có consent
        </button>
        <button class="chip" onclick="fillQuestion('What are the risks if a company hides overseas revenue?')">
          Công ty che giấu doanh thu ở nước ngoài
        </button>
      </div>
    </aside>

    <main class="chat">
      <header class="topbar">
        <div>
          <div class="top-title">AI Legal Assistant</div>
          <div class="top-desc">Chat trực tiếp với hệ thống Multi-Agent</div>
        </div>
        <div class="status"><span>●</span> Online</div>
      </header>

      <section id="messages" class="messages">
        <div class="msg-row">
          <div class="avatar">AI</div>
          <div class="bubble bot-bubble">
Xin chào! Bạn có thể nhập một câu hỏi pháp lý. Hệ thống sẽ tự điều phối qua các agent chuyên môn để phân tích và tổng hợp câu trả lời.
          </div>
        </div>
      </section>

      <div id="typing" class="typing">
        <span>
          Multi-Agent đang phân tích
          <i></i><i></i><i></i>
        </span>
      </div>

      <footer class="composer">
        <div class="input-wrap">
          <textarea id="input" rows="1" placeholder="Nhập câu hỏi của bạn..."></textarea>
          <button id="sendBtn" onclick="sendMessage()">Gửi</button>
        </div>
        <div class="hint">Enter để gửi, Shift + Enter để xuống dòng.</div>
      </footer>
    </main>
  </div>

  <script>
    const messages = document.getElementById("messages");
    const input = document.getElementById("input");
    const sendBtn = document.getElementById("sendBtn");
    const typing = document.getElementById("typing");

    function fillQuestion(text) {
      input.value = text;
      autoResize();
      input.focus();
    }

    function addMessage(text, type) {
      const row = document.createElement("div");
      row.className = "msg-row " + (type === "user" ? "user-row" : "");

      if (type === "bot") {
        const avatar = document.createElement("div");
        avatar.className = "avatar";
        avatar.textContent = "AI";
        row.appendChild(avatar);
      }

      const bubble = document.createElement("div");
      bubble.className = "bubble " + (type === "user" ? "user-bubble" : "bot-bubble");
      bubble.textContent = text;
      row.appendChild(bubble);

      messages.appendChild(row);
      messages.scrollTop = messages.scrollHeight;
    }

    function autoResize() {
      input.style.height = "auto";
      input.style.height = Math.min(input.scrollHeight, 140) + "px";
    }

    async function sendMessage() {
      const text = input.value.trim();
      if (!text) return;

      addMessage(text, "user");
      input.value = "";
      autoResize();

      sendBtn.disabled = true;
      sendBtn.textContent = "Đang gửi...";
      typing.style.display = "block";
      messages.scrollTop = messages.scrollHeight;

      try {
        const res = await fetch("/api/chat", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({message: text})
        });

        const data = await res.json();
        addMessage(data.answer, "bot");
      } catch (err) {
        addMessage("Không kết nối được web server: " + err.message, "bot");
      } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = "Gửi";
        typing.style.display = "none";
        input.focus();
      }
    }

    input.addEventListener("input", autoResize);

    input.addEventListener("keydown", function(e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  </script>
</body>
</html>
    """)