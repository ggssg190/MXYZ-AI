const input = document.getElementById("messageInput");
const messages = document.getElementById("messages");
const form = document.getElementById("chatForm");
const sendButton = document.getElementById("sendButton");
const modeLabel = document.getElementById("modeLabel");
const welcome = document.getElementById("welcome");
const newChat = document.getElementById("newChat");

let history = [];

function addMessage(role, content) {
    const row = document.createElement("div");
    row.className = `message ${role}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = role === "user" ? "U" : "M";

    const body = document.createElement("div");
    body.className = "message-content";
    body.textContent = content;

    row.append(avatar, body);
    messages.appendChild(row);

    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: "smooth"
    });

    return body;
}

async function checkHealth() {
    try {
        const response = await fetch("/api/health");
        if (!response.ok) throw new Error("Server tidak merespons");

        const data = await response.json();

        modeLabel.textContent = data.ai_configured
            ? `AI aktif · ${data.model || "Ready"}`
            : "API belum dikonfigurasi";
    } catch (error) {
        modeLabel.textContent = "Koneksi server bermasalah";
    }
}

input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 180) + "px";
});

input.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        form.requestSubmit();
    }
});

form.addEventListener("submit", async event => {
    event.preventDefault();

    const message = input.value.trim();
    if (!message) return;

    addMessage("user", message);

    if (welcome) welcome.style.display = "none";

    input.value = "";
    input.style.height = "auto";
    sendButton.disabled = true;

    const loading = addMessage("assistant", "MXYZ sedang berpikir...");

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "same-origin",
            body: JSON.stringify({
                messages: [
                    ...history,
                    {
                        role: "user",
                        content: message
                    }
                ],
                temperature: 0.7,
                max_tokens: 2048
            })
        });

        const data = await response.json();

        if (!response.ok) {
            const detail = data.detail || data.error || response.statusText;
            throw new Error(
                typeof detail === "string"
                    ? detail
                    : JSON.stringify(detail)
            );
        }

        const answer = data.reply ?? data.response;

        if (!answer) {
            throw new Error("Respons API tidak berisi jawaban.");
        }

        loading.textContent = answer;

        history.push(
            { role: "user", content: message },
            { role: "assistant", content: answer }
        );

        history = history.slice(-30);

    } catch (error) {
        loading.textContent = "Terjadi kesalahan: " + error.message;
    } finally {
        sendButton.disabled = false;
        input.focus();
    }
});

newChat.addEventListener("click", () => {
    history = [];
    messages.replaceChildren();

    if (welcome) welcome.style.display = "flex";

    input.focus();
});

checkHealth();
