from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from dotenv import load_dotenv
import requests
import os
from pydantic import BaseModel


load_dotenv()


cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))


app = FastAPI(title="MedBot - Assistente Médico com Geolocalização")


class ChatRequest(BaseModel):
    message: str
    cidade: str | None = None  


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


prompt_sistema = (
    "Você é um assistente médico virtual ético e acolhedor. "
    "Sua função é identificar o tipo de especialista ideal com base nos sintomas descritos. "
    "NUNCA faça diagnósticos nem prescreva medicamentos. "
    "Apenas indique o tipo de especialista e oriente o paciente a procurar atendimento."
)


def buscar_especialistas(tipo: str, cidade: str = None):
    base_url = "https://nominatim.openstreetmap.org/search"
    query = f"{tipo} {cidade}" if cidade else tipo
    params = {
        "q": query,
        "format": "json",
        "limit": 5,
        "addressdetails": 1,
    }
    headers = {"User-Agent": "MedBot/1.0 (seu_email_real@gmail.com)"}

    resposta = requests.get(base_url, params=params, headers=headers)
    dados = resposta.json()

    resultados = []
    for lugar in dados:
        resultados.append({
            "nome": lugar.get("display_name", "Nome não disponível"),
            "lat": lugar.get("lat"),
            "lng": lugar.get("lon"),
            "endereco": lugar.get("display_name")
        })
    return resultados


@app.post("/chat")
async def chat(request: ChatRequest):
    mensagem_usuario = request.message
    cidade = request.cidade


    if not mensagem_usuario.strip():
        return {"resposta": "Por favor, envie uma mensagem válida."}


    resposta_ia = cliente.chat.completions.create(
    model="llama-3.1-8b-instant",


        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": mensagem_usuario},
        ],
        temperature=0.5,
    )

    resposta_texto = resposta_ia.choices[0].message.content


    especialistas = [
        "cardiologista", "dermatologista", "neurologista", "ortopedista",
        "ginecologista", "psicólogo", "otorrinolaringologista",
        "pediatra", "clínico geral", "endocrinologista", "urologista"
    ]

    tipo_encontrado = next((e for e in especialistas if e in resposta_texto.lower()), "clínico geral")

 
    locais = []
    if cidade:
        locais = buscar_especialistas(tipo_encontrado, cidade)

    
    return {
        "mensagem": resposta_texto,
        "especialista": tipo_encontrado,
        "locais": locais
    }
