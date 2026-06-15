# Osoba A — Uruchomienie, budowa okna, menu i zapis gry

Ten dokument opisuje **bardzo szczegółowo** część, za którą odpowiada Osoba A.
Po przeczytaniu powinieneś umieć omówić każdą swoją funkcję linijka po linijce
oraz uzasadnić podjęte decyzje.

## 1. Co należy do Ciebie

**Pliki / fragmenty:**
- cały `main.py`,
- z `gui.py`: `utworz_okno`, `zaladuj_dane`, `pokaz_menu`, `nowa_gra`,
- z `gui.py` (zapis gry): `istnieje_zapis`, `komunikat`, `zapisz_gre`, `wczytaj_gre`.

W skrócie: Twoja część odpowiada za **start programu**, **zbudowanie okna**,
**menu główne** oraz **zapisywanie i wczytywanie gry**. To wszystko, co dzieje
się, zanim gracz zacznie klikać przez kolejne sceny (tym zajmuje się Osoba B).

## 2. Jak Twoja część łączy się z resztą

- `main.py` **woła** `utworz_okno()` z `gui.py` (przez `from gui import ...`).
- `zaladuj_dane()` **woła** `wczytaj_fabule` (Osoba C) i `inicjalizuj_stan`
  (Osoba D), a wynik zapisuje do zmiennych globalnych `fabula` i `stan`.
- `nowa_gra()` i `wczytaj_gre()` **wołają** `odswiez_scene()` (Osoba B), żeby
  narysować pierwszą scenę.
- `pokaz_menu()` korzysta z `istnieje_zapis()`, żeby wiedzieć, czy uaktywnić
  przycisk KONTYNUUJ.

---

## 3. `main.py` — punkt startu

```python
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(SCRIPT_DIR, "data", "config.json")
STORY = os.path.join(SCRIPT_DIR, "data", "story.json")
```

`__file__` to ścieżka do tego pliku. `os.path.dirname(...)` daje katalog, w którym
plik leży. Dzięki temu ścieżki do danych są liczone **względem pliku**, a nie
względem tego, skąd uruchomiono program — gra zadziała niezależnie od katalogu.

### `sprawdz_pliki()`

```python
def sprawdz_pliki():
    for sciezka in [CONFIG, STORY]:
        if not os.path.exists(sciezka):
            print("BLAD: brakuje pliku:", sciezka)
            sys.exit(1)
```

Przechodzi po liście wymaganych plików. `os.path.exists` sprawdza, czy plik
istnieje. Jeśli któregoś brakuje, wypisuje komunikat i **kończy program**
poleceniem `sys.exit(1)` (kod 1 oznacza zakończenie z błędem).

**Decyzja:** lepiej zatrzymać się od razu na starcie, niż dopiero wtedy, gdy gra
spróbuje wczytać brakujący plik w trakcie rozgrywki. Łatwiej wtedy zrozumieć, co
poszło nie tak.

### `uruchom()`

```python
def uruchom():
    sprawdz_pliki()
    from gui import utworz_okno
    print("Uruchamianie Cien nad Arkham...")
    okno = utworz_okno()
    okno.mainloop()
    print("Gra zakonczona.")
```

Kolejność: najpierw sprawdzamy pliki, potem importujemy i budujemy okno.
`okno.mainloop()` to **pętla zdarzeń** tkintera — program „utyka" w niej i czeka
na kliknięcia użytkownika aż do zamknięcia okna. Linijka po `mainloop()` wykona
się dopiero po zamknięciu gry.

**Dlaczego `from gui import` jest w środku funkcji, a nie na górze pliku?** Bo
chcemy najpierw sprawdzić pliki, a dopiero potem uruchamiać interfejs. Import
wewnątrz funkcji to dopuszczalne i tu wygodne rozwiązanie.

---

## 4. `gui.py` — Twoje funkcje

### `zaladuj_dane()`

```python
def zaladuj_dane():
    global fabula, stan
    plik = open(CONFIG_PATH, "r", encoding="utf-8")
    config = json.load(plik)
    plik.close()
    fabula = wczytaj_fabule(STORY_PATH)
    stan = inicjalizuj_stan(config)
```

Wczytuje ustawienia (`config.json`) i fabułę (`story.json`), a potem tworzy stan
startowy. `encoding="utf-8"` jest ważne, bo teksty mają polskie znaki.
`global fabula, stan` oznacza, że zapisujemy do zmiennych **globalnych** modułu,
żeby inne funkcje (np. `odswiez_scene`) miały do nich dostęp.

**Decyzja:** zmienne globalne to uproszczenie. W większym programie użyłoby się
klasy, ale przy tej skali globalne zmienne w jednym module są czytelne i
wystarczające.

### `utworz_okno()` — najważniejsza funkcja A

To tutaj powstaje całe okno. Przejdźmy po kawałkach.

**1. Okno bazowe:**
```python
root = tk.Tk()
root.title("Cien nad Arkham")
root.configure(bg="#000000")
```
`tk.Tk()` tworzy główne okno. `title` ustawia napis na pasku, `bg` to kolor tła.

**2. Wczytanie ramki:**
```python
obrazek_ramki = None
if os.path.exists(FRAME_PATH):
    try:
        obrazek_ramki = tk.PhotoImage(file=FRAME_PATH)
    except tk.TclError:
        obrazek_ramki = None
```
`tk.PhotoImage` wczytuje obrazek PNG. Całość jest w `try/except`, bo gdyby plik
był uszkodzony, gra nie powinna się wywalić — po prostu zostanie bez ramki.

**3. Dobór rozmiaru do ekranu:**
```python
if szer_ekranu < 1240 or wys_ekranu < 1000:
    if obrazek_ramki is not None:
        obrazek_ramki = obrazek_ramki.subsample(2, 2)
    SZER_OKNA = RAMKA_SZER // 2   # 592
    WYS_OKNA = RAMKA_WYS // 2     # 456
else:
    SZER_OKNA = RAMKA_SZER        # 1184
    WYS_OKNA = RAMKA_WYS          # 912
```
Jeśli ekran jest mały, zmniejszamy okno o połowę, a ramkę pomniejszamy metodą
`subsample(2, 2)` (bierze co drugi piksel). Na dużym ekranie używamy pełnego
rozmiaru 1184×912 (tyle ma grafika ramki).

**4. Przeliczenie otworu ramki:**
```python
OX0 = OTW_L * SZER_OKNA
OX1 = OTW_R * SZER_OKNA
OY0 = OTW_T * WYS_OKNA
OY1 = OTW_B * WYS_OKNA
OCX = (OX0 + OX1) / 2
OCY = (OY0 + OY1) / 2
OW = OX1 - OX0
OH = OY1 - OY0
```
`OTW_L`, `OTW_R`, `OTW_T`, `OTW_B` to **ułamki** (np. lewy brzeg ≈ 0,139
szerokości). Mnożąc przez rozmiar okna, dostajemy współrzędne otworu w pikselach.
`OCX/OCY` to środek otworu, `OW/OH` — jego szerokość i wysokość. Z tych wartości
Osoba B korzysta przy rozmieszczaniu treści.

**5. Wczytanie i skalowanie kości** (analogicznie do ramki, pomniejszane tak, by
zmieściło się w ~22% wysokości otworu).

**6. Płótno i ramka na wierzchu:**
```python
canvas = tk.Canvas(root, width=SZER_OKNA, height=WYS_OKNA, bg=TLO, ...)
canvas.pack(fill="both", expand=True)
if obrazek_ramki is not None:
    canvas.create_image(0, 0, image=obrazek_ramki, anchor="nw", tags="ramka")
pokaz_menu()
return root
```
Tworzymy Canvas (tło brązowe `TLO`), kładziemy na nim ramkę (z tagiem `"ramka"`,
żeby dało się ją trzymać na wierzchu) i pokazujemy menu.

**Dlaczego ułamki, a nie sztywne piksele?** Bo gdy okno raz jest 1184, a raz 592,
sztywne liczby by nie pasowały. Ułamki dopasowują się same.

### `pokaz_menu()`

Rysuje menu główne — tytuł, podtytuł i trzy przyciski:
```python
b_kont = tk.Button(canvas, text="KONTYNUUJ", ..., command=wczytaj_gre)
if not istnieje_zapis():
    b_kont.config(state="disabled", fg="#6b5d4a")
```
Przyciski są umieszczane na płótnie przez `canvas.create_window(...)` na
wysokościach liczonych od `OY0` (np. NOWA GRA na 0,53 wysokości otworu).
Kluczowy fragment: jeśli **nie ma zapisu**, przycisk KONTYNUUJ jest wyłączany
(`state="disabled"`) i przygaszany — nie da się go kliknąć.

**Decyzja:** przycisk jest widoczny zawsze, ale nieaktywny bez zapisu. To czytelne
dla gracza — od razu widać, że opcja istnieje, lecz na razie nie ma czego wczytać.

### `nowa_gra()`

```python
def nowa_gra():
    zaladuj_dane()
    odswiez_scene()
```
Dwa kroki: wczytaj dane od zera i narysuj pierwszą scenę. Wywoływana przyciskiem
NOWA GRA oraz „Zagraj ponownie" na ekranie końca.

---

## 5. Zapis i wczytanie gry

### `istnieje_zapis()`
```python
def istnieje_zapis():
    return os.path.exists(SAVE_PATH)
```
Prosta funkcja: czy plik `data/save.json` istnieje. Używana przez menu.

### `komunikat(tekst, kolor=KOLOR_ZLOTY)`
```python
canvas.delete("komunikat")
canvas.create_text(OCX, OY1 - OH * 0.04, text=tekst, ..., tags="komunikat")
root.after(1800, lambda: canvas.delete("komunikat"))
```
Pokazuje krótki napis na dole otworu (np. „Grę zapisano."). `root.after(1800, ...)`
mówi: „po 1800 milisekundach (1,8 s) usuń ten napis". Dzięki temu komunikat sam
znika. Najpierw kasujemy ewentualny poprzedni komunikat, żeby się nie nakładały.

### `zapisz_gre()`
```python
try:
    f = open(SAVE_PATH, "w", encoding="utf-8")
    json.dump(stan, f, ensure_ascii=False, indent=2)
    f.close()
    komunikat("Grę zapisano.")
except OSError:
    komunikat("Nie udało się zapisać.", KOLOR_ZLY)
```
`json.dump(stan, ...)` zapisuje cały słownik stanu do pliku. `ensure_ascii=False`
zachowuje polskie znaki, `indent=2` robi czytelne wcięcia. Jeśli zapis się nie
uda (np. brak uprawnień), `except OSError` wyłapie błąd i pokaże komunikat
zamiast wywalić grę.

**Decyzja (kluczowa na obronie):** ponieważ stan to zwykły słownik z prostych
typów (liczby, napisy, listy), zapis to **jedna linijka** `json.dump`. Gdyby stan
był klasą, trzeba by pisać dodatkowy kod do zamiany obiektu na dane. To dowód, że
wybór słownika (decyzja Osoby D) opłacił się także tutaj.

### `wczytaj_gre()`
```python
if not istnieje_zapis():
    komunikat("Brak zapisanej gry.", KOLOR_ZLY); return
try:
    f = open(SAVE_PATH, "r", encoding="utf-8")
    wczytany = json.load(f); f.close()
except (OSError, ValueError):
    komunikat("Plik zapisu jest uszkodzony.", KOLOR_ZLY); return

if fabula is None:
    fabula = wczytaj_fabule(STORY_PATH)
if "odwiedzone" not in wczytany: wczytany["odwiedzone"] = []
if "ekwipunek" not in wczytany: wczytany["ekwipunek"] = []
wczytany["ostatni_rzut"] = None
stan = wczytany
odswiez_scene()
komunikat("Wczytano zapisaną grę.")
```
Po kolei: jeśli nie ma zapisu — komunikat i koniec. Jeśli plik jest uszkodzony
(`json.load` rzuci `ValueError`) — też komunikat zamiast wysypania. Jeśli
wczytujemy z menu, fabuła może być jeszcze niewczytana (`fabula is None`), więc ją
doczytujemy. Dokładamy brakujące pola na wszelki wypadek (gdyby zapis był stary) i
zerujemy `ostatni_rzut` (żeby po wczytaniu nie wyświetlił się stary rzut). Na
końcu podstawiamy stan i rysujemy scenę.

**Decyzja:** wszystkie operacje na pliku są w `try/except`. Uszkodzony lub
brakujący zapis nie może zatrzymać gry — w najgorszym razie zobaczymy komunikat.

---

## 6. Decyzje projektowe w Twojej części

1. **Ścieżki liczone od `__file__`** — gra działa z dowolnego katalogu.
2. **Sprawdzenie plików na starcie** — błąd wychodzi od razu, nie w połowie gry.
3. **`try/except` przy wczytywaniu obrazków i pliku zapisu** — drobny problem nie
   wywala całej gry.
4. **Ułamkowe współrzędne otworu** — automatyczne skalowanie pod różne ekrany.
5. **Jeden slot zapisu (`save.json`)** — najprostsze możliwe rozwiązanie; w pełni
   wystarcza, a zapis/odczyt to jeden `json.dump` / `json.load`.
6. **KONTYNUUJ wyłączany bez zapisu** — czytelna informacja dla gracza.

## 7. Co możesz powiedzieć na obronie

- **„Jak uruchamia się gra?”** — `main.py` sprawdza pliki, woła `utworz_okno`,
  a `mainloop()` czeka na kliknięcia.
- **„Jak działa zapis?”** — stan to słownik, więc `json.dump` zapisuje go do
  `save.json`; wczytanie to `json.load`. Wszystko w `try/except`.
- **„Czemu okno raz jest większe, raz mniejsze?”** — na małym ekranie zmniejszamy
  je o połowę, a położenie treści liczymy w ułamkach, więc układ zawsze pasuje.
- **„Po co przycisk KONTYNUUJ jest czasem szary?”** — bo `istnieje_zapis()`
  zwraca `False`, więc go wyłączamy — nie ma jeszcze czego wczytać.

## 8. Twoje testy

Twoja sekcja to przypadki **A1–A10** w pliku `TestCases_Cien_nad_Arkham.xlsx`
oraz `TESTY.md` (kontrola plików, budowa i skalowanie okna, wczytanie zasobów,
stan startowy, logika przycisku KONTYNUUJ).
