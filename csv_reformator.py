import pandas as pd

# Načtení CSV souboru (uprav oddělovač podle potřeby)
df = pd.read_csv("final_data_string.csv", sep=",")

# Pořadí sloupců, jaké potřebuješ: rok, delka, hodnoceni_pocet, zanr, zeme
desired_order = ["rok", "delka", "hodnoceni_pocet", "zanr", "zeme"]

# Přeuspořádání sloupců
df = df[desired_order]

# Uložení do nového CSV
df.to_csv("final_data_string_ordered.csv", index=False)
