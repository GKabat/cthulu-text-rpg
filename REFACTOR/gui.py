# gui.py - okno gry zrobione na tkinter
# Rysujemy wszystko na jednym Canvasie. Tlo jest brazowe na cale okno,
# a ramka (frame.png ma przezroczysty srodek) idzie na wierzch, zeby
# tresc gry siedziala w srodku ramki.

import json
import os
import tkinter as tk

from engine import wczytaj_fabule, pobierz_wezel, wykonaj_wybor, czy_koniec
from game_state import inicjalizuj_stan


# sciezki - liczone od miejsca tego pliku, zeby dzialalo z kazdego katalogu
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)

CONFIG_PATH = os.path.join(SCRIPT_DIR, "data", "config.json")
STORY_PATH = os.path.join(SCRIPT_DIR, "data", "story.json")
FRAME_PATH = os.path.join(SCRIPT_DIR, "tiles", "frame.png")
KOSC_PATH = os.path.join(SCRIPT_DIR, "tiles", "dice_roll.png")
SAVE_PATH = os.path.join(SCRIPT_DIR, "data", "save.json")   # zapis gry, jeden slot


# rozmiar ramki frame.png i gdzie ma ona przezroczysty otwor (jako ulamki,
# zeby dzialalo tez jak okno jest pomniejszone)
RAMKA_SZER = 1184
RAMKA_WYS = 912
OTW_L = 164 / RAMKA_SZER
OTW_R = 1019 / RAMKA_SZER
OTW_T = 170 / RAMKA_WYS
OTW_B = 749 / RAMKA_WYS


# kolory
TLO = "#1a0f0a"
KOLOR_TEKST = "#e8d5b0"
KOLOR_ZLOTY = "#c8a96e"
KOLOR_HP_OK = "#7ec87e"
KOLOR_SAN_OK = "#7eb8e0"
KOLOR_ZLY = "#e05555"
PRZYCISK_BG = "#2a1a0e"


# zmienne globalne
fabula = None
stan = None
root = None
canvas = None

obrazek_ramki = None   # trzymamy referencje zeby tkinter nie skasowal obrazka
obrazek_kosci = None
obrazki_ref = []       # obrazki sceny - czyscimy przy kazdym odswiezeniu
przyciski_ref = []     # przyciski na canvasie - do skasowania

# geometria okna i otworu - ustawiana w utworz_okno
SZER_OKNA = RAMKA_SZER
WYS_OKNA = RAMKA_WYS
OX0 = OY0 = OX1 = OY1 = 0
OCX = OCY = 0
OW = OH = 0


def zaladuj_dane():
    global fabula, stan
    plik = open(CONFIG_PATH, "r", encoding="utf-8")
    config = json.load(plik)
    plik.close()
    fabula = wczytaj_fabule(STORY_PATH)
    stan = inicjalizuj_stan(config)


# zapis i wczytanie gry
def istnieje_zapis():
    return os.path.exists(SAVE_PATH)


def komunikat(tekst, kolor=KOLOR_ZLOTY):
    # maly napis na dole, sam znika po chwili
    canvas.delete("komunikat")
    canvas.create_text(
        OCX, OY1 - OH * 0.04, text=tekst,
        font=("Georgia", 11, "bold"), fill=kolor, anchor="s", tags="komunikat",
    )
    root.after(1800, lambda: canvas.delete("komunikat"))


def zapisz_gre():
    # caly stan to zwykly slownik wiec wystarczy json.dump
    try:
        f = open(SAVE_PATH, "w", encoding="utf-8")
        json.dump(stan, f, ensure_ascii=False, indent=2)
        f.close()
        komunikat("Grę zapisano.")
    except OSError:
        komunikat("Nie udało się zapisać.", KOLOR_ZLY)


def wczytaj_gre():
    global fabula, stan
    if not istnieje_zapis():
        komunikat("Brak zapisanej gry.", KOLOR_ZLY)
        return
    try:
        f = open(SAVE_PATH, "r", encoding="utf-8")
        wczytany = json.load(f)
        f.close()
    except (OSError, ValueError):
        komunikat("Plik zapisu jest uszkodzony.", KOLOR_ZLY)
        return

    # jak wczytujemy z menu to fabuly jeszcze nie ma, trzeba ja doczytac
    if fabula is None:
        fabula = wczytaj_fabule(STORY_PATH)

    # na wszelki wypadek gdyby zapis byl stary i czegos brakowalo
    if "odwiedzone" not in wczytany:
        wczytany["odwiedzone"] = []
    if "ekwipunek" not in wczytany:
        wczytany["ekwipunek"] = []
    wczytany["ostatni_rzut"] = None
    stan = wczytany

    odswiez_scene()
    komunikat("Wczytano zapisaną grę.")


def wyczysc_kontent():
    # kasuje wszystko co narysowane (tag kontent) i przyciski, ramka zostaje
    global obrazki_ref, przyciski_ref
    canvas.delete("kontent")
    canvas.delete("komunikat")
    for b in przyciski_ref:
        b.destroy()
    przyciski_ref = []
    obrazki_ref = []


def ramka_na_wierzch():
    canvas.tag_raise("ramka")


def wczytaj_obrazek(sciezka, max_w, max_h):
    # wczytuje png i jak za duzy to pomniejsza przez subsample
    if sciezka is None:
        return None
    pelna = sciezka
    if not os.path.isabs(pelna):
        pelna = os.path.join(ROOT, sciezka)   # np "tiles/camp.png"
    if not os.path.exists(pelna):
        return None
    try:
        img = tk.PhotoImage(file=pelna)
    except tk.TclError:
        return None
    k = 1
    while (img.width() // k) > max_w or (img.height() // k) > max_h:
        k = k + 1
        if k > 12:
            break
    if k > 1:
        img = img.subsample(k, k)
    return img


# podpowiedzi co robi dany wybor (pokazujemy je na przyciskach)
def opis_efektu(efekt):
    # robi tekst typu "Sanity -10", "HP -25", "+kieł wilka"
    if not efekt:
        return ""
    czesci = []
    if "hp" in efekt:
        v = efekt["hp"]
        if v > 0:
            czesci.append("HP +" + str(v))
        else:
            czesci.append("HP " + str(v))
    if "sanity" in efekt:
        v = efekt["sanity"]
        if v > 0:
            czesci.append("Sanity +" + str(v))
        else:
            czesci.append("Sanity " + str(v))
    if "dodaj_przedmiot" in efekt:
        czesci.append("+" + efekt["dodaj_przedmiot"])
    return ", ".join(czesci)


def opis_celu(wezel):
    # co czeka w wezle do ktorego prowadzi wybor
    if wezel is None:
        return "dalej"
    ef = opis_efektu(wezel.get("efekt"))
    if wezel.get("zakonczone"):
        if wezel.get("zakonczenie") == "dobry":
            koniec = "ZWYCIĘSTWO"
        else:
            koniec = "KONIEC GRY"
        if ef:
            return koniec + " (" + ef + ")"
        return koniec
    if ef:
        return ef
    return "dalej"


def podpowiedz_efektu(wybor):
    warunek = wybor.get("warunek")
    cel = pobierz_wezel(fabula, wybor.get("cel"))

    # wybor z testem (rzut/warunek) i osobnym celem porazki
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
        return test + "   |   sukces: " + opis_celu(cel) + "   |   porażka: " + opis_celu(celp)

    # zwykly wybor bez progu porazki
    czesci = []
    if warunek and "min_sanity" in warunek:
        czesci.append("wymaga Sanity >= " + str(warunek["min_sanity"]))
    if warunek and "min_hp" in warunek:
        czesci.append("wymaga HP >= " + str(warunek["min_hp"]))
    opis = opis_celu(cel)
    if opis and opis != "dalej":
        czesci.append(opis)
    if not czesci:
        return "bez zmian"
    return "   ".join(czesci)


# ekran menu
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

    # kontynuuj dziala tylko jak jest zapis, inaczej go wylaczamy
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


# ekran gry - rysuje aktualna scene
def odswiez_scene():
    wyczysc_kontent()

    wezel = pobierz_wezel(fabula, stan["obecny_wezel"])

    pad = OW * 0.05
    vpad = OH * 0.04

    # gorny pasek: HP, Sanity, ekwipunek. Dajemy na srodek zeby nie chowaly
    # sie za ramka po bokach.
    if stan["hp"] < 30:
        kolor_hp = KOLOR_ZLY
    else:
        kolor_hp = KOLOR_HP_OK
    if stan["sanity"] < 30:
        kolor_san = KOLOR_ZLY
    else:
        kolor_san = KOLOR_SAN_OK

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

    # przycisk menu w prawym gornym rogu
    b_menu = tk.Button(
        canvas, text="Menu", font=("Georgia", 10),
        bg=PRZYCISK_BG, fg="#888", relief="flat", command=pokaz_menu,
    )
    canvas.create_window(OX1 - pad, OY0 + vpad, window=b_menu, anchor="ne", tags="kontent")
    przyciski_ref.append(b_menu)

    # zapisz/wczytaj w lewym gornym rogu
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

    # tresc sceny zaczynamy ponizej gornego paska
    y = OY0 + OH * 0.13

    img = wczytaj_obrazek(wezel.get("obrazek"), int(OW * 0.6), int(OH * 0.26))
    if img is not None:
        obrazki_ref.append(img)
        canvas.create_image(OCX, y, image=img, anchor="n", tags="kontent")
        y = y + img.height() + OH * 0.02

    item_tekst = canvas.create_text(
        OCX, y, text=wezel["tekst"], width=OW - 2 * pad,
        font=("Georgia", 12), fill=KOLOR_TEKST, anchor="n", justify="left",
        tags="kontent",
    )
    # bbox daje rzeczywista wysokosc tekstu, zeby wiedziec gdzie dalej rysowac
    bbox = canvas.bbox(item_tekst)
    if bbox is not None:
        y = bbox[3] + OH * 0.025

    # albo koniec gry albo przyciski wyborow
    if czy_koniec(wezel):
        ekran_koncowy(wezel.get("zakonczenie", "dobry"))
    elif stan["hp"] <= 0 or stan["sanity"] <= 0:
        ekran_koncowy("zly")
    else:
        for wybor in wezel["wybory"]:
            # do tekstu przycisku doklejamy podpowiedz co robi ten wybor
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
            y = y + b.winfo_reqheight() + OH * 0.018

        # jak byl rzut koscia to pod przyciskami pokazujemy kosc i wynik
        rzut = stan.get("ostatni_rzut")
        if rzut is not None and obrazek_kosci is not None:
            ky = y + OH * 0.015
            canvas.create_image(OCX, ky, image=obrazek_kosci, anchor="n", tags="kontent")
            if rzut["sukces"]:
                kol = KOLOR_HP_OK
                verdykt = "SUKCES"
            else:
                kol = KOLOR_ZLY
                verdykt = "PORAŻKA"
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
    # naglowek konca + przyciski. Tekst koncowej sceny zostaje (nie czyscimy go).
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


def utworz_okno():
    global root, canvas, obrazek_ramki, obrazek_kosci
    global SZER_OKNA, WYS_OKNA, OX0, OY0, OX1, OY1, OCX, OCY, OW, OH

    root = tk.Tk()
    root.title("Cien nad Arkham")
    root.configure(bg="#000000")

    # wczytujemy ramke, na malych ekranach robimy ja 2x mniejsza
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

    # przeliczamy otwor ramki na piksele
    OX0 = OTW_L * SZER_OKNA
    OX1 = OTW_R * SZER_OKNA
    OY0 = OTW_T * WYS_OKNA
    OY1 = OTW_B * WYS_OKNA
    OCX = (OX0 + OX1) / 2
    OCY = (OY0 + OY1) / 2
    OW = OX1 - OX0
    OH = OY1 - OY0

    # kosc wczytujemy raz i od razu skalujemy
    obrazek_kosci = None
    if os.path.exists(KOSC_PATH):
        try:
            dk = tk.PhotoImage(file=KOSC_PATH)
            k = 1
            while dk.height() // k > OH * 0.22:
                k = k + 1
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

    # ramka na wierzch, jej przezroczysty srodek pokazuje brazowe tlo
    if obrazek_ramki is not None:
        canvas.create_image(0, 0, image=obrazek_ramki, anchor="nw", tags="ramka")

    pokaz_menu()
    return root


if __name__ == "__main__":
    okno = utworz_okno()
    okno.mainloop()
