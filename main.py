import os
import requests
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Any, Dict

app = FastAPI(title="Triverse Cloud MCP Server")

API_KEY = os.getenv("TRIVERSE_API_KEY")
API_URL = "https://api.triverse.ai/v1/chat/completions"

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Any] = None

@app.post("/mcp")
def mcp_endpoint(request: JSONRPCRequest):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt_text = "Hello"
    if request.params and "prompt" in request.params:
        prompt_text = request.params["prompt"]
    elif request.method:
        prompt_text = request.method

    payload = {
        "model": "default-model",
        "messages": [{"role": "user", "content": prompt_text}]
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        res_data = response.json()
        return {
            "jsonrpc": "2.0",
            "result": res_data,
            "id": request.id
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": request.id
        }

# --- यहाँ नए ऑथेंटिकेशन / OAuth एंडपॉइंट्स जोड़े गए हैं ताकि 404 Not Found न आए ---
@app.get("/authorize")
def oauth_authorize(response_type: Optional[str] = None, client_id: Optional[str] = None, redirect_uri: Optional[str] = None, state: Optional[str] = None):
    # सीधे ऑथराइजेशन कोड पास कर देगा ताकि ऐप आगे बढ़ जाए
    if redirect_uri:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=f"{redirect_uri}?code=mock_auth_code_123&state={state}")
    return {"status": "authorized", "code": "mock_auth_code_123"}

@app.post("/token")
@app.post("/oauth/token")
def oauth_token():
    return {
        "access_token": API_KEY,
        "token_type": "Bearer",
        "expires_in": 3600
    }

@app.get("/mcp")
def mcp_get():
    return {"status": "online", "protocol": "Model Context Protocol over HTTP"}

@app.get("/")
def home():
    return {"status": "Triverse MCP Server is running successfully on Render!"}
        
