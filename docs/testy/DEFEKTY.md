# Rejestr defektów — Cień nad Arkham

Lista defektów wykrytych podczas testów. Każdy wpis zawiera: ID, tytuł,
istotność, środowisko, kroki reprodukcji, opis problemu, rezultat oczekiwany
i korelację z przypadkami testowymi.

| ID | Tytuł | Istotność | Powiązane testy | Status |
|---|---|---|---|---|
| DEF-1 | Wczytanie zapisu z nieistniejącą sceną kończy się wyjątkiem | Krytyczny | A10, A9 | Otwarty |
| DEF-2 | „Zapisz" nadpisuje istniejący zapis bez ostrzeżenia | Niski | A10 | Otwarty |

---

## DEF-1 — Wczytanie zapisu z nieistniejącą sceną kończy się wyjątkiem

- **ID:** DEF-1
- **Tytuł:** Wczytanie zapisu z nieistniejącą sceną kończy się wyjątkiem
- **Istotność:** Krytyczny
- **Środowisko:** Linux (Fedora), Python 3.14, tkinter
- **Potwierdzony:** tak (odtworzony wyjątek)
- **Kroki reprodukcji:**
  1. Uruchom grę, kliknij **NOWA GRA** i przejdź do dowolnej sceny.
  2. Kliknij **Zapisz** (powstanie `data/save.json`).
  3. Zamknij grę, otwórz `save.json` w edytorze i zmień `"obecny_wezel"` na
     nazwę nieistniejącej sceny, np. `"scena_ktorej_nie_ma"`.
  4. Uruchom grę ponownie i kliknij **KONTYNUUJ**.
- **Co się dzieje:** Gra wczytuje stan z pliku i próbuje narysować scenę, której
  nie ma. `pobierz_wezel` zwraca `None`, po czym `odswiez_scene` wywołuje
  `wezel.get("obrazek")` na `None` i program przerywa działanie.
- **Rezultat oczekiwany:** Gra wyświetla komunikat (np. „Plik zapisu jest
  uszkodzony") i wraca do menu bez wyjątku.
- **Rezultat faktyczny:** `AttributeError: 'NoneType' object has no attribute 'get'`
  w `odswiez_scene`.
- **Korelacja z testami:** **A10** (wczytanie zapisu / KONTYNUUJ) i **A9**;
  testy sprawdzają poprawny zapis, ale nie obejmują uszkodzonego pliku.
- **Naprawa:** dodać w `wczytaj_gre` / `odswiez_scene` sprawdzenie, czy
  `pobierz_wezel` zwróciło `None`, i powrót do menu z komunikatem.

---

## DEF-2 — „Zapisz" nadpisuje istniejący zapis bez ostrzeżenia

- **ID:** DEF-2
- **Tytuł:** „Zapisz" nadpisuje istniejący zapis bez ostrzeżenia
- **Istotność:** Niski
- **Środowisko:** Linux (Fedora), Python 3.14, tkinter
- **Potwierdzony:** obserwacja (wynika z budowy `zapisz_gre`)
- **Kroki reprodukcji:**
  1. Uruchom grę, zagraj chwilę i kliknij **Zapisz**.
  2. Zagraj dalej, przejdź do innej sceny.
  3. Kliknij **Zapisz** ponownie.
- **Co się dzieje:** Drugi zapis od razu nadpisuje `data/save.json` bez żadnego
  pytania. Poprzedni stan jest tracony bezpowrotnie.
- **Rezultat oczekiwany:** Potwierdzenie przed nadpisaniem istniejącego zapisu.
- **Rezultat faktyczny:** Cichy nadpis bez ostrzeżenia.
- **Korelacja z testami:** **A10** (zapis / wczytanie gry).
- **Naprawa:** świadome uproszczenie (jeden slot). Ewentualnie: okno
  potwierdzenia lub kilka slotów zapisu.

---

## Powiązanie z arkuszem testów

Defekty są ujęte w `TestCases_Cien_nad_Arkham.xlsx` jako przypadki o wyniku
**Negatywnym** (kolumny *Bug ID* i *Kryteria niepowodzenia*),
z odwołaniem do powiązanych testów.
