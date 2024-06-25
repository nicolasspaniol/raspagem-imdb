""" Módulo responsável pela higienização dos dados extraidos no scraping """

import pandas as pd
import re


def sanitize_string(string):
    """
    Limpa a string, excluindo caracteres repetidos
    """
    str_limpa = re.sub(r"(.)\1{2,}", r"\1", string)
    return str_limpa.strip()


def sanitize_number(num):
    """
    Limpa as strings numéricas, garantindo que contenham apenas números
    """
    return re.sub(r"[^0-9.]", "", str(num))


# Importa os dados
dirty_df = pd.read_csv("reviews.csv")

# Utiliza a função `sanitize_string` para limpar os campos de texto da base de dados
clean_df = dirty_df.copy()
clean_df["title"] = dirty_df["title"].apply(sanitize_string)
clean_df["comment"] = dirty_df["comment"].apply(sanitize_string)

# Utiliza a função `sanitize_number` para limpar os campos numéricos da base de dados
clean_df["rating"] = dirty_df["rating"].apply(sanitize_number)
clean_df["helpful_count"] = dirty_df["helpful_count"].apply(sanitize_number)
clean_df["helpful_total"] = dirty_df["helpful_total"].apply(sanitize_number)

# Garante que não haja linhas duplicadas
clean_df = clean_df.drop_duplicates()

# Salva os dados em um arquivo .csv
clean_df.to_csv("reviews_limpos.csv", index=False)
