from fastapi import FastAPI
from bs4 import BeautifulSoup
import requests

app = FastAPI()

@app.get("/scrape-playa-faq")
def scrape_faq():
    url = "https://playaebikes.com/faq/"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": f"Failed to fetch page. Status code: {response.status_code}"}

    soup = BeautifulSoup(response.text, "html.parser")
    faq_items = soup.select(".elementor-accordion-item")

    faq_data = []

    for item in faq_items:
        question_tag = item.select_one(".elementor-tab-title")
        answer_tag = item.select_one(".elementor-tab-content")
        if question_tag and answer_tag:
            faq_data.append({
                "question": question_tag.get_text(strip=True),
                "answer": answer_tag.get_text(strip=True)
            })

    return {"faqs": faq_data}
