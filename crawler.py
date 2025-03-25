import os
import csv
import time
import random
import logging
import requests
import re

from bs4 import BeautifulSoup

# ASCII-only log file
LOG_FILE = r"C:\pv\Omega\csfd_random_films.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


def save_urls(urls, csv_file):
    """
    Uloží URL (unikátní) do CSV souboru (přepíše celý soubor).
    V prvním řádku je 'url'. Po uložení se zapíše log, který indikuje počet uložených URL a cestu k souboru.
    """
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["url"])
        for link in sorted(urls):
            writer.writerow([link])
    # Přidáme logovací hlášku
    logging.info(f"Uloženo {len(urls)} URL do souboru {csv_file}.")
    print(f"Uloženo {len(urls)} URL do souboru {csv_file}.")


def crawl_csfd_random(
        output_csv=r"C:\pv\Omega\csfd_random_links.csv",
        max_films=1500,
        max_attempts=100000
):
    """
    1) Náhodně generuje čísla od 1 do 1 000 000.
    2) Ke každému číslu složí URL ve tvaru https://www.csfd.cz/film/<cislo>/.
    3) Zjistí, zda stránka existuje (status_code 200 a neobsahuje text "Nenalezeno").
    4) Pokud stránka existuje, ověří se, zda výsledná URL (r.url) odpovídá formátu filmové stránky,
       který začíná na https://www.csfd.cz/film/ a za číslem může následovat cokoliv.
    5) Pokud URL odpovídá, uloží se do CSV.
    6) Ukončí se, jakmile nasbírá max_films (default 200), nebo vyčerpá max_attempts (default 100000).
    7) Při každých 10 pokusech se uloží průběžný stav a logují se také informace.
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "cs-CZ,cs;q=0.9,en-US,en;q=0.8"
    }

    # Upravený regulární výraz:
    # URL musí začínat na https://www.csfd.cz/film/, následovat čísla a poté může být cokoliv.
    film_regex = re.compile(r"^https://www\.csfd\.cz/film/\d+.*$")

    found_urls = set()  # nalezené platné filmy
    tried_numbers = set()  # abychom každé číslo netestovali vícekrát

    logging.info(f"Začínáme s max_films={max_films}, max_attempts={max_attempts}.")
    print(f"Začínáme, chceme nasbírat {max_films} filmů.")

    attempts = 0
    while len(found_urls) < max_films and attempts < max_attempts:
        attempts += 1
        # Vygenerujeme náhodné číslo od 1 do 1 000 000
        num = random.randint(1, 1_000_000)

        if num in tried_numbers:
            continue  # už jsme toto číslo testovali
        tried_numbers.add(num)

        film_url = f"https://www.csfd.cz/film/{num}/"
        logging.info(f"Testuji: {film_url} (attempt={attempts}, found={len(found_urls)})")
        print(f"[{attempts}] Checking {film_url} ...")

        try:
            r = requests.get(film_url, headers=headers, timeout=10)
        except Exception as e:
            logging.error(f"Chyba při requestu {film_url}: {e}")
            print(f"Chyba při requestu {film_url}: {e}")
            continue

        if r.status_code == 200:
            # Otestujeme, zda stránka nehlásí "nenalezeno"
            if "Nepodařilo se" in r.text or "nenalezeno" in r.text or "Stránka neexistuje" in r.text:
                logging.info(f"Film {film_url} => NEEXISTUJE (obsah hlásí nenalezeno).")
                continue
            # Ověříme finální URL
            final_url = r.url
            if film_regex.match(final_url):
                found_urls.add(final_url)
                logging.info(f"Film {final_url} => OK, celkem máme {len(found_urls)}.")
                print(f"  -> Našli jsme film, celkem {len(found_urls)}.")
            else:
                logging.info(f"URL {final_url} neodpovídá formátu filmové stránky, přeskakuji.")
        else:
            logging.info(f"Film {film_url} => status_code={r.status_code}, přeskakuji.")

        # Každých 10 pokusů uložíme průběžný stav
        if attempts % 10 == 0:
            save_urls(found_urls, output_csv)

    # Konec - uložíme finální stav
    save_urls(found_urls, output_csv)
    logging.info(f"Konec. Celkem {len(found_urls)} filmů, {attempts} pokusů.")
    print(f"Konec. Nasbírali jsme {len(found_urls)} filmů, zkusili {attempts} pokusů.")


if __name__ == "__main__":
    crawl_csfd_random()
