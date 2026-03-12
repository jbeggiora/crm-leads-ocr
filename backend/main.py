from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional
import pytesseract
from PIL import Image
import uuid
import io
import re

# Configuração do Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = FastAPI()

# --- MODELOS DE DADOS ---
class Lead(BaseModel):
    id: Optional[str] = None
    nome: Optional[str] = "Não identificado"
    telefone: Optional[str] = "Não identificado"
    mensagem: Optional[str] = None

# --- FUNÇÕES DE INTELIGÊNCIA ---
def limpar_dados_ocr(texto):
    # 1. Busca Telefone
    padrao_tel = r'(\+?55\s?\d{2}\s?9?\d{4}-?\d{4})'
    tel_match = re.search(padrao_tel, texto)
    telefone = tel_match.group(0) if tel_match else "Não encontrado"

    # 2. Busca Nome
    padrao_nome_til = r'~\s?(\w+)'
    nome_match = re.search(padrao_nome_til, texto)
    if nome_match:
        nome = nome_match.group(1)
    else:
        padrao_contato = r'(\w+)\n+Não está nos seus contatos'
        match_contato = re.search(padrao_contato, texto, re.IGNORECASE)
        nome = match_contato.group(1) if match_contato else "Desconhecido"

    # 3. EXTRAÇÃO DE CONTEXTO
    linhas = texto.split('\n')
    mensagens_relevantes = []
    for linha in linhas:
        if len(linha.strip()) > 15 and "Não está nos seus contatos" not in linha and "grupos em comum" not in linha:
            mensagens_relevantes.append(linha.strip())
    
    contexto = " | ".join(mensagens_relevantes[-3:]) if mensagens_relevantes else "Sem contexto adicional"
    return nome, telefone, contexto

# --- ROTAS ---

@app.get("/")
async def root():
    return {"status": "Marco 0.3.5 - Extração com Contexto Ativa"}

@app.post("/upload-print/", response_model=Lead)
async def upload_print(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Formato de imagem inválido.")

    try: # <--- O TRY PRECISA COMEÇAR AQUI
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        texto_extraido = pytesseract.image_to_string(image, lang='por')
        
        nome, telefone, contexto = limpar_dados_ocr(texto_extraido)

        return Lead(
            id=str(uuid.uuid4()),
            nome=nome,
            telefone=telefone,
            mensagem=contexto
        )
    except Exception as e: # <--- AGORA O EXCEPT ESTÁ CORRETO
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

@app.post("/leads-manual/")
async def criar_lead_manual(lead: Lead):
    lead.id = str(uuid.uuid4())
    return {"message": "Lead manual recebido!", "data": lead}