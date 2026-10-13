produit = "clavier"
prix = 49.99
stock = 100
print("le produit est:" + produit + "stock indisponible:" + str(stock) + "prix:" + str(prix))

print(f"le produit est: {produit} stock indisponible: {stock} prix: {prix}")
prix_ttc = [59, 29, 19, 9]
prix_ht=[]

for p in prix_ttc:
    prix_ht.append(round(p/1.2, 3))

    print(prix_ht)

    prix_ht_1=[round(p / 1.2, 3) for p in prix_ttc if p>15]
    print(prix_ht_1)
