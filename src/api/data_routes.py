from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup

router = APIRouter(prefix="/data", tags=["Advanced Data Processing"])

logger = logging.getLogger(__name__)

# -------------------------------------------------
# MODELS
# -------------------------------------------------

class RawDataRequest(BaseModel):
    data: List[Dict[str, Any]]


class TransformRequest(BaseModel):
    data: List[Dict[str, Any]]
    rename_keys: Dict[str, str] | None = None
    drop_keys: List[str] | None = None


class URLScrapeRequest(BaseModel):
    url: str
    selectors: Dict[str, str]


# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def clean_text(value: Any) -> Any:
    if isinstance(value, str):
        value = value.strip()
        value = re.sub(r"\s+", " ", value)
        return value
    return value


# -------------------------------------------------
# ENDPOINTS
# -------------------------------------------------

@router.get("/health")
async def data_health():
    return {"status": "data routes operational"}


# -------------------------------------------------
# CLEAN DATA
# -------------------------------------------------

@router.post("/clean")
async def clean_data(payload: RawDataRequest):
    """
    Cleans raw dataset:
    - trims text
    - removes empty fields
    - normalizes whitespace
    """
    cleaned = []

    for row in payload.data:
        clean_row = {
            k: clean_text(v)
            for k, v in row.items()
            if v not in ["", None, []]
        }
        cleaned.append(clean_row)

    logger.info("Cleaned %d records", len(cleaned))
    return {
        "status": "success",
        "records": len(cleaned),
        "data": cleaned,
    }


# -------------------------------------------------
# TRANSFORM DATA
# -------------------------------------------------

@router.post("/transform")
async def transform_data(payload: TransformRequest):
    """
    Transforms dataset:
    - rename keys
    - drop keys
    """
    transformed = []

    for row in payload.data:
        new_row = dict(row)

        if payload.rename_keys:
            for old, new in payload.rename_keys.items():
                if old in new_row:
                    new_row[new] = new_row.pop(old)

        if payload.drop_keys:
            for key in payload.drop_keys:
                new_row.pop(key, None)

        transformed.append(new_row)

    return {
        "status": "success",
        "records": len(transformed),
        "data": transformed,
    }


# -------------------------------------------------
# WEB SCRAPING (NON-SELENIUM)
# -------------------------------------------------

@router.post("/scrape-url")
async def scrape_url(payload: URLScrapeRequest):
    """
    Lightweight HTML scraping (requests + BeautifulSoup)
    """
    try:
        response = requests.get(payload.url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    soup = BeautifulSoup(response.text, "html.parser")
    result = {}

    for key, selector in payload.selectors.items():
        element = soup.select_one(selector)
        result[key] = element.get_text(strip=True) if element else None

    return {
        "status": "success",
        "url": payload.url,
        "data": result,
    }


# -------------------------------------------------
# END-TO-END DATA PIPELINE
# -------------------------------------------------

@router.post("/process")
async def process_data(payload: RawDataRequest):
    """
    Full pipeline:
    - Clean
    - Normalize
    - Convert to structured dataframe
    """
    if not payload.data:
        raise HTTPException(status_code=400, detail="No data provided")

    df = pd.DataFrame(payload.data)

    # Clean text columns
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].apply(clean_text)

    df = df.dropna(how="all")

    return {
        "status": "success",
        "records": len(df),
        "columns": list(df.columns),
        "preview": df.head(5).to_dict(orient="records"),
    }
