import os
import requests
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

app = FastAPI(title="Triverse Cloud MCP Server")

# यह सीधे क्लाउड के Environment Variable से की पढ़ेगा (कोड्स में कुछ नहीं लिखा)
API_KEY = os.getenv("TRIVERSE_API_KEY")
API_URL = "https://api.triverse.ai/v1/chat/completions"

class PromptRequest(BaseModel):
    prompt: str

@app.post("/mcp")
def mcp_endpoint(data: PromptRequest, authorization: str = Header(None)):
    expected_auth = f"Bearer {API_KEY}"
    if not authorization or authorization != expected_auth:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")
    
    headers = {
        "Authorization": expected_auth,
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "default-model",
        "messages": [{"role": "user", "content": data.prompt}]
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def home():
    return {"status": "Secure Triverse MCP Server is running!"}
    
