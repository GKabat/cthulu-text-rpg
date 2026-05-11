# gui.py
# Proste okno gry oparte na tkinter (standardowa biblioteka Pythona).
# Wyswietla obrazek sceny, tekst, statystyki, ekwipunek i przyciski wyborow.
# Po rzucie kostka pokazuje dodatkowo grafike kosci i wynik rzutu.
# Jako tlo ekranu gry uzywa grafiki ramki (tiles/frame.png).

import json
import os
import tkinter as tk

from engine import wczytaj_fabule, pobierz_wezel, wykonaj_wybor, czy_koniec
from game_state import inicjalizuj_stan


CONFIG_PATH = "data/config.json"
STORY_PATH = "data/story.json"
DICE_PATH = "tiles/dice_roll.png"
FRAME_PATH = "tiles/frame.png"

# Grafika ramki ma wymiary 1184x912 - okno dopasowane 1:1.
SZER_OKNA = 1184
WYS_OKNA = 912

# Marginesy wewnetrzne zostawiajace miejsce na ozdobne brzegi ramki.
# Kontent gry mieci sie w obszarze (SZER - 2*MARG_BOK) x (WYS - MARG_GORA - MARG_DOL).
# Wartosci dobrane do tiles/frame.png. Zwieksz jezeli ramka jest cieta.
MARG_GORA = 90
MARG_DOL = 110
MARG_BOK = 130


# Zmienne globalne GUI.
fabula = None
stan = None
root = None
ramka_menu = None
ramka_gra = None
kontent_gra = None
ramka_rzut = None
etykieta_obrazka = None
etykieta_kosci = None
etykieta_rzut_tekst = None
etykieta_tekst = None
etykieta_hp = None
etykieta_sanity = None
etykieta_ekw = None
ramka_wyborow = None

# Trzymamy referencje do obrazkow (zeby Tk nie zwolnil ich przez gc).
biezacy_obrazek = None
obrazek_kosci = None
obrazek_ramki = None

# Szerokosc zawijania tekstu - ustalana w utworz_okno wg rozmiaru kontentu.
WRAPLENGTH_TEKST = 900
WRAPLENGTH_PRZYCISK = 820


def zaladuj_dane():
    global fabula, stan
    plik = open(CONFIG_PATH, "r", encoding="utf-8")
    config = json.load(plik)
    plik.close()
    fabula = wczytaj_fabule(STORY_PATH)
    stan = inicjalizuj_stan(config)


def pokaz_menu():
    ramka_gra.pack_forget()
    ramka_menu.pack(fill="both", expand=True)


def pokaz_gre():
    ramka_menu.pack_forget()
    ramka_gra.pack(fill="both", expand=True)
    odswiez_scene()


def nowa_gra():
    zaladuj_dane()
    pokaz_gre()


def aktualizuj_statystyki(hp, sanity):
    if hp < 30:
        kolor_hp = "#e05555"
    else:
        kolor_hp = "#7ec87e"
    if sanity < 30:
        kolor_sanity = "#e05555"
    else:
        kolor_sanity = "#7eb8e0"
    etykieta_hp.config(text="HP: " + str(hp), fg=kolor_hp)
    etykieta_sanity.config(text="Sanity: " + str(sanity), fg=kolor_sanity)


def aktualizuj_ekwipunek(ekwipunek):
    if len(ekwipunek) == 0:
        etykieta_ekw.config(text="Ekwipunek: (pusty)")
    else:
        etykieta_ekw.config(text="Ekwipunek: " + ", ".join(ekwipunek))


def wyswietl_obrazek(sciezka):
    # Tkinter natywnie obsluguje PNG od Pythona 3.9.
    global biezacy_obrazek
    if sciezka is not None and os.path.exists(sciezka):
        try:
            biezacy_obrazek = tk.PhotoImage(file=sciezka)
            etykieta_obrazka.config(image=biezacy_obrazek)
            etykieta_obrazka.pack(pady=10)
            return
        except tk.TclError:
            pass
    etykieta_obrazka.pack_forget()


def wyswietl_rzut(rzut):
    # Pokazuje grafike kosci i wynik rzutu nad tekstem sceny.
    # rzut: slownik {"wynik": int, "prog": int, "sukces": bool} lub None.
    global obrazek_kosci
    if rzut is None:
        ramka_rzut.pack_forget()
        return

    if os.path.exists(DICE_PATH):
        try:
            obrazek_kosci = tk.PhotoImage(file=DICE_PATH)
            obrazek_kosci = obrazek_kosci.subsample(3, 3)
            etykieta_kosci.config(image=obrazek_kosci)
        except tk.TclError:
            etykieta_kosci.config(image="")
    else:
        etykieta_kosci.config(image="")

    if rzut["sukces"]:
        wynik_txt = "SUKCES"
        kolor = "#7ec87e"
    else:
        wynik_txt = "PORAZKA"
        kolor = "#e05555"

    etykieta_rzut_tekst.config(
        text="Rzut k20: " + str(rzut["wynik"]) +
             "  /  prog: " + str(rzut["prog"]) +
             "  ->  " + wynik_txt,
        fg=kolor,
    )
    ramka_rzut.pack(fill="x", padx=20, pady=4)


def wyswietl_scene(tekst, obrazek):
    etykieta_tekst.config(text=tekst)
    wyswietl_obrazek(obrazek)


def wyswietl_wybory(wybory):
    for widget in ramka_wyborow.winfo_children():
        widget.destroy()

    i = 0
    while i < len(wybory):
        wybor = wybory[i]
        # domyslny argument w lambda zamyka biezaca wartosc wyboru
        przycisk = tk.Button(
            ramka_wyborow,
            text=wybor["tekst"],
            font=("Georgia", 11),
            bg="#2a1a0e", fg="#e8d5b0",
            relief="flat",
            wraplength=WRAPLENGTH_PRZYCISK,
            command=lambda w=wybor: obsluz_wybor(w),
        )
        przycisk.pack(fill="x", padx=20, pady=4)
        i = i + 1


def obsluz_wybor(wybor):
    wykonaj_wybor(fabula, wybor, stan)
    odswiez_scene()


def odswiez_scene():
    id_wezla = stan["obecny_wezel"]
    wezel = pobierz_wezel(fabula, id_wezla)

    wyswietl_scene(wezel["tekst"], wezel.get("obrazek"))
    aktualizuj_statystyki(stan["hp"], stan["sanity"])
    aktualizuj_ekwipunek(stan["ekwipunek"])
    wyswietl_rzut(stan.get("ostatni_rzut"))

    # Najpierw flaga zakonczone - daje wezlowi wlasny tekst i grafike.
    # Dopiero potem fallback przez 0 HP / 0 Sanity.
    if czy_koniec(wezel):
        typ = wezel.get("zakonczenie", "dobry")
        ekran_koncowy(typ)
    elif stan["hp"] <= 0 or stan["sanity"] <= 0:
        ekran_koncowy("zly")
    else:
        wyswietl_wybory(wezel["wybory"])

    # Wynik rzutu pokazujemy tylko raz.
    stan["ostatni_rzut"] = None


def ekran_koncowy(typ):
    for widget in ramka_wyborow.winfo_children():
        widget.destroy()

    if typ == "dobry":
        naglowek = "ZWYCIESTWO"
        kolor = "#7ec87e"
    else:
        naglowek = "KONIEC GRY"
        kolor = "#e05555"

    tk.Label(
        ramka_wyborow, text=naglowek,
        font=("Georgia", 18, "bold"),
        bg="#1a0f0a", fg=kolor,
    ).pack(pady=10)

    tk.Button(
        ramka_wyborow, text="Zagraj ponownie",
        font=("Georgia", 11),
        bg="#2a1a0e", fg="#e8d5b0", relief="flat",
        command=nowa_gra,
    ).pack(fill="x", padx=20, pady=4)

    tk.Button(
        ramka_wyborow, text="Wroc do menu",
        font=("Georgia", 11),
        bg="#2a1a0e", fg="#e8d5b0", relief="flat",
        command=pokaz_menu,
    ).pack(fill="x", padx=20, pady=4)


def utworz_okno():
    global root, ramka_menu, ramka_gra, kontent_gra, ramka_rzut
    global etykieta_obrazka, etykieta_kosci, etykieta_rzut_tekst
    global etykieta_tekst, etykieta_hp, etykieta_sanity, etykieta_ekw, ramka_wyborow
    global obrazek_ramki
    global SZER_OKNA, WYS_OKNA, MARG_GORA, MARG_DOL, MARG_BOK
    global WRAPLENGTH_TEKST, WRAPLENGTH_PRZYCISK

    root = tk.Tk()
    root.title("Cien nad Arkham")
    root.configure(bg="#000000")

    # ── Wczytywanie ramki + dopasowanie do ekranu ────────────────
    # Ramka frame.png ma 1184x912. Na malych ekranach (np. 1366x768)
    # to za duzo - skalujemy 2x w dol przez subsample, co daje 592x456.
    obrazek_ramki = None
    if os.path.exists(FRAME_PATH):
        try:
            obrazek_ramki = tk.PhotoImage(file=FRAME_PATH)
        except tk.TclError:
            obrazek_ramki = None

    szer_ekranu = root.winfo_screenwidth()
    wys_ekranu = root.winfo_screenheight()

    # Jezeli ekran nie pomiesci pelnej ramki (1184x912 + miejsce na pasek
    # zadan i tytul okna), uzywamy wersji zmniejszonej 2x.
    if szer_ekranu < 1240 or wys_ekranu < 1000:
        if obrazek_ramki is not None:
            obrazek_ramki = obrazek_ramki.subsample(2, 2)
        SZER_OKNA = 592
        WYS_OKNA = 456
        MARG_GORA = 70
        MARG_DOL = 70
        MARG_BOK = 80
    else:
        SZER_OKNA = 1184
        WYS_OKNA = 912
        MARG_GORA = 140
        MARG_DOL = 140
        MARG_BOK = 160

    root.geometry(str(SZER_OKNA) + "x" + str(WYS_OKNA))

    szer_kontentu = SZER_OKNA - 2 * MARG_BOK
    wys_kontentu = WYS_OKNA - MARG_GORA - MARG_DOL

    WRAPLENGTH_TEKST = szer_kontentu - 40
    WRAPLENGTH_PRZYCISK = szer_kontentu - 80

    # ── Menu glowne ──────────────────────────────────────────────
    # Tlo = Label z ramka (na dole), kontent_menu Frame na wierzchu
    # przykrywa srodek ramki swoim solidnym bg.
    # UWAGA: Tk nie pozwala polozyc Canvas image NA WIERZCHU widget'ow -
    # create_window jest zawsze rysowane na koncu. Dlatego ramka
    # SIEDZI POD kontentem; marginesy musza byc DUZE, zeby kontent
    # nie zachodzil na ozdoby ramki.
    ramka_menu = tk.Frame(root, bg="#1a0f0a")

    if obrazek_ramki is not None:
        tlo_menu = tk.Label(ramka_menu, image=obrazek_ramki, bg="#1a0f0a", borderwidth=0)
        tlo_menu.place(x=0, y=0)

    kontent_menu = tk.Frame(ramka_menu, bg="#1a0f0a")
    kontent_menu.place(
        x=MARG_BOK, y=MARG_GORA,
        width=szer_kontentu, height=wys_kontentu,
    )

    tk.Label(
        kontent_menu, text="CIEN NAD ARKHAM",
        font=("Georgia", 26, "bold"),
        bg="#1a0f0a", fg="#c8a96e",
    ).place(relx=0.5, rely=0.30, anchor="center")

    tk.Label(
        kontent_menu, text="Tekstowe RPG w klimacie Cthulhu",
        font=("Georgia", 12, "italic"),
        bg="#1a0f0a", fg="#888",
    ).place(relx=0.5, rely=0.40, anchor="center")

    tk.Button(
        kontent_menu, text="START",
        font=("Georgia", 13, "bold"),
        bg="#4a2a1e", fg="#e8d5b0", relief="flat",
        width=18, height=2,
        command=nowa_gra,
    ).place(relx=0.5, rely=0.55, anchor="center")

    tk.Button(
        kontent_menu, text="WYJSCIE",
        font=("Georgia", 11),
        bg="#2a1a0e", fg="#888", relief="flat",
        width=18, height=2,
        command=root.quit,
    ).place(relx=0.5, rely=0.70, anchor="center")

    # ── Ekran gry ────────────────────────────────────────────────
    ramka_gra = tk.Frame(root, bg="#1a0f0a")

    if obrazek_ramki is not None:
        tlo_gra = tk.Label(ramka_gra, image=obrazek_ramki, bg="#1a0f0a", borderwidth=0)
        tlo_gra.place(x=0, y=0)

    kontent_gra = tk.Frame(ramka_gra, bg="#1a0f0a")
    kontent_gra.place(
        x=MARG_BOK, y=MARG_GORA,
        width=szer_kontentu, height=wys_kontentu,
    )

    # Pasek statystyk u gory kontentu
    ramka_stat = tk.Frame(kontent_gra, bg="#0d0705")
    ramka_stat.pack(fill="x")

    etykieta_hp = tk.Label(
        ramka_stat, text="HP: 100",
        font=("Georgia", 12, "bold"),
        bg="#0d0705", fg="#7ec87e",
    )
    etykieta_hp.pack(side="left", padx=20, pady=6)

    etykieta_sanity = tk.Label(
        ramka_stat, text="Sanity: 100",
        font=("Georgia", 12, "bold"),
        bg="#0d0705", fg="#7eb8e0",
    )
    etykieta_sanity.pack(side="left", padx=20, pady=6)

    tk.Button(
        ramka_stat, text="Menu",
        font=("Georgia", 10),
        bg="#2a1a0e", fg="#888", relief="flat",
        command=pokaz_menu,
    ).pack(side="right", padx=10, pady=4)

    # Pasek ekwipunku - ponizej statystyk
    etykieta_ekw = tk.Label(
        kontent_gra, text="Ekwipunek: (pusty)",
        font=("Georgia", 10, "italic"),
        bg="#1a0f0a", fg="#aaa", anchor="w",
    )
    etykieta_ekw.pack(fill="x", padx=20, pady=2)

    # Obrazek sceny (pack/pack_forget zalezy od dostepnosci pliku)
    etykieta_obrazka = tk.Label(kontent_gra, bg="#1a0f0a")

    # Ramka rzutu (kosci + tekst)
    ramka_rzut = tk.Frame(kontent_gra, bg="#0d0705")
    etykieta_kosci = tk.Label(ramka_rzut, bg="#0d0705")
    etykieta_kosci.pack(side="left", padx=10, pady=6)
    etykieta_rzut_tekst = tk.Label(
        ramka_rzut, text="",
        font=("Georgia", 11, "bold"),
        bg="#0d0705", fg="#e8d5b0",
    )
    etykieta_rzut_tekst.pack(side="left", padx=10)

    # Tekst sceny
    etykieta_tekst = tk.Label(
        kontent_gra, text="",
        font=("Georgia", 12),
        bg="#1a0f0a", fg="#e8d5b0",
        wraplength=WRAPLENGTH_TEKST, justify="left", anchor="w",
    )
    etykieta_tekst.pack(fill="x", padx=20, pady=10)

    tk.Frame(kontent_gra, bg="#3a2a1e", height=1).pack(fill="x", padx=20, pady=4)

    # Przyciski wyborow
    ramka_wyborow = tk.Frame(kontent_gra, bg="#1a0f0a")
    ramka_wyborow.pack(fill="both", expand=True, pady=10)

    ramka_menu.pack(fill="both", expand=True)
    return root


if __name__ == "__main__":
    okno = utworz_okno()
    okno.mainloop()
