from unidecode import unidecode
import pandas as pd
import re

######################################################################
# Funçoes

# Limpar os imputs, em dois casos, string e numerico
def limparstr(string, type):
    if type:
        ## CASO STRING
        # Remove caracteres indesejados
        str_limpa = re.sub(r'[^\w\s.,?!:;()"\'\s-]', '', str(string))
        # Complia uma expressoes, que identifica caracteres iguais em sequencia
        expression = re.compile(r'(.)\1{2,}')
        # Aplica a expressão
        str_limpa = expression.sub(r'\1', str(string))
        # Remove acentuaçoes
        str_limpa = unidecode(str_limpa)
    else:
        ## CASO NUMERICO
        str_limpa = re.sub(r'[^0-9.]', '', str(string))

    return str_limpa.strip()

# Resume grotescamente a string para questoes de teste
def resumir(str):
    if str:
        return str[:100]
    else:
        return "NaN"
    
######################################################################
#Limpeza de dados

## IMPORTA OS DADOS
dfdirty = pd.read_csv(r"raspagem-imdb\dataset\output.csv")

## LIMPA OS DADOS
# String
dfclean = dfdirty.copy()
dfclean['title'] = dfdirty['title'].apply(limparstr, type=1)
dfclean['comment'] = dfdirty['comment'].apply(limparstr, type=1)
dfclean['has_spoiler'] = dfdirty['has_spoiler'].apply(limparstr, type=1)

# Numerico
dfclean['rating'] = dfdirty['rating'].apply(limparstr, type=0)
dfclean['helpful_count'] = dfdirty['helpful_count'].apply(limparstr, type=0)
dfclean['helpful_total'] = dfdirty['helpful_total'].apply(limparstr, type=0)


## ELIMINA LINHAS DUPLICADAS
dfclean = dfclean.drop_duplicates()

## RESUME OS COMENTARIOS grostescamente
dfclean['comment'] = dfclean['comment'].apply(resumir)

######################################################################

## Salva os dados em um arquivo .csv
dfclean.to_csv(r"raspagem-imdb\dataset\reviews_limpos.csv", index=False)
