from openai import OpenAI
import pandas as pd
import json


# A função abaixo só serve pra controlar o formato da resposta do GPT e
# não executa nenhuma ação
def register_emotions(emotion_0, emotion_1, emotion_2):
    """ Registers the two main emotions displayed in the review, in order of prevalence """
    pass


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
    # while True:
    #     KEY = input("Digite sua chave da api da OpenAI: \n")
    #     if KEY:
    #         break

    KEY = ""

    client = OpenAI(api_key = KEY)
    
    reviews_df = pd.read_csv(r"reviews.csv")

    ids, ratings, emotions_0, emotions_1, emotions_2 = [], [], [], [], []

    for row in reviews_df.itertuples():
        id = row.movie_id
        comment = row.comment
        rating = row.rating

        ids.append(id)
        ratings.append(rating)

        messages = [
            {
                "role": "system",
                "content": "Given a movie review, your job is to identify and register the THREE MAIN EMOTIONS displayed in the text, in order of prevalence. Here goes the review: "
            },
            {
                "role": "user",
                "content": "REVIEW: " + comment
            }
        ]

        response = client.chat.completions.create(
            model = "gpt-3.5-turbo-0125",
            messages = messages,
            tools = tools,
            tool_choice = "required" # <- Importante deixar `required` aqui
        ).choices[0].message

        tool_call = response.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        emotions = [
            args.get("emotion_0"),
            args.get("emotion_1"),
            args.get("emotion_2")
        ]

        if len(emotions) != 3:
            print(f"saíram {len(emotions)} emoções")

        emotions_0.append(emotions[0])
        emotions_1.append(emotions[1])
        emotions_2.append(emotions[2])
    
    emotions_df = {
        "movie_id": ids,
        "rating": ratings,
        "emotion_0": emotions_0,
        "emotion_1": emotions_1,
        "emotion_2": emotions_2
    }

    df = pd.DataFrame(emotions_df)

    df.to_csv("emotions.csv", index=False)