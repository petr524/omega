import csv
import os
import re
import time
import logging
import requests
from bs4 import BeautifulSoup

# Nastavení logovacího souboru
LOG_FILE = "csfd_crawler.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# --- REGEXY pro délku, hodnocení, atd. ---
RE_LEN_H_M = re.compile(r"(\d+)\s*h\s*(\d+)\s*min")  # "1 h 10 min" => 1,10
RE_LEN_H_ONLY = re.compile(r"(\d+)\s*h")             # "2 h" => 2
RE_LEN_MIN_ONLY = re.compile(r"(\d+)\s*min")         # "116 min" => 116
RE_RATING_COUNT = re.compile(r"Hodnocení\s*\(([\d\s]+)\)")  # "Hodnocení (116 107)" => "116 107"
RE_RATING_PERCENT = re.compile(r"(\d+)\s?%")               # "91%" => "91"

# Příklad setu možných zemí (můžete doplnit podle potřeby)
ALL_COUNTRIES = {
    "Česko", "Slovensko", "USA", "Velká Británie", "Polsko", "Francie", "Německo",
    "Rakousko", "Kanada", "Maďarsko", "Japonsko", "Itálie", "Španělsko"
}

# Příklad setu žánrů (můžete doplnit podle potřeby)
ALL_GENRES = {
    "Komedie", "Drama", "Akční", "Dobrodružný", "Sci-Fi", "Krimi",
    "Horor", "Thriller", "Muzikál", "Fantasy", "Romantický",
    "Animovaný", "Rodinný", "Válečný", "Historický"
}


def parse_runtime(origin_text):
    """
    Zpracuje délku z textu, např.:
      - "116 min" => "116"
      - "1 h 10 min" => "70"
      - "2 h" => "120"
    Pokud nic nenajde, vrátí "NaN".
    """
    # "X h Y min"
    m = RE_LEN_H_M.search(origin_text)
    if m:
        hours = int(m.group(1))
        mins = int(m.group(2))
        return str(hours * 60 + mins)

    # "X h"
    m = RE_LEN_H_ONLY.search(origin_text)
    if m:
        hours = int(m.group(1))
        return str(hours * 60)

    # "X min"
    m = RE_LEN_MIN_ONLY.search(origin_text)
    if m:
        return m.group(1)

    return "NaN"


def parse_country(origin_text):
    """
    Zkusí z textu (např. "Česko, 1999, 116 min") vytáhnout první část před čárkou
    a ověřit v seznamu ALL_COUNTRIES. Pokud tam není, vrací "NaN".
    """
    parts = origin_text.split(",")
    if not parts:
        return "NaN"
    first_part = parts[0].strip()
    # validujeme
    for c in ALL_COUNTRIES:
        if c.lower() == first_part.lower():
            return c
    return "NaN"


def parse_year_and_rest(origin_text):
    """
    Z "Česko, 1999, 116 min" => ("1999", "116 min")
    Pokud to nevyjde, vrací ("NaN","NaN").
    """
    parts = origin_text.split(",")
    if len(parts) < 3:
        return "NaN", "NaN"
    # 2. prvek = rok
    rok = parts[1].strip()
    remainder = ",".join(parts[2:]).strip()
    return rok, remainder


def parse_genres(genre_text):
    """
    Např. "Komedie / Drama" => "Komedie,Drama"
    Použijeme ALL_GENRES k validaci, ale klidně jen rozsekneme "/".
    """
    splitted = [g.strip() for g in genre_text.split("/")]
    final_list = []
    for g in splitted:
        if g in ALL_GENRES:
            final_list.append(g)
        else:
            # Pokud není v setu, necháme beze změn nebo "NaN" - dle preferencí
            final_list.append(g)
    return ",".join(final_list)


def parse_rating_count(full_text):
    """
    Najde "Hodnocení (116 107)" => "116107"
    Pokud nenajde => "NaN"
    """
    m = RE_RATING_COUNT.search(full_text)
    if not m:
        return "NaN"
    raw_val = m.group(1).strip()
    return raw_val.replace(" ", "")


def parse_rating_percent(soup):
    """
    <div class="film-rating-average">91%</div> => "91"
    """
    div = soup.find("div", class_="film-rating-average")
    if not div:
        return "NaN"
    raw = div.get_text(strip=True)
    m = RE_RATING_PERCENT.search(raw)
    if not m:
        return "NaN"
    return m.group(1)


def zpracuj_film(url):
    """
    Stáhne HTML z daného URL, zpracuje:
      - delka (string)
      - zanry (string)
      - zeme (string)
      - rok (string)
      - hodnoceni_procenta (string)
      - hodnoceni_pocet (string)
    Pokud cokoliv selže => "NaN".
    """
    data = {
        "delka": "NaN",
        "zanry": "NaN",
        "zeme": "NaN",
        "rok": "NaN",
        "hodnoceni_procenta": "NaN",
        "hodnoceni_pocet": "NaN"
    }

    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")

            # 1) Žánry
            genre_div = soup.find("div", class_="genres")
            if genre_div:
                genre_text = genre_div.get_text(strip=True)
                data["zanry"] = parse_genres(genre_text)

            # 2) origin => "Česko, 1999, 116 min"
            origin_div = soup.find("div", class_="origin")
            if origin_div:
                origin_text = origin_div.get_text(strip=True)
                # zeme
                c = parse_country(origin_text)
                data["zeme"] = c
                # rok + zbytek
                r, remainder = parse_year_and_rest(origin_text)
                data["rok"] = r
                # delka
                d = parse_runtime(remainder)
                data["delka"] = d

            # 3) Hodnocení v procentech
            data["hodnoceni_procenta"] = parse_rating_percent(soup)

            # 4) Počet hodnocení (z plného textu)
            full_text = soup.get_text("\n", strip=True)
            data["hodnoceni_pocet"] = parse_rating_count(full_text)

        else:
            logging.error(f"Chyba HTTP {resp.status_code} pro URL: {url}")
            data = {k: "NaN" for k in data}
    except Exception as e:
        logging.error(f"Chyba při zpracování {url}: {e}")
        data = {k: "NaN" for k in data}

    return data


def main():
    input_csv = "csfd_random_links.csv"      # vstupní soubor s hlavičkou "url"
    output_csv = "csfd_films_data.csv"

    # Kolik řádků už je ve výstupu?
    zpracovanych = 0
    if os.path.exists(output_csv):
        with open(output_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # přeskočíme hlavičku
            for _ in reader:
                zpracovanych += 1

    logging.info(f"Start. Uz mame {zpracovanych} zpracovanych zaznamu.")
    print(f"Start. Uz mame {zpracovanych} zpracovanych zaznamu.")

    if not os.path.exists(input_csv):
        logging.error(f"Soubor {input_csv} neexistuje, konec.")
        print(f"Soubor {input_csv} neexistuje, konec.")
        return

    with open(input_csv, "r", encoding="utf-8") as fin:
        reader = csv.reader(fin)
        header = next(reader, None)  # "url"
        if not header:
            logging.error("Vstupni CSV je prazdne, konec.")
            print("Vstupni CSV je prazdne, konec.")
            return

        # Přeskočíme zpracované
        for _ in range(zpracovanych):
            next(reader, None)

        mode = "a" if os.path.exists(output_csv) else "w"
        with open(output_csv, mode, newline="", encoding="utf-8") as fout:
            fieldnames = ["delka", "zanry", "zeme", "rok", "hodnoceni_procenta", "hodnoceni_pocet"]
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            if zpracovanych == 0:
                writer.writeheader()

            idx = zpracovanych
            try:
                for row in reader:
                    idx += 1
                    if not row:
                        continue
                    url = row[0].strip()
                    if not url:
                        continue

                    vysledek = zpracuj_film(url)
                    writer.writerow(vysledek)
                    fout.flush()

                    logging.info(f"[{idx}] {url} => {vysledek}")
                    print(f"[{idx}] {url} => {vysledek}")

                    time.sleep(1)  # krátká pauza
            except KeyboardInterrupt:
                logging.warning("Program přerušen uživatelem (Ctrl+C).")
                print("\nProgram přerušen uživatelem (Ctrl+C).")
            finally:
                logging.info(f"Konec. Celkem zpracováno {idx} záznamů.")
                print(f"Konec. Celkem zpracováno {idx} záznamů.")


if __name__ == "__main__":
    main()
