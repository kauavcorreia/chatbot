from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from dotenv import load_dotenv
import os
import json
from pydantic import BaseModel



load_dotenv() #PUXA A API KEY no .env


GROQ_API_KEY = Groq(api_key=os.getenv("GROQ_API_KEY"))
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


app = FastAPI(title="MedBot - Assistente Médico Inteligente")



class ChatRequest(BaseModel): 
    message: str


local_usuario = {
    "cidade": None        
}

def buscar_clinicas(especialidade: str, cidade: str):
    url = (
        "https://maps.googleapis.com/maps/api/place/textsearch/json"
        f"?query={especialidade}+em+{cidade}"
        f"&key={GOOGLE_API_KEY}"
    )

    requests = requests.get(url).json()
    
    clinicas = []

    for item in requests.get("results", [])[:5]:
        clinicas.append({
            "nome": item.get("name"),
            "endereco": item.get("formatted_address"),
            "rating": item.get("rating")
        })

    return clinicas

# PERMITE CONEXOES COM O FRONT-END
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prompt_sistema = (
    "Você é um assistente médico virtual ético e acolhedor. "
    "Sua função é APENAS indicar o especialista mais adequado com base nos sintomas descritos. "
    "NÃO faça diagnósticos, NÃO prescreva remédios e NÃO utilize termos técnicos médicos. "
    "Explique de forma leve e acolhedora o motivo da recomendação.\n\n"
    "Sua resposta deve ser SEMPRE em JSON seguindo EXATAMENTE este formato:\n"
    "{\n"
    "  \"especialista\": \"nome do especialista\",\n"
    "  \"mensagem\": \"texto explicando a recomendação sem diagnóstico\"\n"
    "}\n\n"
    "Exemplos válidos:\n"
    "{ \"especialista\": \"cardiologista\", \"mensagem\": \"Pode ser interessante consultar um cardiologista para avaliar melhor esses sintomas.\" }\n"
    "{ \"especialista\": \"dermatologista\", \"mensagem\": \"Um dermatologista pode ajudar a analisar essa alteração na pele.\" }\n"
)


# ROTA PRINCIPAL DO CHAT
@app.post("/chat")
async def chat(request: ChatRequest):


    mensagem_usuario = request.message.strip()


    if not mensagem_usuario:
        return {
            "erro": "Envie uma mensagem válida."
        }


    resposta_ia = GROQ_API_KEY.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": mensagem_usuario},
        ],
        temperature=0.4,
    )

    resposta_texto = resposta_ia.choices[0].message.content

    try:
        dados = json.loads(resposta_texto)
        especialista = dados.get("especialista", "clínico geral")
        mensagem = dados.get("mensagem", resposta_texto)
    except:
   
        especialista = "clínico geral"
        mensagem = resposta_texto

   
    return {
        "especialista": especialista,
        "mensagem": mensagem
    }
