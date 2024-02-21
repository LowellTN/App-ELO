from flask import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from random import *
from sqlalchemy import *
from ELO import *
import os

app.secret_key = os.urandom(24)

TEMPLATE_DIR = os.path.abspath('./templates')
STATIC_DIR = os.path.abspath('./templates/static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = os.urandom(24)

### Base de données 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///elo.db'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    elo = db.Column(db.Integer, default=1000)
    K = db.Column(db.Integer, default=40)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player1_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    winner_id = db.Column(db.Integer, db.ForeignKey('player.id'))   
    player1 = db.relationship('Player', foreign_keys=[player1_id], backref='matches_as_player1')
    player2 = db.relationship('Player', foreign_keys=[player2_id], backref='matches_as_player2')
    winner = db.relationship('Player', foreign_keys=[winner_id], backref='matches_as_winner')



with app.app_context():
    db.create_all()

### Architecture du site

@app.route('/')
def mainpage():
    return render_template('mainpage.html')

@app.route('/addplayer', methods=['GET', 'POST'])
def addplayer():
    if request.method == 'POST':
        player_name = request.form.get('player_name')
        print(f"Nom du joueur à ajouter : {player_name}")

        player = Player(name=player_name, elo=1000)
        print(f"Joueur créé : {player}")

        db.session.add(player)
        db.session.commit()
        print("Joueur ajouté à la base de données")

        return redirect(url_for('addplayer'))

    return render_template('addplayer.html')

    # Si la requête est GET, renvoie le formulaire
    return render_template('addplayer.html')

@app.route('/allplayers')
def liste_joueurs():
    joueurs = Player.query.all()  # Assure-toi que tu importes le modèle Player
    return render_template('allplayers.html', joueurs = joueurs)

@app.route('/show_matches', methods=['GET'])
def show_matches():
    player_search = request.args.get('player_search', '')
    matches = []

    if player_search:
        # Recherche les matches impliquant le joueur spécifié
        player = Player.query.filter(Player.name.ilike(f'%{player_search}%')).first()
        if player:
            matches = Match.query.filter((Match.player1 == player) | (Match.player2 == player)).all()
    else:
        # Affiche tous les matches si aucune recherche n'est effectuée
        matches = Match.query.all()

    return render_template('show_matches.html', matches=matches)



@app.route('/new_match', methods=['GET', 'POST'])
def new_match():
    players = Player.query.all()

    if request.method == 'POST':
        player1_id = request.form.get('player1')
        player2_id = request.form.get('player2')
        winner_id = request.form.get('winner')

        print(player1_id)
        print(player2_id)
        print(winner_id)


        # Récupère les objets Player correspondants
        player1 = Player.query.get(player1_id)
        player2 = Player.query.get(player2_id)
        winner = Player.query.get(winner_id)

        print(player1)
        print(player2)
        print(winner)
        # Crée une nouvelle instance de Match
        match = Match(player1=player1, player2=player2, winner=winner)

        # Met à jour les Elo des joueurs en fonction du résultat du match
        rg1 = recent_game(player1.id)
        rg2 = recent_game(player2.id)
        player1.K = vark(nombre_parties(player1.id),rg1,player1.K)
        player2.K = vark(nombre_parties(player2.id),rg2,player2.K)
        
        print(rg1)
        print(rg2)
        print(player1.K)
        print(player2.K)

        new_elo = update_elo(player1, player1.elo, player1.K, player2, player2.elo, player2.K, winner)
        
        player1.elo = new_elo[0]
        player2.elo = new_elo[1]

        # Ajoute le match à la base de données
        db.session.add(match)
        db.session.commit()

        return redirect(url_for('show_matches'))

    return render_template('new_match.html', players=players)



@app.teardown_request
def teardown_request(exception=None):
    if exception is None:
        db.session.commit()
    else:
        db.session.rollback()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

### Fonction Python

def recent_game(player_id):
    rg = []
    recent_matches = Match.query.filter((Match.player1_id == player_id) | (Match.player2_id == player_id)).order_by(desc(Match.id)).limit(10).with_entities(Match.winner_id).all()
    print(recent_matches)
    for match in recent_matches:
        if player_id == match[0]:
            rg.append(1)
        elif match[0] == None:
            rg.append(0)
        else:
            rg.append(-1)
    return rg


def nombre_parties(player_id):
    matches_as_player1 = Match.query.filter_by(player1_id=player_id).count()
    matches_as_player2 = Match.query.filter_by(player2_id=player_id).count()
    total_matches = matches_as_player1 + matches_as_player2
    return total_matches

### Fonction Database


if __name__ == "__main__":
    with app.app_context():
        player_id = 2
        print(nombre_parties(player_id))
    


    # Afficher les résultats