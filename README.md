Predikce filmového hodnocení 
Tento projekt slouží jako ukázka kompletního softwarového řešení, které zahrnuje:

Sběr a předzpracování reálných dat (z ČSFD, prováděno crawlerem).

Vytvoření a trénink modelu strojového učení na základě vlastních nasbíraných dat (minimálně 1500 záznamů a 5 atributů).

Implementaci finální aplikace (pomocí Streamlit) pro interaktivní předpověď filmového hodnocení.

1. Reálné využití a popis projektu
Aplikace umožňuje uživatelům zadat parametry filmu (délka, rok, počet hodnocení, žánr, země) a na základě trénovaného modelu strojového učení předpovědět výsledné hodnocení v procentech. Data byla reálně sesbírána z portálu ČSFD pomocí vlastního crawleru. Model lze měnit (lineární regrese, Random Forest, Extra Tree, neuronová síť), abychom mohli porovnat různé algoritmy.

2. Obsah a struktura projektu
bash
├── app.py                   # Hlavní streamlit aplikace
├── crawler.py               # Vlastní crawler pro sběr dat z ČSFD
├── csfd_crawler.log         # Logy z běhu crawleru
├── csfd_details.log         # Další logy
├── csfd_random_links.csv    # Pomocné CSV se sesbíranými linky
├── csfd_films_data.csv      # Nezpracovaná data z ČSFD (před čištěním)
├── final_data.csv           # Data po základním čištění (mezikrok)
├── final_data_ordered.csv   # Finální data se sloupci v požadovaném pořadí
├── final_data_string.csv    # Příklad další verze CSV s textovými sloupci
├── models/                  # Složka s natrénovanými modely
│   ├── omega_lin_model.dat
│   ├── omega_forest_model.dat
│   ├── omega_tree_model.dat
│   └── omega_neuron_model.dat
├── notebooks/               # (Nepovinné) Google Colab / Jupyter Notebooky
│   └── model_training.ipynb # Notebook s tvorbou a trénováním modelu
├── .venv/                   # Virtuální prostředí (není nutné commitovat)
├── README.md                # Tento soubor
└── requirements.txt         # Seznam knihoven a verzí
2.1 Externí a vlastní kód
Vlastní kód:

crawler.py (autorský crawler pro sběr dat z ČSFD)

app.py (logika Streamlit aplikace)

Notebook s trénováním modelu v notebooks/model_training.ipynb

Cizí kód:

Všechny knihovny instalované přes pip (Streamlit, Pandas, TensorFlow, scikit-learn, …).

Jsou odděleny v requirements.txt a instalovány jako externí balíčky.

3. Sběr a zpracování dat
3.1 Sběr dat
Crawler (crawler.py) prochází stránku ČSFD, získává informace o filmech (hodnocení, žánr, rok, země původu, délku, atd.).

Data se ukládají do CSV (csfd_films_data.csv, csfd_random_links.csv atd.).

3.2 Čištění, transformace a škálování
Odstraňování duplicit a nekonzistentních záznamů.

Konverze textových sloupců (např. "zeme", "zanr") na číselné kódy.

Rozdělení dat na trénovací a testovací sadu.

Finální soubor: final_data_ordered.csv obsahuje sloupce rok, delka, hodnoceni_pocet, zanr, zeme ve správném pořadí.

4. Model strojového učení
4.1 Trénování
Model byl vytvořen v notebooku (např. notebooks/model_training.ipynb) nebo Google Colabu.

Datový základ: Minimálně 1500 záznamů (reálné filmy) s 5 atributy.

Typy modelů:

Lineární regrese (omega_lin_model.dat)

Random Forest (omega_forest_model.dat)

Extra Tree Regressor (omega_tree_model.dat)

Jednoduchá neuronová síť (omega_neuron_model.dat)

4.2 Ukládání a vyhodnocení
Každý model je uložen jako pickle soubor ve složce models/.

Hodnocení modelu probíhalo měřením např. MSE, MAE, R2, apod. (viz notebook).

5. Spuštění aplikace
5.1 Požadavky
Python 3.7+ (doporučeno 3.7–3.9 pro TensorFlow a scikit-learn).

Knihovny uvedené v requirements.txt:

streamlit
pandas
scikit-learn
tensorflow-cpu
Instalace:

pip install -r requirements.txt
5.2 Spuštění bez IDE
Aktivujte virtuální prostředí (nepovinné, ale doporučené):

Spusťte aplikaci:
streamlit run app.py
Otevřete odkaz v prohlížeči (typicky http://localhost:8501).

5.3 Použití aplikace
V bočním panelu vyberte model (Lineární regrese, Random Forest, Extra Tree, Neuron).

V hlavním panelu zadejte parametry (rok, délka, počet hodnocení) a vyberte zemi a žánr.

Klikněte na „Předpovědět hodnocení“.

Zobrazí se výsledek predikce (např. „68.50 %“).

6. Předvedení a obhajoba
Prezentace sběru dat – ukázka crawleru, logů a souborů se surovými daty.

Proces čištění – vysvětlení transformací (odstranění duplicit, mapování žánrů, atd.).

Trénování modelu – v notebooku ukázat, jak byla data rozdělena na trénovací a testovací sadu, jak byly modely laděny a vyhodnocovány.

Spuštění aplikace – praktické předvedení.

Odpovědi na otázky – vysvětlení logiky kódu, prokázání autorského podílu.

7. Oddělení cizího kódu
Veškeré knihovny třetích stran (Streamlit, Pandas, scikit-learn, TensorFlow, …) jsou nainstalovány přes pip a spravovány v requirements.txt.

Vlastní kód:

app.py, crawler.py, notebook s trénováním modelu, atd.

Cizí kód:

Standardní pythoní knihovny, balíčky v lib / .venv, atd.

8. Zdroje a licence
Data: Vlastní crawler z portálu ČSFD.

Knihovny:

Streamlit – MIT License

scikit-learn – BSD License

TensorFlow – Apache License 2.0

Autorský kód: crawler.py, app.py, Jupyter Notebooky.

Projekt: Vlastní, vyvinut v rámci předmětu PV/PSS.

9. Závěr
Tento projekt ukazuje kompletní cyklus tvorby softwaru pro predikci filmového hodnocení:

Sběr reálných dat (crawler z ČSFD).

Čištění, transformace (CSV s ~1500+ filmy).

Trénování modelů (regrese, stromy, neuronka).

Uživatelská aplikace (Streamlit) s možností volby modelu a interaktivním zadáním parametrů.

Projekt je tak připraven k obhajobě dle zadání – splňuje požadované náležitosti (reálná data, min. 1500 záznamů, 5 atributů, dokumentace a návod k použití).

