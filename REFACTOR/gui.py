# gui.py  (wersja REFACTOR)
# Okno gry oparte na tkinter. Roznica wzgledem starej wersji:
# - calosc rysujemy na jednym Canvasie,
# - tlo (brazowe) wypelnia cale okno, wiec nic nie "przebija" zza ramki,
# - ramke (tiles/frame.png z PRZEZROCZYSTYM srodkiem) kladziemy NA WIERZCHU,
#   a tresc gry siedzi w jej przezroczystym otworze.
#
# Dzieki przezroczystemu srodkowi ramki brazowe tlo Canvasa widac w otworze,
# a kamienne brzegi ramki zaslaniaja wszystko poza otworem.

import json
import os
import tkinter as tk

from engine import wczytaj_fabule, pobierz_wezel, wykonaj_wybor, czy_koniec
from game_state import inicjalizuj_stan


# ── Sciezki (liczone wzgledem polozenia tego pliku, wiec dzialaja z dowolnego cwd) ──
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))   # .../REFACTOR
ROOT = os.path.dirname(SCRIPT_DIR)                         # katalog glowny projektu

def _dane(nazwa):
    # Najpierw szukamy danych nowej wersji (REFACTOR/data), inaczej wspolne (../data).
    lokalna = os.path.join(SCRIPT_DIR, "data", nazwa)
    if os.path.exists(lokalna):
        return lokalna
    return os.path.join(ROOT, "data", nazwa)


CONFIG_PATH = _dane("config.json")   # REFACTOR/data jesli jest, inaczej ../data
STORY_PATH = _dane("story.json")
FRAME_PATH = os.path.join(SCRIPT_DIR, "tiles", "frame.png")  # ramka z przezroczystym otworem
KOSC_PATH = os.path.join(SCRIPT_DIR, "tiles", "dice_roll.png")    # grafika k20 (lokalna nowej wersji)
SAVE_PATH = os.path.join(SCRIPT_DIR, "data", "save.json")    # plik zapisu gry (jeden slot)


# Wymiary grafiki ramki (frame.png). Otwor (przezroczysty srodek) podany jako
# UŁAMKI rozmiaru ramki - dziala niezaleznie od skali okna.
RAMKA_SZER = 1184
RAMKA_WYS = 912
OTW_L = 164 / RAMKA_SZER
OTW_R = 1019 / RAMKA_SZER
OTW_T = 170 / RAMKA_WYS
OTW_B = 749 / RAMKA_WYS


# ── Kolory i czcionki ─────────────────────────────────────────────
TLO = "#1a0f0a"        # brazowe tlo wnetrza (i calego Canvasa)
TLO_PASEK = "#0d0705"  # ciemniejszy pasek (statystyki / rzut)
KOLOR_TEKST = "#e8d5b0"
KOLOR_ZLOTY = "#c8a96e"
KOLOR_HP_OK = "#7ec87e"
KOLOR_SAN_OK = "#7eb8e0"
KOLOR_ZLY = "#e05555"
PRZYCISK_BG = "#2a1a0e"


# ── Stan globalny GUI ─────────────────────────────────────────────
fabula = None
stan = None
root = None
canvas = None

obrazek_ramki = None      # referencja do PhotoImage ramki (zeby gc jej nie zwolnil)
obrazek_kosci = None      # PhotoImage grafiki k20 (wczytany raz, przeskalowany)
obrazki_ref = []          # referencje do obrazkow sceny (czyscimy co odswiezenie)
przyciski_ref = []        # widgety Button osadzone na canvasie (do zniszczenia)

# Geometria okna i otworu (ustawiana w utworz_okno).
SZER_OKNA = RAMKA_SZER
WYS_OKNA = RAMKA_WYS
OX0 = OY0 = OX1 = OY1 = 0   # otwor w pikselach
OCX = OCY = 0               # srodek otworu
OW = OH = 0                 # szer/wys otworu


def zaladuj_dane():
    global fabula, stan
    plik = open(CONFIG_PATH, "r", encoding="utf-8")
    config = json.load(plik)
    plik.close()
    fabula = wczytaj_fabule(STORY_PATH)
    stan = inicjalizuj_stan(config)


# ── Zapis / wczytanie gry (jeden slot: data/save.json) ────────────
def istnieje_zapis():
    return os.path.exists(SAVE_PATH)


def komunikat(tekst, kolor=KOLOR_ZLOTY):
    # Krotki komunikat u dolu otworu, znika sam po ~1.8 s.
    canvas.delete("komunikat")
    canvas.create_text(
        OCX, OY1 - OH * 0.04, text=tekst,
        font=("Georgia", 11, "bold"), fill=kolor, anchor="s", tags="komunikat",
    )
    root.after(1800, lambda: canvas.delete("komunikat"))


def zapisz_gre():
    # Caly stan to slownik typow JSON - zapis to jeden json.dump.
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(stan, f, ensure_ascii=False, indent=2)
        komunikat("Grę zapisano.")
    except OSError:
        komunikat("Nie udało się zapisać.", KOLOR_ZLY)


def wczytaj_gre():
    global fabula, stan
    if not istnieje_zapis():
        komunikat("Brak zapisanej gry.", KOLOR_ZLY)
        return
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            wczytany = json.load(f)
    except (OSError, ValueError):
        komunikat("Plik zapisu jest uszkodzony.", KOLOR_ZLY)
        return

    # Fabula jest statyczna - wczytujemy ja, jesli jeszcze nie ma (np. z menu).
    if fabula is None:
        fabula = wczytaj_fabule(STORY_PATH)

    # Uzupelnij ewentualne brakujace pola (gdyby zapis byl starszy).
    wczytany.setdefault("odwiedzone", [])
    wczytany.setdefault("ekwipunek", [])
    wczytany["ostatni_rzut"] = None
    stan = wczytany

    odswiez_scene()
    komunikat("Wczytano zapisaną grę.")


# ── Pomocnicze: czyszczenie i utrzymanie ramki na wierzchu ────────
def wyczysc_kontent():
    # Usuwa wszystkie elementy tresci (oznaczone tagiem "kontent")
    # oraz osadzone przyciski. Ramka (tag "ramka") zostaje.
    global obrazki_ref, przyciski_ref
    canvas.delete("kontent")
    canvas.delete("komunikat")
    for b in przyciski_ref:
        b.destroy()
    przyciski_ref = []
    obrazki_ref = []


def ramka_na_wierzch():
    # Ramka ma byc zawsze nad rysowana trescia (tekst, obrazki).
    canvas.tag_raise("ramka")


def wczytaj_obrazek(sciezka, max_w, max_h):
    # Wczytuje PNG i w razie potrzeby pomniejsza calkowitym subsample,
    # tak by zmiescil sie w max_w x max_h. Zwraca PhotoImage lub None.
    if sciezka is None:
        return None
    pelna = sciezka
    if not os.path.isabs(pelna):
        pelna = os.path.join(ROOT, sciezka)   # np. "tiles/camp.png" -> ROOT/tiles/camp.png
    if not os.path.exists(pelna):
        return None
    try:
        img = tk.PhotoImage(file=pelna)
    except tk.TclError:
        return None
    # dobierz wspolczynnik pomniejszenia (1,2,3,...)
    k = 1
    while (img.width() // k) > max_w or (img.height() // k) > max_h:
        k += 1
        if k > 12:
            break
    if k > 1:
        img = img.subsample(k, k)
    return img


# ── Podpowiedzi o efektach wyborow (tryb prezentacji) ─────────────
def opis_efektu(efekt):
    # Zamienia slownik efektu wezla na krotki tekst, np. "Sanity -10",
    # "HP -25", "Sanity +20", "+kieł wilka". Zwraca "" gdy brak efektu.
    if not efekt:
        return ""
    czesci = []
    if "hp" in efekt:
        v = efekt["hp"]
        czesci.append("HP " + ("+" + str(v) if v > 0 else str(v)))
    if "sanity" in efekt:
        v = efekt["sanity"]
        czesci.append("Sanity " + ("+" + str(v) if v > 0 else str(v)))
    if "dodaj_przedmiot" in efekt:
        czesci.append("+" + efekt["dodaj_przedmiot"])
    return ", ".join(czesci)


def _opis_celu(wezel):
    # Opis tego, do czego prowadzi dany wezel: efekt + ewentualne zakonczenie.
    if wezel is None:
        return "dalej"
    ef = opis_efektu(wezel.get("efekt"))
    if wezel.get("zakonczone"):
        koniec = "ZWYCIĘSTWO" if wezel.get("zakonczenie") == "dobry" else "KONIEC GRY"
        if ef:
            return koniec + " (" + ef + ")"
        return koniec
    return ef if ef else "dalej"


def podpowiedz_efektu(wybor):
    # Buduje podpowiedz dla jednego wyboru na podstawie warunku i celow.
    warunek = wybor.get("warunek")
    cel = pobierz_wezel(fabula, wybor.get("cel"))

    if "cel_porazka" in wybor:
        celp = pobierz_wezel(fabula, wybor["cel_porazka"])
        if warunek and warunek.get("rzut_koscia"):
            test = "rzut k20 >= " + str(warunek.get("prog", 10))
        elif warunek and "min_sanity" in warunek:
            test = "wymaga Sanity >= " + str(warunek["min_sanity"])
        elif warunek and "min_hp" in warunek:
            test = "wymaga HP >= " + str(warunek["min_hp"])
        else:
            test = "test"
        return test + "   |   sukces: " + _opis_celu(cel) + "   |   porażka: " + _opis_celu(celp)

    # wybor bez progu porazki
    czesci = []
    if warunek and "min_sanity" in warunek:
        czesci.append("wymaga Sanity >= " + str(warunek["min_sanity"]))
    if warunek and "min_hp" in warunek:
        czesci.append("wymaga HP >= " + str(warunek["min_hp"]))
    opis = _opis_celu(cel)
    if opis and opis != "dalej":
        czesci.append(opis)
    if not czesci:
        return "bez zmian"
    return "   ".join(czesci)


# ── Ekran menu ────────────────────────────────────────────────────
def pokaz_menu():
    wyczysc_kontent()

    canvas.create_text(
        OCX, OY0 + OH * 0.30, text="CIEN NAD ARKHAM",
        font=("Georgia", 26, "bold"), fill=KOLOR_ZLOTY, tags="kontent",
    )
    canvas.create_text(
        OCX, OY0 + OH * 0.40, text="Tekstowe RPG w klimacie Cthulhu",
        font=("Georgia", 12, "italic"), fill="#888", tags="kontent",
    )

    b_start = tk.Button(
        canvas, text="NOWA GRA", font=("Georgia", 13, "bold"),
        bg="#4a2a1e", fg=KOLOR_TEKST, relief="flat", width=18, height=2,
        command=nowa_gra,
    )
    canvas.create_window(OCX, OY0 + OH * 0.53, window=b_start, tags="kontent")
    przyciski_ref.append(b_start)

    # Kontynuuj - aktywne tylko gdy istnieje zapis.
    b_kont = tk.Button(
        canvas, text="KONTYNUUJ", font=("Georgia", 12, "bold"),
        bg="#3a2418", fg=KOLOR_TEKST, relief="flat", width=18, height=2,
        command=wczytaj_gre,
    )
    if not istnieje_zapis():
        b_kont.config(state="disabled", fg="#6b5d4a")
    canvas.create_window(OCX, OY0 + OH * 0.65, window=b_kont, tags="kontent")
    przyciski_ref.append(b_kont)

    b_wyjscie = tk.Button(
        canvas, text="WYJSCIE", font=("Georgia", 11),
        bg=PRZYCISK_BG, fg="#888", relief="flat", width=18, height=2,
        command=root.quit,
    )
    canvas.create_window(OCX, OY0 + OH * 0.77, window=b_wyjscie, tags="kontent")
    przyciski_ref.append(b_wyjscie)

    ramka_na_wierzch()


def nowa_gra():
    zaladuj_dane()
    odswiez_scene()


# ── Ekran gry ─────────────────────────────────────────────────────
def odswiez_scene():
    wyczysc_kontent()

    wezel = pobierz_wezel(fabula, stan["obecny_wezel"])

    pad = OW * 0.05
    vpad = OH * 0.04

    # ── Gorny pasek: HP / Sanity / Ekwipunek - WYSRODKOWANE ──
    # (wysrodkowane, zeby nie chowaly sie za ozdobami ramki przy krawedziach)
    kolor_hp = KOLOR_ZLY if stan["hp"] < 30 else KOLOR_HP_OK
    kolor_san = KOLOR_ZLY if stan["sanity"] < 30 else KOLOR_SAN_OK
    canvas.create_text(
        OCX - OW * 0.02, OY0 + vpad, text="HP: " + str(stan["hp"]),
        font=("Georgia", 12, "bold"), fill=kolor_hp, anchor="e", tags="kontent",
    )
    canvas.create_text(
        OCX + OW * 0.02, OY0 + vpad, text="Sanity: " + str(stan["sanity"]),
        font=("Georgia", 12, "bold"), fill=kolor_san, anchor="w", tags="kontent",
    )

    if len(stan["ekwipunek"]) == 0:
        tekst_ekw = "Ekwipunek: (pusty)"
    else:
        tekst_ekw = "Ekwipunek: " + ", ".join(stan["ekwipunek"])
    canvas.create_text(
        OCX, OY0 + vpad + OH * 0.05, text=tekst_ekw,
        font=("Georgia", 10, "italic"), fill="#aaa", anchor="n", tags="kontent",
    )

    # Przycisk Menu (prawy gorny rog otworu)
    b_menu = tk.Button(
        canvas, text="Menu", font=("Georgia", 10),
        bg=PRZYCISK_BG, fg="#888", relief="flat", command=pokaz_menu,
    )
    canvas.create_window(OX1 - pad, OY0 + vpad, window=b_menu, anchor="ne", tags="kontent")
    przyciski_ref.append(b_menu)

    # Zapis / wczytanie (lewy gorny rog otworu)
    b_zapisz = tk.Button(
        canvas, text="Zapisz", font=("Georgia", 10),
        bg=PRZYCISK_BG, fg="#c8b48a", relief="flat", command=zapisz_gre,
    )
    canvas.create_window(OX0 + pad, OY0 + vpad, window=b_zapisz, anchor="nw", tags="kontent")
    przyciski_ref.append(b_zapisz)

    b_wczytaj = tk.Button(
        canvas, text="Wczytaj", font=("Georgia", 10),
        bg=PRZYCISK_BG, fg="#c8b48a", relief="flat", command=wczytaj_gre,
    )
    canvas.create_window(OX0 + pad, OY0 + vpad + OH * 0.05, window=b_wczytaj, anchor="nw", tags="kontent")
    przyciski_ref.append(b_wczytaj)

    # ── Tresc sceny ──
    y = OY0 + OH * 0.13

    img = wczytaj_obrazek(wezel.get("obrazek"), int(OW * 0.6), int(OH * 0.26))
    if img is not None:
        obrazki_ref.append(img)
        canvas.create_image(OCX, y, image=img, anchor="n", tags="kontent")
        y += img.height() + OH * 0.02

    item_tekst = canvas.create_text(
        OCX, y, text=wezel["tekst"], width=OW - 2 * pad,
        font=("Georgia", 12), fill=KOLOR_TEKST, anchor="n", justify="left",
        tags="kontent",
    )
    bbox = canvas.bbox(item_tekst)
    if bbox is not None:
        y = bbox[3] + OH * 0.025

    # ── Koniec gry albo przyciski wyborow (podpowiedz o efekcie NA przycisku) ──
    if czy_koniec(wezel):
        ekran_koncowy(wezel.get("zakonczenie", "dobry"))
    elif stan["hp"] <= 0 or stan["sanity"] <= 0:
        ekran_koncowy("zly")
    else:
        for wybor in wezel["wybory"]:
            etykieta = wybor["tekst"] + "\n( " + podpowiedz_efektu(wybor) + " )"
            b = tk.Button(
                canvas, text=etykieta, font=("Georgia", 11),
                bg=PRZYCISK_BG, fg=KOLOR_TEKST, relief="flat",
                justify="center", wraplength=int(OW - 2 * pad),
                command=lambda w=wybor: obsluz_wybor(w),
            )
            canvas.create_window(OCX, y, window=b, anchor="n",
                                 width=int(OW - 2 * pad), tags="kontent")
            przyciski_ref.append(b)
            canvas.update_idletasks()
            y += b.winfo_reqheight() + OH * 0.018

        # Grafika kosci POD wszystkimi przyciskami + wynik rzutu - gdy nastapil rzut
        rzut = stan.get("ostatni_rzut")
        if rzut is not None and obrazek_kosci is not None:
            ky = y + OH * 0.015
            canvas.create_image(OCX, ky, image=obrazek_kosci, anchor="n", tags="kontent")
            kol = KOLOR_HP_OK if rzut["sukces"] else KOLOR_ZLY
            verdykt = "SUKCES" if rzut["sukces"] else "PORAŻKA"
            canvas.create_text(
                OCX, ky + obrazek_kosci.height() + 6,
                text="Rzut k20: " + str(rzut["wynik"]) +
                     "   /   prog " + str(rzut["prog"]) + "   ->   " + verdykt,
                font=("Georgia", 12, "bold"), fill=kol, anchor="n", tags="kontent",
            )

    stan["ostatni_rzut"] = None
    ramka_na_wierzch()


def obsluz_wybor(wybor):
    wykonaj_wybor(fabula, wybor, stan)
    odswiez_scene()


def ekran_koncowy(typ):
    # Wywolywane z wnetrza odswiez_scene - dorysowuje naglowek i przyciski
    # konca gry. Nie czysci tresci (chcemy zostawic tekst koncowej sceny).
    if typ == "dobry":
        naglowek = "ZWYCIESTWO"
        kolor = KOLOR_HP_OK
    else:
        naglowek = "KONIEC GRY"
        kolor = KOLOR_ZLY

    y = OY1 - OH * 0.22
    canvas.create_text(
        OCX, y, text=naglowek, font=("Georgia", 18, "bold"),
        fill=kolor, anchor="n", tags="kontent",
    )

    b_znowu = tk.Button(
        canvas, text="Zagraj ponownie", font=("Georgia", 11),
        bg=PRZYCISK_BG, fg=KOLOR_TEKST, relief="flat", width=24,
        command=nowa_gra,
    )
    canvas.create_window(OCX, y + OH * 0.07, window=b_znowu, anchor="n", tags="kontent")
    przyciski_ref.append(b_znowu)

    b_menu = tk.Button(
        canvas, text="Wroc do menu", font=("Georgia", 11),
        bg=PRZYCISK_BG, fg=KOLOR_TEKST, relief="flat", width=24,
        command=pokaz_menu,
    )
    canvas.create_window(OCX, y + OH * 0.14, window=b_menu, anchor="n", tags="kontent")
    przyciski_ref.append(b_menu)


# ── Budowa okna ───────────────────────────────────────────────────
def utworz_okno():
    global root, canvas, obrazek_ramki, obrazek_kosci
    global SZER_OKNA, WYS_OKNA, OX0, OY0, OX1, OY1, OCX, OCY, OW, OH

    root = tk.Tk()
    root.title("Cien nad Arkham")
    root.configure(bg="#000000")

    # Wczytanie ramki. Na malych ekranach pomniejszamy ja 2x.
    obrazek_ramki = None
    if os.path.exists(FRAME_PATH):
        try:
            obrazek_ramki = tk.PhotoImage(file=FRAME_PATH)
        except tk.TclError:
            obrazek_ramki = None

    szer_ekranu = root.winfo_screenwidth()
    wys_ekranu = root.winfo_screenheight()

    if szer_ekranu < 1240 or wys_ekranu < 1000:
        if obrazek_ramki is not None:
            obrazek_ramki = obrazek_ramki.subsample(2, 2)
        SZER_OKNA = RAMKA_SZER // 2
        WYS_OKNA = RAMKA_WYS // 2
    else:
        SZER_OKNA = RAMKA_SZER
        WYS_OKNA = RAMKA_WYS

    root.geometry(str(SZER_OKNA) + "x" + str(WYS_OKNA))

    # Otwor w pikselach (wg ulamkow OTW_*)
    OX0 = OTW_L * SZER_OKNA
    OX1 = OTW_R * SZER_OKNA
    OY0 = OTW_T * WYS_OKNA
    OY1 = OTW_B * WYS_OKNA
    OCX = (OX0 + OX1) / 2
    OCY = (OY0 + OY1) / 2
    OW = OX1 - OX0
    OH = OY1 - OY0

    # Grafika k20 - wczytana raz i przeskalowana do ~18% wysokosci otworu.
    obrazek_kosci = None
    if os.path.exists(KOSC_PATH):
        try:
            dk = tk.PhotoImage(file=KOSC_PATH)
            k = 1
            while dk.height() // k > OH * 0.22:
                k += 1
                if k > 12:
                    break
            if k > 1:
                dk = dk.subsample(k, k)
            obrazek_kosci = dk
        except tk.TclError:
            obrazek_kosci = None

    canvas = tk.Canvas(
        root, width=SZER_OKNA, height=WYS_OKNA,
        bg=TLO, highlightthickness=0, borderwidth=0,
    )
    canvas.pack(fill="both", expand=True)

    # Ramka na wierzchu (jej przezroczysty srodek pokazuje brazowe tlo Canvasa)
    if obrazek_ramki is not None:
        canvas.create_image(0, 0, image=obrazek_ramki, anchor="nw", tags="ramka")

    pokaz_menu()
    return root


if __name__ == "__main__":
    okno = utworz_okno()
    okno.mainloop()
