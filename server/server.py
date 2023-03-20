import datetime
import json
import uuid
from typing import List, Dict

from pydantic import BaseModel
from util import analyise, checkAns, checkQus, setInterval
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
import time
import re
import json

app = FastAPI()

origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message:
    def __init__(self, msg) -> None:
        temp = json.loads(msg)
        self.type = temp['type']
        self.data = temp["data"]
    #TODO: add analyer

class Employee:
    def __init__(self, websocket: WebSocket, id: str) -> None:
        self.websocket = websocket
        self.eid = id
    @property
    def id(self) -> str:
        return self.eid

class Client:
    def __init__(self, websocket: WebSocket) -> None:
        self.websocket = websocket
        self.uuid = uuid.uuid4() 
        self.chats = []

    @property
    def id(self) -> str:
        return str(self.uuid)

    @property
    def isConnected(self) -> bool:
        return hasattr(self, "connected_employ") 
    
    def connect_to(self, websocket: WebSocket) -> None:
        self.connected_employ = websocket

class ConnectionManager:
    def __init__(self):
        self.clients: Dict[str, Client] = {}
        self.employees: Dict[str, Employee] = {}
        self.last_update  = time.time()

    async def broadcast_to_employees(self, broadcastMsg: dict)->None:
        print(f"Sending {broadcastMsg['type']} to {self.employees} ")
        for employee in self.employees.values():
            await employee.websocket.send_json(broadcastMsg)

    async def connect_client(self, websocket: WebSocket):
        client = Client(websocket)
        await websocket.accept()
        self.clients[client.id] = client
        print(f"Client connected: {client.id}")
        await self.update_client_data()
        return client

    async def connect_employee(self, websocket: WebSocket):
        employee = Employee(websocket, f"id{time.time()}") # TODO: get ID from employee
        await websocket.accept()
        self.employees[employee.id] = employee
        print(f"Employee connected: {employee.id}")
        await self.update_client_data()
        return employee

    async def connect_client_to_employee(self, id:str,  websocket: WebSocket):
        self.clients[id].connect_to(websocket)
        await self.clients[id].websocket.send_json({"type": "connected to employee" , "data":{"connected to employee": True}})
        await websocket.send_json({"type":"akc", "data":{"id": id, "connected": True}})
        print(f"Client {id}, connected to Employee")
        await self.update_client_data()

    async def update_client_data(self):
        unconnected_clients = []
        for client in connectionManager.clients.values():
            if client.isConnected == False:
                unconnected_clients.append(client.id)
        print(f"Unconnected clients are : {unconnected_clients}")
        await self.broadcast_to_employees({"type":"update", "data": {"client list": unconnected_clients}})

    async def send_client_history(self, id:str, websocket: WebSocket):
        history = self.clients[id].chats
        await websocket.send_json({"type": "chat history", "data":{"history":history}})

    async def send_to_client(self, id, msg):
        self.clients[id].chats.append(f"employee: {msg}")
        await self.clients[id].websocket.send_json({"type": "msg", "data":{"msg": msg}})

    async def send_to_employee(self, client:Client, msg):
        client.chats.append(f"client: {msg}")
        await client.connected_employ.send_json({"type":"new_msg", "data": {"msg": msg}})

    async def disconnect_client(self, clientId: str):
        await connectionManager.clients[clientId].websocket.close()
        del connectionManager.clients[clientId]
        await self.update_client_data()

class Transcript:
    def __init__(self, clientID, employeeID):
        self.cId = clientID
        self.eId = employeeID
        self.chatId = employeeID+clientID
        self.chatDate = datetime.datetime.now().date().strftime("%d/%m/%y")
        self.messages = []
        self.lookingForAns = False

    def addMsg(self,text):

        regex = rf"(.*) ({self.cId}|{self.eId}): (.*)"
        match = re.search(regex, text, re.MULTILINE | re.UNICODE | re.DOTALL)
        
        if match:
        
            timestamp, sender, transcript = [match.group(i) for i in range(1,4)]
            analysisResult = analyise(transcript)
            qus, ans = checkQus(transcript)
            
            entry = {
                "mid":len(self.messages),
                "timestamp": timestamp,
                "sender_id": sender,
                "text": transcript,
                "emotion": analysisResult["emotions"].output,
                "sentiment": analysisResult["sentiment"].output
                }
            
            if qus and sender==self.cId:
                entry["isQuestion"] = True
                entry["question"] = qus
                entry["expcted_ans"] = ans
                self.lookingForAns = True
                self.expectedAns = ans
                self.qid = len(self.messages)
            elif self.lookingForAns and sender == self.eId:
                similarity_score = checkAns(transcript, self.expectedAns)
                self.messages[self.qid]["ans"] = transcript
                self.messages[self.qid]["ans_similarity"] = similarity_score
            self.messages.append(entry) 
        else:
            print(f"couldn't find values skipping: {text}")
    
    @property
    def json(self):
        return {"chat_id": self.chatId, 
                "date": self.chatDate, 
                "client": self.cId,
                "employee": self.eId,
                "messages": self.messages}
    #TODO: Add analyzer here only


class Data(BaseModel):
    answer: str
    expectedAns: str        

connectionManager = ConnectionManager()

@app.get("/")
def root():
    return "working fine"

# TODO: add embedding checker for qus asked
# TODO: save chats on exit or just use some REDIS based cache saving techniques 
# TODO: save analytics and details in DB after confirming the structue with team

# @app.post("/query")
# def read_root(msg: Message):
#     res = analyise(msg.msg)
#     qusAsked, ansExpected = checkQus([msg.msg])
#     return {"msg": ansExpected, "analysis": res, "rec": msg, "qus": qusAsked, "ans": ansExpected}

@app.websocket("/client_chat")
async def client_chat(websocket: WebSocket):
    client = await connectionManager.connect_client(websocket)
    await websocket.send_json({"type": "id", "data":{"uuid": client.id}})
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            #TODO: add a loader until employee connects 
            await connectionManager.send_to_employee(client, data["msg"])
    except WebSocketDisconnect:
        await connectionManager.disconnect_client(client.id)


@app.websocket("/employee_chat")
async def employee_chat(websocket: WebSocket):
    employee = await connectionManager.connect_employee(websocket)
    try: 
        while True:
            req = await websocket.receive_text()
            msg = Message(req)

            if msg.type == "connect_client":
                await connectionManager.connect_client_to_employee(msg.data["id"], websocket)
            elif msg.type == "client_history":
                await connectionManager.send_client_history(msg.data["id"], websocket)
            elif msg.type == "send_to_client":
                await connectionManager.send_to_client(msg.data["id"], msg.data["msg"]) 
                # TODO: make it a proper msg and analyze it 
                #     res = analyise(msg.data["msg"])
                #     qusAsked, ansExpected = checkQus([msg.msg])
            else:
                await websocket.send_text("yet to implement")   
    except WebSocketDisconnect:
        del connectionManager.employees[employee.id]
        await websocket.close()

@app.post("/convert")
async def transcript_processing(file: UploadFile = File(default="File to convert to json")):
    raw_file_content = file.file.read().decode("utf-8")
    transcript = Transcript("3a94f155-0b21-4e87-b28f-a0d960be9218", "employeeID")
    for line in raw_file_content.split("~~~"):
        transcript.addMsg(line)
    return transcript.json

@app.post("/erc")
async def expectedResponseChecker(Body:Data):
    similarity_score = checkAns(Body.answer, Body.expectedAns)
    return {"score":similarity_score} 
