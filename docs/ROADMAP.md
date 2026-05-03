# Roadmap - co jeszcze zrobic, zeby oddac projekt

Lista prosta, w kolejnosci. Odhaczaj co zrobione.

## Czesc kodowa (gotowa po tym wpisie)
- [x] Naprawic pusty `game_state.py` (byl tylko komentarz `# test`)
- [x] Naprawic `mechanics.py` - dopasowac nazwy (`sprawdz_rzut`) i argument rzutu
- [x] Wywalic `Pillow` z `gui.py` i `main.py` - zostaje tylko `tkinter` (standard lib)
- [x] Naprawic `gui.py` - sklejony komentarz z importem, hardkod sciezki Windows, brak `utworz_okno()`
- [x] Dorzucic warunki `min_hp`, `min_sanity`, `wymagany_przedmiot`
- [x] Dodac `cel_porazka` (gdzie iesc gdy test rzutu sie nie uda)
- [x] Napisac `data/story.json` z 12 wezlami pokrywajacymi wszystkie mechaniki
- [x] Sprawdzic ze gra przechodzi sciezke happy-path

## Co jeszcze zrobic samemu (co prowadzacy chce widziec)

### 1. Karta projektu (zalacznik z wymagan)
- [ ] Wpisac tytul: "Cien nad Arkham"
- [ ] Wpisac sklad zespolu (5 osob)
- [ ] Cel: tekstowa gra RPG inspirowana Cthulhu, GUI w tkinter
- [ ] Technologia: Python 3, tylko biblioteka standardowa (`tkinter`, `json`, `random`, `os`, `sys`)

### 2. Opis projektu + wymagania funkcjonalne i niefunkcjonalne
- [ ] Wymagania funkcjonalne (FR-1 ... FR-N):
  - FR-1: Gra wczytuje fabule z pliku JSON
  - FR-2: Gracz przechodzi miedzy wezlami fabuly poprzez wybory
  - FR-3: Gra obsluguje rzut kością (k20) jako test umiejetnosci
  - FR-4: Statystyki HP i Sanity moga rosnac/spadac w wyniku zdarzen
  - FR-5: Gra obsluguje ekwipunek (zbieranie przedmiotow)
  - FR-6: Gra ma menu glowne, ekran gry i ekran konca
  - FR-7: Gra ma 2 zakonczenia (dobre i zle)
  - FR-8: Gra konczy sie gdy HP=0 lub Sanity=0
- [ ] Wymagania niefunkcjonalne (NFR):
  - NFR-1: Gra dziala na Windows i Linux (Python 3.10+)
  - NFR-2: Gra korzysta tylko z biblioteki standardowej
  - NFR-3: Czas wczytywania menu < 1s
  - NFR-4: Tekst polski bez znakow diakrytycznych (uniknac problemow z UTF-8 na Windowsie)

### 3. Diagramy (1 na osobe = 5 sztuk)
- [ ] Diagram przypadkow uzycia (use case) - 1 sztuka, np. drawio (juz masz `others/Use Case.drawio`)
- [ ] Diagramy czynnosci (activity) - przyklady do narysowania:
  1. Aktywacja - sciezka gracza od menu do konca gry
  2. Aktywacja - wykonanie wyboru z testem rzutu kostka
  3. Aktywacja - aplikacja efektu wezla (zmiana HP/Sanity/ekwipunku)
  4. Aktywacja - sprawdzenie warunku wyboru (rzut, hp, sanity, przedmiot)
  5. Aktywacja - przejscie do ekranu konca gry (dobry/zly)

### 4. Test plan - 50 test case-ow (10 per osoba)
- [ ] Otworz `docs/TEST_PLAN.md` (gotowy szkic) i uzupelnij wedlug wzoru z zalacznika
- 5 obszarow testow po 10 przypadkow:
  - Osoba 1: testy wczytywania konfiguracji i fabuly (`config.json`, `story.json`)
  - Osoba 2: testy mechanik (rzut kostka, sprawdz_rzut, granice 0..100)
  - Osoba 3: testy silnika (przejscia miedzy wezlami, warunki, efekty)
  - Osoba 4: testy GUI (przyciski, wyswietlanie statystyk, ekran konca)
  - Osoba 5: testy integracyjne (cala sciezka happy-path, sciezka zlych zakonczen, restart)

### 5. Dokumentacja projektowa
- [ ] Spis tresci, opis architektury (5 plikow Python + folder data + folder docs)
- [ ] Diagram modulow (kto kogo importuje):
  - `main.py` -> `gui.py`
  - `gui.py` -> `engine.py`, `game_state.py`
  - `engine.py` -> `game_state.py`, `mechanics.py`
- [ ] Instrukcja uruchomienia: `python main.py`
- [ ] Format pliku `story.json` z opisem pol (tekst, wybory, efekt, warunek, zakonczone)

## Kolejnosc oddawania (zalecana)
1. Najpierw uruchom gre lokalnie: `python main.py` - upewnij sie ze dziala u Ciebie.
2. Wypelnij karte projektu (10 min).
3. Narysuj 5 diagramow (po 1 na osobe) - mozesz uzyc draw.io lub plantUML.
4. Wpisz wymagania FR/NFR (15 min, gotowy szkic powyzej).
5. Skopiuj `docs/TEST_PLAN.md` do oddania - dorob pozostale przypadki na podstawie szkicu.
6. Zlozic dokumentacje projektowa w jeden PDF/Word.
