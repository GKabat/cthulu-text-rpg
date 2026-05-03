# Test Plan - Cien nad Arkham

Wzorzec wpisu (1 wiersz = 1 test case):

| ID | Modul | Opis | Krok | Dane wejsciowe | Oczekiwany wynik | Status |
|---|---|---|---|---|---|---|

50 testow, podzielone na 5 obszarow po 10. Tu jest szkielet - dorób w razie potrzeby.

## Osoba 1 - testy konfiguracji i wczytywania danych (TC-CFG-01..10)

| ID | Modul | Opis | Krok | Dane wejsciowe | Oczekiwany wynik | Status |
|---|---|---|---|---|---|---|
| TC-CFG-01 | main.py | Brak `data/config.json` | uruchom main.py bez pliku config | brak pliku | program konczy sie z bledem "BLAD: brakuje plikow" | - |
| TC-CFG-02 | main.py | Brak `data/story.json` | uruchom bez story | brak story | program konczy sie z bledem | - |
| TC-CFG-03 | engine.py | Niepoprawny JSON w story | edytuj story.json (usun nawias) | bledny JSON | wyjatek `json.JSONDecodeError` | - |
| TC-CFG-04 | engine.py | Brakujacy klucz `start_wezel` | usun klucz z config | config bez `start_wezel` | wyjatek `KeyError` na starcie | - |
| TC-CFG-05 | game_state | Inicjalizacja stanu z domyslnymi wartosciami | wywolaj `inicjalizuj_stan(config)` | poprawny config | stan ma hp=100, sanity=100, pusty ekwipunek | - |
| TC-CFG-06 | engine.py | Ladowanie 12-wezlowej fabuly | wczytaj story.json | poprawny story | drukuje "Wczytano fabule: 12 wezlow." | - |
| TC-CFG-07 | engine.py | Zapytanie o wezel ktory nie istnieje | `pobierz_wezel(fabula, "xxx")` | id "xxx" | drukuje BLAD i zwraca None | - |
| TC-CFG-08 | game_state | Uzywanie konfiguracji z wlasnym imieniem postaci | config z "nazwa": "Test" | imie "Test" | stan ma `nazwa_postaci`: "Test" | - |
| TC-CFG-09 | game_state | Klucz `wersja` zachowany w configu | sprawdz po wczytaniu | "1.0" | "1.0" w slowniku | - |
| TC-CFG-10 | engine.py | Plik z polskimi znakami w UTF-8 | uzyj tekstu z ogonkami | UTF-8 | tekst wczytuje sie bez bledow | - |

## Osoba 2 - testy mechanik (TC-MECH-01..10)

| ID | Modul | Opis | Krok | Dane wejsciowe | Oczekiwany wynik | Status |
|---|---|---|---|---|---|---|
| TC-MECH-01 | mechanics | rzut_koscia(20) zwraca 1..20 | wywolaj 100x | k20 | wszystkie wyniki w 1..20 | - |
| TC-MECH-02 | mechanics | rzut_koscia(6) zwraca 1..6 | wywolaj 100x | k6 | wszystkie w 1..6 | - |
| TC-MECH-03 | mechanics | sprawdz_rzut(15, 12) | rzut 15 prog 12 | (15, 12) | True | - |
| TC-MECH-04 | mechanics | sprawdz_rzut(8, 12) | rzut 8 prog 12 | (8, 12) | False | - |
| TC-MECH-05 | mechanics | sprawdz_rzut na granicy (rzut == prog) | (12, 12) | (12, 12) | True | - |
| TC-MECH-06 | game_state | aktualizuj_stan z hp -10 | hp 100 -> -10 | {"hp": -10} | hp=90 | - |
| TC-MECH-07 | game_state | aktualizuj_stan nie schodzi ponizej 0 | hp 5 -> -100 | {"hp": -100} | hp=0 | - |
| TC-MECH-08 | game_state | aktualizuj_stan nie wchodzi powyzej 100 | hp 95 -> +20 | {"hp": +20} | hp=100 | - |
| TC-MECH-09 | game_state | aktualizuj_stan dla sanity rownolegle z hp | {"hp": -5, "sanity": -10} | -5/-10 | hp=95, sanity=90 | - |
| TC-MECH-10 | game_state | dodaj_przedmiot dorzuca do ekwipunku | {"dodaj_przedmiot": "X"} | "X" | ekwipunek zawiera "X" | - |

## Osoba 3 - testy silnika fabuly (TC-ENG-01..10)

| ID | Modul | Opis | Krok | Dane wejsciowe | Oczekiwany wynik | Status |
|---|---|---|---|---|---|---|
| TC-ENG-01 | engine | Wybor bez warunku przechodzi | start->oboz | wybor[1] | obecny_wezel = "oboz" | - |
| TC-ENG-02 | engine | Wybor z warunkiem rzutu kostka - sukces | wymus rzut 20 | rzut 20, prog 12 | przejscie zachodzi | - |
| TC-ENG-03 | engine | Wybor z warunkiem rzutu kostka - porazka | wymus rzut 1 | rzut 1, prog 12 | przejscie do `cel_porazka` | - |
| TC-ENG-04 | engine | Warunek min_hp niespelniony | hp=20, wymagane 30 | min_hp 30 | brak przejscia | - |
| TC-ENG-05 | engine | Warunek min_sanity niespelniony | sanity=20, wymagane 40 | min_sanity 40 | brak przejscia | - |
| TC-ENG-06 | engine | Warunek wymagany_przedmiot brak | ekwipunek pusty | "latarnia" | brak przejscia | - |
| TC-ENG-07 | engine | Warunek wymagany_przedmiot OK | ekwipunek ["latarnia"] | "latarnia" | przejscie zachodzi | - |
| TC-ENG-08 | engine | Efekt wezla aplikuje sie po wejsciu | wejdz do "jaskinia" | sanity 100 | sanity 90 po wejsciu | - |
| TC-ENG-09 | engine | Wezel z `zakonczone: true` zatrzymuje gre | wejdz do "final_dobry" | flaga | czy_koniec() = True | - |
| TC-ENG-10 | engine | Lista odwiedzone nie ma duplikatow | wroc do startu 2x | ten sam id | tylko 1 wpis | - |

## Osoba 4 - testy GUI (TC-GUI-01..10)

| ID | Modul | Opis | Krok | Dane wejsciowe | Oczekiwany wynik | Status |
|---|---|---|---|---|---|---|
| TC-GUI-01 | gui | Otwarcie okna menu | uruchom `python main.py` | - | widac "CIEN NAD ARKHAM" i "START" | - |
| TC-GUI-02 | gui | Klikniecie START | start | klikniecie | przelacza na ekran gry, widac tekst startowy | - |
| TC-GUI-03 | gui | Wyswietlanie HP/Sanity | po starcie | - | "HP: 100", "Sanity: 100" | - |
| TC-GUI-04 | gui | Wyswietlanie ekwipunku | start (pusty) | - | "Ekwipunek: (pusty)" | - |
| TC-GUI-05 | gui | Aktualizacja po zebraniu przedmiotu | start->oboz | klik "Przeszukaj oboz" | "Ekwipunek: latarnia" | - |
| TC-GUI-06 | gui | Aktualizacja HP po stracie | wejdz do `chata_porazka` | -10 hp | etykieta hp = "HP: 90" | - |
| TC-GUI-07 | gui | Ekran zwyciestwa | dojdz do final_dobry | - | naglowek "ZWYCIESTWO" | - |
| TC-GUI-08 | gui | Ekran przegranej | doprowadz hp do 0 | - | naglowek "KONIEC GRY" | - |
| TC-GUI-09 | gui | Powrot do menu z gry | klik "Menu" | - | wraca do menu glownego | - |
| TC-GUI-10 | gui | Restart gry | klik "Zagraj ponownie" | - | stan resetuje sie do startowego | - |

## Osoba 5 - testy integracyjne (TC-INT-01..10)

| ID | Modul | Opis | Krok | Dane wejsciowe | Oczekiwany wynik | Status |
|---|---|---|---|---|---|---|
| TC-INT-01 | calosc | Happy path z mapa | oboz->przed_chata->chata->rozstaje->mapa | - | final_dobry, ekwipunek [latarnia, mapa] | - |
| TC-INT-02 | calosc | Happy path z Sanity | jaskinia->glebiny->walka (sukces)->rozstaje->zapytaj | sanity > 40 | final_dobry | - |
| TC-INT-03 | calosc | Zla sciezka przez atak na starca | start->...->rozstaje->zaatakuj | - | final_zly | - |
| TC-INT-04 | calosc | Zla sciezka przez szept | rozstaje z sanity < 40 | - | szept->final_zly | - |
| TC-INT-05 | calosc | Niemozna wejsc do chaty bez latarni | start->jaskinia->...->przed_chata bez latarni | brak latarni | przycisk niedziala | - |
| TC-INT-06 | calosc | Wszystkie wezle osiagalne | sprawdz po kolei | - | kazdy z 12 wezlow ma sciezke | - |
| TC-INT-07 | calosc | Restart po koncu gry | klik "Zagraj ponownie" | - | nowy stan, gra od startu | - |
| TC-INT-08 | calosc | Wyjscie z menu | klik "WYJSCIE" | - | okno sie zamyka | - |
| TC-INT-09 | calosc | Smierc przez 0 HP | wymusic spadek HP do 0 | - | natychmiastowy ekran konca | - |
| TC-INT-10 | calosc | Smierc przez 0 Sanity | wymusic spadek Sanity do 0 | - | natychmiastowy ekran konca | - |
