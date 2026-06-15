# Roadmap - co zrobione i co zostalo

## Stan: GOTOWE DO ODDANIA

### Kod (gotowe)
- [x] Naprawiony `game_state.py`, `mechanics.py`, `engine.py`, `gui.py`, `main.py`
- [x] `gui.py` bez Pillow (tylko stdlib `tkinter`), z natywnym wyswietlaniem PNG
- [x] `gui.py` z osobnymi funkcjami: `wyswietl_scene`, `wyswietl_wybory`, `aktualizuj_statystyki`, `ekran_koncowy` (zgodnie ze specyfikacja)
- [x] `engine.py` obsluguje warunki: `rzut_koscia`, `min_hp`, `min_sanity` + opcjonalny `cel_porazka`
- [x] `data/story.json` z 12 wezlami pokrywajacymi wszystkie mechaniki
- [x] `assets/README.md` z lista 11 wymaganych plikow PNG
- [x] Smoke testy przeszly (silnik startuje, wszystkie sciezki dzialaja)

### Dokumenty (gotowe)
- [x] `docs/Karta_projektu_Cien_nad_Arkham.docx` - wypelniona karta projektu
- [x] `docs/TestCases_Cien_nad_Arkham.xlsx` - 50 test case-ow w formacie z przykladu
- [x] `docs/OBRONA.md` - sciaga na obrone
- [x] `docs/ROADMAP.md` - ten plik

## Co zostalo do zrobienia samemu

### Karta projektu
- [ ] Wpisac w docx prawdziwe dane:
  - Nazwa i adres uczelni / partnera
  - Imie i nazwisko prowadzacego + tytul
  - 5 x: imie i nazwisko czlonka zespolu + nr albumu
- Place'holder `[do uzupelnienia]` zostal w 11 miejscach.

### Grafiki PNG (juz w repo, folder `tiles/`)
- [x] camp.png, cave_entrance.png, cave_road.png, dice_roll.png, evil_eyes.png,
      gone_mad.png, old_man.png, win.png, wolf.png, wood_road.png
- Mozna podmienic na ladniejsze - struktura wezlow w story.json zostanie taka sama.

### Diagramy (1 na osobe = 5 sztuk)
- [ ] Diagram przypadkow uzycia (use case) - `others/Use Case.drawio` juz jest
- [ ] Diagramy czynnosci (activity) - 4 dodatkowe, propozycje:
  1. Sciezka gracza od menu do konca gry (sciezka happy-path)
  2. Wykonanie wyboru z testem rzutu kostka (sukces/porazka -> cel/cel_porazka)
  3. Aplikacja efektu wezla na stan (zmiana HP/Sanity z przycinaniem do 0..100)
  4. Sprawdzenie warunku wyboru (rzut, hp, sanity)
  5. Przejscie do ekranu konca gry (przez 0 HP, 0 Sanity, lub flage zakonczone)

### Pelna dokumentacja projektowa
- [ ] Sprawdzic `Karta_projektu_Cien_nad_Arkham.docx`, otworzyc w Word/LibreOffice, sformatowac jak chcesz
- [ ] Otworzyc `TestCases_Cien_nad_Arkham.xlsx` w Excelu, ewentualnie pokolorowac priorytety / wyniki
- [ ] Zlozyc wszystko (PDF + xlsx + diagramy) w jeden archiwum do oddania

### Kolejnosc oddawania
1. Otworz `python main.py` u siebie - upewnij sie ze gra dziala.
2. Otworz docx i xlsx - upewnij sie ze prowadzacy je otworzy bez bledu.
3. Uzupelnij dane personalne w docx.
4. Narysuj brakujace 4 diagramy (uzyj draw.io / plantUML / ołowka).
5. Wszystko spakuj w jeden zip i oddaj.

## Uruchomienie regeneratorow

Jezeli chcesz cos zmienic w karcie projektu lub testach, edytuj skrypty w `tools/` i uruchom:

```
python tools/build_docx.py    # regeneruje docs/Karta_projektu_Cien_nad_Arkham.docx
python tools/build_xlsx.py    # regeneruje docs/TestCases_Cien_nad_Arkham.xlsx
```
