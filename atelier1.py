print("=== 1. Variables et affichage ===")
prenom = input("Entrez votre prenom : ")
age = input("Entrez votre age : ")
print(f"Hello {prenom}, you are {age} years old.")


print("\n=== 2. Conditions : nombre pair ou impair ===")
nombre = int(input("Entrez un nombre entier : "))

if nombre % 2 == 0:
    print(f"{nombre} est pair.")
else:
    print(f"{nombre} est impair.")


print("\n=== 3.a. Parcours d'une chaine ===")
mot = input("Entrez un mot : ")

for lettre in mot:
    print(lettre)


print("\n=== 3.b. Somme des entiers de 1 a 100 ===")
somme = 0

for entier in range(1, 101):
    somme = somme + entier

print(f"La somme des entiers de 1 a 100 est : {somme}")


print("\n=== 4. Listes ===")
notes = [12, 15, 9, 18, 14]
moyenne = sum(notes) / len(notes)
note_maximale = max(notes)
note_minimale = min(notes)

print(f"Notes : {notes}")
print(f"Moyenne : {moyenne}")
print(f"Note maximale : {note_maximale}")
print(f"Note minimale : {note_minimale}")


print("\n=== 5. Dictionnaires ===")
student = {
    "name": "Ali",
    "age": 20,
    "study field": "computer science"
}

student["email"] = "ali@example.com"

for cle, valeur in student.items():
    print(f"{cle} : {valeur}")


print("\n=== 6.a. Ensembles ===")
animaux = {"cat", "dog", "bird", "cat"}

print(animaux)
print(f"Nombre d'animaux differents : {len(animaux)}")


print("\n=== 6.b. Tuple ===")
personne = ("Ali", 20, "Tunis")

for element in personne:
    print(element)


print("\n=== Application 1 : pays visites ===")
pays_visites = [
    "Tunisie",
    "France",
    "Italie",
    "France",
    "Tunisie",
    "France",
    "Espagne"
]

nombre_visites = {}

for pays in pays_visites:
    if pays in nombre_visites:
        nombre_visites[pays] = nombre_visites[pays] + 1
    else:
        nombre_visites[pays] = 1

print(f"Nombre de visites par pays : {nombre_visites}")

pays_plus_visite = max(nombre_visites, key=nombre_visites.get)
print(f"Pays le plus visite : {pays_plus_visite}")


print("\n=== Application 2 : achats en ligne ===")
purchases = [
    {"product": "Computer", "price": 1200, "quantity": 2},
    {"product": "Mouse", "price": 25, "quantity": 5},
    {"product": "Keyboard", "price": 45, "quantity": 3},
    {"product": "Monitor", "price": 300, "quantity": 2},
    {"product": "Mouse", "price": 25, "quantity": 2}
]

montant_total = 0
quantites_par_produit = {}
ventes_par_produit = {}

for achat in purchases:
    produit = achat["product"]
    prix = achat["price"]
    quantite = achat["quantity"]
    valeur_achat = prix * quantite
    montant_total = montant_total + valeur_achat

    if produit in quantites_par_produit:
        quantites_par_produit[produit] += quantite
    else:
        quantites_par_produit[produit] = quantite

    if produit in ventes_par_produit:
        ventes_par_produit[produit] += valeur_achat
    else:
        ventes_par_produit[produit] = valeur_achat

print(f"Montant total depense : {montant_total} euros")
print(f"Quantites totales par produit : {quantites_par_produit}")

produit_plus_achete = max(
    quantites_par_produit,
    key=quantites_par_produit.get
)
print(f"Produit le plus achete : {produit_plus_achete}")

print("Valeur totale des ventes par produit :")
for produit, valeur in ventes_par_produit.items():
    print(f"{produit} : {valeur} euros")


print("\n=== Application 3 : manipulation d'une phrase ===")
phrase = input("Entrez une phrase complete : ")
mots = phrase.split()

print("Liste des mots : {}".format(mots))

mots.append("incroyable")

if "puissant" in mots:
    position = mots.index("puissant")
    mots[position] = "facile"

print(f"Nombre total de mots : {len(mots)}")

nouvelle_phrase = "-".join(mots)
print("Nouvelle phrase : {}".format(nouvelle_phrase))

for numero, mot in enumerate(mots, start=1):
    print(f"Mot {numero} : {mot.upper()}")
