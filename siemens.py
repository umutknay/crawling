from fastapi import FastAPI
from parsel import Selector
import requests

app = FastAPI()

@app.get("/")
def health_check():
    """Health check endpoint for Render"""
    return {"status": "ok"}

@app.get("/image")
def get_image(code: str):
    url = f"https://mall.industry.siemens.com/mall/en/fescomelsaownuy/Catalog/Product?mlfb={code}&SiepCountryCode=OE"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://mall.industry.siemens.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        selector = Selector(text=response.text)
        img = selector.css('meta[property="og:image"]::attr(content)').get()
        
        if not img:
            img = selector.css('meta[name="og:image"]::attr(content)').get()
        
        return {"image_url": img if img else None}

    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}", "image_url": None}
    except Exception as e:
        return {"error": f"Processing error: {str(e)}", "image_url": None}
