from fastapi import FastAPI, Request, Response, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from kmap import *

ROOT_DIRECTORY = Path(__file__).parent
PARENT_DIRECTORY = ROOT_DIRECTORY.parent
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.mount("/static", StaticFiles(directory=ROOT_DIRECTORY / "frontend" / "build" / "static"), name="static")

@app.get("/favicon.ico")
def read_favicon():
    return FileResponse(ROOT_DIRECTORY / "frontend" /  "build" / "favicon.ico")

## React App + API Calls ##

# Catch-all route for React and other specific FastAPI routes
@app.get("/{path:path}")
async def read_root(request: Request, path: str):
    file_path = ROOT_DIRECTORY / "frontend" / "build" / path
    if file_path.is_file():  # Serve the file if it exists
        return FileResponse(file_path)
    return FileResponse(ROOT_DIRECTORY / "frontend" / "build" / "index.html")  # Serve index.html for React Router

@app.post("/api/generate")
async def generate(request: Request):
    data = await request.json()
    vars = data["variables"]
    minterms = data["minterms"]
    
    num_vars = len(vars)

    # Determine the dimensions of the K-Map
    row_size = 2 ** (math.ceil(num_vars / 2))
    col_size = 2 ** (math.floor(num_vars / 2))

    # Initialize K-Map matrix with zeros
    kmap_matrix = np.zeros((row_size, col_size), dtype=int)

    # Populate K-Map matrix based on the minterms
    for idx, minterm in enumerate(minterms):
        row = idx // col_size
        col = idx % col_size
        kmap_matrix[row][col] = minterm

    # Generate Gray code labels for row and column
    row_labels = gray_code(math.ceil(num_vars / 2))
    col_labels = gray_code(math.floor(num_vars / 2))

    # Call plot_kmap to generate the K-Map
    await plot_kmap(kmap_matrix, row_labels, col_labels, vars)

    # Assuming the image is saved as kmap.png in the same directory
    image_path = ROOT_DIRECTORY / "frontend" / "build" / "kmap.png"
    
    if image_path.is_file():
        return FileResponse(image_path)
    else:
        raise HTTPException(status_code=404, detail="Image not found")