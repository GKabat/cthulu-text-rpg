"""
Generator pliku Karta_projektu_Cien_nad_Arkham.docx.
Buduje minimalny ale poprawny .docx (Word/LibreOffice otwiera bez bledu).
Times New Roman 12pt, interlinia 1.5 - zgodnie z wymogami szablonu uczelni.

Uruchomienie:
    python tools/build_docx.py
"""

import os
import zipfile
from xml.sax.saxutils import escape


# --------------------------------------------------------------------------- helpers


def p(text="", bold=False, italic=False, size=24, align="left", spacing=360):
    """Akapit Word. size = polowa pkt (24 = 12pt). spacing 360 = interlinia 1.5."""
    rpr = ""
    if bold:
        rpr += "<w:b/>"
    if italic:
        rpr += "<w:i/>"
    rpr += f'<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/><w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'

    align_xml = ""
    if align == "center":
        align_xml = '<w:jc w:val="center"/>'
    elif align == "right":
        align_xml = '<w:jc w:val="right"/>'
    elif align == "both":
        align_xml = '<w:jc w:val="both"/>'

    spacing_xml = f'<w:spacing w:line="{spacing}" w:lineRule="auto"/>'
    runs = ""
    if text:
        runs = f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r>'
    return f'<w:p><w:pPr>{spacing_xml}{align_xml}<w:rPr>{rpr}</w:rPr></w:pPr>{runs}</w:p>'


def heading(text, size=28):
    """Naglowek sekcji - bold, wieksza czcionka."""
    return p(text, bold=True, size=size, spacing=360)


def cell(text, bold=False, width=2500):
    """Komorka tabeli."""
    rpr = ""
    if bold:
        rpr += "<w:b/>"
    rpr += '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="22"/><w:szCs w:val="22"/>'
    runs = f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r>' if text else ""
    return (
        f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>'
        '<w:tcBorders><w:top w:val="single" w:sz="4" w:color="000000"/>'
        '<w:left w:val="single" w:sz="4" w:color="000000"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="000000"/>'
        '<w:right w:val="single" w:sz="4" w:color="000000"/></w:tcBorders>'
        '</w:tcPr>'
        f'<w:p><w:pPr><w:spacing w:line="276" w:lineRule="auto"/></w:pPr>{runs}</w:p>'
        '</w:tc>'
    )


def row(*cells):
    return "<w:tr>" + "".join(cells) + "</w:tr>"


def table(rows, widths=None):
    return (
        '<w:tbl><w:tblPr><w:tblW w:w="9000" w:type="dxa"/>'
        '<w:tblBorders>'
        '<w:top w:val="single" w:sz="4" w:color="000000"/>'
        '<w:left w:val="single" w:sz="4" w:color="000000"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="000000"/>'
        '<w:right w:val="single" w:sz="4" w:color="000000"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="000000"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="000000"/>'
        '</w:tblBorders></w:tblPr>'
        + "".join(rows)
        + "</w:tbl>"
    )


def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


# --------------------------------------------------------------------------- content


def build_body():
    parts = []

    # ── Strona tytulowa ─────────────────────────────────────────────────────
    parts.append(p(""))
    parts.append(p(""))
    parts.append(p(""))
    parts.append(p("RAPORT Z PROJEKTU WDROZENIOWEGO", bold=True, size=36, align="center"))
    parts.append(p("kierunek Informatyka", size=28, align="center"))
    parts.append(p(""))
    parts.append(p(""))
    parts.append(p("Cien nad Arkham", bold=True, size=44, align="center"))
    parts.append(p("Tekstowe RPG w klimacie Call of Cthulhu", italic=True, size=26, align="center"))
    parts.append(p(""))
    parts.append(p(""))
    parts.append(p(""))
    parts.append(p("Cactus Studio", bold=True, size=28, align="center"))
    parts.append(p("Gdansk 2026", size=24, align="center"))
    parts.append(page_break())

    # ── Karta projektu ──────────────────────────────────────────────────────
    parts.append(heading("Karta projektu", 32))
    parts.append(p(""))

    parts.append(p("Tytul projektu", bold=True))
    parts.append(p("Cien nad Arkham - tekstowe RPG w klimacie Call of Cthulhu z prostym GUI."))
    parts.append(p(""))

    # Dane partnerów
    parts.append(p("Dane Partnerow (Beneficjent, Zleceniodawca, Potencjalny Interesariusz)", bold=True))
    parts.append(table([
        row(cell("Nazwa", bold=True, width=2500), cell("[do uzupelnienia - nazwa uczelni / partnera]", width=6500)),
        row(cell("Adres", bold=True), cell("[do uzupelnienia - adres uczelni / partnera]")),
    ]))
    parts.append(p(""))

    # Prowadzący
    parts.append(p("Prowadzacy przedmiot Projekt wdrozeniowy", bold=True))
    parts.append(table([
        row(cell("Imie i nazwisko", bold=True, width=3500), cell("[do uzupelnienia]", width=5500)),
        row(cell("Stopien / Tytul naukowy", bold=True), cell("[do uzupelnienia]")),
    ]))
    parts.append(p(""))

    # Zespół - 5 osób
    parts.append(p("Czlonkowie Zespolu projektowego", bold=True))
    role = [
        ("Osoba 1 - Architekt Danych i Fabuly", "Projektowanie story.json i config.json, balans mechanik (HP, Sanity, progi rzutow), tresc fabularna."),
        ("Osoba 2 - Programista Silnika", "Implementacja engine.py i game_state.py - nawigacja po drzewku fabuly, zarzadzanie stanem gry."),
        ("Osoba 3 - Programista Mechanik RPG", "Implementacja mechanics.py - rzuty kostka, sprawdzenia warunkow, czyste funkcje obliczeniowe."),
        ("Osoba 4 - Programista Interfejsu", "Implementacja gui.py - okno Tkinter, przyciski wyborow, wyswietlanie obrazkow PNG."),
        ("Osoba 5 - Integrator i QA", "Implementacja main.py, zarzadzanie repozytorium Git, testowanie eksploracyjne, README, dokumentacja."),
    ]
    for r, z in role:
        parts.append(table([
            row(cell("Imie i nazwisko", bold=True, width=3000), cell("[do uzupelnienia]", width=6000)),
            row(cell("Nr albumu", bold=True), cell("[do uzupelnienia]")),
            row(cell("Rola w zespole", bold=True), cell(r)),
            row(cell("Zadania realizowane w projekcie", bold=True), cell(z)),
        ]))
        parts.append(p(""))

    # Cel
    parts.append(p("Cel projektu", bold=True))
    parts.append(p(
        "Stworzenie gry tekstowej typu RPG z elementami losowosci (rzuty kostka), "
        "rozgalezieniem fabuly i prostym interfejsem graficznym. Glownym celem dydaktycznym "
        "bylo nauczenie sie pracy zespolowej w Pythonie, podzialu odpowiedzialnosci miedzy "
        "modulami oraz uzywania kontroli wersji (Git/GitHub)."
    ))
    parts.append(p(""))

    # Metodologia
    parts.append(p("Metodologia", bold=True))
    parts.append(p(
        "Iteracyjne wytwarzanie oprogramowania z podzialem na 5 faz (przygotowanie srodowiska, "
        "analiza, prototyp 'kregoslupa', rozbudowa rownolegla, integracja i polerowanie). "
        "Architektura data-driven - silnik gry nie zna fabuly, wczytuje ja z plikow JSON."
    ))
    parts.append(p(""))

    # Rezultaty
    parts.append(p("Rezultat (rezultaty) projektu", bold=True))
    parts.append(p(
        "Dzialajaca gra napisana w Pythonie 3 z uzyciem wylacznie biblioteki standardowej. "
        "12 wezlow fabularnych, dwa zakonczenia, mechanika rzutow kostka i sprawdzen progowych "
        "(HP, Sanity). Gra uruchamia sie na Windows i Linuksie poleceniem 'python main.py'."
    ))
    parts.append(p(""))

    # Termin
    parts.append(p("Termin realizacji", bold=True))
    parts.append(p("3 tygodnie (21 dni roboczych) - kwiecien-maj 2026."))
    parts.append(page_break())

    # ── Szczegolowe zalozenia i realizacja ──────────────────────────────────
    parts.append(heading("Szczegolowe zalozenia i realizacja projektu", 32))

    parts.append(heading("1. Wprowadzenie i cele projektu", 26))
    parts.append(p(
        "Projekt 'Cien nad Arkham' jest tekstowa gra typu RPG (role-playing game) inspirowana "
        "swiatem Call of Cthulhu autorstwa H.P. Lovecrafta. Gracz wciela sie w rolę badacza, "
        "ktory budzi sie w opuszczonym obozie i musi przezyc noc w mglistym lesie, podejmujac "
        "decyzje wplywajace na losy postaci i ostateczne zakonczenie historii.",
        align="both"
    ))
    parts.append(p(
        "Glownym celem projektu bylo nauczenie sie tworzenia oprogramowania w zespole - od "
        "projektowania struktury danych, przez podzial pracy na moduly, az po integracje i testowanie. "
        "Drugorzednym celem bylo zapoznanie sie z biblioteka graficzna Tkinter oraz formatem JSON "
        "do przechowywania danych aplikacji.",
        align="both"
    ))
    parts.append(p(
        "Beneficjentem projektu jest spolecznosc studencka kierunku Informatyka jako material "
        "edukacyjny i przyklad architektury data-driven. Projekt jest udostepniony w repozytorium "
        "publicznym GitHub.",
        align="both"
    ))
    parts.append(p(""))

    parts.append(heading("2. Opis problemu lub potrzeby", 26))
    parts.append(p(
        "Studenci pierwszego roku Informatyki czesto maja trudnosci z przejsciem od cwiczen "
        "indywidualnych do realnej pracy zespolowej. Brak doswiadczenia z systemami kontroli "
        "wersji, podzialem odpowiedzialnosci i integracja modulow napisanych przez rozne osoby "
        "prowadzi do chaosu i konfliktow w kodzie.",
        align="both"
    ))
    parts.append(p(
        "Projekt 'Cien nad Arkham' zostal zaprojektowany jako odpowiedz na te potrzebe - zapewnia "
        "jasny podzial: jeden plik = jeden wlasciciel. Architektura data-driven oddziela tresc "
        "(JSON) od logiki (Python), co umozliwia rownoległa prace projektanta fabuly i programistow "
        "bez konfliktow.",
        align="both"
    ))
    parts.append(p(""))

    parts.append(heading("3. Zakres prac", 26))
    parts.append(p("W ramach MVP zaimplementowano:", bold=True))
    parts.append(p("- Silnik fabularny wczytujacy drzewko decyzyjne z pliku JSON."))
    parts.append(p("- Mechanike rzutu kostka k20 i sprawdzania progow."))
    parts.append(p("- Statystyki postaci: HP (zdrowie) i Sanity (poczytalnosc), zakres 0..100."))
    parts.append(p("- Interfejs graficzny w Tkinter z menu glownym, ekranem gry i ekranem konca."))
    parts.append(p("- Wyswietlanie obrazkow PNG dla scen."))
    parts.append(p("- 12 wezlow fabularnych z dwoma zakonczeniami (dobre / zle)."))
    parts.append(p(""))
    parts.append(p("Swiadomie wykluczono z zakresu MVP:", bold=True))
    parts.append(p("- System zapisu/odczytu gry (zlozona serializacja stanu)."))
    parts.append(p("- Baza danych SQL/SQLite (overkill dla 12 wezlow)."))
    parts.append(p("- Pygame (zbyt wysoki prog wejscia dla zespolu)."))
    parts.append(p("- System levelowania i ekwipunku (mozliwe rozszerzenie post-MVP)."))
    parts.append(p(""))

    parts.append(heading("4. Metodologia", 26))
    parts.append(p(
        "Wykorzystano iteracyjna metode wytwarzania oprogramowania z czeczes integracja co 2 dni. "
        "Architekturalne zasady projektu:",
        align="both"
    ))
    parts.append(p("a) Data-driven design - silnik gry operuje generycznie na danych z JSON. Zmiana "
                   "calej fabuly nie wymaga zmiany ani jednej linii kodu w engine.py.", align="both"))
    parts.append(p("b) Jeden plik = jeden wlasciciel - eliminuje konflikty w Git i upraszcza odpowiedzialnosc."))
    parts.append(p("c) Czyste funkcje w mechanics.py - kazda funkcja przyjmuje wejscie, zwraca wynik, "
                   "nie modyfikuje stanu globalnego, nie wyswietla tekstu.", align="both"))
    parts.append(p("d) Jedyne zrodlo prawdy o stanie - caly stan gry trzymany w jednym slowniku w game_state.py."))
    parts.append(p(""))
    parts.append(p("Narzedzia:", bold=True))
    parts.append(p("- Python 3 (tylko biblioteka standardowa: tkinter, json, random, os, sys)."))
    parts.append(p("- Git i GitHub do kontroli wersji."))
    parts.append(p("- Visual Studio Code jako edytor."))
    parts.append(p("- draw.io do diagramow UML."))
    parts.append(p(""))

    parts.append(heading("5. Harmonogram prac/dzialan", 26))
    parts.append(table([
        row(cell("Faza", bold=True, width=1500), cell("Dni", bold=True, width=1500), cell("Opis", bold=True, width=6000)),
        row(cell("Faza 0"), cell("1-2"), cell("Przygotowanie srodowiska: instalacja Pythona, VS Code, Git. Zalozenie repo GitHub.")),
        row(cell("Faza 1"), cell("2-4"), cell("Analiza i projektowanie: drzewko fabuly, struktury danych JSON, kontrakt funkcji.")),
        row(cell("Faza 2"), cell("4-7"), cell("Prototyp 'kregoslupa' - cala druzyna razem, 3-5 wezlow, gra dziala end-to-end.")),
        row(cell("Faza 3"), cell("7-14"), cell("Rozbudowa rownolegla - kazdy rozbudowuje swoja czesc, integracja co 2 dni.")),
        row(cell("Faza 4"), cell("14-18"), cell("Integracja, testy, poprawki bledow, obsluga przypadkow brzegowych.")),
        row(cell("Faza 5"), cell("18-21"), cell("Polerowanie, pixel art, README, dokumentacja, prezentacja.")),
    ]))
    parts.append(p(""))
    parts.append(p("Kamienie milowe:", bold=True))
    parts.append(p("- Dzien 7: gra dziala end-to-end (3 wezly, brzydka, ale dziala)."))
    parts.append(p("- Dzien 14: 12 wezlow fabularnych, wszystkie mechaniki zaimplementowane."))
    parts.append(p("- Dzien 21: gra gotowa do oddania, dokumentacja kompletna."))
    parts.append(p(""))

    parts.append(heading("6. Wyniki i osiagniecia", 26))
    parts.append(p("Osiagniete wyniki:", bold=True))
    parts.append(p("- W pelni dzialajaca gra napisana w Pythonie 3."))
    parts.append(p("- 12 wezlow fabularnych z roznymi sciezkami przechodzenia."))
    parts.append(p("- 3 typy warunkow: rzut kostka, minimalny HP, minimalny Sanity."))
    parts.append(p("- 2 zakonczenia (dobre i zle) plus konce przez 0 HP / 0 Sanity."))
    parts.append(p("- Interfejs graficzny z menu, ekranem gry i ekranem konca."))
    parts.append(p("- Pelne pokrycie testami eksploracyjnymi (50 test case-ow)."))
    parts.append(p(""))
    parts.append(p("Osiagniete cele dydaktyczne:", bold=True))
    parts.append(p("- Zespol nauczyl sie pracy z Git (clone, pull, commit, push, rozwiazywanie konfliktow)."))
    parts.append(p("- Wszyscy czlonkowie zespolu rozumieja architekture i potrafia ja wytlumaczyc."))
    parts.append(p("- Zaimplementowano architekture data-driven, ktora pozwala edytowac fabule bez zmian kodu."))
    parts.append(p(""))

    parts.append(heading("7. Analiza ryzyka", 26))
    parts.append(table([
        row(cell("Ryzyko", bold=True, width=4000), cell("Mitygacja zastosowana w projekcie", bold=True, width=5000)),
        row(cell("Rozjazd stanu gry miedzy modulami"), cell("Caly stan gry trzymany w jednym slowniku game_state. Tylko engine modyfikuje stan.")),
        row(cell("'Big bang' integracyjny pod koniec projektu"), cell("Kregoslup zbudowany razem w fazie 2, pelna integracja co 2 dni.")),
        row(cell("Konflikty w Git"), cell("Zasada: jeden plik = jeden wlasciciel. Pull przed kazda sesja pracy.")),
        row(cell("Brak umowy o interfejsach miedzy osobami"), cell("Pisemny kontrakt funkcji w dokumencie kontekst_projektu_dla_llm.md.")),
        row(cell("Hardkodowanie danych w kodzie"), cell("Cala tresc fabuly w story.json, konfiguracja w config.json.")),
        row(cell("Brak obslugi bledow uzytkownika"), cell("Try/except przy wczytywaniu plikow, fallback gdy brakuje obrazka.")),
        row(cell("Niezrozumienie kodu po oddaniu projektu"), cell("Materialy obronne w docs/OBRONA.md - 5 typowych pytan i odpowiedzi.")),
    ]))
    parts.append(p(""))

    parts.append(heading("8. Wnioski i rekomendacje", 26))
    parts.append(p(
        "Projekt potwierdzil ze architektura data-driven jest skutecznym rozwiazaniem dla "
        "zespolow poczatkujacych - oddzielenie tresci od logiki pozwala na rownolegla prace "
        "bez ciaglych konfliktow w kodzie. Zasada jeden plik = jeden wlasciciel sprawdzila sie "
        "i moze byc zalecana dla podobnych projektow studenckich.",
        align="both"
    ))
    parts.append(p(
        "Zalecenia dla kolejnych etapow rozwoju gry:",
        bold=True
    ))
    parts.append(p("- Dodanie systemu zapisu/odczytu gry (serializacja stanu do JSON)."))
    parts.append(p("- Rozbudowa fabuly do 30-50 wezlow."))
    parts.append(p("- Migracja z Tkinter na Pygame dla bogatszej grafiki."))
    parts.append(p("- Dodanie systemu ekwipunku i prostej walki."))
    parts.append(p("- Dzwiek i muzyka tla."))
    parts.append(p(""))

    parts.append(heading("9. Bibliografia", 26))
    parts.append(p("1. Dokumentacja Pythona 3 - https://docs.python.org/3/"))
    parts.append(p("2. Dokumentacja Tkinter - https://docs.python.org/3/library/tkinter.html"))
    parts.append(p("3. Specyfikacja JSON - https://www.json.org/"))
    parts.append(p("4. Pro Git (Scott Chacon, Ben Straub) - https://git-scm.com/book/"))
    parts.append(p("5. H.P. Lovecraft - 'Cien nad Innsmouth', 'Zew Cthulhu' (inspiracja klimatu)."))
    parts.append(p(""))

    parts.append(heading("10. Zalaczniki", 26))
    parts.append(p("- Repozytorium GitHub z pelnym kodem zrodlowym."))
    parts.append(p("- TestCases_Cien_nad_Arkham.xlsx - plan testow (50 przypadkow)."))
    parts.append(p("- Diagram przypadkow uzycia (Use Case) - others/Use Case.drawio."))
    parts.append(p("- Diagramy czynnosci (Activity) - 5 sztuk, po 1 na osobe."))
    parts.append(p("- docs/OBRONA.md - materialy do obrony projektu."))
    parts.append(p("- docs/ROADMAP.md - lista zadan i postepow projektu."))

    return "".join(parts)


# --------------------------------------------------------------------------- docx files


DOCUMENT_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>
{body}
<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>
</w:body>
</w:document>'''


CONTENT_TYPES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''


RELS_ROOT = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''


def main():
    out_path = "docs/Karta_projektu_Cien_nad_Arkham.docx"
    body = build_body()
    document_xml = DOCUMENT_XML.format(body=body)

    os.makedirs("docs", exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS_ROOT)
        z.writestr("word/document.xml", document_xml)

    print(f"OK -> {out_path} ({os.path.getsize(out_path)} bajtow)")


if __name__ == "__main__":
    main()
