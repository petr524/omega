import csv
import requests
from bs4 import BeautifulSoup
import re

def parse_film_details(url):
    """
    Z dané URL (detail filmu na CSFD) vytěží pět věcí:
      - country (např. 'USA')
      - length (např. '142 min')
      - genre (např. 'Drama / Krimi')
      - rating_percent (např. '95%')
      - rating_count (např. '(592 453)')

    Vrací slovník s těmito klíči.
    Pokud něco nenajde, vrátí prázdný řetězec.
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    result = {
        "url": url,
        "country": "",
        "length": "",
        "genre": "",
        "rating_percent": "",
        "rating_count": ""
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            print(f"[WARN] URL {url} vrací status_code={r.status_code}")
            return result

        soup = BeautifulSoup(r.text, "html.parser")

        # ---------------------------------------------------------------------
        # 1) Najdeme DIV (nebo jiný blok), kde je země, rok, délka, žánr.
        #    Např. <div class="film-info">. Upravit podle reálného HTML.
        info_div = soup.find("div", class_="film-info")
        if info_div:
            lines = list(info_div.stripped_strings)
            # lines může vypadat např.:
            # [
            #   "Vykoupení z věznice Shawshank",
            #   "The Shawshank Redemption (více)",
            #   "Drama / Krimi",
            #   "USA, 1994, 142 min",
            #   ...
            # ]

            # a) Žánr (hledáme řádek s lomítkem "/")
            for line in lines:
                if "/" in line:  # např. "Drama / Krimi"
                    result["genre"] = line.strip()
                    break

            # b) Země + délka (řádek, kde je "min")
            for line in lines:
                if "min" in line:
                    # Příklad: "USA, 1994, 142 min"
                    # Rozdělíme čárkami nebo lomítky, ořízneme mezery
                    parts = [p.strip() for p in re.split(r"[,/]", line) if p.strip()]
                    # Např. ["USA", "1994", "142 min"]
                    if len(parts) >= 1:
                        result["country"] = parts[0]  # "USA"
                    # Najdeme část, kde je 'min'
                    for p in parts:
                        if "min" in p:
                            result["length"] = p  # "142 min"
                    break

        # ---------------------------------------------------------------------
        # 2) Hodnocení - např. "95% (592 453)" v nějakém bloku <div class="film-rating">
        rating_div = soup.find("div", class_="film-rating")
        if rating_div:
            rating_text = rating_div.get_text(strip=True)
            # Příklad: "95% (592 453)"
            # Najdeme procenta a číslo v závorce regulárním výrazem
            match = re.search(r"(\d+)%\s*\(([\d\s]+)\)", rating_text)
            if match:
                # Skupina 1 = '95' => rating_percent
                # Skupina 2 = '592 453' => rating_count
                result["rating_percent"] = match.group(1) + "%"     # "95%"
                raw_count = match.group(2).strip()                  # "592 453"
                result["rating_count"] = f"({raw_count})"           # "(592 453)"

    except Exception as e:
        print(f"[ERROR] Chyba při parsování URL {url}: {e}")

    return result


def scrape_csfd_details(input_csv, output_csv):
    """
    Načte seznam URL (sloupec 'url') z input_csv,
    pro každou URL vytěží (country, length, genre, rating_percent, rating_count)
    a uloží je do output_csv.
    """

    # 1) Načteme vstupní CSV
    with open(input_csv, "r", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        urls = [row["url"] for row in reader if "url" in row]

    print(f"Načteno {len(urls)} URL z {input_csv}.")

    # 2) Připravíme výstupní CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as f_out:
        fieldnames = ["url", "country", "length", "genre", "rating_percent", "rating_count"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        # 3) Projdeme všechny URL, vytěžíme data a uložíme je do CSV
        for i, url in enumerate(urls, start=1):
            print(f"[{i}/{len(urls)}] Zpracovávám {url} ...")
            details = parse_film_details(url)
            writer.writerow(details)

    print(f"Hotovo. Výsledky uloženy v: {output_csv}")


if __name__ == "__main__":
    # Příklad použití:
    input_csv_path = r"C:\pv\Omega\csfd_random_links.csv"      # Vstupní CSV s odkazy
    output_csv_path = r"C:\pv\Omega\csfd_parsed_details.csv"   # Výstupní CSV s daty
    scrape_csfd_details(input_csv_path, output_csv_path)
