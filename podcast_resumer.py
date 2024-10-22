import os
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())


template="""
    Você é um assistente para resumir Podcasts.

    Você receberá o conteúdo transcrito de um Podcast e deverá
    criar um resumo, em MARKDOWN, contendo: 
    1. Uma introdução
        - Escreva 1 parágrafo com uma introdução sobre o que foi falado no podcast
    
    2. Os principais pontos abordados, em ordem cronológica. Numere-os.
        - Escreva um texto bem completo sobre cada um dos pontos. Seja específico.
    
    3. Uma conclusão
        - Escreva um parágrafo sobre conclusão.
    
    Podcast: {input}
    """
prompt_template = PromptTemplate.from_template(template)

chat = ChatOpenAI(model="gpt-4o-mini")
chain = prompt_template | chat

transcript = open("transcript.txt", "r").read()
response = chain.invoke({"input": transcript})

open("summary.md", "w").write(response.content)
