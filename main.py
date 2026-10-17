import os
import requests
from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, Any, Dict

app = FastAPI(title="Triverse Cloud MCP Server")

API_KEY = os.getenv("TRIVERSE_API_KEY")
API_URL = "https://api.triverse.ai/v1/chat/completions"
BASE_URL = "https://xvxbxb.onrender.com"

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

# --- 1. OAuth Discovery Metadata (ताकि Claude को रास्ते पता चलें) ---
@app.get("/.well-known/oauth-authorization-server")
@app.get("/.well-known/openid-configuration")
def oauth_metadata():
    return {
        "issuer": BASE_URL,
        "authorization_endpoint": f"{BASE_URL}/authorize",
        "token_endpoint": f"{BASE_URL}/token",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "client_credentials"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic", "none"]
    }

# --- 2. OAuth Authorization Endpoint ---
@app.get("/authorize")
def oauth_authorize(
    response_type: Optional[str] = None,
    client_id: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    state: Optional[str] = None
):
    if redirect_uri:
        # क्लाइंट को तुरंत ऑथ कोड के साथ रीडायरेक्ट कर देगा
        return RedirectResponse(url=f"{redirect_uri}?code=mock_auth_code_xyz&state={state}")
    return {"status": "authorized", "code": "mock_auth_code_xyz"}

# --- 3. OAuth Token Endpoint ---
@app.post("/token")
@app.post("/oauth/token")
def oauth_token():
    return {
        "access_token": API_KEY,
        "token_type": "Bearer",
        "expires_in": 86400
    }

@app.get("/mcp")
def mcp_get():
    return {"status": "online", "protocol": "Model Context Protocol over HTTP"}

@app.get("/")
def home():
    return {"status": "Triverse MCP Server is running successfully on Render!"}
        
