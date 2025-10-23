from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()

# Inicializa cliente da OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Inicializa o app
app = FastAPI(title="MedBot - Assistente Médico Ético")

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print("OPENAI_API_KEY:", api_key)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, troque pelo endereço do front
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    if not user_message.strip():
        return {"response": "Por favor, envie uma mensagem válida."}

    # Prompt base que define o comportamento médico ético
    system_prompt = (
        "Você é um assistente médico virtual empático, ético e responsável. "
        "Forneça informações médicas gerais e oriente o usuário a procurar um profissional de saúde quando necessário. "
        "Evite diagnósticos, prescrições e prognósticos. "
        "Responda sempre em linguagem acessível e com tom acolhedor."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.6,  # equilíbrio entre criatividade e segurança
    )

    reply = response.choices[0].message.content
    return {"response": reply}

