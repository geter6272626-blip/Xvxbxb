import os
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, Any, Dict

app = FastAPI(title="Triverse Cloud MCP Server with Tools")

API_KEY = os.getenv("TRIVERSE_API_KEY")
API_URL = "https://api.triverse.ai/v1/chat/completions"
BASE_URL = "https://xvxbxb.onrender.com"

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Any] = None

# --- 1. MCP Core Endpoint (टूल्स और रिक्वेस्ट हैंडल करने के लिए) ---
@app.post("/mcp")
def mcp_endpoint(request: JSONRPCRequest):
    # जब Claude टूल्स की लिस्ट मांगता है
    if request.method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "result": {
                "tools": [
                    {
                        "name": "triverse_chat",
                        "description": "Send a prompt or message to Triverse AI and get a response.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "prompt": {
                                    "type": "string",
                                    "description": "The message or prompt to send to Triverse AI."
                                }
                            },
                            "required": ["prompt"]
                        }
                    }
                ]
            },
            "id": request.id
        }

    # जब Claude किसी टूल को चलाता है या चैट करता है
    prompt_text = "Hello"
    if request.params:
        if "arguments" in request.params and "prompt" in request.params["arguments"]:
            prompt_text = request.params["arguments"]["prompt"]
        elif "prompt" in request.params:
            prompt_text = request.params["prompt"]

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "default-model",
        "messages": [{"role": "user", "content": prompt_text}]
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        res_data = response.json()
        
        ai_reply = "No response"
        if "choices" in res_data and len(res_data["choices"]) > 0:
            ai_reply = res_data["choices"][0].get("message", {}).get("content", str(res_data))
        else:
            ai_reply = str(res_data)

        return {
            "jsonrpc": "2.0",
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": ai_reply
                    }
                ]
            },
            "id": request.id
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": request.id
        }

# --- 2. OAuth Discovery Metadata (Claude के हैंडشेक के लिए) ---
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

# --- 3. OAuth Authorization Endpoint ---
@app.get("/authorize")
def oauth_authorize(
    response_type: Optional[str] = None,
    client_id: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    state: Optional[str] = None
):
    if redirect_uri:
        separator = "&" if "?" in redirect_uri else "?"
        return RedirectResponse(url=f"{redirect_uri}{separator}code=mock_auth_code_xyz&state={state}")
    return {"status": "authorized", "code": "mock_auth_code_xyz"}

# --- 4. OAuth Token Endpoint ---
@app.post("/token")
@app.post("/oauth/token")
def oauth_token(request: Request):
    return {
        "access_token": API_KEY,
        "token_type": "Bearer",
        "expires_in": 86400
    }

@app.get("/mcp")
def mcp_get():
    return {"status": "online", "protocol": "Model Context Protocol over HTTP with Tools"}

@app.get("/")
def home():
    return {"status": "Triverse MCP Server with Tools is running on Render!"}
    
