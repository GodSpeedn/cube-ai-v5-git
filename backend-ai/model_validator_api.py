from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import List, Dict, Any
import openai
from openai import OpenAI
import google.generativeai as genai
from mistralai.client import MistralClient
import requests
import os

app = FastAPI(title="AI Model Validator API")

class ListModelsRequest(BaseModel):
    provider: str
    api_key: str

class CheckModelRequest(BaseModel):
    provider: str
    api_key: str
    model_id: str

@app.post("/api/list-models")
async def list_models(request: ListModelsRequest = Body(...)):
    try:
        client = None
        models = []
        match request.provider.lower():
            case "openai":
                client = OpenAI(api_key=request.api_key)
                response = client.models.list()
                models = [m.id for m in response.data]
            case "xai" | "grok":
                # xAI API is OpenAI-compatible (base_url: https://api.x.ai/v1)
                client = OpenAI(api_key=request.api_key, base_url="https://api.x.ai/v1")
                response = client.models.list()
                models = [m.id for m in response.data]
            case "mistral":
                client = MistralClient(api_key=request.api_key)
                response = client.list_models()
                models = [m.id for m in response.data]
            case "gemini":
                genai.configure(api_key=request.api_key)
                # Gemini doesn't have a direct /models list via SDK; fetch from known models or API
                # Use REST call to https://generativelanguage.googleapis.com/v1beta/models
                url = "https://generativelanguage.googleapis.com/v1beta/models"
                headers = {"x-goog-api-key": request.api_key}
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    models = [m["name"] for m in data.get("models", [])]
                else:
                    raise HTTPException(status_code=400, detail="Failed to fetch Gemini models")
            case _:
                raise HTTPException(status_code=400, detail="Unsupported provider")
        
        return {"provider": request.provider, "models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/check-model")
async def check_model(request: CheckModelRequest = Body(...)):
    list_req = ListModelsRequest(provider=request.provider, api_key=request.api_key)
    models_data = await list_models(list_req)
    models = models_data["models"]
    is_valid = request.model_id in models
    return {
        "provider": request.provider,
        "model_id": request.model_id,
        "is_valid": is_valid,
        "available_models": models
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
