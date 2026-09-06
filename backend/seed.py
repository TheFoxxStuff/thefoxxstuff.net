import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "thefoxxstuff"

async def seed():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    await db.music.delete_many({})
    await db.blog.delete_many({})
    await db.arts.delete_many({})
    await db.about.delete_many({})

    music_releases = [
        {"title": "GLOBAL COLLAPSE", "release_date": datetime(2025, 10, 1), "genre": "Experimental", "release_type": "Album", "price": "Name your price", "tracks": [{"number": 1, "title": "Collapse Intro", "duration": "02:30"}, {"number": 2, "title": "Digital Void", "duration": "04:15"}], "gallery": [], "cover_image": None, "is_new": True, "production_notes": "All music written and produced by TheFoxxStuff", "liner_notes": "So I spent a few hours in this world...", "views": 0},
        {"title": "I WANNA DIE", "release_date": datetime(2024, 4, 1), "genre": "Hardcore", "release_type": "EP", "price": "Name your price", "tracks": [{"number": 1, "title": "Despair", "duration": "03:01"}], "gallery": [], "cover_image": None, "is_new": False, "views": 128},
        {"title": "ONE SOUL", "release_date": datetime(2021, 5, 25), "genre": "Breakcore", "release_type": "Single", "price": "Name your price", "tracks": [{"number": 1, "title": "One Soul", "duration": "04:20"}], "gallery": [], "cover_image": None, "is_new": False, "views": 256},
        {"title": "ASTRAL SUMMER", "release_date": datetime(2020, 2, 25), "genre": "Experimental", "release_type": "Single", "price": "Name your price", "tracks": [{"number": 1, "title": "Summer Memories", "duration": "03:01"}], "gallery": [], "cover_image": None, "is_new": False, "views": 512},
        {"title": "LOW", "release_date": datetime(2019, 4, 19), "genre": "Drum'n'Bass", "release_type": "EP", "price": "Name your price", "tracks": [{"number": 1, "title": "Low", "duration": "03:30"}], "gallery": [], "cover_image": None, "is_new": False, "views": 89},
    ]

    blog_posts = [
        {"title": "Путешествия в Москву", "content": "Nulla ut leo faucibus ipsum tristique...", "excerpt": "Nulla ut leo faucibus ipsum tristique.", "cover_image": None, "created_at": datetime(2024, 4, 28), "views": 512},
        {"title": "Новый релиз", "content": "Рассказываю о новом альбоме...", "excerpt": "Рассказываю о новом альбоме.", "cover_image": None, "created_at": datetime(2024, 4, 25), "views": 256},
    ]

    artworks = []
    for year in [2025, 2024, 2023]:
        for i in range(7 if year == 2025 else 4):
            artworks.append({"title": f"Artwork {year}-{i+1}", "description": "Digital artwork.", "image_url": None, "dimensions": "1024 x 1024", "file_size": "1.2 MB", "year": year, "created_at": datetime(year, 4, 28 - i), "views": 100 + i * 50})

    about = {"name": "TheFoxxStuff", "location": "Republic of Sakha (Yakutia)", "genres": ["Hardcore", "Breakcore", "Drum'n'Bass"], "bio": "He has his own unique style...", "avatar": None, "email": "mail@thefoxxstuff.net", "social_links": {"bandcamp": "https://thefoxxstuff.bandcamp.com", "soundcloud": "https://soundcloud.com/thefoxxstuff", "twitter": "https://twitter.com/thefoxxstuff", "vk": "https://vk.com/thefoxxstuff", "telegram": "https://t.me/thefoxxstuff"}, "liner_notes": "So I spent a few hours in this world..."}

    await db.music.insert_many(music_releases)
    await db.blog.insert_many(blog_posts)
    await db.arts.insert_many(artworks)
    await db.about.insert_one(about)

    print("Database seeded! Register a new user - first user will be admin.")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed())
