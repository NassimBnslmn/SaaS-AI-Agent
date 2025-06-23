import sqlite3

# Chemin vers ta base SQLite
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Requête pour chercher l'utilisateur
email_to_search = 'nassim.benslimane@se.univ-bejaia.dz'
cursor.execute("SELECT * FROM user_user WHERE email = ?", (email_to_search,))

# Affichage des résultats
user = cursor.fetchone()
if user:
    print("Utilisateur trouvé :", user)
else:
    print("Aucun utilisateur trouvé avec cet email.")

conn.close()
