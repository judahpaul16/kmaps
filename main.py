from fastapi import FastAPI, Request, Response, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.exceptions import HTTPException
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import requests
import json
import os

ROOT_DIRECTORY = Path(__file__).parent
PARENT_DIRECTORY = ROOT_DIRECTORY.parent
app = FastAPI()

app.mount("/static", StaticFiles(directory=ROOT_DIRECTORY / "frontend" / "build" / "static"), name="static")

@app.get("/favicon.ico")
def read_favicon():
    return FileResponse(ROOT_DIRECTORY / "frontend" /  "build" / "favicon.ico")

## React App + API Calls ##

# Catch-all route for React and other specific FastAPI routes
@app.get("/{path:path}")
async def read_root(request: Request, path: str):
    if path == 'api/callback':
        return await handle_callback(request)
    else:
        return FileResponse(ROOT_DIRECTORY / "frontend" / "build" / "index.html")
    
async def handle_callback(request: Request):
    # Stuff to do after callback
    return