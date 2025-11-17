const API_URL = "http://localhost:8000/chat";


const messageWindow = document.getElementById("message-window");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");


function addMessage(role, text) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message");

    if (role === "user") {
        messageDiv.classList.add("user-message");
    } else {
        messageDiv.classList.add("groq-message");
    }

    messageDiv.textContent = text;
    messageWindow.appendChild(messageDiv);
    messageWindow.scrollTop = messageWindow.scrollHeight;
    return messageDiv;
}


async function sendMessage() {
    const text = userInput.value.trim();
    if (text === "") return;

    
    addMessage("user", text);

    userInput.value = "";

    
    const thinking = addMessage("groq", "Digitando...");

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: text })
        });

        const data = await response.json();


        messageWindow.removeChild(thinking);


        const respostaFormatada =
            `Especialista recomendado: ${data.especialista}\n\n${data.mensagem}`;

        addMessage("groq", respostaFormatada);
    } catch (error) {
        console.error("Erro:", error);
        messageWindow.removeChild(thinking);
        addMessage("groq", "❌ Erro ao conectar ao servidor.");
    }
}


sendButton.addEventListener("click", sendMessage);


userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

