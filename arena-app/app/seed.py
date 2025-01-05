from . import db
from .models import File
from .services import fetch_random_new_file

def seed_database():
    """
    Seeds the database with initial files if empty.
    """
    if File.query.count() == 0:
        print("Seeding database with initial files...")
        for _ in range(10):  # Fetch 10 random new files
            fetch_random_new_file()
        print("Database seeded.")
