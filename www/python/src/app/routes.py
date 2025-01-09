from flask import Blueprint, render_template, request, jsonify
from .services import select_files
from .models import File
from . import db
arena = Blueprint('arena', __name__)

def extract_statements(raw_data):
        entity = next(iter(raw_data["entities"].values()))
        statements = entity.get("statements", {})
        parsed_statements = {}
        try:
            for prop, items in statements.items():
                values = [
                    item["mainsnak"]["datavalue"]["value"]
                    for item in items
                    if "datavalue" in item["mainsnak"]
                ]
                parsed_statements[prop] = values
            return parsed_statements
        except:
            return parsed_statements

 
@arena.route('/')
def index():
    # Use the matchmaking system to select files
    file1, file2, data1, data2 = select_files(category="Files from the Biodiversity Heritage Library")
    data1 = extract_statements(data1)
    data2 = extract_statements(data2)
    print(data1)
    return render_template('arena.html', file1=file1, file2=file2, data1= data1, data2= data2)
def update_elo(winner, loser, draw=False, k_factor=100):
    """
    Updates the Elo ratings for the winner and loser after a match.
    If it's a draw, adjust ratings accordingly.
    """
    # Current ratings
    winner_rating = winner.elo
    loser_rating = loser.elo

    # Expected scores
    expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner_rating - loser_rating) / 400))

    # Actual scores
    if draw:
        score_winner = 0.5
        score_loser = 0.5
    else:
        score_winner = 1
        score_loser = 0

    # Update ratings
    winner.elo = winner_rating + k_factor * (score_winner - expected_winner)
    loser.elo = loser_rating + k_factor * (score_loser - expected_loser)

    # Update stats
    if draw:
        winner.draws += 1
        loser.draws += 1
    else:
        winner.wins += 1
        loser.losses += 1

    return winner, loser


@arena.route('/submit_choice', methods=['POST'])
def submit_choice():
    """
    Handles the match result submission and updates Elo ratings.
    """
    data = request.json
    winner_id = data.get('winner')
    loser_id = data.get('loser')
    is_draw = data.get('draw', False)  # Optional parameter for a draw

    winner = File.query.get(winner_id)
    loser = File.query.get(loser_id)

    if not winner or not loser:
        return jsonify({"error": "Invalid file IDs"}), 400

    # Update Elo ratings
    update_elo(winner, loser, draw=is_draw)

    # Commit changes to the database
    db.session.commit()

    return jsonify({})


@arena.route('/rank')
def rank():
    # Retrieve all files ordered by wins descending
    files = File.query.order_by((File.elo).desc()).all()    
    return render_template('rank.html', files=files)
