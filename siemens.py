from fastapi import FastAPI
from parsel import Selector
import requests
from urllib.parse import urljoin

app = FastAPI()

@app.get("/")
def health_check():
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
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        selector = Selector(text=response.text)
        
        # Ürün resmi
        img = selector.css("img.productPicture::attr(src)").get()
        if img:
            img = urljoin(url, img)

        # Ürün detayları tablosu
        product_details = {}
        details_table = selector.css("table.ProductDetailsTable")
        
        if details_table:
            rows = details_table.css("tr")
            current_section = None
            allowed_sections = {"Product", "Additional Product Information"}
            
            for row in rows:
                tds = row.css("td")
                if len(tds) == 1:
                    section = tds[0].xpath('normalize-space(string())').get()
                    if section in allowed_sections:
                        current_section = section
                        product_details[current_section] = {}
                    else:
                        current_section = None
                    continue
                
                if len(tds) >= 2 and current_section:
                    header = tds[0].xpath('normalize-space(string())').get()
                    value = tds[1].xpath('normalize-space(string())').get()
                    if header:
                        product_details[current_section][header] = value if value else ""

        return {
            "code": code, 
            "image_url": img, 
            "url": url,
            "product_details": product_details
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}", "code": code, "image_url": None, "product_details": {}}
    except Exception as e:
        return {"error": f"Processing error: {str(e)}", "code": code, "image_url": None, "product_details": {}}