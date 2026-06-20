# Osoba D - Stan gry oraz dane (fabuła i konfiguracja)

Ten dokument opisuje **bardzo szczegółowo** część, za którą odpowiada Osoba D.
Po przeczytaniu powinieneś umieć omówić każdą swoją funkcję linijka po linijce,
wytłumaczyć format danych oraz uzasadnić podjęte decyzje.

## 1. Co należy do Ciebie

- cały `game_state.py` - tworzenie i zmienianie stanu bohatera,
- `app/data/config.json` - ustawienia startowe,
- `app/data/story.json` - cała fabuła (wszystkie sceny i wybory).

W skrócie: Twoja część to **dane i ich obsługa** - z jednej strony „kartka" ze
statystykami bohatera, z drugiej cały scenariusz gry. Nie rysujesz ani nie
przeliczasz przejść, ale to Twoje struktury danych napędzają cały program.

## 2. Jak Twoja część łączy się z resztą

- `inicjalizuj_stan` jest wołane przez `zaladuj_dane` (Osoba A) na początku gry.
- `aktualizuj_stan` jest wołane przez `wykonaj_wybor` (Osoba C) przy każdym
  wejściu do sceny.
- `app/data/story.json` czyta `wczytaj_fabule` (Osoba C); `app/data/config.json` czyta
  `zaladuj_dane` (Osoba A).
- Podpowiedzi (Osoba B) opisują efekty, które Ty zdefiniowałeś w `story.json`.

---

## 3. `game_state.py` - stan bohatera

### `inicjalizuj_stan(config)`
```python
def inicjalizuj_stan(config):
    postac = config["postac"]
    stan = {
        "obecny_wezel": config["start_wezel"],
        "hp": postac["hp"],
        "sanity": postac["sanity"],
        "nazwa_postaci": postac["nazwa"],
        "odwiedzone": [],
        "ekwipunek": [],
        "ostatni_rzut": None,
    }
    return stan
```
Tworzy **nowy stan gry** na podstawie ustawień. Pola:
- `obecny_wezel` - nazwa sceny startowej (z `config["start_wezel"]`, czyli „intro"),
- `hp`, `sanity` - punkty startowe (z `config`, czyli po 100),
- `nazwa_postaci` - imię bohatera,
- `odwiedzone` - pusta lista odwiedzonych scen,
- `ekwipunek` - pusta lista przedmiotów,
- `ostatni_rzut` - `None`, bo na starcie nie było żadnego rzutu.

**Decyzja:** stan to **słownik**, a nie obiekt klasy. To najprostsza struktura
„klucz → wartość" i w zupełności wystarcza. Każdy moduł może go odczytać i
zmienić, a zapis do pliku to jeden `json.dump`.

### `aktualizuj_stan(stan, efekt)`
```python
def aktualizuj_stan(stan, efekt):
    if efekt is None:
        return stan
    if "hp" in efekt:
        stan["hp"] = stan["hp"] + efekt["hp"]
        if stan["hp"] < 0:   stan["hp"] = 0
        if stan["hp"] > 100: stan["hp"] = 100
    if "sanity" in efekt:
        stan["sanity"] = stan["sanity"] + efekt["sanity"]
        if stan["sanity"] < 0:   stan["sanity"] = 0
        if stan["sanity"] > 100: stan["sanity"] = 100
    if "dodaj_przedmiot" in efekt:
        stan["ekwipunek"].append(efekt["dodaj_przedmiot"])
    return stan
```
Nakłada efekt sceny na stan. Trzy możliwe składniki efektu (mogą wystąpić razem):
- `"hp"` - dodaje (lub odejmuje, gdy liczba ujemna) punkty życia,
- `"sanity"` - to samo dla poczytalności,
- `"dodaj_przedmiot"` - dokłada nazwę przedmiotu do ekwipunku.

Jeśli efekt to `None` (scena bez efektu) - nic nie zmieniamy.

**Najważniejsza rzecz - „przycinanie" (clamping):**
```python
if stan["hp"] < 0:   stan["hp"] = 0
if stan["hp"] > 100: stan["hp"] = 100
```
Po każdej zmianie pilnujemy, by wartość została w zakresie **0–100**. Bez tego
HP mogłoby spaść do −50 albo urosnąć do 130 - co nie miałoby sensu. Dwa proste
`if`-y załatwiają sprawę.

**Decyzja:** efekt to słownik z opcjonalnymi kluczami. Sprawdzamy każdy przez
`if "..." in efekt`, więc efekt może zawierać dowolną kombinację (samo HP, samo
Sanity, oba naraz, albo przedmiot). Łatwo to też rozszerzyć o nowe pola.

### `pobierz_stan(stan)`
```python
def pobierz_stan(stan):
    return stan.copy()
```
Zwraca **kopię** stanu. `stan.copy()` tworzy nowy słownik z tymi samymi
wartościami. Dzięki temu, kto dostanie kopię, może ją zmieniać, nie psując
oryginału.

**Uwaga (na obronie):** to tzw. *płytka kopia* - kopiuje wierzchni słownik. Dla
tej gry wystarcza, bo statystyki to liczby. Funkcja jest przygotowana „na zapas",
jako bezpieczny sposób udostępniania stanu na zewnątrz.

---

## 4. `app/data/config.json` - ustawienia startowe

```json
{
    "tytul": "Cień nad Arkham",
    "wersja": "2.0",
    "postac": {
        "nazwa": "Badacz",
        "hp": 100,
        "sanity": 100
    },
    "start_wezel": "intro"
}
```
To „metryczka" gry: tytuł, wersja, dane postaci (imię, startowe HP i Sanity) oraz
nazwa sceny, od której zaczynamy (`start_wezel`).

**Decyzja:** wartości startowe są w pliku, a nie wpisane w kodzie. Żeby zmienić
startowe życie czy scenę początkową, wystarczy edytować `config.json` - bez
ruszania programu.

---

## 5. `app/data/story.json` - fabuła (Twoja największa część)

To cała historia gry zapisana jako **słownik węzłów**. Kluczem jest nazwa sceny,
wartością - jej opis. Przykład jednej sceny:

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

### Pola sceny (węzła)
- `tekst` - opis do przeczytania (druga osoba, np. „Budzisz się...").
- `obrazek` - ścieżka do grafiki sceny (np. `tiles/wood_road.png`).
- `wybory` - lista opcji. Każdy wybór ma:
  - `tekst` - napis na przycisku,
  - `cel` - nazwa sceny, do której prowadzi,
  - `warunek` - `null` (brak) albo słownik z warunkiem:
    `{"rzut_koscia": true, "prog": N}` / `{"min_sanity": N}` / `{"min_hp": N}`,
  - `cel_porazka` (opcjonalnie) - scena, do której idziemy, gdy warunek się nie
    powiedzie.
- `efekt` - co zmienia wejście do sceny: `null` albo np. `{"sanity": -10}`,
  `{"hp": -25}`, `{"dodaj_przedmiot": "kieł wilka"}`.
- `zakonczone` - `true`, jeśli to koniec gry; wtedy dochodzi `zakonczenie` o
  wartości `"dobry"` (ekran ZWYCIESTWO) lub `"zly"` (ekran KONIEC GRY).

### Budowa fabuły (17 scen)
Fabuła ma 17 węzłów. Najważniejsze „rozgałęzienia":
- **start `intro` → `rozdroze`** - rozdroże z trzema drogami (jaskinia, las,
  chata),
- droga **jaskini** prowadzi do utraty Sanity i może skończyć się szaleństwem,
- droga **lasu** prowadzi do wilka (rzut k20) i do drugiego rozdroża ze starcem,
- droga **chaty** (rzut k20) prowadzi do mapy i dobrego zakończenia,
- trzy zakończenia: `final_dobry` (ZWYCIESTWO), `final_szalenstwo` i
  `walka_z_cieniem` (KONIEC GRY).

**Spójność danych - o co trzeba dbać:**
- każdy `cel` i `cel_porazka` musi wskazywać **istniejącą** scenę (inaczej gra
  trafi w pustkę),
- każdy wybór z `rzut_koscia` powinien mieć `prog`,
- każda scena z `zakonczone: true` powinna mieć `zakonczenie`.
To dokładnie sprawdzają Twoje testy danych (D8–D10).

**Decyzja (kluczowa na obronie):** trzymanie fabuły w osobnym pliku JSON oddziela
**treść** od **programu**. Można dopisywać sceny, zmieniać teksty i efekty bez
dotykania kodu Pythona. Programista i scenarzysta mogą pracować niezależnie.

---

## 6. Decyzje projektowe w Twojej części

1. **Stan jako słownik** - najprostsza struktura, łatwa do odczytu, zmiany i
   zapisania (`json.dump`).
2. **Przycinanie 0–100** - statystyki zawsze mają sens.
3. **Efekt jako słownik z opcjonalnymi kluczami** - dowolna kombinacja HP /
   Sanity / przedmiotu; łatwe do rozszerzenia.
4. **Wartości startowe w `config.json`** - zmiana bez ruszania kodu.
5. **Fabuła w `story.json`** - oddzielenie treści od programu.
6. **`cel_porazka` w danych** - rozgałęzienie „sukces / porażka" zapisane w
   danych, nie w kodzie.

## 7. Co możesz powiedzieć na obronie

- **„Czemu stan to słownik, a nie klasa?”** - bo to prosta struktura
  klucz–wartość, w zupełności wystarcza, a w dodatku zapis to jeden `json.dump`.
- **„Jak działa utrata życia?”** - `aktualizuj_stan` dodaje wartość efektu do HP
  i przycina wynik do zakresu 0–100.
- **„Jak zbudowana jest jedna scena?”** - to słownik z tekstem, obrazkiem, listą
  wyborów, efektem i flagą końca.
- **„Po co fabuła w osobnym pliku?”** - żeby zmieniać historię bez ruszania kodu;
  treść jest oddzielona od programu.

## 8. Twoje testy

Twoja sekcja to przypadki **D1–D10** w `TestCases_Cien_nad_Arkham.xlsx` i
`TESTY.md` (inicjalizacja stanu, aktualizacja z przycinaniem 0–100, ekwipunek,
kopia stanu, integralność i spójność `story.json`). Część logiczna jest też
w automatycznym `tests/test_gra.py`.
