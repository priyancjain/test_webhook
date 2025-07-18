from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
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

# HEAD request to validate webhook (used by Zoho)
@app.head("/faq")
async def handle_head():
    return Response(status_code=200)

# POST request to trigger scraping
@app.post("/faq")
async def webhook(request: Request):
    try:
        data = await request.json()
        faqs = fetch_faq(URL)
        total_qs = sum(len(qs) for qs in faqs.values())

        return JSONResponse(content={
            "action": {
                "type": "reply",
                "value": f"✅ Fetched {total_qs} FAQs successfully."
            },
            "faq_count": total_qs,
            "categories": list(faqs.keys())
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "action": {
                "type": "reply",
                "value": "❌ Failed to fetch FAQs. Please try again later."
            },
            "error": str(e)
        })
