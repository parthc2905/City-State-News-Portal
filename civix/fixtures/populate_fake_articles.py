import os
import django
import random
from datetime import datetime
from django.utils.text import slugify

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civix.settings')
django.setup()

from news.models import News_article  # adjust app name if different

titles = [
    "Market Trends Update", "City Development योजना", "Education Reform Insights",
    "Tech Innovation Report", "Healthcare Advances", "Global Affairs Analysis",
    "Startup Ecosystem Growth", "Climate Change Impact", "Sports Championship Highlights",
    "Political Debate Overview", "Travel Industry Recovery", "Automobile Sector Growth",
    "Agriculture Policy Update", "Job Market Trends", "Weather Alert Report"
]

long_content = """
In a significant development, experts and officials have highlighted multiple aspects influencing the current scenario.
The situation reflects broader trends observed across industries and regions, indicating structural shifts and evolving priorities.

Detailed analysis suggests that stakeholders are adapting to new challenges while leveraging opportunities for growth and stability.
Several initiatives have been introduced to address emerging concerns, focusing on long-term sustainability and operational efficiency.

Furthermore, data-driven insights reveal measurable improvements in performance metrics, although certain risks remain under observation.
Authorities continue to monitor developments closely and are expected to introduce additional measures if required.

Overall, the outlook remains cautiously optimistic, with emphasis on strategic planning, innovation, and collaboration across sectors.
"""

def generate_articles():
    articles = []

    for i in range(150):
        title = random.choice(titles) + f" {i+1}"

        article = News_article(
            title=title,
            slug=slugify(title),
            excerpt="This is a preview summary of the article highlighting key developments and insights.",
            content=long_content * random.randint(2, 4),
            category_id_id=(i % 20) + 1,   # covers all categories
            city_id_id=random.randint(1, 3),
            author_id_id=1,
            status="approved",
            visibility="public",
            is_breaking=True if i < 10 else False,
            views_count=random.randint(50, 1000),
            published_at=datetime.now()
        )

        articles.append(article)

    News_article.objects.bulk_create(articles)
    print("150 fake articles inserted successfully.")

if __name__ == "__main__":
    generate_articles()