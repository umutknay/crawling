from fastapi import FastAPI, HTTPException
import requests
#from bs4 import BeautifulSoup
from parsel import Selector
from urllib.parse import urljoin

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.get("/siemens-image")
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
    

# @app.get("/sick-image/{product_code}")
# def download_image(product_code: str):
#     url = f'https://www.sick.com/tr/tr'
    
#     # Belirtilen URL'ye GET isteği gönderme işlemi
#     response_search_page = requests.get(url)
    
#     if response_search_page.status_code == 200:
#         soup = BeautifulSoup(response_search_page.content, 'html.parser')
        
#         # Bulunan ürünün URL'sini bul
#         product_url = None
#         for a_tag in soup.find_all('a', href=True):
#             if '/tr/tr/products/' in a_tag['href'] and str(product_code) in a_tag['href']:
#                 product_url = f'https://www.sick.com{a_tag["href"]}'
#                 break
                
#         # Eğer ürün sayfası URL'si bulunamazsa hata mesajı döndür
#         if not product_url:
#             raise HTTPException(status_code=404, detail=f"{product_code} için bir ürün url'si bulunamadı.")
        
#         # Ürün sayfasına gidin ve resmi indirin
#         response_product_page = requests.get(product_url)
        
#         soup_product = BeautifulSoup(response_product_page.content, 'html.parser')
            
#         # Resim URL'sini bul (örnek olarak en başta yer alan büyük bir resme bakıyoruz)
#         image_tag = soup_product.find('img', {'class': 'product-image'})
#         if image_tag and 'src' in image_tag.attrs:
#             image_url = image_tag['src']
            
#             if not image_url.startswith('http'):
#                 image_url = f'https://www.sick.com{image_url}'
                
#             # İndirme işlemi
#             response_image = requests.get(image_url)
            
#             if response_image.status_code == 200:
#                 return {'image': response_image.content}
#             else:
#                 raise HTTPException(status_code=500, detail="Resim indirme hatası.")
#         else:
#             raise HTTPException(status_code=404, detail=f"{product_code} için bir ürün resmi bulunamadı.")
#     else:
#         raise HTTPException(status_code=response_search_page.status_code, detail='Belirtilen URL için bağlantı sağlanamadı.')
