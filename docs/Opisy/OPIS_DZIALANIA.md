# Cień nad Arkham - jak działa program (od ogółu do szczegółu)

Ten dokument tłumaczy, jak zbudowana jest gra i dlaczego podjęto takie, a nie
inne decyzje. Jest napisany tak, aby po przeczytaniu można było **własnymi
słowami opowiedzieć, co dzieje się w kodzie** - nawet bez dużego doświadczenia
w programowaniu. Czytaj od góry do dołu: zaczynamy od ogólnego obrazu, a potem
schodzimy do szczegółów.

---

## 1. Co to za program (w dwóch zdaniach)

To **tekstowa gra paragrafowa** w klimacie grozy (Lovecraft/Poe). Gracz czyta
opis sceny, wybiera jedną z opcji, a gra przechodzi do kolejnej sceny - czasem
o wyniku decyduje **rzut kością**. Bohater ma dwa paski: **HP** (życie) i
**Sanity** (poczytalność). Celem jest przetrwać noc i dotrzeć do latarni morskiej.

Najprościej: to taka interaktywna książka, w której to ty decydujesz, co dalej,
a program pilnuje zasad i liczy punkty.

---

## 2. Z czego składa się projekt (mapa plików)

Program jest podzielony na małe pliki, z których każdy odpowiada za jedną rzecz.
Dzięki temu łatwiej się w tym połapać - każdy fragment ma swoje miejsce.

| Plik | Za co odpowiada | Porównanie |
|---|---|---|
| `main.py` | uruchamia grę, sprawdza, czy są potrzebne pliki | włącznik / stacyjka |
| `gui.py` | rysuje okno i wszystko, co widać; obsługuje kliknięcia | scena i to, co widzi gracz |
| `engine.py` | „silnik" - pilnuje, w której scenie jesteśmy i jak przejść dalej | reżyser sztuki |
| `game_state.py` | przechowuje i zmienia punkty bohatera (HP, Sanity, ekwipunek) | kartka z aktualnymi statystykami |
| `mechanics.py` | rzut kością i sprawdzenie, czy się udało | kostka do gry |
| `app/data/story.json` | cała fabuła: wszystkie sceny i wybory | scenariusz |
| `app/data/config.json` | ustawienia startowe (tytuł, startowe HP/Sanity) | metryczka gry |
| `app/tiles/` | grafiki (ramka okna, kość, obrazki scen) | dekoracje |

**Dlaczego tyle plików, a nie jeden duży?** Bo gdy każdy plik robi jedną rzecz,
łatwiej znaleźć błąd i łatwiej podzielić pracę w zespole. Jeśli coś jest nie tak
z liczeniem życia, wiadomo, że szukamy w `game_state.py`, a nie w całości.

---

## 3. Trzy pojęcia, które trzeba zrozumieć

Cała gra kręci się wokół trzech rzeczy. Jak je zrozumiesz, reszta jest prosta.

**Fabuła** - to cała historia wczytana z pliku `story.json`. W kodzie jest to
**słownik** (po angielsku *dictionary*): zbiór par „klucz → wartość". Kluczem
jest nazwa sceny (np. `rozdroze`), a wartością - opis tej sceny.

**Węzeł (scena)** - pojedynczy element fabuły, czyli jedna „strona" gry. Każdy
węzeł ma: tekst do przeczytania, obrazek, listę wyborów oraz ewentualny
**efekt** (np. utrata 10 punktów Sanity). Słowo „węzeł" pochodzi stąd, że sceny
łączą się ze sobą jak punkty na mapie połączone ścieżkami.

**Stan gry** - to „kartka", na której zapisane jest wszystko, co dotyczy
bohatera **w danej chwili**: w której scenie jest, ile ma HP i Sanity, co ma
w ekwipunku. W kodzie stan to też słownik.

Do tego dochodzi **k20** - kość dwudziestościenna (jak w grach RPG). Losuje
liczbę od 1 do 20; im wyższa, tym lepiej.

---

## 4. Jak gra działa krok po kroku (cykl gry)

Najważniejsza rzecz: gra to **pętla**, która powtarza się w kółko aż do końca.

```
   uruchomienie (main.py)
        │
        ▼
   zbudowanie okna + menu (gui.py)
        │   klikasz NOWA GRA
        ▼
   wczytanie danych → stan startowy (HP 100, Sanity 100, scena "intro")
        │
        ▼
 ┌───────────────────────────────────────────┐
 │  odswiez_scene(): narysuj aktualną scenę   │ ◄───┐
 │  (tekst, obrazek, statystyki, przyciski)   │     │
 └───────────────────────────────────────────┘     │
        │   gracz klika wybór                       │
        ▼                                           │
   obsluz_wybor() → engine.wykonaj_wybor():         │
   • sprawdź warunek (czasem rzut kością)           │
   • przejdź do nowej sceny                         │
   • nałóż efekt nowej sceny (zmień HP/Sanity)      │
        │                                           │
        └───────────────────────────────────────────┘
        │   gdy scena jest końcowa albo HP/Sanity = 0
        ▼
   ekran końcowy (ZWYCIESTWO albo KONIEC GRY)
```

Słownie: program rysuje scenę i czeka. Gdy klikniesz wybór, silnik przelicza, co
ma się stać, zmienia stan, ustawia nową scenę - i znowu ją rysuje. I tak w kółko,
aż dojdziesz do zakończenia albo bohater straci wszystkie punkty.

**Ważny szczegół:** efekt sceny (np. „−10 Sanity") nakłada się **w chwili
wejścia** do tej sceny, a nie w trakcie jej wyświetlania. Czyli najpierw silnik
przenosi cię do nowej sceny i odejmuje punkty, a dopiero potem okno ją rysuje.

---

## 5. Każdy plik szczegółowo

Teraz po kolei, od najprostszych plików do najbardziej rozbudowanego.

### 5.1. `mechanics.py` - kostka

Najmniejszy plik. Dwie funkcje:

- `rzut_koscia(zakres=20)` - losuje liczbę od 1 do 20 (używa gotowego
  `random.randint`).
- `sprawdz_rzut(wynik, prog)` - zwraca `True`, jeśli `wynik >= prog`, czyli gdy
  rzut był wystarczająco wysoki. Im wyższy próg, tym trudniejsza próba.

**Dlaczego osobny plik na dwie funkcje?** Bo „losowanie" to jedna, wyraźnie
oddzielona część zasad. Gdybyśmy chcieli kiedyś dodać inne kości, wiemy gdzie.

### 5.2. `game_state.py` - punkty bohatera

Trzy funkcje pracujące na słowniku ze stanem:

- `inicjalizuj_stan(config)` - tworzy nowy stan na początku gry: ustawia HP i
  Sanity z pliku konfiguracyjnego, scenę startową, pusty ekwipunek.
- `aktualizuj_stan(stan, efekt)` - nakłada efekt sceny: dodaje lub odejmuje HP /
  Sanity, ewentualnie dokłada przedmiot do ekwipunku.
- `pobierz_stan(stan)` - zwraca kopię stanu.

**Najważniejsza decyzja tutaj - „przycinanie" (clamping).** Po każdej zmianie
HP i Sanity są pilnowane, żeby nie wyszły poza zakres **0–100**:

```python
stan["hp"] = stan["hp"] + efekt["hp"]
if stan["hp"] < 0:
    stan["hp"] = 0
if stan["hp"] > 100:
    stan["hp"] = 100
```

Dzięki temu życie nie spadnie poniżej zera ani nie urośnie powyżej 100 -
statystyki zawsze mają sens.

### 5.3. `engine.py` - silnik gry

To „mózg" zasad. Najważniejsze funkcje:

- `wczytaj_fabule(sciezka)` - otwiera plik `story.json` i zamienia go na słownik
  węzłów.
- `pobierz_wezel(fabula, id_wezla)` - zwraca scenę o podanej nazwie. Jeśli takiej
  nazwy nie ma - zwraca `None` i wypisuje komunikat o błędzie (zamiast wywalić
  całą grę).
- `sprawdz_warunek(warunek, stan)` - sprawdza, czy gracz może skorzystać z danego
  wyboru. Są trzy rodzaje warunków:
  - **rzut kością** (`rzut_koscia` + `prog`) - losuje k20 i porównuje z progiem;
    wynik zapisuje do stanu, żeby okno mogło go pokazać,
  - **minimum Sanity** (`min_sanity`) - wybór dostępny, gdy Sanity ≥ podana liczba,
  - **minimum HP** (`min_hp`) - analogicznie dla życia.
  Gdy warunek to `None` (brak), wybór po prostu zawsze prowadzi dalej.
- `wykonaj_wybor(fabula, wybor, stan)` - to serce przejścia między scenami:
  1. sprawdza warunek,
  2. jeśli warunek **niespełniony** i wybór ma zapasowy cel `cel_porazka` -
     idzie tam (np. nieudane wyważenie drzwi prowadzi do sceny z obrażeniami),
  3. jeśli warunek **spełniony** - przechodzi do głównego celu `cel`,
  4. po wejściu do nowej sceny nakłada jej efekt na stan.
- `czy_koniec(wezel)` - mówi, czy scena jest oznaczona jako koniec gry.

**Decyzja: rozdzielenie „warunku" i „efektu".** Rzut kością sam w sobie **nie
zmienia** punktów - on tylko decyduje, do której sceny pójdziemy. Dopiero scena,
do której trafimy, ma swój efekt. To upraszcza zasady: jedno miejsce decyduje
„dokąd", drugie „co się zmienia".

`engine.py` ma też na końcu **tryb konsolowy** (uruchamiany przez
`python engine.py`), który pozwala przejść grę w samym tekście, bez okna.
Służył do szybkiego sprawdzania logiki w trakcie pisania.

### 5.4. `gui.py` - okno i wszystko, co widać

Największy plik, bo interfejs zawsze ma najwięcej szczegółów. Używa biblioteki
**tkinter** (wbudowanej w Pythona). Najważniejsze pomysły:

**Wszystko rysujemy na jednym płótnie (`Canvas`).** Canvas to taki obszar, na
którym można kłaść teksty, obrazki i przyciski w dowolnym miejscu (podając
współrzędne). Tło całego płótna jest brązowe.

**Ramka leży na wierzchu.** Grafika ramki (`app/tiles/frame.png`) ma **przezroczysty
środek** - przez tę „dziurę" widać brązowe tło, a kamienne brzegi zasłaniają
wszystko poza środkiem. Treść gry (tekst, przyciski) trzymamy dokładnie w tym
przezroczystym otworze.

**Otwór liczony w ułamkach.** Położenie otworu zapisaliśmy jako ułamki rozmiaru
ramki (np. lewy brzeg to ok. 0,139 szerokości). Dzięki temu, gdy na małym
ekranie zmniejszymy okno o połowę, otwór sam się przeliczy i wszystko nadal
pasuje.

Najważniejsze funkcje:

- `utworz_okno()` - buduje okno: wczytuje ramkę i grafikę kości, dobiera rozmiar
  okna do ekranu (duży 1184×912 lub mały 592×456), tworzy Canvas, pokazuje menu.
- `pokaz_menu()` - rysuje menu główne: **NOWA GRA**, **KONTYNUUJ** (aktywne tylko
  gdy istnieje zapis) i **WYJSCIE**.
- `nowa_gra()` - wczytuje dane i rysuje pierwszą scenę.
- `odswiez_scene()` - najważniejsza funkcja widoku. Czyści ekran i rysuje od nowa:
  statystyki (HP, Sanity, ekwipunek), obrazek sceny, tekst, a pod nim przyciski
  wyborów. Jeśli właśnie był rzut kością - pokazuje pod przyciskami grafikę kości
  i wynik.
- `obsluz_wybor(wybor)` - wywoływana po kliknięciu przycisku: prosi silnik o
  wykonanie wyboru, a potem znów odświeża scenę.
- `ekran_koncowy(typ)` - pokazuje napis **ZWYCIESTWO** albo **KONIEC GRY** oraz
  przyciski „Zagraj ponownie" i „Wróć do menu".

**Podpowiedzi na przyciskach.** Pod tekstem każdego wyboru pojawia się druga
linijka z informacją, co dany wybór robi (np. „( Sanity -10 )" albo
„rzut k20 >= 12 | sukces: ... | porażka: HP -10"). Te podpowiedzi nie są wpisane
ręcznie - funkcje `opis_efektu`, `opis_celu` i `podpowiedz_efektu` **tworzą je
automatycznie** na podstawie danych sceny. Dzięki temu, gdy zmienimy fabułę,
podpowiedzi same się zaktualizują.

**Zapis i wczytanie gry.** Przyciski „Zapisz" / „Wczytaj" w grze oraz
„KONTYNUUJ" w menu. Zapis to jeden plik `app/data/save.json`. Ponieważ stan gry to
zwykły słownik, zapis sprowadza się do jednej operacji `json.dump`, a wczytanie
do `json.load`.

### 5.5. `main.py` - uruchamianie

Krótki plik, od którego wszystko się zaczyna:

- `sprawdz_pliki()` - sprawdza, czy istnieją pliki z danymi. Jeśli ich brakuje,
  wypisuje komunikat i kończy program (lepiej zatrzymać się od razu niż w połowie
  gry).
- `uruchom()` - woła sprawdzenie plików, a potem buduje i pokazuje okno.

---

## 6. Format danych - jak wygląda jedna scena

Cała fabuła siedzi w `story.json`. Pojedyncza scena (węzeł) wygląda tak:

```json
"rozdroze": {
  "tekst": "Ścieżka rozdziela się na trzy...",
  "obrazek": "tiles/wood_road.png",
  "wybory": [
    {"tekst": "Zejść do jaskini.", "cel": "jaskinia", "warunek": null},
    {"tekst": "Pójść leśnym duktem.", "cel": "polana", "warunek": null},
    {"tekst": "Naprzeć na drzwi.", "cel": "chata",
     "warunek": {"rzut_koscia": true, "prog": 12}, "cel_porazka": "chata_porazka"}
  ],
  "efekt": null,
  "zakonczone": false
}
```

Co znaczą pola:
- `tekst` - opis sceny do przeczytania,
- `obrazek` - ścieżka do grafiki,
- `wybory` - lista opcji; każda ma swój `tekst`, `cel` (dokąd prowadzi),
  opcjonalny `warunek` i opcjonalny `cel_porazka` (dokąd iść przy nieudanym
  warunku),
- `efekt` - co zmienia wejście do sceny (np. `{"hp": -10}`), albo `null`,
- `zakonczone` - czy to koniec gry; jeśli tak, dochodzi `zakonczenie` o wartości
  `"dobry"` (ZWYCIESTWO) lub `"zly"` (KONIEC GRY).

**Dlaczego fabuła jest w osobnym pliku, a nie w kodzie?** Bo dzięki temu można
zmieniać, dopisywać i poprawiać historię **bez dotykania kodu**. Scenarzysta
edytuje `story.json`, a programista nie musi nic robić.

---

## 7. Decyzje projektowe - dlaczego tak, a nie inaczej

To jest sedno: nie chodzi tylko o to, *co* robi kod, ale *dlaczego* robi to
w ten sposób. Oto najważniejsze wybory i ich uzasadnienia.

1. **Stan gry w słowniku, a nie w klasie.** Słownik to najprostsza struktura
   „klucz → wartość". Do przechowania HP, Sanity i bieżącej sceny w zupełności
   wystarcza. Klasa wymagałaby pisania konstruktora i metod - to byłoby
   niepotrzebne komplikowanie tak prostej rzeczy.

2. **Fabuła w pliku JSON, nie w kodzie.** Oddzielamy treść od programu. Historię
   można rozwijać bez znajomości Pythona, a sam kod pozostaje krótki.

3. **Biblioteka tkinter, nie pygame/PyQt.** `tkinter` jest **wbudowany** w
   Pythona - nie trzeba nic instalować. Inne biblioteki trzeba by doinstalować,
   co utrudnia oddanie i uruchomienie projektu na innym komputerze.

4. **Bez biblioteki Pillow.** Tkinter od nowszych wersji Pythona sam wyświetla
   pliki PNG. Skoro umie to „z pudełka", nie dokładamy kolejnej zależności.

5. **Ramka na wierzchu Canvasa.** Brązowe tło wypełnia całe okno, a ramka z
   przezroczystym środkiem leży na nim. Dzięki temu nic nie „przebija" zza ramki
   i całość wygląda jak spójny obrazek, a nie jak panel doklejony na siłę.

6. **Otwór ramki liczony ułamkami.** Pozwala zmniejszyć okno na małym ekranie
   bez psucia układu - wszystko skaluje się proporcjonalnie.

7. **Podpowiedzi generowane automatycznie.** Zamiast wpisywać przy każdym wyborze
   ręcznie „to odejmuje 10 Sanity", program odczytuje efekt z danych i sam
   tworzy opis. Mniej pracy i brak ryzyka, że podpowiedź rozjedzie się z fabułą.

8. **Zapis przez `json.dump`.** Skoro stan to słownik z prostych wartości, zapis
   i odczyt to dosłownie jedna linijka - żadnej dodatkowej biblioteki.

9. **Proste funkcje zamiast zaawansowanych technik.** W całym projekcie
   świadomie nie używamy klas dziedziczonych, dekoratorów, programowania
   asynchronicznego itp. Gra jest mała i niczego takiego nie potrzebuje. Zasada:
   **najprostsze rozwiązanie, które działa.**

---

## 8. Jak opowiedzieć o tym w minutę

Gdyby ktoś zapytał „o co chodzi w tym programie?", można odpowiedzieć tak:

> To tekstowa gra paragrafowa. Fabuła siedzi w pliku JSON jako zbiór scen -
> każda ma tekst, wybory i efekt. Program trzyma stan bohatera (HP, Sanity,
> położenie) w słowniku. Gdy gracz klika wybór, silnik sprawdza warunek (czasem
> rzuca kością k20), przechodzi do nowej sceny i nakłada jej efekt na stan.
> Okno (zrobione na tkinter) po każdej zmianie rysuje scenę od nowa. Gra kończy
> się, gdy dojdziemy do sceny końcowej albo gdy HP lub Sanity spadnie do zera.
> Trzymaliśmy się prostych rozwiązań, bo gra jest mała i nie wymaga niczego
> bardziej skomplikowanego.

---

## 9. Słowniczek pojęć

- **Słownik (dictionary)** - struktura „klucz → wartość", np. `{"hp": 100}`.
- **JSON** - tekstowy format zapisu danych; wygląda jak słowniki i listy.
  Używamy go na fabułę, ustawienia i zapis gry.
- **Węzeł / scena** - jedna „strona" gry: tekst, obrazek, wybory, efekt.
- **Stan gry** - bieżące dane bohatera (HP, Sanity, scena, ekwipunek).
- **Efekt** - zmiana, jaką wprowadza wejście do sceny (np. `−10 Sanity`).
- **Warunek** - co musi być spełnione, by skorzystać z wyboru (rzut kością albo
  minimum HP/Sanity).
- **k20** - kość dwudziestościenna; losuje liczbę 1–20.
- **Przycięcie (clamping)** - pilnowanie, by wartość nie wyszła poza zakres
  (tu: HP i Sanity zawsze 0–100).
- **tkinter** - wbudowana w Pythona biblioteka do okien i przycisków.
- **Canvas (płótno)** - obszar okna, na którym kładziemy teksty, obrazki i
  przyciski we wskazanych miejscach.
- **Widget** - element interfejsu, np. przycisk czy etykieta tekstowa.
