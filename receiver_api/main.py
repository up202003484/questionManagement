from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()
latest_question = ""

@app.post("/receive")
async def receive(request: Request):
    global latest_question
    data = await request.json()
    latest_question = data.get("question_text", "")
    return JSONResponse(content={"message": "Received!"})

@app.get("/latest")
async def latest():
    return {"question_text": latest_question}