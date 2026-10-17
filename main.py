import os
import requests
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Any, Dict, List

app = FastAPI(title="Triverse Cloud MCP Server")

API_KEY = os.getenv("TRIVERSE_API_KEY")
API_URL = "https://api.triverse.ai/v1/chat/completions"

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Any] = None

@app.post("/mcp")
def mcp_endpoint(request: JSONRPCRequest, authorization: Optional[str] = Header(None)):
    # अगर क्लाइंट ऑथेंटिकेशन भेज रहा है, तो ठीक, वरना एनवायरनमेंट वाली की इस्तेमाल होगी
    expected_auth = f"Bearer {API_KEY}"
    
    # यदि Claude या कोई टूल सीधे JSON-RPC या प्रॉम्प्ट भेज रहा है
    prompt_text = "Hello"
    if request.params and "prompt" in request.params:
        prompt_text = request.params["prompt"]
    elif request.method:
        prompt_text = request.method

    headers = {
        "Authorization": expected_auth,
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "default-model",
        "messages": [{"role": "user", "content": prompt_text}]
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        res_data = response.json()
        
        # MCP / JSON-RPC रिस्पॉन्स फॉर्मेट
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

@app.get("/mcp")
def mcp_get():
    # अगर कोई ब्राउज़र या कनेक्टर GET रिक्वेस्ट करे तो MCP हैंडशेक की जानकारी दे
    return {
        "status": "online",
        "protocol": "Model Context Protocol over HTTP",
        "endpoints": {"mcp": "POST /mcp"}
    }

@app.get("/")
def home():
    return {"status": "Triverse MCP Server is running successfully on Render!"}
        
