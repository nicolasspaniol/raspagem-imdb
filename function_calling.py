import openai
import json
import random


client = openai.OpenAI()


 # A função abaixo só serve pra controlar o formato da resposta do GPT e
 # não executa nenhuma ação
def register_emotions(emotion_0, emotion_1):
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
            },
            "required": ["emotion_0", "emotion_1"]
        }
    }
}]

review = "It doesn't seem possible that an Alamo movie could be worse than John Wayne's great bomb, but this movie is. Sterling Hayden may be the only believable actor and just barely. The supposed 'friendship' between Bowie and Santa Anna?! But one of a host of trite disasters. Only good for a late night laugh and just barely. The physical lay out of the Alamo is not realistic, but the death of the \"Big Three\" is better than Wayne's version--although similar. It's too bad because the story of the Alamo deserved a better treatment. This script shows that it was hacked out when Wayne turned down the movie. Too bad Republic pictures didn't fold before this turkey flew or flopped!"

messages = [
    {
        "role": "system",
        "content": "Given a movie review, your job is to identify and register the THREE MAIN EMOTIONS displayed in the text, in order of prevalence. Here goes the review: "
    },
    {
        "role": "user",
        "content": "REVIEW: " + review
    }
]

# No código que chama o ChatGPT 
response = client.chat.completions.create(
    model = "gpt-3.5-turbo-0125",
    messages = messages,
    tools = tools,
    tool_choice = "required" # <- Importante deixar `required` aqui
).choices[0].message

# A presença de `tool_calls` é garantida pelo argumento `required` acima
tool_call = response.tool_calls[0]
args = json.loads(tool_call.function.arguments)
emotions = [
    args.get("emotion_0"),
    args.get("emotion_1"),
]

print(emotions)
