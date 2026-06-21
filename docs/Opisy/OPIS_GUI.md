# GUI - Interfejs graficzny (`main.py` + `gui.py`)

## 1. Zakres

- cały `main.py`,
- cały `gui.py`: budowa okna, menu, zapis gry, renderowanie scen, podpowiedzi.

## 2. Zależności z innymi modułami

- `main.py` woła `utworz_okno()` z `gui.py`.
- `zaladuj_dane()` woła `wczytaj_fabule` (engine.py) i `inicjalizuj_stan` (game_state.py),
  wyniki zapisuje do globalnych `fabula` i `stan`.
- `nowa_gra()` i `wczytaj_gre()` wołają `odswiez_scene()`, żeby narysować pierwszą scenę.
- `odswiez_scene()` czyta globalne `fabula` i `stan` oraz woła `pobierz_wezel`, `czy_koniec`
  (engine.py).
- Po kliknięciu wyboru `obsluz_wybor()` woła `wykonaj_wybor` (engine.py), a potem
  znów `odswiez_scene()`.

---

## 3. `main.py` - punkt startu

```python
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(SCRIPT_DIR, "data", "config.json")
STORY = os.path.join(SCRIPT_DIR, "data", "story.json")
```

`__file__` to ścieżka do tego pliku. `os.path.dirname(...)` daje katalog, w którym
plik leży. Dzięki temu ścieżki do danych są liczone **względem pliku**, a nie
względem katalogu roboczego - gra zadziała niezależnie od miejsca uruchomienia.

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
poleceniem `sys.exit(1)`. Lepiej zatrzymać się od razu niż dopiero gdy gra
spróbuje wczytać brakujący plik w trakcie rozgrywki.

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
`okno.mainloop()` to **pętla zdarzeń** tkintera - program czeka w niej na
kliknięcia użytkownika aż do zamknięcia okna.

Import `from gui import` jest wewnątrz funkcji, żeby najpierw sprawdzić pliki,
a dopiero potem uruchamiać interfejs.

---

## 4. `gui.py` - okno, menu i zapis

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

Wczytuje ustawienia (`config.json`) i fabułę (`story.json`), tworzy stan startowy.
`encoding="utf-8"` konieczne ze względu na polskie znaki.
`global fabula, stan` zapisuje do zmiennych globalnych modułu, żeby inne funkcje
(np. `odswiez_scene`) miały do nich dostęp.

### `utworz_okno()`

**1. Okno bazowe:**
```python
root = tk.Tk()
root.title("Cien nad Arkham")
root.configure(bg="#000000")
```

**2. Wczytanie ramki:**
```python
obrazek_ramki = None
if os.path.exists(FRAME_PATH):
    try:
        obrazek_ramki = tk.PhotoImage(file=FRAME_PATH)
    except tk.TclError:
        obrazek_ramki = None
```
`tk.PhotoImage` wczytuje PNG. Całość w `try/except` - uszkodzony plik nie wywala
gry, tylko zostaje bez ramki.

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
Na małym ekranie okno zmniejszane o połowę, ramka przez `subsample(2, 2)`.

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
`OTW_L/R/T/B` to ułamki (np. lewy brzeg ≈ 0,139 szerokości). Mnożąc przez rozmiar
okna, dostajemy piksele. `OCX/OCY` to środek otworu, `OW/OH` - jego rozmiary.
Używane przy rozmieszczaniu treści w `odswiez_scene`.

Ułamki zamiast sztywnych pikseli - bo przy dwóch różnych rozmiarach okna
sztywne liczby nie pasowałyby. Ułamki dopasowują się automatycznie.

**5. Płótno i ramka:**
```python
canvas = tk.Canvas(root, width=SZER_OKNA, height=WYS_OKNA, bg=TLO, ...)
canvas.pack(fill="both", expand=True)
if obrazek_ramki is not None:
    canvas.create_image(0, 0, image=obrazek_ramki, anchor="nw", tags="ramka")
pokaz_menu()
return root
```
Canvas (brązowe tło `TLO`), ramka z tagiem `"ramka"` (trzymana na wierzchu), menu.

### `pokaz_menu()`

Rysuje menu główne - tytuł, podtytuł i trzy przyciski:
```python
b_kont = tk.Button(canvas, text="KONTYNUUJ", ..., command=wczytaj_gre)
if not istnieje_zapis():
    b_kont.config(state="disabled", fg="#6b5d4a")
```
Jeśli nie ma zapisu, KONTYNUUJ jest wyłączany - widoczny, ale nieaktywny.
Gracz od razu widzi, że opcja istnieje, lecz nie ma czego wczytać.

### `nowa_gra()`

```python
def nowa_gra():
    zaladuj_dane()
    odswiez_scene()
```
Wczytaj dane od zera i narysuj pierwszą scenę.

---

## 5. Zapis i wczytanie gry

### `istnieje_zapis()`
```python
def istnieje_zapis():
    return os.path.exists(SAVE_PATH)
```
Czy plik `app/data/save.json` istnieje. Używane przez menu.

### `komunikat(tekst, kolor=KOLOR_ZLOTY)`
```python
canvas.delete("komunikat")
canvas.create_text(OCX, OY1 - OH * 0.04, text=tekst, ..., tags="komunikat")
root.after(1800, lambda: canvas.delete("komunikat"))
```
Krótki napis na dole otworu (np. „Grę zapisano."). `root.after(1800, ...)` usuwa
go po 1,8 s. Kasujemy ewentualny poprzedni komunikat, żeby się nie nakładały.

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
`json.dump(stan, ...)` zapisuje cały słownik stanu. `ensure_ascii=False` zachowuje
polskie znaki, `indent=2` daje czytelne wcięcia. `except OSError` chroni przed
błędem zapisu zamiast wywalić grę.

Stan to zwykły słownik z prostych typów (liczby, napisy, listy), więc zapis to
**jedna linijka** `json.dump`. To korzyść z trzymania stanu jako słownika.

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
Jeśli plik uszkodzony (`json.load` rzuci `ValueError`) - komunikat zamiast
wyjątku. Jeśli fabuła jeszcze nie wczytana (`fabula is None`) - doczytujemy.
Brakujące pola uzupełniamy na wypadek starego zapisu. Zerujemy `ostatni_rzut`,
żeby stary wynik rzutu nie pojawił się po wczytaniu.

---

## 6. Renderowanie sceny

### `wyczysc_kontent()`
```python
def wyczysc_kontent():
    global obrazki_ref, przyciski_ref
    canvas.delete("kontent")
    canvas.delete("komunikat")
    for b in przyciski_ref:
        b.destroy()
    przyciski_ref = []
    obrazki_ref = []
```
Przed nową sceną kasujemy starą. Tag `"kontent"` usuwa wszystkie elementy naraz.
Przyciski to osobne obiekty (`tk.Button`) - niszczymy je w pętli. Ramka (tag
`"ramka"`) nie ma tagu `"kontent"`, więc zostaje.

### `ramka_na_wierzch()`
```python
def ramka_na_wierzch():
    canvas.tag_raise("ramka")
```
Podnosi ramkę na samą górę, żeby kamienne brzegi przykrywały elementy
wystające poza otwór. Wołane na końcu każdego rysowania.

### `wczytaj_obrazek(sciezka, max_w, max_h)`
```python
img = tk.PhotoImage(file=pelna)
k = 1
while (img.width() // k) > max_w or (img.height() // k) > max_h:
    k = k + 1
    if k > 12:
        break
if k > 1:
    img = img.subsample(k, k)
return img
```
Wczytuje PNG i pomniejsza go `subsample(k, k)` aż zmieści się w `max_w × max_h`.
`subsample` wymaga liczby całkowitej (2×, 3×...), ale jest wbudowany w tkinter -
nie potrzeba zewnętrznej biblioteki graficznej. Jeśli pliku nie ma - zwraca `None`.

### `odswiez_scene()` - główne rysowanie

**1. Czyszczenie i pobranie sceny:**
```python
wyczysc_kontent()
wezel = pobierz_wezel(fabula, stan["obecny_wezel"])
pad = OW * 0.05
vpad = OH * 0.04
```
`pad` i `vpad` to marginesy skalowane od rozmiaru otworu.

**2. Górny pasek - statystyki (wyśrodkowane):**
```python
if stan["hp"] < 30: kolor_hp = KOLOR_ZLY
else:               kolor_hp = KOLOR_HP_OK
canvas.create_text(OCX - OW*0.02, OY0+vpad, text="HP: "+str(stan["hp"]),
                   fill=kolor_hp, anchor="e", ...)
canvas.create_text(OCX + OW*0.02, OY0+vpad, text="Sanity: "+str(stan["sanity"]),
                   fill=kolor_san, anchor="w", ...)
```
HP i Sanity wyśrodkowane wokół środka otworu (HP z prawej, Sanity z lewej).
Kolor czerwony gdy wartość < 30. Statystyki na środku, bo przy krawędziach
chowałyby się za ozdobami ramki.

**3.** Ekwipunek - „(pusty)" albo lista przedmiotów.

**4.** Przyciski górne - „Menu", „Zapisz", „Wczytaj".

**5. Obrazek i tekst sceny:**
```python
y = OY0 + OH * 0.13
img = wczytaj_obrazek(wezel.get("obrazek"), int(OW*0.6), int(OH*0.26))
if img is not None:
    obrazki_ref.append(img)
    canvas.create_image(OCX, y, image=img, anchor="n", tags="kontent")
    y = y + img.height() + OH*0.02
item_tekst = canvas.create_text(OCX, y, text=wezel["tekst"], width=OW-2*pad, ...)
bbox = canvas.bbox(item_tekst)
if bbox is not None:
    y = bbox[3] + OH*0.025
```
`y` to kursor w pionie - rośnie w miarę dodawania elementów. Obrazek trafia do
listy `obrazki_ref` - inaczej tkinter usunąłby go z pamięci i zniknąłby z ekranu.
`canvas.bbox(item_tekst)` zwraca prostokąt tekstu - z jego dolnej krawędzi
(`bbox[3]`) wiadomo, gdzie zacząć rysować przyciski. Tekst zawija się na różną
liczbę linii, stąd `bbox` zamiast stałej wartości.

**6. Koniec gry albo przyciski wyboru:**
```python
if czy_koniec(wezel):
    ekran_koncowy(wezel.get("zakonczenie", "dobry"))
elif stan["hp"] <= 0 or stan["sanity"] <= 0:
    ekran_koncowy("zly")
else:
    for wybor in wezel["wybory"]:
        etykieta = wybor["tekst"] + "\n( " + podpowiedz_efektu(wybor) + " )"
        b = tk.Button(canvas, text=etykieta, ..., command=lambda w=wybor: obsluz_wybor(w))
        canvas.create_window(OCX, y, window=b, anchor="n", width=int(OW-2*pad), ...)
        przyciski_ref.append(b)
        canvas.update_idletasks()
        y = y + b.winfo_reqheight() + OH*0.018
```
Ekran końcowy gdy: scena oznaczona jako końcowa, lub HP/Sanity = 0. W przeciwnym
razie dla każdego wyboru tworzymy przycisk z podpowiedzią w drugiej linii.
`command=lambda w=wybor: obsluz_wybor(w)` - zapis `w=wybor` „przymraża" bieżącą
wartość; bez tego wszystkie przyciski wskazywałyby ostatni wybór.

**7. Grafika kości i wynik:**
```python
rzut = stan.get("ostatni_rzut")
if rzut is not None and obrazek_kosci is not None:
    ky = y + OH*0.015
    canvas.create_image(OCX, ky, image=obrazek_kosci, anchor="n", ...)
    if rzut["sukces"]: kol = KOLOR_HP_OK; verdykt = "SUKCES"
    else:              kol = KOLOR_ZLY;   verdykt = "PORAŻKA"
    canvas.create_text(OCX, ky + obrazek_kosci.height() + 6,
        text="Rzut k20: "+str(rzut["wynik"])+"   /   prog "+str(rzut["prog"])+"   ->   "+verdykt,
        fill=kol, ...)
```
Jeśli był rzut, pod przyciskami pokazujemy grafikę kości i wynik (zielony/czerwony).

**8. Na koniec:**
```python
stan["ostatni_rzut"] = None
ramka_na_wierzch()
```
Zerujemy `ostatni_rzut` (wynik pokazuje się tylko raz) i podnosimy ramkę.

### `obsluz_wybor(wybor)`
```python
def obsluz_wybor(wybor):
    wykonaj_wybor(fabula, wybor, stan)
    odswiez_scene()
```
Silnik wykonuje wybór (zmiana sceny i stanu), potem rysowana jest nowa scena.
To zamknięcie pętli gry: rysuj → klik → przelicz → rysuj.

### `ekran_koncowy(typ)`
```python
if typ == "dobry": naglowek = "ZWYCIESTWO"; kolor = KOLOR_HP_OK
else:              naglowek = "KONIEC GRY"; kolor = KOLOR_ZLY
canvas.create_text(OCX, y, text=naglowek, ...)
# + przyciski "Zagraj ponownie" (nowa_gra) i "Wroc do menu" (pokaz_menu)
```
Napis końcowy w odpowiednim kolorze i dwa przyciski. Tekst sceny zostaje -
gracz widzi jednocześnie opis i werdykt.

---

## 7. Podpowiedzi o efektach

Trzy funkcje, które automatycznie tworzą opis efektu wyboru z danych. Nie trzeba
wpisywać podpowiedzi ręcznie - wynikają z `story.json`. Gdy ktoś zmieni efekt
sceny, podpowiedź zaktualizuje się sama.

### `opis_efektu(efekt)`
```python
if not efekt:
    return ""
czesci = []
if "hp" in efekt:
    v = efekt["hp"]
    if v > 0: czesci.append("HP +" + str(v))
    else:     czesci.append("HP " + str(v))
...
return ", ".join(czesci)
```
Zamienia słownik efektu na tekst: `{"hp": -25}` → `"HP -25"`,
`{"sanity": 20}` → `"Sanity +20"`, `{"dodaj_przedmiot": "kieł wilka"}` → `"+kieł wilka"`.

### `opis_celu(wezel)`
```python
if wezel is None: return "dalej"
ef = opis_efektu(wezel.get("efekt"))
if wezel.get("zakonczone"):
    if wezel.get("zakonczenie") == "dobry": koniec = "ZWYCIĘSTWO"
    else: koniec = "KONIEC GRY"
    return koniec + " (" + ef + ")" if ef else koniec
return ef if ef else "dalej"
```
Opisuje co czeka w scenie docelowej: efekt albo informację o zakończeniu.
Gdy nic szczególnego - „dalej".

### `podpowiedz_efektu(wybor)`
Łączy powyższe w jedną podpowiedź:
- **wybór z progiem porażki** (`cel_porazka`): warunek + skutek sukcesu i porażki,
  np. `rzut k20 >= 12 | sukces: dalej | porażka: HP -10`.
- **wybór zwykły**: warunek (jeśli jest) i efekt celu; gdy nic się nie zmienia - `bez zmian`.

---

## 8. Decyzje projektowe

1. **Ścieżki liczone od `__file__`** - gra działa z dowolnego katalogu.
2. **Sprawdzenie plików na starcie** - błąd widoczny od razu, nie w połowie gry.
3. **`try/except` przy obrazkach i pliku zapisu** - drobny problem nie wywala gry.
4. **Ułamkowe współrzędne otworu** - automatyczne skalowanie pod różne ekrany.
5. **Jeden slot zapisu (`save.json`)** - najprostsze możliwe rozwiązanie.
6. **KONTYNUUJ wyłączany bez zapisu** - czytelna informacja dla gracza.
7. **Tagi `"kontent"` / `"ramka"`** - łatwe czyszczenie ekranu z pominięciem ramki.
8. **Lista `obrazki_ref`** - trzyma obrazki, żeby tkinter ich nie usunął z pamięci.
9. **Kursor `y` + `canvas.bbox`** - układanie elementów pod sobą mimo zmiennej długości tekstu.
10. **`lambda w=wybor`** - poprawne zapamiętanie wyboru w przycisku.
11. **Podpowiedzi liczone z danych** - automatyczna zgodność z fabułą.
12. **Zerowanie `ostatni_rzut`** - wynik rzutu pokazuje się tylko raz.

---

## 9. Kluczowe pytania

- **„Jak uruchamia się gra?"** - `main.py` sprawdza pliki, woła `utworz_okno`,
  a `mainloop()` czeka na kliknięcia.
- **„Jak działa zapis?"** - stan to słownik, więc `json.dump` zapisuje go do
  `save.json`; wczytanie to `json.load`. Wszystko w `try/except`.
- **„Czemu okno raz jest większe, raz mniejsze?"** - na małym ekranie zmniejszamy
  je o połowę; położenie treści liczymy w ułamkach, więc układ zawsze pasuje.
- **„Po co KONTYNUUJ czasem jest szary?"** - `istnieje_zapis()` zwraca `False`,
  więc przycisk wyłączamy - nie ma jeszcze czego wczytać.
- **„Jak rysowana jest scena?"** - `odswiez_scene` czyści ekran, pobiera węzeł
  i układa pod sobą statystyki, obrazek, tekst i przyciski; na końcu podnosi ramkę.
- **„Skąd biorą się podpowiedzi na przyciskach?"** - `podpowiedz_efektu` czyta
  efekt i warunek wyboru z danych i sam buduje opis.
- **„Czemu obrazki trzymane są w liście?"** - tkinter usuwa obrazki, do których
  nikt się nie odwołuje; lista utrzymuje je przy życiu.
- **„Jak rozpoznawany jest koniec gry?"** - `czy_koniec` (scena końcowa) albo
  spadek HP/Sanity do zera; wtedy wołana jest `ekran_koncowy`.
