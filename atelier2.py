class Personne:
    def __init__(self, nom, age):
        self.nom = nom
        self.age = age

    def se_presenter(self):
        return f"Je m'appelle {self.nom} et j'ai {self.age} ans."

    def __str__(self):
        return self.se_presenter()

    def __del__(self):
        print(f"{self.nom} a ete detruit")


class Etudiant(Personne):
    def __init__(self, nom, age, niveau):
        super().__init__(nom, age)
        self.niveau = niveau

    def etudier(self):
        return f"Je suis en {self.niveau} et j'etudie dur !"


print("=== Exemple 1 : classe Personne ===")
personne_alice = Personne("Alice", 30)
print(personne_alice.se_presenter())

print("\n=== Exemple 2 : methode __str__ ===")
print(personne_alice)

print("\n=== Exemple 3 : heritage ===")
etudiant_bob = Etudiant("Bob", 20, "Master")
print(etudiant_bob.se_presenter())
print(etudiant_bob.etudier())


class Panier:
    def __init__(self, articles):
        self.articles = articles

    def __len__(self):
        return len(self.articles)

    def __getitem__(self, index):
        return self.articles[index]


print("\n=== Exemple 5 : methode __len__ ===")
panier = Panier(["pomme", "banane"])
print(len(panier))

print("\n=== Exemple 6 : methode __getitem__ ===")
print(panier[0])


class Produit:
    def __init__(self, nom, prix):
        self.nom = nom
        self.prix = prix

    def __eq__(self, autre):
        if isinstance(autre, Produit):
            return self.nom == autre.nom
        return False


print("\n=== Exemple 7 : methode __eq__ ===")
prod1 = Produit("Livre", 10.0)
prod2 = Produit("Livre", 15.0)
print(prod1 == prod2)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, autre):
        return Point(self.x + autre.x, self.y + autre.y)

    def __str__(self):
        return f"({self.x}, {self.y})"


print("\n=== Exemple 8 : methode __add__ ===")
point1 = Point(1, 2)
point2 = Point(3, 4)
print(point1 + point2)

print("\n=== Exemple 9 : methode __del__ ===")
personne_charlie = Personne("Charlie", 25)
del personne_charlie


class Livre:
    def __init__(self, titre, auteur, annee, disponible=True):
        self.titre = titre
        self.auteur = auteur
        self.annee = annee
        self.disponible = disponible

    def emprunter(self):
        if self.disponible:
            self.disponible = False
            return "Livre emprunte !"
        return "Indisponible."

    def retourner(self):
        self.disponible = True
        return "Livre retourne."

    def __str__(self):
        disponibilite = "Oui" if self.disponible else "Non"
        return (
            f"Titre : {self.titre}, Auteur : {self.auteur}, "
            f"Annee : {self.annee}, Disponible : {disponibilite}"
        )


class Roman(Livre):
    def __init__(self, titre, auteur, annee, genre, disponible=True):
        super().__init__(titre, auteur, annee, disponible)
        self.genre = genre

    def __str__(self):
        return f"{super().__str__()}, Genre : {self.genre}"


class Bibliotheque:
    def __init__(self):
        self.livres = []

    def ajouter_livre(self, livre):
        self.livres.append(livre)

    def lister_livres(self):
        return [str(livre) for livre in self.livres]

    def emprunter_livre(self, titre):
        for livre in self.livres:
            if livre.titre == titre:
                return livre.emprunter()
        return "Livre non trouve."


print("\n=== Partie 3 : gestion d'une bibliotheque ===")
bibliotheque = Bibliotheque()
livre1 = Livre("Le Petit Prince", "Antoine de Saint-Exupery", 1943)
roman1 = Roman("1984", "George Orwell", 1949, "Dystopie")

bibliotheque.ajouter_livre(livre1)
bibliotheque.ajouter_livre(roman1)

print(bibliotheque.emprunter_livre("Le Petit Prince"))

print("\nListe apres l'emprunt :")
for description in bibliotheque.lister_livres():
    print(description)

print("\n" + livre1.retourner())

print("\nListe apres le retour :")
for description in bibliotheque.lister_livres():
    print(description)
