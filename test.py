import requests
import json

API_KEY = "dd42a017f0d44991a87b0da03bf36840"

# Refined categories for local Indian context
CATEGORIES = ["local news", "district news", "village", "urban", "rural"]
BASE_URL = "https://newsapi.org/v2/everything"

all_news = []

# Fetch data from 5th April 2026
target_date = "2026-04-01"

for cat in CATEGORIES:
    # Combining category with 'India' to ensure local context
    query = f"India {cat}"
    
    params = {
        "q": query,
        "from": target_date,
        "to": target_date,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": 20, # Reduced per category to keep a diverse mix
        "apiKey": API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if data.get("status") != "ok":
        print(f"Error fetching {cat}: {data.get('message')}")
        continue

    total = data.get("totalResults", 0)
    print(f"{cat} news fetched for {target_date}: {total} total results found")

    for article in data.get("articles", []):
        news_item = {
            "category": cat,
            "title": article.get("title"),
            "content": article.get("description"),
            "image": article.get("urlToImage"),
            "source": article.get("source", {}).get("name"),
            "published_at": article.get("publishedAt"),
            "url": article.get("url")
        }

        if news_item["title"]:
            all_news.append(news_item)

    print(f"{cat} news fetched")

# save to JSON file
with open("india_news.json", "w", encoding="utf-8") as f:
    json.dump(all_news, f, indent=4, ensure_ascii=False)

print(f"Total articles saved: {len(all_news)}")