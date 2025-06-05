#Autor - Pavel Winter, 3.A, SPŠD Motol, negativnibomba23@gmail.com
#Poznámka autora: Užijte si to.

import sys
import csv
import requests
from bs4 import BeautifulSoup

# Požadované strany podle zadání
POZADOVANE_STRANY = {
    "Občanská demokratická strana": "ODS",
    "Česká str.sociálně demokrat.": "ČSSD",
    "Komunistická str.Čech a Moravy": "KSČM",
    "ANO 2011": "ANO 2011",
    "Svoboda a přímá demokracie - Tomio Okamura (SPD)": "SPD",
    "Česká pirátská strana": "Piráti"
}


def get_obec_urls(main_url):
    base = "https://volby.cz/pls/ps2017nss/"
    r = requests.get(main_url)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.select("td.cislo a")
    urls = [base + a["href"] for a in links]
    return urls


def parse_obec(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    # Základní info
    h3 = soup.find("h3").text.strip()
    kod_obce = h3.split(":")[0].split(" ")[-1]
    nazev_obce = h3.split(":")[1].strip()

    volici = soup.find("td", headers="sa2").text.strip().replace("\xa0", "")
    obalky = soup.find("td", headers="sa3").text.strip().replace("\xa0", "")
    platne = soup.find("td", headers="sa6").text.strip().replace("\xa0", "")

    # Strany a hlasy
    strany = soup.find_all("td", class_="overflow_name")
    hlasy = soup.find_all("td", headers=lambda h: h and "t1sa2" in h)

    vysledky = {zkr: "0" for zkr in POZADOVANE_STRANY.values()}

    for s, h in zip(strany, hlasy):
        nazev = s.text.strip()
        if nazev in POZADOVANE_STRANY:
            zkr = POZADOVANE_STRANY[nazev]
            pocet = h.text.strip().replace("\xa0", "")
            vysledky[zkr] = pocet

    return [kod_obce, nazev_obce, volici, obalky, platne] + [vysledky[zkr] for zkr in ["ODS", "ČSSD", "KSČM", "ANO 2011", "SPD", "Piráti"]]


def main():
    if len(sys.argv) != 3:
        print("Použití: python projekt_3.py <URL> <výstupní_soubor.csv>")
        exit(1)

    input_url = sys.argv[1]
    output_csv = sys.argv[2]

    print("Stahuji seznam obcí...")
    urls = get_obec_urls(input_url)
    print(f"Nalezeno obcí: {len(urls)}")

    print("Zpracovávám obce...")
    data = []
    for url in urls:
        radek = parse_obec(url)
        data.append(radek)

    print("Ukládám do CSV...")
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        hlavicka = ["kód obce", "název obce", "voliči v seznamu", "vydané obálky", "platné hlasy", "ODS", "ČSSD", "KSČM", "ANO 2011", "SPD", "Piráti"]
        writer.writerow(hlavicka)
        writer.writerows(data)

    print(f"✅ Hotovo! Výsledky zapsány do: {output_csv}")


if __name__ == "__main__":
    main()