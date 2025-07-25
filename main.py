import time
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

HEADERS = {"User-Agent": "Mozilla/5.0"}
BASE_URL = "https://playaebikes.com/faq/"
faq_data = []

class FAQItem(BaseModel):
    question: str
    answer: str
    url: str

def scrape_faqs():
    global faq_data
    response = requests.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    faq_data = []
    faq_items = soup.select("h3.elementor-post__title")

    for item in faq_items:
        question = item.get_text(strip=True)
        link = item.find('a')['href']
        if not link.startswith("http"):
            link = BASE_URL + link.lstrip("/")

        try:
            faq_response = requests.get(link, headers=HEADERS)
            faq_soup = BeautifulSoup(faq_response.text, 'html.parser')
            main = faq_soup.find('main')
            answer_parts = []

            if main:
                divs = main.find_all('div', recursive=True)
                for div in divs:
                    text = div.get_text(separator="\n", strip=True)
                    if len(text) > 40:
                        answer_parts.append(text)

            answer_text = "\n\n".join(answer_parts).strip()
            if not answer_text:
                answer_text = "Answer not found."
        except Exception as e:
            answer_text = f"Error fetching: {str(e)}"

        faq_data.append({
            "question": question,
            "answer": answer_text,
            "url": link
        })

        time.sleep(0.5)  # rate limiting

@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to the Playa eBikes® FAQ API"}

@app.get("/faqs", response_model=List[FAQItem], tags=["FAQs"])
def get_all_faqs():
    scrape_faqs()
    return faq_data

@app.get("/faq", response_model=Optional[FAQItem], tags=["FAQs"])
def get_faq_by_question(question: str = Query(..., description="Exact FAQ question")):
    q = question.strip().lower()
    for item in faq_data:
        if item["question"].strip().lower() == q:
            return item
    return {"error": "Question not found"}

@app.post("/refresh", tags=["Admin"])
def refresh_data():
    scrape_faqs()
    return {"status": "FAQ data refreshed", "count": len(faq_data)}

# Auto-scrape on app start
scrape_faqs()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True)
