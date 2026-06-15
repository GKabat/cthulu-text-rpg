# Osoba B — Renderowanie sceny, podpowiedzi i ekrany końca

Ten dokument opisuje **bardzo szczegółowo** część, za którą odpowiada Osoba B.
Po przeczytaniu powinieneś umieć omówić każdą swoją funkcję linijka po linijce
oraz uzasadnić podjęte decyzje.

## 1. Co należy do Ciebie

Z pliku `gui.py`:
- `odswiez_scene` — główne rysowanie sceny (najważniejsza funkcja),
- `obsluz_wybor` — obsługa kliknięcia w wybór,
- `ekran_koncowy` — ekran zwycięstwa / końca gry,
- pomocnicze: `wyczysc_kontent`, `ramka_na_wierzch`, `wczytaj_obrazek`,
- podpowiedzi: `opis_efektu`, `opis_celu`, `podpowiedz_efektu`.

W skrócie: Twoja część odpowiada za **to, co gracz widzi w trakcie gry** — scenę,
statystyki, przyciski z podpowiedziami, grafikę rzutu i ekrany końcowe. Osoba A
buduje okno i menu; Ty wypełniasz wnętrze treścią.

## 2. Jak Twoja część łączy się z resztą

- `odswiez_scene()` czyta zmienne globalne `fabula` i `stan` (przygotowane przez
  Osobę A) oraz woła `pobierz_wezel`, `czy_koniec` (Osoba C).
- Po kliknięciu wyboru `obsluz_wybor()` woła `wykonaj_wybor` (Osoba C), a potem
  znów `odswiez_scene()`.
- `podpowiedz_efektu()` zagląda do danych sceny (struktura od Osoby D), żeby
  zbudować opis tego, co robi wybór.

---

## 3. Funkcje pomocnicze (fundament rysowania)

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
Przed narysowaniem nowej sceny trzeba usunąć starą. Każdy element rysujemy z
**tagiem** `"kontent"`, więc `canvas.delete("kontent")` kasuje je wszystkie na
raz. Przyciski to osobne obiekty (`tk.Button`), więc dodatkowo niszczymy je w
pętli i czyścimy listę `przyciski_ref`. Ramka (tag `"ramka"`) **nie** ma tagu
`"kontent"`, więc zostaje.

**Decyzja:** tagowanie elementów to prosty sposób na „wyczyść wszystko oprócz
ramki". Bez tego trzeba by pamiętać i kasować każdy element z osobna.

### `ramka_na_wierzch()`
```python
def ramka_na_wierzch():
    canvas.tag_raise("ramka")
```
`tag_raise` podnosi ramkę na samą górę, żeby jej kamienne brzegi przykrywały
wszystko, co wystaje poza otwór. Wołane na końcu każdego rysowania.

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
Wczytuje PNG i — jeśli jest za duży — **pomniejsza go** metodą `subsample(k, k)`
(bierze co k-ty piksel). Pętla zwiększa `k`, dopóki obrazek nie zmieści się w
zadanym prostokącie `max_w × max_h`. Zabezpieczenie `if k > 12: break` chroni
przed nieskończoną pętlą. Jeśli pliku nie ma, funkcja zwraca `None`.

**Decyzja:** `subsample` zmniejsza tylko o całkowite wielokrotności (2×, 3×...),
ale jest wbudowany w tkinter — nie potrzebujemy biblioteki do grafiki (Pillow).

---

## 4. Podpowiedzi o efektach (tryb prezentacji)

To zestaw trzech funkcji, które **automatycznie** tworzą opis tego, co robi dany
wybór. Dzięki temu nie trzeba wpisywać podpowiedzi ręcznie w danych.

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
Zamienia słownik efektu na tekst. Dla `{"hp": -25}` zwróci `"HP -25"`, dla
`{"sanity": 20}` → `"Sanity +20"` (przy wartości dodatniej dokleja `+`), a dla
`{"dodaj_przedmiot": "kieł wilka"}` → `"+kieł wilka"`. Gdy efektu nie ma —
zwraca pusty napis.

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
Opisuje, co czeka w scenie, do której prowadzi wybór: jej efekt, a jeśli to
scena końcowa — informację „ZWYCIĘSTWO" lub „KONIEC GRY". Gdy nic szczególnego —
zwraca „dalej".

### `podpowiedz_efektu(wybor)`
Łączy powyższe w jedną podpowiedź. Dwa przypadki:
- **wybór z progiem porażki** (`cel_porazka`): pokazuje warunek oraz skutek
  sukcesu i porażki, np.
  `rzut k20 >= 12   |   sukces: dalej   |   porażka: HP -10`.
- **wybór zwykły**: pokazuje warunek (jeśli jest) i efekt celu, np. `Sanity -10`;
  gdy nic się nie zmienia — `bez zmian`.

**Decyzja (ważna na obronie):** podpowiedzi są **liczone z danych**, a nie
wpisane ręcznie. Gdy Osoba D zmieni efekt sceny, podpowiedź zaktualizuje się
sama. To mniej pracy i brak ryzyka, że opis rozjedzie się z fabułą.

---

## 5. `odswiez_scene()` — serce widoku

Najważniejsza funkcja Osoby B. Rysuje całą scenę od nowa. Kroki:

**1. Czyszczenie i pobranie sceny:**
```python
wyczysc_kontent()
wezel = pobierz_wezel(fabula, stan["obecny_wezel"])
pad = OW * 0.05
vpad = OH * 0.04
```
`pad` i `vpad` to marginesy liczone od rozmiaru otworu (czyli też skalowane).

**2. Górny pasek — statystyki (wyśrodkowane):**
```python
if stan["hp"] < 30: kolor_hp = KOLOR_ZLY
else:               kolor_hp = KOLOR_HP_OK
canvas.create_text(OCX - OW*0.02, OY0+vpad, text="HP: "+str(stan["hp"]),
                   fill=kolor_hp, anchor="e", ...)
canvas.create_text(OCX + OW*0.02, OY0+vpad, text="Sanity: "+str(stan["sanity"]),
                   fill=kolor_san, anchor="w", ...)
```
HP i Sanity są **wyśrodkowane** wokół środka otworu: HP kotwiczone od prawej
(`anchor="e"`), Sanity od lewej (`anchor="w"`). Kolor robi się czerwony, gdy
wartość spadnie poniżej 30 (ostrzeżenie).

**Decyzja:** statystyki są na środku, bo przy krawędziach chowałyby się za
ozdobami kamiennej ramki.

**3. Ekwipunek** — napis „Ekwipunek: (pusty)" albo lista przedmiotów.

**4. Przyciski górne** — „Menu" (prawy róg), „Zapisz" i „Wczytaj" (lewy róg).
Wołają funkcje Osoby A (`pokaz_menu`, `zapisz_gre`, `wczytaj_gre`).

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
`y` to „kursor" w pionie — rośnie w miarę dokładania elementów. Obrazek
dokładamy do listy `obrazki_ref`, **inaczej tkinter usunąłby go z pamięci** i
zniknąłby z ekranu. `canvas.bbox(item_tekst)` zwraca prostokąt zajmowany przez
tekst — z jego dolnej krawędzi (`bbox[3]`) wiemy, gdzie zacząć rysować przyciski.

**Decyzja:** używamy `bbox`, bo tekst zawija się na różną liczbę linii i nie
wiemy z góry, ile zajmie miejsca.

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
Najpierw sprawdzamy koniec gry: scena oznaczona jako końcowa **albo** spadek HP/
Sanity do zera → ekran końcowy. W przeciwnym razie dla każdego wyboru tworzymy
przycisk, którego napis to tekst wyboru **plus podpowiedź** w drugiej linii.
`command=lambda w=wybor: obsluz_wybor(w)` zapamiętuje, który to wybór (zapis
`w=wybor` „przymraża" bieżącą wartość — bez tego wszystkie przyciski wskazywałyby
ostatni wybór). `winfo_reqheight()` zwraca wysokość przycisku, żeby wiedzieć, ile
zejść w dół z kursorem.

**7. Grafika kości i wynik (gdy był rzut):**
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
Jeśli przy poprzednim wyborze nastąpił rzut (`ostatni_rzut` nie jest `None`), pod
przyciskami pokazujemy grafikę kości i wynik (np. „Rzut k20: 14 / prog 12 ->
SUKCES"), kolorem zielonym przy sukcesie, czerwonym przy porażce.

**8. Na koniec:**
```python
stan["ostatni_rzut"] = None
ramka_na_wierzch()
```
Zerujemy `ostatni_rzut`, żeby wynik pokazał się tylko raz, i podnosimy ramkę na
wierzch.

### `obsluz_wybor(wybor)`
```python
def obsluz_wybor(wybor):
    wykonaj_wybor(fabula, wybor, stan)
    odswiez_scene()
```
Po kliknięciu: pozwól silnikowi (Osoba C) wykonać wybór (zmiana sceny i stanu),
a potem narysuj nową scenę. To zamyka **pętlę gry**: rysuj → klik → przelicz →
rysuj.

### `ekran_koncowy(typ)`
```python
if typ == "dobry": naglowek = "ZWYCIESTWO"; kolor = KOLOR_HP_OK
else:              naglowek = "KONIEC GRY"; kolor = KOLOR_ZLY
canvas.create_text(OCX, y, text=naglowek, ...)
# + przyciski "Zagraj ponownie" (nowa_gra) i "Wroc do menu" (pokaz_menu)
```
Rysuje napis końcowy w odpowiednim kolorze i dwa przyciski. Tekst zakończonej
sceny zostaje na ekranie (nie czyścimy go) — gracz widzi i opis, i werdykt.

---

## 6. Decyzje projektowe w Twojej części

1. **Tagi `"kontent"` / `"ramka"`** — łatwe czyszczenie ekranu z pominięciem ramki.
2. **Lista `obrazki_ref`** — trzyma obrazki, żeby tkinter ich nie skasował.
3. **Kursor `y` + `canvas.bbox`** — układanie elementów pod sobą mimo zmiennej
   długości tekstu.
4. **`lambda w=wybor`** — poprawne zapamiętanie wyboru w przycisku.
5. **Podpowiedzi liczone z danych** — automatyczna zgodność z fabułą.
6. **Statystyki wyśrodkowane** — nie chowają się za ramką.
7. **Rzut pokazywany tylko raz** (zerowanie `ostatni_rzut`).

## 7. Co możesz powiedzieć na obronie

- **„Jak rysowana jest scena?”** — `odswiez_scene` czyści ekran, pobiera węzeł i
  układa pod sobą statystyki, obrazek, tekst i przyciski; na końcu podnosi ramkę.
- **„Skąd biorą się podpowiedzi na przyciskach?”** — `podpowiedz_efektu` czyta
  efekt i warunek wyboru z danych i sam buduje opis.
- **„Czemu obrazki trzymacie w liście?”** — bo tkinter usuwa obrazki, do których
  nikt się nie odwołuje; lista utrzymuje je przy życiu.
- **„Jak rozpoznajecie koniec gry?”** — `czy_koniec` (scena końcowa) albo spadek
  HP/Sanity do zera; wtedy wołamy `ekran_koncowy`.

## 8. Twoje testy

Twoja sekcja to przypadki **B1–B10** w `TestCases_Cien_nad_Arkham.xlsx` i
`TESTY.md` (kolory statystyk, ekwipunek, liczba przycisków, podpowiedzi, grafika
i wynik rzutu, ekrany końca). Część logiczna (podpowiedzi) jest też w
automatycznym `tests/test_gra.py`.
