// === URL do seu backend FastAPI ===
const API_URL = "http://localhost:8000/chat";

// Seletores
const messageWindow = document.getElementById("message-window");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

// Função para adicionar mensagens
function addMessage(role, text) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message");

    if (role === "user") {
        messageDiv.classList.add("user-message");
    } else {
        messageDiv.classList.add("gemini-message");
    }

    messageDiv.textContent = text;
    messageWindow.appendChild(messageDiv);
    messageWindow.scrollTop = messageWindow.scrollHeight;
    return messageDiv;
}

// Enviar mensagem ao backend
async function sendMessage() {
    const text = userInput.value.trim();
    if (text === "") return;

    // Adiciona mensagem do usuário
    addMessage("user", text);

    userInput.value = "";

    // "Digitando..."
    const thinking = addMessage("gemini", "Digitando...");

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: text })
        });

        const data = await response.json();

        // Remove "digitando..."
        messageWindow.removeChild(thinking);

        // Mensagem formatada do backend
        const respostaFormatada =
            `Especialista recomendado: ${data.especialista}\n\n${data.mensagem}`;

        addMessage("groq", respostaFormatada);
    } catch (error) {
        console.error("Erro:", error);
        messageWindow.removeChild(thinking);
        addMessage("groq", "❌ Erro ao conectar ao servidor.");
    }
}

// Botão enviar
sendButton.addEventListener("click", sendMessage);

// Enviar com Enter
userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

