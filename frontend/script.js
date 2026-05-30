const API_BASE_URLS = [
    window.location.origin.startsWith("http") ? window.location.origin : null,
    "http://localhost:8000",
    "http://127.0.0.1:8000"
].filter(Boolean);

function toggleChat() {
    const chat = document.getElementById("chat-window");
    chat.style.display = chat.style.display === "flex" ? "none" : "flex";
}

function toggleFull() {
    document.getElementById("chat-window").classList.toggle("fullscreen");
}

function addMessage(sender, text) {
    const chatBody = document.getElementById("chat-body");

    const msg = document.createElement("div");
    msg.className = sender === "You" ? "msg user" : "msg ai";

    msg.innerHTML = `<span>${marked.parse(text)}</span>`;
    chatBody.appendChild(msg);

    chatBody.scrollTop = chatBody.scrollHeight;
}

function showTyping() {
    const chatBody = document.getElementById("chat-body");

    const msg = document.createElement("div");
    msg.className = "msg ai";
    msg.id = "typing";

    msg.innerHTML = `<div class="loader"></div>`;
    chatBody.appendChild(msg);
}

function removeTyping() {
    const el = document.getElementById("typing");
    if (el) el.remove();
}

async function sendMessage() {
    const input = document.getElementById("message");
    const text = input.value.trim();

    if (!text) return;

    addMessage("You", text);
    input.value = "";

    showTyping();

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000);

    try {
        let res;
        let lastError;

        for (const apiBaseUrl of API_BASE_URLS) {
            try {
                res = await fetch(`${apiBaseUrl}/ask`, {
                    method: "POST",
                    mode: "cors",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ query: text }),
                    signal: controller.signal
                });
                if (res.status === 404 || res.status === 405) {
                    lastError = new Error(`${apiBaseUrl} does not expose /ask`);
                    res = undefined;
                    continue;
                }
                break;
            } catch (err) {
                lastError = err;
            }
        }

        if (!res) {
            throw lastError || new Error("API not reachable");
        }
        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            throw new Error(errorData.detail || `API error: ${res.status}`);
        }

        const data = await res.json();

        removeTyping();
        addMessage("AI", data.answer || "No response");

    } catch (err) {
        removeTyping();
        const message = err.name === "AbortError"
            ? "The AI is still working. Please try again after a moment, or restart Ollama if this keeps happening."
            : err.message || "API not reachable";
        addMessage("Error", message);
        console.error(err);
    } finally {
        clearTimeout(timeoutId);
    }
}

// Enter key
document.getElementById("message").addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
    }
});
