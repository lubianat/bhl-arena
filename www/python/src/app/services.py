import requests
from .models import File
from . import db
from sqlalchemy.sql import func  # Import func for SQLAlchemy functions
import random

WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"


def get_data_statements(filename):
    """
    Get the Structured Data Wikidata statements for a given Commons file.
    
    Args:
        filename (str): The name of the file on Wikimedia Commons.
        
    Returns:
        dict: A dictionary containing Structured Data statements, or an error message.
    """
    # Base URL for Wikimedia Commons API
    base_url = "https://commons.wikimedia.org/w/api.php"
    
    # Parameters for the API request
    params = {
        "action": "wbgetentities",
        "format": "json",
        "sites": "commonswiki",
        "titles": f"File:{filename}",
        "props": "claims",
    }
    
        # Make the API request
    response = requests.get(base_url, params=params)
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
    
    # Parse the response JSON
    data = response.json()
    print(data)
    return data

def fetch_random_file_from_category(category):
    """
    Fetch a random file from a Wikimedia Commons category using 'Special:RandomInCategory'.
    """
    # 1) Let the server handle randomness by requesting the special page
    random_url = (
        f"https://commons.wikimedia.org/wiki/Special:RandomInCategory?wpcategory={category}"
    )
    response = requests.get(random_url)
    # 2) The request will follow redirects by default. The final URL is the random file page
    final_url = response.url
    print(f"Final URL after redirect: {final_url}")    
    # If it didn't land on something in the File namespace, bail or handle accordingly
    # e.g. if it’s "Category:SomeCategory" or "Commons:Something", it's not a file
    if "?title=File:" not in final_url:
        print (
            f"Random result not a file page. Got URL: {final_url}"
        )
        return fetch_random_file_from_category(category)

    file_title = final_url.split("?title=File:")[-1].split("&")[0].replace("_", " ")
    if ".jpg" not in file_title:
        print(
            f"Random result not a JPG file. Got title: {file_title}"
        )
        return fetch_random_file_from_category(category)
    # Check if the file already exists in the database
    existing_file = File.query.filter_by(name=file_title).first()
    if existing_file:
        print(f"File already exists in database: {file_title}")
        return existing_file

    # Add new file to the database
    new_file = File(name=file_title)
    db.session.add(new_file)
    db.session.commit()
    print(f"New file added to database: {file_title}")
    return new_file

def get_or_fetch_files():
    """
    Always fetch new files from the Wikimedia category and populate the database.
    Ensures at least two files are returned.
    """
    # Ensure the database has two entries by always fetching new files
    while File.query.count() < 2:
        print(File.query.count())
        print("Fetching new files to ensure at least two entries in the database.")
        fetch_random_file_from_category("Files from the Biodiversity Heritage Library")

    # Always fetch new files from Wikimedia and add them to the database
    fetch_random_file_from_category("Files from the Biodiversity Heritage Library")
    fetch_random_file_from_category("Files from the Biodiversity Heritage Library")

    # Query the database for two random files
    files = File.query.order_by(func.random()).limit(2).all()
    return files[0], files[1]


def select_files(category):
    """
    Elo-Driven Matchmaking System
    Returns a pair of files based on dynamic match type selection.
    """
    # Define match type probabilities
    match_type = random.choices(
        ['exploratory', "exploratory_challenge", 'top_match', 'random','challenge'],
        weights=[0.5,0.1, 0.1,0.1, 0.1],  
        k=1
    )[0]


    if match_type == 'exploratory':
        # Get a "new" file and a top-ranked file
        file1 = fetch_random_file_from_category(category) 
        file2 = fetch_random_file_from_category(category) 
        # Ensure they are distinct
        if file1.id == file2.id:
            file2 = fetch_random_file_from_category(category)  # Fetch another new file if there's an overlap
    
    if match_type == 'exploratory_challenge':
        # Get a "new" file and a top-ranked file
        file2 = fetch_random_file_from_category(category) 
        top_files = File.query.order_by(File.elo.desc()).limit(20).all()
        file1 = random.sample(top_files, 1)[0]
        # Ensure they are distinct
        if file2.id == file1.id:
            file2 = fetch_random_file_from_category(category)  # Fetch another new file if there's an overlap

    elif match_type == 'top_match':
        # Select two distinct top-ranked files
        top_files = File.query.order_by(File.elo.desc()).limit(20).all()
        if len(top_files) >= 2:
            file1, file2 = random.sample(top_files, 2)  # Guarantees no duplicates
        else:
            file1, file2 = top_files[0], fetch_random_file_from_category(category)  # Fallback to include a new file


    elif match_type == 'random':
        # Select a top-ranked file and a mid-tier or underdog file
        file1 = File.query.order_by(func.random()).first()
        file2 = File.query.order_by(func.random()).first()
    
    elif match_type == 'challenge':
        # Select a top-ranked file and a mid-tier or underdog file
        top_files = File.query.order_by(File.elo.desc()).limit(20).all()
        file1 = random.sample(top_files, 1)[0]
        file2 = File.query.filter(File.elo < 1500).order_by(func.random()).first()
        # Ensure distinct files
        if file2.id == file1.id:
            file2 = File.query.filter(File.elo < 1500, File.id != file1.id).order_by(func.random()).first()
   
    print("Getting SDC")
    print(match_type)
    data1 = get_data_statements(file1.name)

    data2 = get_data_statements(file2.name)
    print(file1)
    print(file2)

    return [file1, file2, data1, data2]
