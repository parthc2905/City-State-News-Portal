import os
import django
from django.utils import timezone
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civix.settings')
django.setup()

from core.models import User
from location.models import State, City
from news.models import Category, News_article

def create_fake_data():
    # 1. Ensure at least one user exists to be the author
    author = User.objects.filter(role='journalist').first()
    if not author:
        author = User.objects.create(
            first_name="Sam",
            last_name="Reporter",
            email="sam.reporter@example.com",
            role="journalist",
            account_status="active",
            approval_status="approved",
            phone="555-0199"
        )
        author.set_password("password123")
        author.save()
        print(f"Created author: {author.email}")
    else:
        print(f"Using existing author: {author.email}")

    # 2. Ensure categories exist
    categories = ['Politics', 'Technology', 'Sports', 'Business', 'Culture']
    db_cats = {}
    for cat_name in categories:
        cat, created = Category.objects.get_or_create(
            category_name=cat_name, 
            defaults={'slug': cat_name.lower()}
        )
        db_cats[cat_name] = cat

    # 3. Ensure state and city exist
    state, _ = State.objects.get_or_create(state_name="Maharashtra", defaults={'region_type': 'state'})
    city, _ = City.objects.get_or_create(city_name="Mumbai", defaults={'state_id': state})

    # 4. Realistic Fake Articles Data
    articles_data = [
        {
            "title": "City Council Approves New Green Transit Initiative for Downtown",
            "excerpt": "A sweeping new public transportation proposal aims to reduce carbon emissions by replacing older buses with a fully electric fleet by 2028.",
            "content": """
                <p>In a landmark 7-2 vote late Tuesday evening, the City Council approved the "Green Transit Now" initiative, setting the stage for a dramatic overhaul of the downtown transportation network.</p>
                <h2>Major Changes Coming</h2>
                <p>The highly debated bill includes $45 million in funding to purchase exactly 120 fully electric buses over the next three years. This shift is expected to decrease downtown carbon emissions by up to 15% annually.</p>
                <blockquote>"This is a massive step forward for our city's sustainability goals. We can no longer rely on outdated, pollution-heavy infrastructure," Mayor Jenkins announced at the press conference.</blockquote>
                <ul>
                    <li><strong>Phase 1:</strong> 40 new electric buses by Q2 2027.</li>
                    <li><strong>Phase 2:</strong> Installation of 15 new rapid charging hubs.</li>
                    <li><strong>Phase 3:</strong> Retirement of all diesel vehicles by end of 2028.</li>
                </ul>
                <p>Critics of the initiative argue the upfront costs are too high, pointing to potential delays in the supply chain for electric vehicle batteries. However, proponents remain optimistic that the long-term environmental and health benefits will outweigh the initial financial burden.</p>
            """,
            "category": db_cats['Politics'],
            "status": "approved",
            "is_breaking": True,
            "views_count": 1405
        },
        {
            "title": "Local Tech Startup 'AeroSynth' Secures $12M Series A Funding",
            "excerpt": "AeroSynth, developers of AI-driven supply chain optimization software, has closed a massive Series A round led by Horizon Ventures.",
            "content": """
                <p>The local technology sector received a massive boost today as <strong>AeroSynth</strong> announced the successful closure of a $12 million Series A funding round.</p>
                <p>Founded by two state university alumni, AeroSynth utilizes advanced machine learning algorithms to predict supply chain bottlenecks before they happen. Their software has already been adopted by three Fortune 500 manufacturing firms in the metropolitan area.</p>
                <h3>Expansion Plans</h3>
                <p>CEO and co-founder Elena Rostova told reporters that the bulk of the funding will go toward expanding their engineering team and opening a new research facility in the city's tech district.</p>
                <p>"We've proven that our predictive models work. Now it's about scaling our infrastructure to handle global enterprise data," Rostova explained.</p>
                <p>The lead investor, Horizon Ventures, is known for backing high-growth B2B SaaS companies. This investment marks their largest single check written to a company in this region.</p>
            """,
            "category": db_cats['Technology'],
            "status": "approved",
            "is_breaking": False,
            "views_count": 890
        },
        {
            "title": "Championship Finals: City Falcons Secure Last-Minute Victory",
            "excerpt": "In a nail-biting finish, the City Falcons scored with just 12 seconds remaining on the clock to win the regional championship 24-21.",
            "content": """
                <p>The stadium erupted into absolute chaos on Saturday night as the City Falcons pulled off one of the most miraculous comebacks in regional sports history.</p>
                <p>Trailing 21-17 with less than two minutes remaining, quarterback Marcus Vance orchestrated a flawless 85-yard drive. Facing a critical 4th-and-goal from the 3-yard line, Vance scrambled out of the pocket and found tight end David Kells in the back corner of the endzone.</p>
                <h2>A Season for the Books</h2>
                <p>This victory caps off an incredible turnaround season for the Falcons, who started the year with three consecutive losses. Head Coach Sarah Miller praised the team's resilience:</p>
                <blockquote>"These players never stopped believing. When we were down by 14 points at halftime, nobody panicked. They just executed the game plan."</blockquote>
                <p>The Falcons will now advance to the National Quarterfinals next month.</p>
            """,
            "category": db_cats['Sports'],
            "status": "approved",
            "is_breaking": False,
            "views_count": 3204
        },
        {
            "title": "Q3 Economic Report: Downtown Retail Sees Resurgence",
            "excerpt": "Foot traffic and consumer spending in the downtown commercial district have reached their highest levels since 2019, according to the latest economic report.",
            "content": """
                <p>Small business owners in the downtown corridor finally have reason to celebrate. The Q3 Economic Impact Report released this morning shows a 22% quarter-over-quarter increase in retail spending.</p>
                <p>The surge is attributed to a combination of factors, including the return of major conferences at the convention center and the success of the city's "Shop Local" weekend initiatives.</p>
                <h3>Sector Breakdown</h3>
                <ul>
                    <li><strong>Restaurants & Hospitality:</strong> +28% growth</li>
                    <li><strong>Boutique Retail:</strong> +15% growth</li>
                    <li><strong>Entertainment Venues:</strong> +31% growth</li>
                </ul>
                <p>“We’re seeing a real appetite for in-person experiences,” said Michael Chen, director of the Downtown Business Association. “People want to dine out, they want to browse physical stores, and they are spending more time hanging around the district after work hours.”</p>
            """,
            "category": db_cats['Business'],
            "status": "draft",
            "is_breaking": False,
            "views_count": 0
        },
        {
            "title": "Museum of Modern Art Unveils Controversial 'Digital Horizons' Exhibit",
            "excerpt": "A new interactive exhibition relying entirely on virtual reality and AI-generated artwork is drawing both immense crowds and fierce debate in the art community.",
            "content": """
                <p>The Museum of Modern Art's newest installation, "Digital Horizons," contains exactly zero physical paintings or sculptures. Instead, visitors are handed VR headsets upon entry and immersed in a constantly evolving, AI-generated landscape.</p>
                <p>The exhibit, curated by renowned digital artist Vektor, is intentionally designed to provoke questions about authorship and creativity in the 21st century.</p>
                <h2>Public Reaction</h2>
                <p>Opening weekend saw lines wrapping around the block, with tickets selling out in under an hour. However, traditional art critics have been less enthusiastic.</p>
                <blockquote>"It is a fascinating technological demonstration, but calling it an emotional piece of human art is stretching the definition to its breaking point," wrote Vivian Vance in the Sunday Arts Review.</blockquote>
                <p>Regardless of the critical consensus, "Digital Horizons" has already become the most financially successful opening in the museum's 40-year history. The exhibit runs through November 15th.</p>
            """,
            "category": db_cats['Culture'],
            "status": "pending",
            "is_breaking": False,
            "views_count": 12
        }
    ]

    # 5. Insert Articles into DB
    for data in articles_data:
        # Avoid duplicate titles
        if not News_article.objects.filter(title=data['title']).exists():
            News_article.objects.create(
                title=data['title'],
                excerpt=data['excerpt'],
                content=data['content'],
                category_id=data['category'],
                city_id=city,
                author_id=author,
                status=data['status'],
                is_breaking=data['is_breaking'],
                views_count=data['views_count'],
                published_at=timezone.now() if data['status'] == 'approved' else None
            )
            print(f"Created article: {data['title']}")
        else:
            print(f"Article already exists: {data['title']}")

if __name__ == '__main__':
    create_fake_data()
    print("Database seeding complete!")
