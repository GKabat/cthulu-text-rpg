# Rejestr defektów — Cień nad Arkham

Lista defektów wykrytych podczas testów. Każdy wpis ma stałą strukturę: ID,
tytuł, istotność, środowisko, szczegółowe kroki reprodukcji, opis słowny (co się
dzieje), rezultat oczekiwany oraz korelację z przypadkami testowymi.

Defekty oznaczone jako **potwierdzone** zostały realnie odtworzone i kończą się
rzeczywistym wyjątkiem; pozostałe wynikają wprost z budowy kodu.

| ID | Tytuł | Istotność | Powiązane testy | Status |
|---|---|---|---|---|
| DEF-1 | Wczytanie zapisu z nieistniejącą sceną kończy się wyjątkiem | Krytyczny | A10, A9 | Otwarty |
| DEF-2 | Literówka w polu `cel` w fabule wywala interfejs | Wysoki | D9, C6 | Otwarty |
| DEF-3 | Tryb konsolowy silnika nie działa z katalogu projektu | Średni | C4 | Zamknięty |
| DEF-4 | Brak przewijania — długa scena może wyjść poza obszar gry | Średni | B5, B10 | Otwarty |
| DEF-5 | Zmiana rozmiaru okna rozjeżdża układ | Niski | A3, A6, A7 | Otwarty |
| DEF-6 | „Zapisz" nadpisuje istniejący zapis bez ostrzeżenia | Niski | A10 | Otwarty |

---

## DEF-1 — Wczytanie zapisu z nieistniejącą sceną kończy się wyjątkiem

- **ID:** DEF-1
- **Tytuł / nazwa:** Wczytanie zapisu z nieistniejącą sceną kończy się wyjątkiem
- **Istotność (priorytet):** Krytyczny
- **Środowisko / konfiguracja:** Linux (Fedora), Python 3.14, tkinter
- **Potwierdzony:** tak (odtworzony wyjątek)
- **Kroki reprodukcji:**
  1. Uruchom grę i kliknij **NOWA GRA**, przejdź do dowolnej sceny.
  2. Kliknij **Zapisz** (powstanie plik `data/save.json`).
  3. Zamknij grę. Otwórz `save.json` w edytorze tekstu.
  4. Zmień wartość pola `"obecny_wezel"` na nazwę sceny, której nie ma w fabule,
     np. `"scena_ktorej_nie_ma"`, i zapisz plik.
  5. Uruchom grę ponownie i w menu kliknij **KONTYNUUJ**.
- **Co się dzieje (opis słowny):** Po kliknięciu KONTYNUUJ gra wczytuje stan z
  pliku i próbuje narysować scenę o nazwie, której nie ma. Funkcja `pobierz_wezel`
  zwraca `None`, a `odswiez_scene` od razu odwołuje się do `wezel.get("obrazek")`,
  przez co program przerywa działanie z błędem.
- **Rezultat oczekiwany:** Gra obsługuje błędny zapis łagodnie — pokazuje
  komunikat (np. „Plik zapisu jest uszkodzony") i/lub wraca do menu, bez przerwania.
- **Rezultat faktyczny:** Wyjątek `AttributeError: 'NoneType' object has no
  attribute 'get'` w `odswiez_scene`.
- **Korelacja z test case'ami:** problem w obszarze testów **A10** (wczytanie
  zapisu / KONTYNUUJ) oraz **A9**; te testy sprawdzają poprawny zapis, ale nie
  obejmują uszkodzonego pliku.
- **Prawdopodobna przyczyna / naprawa:** `wczytaj_gre` i `odswiez_scene` nie
  sprawdzają, czy `pobierz_wezel` zwrócił `None`. Wystarczy dodać kontrolę i powrót
  do menu z komunikatem.

---

## DEF-2 — Literówka w polu `cel` w fabule wywala interfejs

- **ID:** DEF-2
- **Tytuł / nazwa:** Literówka w polu `cel` w fabule wywala interfejs
- **Istotność (priorytet):** Wysoki
- **Środowisko / konfiguracja:** Linux (Fedora), Python 3.14, tkinter
- **Potwierdzony:** tak (odtworzony wyjątek)
- **Kroki reprodukcji:**
  1. Otwórz `data/story.json`.
  2. W którymkolwiek wyborze zmień pole `"cel"` na nazwę nieistniejącej sceny,
     np. `"literowka_xyz"`, i zapisz plik.
  3. Uruchom grę, przejdź do sceny zawierającej ten wybór.
  4. Kliknij ten wybór.
- **Co się dzieje (opis słowny):** Silnik wykrywa, że scena docelowa nie istnieje,
  i wypisuje w konsoli `[engine] BLAD: brak wezla ...`, ale **mimo to** ustawia
  `obecny_wezel` na tę nieistniejącą nazwę. Następnie `odswiez_scene` próbuje
  narysować scenę `None` i przerywa działanie.
- **Rezultat oczekiwany:** Bezpieczna obsługa — np. pozostanie na bieżącej scenie
  i komunikat, bez przerwania gry.
- **Rezultat faktyczny:** Wyjątek `AttributeError: 'NoneType' object has no
  attribute 'get'`.
- **Korelacja z test case'ami:** powiązany z **D9** (test „brak martwych linków",
  który sprawdza, że każdy `cel` wskazuje istniejącą scenę) oraz **C6**
  (`pobierz_wezel` zwraca `None` dla nieznanej sceny). Defekt jest „uśpiony" —
  w obecnych danych wszystkie cele są poprawne, więc ujawnia się dopiero przy
  błędnych danych.
- **Prawdopodobna przyczyna / naprawa:** brak walidacji w warstwie GUI; dodatkowo
  `wykonaj_wybor` ustawia `obecny_wezel` nawet, gdy nowa scena nie istnieje.

---

## DEF-3 — Tryb konsolowy silnika nie działa z katalogu projektu ✓ Zamknięty

- **ID:** DEF-3
- **Tytuł / nazwa:** Tryb konsolowy silnika nie działa z katalogu projektu
- **Istotność (priorytet):** Średni
- **Środowisko / konfiguracja:** Linux (Fedora), Python 3.14 (konsola)
- **Potwierdzony:** tak (odtworzony wyjątek)
- **Status:** Zamknięty — naprawiony podczas reorganizacji struktury projektu
- **Kroki reprodukcji (historyczne):**
  1. Otwórz terminal w katalogu głównym projektu.
  2. Uruchom polecenie: `python src/engine.py`.
- **Co się działo (opis słowny):** Tryb konsolowy silnika próbował otworzyć plik
  `data/config.json` ścieżką **względną do bieżącego katalogu**, a nie do
  położenia pliku `engine.py`. Dane są w `data/`, więc plik nie zostawał
  znaleziony i program przerywał działanie. Tryb działał tylko, gdy uruchomiono go
  z wnętrza katalogu zawierającego `engine.py`.
- **Rezultat oczekiwany:** Uruchamia się tekstowy (konsolowy) tryb przejścia gry,
  niezależnie od katalogu, z którego polecenie zostało wywołane.
- **Rezultat faktyczny (przed naprawą):** `FileNotFoundError: [Errno 2] No such file or directory:
  'data/config.json'`.
- **Korelacja z test case'ami:** dotyczy sekcji silnika, najbliżej testu **C4**
  (`wczytaj_fabule`); testy C1–C10 importują funkcje silnika i nie uruchamiają
  trybu konsolowego, więc tej ścieżki nie pokrywają.
- **Przyczyna / zastosowana naprawa:** ścieżki w bloku `__main__` w `src/engine.py`
  nie były kotwiczone do `__file__`. Naprawiono przez obliczenie katalogu projektu
  względem położenia pliku: `EDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`.

---

## DEF-4 — Brak przewijania: długa scena może wyjść poza obszar gry

- **ID:** DEF-4
- **Tytuł / nazwa:** Brak przewijania — długa scena może wyjść poza obszar gry
- **Istotność (priorytet):** Średni
- **Środowisko / konfiguracja:** Linux (Fedora), Python 3.14, tkinter; ujawnia się
  najszybciej na małym oknie 592×456 (mniejsze ekrany)
- **Potwierdzony:** obserwacja (wynika z budowy `odswiez_scene`)
- **Kroki reprodukcji:**
  1. Uruchom grę na małym ekranie (okno 592×456) lub zmniejsz rozdzielczość.
  2. Wejdź do sceny z długim tekstem i kilkoma wyborami (np. `rozdroze`).
  3. Zwróć uwagę na dolną krawędź obszaru gry.
- **Co się dzieje (opis słowny):** Treść (tekst, przyciski, grafika kości) jest
  układana kolejno w dół od stałej pozycji startowej. Przy długiej treści ostatnie
  przyciski wypadają poniżej przezroczystego otworu i częściowo chowają się pod
  kamienną ramką. Nie ma paska przewijania, więc część treści bywa nieosiągalna.
- **Rezultat oczekiwany:** Cała treść sceny jest dostępna — np. dzięki przewijaniu
  obszaru treści.
- **Rezultat faktyczny:** Ostatnie elementy mogą być przycięte / zasłonięte ramką.
- **Korelacja z test case'ami:** obszar testów **B5** (liczba i rozmieszczenie
  przycisków) oraz **B10** (rozkład ekranu); testy te sprawdzają liczbę i treść
  elementów, ale nie mieszczenie się w oknie.
- **Prawdopodobna przyczyna / naprawa:** `odswiez_scene` nie obsługuje przewijania
  i zakłada, że treść zmieści się w otworze. Naprawa: skracać sceny albo dodać
  przewijanie obszaru treści.

---

## DEF-5 — Zmiana rozmiaru okna rozjeżdża układ

- **ID:** DEF-5
- **Tytuł / nazwa:** Zmiana rozmiaru okna rozjeżdża układ
- **Istotność (priorytet):** Niski
- **Środowisko / konfiguracja:** Linux (Fedora), Python 3.14, tkinter
- **Potwierdzony:** obserwacja (wynika z budowy `utworz_okno`)
- **Kroki reprodukcji:**
  1. Uruchom grę.
  2. Zmaksymalizuj okno lub rozciągnij je za róg.
- **Co się dzieje (opis słowny):** Rozmiar ramki i współrzędne treści są wyliczane
  jednorazowo przy starcie. Po zmianie rozmiaru okna ramka nie skaluje się, a
  treść zostaje w starych pozycjach — pojawia się pusty obszar i układ przestaje
  pasować.
- **Rezultat oczekiwany:** Układ dopasowuje się do nowego rozmiaru okna albo
  rozmiar jest zablokowany, by uniknąć rozjechania.
- **Rezultat faktyczny:** Pusty obszar po zmianie rozmiaru; ramka i treść nie
  skalują się.
- **Korelacja z test case'ami:** obszar testów **A3** (utworzenie okna) oraz
  **A6/A7** (skalowanie do rozmiaru ekranu); testy sprawdzają rozmiar **startowy**,
  ale nie zachowanie po zmianie rozmiaru w trakcie gry.
- **Prawdopodobna przyczyna / naprawa:** brak reakcji na zdarzenie zmiany rozmiaru.
  Najprościej: `root.resizable(False, False)` albo przeliczanie układu po zdarzeniu
  `<Configure>`.

---

## DEF-6 — „Zapisz" nadpisuje istniejący zapis bez ostrzeżenia

- **ID:** DEF-6
- **Tytuł / nazwa:** „Zapisz" nadpisuje istniejący zapis bez ostrzeżenia
- **Istotność (priorytet):** Niski
- **Środowisko / konfiguracja:** Linux (Fedora), Python 3.14, tkinter
- **Potwierdzony:** obserwacja (wynika z budowy `zapisz_gre`)
- **Kroki reprodukcji:**
  1. Uruchom grę, rozpocznij rozgrywkę i kliknij **Zapisz**.
  2. Zagraj dalej, przejdź do innej sceny.
  3. Kliknij **Zapisz** ponownie.
- **Co się dzieje (opis słowny):** Drugie kliknięcie Zapisz od razu nadpisuje plik
  `save.json` (gra ma jeden slot), bez żadnego pytania. Poprzedni stan jest tracony
  bezpowrotnie.
- **Rezultat oczekiwany:** Ewentualne pytanie o potwierdzenie nadpisania
  poprzedniego zapisu.
- **Rezultat faktyczny:** Cichy nadpis bez ostrzeżenia.
- **Korelacja z test case'ami:** obszar testu **A10** (zapis / wczytanie gry); ten
  sam obszar co DEF-1.
- **Prawdopodobna przyczyna / naprawa:** świadome uproszczenie (jeden slot zapisu).
  Udokumentowane jako ograniczenie; ewentualna naprawa to okno potwierdzenia lub
  kilka slotów zapisu.

---

## Powiązanie z arkuszem testów

Defekty są też ujęte w `TestCases_Cien_nad_Arkham.xlsx` jako przypadki o wyniku
**Negatywnym** (ID `DEF-1`…`DEF-6`, kolumny *Bug ID* i *Kryteria niepowodzenia*),
z odwołaniem do powiązanych testów w opisie niepowodzenia.
