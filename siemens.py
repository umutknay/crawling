from fastapi import FastAPI
from scrapling.fetchers import Fatcher

app=FastAPI()

@app.get("/image")
def get_image(code:str):
    url=f""

    try:
        page=Fatcher.get(url)
        img=page.css('meta[property="og:image"]::attr(content)').get()
        if not img:
            images=page.css('meta[property="og:image"]::attr(content)').get()
            img=images[0] if images else None
        return {"image_url": img}

    except Exception as e:
        return {"error": str(e)}