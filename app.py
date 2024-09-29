from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
import sqlite3
import random

def random_compte_id():
    return random.randint(1000000, 9999999)

# Initialisation de l'application Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Clé secrète pour les sessions
bcrypt = Bcrypt(app)  # Utilisé pour le hachage des mots de passe

# Chemin vers la base de données SQLite
DATABASE = 'users.db'

# Fonction utilitaire pour interagir avec la base de données
def query_db(query, args=(), one=False):
    with sqlite3.connect(DATABASE) as con:
        con.row_factory = sqlite3.Row  # Permet de récupérer les résultats sous forme de dictionnaire
        cur = con.cursor()
        cur.execute(query, args)
        rv = cur.fetchall()
        con.commit()
        cur.close()
        return (rv[0] if rv else None) if one else rv

# Route pour l'inscription d'un nouvel utilisateur
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        compte_id = random_compte_id()

        # Vérifiez si l'utilisateur existe déjà
        user = query_db('SELECT * FROM user WHERE user_login = ? OR user_mail = ?', [username, email], one=True)
        if user:
            flash("L'utilisateur, ou l'email est déjà utilisé par un autre compte.")
            return redirect(url_for('register'))

        # Hacher le mot de passe et insérer l'utilisateur dans la base de données
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        query_db('INSERT INTO user (user_login, user_password, user_compte_id, user_mail) VALUES (?, ?, ?, ?)',
                 [username, hashed_password, compte_id, email])
        flash("Enregistrement réussi. Vous pouvez maintenant vous connecter.")
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Route pour la connexion de l'utilisateur
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Recherchez l'utilisateur dans la base de données
        user = query_db('SELECT * FROM user WHERE user_login = ?', [username], one=True)
        if user is None:
            flash("Nom d'utilisateur incorrect.")
            return redirect(url_for('login'))

        # Vérifiez le mot de passe haché
        if bcrypt.check_password_hash(user['user_password'], password):
            session['username'] = username  # Créez une session pour l'utilisateur
            flash("Connexion réussie.")
            return redirect(url_for('profile'))
        else:
            flash("Mot de passe incorrect.")
            return redirect(url_for('login'))
    
    return render_template('login.html')

# Route pour afficher le profil de l'utilisateur connecté
@app.route('/profile')
def profile():
    if 'username' not in session:
        flash("Vous devez vous connecter pour accéder à cette page.")
        return redirect(url_for('login'))
    
    return f"Bonjour, {session['username']}! Bienvenue sur votre profil."

# Route pour déconnecter l'utilisateur
@app.route('/logout')
def logout():
    session.pop('username', None)  # Supprimez l'utilisateur de la session
    flash("Vous avez été déconnecté.")
    return redirect(url_for('login'))

# Exécuter l'application Flask
if __name__ == '__main__':
    app.run(debug=True)