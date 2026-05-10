# Sciaga na obrone - "jak krowie na rowie"

Tekst napisany jak student po 2 miesiacach Pythona. Bez zaawansowanych slow.
Mowisz wlasnymi slowami, nie czytasz z kartki.

---

## 1. Z czego sklada sie projekt? (po co jest kazdy plik)

- **`main.py`** - to jest plik ktory uruchamiamy. Sprawdza czy istnieja pliki z danymi i wlacza okno gry.
- **`gui.py`** - rysuje okno (menu, ekran gry, przyciski). Uzywam `tkinter` bo to jest "wbudowana" biblioteka Pythona.
- **`engine.py`** - "silnik" gry. Wczytuje fabule i pilnuje na ktorym wezle jest gracz.
- **`game_state.py`** - tu trzymam stan gry (HP, Sanity). To jest zwykly slownik.
- **`mechanics.py`** - rzut koscia i sprawdzenie czy sie udalo.
- **`data/config.json`** - ustawienia startowe (tytul gry, startowe HP, Sanity).
- **`data/story.json`** - cala fabula. Lista "wezlow" - kazdy wezel to scena z wyborami.
- **`assets/`** - folder z grafikami PNG dla scen.

## 2. Jak dziala glowna petla gry? (ekran gry)

Funkcja `odswiez_scene()` w `gui.py`:
1. Sprawdzam ktory wezel jest aktualny (`stan["obecny_wezel"]`).
2. Pobieram wezel z fabuly.
3. Wyswietlam tekst, obrazek i statystyki.
4. Sprawdzam czy to nie koniec (HP=0, Sanity=0 albo flaga `zakonczone`).
5. Rysuje przyciski wyborow.

Jak gracz klika przycisk, wywoluje sie `obsluz_wybor(wybor)` -> ten woła `wykonaj_wybor()` z silnika -> i znowu `odswiez_scene()`. I tak w kolko, az do konca gry.

## 3. Co robi kazda zmienna? (najwazniejsze)

- `fabula` (slownik) - cale story.json wczytane z pliku.
- `stan` (slownik) - aktualny stan gracza:
  - `obecny_wezel` - id sceny w ktorej teraz jest gracz
  - `hp` - punkty zycia (0..100)
  - `sanity` - poczytalnosc (0..100)
  - `nazwa_postaci` - imie postaci z config.json
  - `odwiedzone` - lista juz odwiedzonych scen (zeby nie dodac duplikatow)
- `wezel` - jeden konkretny element fabuly: tekst + obrazek + wybory + efekt.
- `wybor` - jedna opcja przycisku: tekst + cel (do ktorej sceny prowadzi) + opcjonalnie warunek.

## 4. Jak dziala rzut koscia?

W `mechanics.py`:
```python
def rzut_koscia(zakres=20):
    return random.randint(1, zakres)

def sprawdz_rzut(wynik, prog):
    if wynik >= prog:
        return True
    else:
        return False
```

To zwykla losowa liczba od 1 do 20. Jezeli wybor ma w story.json zapisane np. `"warunek": {"rzut_koscia": true, "prog": 12}`, to silnik losuje liczbe i porownuje ja z 12. Jak >= 12, sukces. Jak nie - porazka.

## 5. Jak dziala "if/elif" w warunkach?

W `engine.py` w funkcji `sprawdz_warunek()` mam trzy rodzaje warunkow:
- `rzut_koscia` -> losuje liczbe i sprawdza czy >= prog
- `min_hp` -> sprawdza czy HP gracza jest >= minimum
- `min_sanity` -> tak samo dla Sanity

Robie to przez kolejne `if`. Jak ktorys pasuje to zwracam wynik. Proste jak konstrukcja cepa.

## 6. Jak dziala petla `while`?

W trybie konsolowym (na samym dole `engine.py`) mam petle `while True:` ktora:
1. Pobiera wezel.
2. Drukuje tekst i wybory.
3. Czeka na wpis gracza.
4. Wywoluje wybor.
5. Wraca na poczatek petli.

Petla konczy sie przez `break`, gdy gra dojdzie do wezla z `zakonczone: true` albo HP/Sanity spada do 0.

## 7. Jak dziala obrazek sceny?

Tkinter od Pythona 3.9 sam czyta pliki PNG przez `tk.PhotoImage(file="sciezka")`. Nie potrzeba `Pillow`. Jezeli pliku nie ma na dysku, funkcja `wyswietl_obrazek()` po prostu chowa pole obrazka i nic sie nie psuje.

Grafiki sa w folderze `tiles/` (np. `tiles/camp.png`, `tiles/old_man.png`). Kazdy wezel w `data/story.json` ma pole `obrazek` ze sciezka do pliku.

## 8. Jak dziala wyswietlanie wyniku rzutu?

Gdy gracz klika wybor wymagajacy rzutu kostka, w `engine.sprawdz_warunek()` losuje sie wynik k20 i jest zapisywany do `stan["ostatni_rzut"]`. Funkcja `wyswietl_rzut()` w GUI sprawdza ten klucz po kazdym wyborze - jak nie jest None, pokazuje grafike kosci (`tiles/dice_roll.png`) i tekst typu "Rzut k20: 14 / prog: 12 -> SUKCES" w osobnej ramce nad opisem sceny. Po wyswietleniu czyscimy klucz, zeby informacja nie zostala na stale.

## 8. Jak testowalismy (recznie)?

Recznie testowalem chodzac po grze:
1. **Sciezka happy-path przez rozstaje**: intro -> rozdroze -> rozstaje -> "Zapytaj o droge" (sanity 100, warunek min 50 spelniony) -> final_dobry. Konczy sie ZWYCIESTWEM.
2. **Sciezka happy-path przez chate**: intro -> rozdroze -> "Wywaz drzwi chaty" (rzut udany >= 12) -> chata -> mapa -> final_dobry.
3. **Sciezka utraty sanity (single-click)**: intro -> rozdroze -> jaskinia (-10 san) -> glebiny (-10) -> "Wpatrz sie w te oczy" -> final_szalenstwo (-100 san). Sanity zeruje sie jednym wyborem.
4. **Sciezka utraty hp (single-click)**: intro -> rozdroze -> rozstaje -> "Rzuc sie z piesciami" -> atak_potwora (hp -100). HP zeruje sie jednym wyborem.
5. **Sciezka szeptu (warunek niespelniony)**: doprowadz Sanity ponizej 50 (np. przez kilka wejsc do jaskini), potem rozstaje -> "Zapytaj o droge" -> trafiamy do szept (cel_porazka) zamiast final_dobry.
6. **Test rzutu kostka**: rozdroze -> "Wywaz drzwi chaty". Czasami sukces (chata), czasami porazka (chata_porazka, hp -10). Po rzucie GUI pokazuje grafike kosci i wynik.

Plus uruchomienie samego silnika z konsoli: `python engine.py` - chodzi po grze bez okna, tylko tekst. To pomoglo mi szybko sprawdzic logike bez czekania az narysuje sie GUI.

---

## 5 typowych pytan od prowadzacego (z gotowymi odpowiedziami)

### Pyt. 1: "Dlaczego trzymasz stan gry w slowniku, a nie w klasie?"

**Odp.:** Bo to prostsze. W klasie musialbym pisac konstruktor, samodzielne metody, dziedziczenie - a u mnie to jest po prostu jedna struktura danych: HP, Sanity, obecny wezel. Slownik wystarczy. Kazdy modul moze go odczytac i zmodyfikowac. Jakby projekt rosl, to mozna by przejsc na klase, ale teraz nie ma takiej potrzeby.

### Pyt. 2: "Co sie stanie jak ktos rozpisze blednie story.json?"

**Odp.:** W `engine.py` jest funkcja `pobierz_wezel()` ktora sprawdza czy id wezla istnieje w fabule. Jak nie - drukuje blad i zwraca `None`. W gracznym trybie to konczy gre (None to nie jest wezel z tekstem). Plus `json.load` sam rzuca wyjatek jak skladnia JSON jest zla, wiec wtedy gra nie wstanie. To jest celowe - lepiej zeby wywalilo sie na starcie niz w polowie rozgrywki.

### Pyt. 3: "Czemu nie uzywasz dekoratorow / klas / async?"

**Odp.:** Bo nie potrzebuje. Gra jest synchroniczna - nie ma operacji ktore trwaja dlugo (zadnych sieci ani dlugiego czytania plikow w czasie gry). Nie ma metod ktore powtarzaja sie identycznie - nie potrzebuje dekoratorow. Klasy to overkill na 5 funkcji ktore operuja na slowniku. Trzymam sie zasady "najprostsze rozwiazanie ktore dziala" - tak jak nas uczyli na pierwszym roku.

### Pyt. 4: "Jak dodalbys nowa funkcjonalnosc, np. ekwipunek albo ulepszenie statystyk?"

**Odp.:** Najszybciej dodalbym do `aktualizuj_stan()` w `game_state.py` obsluge nowego pola w `efekt`, np. `"sila": +5` albo `"dodaj_przedmiot": "latarnia"`. Plus odpowiednie pole w startowym stanie (`inicjalizuj_stan`). Jezeli ma byc test - dodaje do `sprawdz_warunek()` nowy `if "min_sila" in warunek` albo `if "wymagany_przedmiot" in warunek`. Logiki nie trzeba przepisywac - format danych jest po prostu rozszerzany. Z gory zaplanowalismy taka mozliwosc, ale do MVP to pomijamy.

### Pyt. 5: "Czemu uzywasz tkinter a nie pygame / PyQt / wxPython?"

**Odp.:** Bo `tkinter` jest w standardowej bibliotece - nie trzeba nic instalowac. PyQt i pygame trzeba doinstalowac przez pip, co utrudnia oddanie projektu (ktos by musial sobie to skonfigurowac). Tkinter ma wszystko czego potrzebuje: okno, etykiety, przyciski, ramki, obrazki PNG. Bez fajerwerkow, ale dziala.

---

## Bonus - co mowic jak nie wiesz

- "Pisalem to z kolega, on to zrobil tu, ja tam"
- "Wiem ze to mozna zrobic ladniej, ale w terminie zostalo tak"
- "Ten fragment wzorowalem na przykladach z labow"
- "Sprawdzalem ze dziala, nie sprawdzalem czemu dziala dokladnie tak"

To brzmi jak student, a nie jak wykladowca.
