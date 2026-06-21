# Stan gry i dane (`game_state.py` + `app/data/`)

## 1. Zakres

- cały `game_state.py` - tworzenie i zmienianie stanu bohatera,
- `app/data/config.json` - ustawienia startowe,
- `app/data/story.json` - cała fabuła (17 scen i wybory).

## 2. Zależności z innymi modułami

- `inicjalizuj_stan` wołane przez `zaladuj_dane` (gui.py) na początku gry.
- `aktualizuj_stan` wołane przez `wykonaj_wybor` (engine.py) przy każdym wejściu do sceny.
- `app/data/story.json` czyta `wczytaj_fabule` (engine.py); `app/data/config.json` czyta
  `zaladuj_dane` (gui.py).
- Podpowiedzi w GUI opisują efekty zdefiniowane w `story.json`.

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
Tworzy **nowy stan gry** na podstawie ustawień z `config.json`. Pola:
- `obecny_wezel` - scena startowa (z `config["start_wezel"]`, czyli „intro"),
- `hp`, `sanity` - punkty startowe (100),
- `odwiedzone` - pusta lista odwiedzonych scen,
- `ekwipunek` - pusta lista przedmiotów,
- `ostatni_rzut` - `None`, bo na starcie nie było rzutu.

Stan to **słownik**, a nie obiekt klasy. Prosta struktura klucz–wartość
w zupełności wystarcza, a zapis do pliku to jeden `json.dump`.

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
Nakłada efekt sceny na stan. Trzy możliwe składniki (mogą wystąpić razem):
- `"hp"` - dodaje / odejmuje punkty życia,
- `"sanity"` - to samo dla poczytalności,
- `"dodaj_przedmiot"` - dokłada przedmiot do ekwipunku.

**Przycinanie (clamping):**
```python
if stan["hp"] < 0:   stan["hp"] = 0
if stan["hp"] > 100: stan["hp"] = 100
```
Po każdej zmianie pilnujemy zakresu 0–100. Dwa proste `if`-y zamiast
bardziej skomplikowanego kodu.

Efekt to słownik z opcjonalnymi kluczami - sprawdzamy każdy przez `if "..." in efekt`,
więc efekt może zawierać dowolną kombinację. Łatwo też rozszerzyć o nowe pola.

### `pobierz_stan(stan)`
```python
def pobierz_stan(stan):
    return stan.copy()
```
Zwraca **płytką kopię** stanu. Zmiana kopii nie psuje oryginału. Dla tej gry
płytka kopia wystarcza (statystyki to liczby). Przygotowane jako bezpieczny
sposób udostępniania stanu na zewnątrz.

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
Tytuł, wersja, dane postaci (imię, startowe HP i Sanity) oraz scena startowa.
Wartości startowe w pliku, a nie w kodzie - żeby zmienić startowe życie lub scenę
początkową, wystarczy edytować `config.json` bez ruszania programu.

---

## 5. `app/data/story.json` - fabuła

Cała historia gry jako **słownik węzłów**. Kluczem jest nazwa sceny, wartością
jej opis. Przykład jednej sceny:

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
- `tekst` - opis sceny (druga osoba, np. „Budzisz się...").
- `obrazek` - ścieżka do grafiki (np. `tiles/wood_road.png`).
- `wybory` - lista opcji. Każdy wybór ma:
  - `tekst` - napis na przycisku,
  - `cel` - nazwa sceny, do której prowadzi,
  - `warunek` - `null` albo słownik: `{"rzut_koscia": true, "prog": N}` /
    `{"min_sanity": N}` / `{"min_hp": N}`,
  - `cel_porazka` (opcjonalnie) - scena przy niespełnionym warunku.
- `efekt` - co zmienia wejście do sceny: `null` albo `{"sanity": -10}`,
  `{"hp": -25}`, `{"dodaj_przedmiot": "kieł wilka"}`.
- `zakonczone` - `true` gdy koniec gry; dochodzi wtedy `zakonczenie`: `"dobry"`
  (ZWYCIESTWO) lub `"zly"` (KONIEC GRY).

### Budowa fabuły (17 scen)
- **`intro` → `rozdroze`** - trzy drogi: jaskinia, las, chata,
- droga **jaskini** - utrata Sanity, możliwe szaleństwo,
- droga **lasu** - wilk (rzut k20) i drugie rozdroże ze starcem,
- droga **chaty** - rzut k20, mapa i dobre zakończenie,
- trzy zakończenia: `final_dobry` (ZWYCIESTWO), `final_szalenstwo`, `walka_z_cieniem` (KONIEC GRY).

### Co musi być spójne w danych
- każdy `cel` i `cel_porazka` musi wskazywać **istniejącą** scenę,
- każdy wybór z `rzut_koscia` powinien mieć `prog`,
- każda scena z `zakonczone: true` powinna mieć `zakonczenie`.

Fabuła w osobnym pliku JSON oddziela **treść** od **programu** - można dopisywać
sceny i zmieniać teksty bez dotykania kodu.

---

## 6. Decyzje projektowe

1. **Stan jako słownik** - prosta struktura, łatwa do odczytu, zmiany i zapisu.
2. **Przycinanie 0–100** - statystyki zawsze mają sens.
3. **Efekt jako słownik z opcjonalnymi kluczami** - dowolna kombinacja HP /
   Sanity / przedmiotu; łatwe do rozszerzenia.
4. **Wartości startowe w `config.json`** - zmiana bez ruszania kodu.
5. **Fabuła w `story.json`** - oddzielenie treści od programu.
6. **`cel_porazka` w danych** - rozgałęzienie sukces/porażka w danych, nie w kodzie.

---

## 7. Kluczowe pytania

- **„Czemu stan to słownik, a nie klasa?"** - bo to prosta struktura klucz–wartość,
  w zupełności wystarcza, a zapis to jeden `json.dump`.
- **„Jak działa utrata życia?"** - `aktualizuj_stan` dodaje wartość efektu do HP
  i przycina wynik do 0–100.
- **„Jak zbudowana jest jedna scena?"** - słownik z tekstem, obrazkiem, listą
  wyborów, efektem i flagą końca.
- **„Po co fabuła w osobnym pliku?"** - żeby zmieniać historię bez ruszania kodu.
