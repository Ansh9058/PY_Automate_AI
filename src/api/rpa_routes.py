from fastapi import APIRouter
from src.services.rpa_service import get_website_title

router = APIRouter()

@router.get("/rpa/title")
def fetch_title(url: str):
    return get_website_title(url)