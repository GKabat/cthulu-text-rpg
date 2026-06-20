# Wymagania systemowe - Cień nad Arkham

## Wymagania funkcjonalne

| ID | Wymaganie |
|---|---|
| WF-01 | System weryfikuje obecność wymaganych plików danych przed uruchomieniem i kończy działanie z czytelnym komunikatem, jeśli któregoś brakuje. |
| WF-02 | System udostępnia menu z opcjami Nowa gra, Kontynuuj i Wyjście. Opcja Kontynuuj jest nieaktywna, gdy plik zapisu nie istnieje. |
| WF-03 | System wyświetla treść aktualnej sceny, statystyki postaci (HP, Sanity, ekwipunek) oraz dostępne wybory z opisem efektu każdego z nich. |
| WF-04 | System rozstrzyga wybory warunkowe rzutem kością k20, porównuje wynik z progiem i informuje gracza o rezultacie. |
| WF-05 | System aktualizuje HP i Sanity postaci po każdym wyborze; obie wartości są ograniczone do zakresu 0–100. |
| WF-06 | System zapisuje i odczytuje pełny stan rozgrywki (aktualna scena, HP, Sanity, ekwipunek) z pojedynczego pliku zapisu. |
| WF-07 | System wykrywa warunki zakończenia gry i wyświetla ekran końcowy właściwy dla danego zakończenia. |

## Wymagania niefunkcjonalne

| ID | Wymaganie |
|---|---|
| WNF-01 | System działa na Pythonie 3.x bez zewnętrznych zależności, zarówno na Linux, jak i Windows. |
| WNF-02 | Czas uruchomienia aplikacji do momentu wyświetlenia menu nie przekracza 3 sekund na typowym komputerze biurowym. |
| WNF-03 | Treść gry (fabuła, konfiguracja) jest przechowywana w plikach JSON oddzielonych od kodu — modyfikacja fabuły nie wymaga zmiany kodu źródłowego. |
| WNF-04 | Kod źródłowy jest podzielony na moduły z wyraźnie określonymi odpowiedzialnościami, co umożliwia niezależną pracę nad każdym z nich. |
| WNF-05 | Aplikacja nie kończy działania nieobsłużonym wyjątkiem podczas normalnego użytkowania. |
