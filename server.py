# server.py
from fastapi import FastAPI
from pydantic import BaseModel
import threading
import uvicorn
app = FastAPI()

class Asset(BaseModel):
    name: str
    path: str

@app.get("/")
def read_root():
    return {"message": "API is running"}

@app.get("/assets")
def list_assets():
    return [
        {"name": "Tree", "path": "/path/to/tree.blend"},
        {"name": "Rock", "path": "/path/to/rock.blend"},
    ]

@app.post("/import")
def import_asset(asset: Asset):
    print(f"Importing: {asset.name} from {asset.path}")
    return {"status": "imported", "asset": asset.name}

def start(port):
    threading.Thread(
        target=uvicorn.run,
        kwargs={"app": app, "host": "127.0.0.1", "port": port, "log_level": "info"},
        daemon=True
    ).start()