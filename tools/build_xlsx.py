"""
Generator pliku TestCases_Cien_nad_Arkham.xlsx.
Format kolumn zgodny z przykladowym plikiem TestCases (1).xlsx:
  ID | Nazwa testu | Typ Testu | Konfiguracja | Priorytet | Reprodukcja | Kryteria | Wynik | Bug ID | Kryteria niepowodzenia

50 test case-ow, 10 na osobe (5 osob x 10).

Uruchomienie:
    python tools/build_xlsx.py
"""

import os
import zipfile
from xml.sax.saxutils import escape


TESTS = []


def add(nazwa, typ, konfig, prio, reprod, kryt, wynik="Pozytywny", bug="", krit_neg=""):
    TESTS.append((nazwa, typ, konfig, prio, reprod, kryt, wynik, bug, krit_neg))


# ── Osoba 1: Architekt Danych i Fabuly (TC-01..10) ──

add("Wczytanie config.json z poprawnym JSON",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. Uruchom python main.py\n2. Sprawdz czy gra wstaje bez bledu",
    "1. Plik wczytuje sie bez wyjatku\n2. Pojawia sie menu glowne")

add("Wczytanie story.json - liczba wezlow",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. Uruchom python engine.py\n2. Sprawdz log w konsoli",
    "1. W logu pojawia sie 'Wczytano fabule: 11 wezlow.'")

add("Brak pliku config.json",
    "Test destruktywny", "Windows 10 / Linux", "Wysoki",
    "1. Tymczasowo zmien nazwe data/config.json\n2. Uruchom python main.py",
    "1. Program pokazuje komunikat 'BLAD: brakuje plikow' i konczy dzialanie")

add("Brak pliku story.json",
    "Test destruktywny", "Windows 10 / Linux", "Wysoki",
    "1. Tymczasowo zmien nazwe data/story.json\n2. Uruchom python main.py",
    "1. Program pokazuje komunikat 'BLAD: brakuje plikow' i konczy dzialanie")

add("Niepoprawny JSON w story.json",
    "Test destruktywny", "Windows 10 / Linux", "Wysoki",
    "1. Edytuj story.json - usun jeden zamykajacy nawias }\n2. Uruchom python main.py i kliknij START",
    "1. Program rzuca wyjatek json.JSONDecodeError\n2. Gra nie wstaje",
    wynik="Negatywny",
    krit_neg="Brak grafycznego komunikatu o bledzie skladni JSON - widac tylko stack trace w konsoli.")

add("Polskie znaki w story.json (UTF-8)",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Sredni",
    "1. Uruchom gre i przejdz do dowolnego wezla\n2. Sprawdz czy polskie znaki (a, e, c, n, o, s, z) renderuja sie poprawnie",
    "1. Wszystkie polskie znaki sa widoczne bez znakow zastepczych")

add("Klucz 'tytul' w config.json zachowuje wartosc",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Niski",
    "1. Uruchom engine.py\n2. Sprawdz pierwsza linie po '=== TEST SILNIKA ==='",
    "1. W konsoli pojawia sie 'Gra: Cien nad Arkham v1.1'")

add("Brakujacy klucz 'start_wezel' w config.json",
    "Test destruktywny", "Windows 10 / Linux", "Sredni",
    "1. Usun klucz 'start_wezel' z config.json\n2. Uruchom main.py i kliknij START",
    "1. Program rzuca wyjatek KeyError",
    wynik="Negatywny",
    krit_neg="Brak walidacji configu przed uruchomieniem - blad pojawia sie dopiero po klikniciu START.")

add("Wezel docelowy z wyboru musi istniec",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Wysoki",
    "1. Edytuj story.json - dodaj wybor z 'cel': 'nieistniejacy'\n2. Uruchom gre i kliknij ten wybor",
    "1. W konsoli pokazuje sie 'BLAD: brak wezla nieistniejacy'\n2. Gra nie crashuje (zwraca None i konczy plynnie)")

add("Format pola 'efekt' aplikuje zmiane HP i Sanity",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Sredni",
    "1. Z menu START -> intro -> rozdroze\n2. Wybierz 'Zapusc sie do jaskini'\n3. Sprawdz Sanity",
    "1. Po wejsciu do wezla 'jaskinia' Sanity spada z 100 do 90")


# ── Osoba 2: Programista Silnika (TC-11..20) ──

add("Inicjalizacja stanu gry z wartosciami z config",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. Uruchom python engine.py\n2. Sprawdz pierwsze wyswietlone HP i Sanity",
    "1. HP = 100\n2. Sanity = 100\n3. obecny_wezel = 'intro'")

add("Przejscie z intro do rozdroze (pierwszy wybor po wstepie)",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. START\n2. Kliknij 'Wstajesz i ruszasz w droge'",
    "1. Wezel zmienia sie na 'rozdroze'\n2. W konsoli widac 'Przejscie -> rozdroze'")

add("Aplikowanie efektu wezla po wejsciu (jaskinia)",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. START -> rozdroze\n2. Wybierz 'Zapusc sie do jaskini'",
    "1. Wezel: jaskinia\n2. Sanity spada o 10 (do 90)")

add("Sprawdzanie warunku rzutu kostka - sukces",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. START -> rozdroze\n2. Klikaj 'Sprobuj wywazyc drzwi chaty' az do SUKCESU (rzut >= 12)",
    "1. Przejscie do wezla 'chata'\n2. Brak utraty HP\n3. Pojawia sie info o rzucie i grafika kosci")

add("Sprawdzanie warunku rzutu kostka - porazka (cel_porazka)",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. START -> rozdroze\n2. Klikaj 'Sprobuj wywazyc drzwi chaty' az do PORAZKI (rzut < 12)",
    "1. Przejscie do 'chata_porazka'\n2. HP spada o 10\n3. Pojawia sie info o rzucie i grafika kosci")

add("Warunek min_sanity niespelniony - skok do cel_porazka (szept)",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Wysoki",
    "1. Doprowadz Sanity ponizej 50 (np. wejdz do jaskini, glebin, wroc do rozdroze powtarzalnie)\n2. Idz na rozstaje\n3. Wybierz 'Zapytaj o droge'",
    "1. Warunek min_sanity 50 niespelniony\n2. Skok do wezla 'szept' (zamiast final_dobry)")

add("Warunek min_sanity spelniony - przejscie do final_dobry",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Wysoki",
    "1. START -> rozdroze (Sanity=100)\n2. Wybierz 'Idz lesnym duktem'\n3. Wybierz 'Zapytaj o droge'",
    "1. Warunek spelniony\n2. Przejscie do final_dobry\n3. Ekran ZWYCIESTWO")

add("Stan 'odwiedzone' nie zawiera duplikatow",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Niski",
    "1. Idz intro -> rozdroze -> jaskinia -> wroc do rozdroze -> jaskinia\n2. Wydrukuj stan['odwiedzone']",
    "1. Lista zawiera kazdy wezel tylko raz")

add("Funkcja czy_koniec wykrywa flage 'zakonczone: true'",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. Wywolaj czy_koniec(fabula['final_dobry'])\n2. Wywolaj czy_koniec(fabula['intro'])",
    "1. Dla final_dobry zwraca True\n2. Dla intro zwraca False")

add("Pobranie nieistniejacego wezla zwraca None",
    "Test destruktywny", "Windows 10 / Linux", "Sredni",
    "1. Wywolaj pobierz_wezel(fabula, 'xxx')",
    "1. Funkcja drukuje 'BLAD: brak wezla xxx'\n2. Zwraca None\n3. Nie rzuca wyjatku")


# ── Osoba 3: Programista Mechanik RPG (TC-21..30) ──

add("rzut_koscia(20) zwraca liczbe 1..20",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. Wywolaj 100 razy rzut_koscia(20) w petli\n2. Sprawdz min/max",
    "1. Wszystkie wyniki w przedziale 1..20")

add("rzut_koscia(6) zwraca liczbe 1..6",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Sredni",
    "1. Wywolaj 100 razy rzut_koscia(6)\n2. Sprawdz min/max",
    "1. Wszystkie wyniki w przedziale 1..6")

add("rzut_koscia bez argumentu uzywa domyslnie k20",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Sredni",
    "1. Wywolaj rzut_koscia() bez argumentu",
    "1. Wynik w przedziale 1..20")

add("sprawdz_rzut(15, 12) zwraca True (sukces)",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. Wywolaj sprawdz_rzut(15, 12)",
    "1. Funkcja zwraca True")

add("sprawdz_rzut(8, 12) zwraca False (porazka)",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. Wywolaj sprawdz_rzut(8, 12)",
    "1. Funkcja zwraca False")

add("sprawdz_rzut na granicy (rzut == prog) zwraca True",
    "Test brzegowy", "Windows 10 / Linux", "Wysoki",
    "1. Wywolaj sprawdz_rzut(12, 12)",
    "1. Funkcja zwraca True (warunek wynik >= prog, nie >)")

add("aktualizuj_stan z efektem hp -10",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. Stan z hp=100\n2. Wywolaj aktualizuj_stan(stan, {'hp': -10})",
    "1. Stan ma hp = 90")

add("aktualizuj_stan nie schodzi ponizej 0",
    "Test brzegowy", "Windows 10 / Linux", "Wysoki",
    "1. Stan z hp=5\n2. Wywolaj aktualizuj_stan(stan, {'hp': -100})",
    "1. Stan ma hp = 0 (a nie -95)")

add("aktualizuj_stan nie wchodzi powyzej 100",
    "Test brzegowy", "Windows 10 / Linux", "Wysoki",
    "1. Stan z hp=95\n2. Wywolaj aktualizuj_stan(stan, {'hp': 20})",
    "1. Stan ma hp = 100 (a nie 115)")

add("aktualizuj_stan z efektem hp i sanity rownolegle",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Sredni",
    "1. Stan z hp=100, sanity=100\n2. Wywolaj aktualizuj_stan(stan, {'hp': -5, 'sanity': -10})",
    "1. Stan ma hp=95, sanity=90")


# ── Osoba 4: Programista Interfejsu (TC-31..40) ──

add("Otwarcie okna gry pokazuje menu glowne",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. Uruchom python main.py",
    "1. Otwiera sie okno 'Cien nad Arkham'\n2. Widac napis CIEN NAD ARKHAM\n3. Widac przyciski START i WYJSCIE")

add("Klikniecie START przelacza na ekran gry z wstepem fabularnym",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. W menu glownym kliknij START",
    "1. Menu znika\n2. Pojawia sie tekst wstepu (intro)\n3. Widac jeden przycisk 'Wstajesz i ruszasz w droge'")

add("Wyswietlanie HP i Sanity na pasku statystyk",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. Po starcie gry sprawdz pasek na gorze",
    "1. Widac 'HP: 100' w kolorze zielonym\n2. Widac 'Sanity: 100' w kolorze niebieskim")

add("Aktualizacja HP po stracie - kolor czerwony przy < 30",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Wysoki",
    "1. Doprowadz HP do 25 (kilkukrotne nieudane wywazanie drzwi chaty)\n2. Sprawdz kolor etykiety HP",
    "1. Etykieta HP ma kolor czerwony (#e05555)")

add("Wyswietlanie obrazka sceny (PNG z folderu tiles/)",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. START\n2. Sprawdz obrazek nad tekstem wstepu",
    "1. Pojawia sie grafika tiles/camp.png\n2. Tekst sceny widoczny pod obrazkiem")

add("Brak pliku obrazka - graceful fallback",
    "Test destruktywny", "Windows 10 / Linux", "Sredni",
    "1. Tymczasowo przenies tiles/camp.png poza folder\n2. Uruchom gre i kliknij START",
    "1. Brak crashu\n2. Tekst sceny i przyciski sa widoczne\n3. Pole obrazka jest schowane")

add("Wyswietlanie wyniku rzutu kostka (grafika kosci + tekst)",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. START -> rozdroze\n2. Kliknij 'Sprobuj wywazyc drzwi chaty'",
    "1. Pojawia sie grafika tiles/dice_roll.png\n2. Pojawia sie tekst typu 'Rzut k20: 14 / prog: 12 -> SUKCES'\n3. Po kolejnym wyborze grafika znika")

add("Klikniecie wyboru wykonuje przejscie miedzy wezlami",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Krytyczny",
    "1. W ekranie gry kliknij dowolny wybor",
    "1. Tekst sceny zmienia sie na nastepny wezel\n2. Statystyki aktualizuja sie zgodnie z efektem")

add("Ekran konca - zwyciestwo (kolor zielony)",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Wysoki",
    "1. Przejdz cala gre szczesliwa sciezka do final_dobry\n2. Sprawdz ekran konca",
    "1. Pojawia sie grafika tiles/win.png\n2. Naglowek 'ZWYCIESTWO' w kolorze zielonym\n3. Widac przyciski 'Zagraj ponownie' i 'Wroc do menu'")

add("Ekran konca - przegrana fabularna (kolor czerwony)",
    "Test funkcjonalnosci", "Windows 10 / Linux", "Wysoki",
    "1. START -> rozdroze -> rozstaje -> 'Rzuc sie z piesciami'",
    "1. Wezel atak_potwora pokazuje grafike tiles/wolf.png\n2. Naglowek 'KONIEC GRY' w kolorze czerwonym\n3. HP = 0")


# ── Osoba 5: Integrator i QA (TC-41..50) ──

add("Pelny przebieg - happy path przez chate (rzut sukces)",
    "Test integracyjny", "Windows 10 / Linux", "Krytyczny",
    "1. START\n2. intro -> rozdroze\n3. 'Sprobuj wywazyc drzwi chaty' az do SUKCESU\n4. 'Wyrusz droga wskazana na mapie'",
    "1. Gra konczy sie ZWYCIESTWEM\n2. HP > 0, Sanity > 0\n3. Grafika win.png")

add("Pelny przebieg - happy path przez rozstaje",
    "Test integracyjny", "Windows 10 / Linux", "Krytyczny",
    "1. START\n2. intro -> rozdroze -> 'Idz lesnym duktem'\n3. 'Zapytaj o droge'",
    "1. Gra konczy sie ZWYCIESTWEM\n2. Sanity = 100 (warunek min 50 spelniony)")

add("Utrata calosci sanity jednym wyborem (wpatrz sie w oczy)",
    "Test integracyjny", "Windows 10 / Linux", "Krytyczny",
    "1. START -> rozdroze -> jaskinia -> glebiny\n2. Wybierz 'Wpatrz sie w te oczy'",
    "1. Przejscie do final_szalenstwo\n2. Sanity = 0\n3. Ekran KONIEC GRY z grafika gone_mad.png")

add("Utrata calosci hp jednym wyborem (atak na starca)",
    "Test integracyjny", "Windows 10 / Linux", "Krytyczny",
    "1. START -> rozdroze -> rozstaje\n2. Wybierz 'Rzuc sie na niego z piesciami'",
    "1. Przejscie do atak_potwora\n2. HP = 0\n3. Ekran KONIEC GRY z grafika wolf.png")

add("Sciezka szept - nieudany test sanity prowadzi do szalenstwa",
    "Test integracyjny", "Windows 10 / Linux", "Wysoki",
    "1. Doprowadz Sanity ponizej 50 (kilka wejsc do jaskini i glebin)\n2. Idz do rozstaje\n3. Wybierz 'Zapytaj o droge'\n4. Kliknij dalej w wezle 'szept'",
    "1. Skok do szept (cel_porazka)\n2. Sanity spada o 30\n3. Po przycisku - final_szalenstwo")

add("Restart gry przyciskiem 'Zagraj ponownie'",
    "Test integracyjny", "Windows 10 / Linux", "Wysoki",
    "1. Zakoncz gre (dowolnie)\n2. Kliknij 'Zagraj ponownie'",
    "1. Stan resetuje sie (HP=100, Sanity=100)\n2. Gra zaczyna od wezla 'intro'")

add("Powrot do menu z trwajacej gry",
    "Test integracyjny", "Windows 10 / Linux", "Sredni",
    "1. W trakcie gry kliknij przycisk 'Menu' na pasku statystyk",
    "1. Powrot do ekranu menu glownego\n2. Klikniecie START rozpoczyna nowa gre")

add("Zamkniecie gry przyciskiem WYJSCIE",
    "Test integracyjny", "Windows 10 / Linux", "Sredni",
    "1. W menu glownym kliknij WYJSCIE",
    "1. Okno zamyka sie\n2. Proces Pythona konczy sie czysto")

add("Test kompatybilnosci na Windows 10",
    "Test kompatybilnosci", "Windows 10", "Krytyczny",
    "1. Sklonuj repo\n2. python --version (3.10+)\n3. python main.py",
    "1. Gra wstaje bez bledow\n2. Tkinter renderuje okno\n3. Polskie znaki widoczne")

add("Test kompatybilnosci na Linux (Ubuntu/Mint)",
    "Test kompatybilnosci", "Ubuntu 22.04", "Krytyczny",
    "1. sudo apt install python3-tk\n2. git clone\n3. python3 main.py",
    "1. Gra wstaje bez bledow\n2. Tkinter renderuje okno\n3. Polskie znaki widoczne")


# --------------------------------------------------------------------------- xlsx

NS = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'


def col_letter(idx):
    s = ""
    while idx > 0:
        idx, r = divmod(idx - 1, 26)
        s = chr(65 + r) + s
    return s


def cell_str(ref, shared_idx):
    return f'<c r="{ref}" t="s"><v>{shared_idx}</v></c>'


def cell_num(ref, num):
    return f'<c r="{ref}"><v>{num}</v></c>'


def main():
    headers = ["ID", "Nazwa testu", "Typ Testu", "Konfiguracja", "Priorytet",
               "Reprodukcja", "Kryteria", "Wynik", "Bug ID", "Kryteria niepowodzenia"]

    strings = []
    string_index = {}

    def s_idx(text):
        text = text or ""
        if text not in string_index:
            string_index[text] = len(strings)
            strings.append(text)
        return string_index[text]

    for h in headers:
        s_idx(h)

    rows_xml = []

    cells = []
    for i, h in enumerate(headers):
        cells.append(cell_str(f"{col_letter(i+1)}1", s_idx(h)))
    rows_xml.append(f'<row r="1">{"".join(cells)}</row>')

    for idx, t in enumerate(TESTS, start=1):
        nazwa, typ, konfig, prio, reprod, kryt, wynik, bug, krit_neg = t
        row_idx = idx + 1
        cells = []
        cells.append(cell_num(f"A{row_idx}", idx))
        cells.append(cell_str(f"B{row_idx}", s_idx(nazwa)))
        cells.append(cell_str(f"C{row_idx}", s_idx(typ)))
        cells.append(cell_str(f"D{row_idx}", s_idx(konfig)))
        cells.append(cell_str(f"E{row_idx}", s_idx(prio)))
        cells.append(cell_str(f"F{row_idx}", s_idx(reprod)))
        cells.append(cell_str(f"G{row_idx}", s_idx(kryt)))
        cells.append(cell_str(f"H{row_idx}", s_idx(wynik)))
        if bug:
            cells.append(cell_str(f"I{row_idx}", s_idx(bug)))
        if krit_neg:
            cells.append(cell_str(f"J{row_idx}", s_idx(krit_neg)))
        rows_xml.append(f'<row r="{row_idx}">{"".join(cells)}</row>')

    sheet_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet {NS}>
<dimension ref="A1:J{len(TESTS)+1}"/>
<sheetViews><sheetView tabSelected="1" workbookViewId="0"/></sheetViews>
<sheetFormatPr defaultRowHeight="15"/>
<cols>
  <col min="1" max="1" width="6"/>
  <col min="2" max="2" width="40"/>
  <col min="3" max="3" width="20"/>
  <col min="4" max="4" width="18"/>
  <col min="5" max="5" width="12"/>
  <col min="6" max="6" width="55"/>
  <col min="7" max="7" width="55"/>
  <col min="8" max="8" width="12"/>
  <col min="9" max="9" width="8"/>
  <col min="10" max="10" width="55"/>
</cols>
<sheetData>
{"".join(rows_xml)}
</sheetData>
</worksheet>'''

    si_xml = []
    for s in strings:
        si_xml.append(f'<si><t xml:space="preserve">{escape(s)}</t></si>')
    shared_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<sst {NS} count="{len(strings)}" uniqueCount="{len(strings)}">
{"".join(si_xml)}
</sst>'''

    workbook_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook {NS} xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets><sheet name="TestCases" sheetId="1" r:id="rId1"/></sheets>
</workbook>'''

    workbook_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>
</Relationships>'''

    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>
</Types>'''

    rels_root = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>'''

    out_path = "docs/TestCases_Cien_nad_Arkham.xlsx"
    os.makedirs("docs", exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels_root)
        z.writestr("xl/workbook.xml", workbook_xml)
        z.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        z.writestr("xl/sharedStrings.xml", shared_xml)
        z.writestr("xl/worksheets/sheet1.xml", sheet_xml)

    print(f"OK -> {out_path} ({os.path.getsize(out_path)} bajtow, {len(TESTS)} testow)")


if __name__ == "__main__":
    main()
