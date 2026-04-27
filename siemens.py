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

    try:
        response = requests.get(url, timeout=10)
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
