# Cień nad Arkham

Tekstowa gra paragrafowa (RPG) w klimacie grozy (inspiracje H.P. Lovecraftem
i E.A. Poem). Projekt zaliczeniowy z przedmiotu **Projekt wdrożeniowy**
(kierunek Informatyka). Napisana w Pythonie, w bibliotece **tkinter**.

## O grze

Budzisz się jako badacz w opuszczonym obozie w lasach wokół Arkham. Czytasz
opisy scen i wybierasz, co zrobić. Bohater ma dwa wskaźniki — **HP** (życie)
i **Sanity** (poczytalność), oba w zakresie 0–100. Część wyborów rozstrzyga
**rzut kością k20**. Gra prowadzi przez 17 scen do jednego z **trzech
zakończeń** (zwycięstwo albo dwa złe końce).

## Jak uruchomić

Wymagania: **Python 3** z biblioteką **tkinter** (wchodzi w skład standardowej
biblioteki — nie trzeba nic instalować).

```bash
python REFACTOR/main.py
```

Tryb tekstowy (konsolowy, do szybkiego sprawdzania logiki) uruchamia się
z wnętrza katalogu nowej wersji:

```bash
cd REFACTOR
python engine.py
```

## Rozgrywka

- **Menu:** Nowa gra / Kontynuuj (aktywne, gdy istnieje zapis) / Wyjście.
- **Ekran gry:** opis sceny, obrazek, statystyki (HP, Sanity, ekwipunek) oraz
  przyciski wyborów. Każdy przycisk ma podpowiedź, co dany wybór robi.
- **Rzut kością:** gdy wybór wymaga testu, pod przyciskami pokazuje się grafika
  kości i wynik (np. `Rzut k20: 14 / prog 12 -> SUKCES`).
- **Zapis / wczytanie:** przyciski w grze oraz „Kontynuuj" w menu
  (jeden slot zapisu: `REFACTOR/data/save.json`).

## Struktura projektu

```
cthulu-text-rpg/
├── REFACTOR/            # aktualna wersja gry
│   ├── main.py          # uruchomienie
│   ├── gui.py           # okno i interfejs (tkinter)
│   ├── engine.py        # silnik: przejścia między scenami, warunki
│   ├── game_state.py    # stan gracza (HP, Sanity, ekwipunek)
│   ├── mechanics.py     # rzut kością k20
│   ├── data/            # story.json (fabuła), config.json (ustawienia)
│   ├── tiles/           # ramka i grafika kości (lokalne)
│   ├── tests/           # test_gra.py (testy logiki)
│   └── docs/            # pełna dokumentacja (poniżej)
├── tiles/               # grafiki scen (wspólne)
└── ARCHIWUM/            # poprzednia, schowana wersja
```

## Testy

Logikę gry sprawdza zestaw testów uruchamianych jednym poleceniem:

```bash
python REFACTOR/tests/test_gra.py
```

Wynik: `PRZESZLO 26 / 26`. Pełny zestaw 40 przypadków testowych (10 na osobę)
jest w `REFACTOR/docs/TestCases_Cien_nad_Arkham.xlsx` oraz `REFACTOR/docs/TESTY.md`.

## Dokumentacja

W katalogu `REFACTOR/docs/`:

- **OPIS_DZIALANIA.md** — jak działa program, od ogółu do szczegółu.
- **OPIS_OSOBA_A/B/C/D.md** — szczegółowy opis części każdej z 4 osób.
- **FABULA.md** — pełna specyfikacja fabuły i mechaniki.
- **TESTY.md** + **TestCases_Cien_nad_Arkham.xlsx** — przypadki testowe.
- **DEFEKTY.md** — rejestr wykrytych defektów.
- **UseCase_System.drawio**, **UseCase_Osoba_A/B/C/D.drawio** — diagramy Use Case.
- **DiagramKlas.drawio** — diagram klas (model pojęciowy).
- **Karta projektu.docx** — karta projektu.

Pliki `.drawio` otwiera się w [draw.io / diagrams.net](https://app.diagrams.net).

## Zespół

Projekt 4-osobowy. Podział pracy na moduły:

| Osoba | Zakres |
|---|---|
| A | uruchomienie, okno i menu, zapis/wczytywanie (`main.py`, część `gui.py`) |
| B | wyświetlanie scen i ekranów, podpowiedzi (część `gui.py`) |
| C | silnik fabuły i mechanika kości (`engine.py`, `mechanics.py`) |
| D | stan gry oraz dane: fabuła i konfiguracja (`game_state.py`, `data/`) |

## Uwagi

Gra korzysta wyłącznie ze standardowej biblioteki Pythona (tkinter, json,
random, os). Stan gry trzymany jest w słowniku, a fabuła w pliku JSON — dzięki
temu treść można zmieniać bez ruszania kodu.
