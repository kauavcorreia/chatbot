// A URL da sua rota de API no backend (exemplo)
const BACKEND_URL = 'SUA_URL_DO_BACKEND_AQUI'; 

// Função principal para enviar a mensagem e falar com o Backend
async function sendMessage() {
    const userText = userInput.value.trim();

    if (userText === "") {
        return;
    }

    // 1. Adiciona a mensagem do usuário na tela
    addMessage('user', userText);
    
    // 2. Limpa o input
    userInput.value = '';
    userInput.style.height = 'auto'; // Reseta a altura do textarea
    
    // Opcional: Adiciona um balão de 'Digitando...'
    const thinkingMessage = addMessage('gemini', 'Digitando...'); 

    try {
        // 3. Fazer a requisição POST para o Backend
        const response = await fetch(BACKEND_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Se o seu backend exigir alguma chave de API, adicione aqui
            },
            body: JSON.stringify({ 
                message: userText // Envia a mensagem do usuário
                // Se você precisar enviar histórico, envie aqui também
            })
        });

        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }

        // 4. Converte a resposta do backend (JSON)
        const data = await response.json();
        
        // 5. Remove a mensagem de 'Digitando...'
        messageWindow.removeChild(thinkingMessage); 
        
        // 6. Adiciona a resposta da IA na tela
        const aiResponse = data.reply || "Desculpe, não recebi uma resposta válida do servidor.";
        addMessage('gemini', aiResponse);

    } catch (error) {
        // Em caso de erro (servidor offline, erro de rede, etc.)
        console.error('Erro ao comunicar com o Backend:', error);
        
        // Remove a mensagem de 'Digitando...'
        messageWindow.removeChild(thinkingMessage);
        
        // Exibe uma mensagem de erro na tela
        addMessage('gemini', 'Desculpe, houve um erro ao conectar com o servidor da IA.');
    }
}

// A função addMessage (que cria os balões de chat) permanece a mesma.
// Apenas altere o final dela para retornar o elemento criado, para que possamos removê-lo depois.
// ... (A função addMessage deve retornar o 'messageDiv')
function addMessage(role, text) {
    const messageDiv = document.createElement('div');
    // ... (restante do código da função addMessage)
    messageDiv.textContent = text;
    messageWindow.appendChild(messageDiv);
    messageWindow.scrollTop = messageWindow.scrollHeight;
    
    return messageDiv; // Importante: Retorna o elemento
}