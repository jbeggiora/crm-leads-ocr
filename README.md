MultiZAP - Gestão Inteligente de Leads (Marco 0.6.0) 🚀
O MultiZAP é uma solução SaaS focada em corretores de imóveis (como a Elite Imóveis) para transformar capturas de tela (prints) de conversas do WhatsApp em leads qualificados e organizados.

🌟 Funcionalidades Principais (v0.6.0)
Visão Computacional com Gemini IA: O sistema utiliza o modelo gemini-1.5-flash para analisar imagens e extrair dados sem depender de padrões fixos de texto.

Extração de Contexto Real: Capaz de identificar o nome do lead e o telefone mesmo quando estão escondidos no corpo da conversa, como no caso de números enviados manualmente.

Scripts de Atendimento Automáticos: Gera uma saudação personalizada baseada no interesse do cliente (ex: sobrado no Xaxim) e na dúvida específica capturada (ex: metragem dos cômodos).

Timestamp de Captura: Registro automático de data e hora para controle de SLA e frescor do lead.

Interface Moderna: Painel desenvolvido com Tailwind CSS para uma experiência limpa e responsiva.

🛠️ Tecnologias Utilizadas
Backend: FastAPI (Python).

IA Multimodal: Google Generative AI (Gemini API).

Banco de Dados: SQLite com SQLAlchemy.

Frontend: HTML5, Tailwind CSS e JavaScript (Fetch API).

📈 Evolução do Projeto (Changelog)
Este projeto demonstra a transição de uma lógica baseada em regras para uma solução baseada em inteligência artificial:

Marco 0.1.0 - 0.5.0 (OCR & Regex):

Utilizava Tesseract/OCR tradicional para extração de texto bruto.

Lógica baseada em expressões regulares (Regex) para tentar limpar dados "sujos".

Limitação: Sofria com ruídos visuais do WhatsApp (símbolos, nomes de botões como "Bloquear" ou "Adicionar") e falhava em layouts variados.

Marco 0.6.0 (IA Multimodal):

Substituição completa do OCR/Regex pelo processamento visual do Gemini.

Fim do "lixo" no banco de dados; a IA agora entende o que é interface e o que é dado relevante.

Adição de geração de linguagem natural para scripts de vendas.