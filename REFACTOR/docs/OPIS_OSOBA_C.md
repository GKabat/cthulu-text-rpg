# Osoba C — Silnik fabuły i mechanika kości

Ten dokument opisuje **bardzo szczegółowo** część, za którą odpowiada Osoba C.
Po przeczytaniu powinieneś umieć omówić każdą swoją funkcję linijka po linijce
oraz uzasadnić podjęte decyzje.

## 1. Co należy do Ciebie

- cały `mechanics.py` — losowanie kości i sprawdzanie progu,
- cały `engine.py` — wczytanie fabuły i przechodzenie między scenami.

W skrócie: Twoja część to **zasady gry** — jak działa rzut kością i jak gra
przechodzi z jednej sceny do drugiej. Nie rysujesz nic na ekranie (to Osoba B),
ale to Ty decydujesz, *dokąd* gracz trafi i *czy* mu się udało.

## 2. Jak Twoja część łączy się z resztą

- `engine.py` korzysta z `mechanics.py` (`rzut_koscia`, `sprawdz_rzut`) oraz z
  `game_state.py` (`aktualizuj_stan`) — czyli z Twojej własnej mechaniki i z
  funkcji Osoby D.
- Osoba B (`obsluz_wybor`) woła Twój `wykonaj_wybor`, a `odswiez_scene` używa
  `pobierz_wezel` i `czy_koniec`.
- Osoba A (`zaladuj_dane`) woła Twój `wczytaj_fabule`.

---

## 3. `mechanics.py` — kości

### `rzut_koscia(zakres=20)`
```python
def rzut_koscia(zakres=20):
    return random.randint(1, zakres)
```
`random.randint(1, zakres)` losuje liczbę całkowitą od 1 do `zakres` **włącznie**.
Domyślnie `zakres=20`, czyli kość k20 (dwudziestościenna, jak w grach RPG).
Parametr domyślny pozwala w razie potrzeby rzucić inną kością, np. `rzut_koscia(6)`.

### `sprawdz_rzut(wynik, prog)`
```python
def sprawdz_rzut(wynik, prog):
    if wynik >= prog:
        return True
    else:
        return False
```
Zwraca `True`, gdy `wynik >= prog`, czyli gdy rzut był **co najmniej** równy
progowi. Im wyższy próg, tym trudniejsza próba (trzeba wyrzucić więcej).

**Uwaga na obronie:** to samo dałoby się napisać krócej jako `return wynik >= prog`.
Forma z `if/else` jest dłuższa, ale dla początkującego czytelniejsza — od razu
widać oba przypadki.

**Decyzja:** kości są w osobnym pliku, bo to jasno wydzielona część zasad
(„losowość"). Gdyby kiedyś doszły inne kości albo modyfikatory, wiadomo gdzie je
dopisać.

---

## 4. `engine.py` — silnik

### `wczytaj_fabule(sciezka)`
```python
def wczytaj_fabule(sciezka):
    plik = open(sciezka, "r", encoding="utf-8")
    fabula = json.load(plik)
    plik.close()
    print("[engine] Wczytano fabule:", len(fabula), "wezlow.")
    return fabula
```
Otwiera plik `story.json`, zamienia jego treść na **słownik** (`json.load`) i go
zwraca. `len(fabula)` to liczba scen — wypisujemy ją dla kontroli (przyda się przy
szukaniu błędów). `encoding="utf-8"` jest konieczne ze względu na polskie znaki.

**Decyzja:** fabuła jest w pliku JSON, a nie wpisana w kodzie. Dzięki temu treść
gry można zmieniać bez ruszania programu (to wspólna decyzja z Osobą D).

### `pobierz_wezel(fabula, id_wezla)`
```python
def pobierz_wezel(fabula, id_wezla):
    if id_wezla not in fabula:
        print("[engine] BLAD: brak wezla", id_wezla)
        return None
    return fabula[id_wezla]
```
Zwraca scenę o danej nazwie. Najpierw sprawdza, czy nazwa **w ogóle istnieje** w
słowniku. Jeśli nie — wypisuje błąd i zwraca `None` (zamiast wywalić grę). To
zabezpieczenie na wypadek literówki w danych (np. wybór prowadzący do
nieistniejącej sceny).

**Decyzja:** zwracamy `None` zamiast pozwolić na wyjątek. Dzięki temu jeden zły
wpis w danych nie zatrzymuje całej gry, a komunikat pomaga znaleźć błąd.

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
- **rzut kością** → losuje k20, porównuje z progiem (`prog`, domyślnie 10) i
  **zapisuje wynik do `stan["ostatni_rzut"]`**, żeby Osoba B mogła go pokazać
  graczowi po przejściu; zwraca, czy się udało,
- **min_hp / min_sanity** → wybór dostępny, gdy życie / poczytalność są co
  najmniej na podanym poziomie.
Gdyby warunek był nieznany — wypisuje błąd i zwraca `False`.

**Decyzja (ważna na obronie):** sam rzut **nie zmienia** punktów. On tylko mówi
„udało się czy nie". Punkty zmieniają się dopiero przez efekt sceny, do której
trafimy. To rozdzielenie „decyzji dokąd" od „zmiany czego" upraszcza zasady.

**Drobny szczegół:** kolejne `if`-y są niezależne, bo dany warunek ma tylko jeden
rodzaj (albo rzut, albo min_hp, albo min_sanity). To proste „rozpoznawanie po
kluczu".

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
To najważniejsza funkcja silnika — **przejście między scenami**. Logika:
1. Pobierz warunek wyboru i sprawdź go (`sprawdz_warunek`).
2. **Jeśli warunek niespełniony:**
   - gdy wybór ma zapasowy cel `cel_porazka` (np. nieudane wyważenie drzwi
     prowadzi do sceny z obrażeniami) — ustaw go jako bieżącą scenę i nałóż jej
     efekt,
   - w przeciwnym razie zostań na miejscu.
3. **Jeśli warunek spełniony:**
   - dopisz dotychczasową scenę do listy `odwiedzone` (jeśli jeszcze jej tam nie
     ma — bez duplikatów),
   - ustaw nową scenę (`cel`) jako bieżącą,
   - nałóż jej efekt na stan.

Zwracana wartość to nazwa nowej sceny.

**Decyzja:** efekt sceny nakładamy **przy wejściu** do niej — i to w obu
przypadkach (sukces i porażka). Dlatego np. wejście do sceny z `{"hp": -10}`
od razu odejmuje 10 życia.

**Po co lista `odwiedzone`?** To prosty zapis, gdzie gracz już był (przyda się np.
do statystyk albo przyszłych rozszerzeń). `not in ... append` pilnuje, by nie
dodawać tej samej sceny dwa razy.

### `czy_koniec(wezel)`
```python
def czy_koniec(wezel):
    return wezel.get("zakonczone", False)
```
Zwraca wartość pola `zakonczone` sceny (domyślnie `False`, gdyby pola nie było).
Mówi reszcie programu, czy dana scena kończy grę. Osoba B na tej podstawie
pokazuje ekran końcowy.

**Dlaczego `.get(... , False)`, a nie `wezel["zakonczone"]`?** Bo `.get` z
wartością domyślną nie wywali się, gdyby jakaś scena nie miała tego pola — po
prostu uzna, że to nie koniec.

### Tryb konsolowy (`if __name__ == "__main__"`)
Na dole pliku jest pętla, która pozwala przejść grę **w samym tekście**
(`python engine.py`): wypisuje opis sceny, statystyki i wybory, czyta numer z
klawiatury i woła `wykonaj_wybor`. Kończy się przy scenie końcowej lub gdy
HP/Sanity spadnie do zera. Służyło do szybkiego testowania logiki bez okna.

---

## 5. Decyzje projektowe w Twojej części

1. **Fabuła w JSON, wczytywana do słownika** — łatwo zmieniać treść bez kodu.
2. **`pobierz_wezel` zwraca `None` przy braku sceny** — błąd w danych nie wywala
   gry, tylko daje komunikat.
3. **Rozdzielenie warunku i efektu** — rzut decyduje „dokąd", scena docelowa
   decyduje „co się zmienia".
4. **Wynik rzutu zapisywany do stanu** — silnik liczy, a GUI tylko pokazuje
   (czysty podział: logika osobno, wyświetlanie osobno).
5. **`cel_porazka`** — elegancki sposób na „udało się / nie udało" bez
   rozbudowanej logiki: wystarczy podać drugi cel.
6. **Tryb konsolowy** — pozwala testować zasady bez interfejsu.

## 6. Co możesz powiedzieć na obronie

- **„Jak działa rzut kością?”** — `rzut_koscia` losuje 1–20, `sprawdz_rzut`
  porównuje z progiem; sukces, gdy wynik ≥ próg.
- **„Co się dzieje po kliknięciu wyboru?”** — `wykonaj_wybor` sprawdza warunek,
  ustawia nową scenę (główną przy sukcesie albo `cel_porazka` przy porażce) i
  nakłada jej efekt.
- **„Czy rzut odejmuje życie?”** — nie; rzut tylko wybiera scenę, a punkty zmienia
  dopiero efekt tej sceny.
- **„Co, jeśli w danych jest literówka w nazwie sceny?”** — `pobierz_wezel`
  zwróci `None` i wypisze błąd, zamiast wywalić grę.

## 7. Twoje testy

Twoja sekcja to przypadki **C1–C10** w `TestCases_Cien_nad_Arkham.xlsx` i
`TESTY.md` (zakres kości, próg, wczytanie fabuły, pobieranie węzła, warunki,
ścieżka porażki, wykrycie końca). Te testy są też **uruchamialne automatycznie**
w `tests/test_gra.py`.
