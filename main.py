from fastapi import FastAPI
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
import requests

app = FastAPI()

URL = "https://playaebikes.com/faq/"

def fetch_faq(url):
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    faq = {}
    for section in soup.select("h2"):
        category = section.get_text(strip=True)
        ul = section.find_next_sibling("ul")
        if not ul:
            continue
        questions = [li.get_text(strip=True).lstrip("• ").lstrip("* ") for li in ul.find_all("li")]
        faq[category] = questions

    return faq

@app.get("/faq")
def get_faq():
    try:
        faq_data = fetch_faq(URL)
        return JSONResponse(content={"faqs": faq_data})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
