from concurrent.futures import ThreadPoolExecutor
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

async def loadSentenceTransformer():
    global sentanceTransformer
    sentanceTransformer = SentenceTransformer('bert-base-nli-mean-tokens')

async def loadAnalyzer(type):
    global emotion_analyzer, sentiment_analyzer
    if type=="emotion":
        emotion_analyzer = create_analyzer(task=type, lang="en")
    elif type=="sentiment":
        sentiment_analyzer = create_analyzer(task=type, lang="en")


async def load_models():
    global question_embeddings
    task1 = await asyncio.gather(loadSentenceTransformer(),
                                 asyncio.create_task(loadAnalyzer("emotion")),
                                 asyncio.create_task(loadAnalyzer("sentiment")))
    question_embeddings = sentanceTransformer.encode(qus)  
    print(task1)

if not DEBUG:
    try:
        asyncio.get_running_loop()
        with ThreadPoolExecutor(1) as pool:
            result = pool.submit(lambda: asyncio.run(load_models())).result()
    except RuntimeError:
        result = asyncio.run(load_models())

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

@useModel(DEBUG, 0.369)
def checkAns(sentence, expectedAnswer):
    sentence_embedding = sentanceTransformer.encode(sentence)
    expectedAnswer_embedding = sentanceTransformer.encode(expectedAnswer)
    similarity_score = cosine_similarity([sentence_embedding],[expectedAnswer_embedding])[0]
    return similarity_score[0]


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



