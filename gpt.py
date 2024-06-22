from openai import OpenAI
import pandas as pd
import json
from math import floor


# Carrega a prompt do sistema em uma variável global
with open("system_prompt.txt") as f:
    global SYSTEM_PROMPT
    SYSTEM_PROMPT = f.read()


# A função abaixo só serve pra controlar o formato da resposta do GPT e
# não executa nenhuma ação
def register_emotions(emotion_0, emotion_1, emotion_2):
    """ Registra as três principais emoções identificadas no filme """
    pass


# Emoções extraídas de https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8402961/
emotions = [
    "joy", "pensiveness", "ecstasy", "acceptance", "sadness", "fear", "interest", "rage", "admiration",
    "amazement", "anger", "vigilance" "boredom", "annoyance", "submission", "serenity", "apprehension",
    "contempt", "surprise", "disapproval", "distraction", "grief", "loathing", "love", "optimism",
    "aggressiveness", "remorse", "anticipation", "awe", "terror", "trust", "disgust"
]

# Ferramentas disponibilizadas ao GPT
tools =[{
    "type": "function",
    "function": {
        "name": register_emotions.__name__,
        "description": register_emotions.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "emotion_0": {"type": "string", "enum": emotions},
                "emotion_1": {"type": "string", "enum": emotions},
                "emotion_2": {"type": "string", "enum": emotions}
            },
            "required": ["emotion_0", "emotion_1", "emotion_2"]
        }
    }
}]


if __name__ == "__main__":
    # Chave lida como variável de ambiente (por enquanto)
    client = OpenAI()
    
    reviews_df = pd.read_csv(r"reviews.csv")
    movies_df = pd.read_csv(r"movies.csv")

    output = []

    total = reviews_df.shape[0]
    percentage = -1
    for i, row in enumerate(reviews_df.itertuples()):
        if floor(100 * i / total) != percentage:
            percentage = floor(100 * i / total)
            print(f"[{"=" * percentage}{" " * (100 - percentage)}] ({percentage}%)", end="\r")

        # https://stackoverflow.com/a/17071908
        movie = movies_df.query(f"movie_id == '{row.movie_id}'").values[0]

        # Incluí o nome do filme pra ajudar o GPT a entender a review
        user_message = f"MOVIE NAME: \"{movie[0]}\"\n" + \
                       f"REVIEW TITLE: \"{row.title}\"\n" + \
                       f"REVIEW BODY: \n{row.comment}"

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

        response = client.chat.completions.create(
            model = "gpt-3.5-turbo-0125",
            messages = messages,
            tools = tools,
            tool_choice = "required" # Força a função a ser chamada
        ).choices[0].message

        tool_call = response.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        output.append({
            "movie_id": row.movie_id,
            "rating": row.rating,
            "emotion_0": args.get("emotion_0"),
            "emotion_1": args.get("emotion_1"),
            "emotion_2": args.get("emotion_2")
        })
    
    emotions_df = pd.DataFrame(output)
    emotions_df.to_csv("emotions.csv", index=False)
