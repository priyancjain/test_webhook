from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)
faq_data = []

HEADERS = {"User-Agent": "Mozilla/5.0"}
BASE_URL = "https://playaebikes.com/faq/"

def scrape_faqs():
    global faq_data
    response = requests.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    faq_data = []
    faq_items = soup.select("h3.elementor-post__title")

    for item in faq_items:
        question = item.get_text(strip=True)
        link = item.find('a')['href']

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

        time.sleep(0.5)  # Rate limiting

@app.route("/faqs", methods=["GET"])
def get_all_faqs():
    return jsonify(faq_data)

@app.route("/faq", methods=["GET"])
def get_faq_by_question():
    q = request.args.get("question", "").strip().lower()
    for item in faq_data:
        if item["question"].strip().lower() == q:
            return jsonify(item)
    return jsonify({"error": "Question not found"}), 404

@app.route("/refresh", methods=["POST"])
def refresh_data():
    scrape_faqs()
    return jsonify({"status": "FAQ data refreshed", "count": len(faq_data)})

if __name__ == "__main__":
    print("Scraping FAQs initially...")
    scrape_faqs()
    app.run(debug=True)
