import streamlit as st
import pandas as pd
import pickle


country_mapping = {
    "cesko": 1,
    "usa": 2,
    "polsko": 3,
    "francie": 4,
    "nemcko": 5,
    "italie": 6,
    "spanelsko": 7,
    "japonsko": 8,
    "velka britanie": 9,
    "kanada": 10
}

# Seznam žánrů (ručně napsané)
genre_mapping = {
    "drama": 1,
    "komedie": 2,
    "akce": 3,
    "horor": 4,
    "thriller": 5,
    "romanticky": 6,
    "sci-fi": 7,
    "animovany": 8,
    "dobrodruzny": 9,
    "documentary": 10
}
# Titulek aplikace
st.title("Předpověď filmového hodnocení")

# Výběr modelu v bočním panelu
model_choice = st.sidebar.selectbox(
    "Vyberte model:",
    ("Linear Regression", "Random Forest Regressor", "Extra Tree Regressor", "Neuron")
)

# Zadání vstupních parametrů
delka = st.number_input("Délka filmu (v minutách):", min_value=1, value=90)
rok = st.number_input("Rok filmu:", min_value=1900, max_value=2100, value=2020)
hodnoceni_pocet = st.number_input("Počet hodnocení:", min_value=0, value=100000)

# Vytvoříme seznam n-tic pro selectboxy – (text, ID)
country_options = list(country_mapping.items())  # např. [("cesko", 1), ("usa", 2), ...]
genre_options = list(genre_mapping.items())         # např. [("drama", 1), ("komedie", 2), ...]

# Selectboxy, které zobrazí text, ale vrátí n-tici (text, ID)
user_country = st.selectbox("Vyberte zemi:", country_options, format_func=lambda x: x[0])
user_genre = st.selectbox("Vyberte žánr:", genre_options, format_func=lambda x: x[0])

# Získáme číselné hodnoty
country_id = user_country[1]
genre_id = user_genre[1]

if st.button("Předpovědět hodnocení"):
    # Sestavení vstupního DataFrame s přesně těmito sloupci a pořadím:
    # ['rok', 'delka', 'hodnoceni_pocet', 'zanr', 'zeme']
    input_data = pd.DataFrame({
        "rok": [rok],
        "delka": [delka],
        "hodnoceni_pocet": [hodnoceni_pocet],
        "zanr": [genre_id],
        "zeme": [country_id]
    })

    # Výběr modelového souboru (předpokládáme, že jsou modely ve složce "models")
    if model_choice == "Linear Regression":
        model_file = "models/omega_lin_model.dat"
    elif model_choice == "Random Forest Regressor":
        model_file = "models/omega_forest_model.dat"
    elif model_choice == "Extra Tree Regressor":
        model_file = "models/omega_tree_model.dat"
    elif model_choice == "Neuron":
        model_file = "models/omega_neuron_model.dat"
    else:
        st.error("Neznámý model.")
        st.stop()

    # Načtení modelu
    try:
        with open(model_file, "rb") as f:
            model = pickle.load(f)
    except Exception as e:
        st.error(f"Chyba při načítání modelu: {e}")
        st.stop()


    # Provedení předpovědi
    try:
        prediction = model.predict(input_data)[0]
        st.write(f"Předpovězené hodnocení: {prediction:.2f}%")
    except Exception as e:
        st.error(f"Chyba při předpovědi: {e}")
