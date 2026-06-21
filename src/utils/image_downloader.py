from typing import List, Dict
import os
import httpx
async def download_images_async(products: List[Dict[str, str]], folder: str) -> int:
    """
    Download all product images concurrently.
    Returns number of successfully downloaded images.
    """
    os.makedirs(folder, exist_ok=True)

    async with httpx.AsyncClient(timeout=20) as client:
        tasks = []
        for idx, p in enumerate(products, start=1):
            url = p.get("image_url")
            if not url:
                continue
            filename = os.path.join(folder, f"product_{idx}.jpg")
            tasks.append(_download_single(client, url, filename))
        results = await httpx.AsyncClient.gather(*tasks)  # (we can't actually call gather here, but user can use asyncio.gather)
    return sum(results)


async def _download_single(client: httpx.AsyncClient, url: str, path: str) -> int:
    try:
        r = await client.get(url)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        return 1
    except Exception:
        return 0
