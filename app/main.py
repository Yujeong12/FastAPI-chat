from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import WebSocket
from typing import List
from pydantic import BaseModel

app = FastAPI()
# index.html 연결
templates = Jinja2Templates(directory="templates")

# WebSocket 연결을 추적하기 위한 연결 리스트=
active_connections: List[WebSocket] = []

# 데이터 저장을 위한 딕셔너리
userdata: dict[str, str] = {'테스트' : '값1'}

# WebSocket 메시지를 위한 모델
class Message(BaseModel):
    username: dict[str, int]
    password:str
    text: str

# 메인 페이지
@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# WebSocket 연결 핸들러
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)  # 새로운 연결을 리스트에 추가
    try:
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            message = Message.parse_raw(data)

            # 존재하지 않는 비밀번호면 유저네임 변경
            if message.password not in userdata:
                userdata[message.password] = message.username[message.password]

            # 모든 연결에 메시지 브로드캐스트
            for connection in active_connections:
                await connection.send_text(f"{userdata[message.password]} : {message.text}")

    finally:
        active_connections.remove(websocket)  # 연결 종료 시 리스트에서 제거

