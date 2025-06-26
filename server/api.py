# server/api.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# Example model
class Asset(BaseModel):
    name: str
    path: str

@router.get("/")
def read_root():
    return {"message": "API is running"}

@router.get("/assets")
def list_assets():
    # Replace with actual project-aware logic later
    return [
        {"name": "Tree", "path": "/path/to/tree.blend"},
        {"name": "Rock", "path": "/path/to/rock.blend"},
    ]

@router.post("/import")
def import_asset(asset: Asset):
    print(f"Importing: {asset.name} from {asset.path}")
    return {"status": "imported", "asset": asset.name}
