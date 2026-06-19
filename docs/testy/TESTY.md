# Przypadki testowe - Cień nad Arkham

40 przypadków testowych (10 na osobę), po jednym zestawie dla każdej z czterech
sekcji projektu. Każdy test jest unikalny i sprawdza inny fragment zachowania kodu.

## Jak podchodzimy do testowania (metodyka)

Testujemy "czarną skrzynkę": dla danego **wejścia** sprawdzamy, czy **wyjście**
jest takie, jakiego oczekujemy - nie patrząc, jak funkcja jest napisana w środku.
Przy projektowaniu testów kierujemy się kilkoma prostymi zasadami:

1. **Przypadki pozytywne i negatywne.** Pozytywny = "normalne" użycie, które ma
   zadziałać (np. wczytanie istniejącego węzła). Negatywny = sytuacja błędna lub
   brzegowa, która też musi być obsłużona (np. wczytanie węzła, którego nie ma →
   `None`, a nie wysypanie się gry).
2. **Wartości brzegowe (boundary).** Błędy najczęściej siedzą na granicach
   zakresów. Dlatego testujemy dokładnie próg, a nie środek przedziału:
   HP = 0 i HP = 100 (przycinanie), wynik rzutu = próg vs próg − 1, Sanity = 30
   (granica koloru), Sanity = 50 (warunek przejścia).
3. **Klasy równoważności.** Wartości, które program traktuje tak samo, grupujemy
   i bierzemy jednego przedstawiciela (np. "dowolne HP < 30" → bierzemy jedno,
   np. 10). Nie ma sensu testować 5, 10, 15 osobno - to ta sama klasa.
4. **Powtarzalność i niezależność.** Każdy test ustawia sobie własny stan
   startowy (warunki wstępne) i nie zależy od innych. Dla losowości (rzut kością)
   nie sprawdzamy konkretnej liczby, tylko **zakres** (1..20) albo regułę
   (wynik ≥ próg → sukces).
5. **Jeden test = jedna rzecz.** Każdy przypadek sprawdza jedno konkretne
   zachowanie, żeby po niepowodzeniu od razu było wiadomo, co się zepsuło.

**Jak je wykonać.** Testy logiki (silnik, stan, mechanika, dane) odpalamy z
konsoli - importujemy funkcję i porównujemy wynik z oczekiwanym (albo `python
engine.py` przechodzi grę w trybie tekstowym). Testy GUI wykonujemy ręcznie -
klikając w grze i patrząc, czy ekran wygląda zgodnie z oczekiwaniem (część da się
też sprawdzić, budując okno i odczytując właściwości elementów Canvasa).

**Priorytet** (kolumna Prio.): W = wysoki (kluczowa funkcja), Ś = średni,
N = niski (kosmetyka / rzadki przypadek).

---

## Sekcja A - Uruchomienie, okno i menu (`main.py` + część `gui.py`)

Funkcje: `sprawdz_pliki`, `utworz_okno`, `zaladuj_dane`, `pokaz_menu`.

| ID | Co testujemy | Warunki wstępne / dane | Kroki | Oczekiwany wynik | Prio. |
|---|---|---|---|---|---|
| A1 | `sprawdz_pliki` - brak danych | usuń/ukryj `data/story.json` | uruchom grę | program kończy się (`sys.exit(1)`) i wypisuje "BLAD: brakuje pliku: ...story.json" | W |
| A2 | `sprawdz_pliki` - komplet | oba pliki `config.json` i `story.json` istnieją | uruchom grę | brak przerwania, gra rusza dalej | W |
| A3 | `utworz_okno` - okno | - | wywołaj `utworz_okno()` | powstaje okno o tytule "Cien nad Arkham" z Canvasem wypełniającym okno | W |
| A4 | `utworz_okno` - wczytanie ramki | plik `tiles/frame.png` istnieje | utwórz okno | `obrazek_ramki` nie jest `None` (ramka wczytana) | Ś |
| A5 | `utworz_okno` - wczytanie kości | plik `tiles/dice_roll.png` istnieje | utwórz okno | `obrazek_kosci` nie jest `None`, jest przeskalowany | Ś |
| A6 | `utworz_okno` - mały ekran | ekran < 1240 px szer. lub < 1000 px wys. | utwórz okno | rozmiar okna 592 × 456, ramka pomniejszona 2× | Ś |
| A7 | `utworz_okno` - duży ekran | ekran ≥ 1240 × 1000 | utwórz okno | rozmiar okna 1184 × 912 | Ś |
| A8 | `zaladuj_dane` - stan startowy | poprawne `config.json` | wywołaj `zaladuj_dane()` | `fabula` i `stan` ustawione; stan: HP 100, Sanity 100, węzeł "intro", ekwipunek pusty | W |
| A9 | `pokaz_menu` - KONTYNUUJ zablokowane | brak pliku `data/save.json` | otwórz menu | przycisk KONTYNUUJ jest nieaktywny (disabled) | Ś |
| A10 | `pokaz_menu` - KONTYNUUJ aktywne | istnieje `data/save.json` | otwórz menu | przycisk KONTYNUUJ jest aktywny i wczytuje zapis | W |

---

## Sekcja B - Renderowanie sceny i ekrany (część `gui.py`)

Funkcje: `odswiez_scene`, `podpowiedz_efektu`, `ekran_koncowy`, `obsluz_wybor`.

| ID | Co testujemy | Warunki wstępne / dane | Kroki | Oczekiwany wynik | Prio. |
|---|---|---|---|---|---|
| B1 | Kolor HP - granica 30 | HP = 29 | odśwież scenę | napis HP w kolorze czerwonym (`#e05555`); dla HP = 30 byłby zielony | Ś |
| B2 | Kolor Sanity - niski | Sanity = 10 | odśwież scenę | napis Sanity w kolorze czerwonym (`#e05555`) | Ś |
| B3 | Ekwipunek pusty | ekwipunek = `[]` | odśwież scenę | wyświetla "Ekwipunek: (pusty)" | N |
| B4 | Ekwipunek z przedmiotem | ekwipunek = `["kieł wilka"]` | odśwież scenę | wyświetla "Ekwipunek: kieł wilka" | N |
| B5 | Liczba przycisków wyborów | węzeł `rozdroze` (3 wybory) | odśwież scenę | powstają dokładnie 3 przyciski wyboru (poza Menu/Zapisz/Wczytaj) | W |
| B6 | Podpowiedź efektu na przycisku | wybór "Zejść do jaskini" (cel: Sanity −10) | odśwież scenę | etykieta przycisku zawiera drugą linię "( Sanity -10 )" | W |
| B7 | Podpowiedź testu na przycisku | wybór "Naprzeć na drzwi" (rzut k20 ≥ 12) | odśwież scenę | etykieta zawiera "rzut k20 >= 12 \| sukces: ... \| porażka: HP -10" | W |
| B8 | Kość + wynik po rzucie | `stan["ostatni_rzut"]` = {wynik 14, prog 12, sukces True} | odśwież scenę | pod przyciskami pojawia się grafika kości oraz linia "Rzut k20: 14 / prog 12 -> SUKCES" (zielona) | W |
| B9 | Brak kości bez rzutu | `stan["ostatni_rzut"]` = `None` | odśwież scenę | brak grafiki kości i brak linii z wynikiem | Ś |
| B10 | Ekran końcowy | wywołanie `ekran_koncowy("dobry")` oraz `("zly")` | wyświetl ekran końca | dla "dobry" nagłówek "ZWYCIESTWO" (zielony), dla "zly" "KONIEC GRY" (czerwony), plus przyciski Zagraj ponownie / Wróć do menu | W |

---

## Sekcja C - Silnik fabuły i mechanika kości (`engine.py` + `mechanics.py`)

Funkcje: `rzut_koscia`, `sprawdz_rzut`, `wczytaj_fabule`, `pobierz_wezel`,
`sprawdz_warunek`, `wykonaj_wybor`, `czy_koniec`.

| ID | Co testujemy | Warunki wstępne / dane | Kroki | Oczekiwany wynik | Prio. |
|---|---|---|---|---|---|
| C1 | `rzut_koscia` - zakres | - | wywołaj 1000× `rzut_koscia(20)` | każdy wynik to liczba całkowita z przedziału 1..20 | W |
| C2 | `sprawdz_rzut` - sukces na granicy | wynik = 12, prog = 12 | `sprawdz_rzut(12, 12)` | zwraca `True` (warunek ≥) | W |
| C3 | `sprawdz_rzut` - porażka pod progiem | wynik = 11, prog = 12 | `sprawdz_rzut(11, 12)` | zwraca `False` | W |
| C4 | `wczytaj_fabule` | poprawny `story.json` | `wczytaj_fabule(STORY_PATH)` | zwraca słownik (dict) z węzłami, niepusty | Ś |
| C5 | `pobierz_wezel` - istnieje | wczytana fabuła | `pobierz_wezel(fabula, "rozdroze")` | zwraca słownik tego węzła (z tekstem i wyborami) | W |
| C6 | `pobierz_wezel` - nie istnieje | wczytana fabuła | `pobierz_wezel(fabula, "xxx")` | zwraca `None` i wypisuje "[engine] BLAD: brak wezla xxx" | W |
| C7 | `sprawdz_warunek` - brak warunku | warunek = `None` | `sprawdz_warunek(None, stan)` | zwraca `True` | Ś |
| C8 | `sprawdz_warunek` - min_sanity | Sanity = 55, potem 40; warunek `{"min_sanity": 50}` | sprawdź oba | dla 55 → `True`, dla 40 → `False` (granica 50) | W |
| C9 | `sprawdz_warunek` - rzut zapisany | warunek `{"rzut_koscia": true, "prog": 12}` | wykonaj sprawdzenie | `stan["ostatni_rzut"]` to słownik z polami `wynik`, `prog` (=12), `sukces` | W |
| C10 | `wykonaj_wybor` - ścieżka porażki | warunek niespełniony, wybór ma `cel_porazka` | wykonaj wybór (np. wymuś porażkę rzutu) | gra przechodzi do węzła z `cel_porazka` i nakłada jego efekt; `czy_koniec` dla węzła końcowego zwraca `True` | W |

---

## Sekcja D - Stan gry i dane (`game_state.py` + `data/story.json`, `config.json`)

Funkcje: `inicjalizuj_stan`, `aktualizuj_stan`, `pobierz_stan` + walidacja danych.

| ID | Co testujemy | Warunki wstępne / dane | Kroki | Oczekiwany wynik | Prio. |
|---|---|---|---|---|---|
| D1 | `inicjalizuj_stan` | config startowy | `inicjalizuj_stan(config)` | słownik: hp 100, sanity 100, obecny_wezel "intro", odwiedzone `[]`, ekwipunek `[]`, ostatni_rzut `None` | W |
| D2 | `aktualizuj_stan` - utrata HP | HP = 100, efekt `{"hp": -25}` | nałóż efekt | HP = 75 | W |
| D3 | `aktualizuj_stan` - dolne przycięcie | HP = 10, efekt `{"hp": -100}` | nałóż efekt | HP = 0 (nie schodzi poniżej 0) | W |
| D4 | `aktualizuj_stan` - górne przycięcie | Sanity = 90, efekt `{"sanity": 20}` | nałóż efekt | Sanity = 100 (nie przekracza 100) | W |
| D5 | `aktualizuj_stan` - przedmiot | ekwipunek `[]`, efekt `{"dodaj_przedmiot": "kieł wilka"}` | nałóż efekt | ekwipunek = `["kieł wilka"]` | Ś |
| D6 | `aktualizuj_stan` - efekt pusty | dowolny stan, efekt `None` | nałóż efekt | stan bez zmian | Ś |
| D7 | `pobierz_stan` - kopia | dowolny stan | weź kopię i zmień w niej HP | oryginalny stan się NIE zmienia (to kopia) | N |
| D8 | `story.json` - integralność | plik fabuły | wczytaj i policz | poprawny JSON, 17 węzłów, `start_wezel` "intro" istnieje w fabule | W |
| D9 | `story.json` - brak martwych linków | plik fabuły | dla każdego wyboru sprawdź `cel` i `cel_porazka` | każdy cel wskazuje na istniejący węzeł (żaden nie prowadzi donikąd) | W |
| D10 | `story.json` - spójność reguł | plik fabuły | przejdź węzły | każdy wybór z `rzut_koscia` ma `prog`; każdy węzeł z `zakonczone: true` ma `zakonczenie` ∈ {dobry, zly} | Ś |

---

## Pokrycie - co który zestaw sprawdza

- **A (10)** - start aplikacji, kontrola plików, budowa i skalowanie okna,
  wczytanie zasobów, stan startowy, logika menu (Kontynuuj).
- **B (10)** - kolory statystyk, ekwipunek, liczba i treść przycisków,
  podpowiedzi efektów, grafika i wynik rzutu, ekrany końca.
- **C (10)** - losowanie i próg kości, ładowanie fabuły, pobieranie węzłów,
  warunki wyborów (w tym zapis rzutu), ścieżka porażki, wykrycie końca.
- **D (10)** - inicjalizacja i aktualizacja stanu (z przycinaniem 0..100),
  ekwipunek, kopia stanu, integralność i spójność danych fabuły.

Każdy z 40 przypadków dotyczy innego zachowania - nie ma duplikatów.
