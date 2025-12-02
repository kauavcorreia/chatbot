from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from dotenv import load_dotenv
from pydantic import BaseModel
import os
import requests
import json

load_dotenv()

GROQ = Groq(api_key=os.getenv("GROQ_API_KEY"))
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

app = FastAPI(title="MedBot - Assistente Médico Inteligente")

class ChatRequest(BaseModel):
    message: str


dados_usuario = {
    "cidade": None
}


def buscar_clinicas(especialidade: str, cidade: str):
    if not cidade:
        return []

    url = (
        "https://maps.googleapis.com/maps/api/place/textsearch/json"
        f"?query={especialidade}+em+{cidade}"
        f"&key={GOOGLE_API_KEY}"
    )

    resposta = requests.get(url).json()

    clinicas = []
    for item in resposta.get("results", [])[:5]:
        clinicas.append({
            "nome": item.get("name"),
            "endereco": item.get("formatted_address"),
        })
    
    return clinicas




prompt_sistema = (
    "Você é um assistente médico virtual ético e acolhedor. "
    "Sua função é APENAS:\n"
    "1. Identificar o especialista adequado pelos sintomas.\n"
    "2. Identificar a cidade quando o usuário disser.\n"
    "3. NUNCA retornar diagnósticos.\n"
    "4. NUNCA dar informações de localização de clínicas, pois isso é feito PELO BACKEND usando Google Places.\n\n"
    "Você SEMPRE responde **somente** JSON. NUNCA responda texto fora do JSON.\n\n"
    "Formato OBRIGATÓRIO:\n"
    "{\n"
    "  \"especialista\": \"nome ou vazio\",\n"
    "  \"mensagem\": \"texto acolhedor e leve\",\n"
    "  \"cidade\": \"nome da cidade ou vazio\"\n"
    "}\n"
)



@app.post("/chat")
async def chat(request: ChatRequest):
    mensagem = request.message.strip()

    
    resposta_ia = GROQ.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": mensagem}
        ],
        temperature=0.3,
    )

    resposta_texto = resposta_ia.choices[0].message.content

    try:
        dados = json.loads(resposta_texto)
    except:
        dados = {
                "especialista": "",
                "mensagem": resposta_texto,
                "cidade": ""
                }

    
    if dados.get("cidade"):
        dados_usuario["cidade"] = dados["cidade"]

    cidade = dados_usuario["cidade"]
    especialista = dados.get("especialista", "")
    mensagem_final = dados.get("mensagem", "")


    if especialista and cidade:
        clinicas = buscar_clinicas(especialista, cidade)
    else:
        clinicas = []

    return {
        "especialista": especialista,
        "mensagem": mensagem_final,
        "cidade_registrada": cidade,
        "clinicas": clinicas
    }

#conexao com front end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
