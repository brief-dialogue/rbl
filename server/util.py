from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pysentimiento import create_analyzer
from pysentimiento.preprocessing import preprocess_tweet
from costant import qus, ans
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import threading
import time 
import asyncio

DEBUG = False



def useModel(serveMockRes = False, MockRes:object = "" ):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if serveMockRes:
               return MockRes
            return func(*args, **kwargs)
        return wrapper
    return decorator

analyizer_mock = {"output": "emotion in txt", "emotions": {"happy": 1.0, "sad": 2,}, "sentiment": "this is mock result"}
checkQus_mock = (None, None)

sentanceTransformer, emotion_analyzer, sentiment_analyzer, question_embeddings = None,None,None,None

def load_models():
    # TODO: load models async fashion
    global sentanceTransformer, emotion_analyzer, sentiment_analyzer, question_embeddings

    if sentanceTransformer!=None and emotion_analyzer!=None and sentiment_analyzer!=None and question_embeddings !=None:
        return

    print("loading Sentance Transformer: ")
    sentanceTransformer = SentenceTransformer('bert-base-nli-mean-tokens')
    print("Sentance Transformer Loaded: ")
    print("loading emotional analyzer: ")
    emotion_analyzer = create_analyzer(task="emotion", lang="en")
    print("emotional analyzier loaded: ")
    print("loading sentiment analyzer: ")
    sentiment_analyzer = create_analyzer(task="sentiment", lang="en")
    print("sentiment analyzer loaded: ")

    print("loading embedings: ")
    question_embeddings = sentanceTransformer.encode(qus)
    # answer_embeddings = sentanceTransformer.encode(ans) # currently unused can be used to comapre answer
    print("embeddings loaded: ")

if not DEBUG:
    load_models()

@useModel(DEBUG, analyizer_mock)
def analyise(msg):
    preprocessed_msg = preprocess_tweet(msg)
    emotion = emotion_analyzer.predict(preprocessed_msg)
    sentiment = sentiment_analyzer.predict(preprocessed_msg)
    return {"output": emotion.output, "emotions": emotion, "sentiment": sentiment}

@useModel(DEBUG, checkQus_mock)
def checkQus(sentence):
    sentence_embedding = sentanceTransformer.encode(sentence)
    similarity_score = cosine_similarity([sentence_embedding],question_embeddings)[0]
    if max(similarity_score) > 0.75:
        id = np.argmax(similarity_score)
        return qus[id], ans[id]
    return None, None

@useModel(DEBUG, 0.0)
def checkAns(sentence, expectedAnswer):
    sentence_embedding = sentanceTransformer.encode(sentence)
    expectedAnswer_embedding = sentanceTransformer.encode(expectedAnswer)
    similarity_score = cosine_similarity([sentence_embedding],[expectedAnswer_embedding])[0]
    return str(similarity_score[0])


class setInterval :
    def __init__(self,interval,action) :
        self.interval=interval
        self.action=action
        self.stopEvent=threading.Event()
        thread=threading.Thread(target=self.__setInterval)
        thread.start()

    def __run_action(self, *args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.action(args))
        loop.close()

    
    def __setInterval(self, *args, **kwargs) :
        nextTime=time.time()+self.interval
        while not self.stopEvent.wait(nextTime-time.time()) :
            nextTime+=self.interval
            self.__run_action()

    def cancel(self) :
        self.stopEvent.set()



