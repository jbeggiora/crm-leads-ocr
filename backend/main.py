import os
import json
import google.generativeai as genai
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uuid

# --- CONFIGURAÇÃO IA ---
# Pegue sua chave em: https://aistudio.google.com/
genai.configure(api_key="SUA_CHAVE_AQUI")
model = genai.GenerativeModel('gemini-1.5-flash')

# --- BANCO DE DADOS ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./multizap.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Lead(Base):
    __tablename__ = "leads"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String)
    telefone = Column(String)
    mensagem = Column(Text)
    script_ia = Column(Text)
    data_captura = Column(String)

Base.metadata.create_all(bind=engine)

# --- APP ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/leads/")
def list_leads(db: Session = Depends(get_db)):
    return db.query(Lead).all()

@app.delete("/leads/{lead_id}")
def delete_lead(lead_id: str, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if lead:
        db.delete(lead)
        db.commit()
    return {"status": "removido"}

@app.post("/upload/")
async function upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        agora = datetime.now()
        data_hora = agora.strftime("%d/%m/%Y às %H:%M")

        # Prompt focado no seu negócio de Elite Imóveis
        prompt = f"""
        Analise este print de WhatsApp. Hoje é {data_hora}.
        Extraia e retorne APENAS um JSON puro (sem markdown) com:
        - "nome": Nome do lead.
        - "telefone": Número de contato.
        - "mensagem": Resumo do que ele quer ou anúncio clicado.
        - "script_ia": Script de saudação: "Olá [nome], aqui é o Jonatas da Elite Imóveis. Vi seu interesse no [produto] e sua dúvida sobre [pergunta]. Vamos conversar?"
        - "data_captura": "{data_hora}"
        """

        img_upload = genai.upload_file(temp_path)
        response = model.generate_content([prompt, img_upload])
        
        dados_ia = json.loads(response.text.replace('```json', '').replace('```', '').strip())

        novo_lead = Lead(
            nome=dados_ia.get('nome', 'Desconhecido'),
            telefone=dados_ia.get('telefone', 'Não encontrado'),
            mensagem=dados_ia.get('mensagem', 'Sem contexto'),
            script_ia=dados_ia.get('script_ia', ''),
            data_captura=dados_ia.get('data_captura', data_hora)
        )
        db.add(novo_lead)
        db.commit()

        return {"status": "sucesso", "lead": novo_lead.nome}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)