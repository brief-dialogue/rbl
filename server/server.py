from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pysentimiento import create_analyzer
from pysentimiento.preprocessing import preprocess_tweet
from costant import qus, ans
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

sentanceTransformer = SentenceTransformer('bert-base-nli-mean-tokens')
emotion_analyzer = create_analyzer(task="emotion", lang="en")
sentiment_analyzer = create_analyzer(task="sentiment", lang="en")

question_embeddings = sentanceTransformer.encode(qus)
answer_embeddings = sentanceTransformer.encode(ans)

app = FastAPI()

origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    msg: str


@app.get("/")
def root():
    return "working fine"


@app.post("/query")
def read_root(msg: Message):
    res = analyise(msg.msg)
    # TODO: add embedding checker for qus asked
    qusAsked, ansExpected = checkQus([msg.msg])
    return {"msg": ansExpected, "analysis": res, "rec": msg, "qus": qusAsked, "ans": ansExpected}


def analyise(msg):
    preprocessed_msg = preprocess_tweet(msg)
    emotion = emotion_analyzer.predict(preprocessed_msg)
    sentiment = sentiment_analyzer.predict(preprocessed_msg)
    return {"output": emotion.output, "emotions": emotion.probas, "sentiment": sentiment}


def checkQus(sentence):
    sentence_embeddings = sentanceTransformer.encode(sentence)
    dist = cosine_similarity(sentence_embeddings,question_embeddings)[0]
    if max(dist) > 0.75:
        id = np.argmax(dist)
        return qus[id], ans[id]
    return None, None
    
