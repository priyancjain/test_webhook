from fastapi import FastAPI, Request
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
    return JSONResponse(content={"method": "GET", "faqs": fetch_faq(URL)})

@app.post("/faq")
async def post_faq(request: Request):
    body = await request.json()
    print("Webhook triggered with payload:", body)
    faqs = fetch_faq(URL)
    return JSONResponse(content={
        "method": "POST",
        "received_payload": body,
        "faqs": faqs
    })
