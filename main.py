from openai import OpenAI
from sanitation import limparstr
import unidecode
import re

######################################################################
# GPT

# Faz o controle  sobre a requisiçao ao gpt
def pergunta_gpt(pergunt):

    prompt = [{"role": "user", "content": pergunt }]

    resposta = client.chat.completions.create(
        messages = prompt,
        model = "gpt-3.5-turbo-0125",
        max_tokens = 500,
        temperature = 0
    )
    
    return resposta.choices[0].message.content

# Gera o prompt e trata a resposta do gpt
def formula_prompt(comment=""):
    if comment:
        prompt = f"Summarize the following comment in a few words:  '{comment}'"
    else:
        return "NaN"
    
    resposta_limpa = format_resposta_gpt( pergunta_gpt(prompt) )

    return resposta_limpa

######################################################################
# Funçoes

# Formata a resposta do GPT, caso precise
def format_resposta_gpt(resposta):
    return limparstr(resposta, 1)

######################################################################


## COLETA A CHAVE API PELO TERMINAL
while True:
    KEY = input("Digite sua chave da api da OpenAI: \n")
    if KEY:
        break

client = OpenAI(api_key = KEY)

resposta_gpt = formula_prompt("Comentario a ser resumido")