""" Módulo responsável pela extração de dados do IMDb """

import re
from bs4 import BeautifulSoup
import requests
import json
import urllib
import pandas as pd
from enum import Enum


class ReviewSorting(Enum):
    FEATURED = "curated"
    REVIEW_DATE = "submissionDate"
    TOTAL_VOTES = "totalVotes"
    PROFILIC_REVIEWER = "reviewVolume"
    REVIEW_RATING = "userRating"


class SortingDirection(Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"


def find_id(movie_title: str, year: int) -> str:
    """
    Procura o ID do filme a partir das sugestões retornadas pelo IMDb quando
    se pesquisa pelo nome do filme. Caso não encontre, retorna `None`
    """

    # Higieniza o nome do filme para passá-lo como parâmetro:
    # "Nome do filme" => "Nome%20do%20filme"
    encoded_title = urllib.parse.quote(movie_title)

    url = f"https://v3.sg.media-imdb.com/suggestion/x/{encoded_title}.json?includeVideos=0"
    response = json.loads(requests.get(url).content)
    suggestions = response["d"]

    for suggestion in suggestions:
        # Verifica se a sugestão é um tipo de filme. As sugestões podem
        # incluir atores, séries, etc. e mesmo os filmes podem ter
        # categorias diferentes, portanto é necessário e suficiente garantir
        # que "movie" esteja no tipo da sugestão
        is_movie = "qid" in suggestion and "movie" in suggestion["qid"]

        # Verifica se o nome bate, supondo que `movie_title` esteja escrito
        # corretamente e em inglês
        title_matches = suggestion["l"].lower() == movie_title.lower()

        # Calcula a diferença entre o ano (de lançamento do filme) exibido
        # no IMDb e contido no dataset. Idealmente eles deveriam ser iguais,
        # mas dependendo do que cada site considera o ano de lançamento,
        # pode haver uma diferença de um ano entre os dois
        year_error = 0 if not "y" in suggestion else suggestion["y"] - year

        # A partir das condições a seguir, podemos concluir que a sugestão se
        # refere ao filme correto
        if title_matches and -1 <= year_error <= 1 and is_movie:
            return suggestion["id"]

    return None


def get_reviews(movie_id: str, count: int, sorting: ReviewSorting, direction: SortingDirection) -> list[str]:
    """
    Faz a raspagens das primeiras `count` reviews, caso existam, do filme
    com o `id` dado, na ordem passada como parâmetro
    """

    assert isinstance(sorting, ReviewSorting)
    assert isinstance(direction, SortingDirection)

    url = f"https://www.imdb.com/title/{movie_id}/reviews?sort={sorting}&dir={direction}&ratingFilter=0"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    review_list = soup.select("div.lister-list div.review-container")
    assert review_list != None
    
    while len(review_list) < count:
        # Emula o request que seria feito caso o usuário apertasse o botão
        # "Load More" na página de reviews

        load_more_button = soup.select_one("div.load-more-data")

        if load_more_button == None or not "data-key" in load_more_button:
             # Provavelmente acabaram as reviews
             count = len(review_list)
             break

        page = load_more_button["data-ajaxurl"]
        pagination_key = load_more_button["data-key"]
        page_response = requests.get(f"https://www.imdb.com{page}&paginationKey={pagination_key}")

        inner_soup = BeautifulSoup(page_response.text, "lxml")
        review_list.extend(inner_soup.select("div.lister-list div.review-container"))

    output = []

    for i in range(count):
        review = review_list[i]

        # O primeiro <span> dentro do <span class="rating-..."> é
        # a nota dada pelo usuário, de 0 a 10 (opcional)
        rating_span = review.select_one("span.rating-other-user-rating")
        rating = None if rating_span == None else int(rating_span.find("span").text)

        # O comentário é obrigatório
        comment = review.select_one("div.content > div.text").text
        
        # Quebras de linhas são substituídas por ";", o que não deve afetar
        # a interpretação dos dados
        comment = comment.replace("\r", "").replace("\n", ";")

        # O título é obrigatório
        title = review.select_one("a.title").text.strip(" \n")

        # Pega uma frase do tipo "10 of 15 found this helpful" e
        # extrai os números como inteiros
        helpful_message = review.select_one("div.actions")
        if helpful_message != None: 
            pattern = r"\s*([0-9,]+) out of ([0-9,]+) [\s\S]+"
            count, total = re.match(pattern, helpful_message.text).groups()
            # Remove as vírgulas dos milhares ("2,024")
            helpful_count = int(count.replace(",", ""))
            helpful_total = int(total.replace(",", ""))
        else:
            helpful_count = None
            helpful_total = None

        # A presença dessa div indica que há spoilers na review
        has_spoiler = review.select_one("span.spoiler-warning") != None

        output.append({
            "movie_id": movie_id,
            "title": title,
            "comment": comment,
            "rating": rating,
            "helpful_count": helpful_count,
            "helpful_total": helpful_total,
            "has_spoiler": has_spoiler
        })

    return output


if __name__ == "__main__":
    dataframe = pd.read_csv(r"dataset/the_oscar_award.csv")
    filtered = dataframe[dataframe["category"] == "WRITING (Original Story)"]

    review_list = []
    movie_list = []

    # https://stackoverflow.com/a/15943975
    print(f"{filtered.shape[0]} filmes encontrados\n----------")

    for i, row in enumerate(filtered.itertuples()):
        year = row.year_film
        id = find_id(row.film, year)

        print(str(i + 1).ljust(5, " "), end = "")

        if id == None:
            print(f"ID de \"{row.film}\" não encontrado")
            continue

        print(f"Raspando reviews de \"{row.film}\" ({id})...")

        movie_list.append({
            "movie_id": id,
            "movie_title": row.film,
            "oscar_category": row.category,
            "oscar_winner": row.winner
        })
        review_list.extend(get_reviews(id, 25, ReviewSorting.TOTAL_VOTES, SortingDirection.DESCENDING))

    print() # Linha em branco

    reviews = pd.DataFrame(review_list)
    reviews.to_csv("reviews.csv", index = False)
    print("Gerado arquivo \"reviews.csv\"")

    movies = pd.DataFrame(movie_list)
    movies.to_csv("movies.csv", index = False)
    print("Gerado arquivo \"movies.csv\"")
