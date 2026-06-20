# Cień nad Arkham

Tekstowa gra przygodowa w klimacie grozy kosmicznej, inspirowana twórczością
H.P. Lovecrafta i E.A. Poego. Napisana w Pythonie z użyciem biblioteki tkinter.

---

## Opis

Gracz wciela się w Badacza, który budzi się w opuszczonym obozie w lasach wokół
Arkham. Rozgrywka polega na czytaniu opisów scen i dokonywaniu wyborów, które
kształtują dalszy przebieg historii. Bohater posiada dwa wskaźniki kondycji:

- **HP** (życie fizyczne) - zakres 0–100
- **Sanity** (poczytalność) - zakres 0–100

Część wyborów wymaga pomyślnego rzutu kością **k20**. Gra obejmuje 17 scen
i prowadzi do jednego z trzech zakończeń.

## Wymagania

- Python 3.x
- Biblioteka `tkinter` (wchodzi w skład standardowej biblioteki Pythona - brak
  dodatkowych zależności)

## Uruchomienie

```bash
python app/src/main.py
```

Dostępny jest też tryb konsolowy (do testowania logiki bez GUI):

```bash
python app/src/engine.py
```

## Rozgrywka

**Menu główne** oferuje trzy opcje: Nowa gra, Kontynuuj (dostępne po zapisaniu
partii) oraz Wyjście.

**Ekran gry** zawiera:
- opis aktualnej sceny
- statystyki postaci (HP, Sanity, ekwipunek) widoczne w górnej części ramki
- przyciski wyborów z podpowiedzią efektu każdego z nich
- grafikę kości k20 oraz wynik rzutu, gdy dany wybór wymaga testu

**Zapis i wczytanie** - jeden slot zapisany w `app/data/save.json`.

## Struktura projektu

```
cthulu-text-rpg/
├── app/
│   ├── src/
│   │   ├── main.py          # punkt wejścia - sprawdzenie plików i start GUI
│   │   ├── gui.py           # okno, menu, wyświetlanie scen, zapis/wczytanie
│   │   ├── engine.py        # silnik: przejścia między scenami, warunki, efekty
│   │   ├── game_state.py    # stan gracza (HP, Sanity, ekwipunek)
│   │   └── mechanics.py     # rzut kością k20 i ocena wyniku
│   ├── data/
│   │   ├── story.json       # fabuła: 17 węzłów, wybory, warunki, efekty
│   │   └── config.json      # konfiguracja startowa postaci
│   └── tiles/               # grafiki scen i interfejsu
├── tests/
│   └── test_gra.py          # 26 testów jednostkowych
└── docs/                    # dokumentacja projektu
```

## Testy

```bash
python tests/test_gra.py
```

Wynik: `PRZESZLO 26 / 26`. Szczegółowe przypadki testowe (40 testów, 10 na osobę)
dostępne są w `docs/testy/TestCases_Cien_nad_Arkham.xlsx` i `docs/testy/TESTY.md`.

## Dokumentacja

Katalog `docs/` zawiera:

| Plik | Zawartość |
|---|---|
| `OPIS_DZIALANIA.md` | Opis działania programu od ogółu do szczegółu |
| `OPIS_OSOBA_GK/AC/SK/BJ.md` | Szczegółowy opis zakresu każdego z członków zespołu |
| `FABULA.md` | Specyfikacja fabuły: drzewo scen, efekty, warunki |
| `DiagramKlas.drawio` | Diagram klas (model pojęciowy, UML) |
| `Karta projektu.docx` | Karta projektu |
| `testy/TESTY.md` | Metodyka i lista 40 przypadków testowych |
| `testy/TestCases_Cien_nad_Arkham.xlsx` | Arkusz przypadków testowych |
| `testy/DEFEKTY.md` | Rejestr wykrytych defektów (2 pozycje) |
| `use_cases/UseCase_System.drawio` | Diagram Use Case całego systemu |
| `use_cases/UseCase_Osoba_GK/AC/SK/BJ.drawio` | Diagramy Use Case per osoba |

Pliki `.drawio` można otwierać w [draw.io / diagrams.net](https://app.diagrams.net).

## Zespół

| Inicjały | Zakres odpowiedzialności |
|---|---|
| GK | Uruchomienie, okno i menu, zapis/wczytywanie (`main.py`, część `gui.py`) |
| AC | Wyświetlanie scen i ekranów, podpowiedzi efektów (część `gui.py`) |
| SK | Silnik fabuły i mechanika kości (`engine.py`, `mechanics.py`) |
| BJ | Stan gry oraz dane: fabuła i konfiguracja (`game_state.py`, `app/data/`) |

## Uwagi techniczne

Projekt korzysta wyłącznie ze standardowej biblioteki Pythona (`tkinter`, `json`,
`random`, `os`). Fabuła jest w całości zdefiniowana w pliku `story.json` - treść
i strukturę scen można modyfikować bez zmiany kodu źródłowego.
