""" Módulo responsável pela extração de dados do IMDb """

import re
from bs4 import BeautifulSoup
import requests
import json
import urllib
import pandas as pd


def find_id(movie_title: str) -> str:
    """
    Encontra o ID do filme por meio das sugestões retornadas na busca pelo
    título
    """

    encoded_title = urllib.parse.quote(movie_title)
    url = f"https://v3.sg.media-imdb.com/suggestion/x/{encoded_title}.json?includeVideos=0"
    
    response = json.loads(requests.get(url).content)
    return response["d"][0]["id"]


def get_comments(movie_id: str) -> list[str]:
    """
    Faz a raspagens dos primeiros 25 comentários de um filme, ordenados pelo
    número de votos
    """

    url = f"https://www.imdb.com/title/{movie_id}/reviews?sort=totalVotes&dir=desc&ratingFilter=0"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "lxml")

    review_list = soup.find("div", {"class": "lister"})
    if review_list == None:
        print("Filme não encontrado!")
        return []
    
    reviews = review_list.find_all("div", {"class": "review-container"})

    results = []

    for review in reviews:
        # O primeiro <span> dentro do <span class="rating-..."> é
        # A nota dada pelo usuário, de 0 a 10 (opcional)
        rating_span = review.find("span", {"class": "rating-other-user-rating"})
        rating = None if rating_span == None else int(rating_span.find("span").text)

        # O comentário é obrigatório
        comment_div = review.find("div", {"class": "content"})
        comment = comment_div.find("div", {"class": "text"}).text
        
        # Quebras de linhas são substituídas por ";", o que não deve afetar
        # a interpretação dos dados
        comment = comment.replace("\r", "").replace("\n", ";")

        # O título é obrigatório
        title = review.find("a", {"class": "title"}).text.strip(" \n")

        # Não necessariamente vão haver votos na review
        helpful_message = review.find("div", {"class": "actions"})
        if helpful_message != None:
            pattern = r"\s*([0-9,]+) out of ([0-9,]+) [\s\S]+"
            msg = helpful_message.text
            count, total = re.match(pattern, msg).groups()
            helpful_count = int(count.replace(",", ""))
            helpful_total = int(total.replace(",", ""))
        else:
            helpful_count = None
            helpful_total = None

        has_spoiler = review.find("span", {"class": "spoiler-warning"}) != None

        results.append({
            "movie_id": movie_id,
            "title": title,
            "comment": comment,
            "rating": rating,
            "helpful_count": helpful_count,
            "helpful_total": helpful_total,
            "has_spoiler": has_spoiler
        })

    return results


if __name__ == "__main__":
    movies_to_fetch = []

    dataframe = pd.read_csv("dataset/the_oscar_award.csv")
    filtered = dataframe[dataframe["category"] == "WRITING (Original Story)"]
    movies_to_fetch = filtered["film"].tolist()

    review_columns = [
        "movie_id", "title", "rating", "comment",
        "helpful_count", "helpful_total", "has_spoiler"
    ]
    review_list = []

    movie_columns = ["movie_id", "movie_title"]
    movie_list = []

    print(f"{len(movies_to_fetch)} filmes encontrados\n----------")

    for i, movie in enumerate(movies_to_fetch):
        id = find_id(movie)
        movie_list.append({ "movie_id": id, "movie_title": movie })

        print(str(i + 1).ljust(5, " "), end = "")
        print(f"Raspando reviews de \"{movie}\" ({id})...")

        review_list.extend(get_comments(id))

    print()

    reviews = pd.DataFrame(review_list, columns = review_columns)
    reviews.to_csv("reviews.csv", index = False)
    print("Gerado arquivo \"reviews.csv\"")

    movies = pd.DataFrame(movie_list, columns = movie_columns)
    movies.to_csv("movies.csv", index = False)
    print("Gerado arquivo \"movies.csv\"")
