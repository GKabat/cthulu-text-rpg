# Silnik fabuły i mechanika kości (`engine.py` + `mechanics.py`)

## 1. Zakres

- cały `mechanics.py` - losowanie kości i sprawdzanie progu,
- cały `engine.py` - wczytanie fabuły i przechodzenie między scenami.

## 2. Zależności z innymi modułami

- `engine.py` korzysta z `mechanics.py` (`rzut_koscia`, `sprawdz_rzut`) oraz z
  `game_state.py` (`aktualizuj_stan`).
- `gui.py` (`obsluz_wybor`) woła `wykonaj_wybor`; `odswiez_scene` używa
  `pobierz_wezel` i `czy_koniec`.
- `gui.py` (`zaladuj_dane`) woła `wczytaj_fabule`.

---

## 3. `mechanics.py` - kości

### `rzut_koscia(zakres=20)`
```python
def rzut_koscia(zakres=20):
    return random.randint(1, zakres)
```
`random.randint(1, zakres)` losuje liczbę całkowitą od 1 do `zakres` **włącznie**.
Domyślnie kość k20 (dwudziestościenna). Parametr domyślny pozwala w razie potrzeby
użyć innej kości, np. `rzut_koscia(6)`.

### `sprawdz_rzut(wynik, prog)`
```python
def sprawdz_rzut(wynik, prog):
    if wynik >= prog:
        return True
    else:
        return False
```
Zwraca `True`, gdy `wynik >= prog`. Im wyższy próg, tym trudniejsza próba.
Forma z `if/else` jest dłuższa niż `return wynik >= prog`, ale czytelniej
pokazuje oba przypadki.

Kości są w osobnym pliku, bo to wyraźnie wydzielona część zasad (losowość).
Nowe kości albo modyfikatory można dodać w jednym miejscu.

---

## 4. `engine.py` - silnik

### `wczytaj_fabule(sciezka)`
```python
def wczytaj_fabule(sciezka):
    plik = open(sciezka, "r", encoding="utf-8")
    fabula = json.load(plik)
    plik.close()
    print("[engine] Wczytano fabule:", len(fabula), "wezlow.")
    return fabula
```
Otwiera `story.json`, zamienia na słownik i zwraca. `len(fabula)` wypisuje liczbę
scen dla kontroli. Fabuła w pliku JSON - treść gry można zmieniać bez ruszania kodu.

### `pobierz_wezel(fabula, id_wezla)`
```python
def pobierz_wezel(fabula, id_wezla):
    if id_wezla not in fabula:
        print("[engine] BLAD: brak wezla", id_wezla)
        return None
    return fabula[id_wezla]
```
Zwraca scenę o danej nazwie. Gdy nazwa nie istnieje - wypisuje błąd i zwraca
`None` zamiast wywalić grę. Jeden zły wpis w danych nie zatrzymuje całej aplikacji.

### `sprawdz_warunek(warunek, stan)`
```python
def sprawdz_warunek(warunek, stan):
    if warunek is None:
        return True
    if "rzut_koscia" in warunek and warunek["rzut_koscia"] == True:
        wynik = rzut_koscia(20)
        prog = warunek.get("prog", 10)
        sukces = sprawdz_rzut(wynik, prog)
        stan["ostatni_rzut"] = {"wynik": wynik, "prog": prog, "sukces": sukces}
        print("[engine] Rzut k20:", wynik, "prog:", prog, "->", "SUKCES" if sukces else "PORAZKA")
        return sukces
    if "min_hp" in warunek:
        return stan["hp"] >= warunek["min_hp"]
    if "min_sanity" in warunek:
        return stan["sanity"] >= warunek["min_sanity"]
    print("[engine] Nieznany warunek:", warunek)
    return False
```
Sprawdza, czy gracz może skorzystać z wyboru. Trzy rodzaje warunków:
- **brak warunku** (`None`) → zawsze `True`,
- **rzut kością** → losuje k20, porównuje z progiem i **zapisuje wynik do
  `stan["ostatni_rzut"]`**, żeby GUI mogło go pokazać; zwraca czy się udało,
- **min_hp / min_sanity** → dostępny gdy życie / poczytalność ≥ podanej wartości.

Sam rzut **nie zmienia** punktów - tylko mówi „udało się czy nie". Punkty
zmieniają się przez efekt sceny, do której trafiamy. Rozdzielenie „decyzji dokąd"
od „zmiany czego" upraszcza zasady.

### `wykonaj_wybor(fabula, wybor, stan)`
```python
def wykonaj_wybor(fabula, wybor, stan):
    warunek = wybor.get("warunek")
    if not sprawdz_warunek(warunek, stan):
        if "cel_porazka" in wybor:
            stan["obecny_wezel"] = wybor["cel_porazka"]
            nowy = pobierz_wezel(fabula, wybor["cel_porazka"])
            if nowy is not None:
                aktualizuj_stan(stan, nowy.get("efekt"))
            return stan["obecny_wezel"]
        print("[engine] Warunek niespelniony, zostajesz na miejscu.")
        return stan["obecny_wezel"]

    nowy_id = wybor["cel"]
    if stan["obecny_wezel"] not in stan["odwiedzone"]:
        stan["odwiedzone"].append(stan["obecny_wezel"])
    stan["obecny_wezel"] = nowy_id
    nowy = pobierz_wezel(fabula, nowy_id)
    if nowy is not None:
        aktualizuj_stan(stan, nowy.get("efekt"))
    print("[engine] Przejscie ->", nowy_id)
    return nowy_id
```
Najważniejsza funkcja silnika - **przejście między scenami**. Logika:
1. Sprawdź warunek wyboru.
2. **Jeśli niespełniony:**
   - gdy wybór ma `cel_porazka` - ustaw tę scenę i nałóż jej efekt,
   - w przeciwnym razie zostań na miejscu.
3. **Jeśli spełniony:**
   - dopisz obecną scenę do `odwiedzone` (bez duplikatów),
   - ustaw nową scenę jako bieżącą i nałóż jej efekt.

Efekt nakładamy **przy wejściu** do sceny - dotyczy zarówno sukcesu, jak i porażki.
`cel_porazka` to elegancki sposób na „sukces / porażka" bez rozbudowanej logiki.

### `czy_koniec(wezel)`
```python
def czy_koniec(wezel):
    return wezel.get("zakonczone", False)
```
Zwraca wartość pola `zakonczone` (domyślnie `False`). `.get(..., False)` nie
wywali się, gdy scena nie ma tego pola.

### Tryb konsolowy (`if __name__ == "__main__"`)
Pętla na dole pliku pozwala przejść grę w czystym tekście (`python engine.py`)
bez okna GUI. Służyła do szybkiego testowania logiki.

---

## 5. Decyzje projektowe

1. **Fabuła w JSON, wczytywana do słownika** - treść można zmieniać bez kodu.
2. **`pobierz_wezel` zwraca `None` przy braku sceny** - błąd w danych nie zatrzymuje gry.
3. **Rozdzielenie warunku i efektu** - rzut decyduje „dokąd", scena docelowa „co się zmienia".
4. **Wynik rzutu zapisywany do stanu** - silnik liczy, GUI tylko pokazuje.
5. **`cel_porazka`** - rozgałęzienie sukces/porażka zapisane w danych, nie w kodzie.
6. **Tryb konsolowy** - testowanie zasad bez interfejsu.

---

## 6. Kluczowe pytania

- **„Jak działa rzut kością?"** - `rzut_koscia` losuje 1–20, `sprawdz_rzut`
  porównuje z progiem; sukces gdy wynik ≥ próg.
- **„Co się dzieje po kliknięciu wyboru?"** - `wykonaj_wybor` sprawdza warunek,
  ustawia nową scenę (sukces → `cel`, porażka → `cel_porazka`) i nakłada jej efekt.
- **„Czy rzut odejmuje życie?"** - nie; rzut wybiera tylko scenę, punkty zmienia
  efekt tej sceny.
- **„Co gdy w danych jest literówka w nazwie sceny?"** - `pobierz_wezel` zwróci
  `None` i wypisze błąd zamiast wywalić grę.
