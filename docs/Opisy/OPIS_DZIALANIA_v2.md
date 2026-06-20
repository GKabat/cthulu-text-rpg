# Cień nad Arkham - dokumentacja techniczna

## 1. Opis ogólny

Tekstowa gra przygodowa w klimacie grozy (inspirowana Lovecraftem i Poem).
Gracz czyta opisy scen i dokonuje wyborów kształtujących przebieg historii.
Część wyborów wymaga pomyślnego rzutu kością k20. Bohater posiada dwa wskaźniki:
**HP** (życie) i **Sanity** (poczytalność), utrzymywane w zakresie 0-100.
Gra kończy się dotarciem do sceny końcowej lub spadkiem HP/Sanity do zera.

Stos technologiczny: Python 3, biblioteka tkinter (stdlib), dane w JSON.
Brak zewnętrznych zależności.

---

## 2. Struktura modułów

| Moduł | Odpowiedzialność |
|---|---|
| `app/src/main.py` | Punkt wejścia: walidacja plików danych, uruchomienie okna |
| `app/src/gui.py` | Interfejs graficzny: okno, menu, renderowanie scen, zapis/wczytanie |
| `app/src/engine.py` | Silnik fabuły: przejścia między scenami, warunki, efekty |
| `app/src/game_state.py` | Stan gracza: inicjalizacja, aktualizacja HP/Sanity/ekwipunku |
| `app/src/mechanics.py` | Mechanika kości: rzut k20, ocena wyniku |
| `app/data/story.json` | Fabuła: węzły scen, wybory, warunki, efekty |
| `app/data/config.json` | Konfiguracja startowa: tytuł, HP/Sanity, scena startowa |
| `app/tiles/` | Zasoby graficzne: ramka okna, kość, obrazki scen |

Podział zapewnia izolację odpowiedzialności: logika gry (engine, mechanics, game_state)
jest niezależna od interfejsu (gui) i może być testowana bez okna.

---

## 3. Kluczowe pojęcia

**Fabuła** - słownik wczytany z `story.json`, mapujący identyfikatory scen
na obiekty węzłów. Klucze to nazwy scen (np. `"rozdroze"`), wartości to deskryptory scen.

**Węzeł** - pojedyncza scena: tekst, opcjonalny obrazek, lista wyborów,
opcjonalny efekt (zmiana HP/Sanity/ekwipunku), flaga końca gry.

**Stan gry** - słownik przechowujący bieżący stan bohatera:
obecna scena, HP, Sanity, nazwa postaci, lista odwiedzonych scen, ekwipunek,
wynik ostatniego rzutu kością.

**Efekt** - słownik opisujący zmianę stanu przy wejściu do sceny: `hp`, `sanity`,
`dodaj_przedmiot`. Wszystkie pola opcjonalne.

**Warunek** - ograniczenie dostępu do wyboru: rzut kością k20 z progiem,
minimum HP lub minimum Sanity. Brak warunku (`null`) oznacza wybór zawsze dostępny.

---

## 4. Przepływ sterowania

```
main.py: sprawdz_pliki() -> uruchom()
         |
         v
gui.py: utworz_okno() -> pokaz_menu()
         |
         | NOWA GRA / KONTYNUUJ
         v
gui.py: zaladuj_dane() / wczytaj_gre()
         |
         v
         +-------------------------------+
         |  odswiez_scene()              | <----+
         |  (scena, statystyki, wybory)  |      |
         +-------------------------------+      |
                    |                           |
                    | klik wyboru               |
                    v                           |
         obsluz_wybor(wybor)                    |
                    |                           |
                    v                           |
         engine.wykonaj_wybor():                |
           1. sprawdz_warunek()                 |
           2. ustaw obecny_wezel                |
           3. aktualizuj_stan() [efekt sceny]   |
                    |                           |
                    +---------------------------+
                    |
                    | scena końcowa lub HP/Sanity = 0
                    v
         ekran_koncowy()
```

Efekt wejścia do sceny nakładany jest w momencie przejścia (przed renderowaniem),
nie podczas wyświetlania.

---

## 5. Opis modułów

### `mechanics.py`

Dwie funkcje bezstanowe:

- `rzut_koscia(zakres=20)` - zwraca losową liczbę całkowitą z zakresu [1, zakres].
- `sprawdz_rzut(wynik, prog)` - zwraca `True` gdy `wynik >= prog`.

### `game_state.py`

- `inicjalizuj_stan(config)` - tworzy słownik stanu na podstawie `config.json`:
  HP i Sanity z konfiguracji, scena z pola `start_wezel`, puste listy odwiedzonych
  i ekwipunku, `ostatni_rzut = None`.
- `aktualizuj_stan(stan, efekt)` - aplikuje efekt sceny; HP i Sanity przycinane
  do zakresu 0-100 (clamping).
- `pobierz_stan(stan)` - zwraca płytką kopię stanu.

### `engine.py`

- `wczytaj_fabule(sciezka)` - deserializuje `story.json` do słownika.
- `pobierz_wezel(fabula, id_wezla)` - zwraca węzeł lub `None` przy braku klucza.
- `sprawdz_warunek(warunek, stan)` - ewaluuje warunek wyboru; przy rzucie kością
  zapisuje wynik do `stan["ostatni_rzut"]` (odczytywany przez GUI po renderowaniu).
- `wykonaj_wybor(fabula, wybor, stan)` - główna funkcja przejścia: sprawdza warunek,
  wyznacza cel (`cel` lub `cel_porazka`), aktualizuje `obecny_wezel` i nakłada efekt.
- `czy_koniec(wezel)` - zwraca wartość pola `zakonczone` (domyślnie `False`).

Moduł zawiera tryb konsolowy (`__main__`), pozwalający przechodzić grę w terminalu
bez uruchamiania GUI. Ścieżki danych kotwiczone względem `__file__`.

### `gui.py`

Zbudowany na `tk.Canvas` - jeden Canvas wypełnia okno, wszystkie elementy
(tekst, obrazki, przyciski) pozycjonowane współrzędnymi bezwzględnymi.

Ramka okna (`tiles/frame.png`) renderowana na wierzchu; jej środek jest
przezroczysty i wyznacza obszar treści. Pozycja i rozmiar obszaru przechowywane
jako ułamki wymiarów okna, co umożliwia skalowanie na ekranach o różnej rozdzielczości
(pełny rozmiar 1184x912, mały 592x456).

Zmienne globalne modułu (`fabula`, `stan`, `canvas`, itp.) pełnią rolę wspólnego
stanu UI, dostępnego dla wszystkich funkcji modułu.

Podpowiedzi efektów na przyciskach wyborów (`podpowiedz_efektu`) generowane
dynamicznie z danych sceny.

Zapis gry: `json.dump(stan, plik)` - stan jako słownik prostych typów
serializuje się bez dodatkowego kodu. Jeden slot zapisu (`app/data/save.json`).

### `main.py`

- `sprawdz_pliki()` - weryfikuje istnienie `config.json` i `story.json`;
  przy braku kończy proces z kodem 1.
- `uruchom()` - wczytuje GUI przez opóźniony import (po walidacji plików),
  buduje okno i wchodzi w pętlę zdarzeń tkinter.

---

## 6. Format danych

### `story.json`

```json
"rozdroze": {
  "tekst": "Ścieżka rozdziela się na trzy...",
  "obrazek": "tiles/wood_road.png",
  "wybory": [
    {"tekst": "Zejść do jaskini.", "cel": "jaskinia", "warunek": null},
    {
      "tekst": "Naprzeć na drzwi.",
      "cel": "chata",
      "warunek": {"rzut_koscia": true, "prog": 12},
      "cel_porazka": "chata_porazka"
    }
  ],
  "efekt": {"sanity": -10},
  "zakonczone": false
}
```

Pole `obrazek` zawiera ścieżkę względną do `ROOT` (`app/`), łączoną przez GUI
przy wczytywaniu zasobu. Pole `efekt` i `warunek` opcjonalne (`null` = brak).
Sceny końcowe zawierają dodatkowo `"zakonczenie": "dobry"` lub `"zly"`.

### `config.json`

```json
{
  "tytul": "Cień nad Arkham",
  "wersja": "2.0",
  "postac": {"nazwa": "Badacz", "hp": 100, "sanity": 100},
  "start_wezel": "intro"
}
```

---

## 7. Decyzje projektowe

| Decyzja | Uzasadnienie |
|---|---|
| Stan jako słownik | Serializowalny przez `json.dump` bez dodatkowego kodu; wystarczający dla prostej struktury |
| Fabuła w JSON | Separacja treści od logiki; możliwość edycji bez znajomości Pythona |
| tkinter (stdlib) | Brak zewnętrznych zależności; działa na standardowej instalacji Python 3 |
| Bez Pillow | tkinter obsługuje PNG natywnie od Pythona 3.x |
| Clamping HP/Sanity w `aktualizuj_stan` | Jedno miejsce pilnuje niezmiennika 0-100 |
| Efekt przy wejściu do sceny | Uproszczony model: wybór decyduje o celu, scena decyduje o skutkach |
| Proste funkcje zamiast klas | Skala projektu nie uzasadnia narzutu obiektowości |
