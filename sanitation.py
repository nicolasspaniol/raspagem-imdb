
""" Módulo responsável pela higienização dos dados extraidos no scraping """

import pandas as pd
import re

def limparstr(string):
    """
    Limpa a string, excluindo caracteres repetidos
    """
    # Complia uma expressoes, que identifica caracteres iguais em sequencia
    expression = re.compile(r'(.)\1{2,}')
    # Aplica a expressão
    str_limpa = expression.sub(r'\1', str(string))
    return str_limpa.strip()

def limpanum(num):
    """
    Limpa as strings numericas, garantindo que contenham apenas números
    """
    str_limpa = re.sub(r'[^0-9.]', '', str(num))
    return strlimpa

## Importa os dados
dfdirty = pd.read_csv(r"reviews.csv")

# Utiliza a função limpastr para limpar os campos de texto da base de dados
dfclean = dfdirty.copy()
dfclean['title'] = dfdirty['title'].apply(limparstr)
dfclean['comment'] = dfdirty['comment'].apply(limparstr)
dfclean['has_spoiler'] = dfdirty['has_spoiler'].apply(limparstr)

# Utiliza a função limpanum para limpar os campos numéricos da base de dados
dfclean['rating'] = dfdirty['rating'].apply(limpanum)
dfclean['helpful_count'] = dfdirty['helpful_count'].apply(limpanum)
dfclean['helpful_total'] = dfdirty['helpful_total'].apply(limpanum)

## Garante que não haja linhas duplicadas
dfclean = dfclean.drop_duplicates()

## Salva os dados em um arquivo .csv
dfclean.to_csv(r"reviews_limpos.csv", index=False)
