from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn
from typing import Optional
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import your ML models and utilities
from models.chatbot import Chatbot
from models.forecasting import TimeSeriesForecaster
from utils.rag import RAGSystem

app = FastAPI(title="Data Science Portfolio")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

# Create directories if they don't exist
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Templates
templates = Jinja2Templates(directory=str(templates_dir))

# Initialize ML models
chatbot = Chatbot()
forecaster = TimeSeriesForecaster()
rag_system = RAGSystem()

@app.head("/health")
@app.get("/health")
async def health_check():
    """
    Health check endpoint that responds to both HEAD and GET requests.
    This endpoint is used by Azure's load balancers and monitoring systems.
    Returns:
        Response: HTTP 200 if healthy, 500 if unhealthy
    """
    try:
        # Check if models are initialized
        if not all([chatbot, forecaster, rag_system]):
            logger.error("One or more ML models failed to initialize")
            return Response(status_code=500)
            
        # Check if static and template directories exist
        if not (static_dir.exists() and templates_dir.exists()):
            logger.error("Required directories are missing")
            return Response(status_code=500)
            
        # If all checks pass, return 200
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return Response(status_code=500)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "title": "Data Science Portfolio"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering home page: {str(e)}")

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    try:
        return templates.TemplateResponse(
            "about.html",
            {"request": request, "title": "About Me"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering about page: {str(e)}")

@app.get("/projects", response_class=HTMLResponse)
async def projects(request: Request):
    try:
        return templates.TemplateResponse(
            "projects.html",
            {"request": request, "title": "Projects"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering projects page: {str(e)}")

@app.get("/skills", response_class=HTMLResponse)
async def skills(request: Request):
    try:
        return templates.TemplateResponse(
            "skills.html",
            {"request": request, "title": "Skills & Tools"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering skills page: {str(e)}")

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    try:
        return templates.TemplateResponse(
            "contact.html",
            {"request": request, "title": "Contact"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering contact page: {str(e)}")

# API endpoints for interactive features
@app.post("/api/chat")
async def chat(message: str = Form(...)):
    try:
        response = await chatbot.get_response(message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/forecast")
async def forecast(data: str = Form(...)):
    try:
        forecast_result = await forecaster.predict(data)
        return {"forecast": forecast_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rag")
async def rag_query(query: str = Form(...)):
    try:
        response = await rag_system.get_response(query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 9000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"Starting server on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) 