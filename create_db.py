import sqlite3

def create_sqlite_db(file):
    """
        Créer une base de données users.db
    """
    connexion = None
    try:
        connexion = sqlite3.connect(file)
        print("Connexion réussie", sqlite3.sqlite_version)
    except sqlite3.Error as erreur:
        print(erreur)
    finally:
        if connexion:
            connexion.close()


if __name__ == '__main__':
    create_sqlite_db("users.db")
