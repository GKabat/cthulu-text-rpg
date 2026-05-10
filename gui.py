# gui.py
# Proste okno gry oparte na tkinter (standardowa biblioteka Pythona).
# Wyswietla obrazek sceny, tekst, statystyki i przyciski wyborow.
# Po rzucie kostka pokazuje dodatkowo grafike kosci i wynik rzutu.

import json
import os
import tkinter as tk

from engine import wczytaj_fabule, pobierz_wezel, wykonaj_wybor, czy_koniec
from game_state import inicjalizuj_stan


CONFIG_PATH = "data/config.json"
STORY_PATH = "data/story.json"
DICE_PATH = "tiles/dice_roll.png"


# Zmienne globalne GUI - wspoldzielone miedzy funkcjami.
fabula = None
stan = None
root = None
ramka_menu = None
ramka_gra = None
ramka_rzut = None
etykieta_obrazka = None
etykieta_kosci = None
etykieta_rzut_tekst = None
etykieta_tekst = None
etykieta_hp = None
etykieta_sanity = None
ramka_wyborow = None
biezacy_obrazek = None  # zeby Tk nie zwolnil PhotoImage przez garbage collector
obrazek_kosci = None


def zaladuj_dane():
    # Wczytuje config i fabule, tworzy nowy stan gry.
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
    # Zielony gdy dobrze, czerwony gdy malo.
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


def wyswietl_obrazek(sciezka):
    # Wczytuje PNG z dysku. Tkinter natywnie obsluguje PNG od Pythona 3.9.
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
            # zmniejsz grafike (oryginal jest dluzy) - subsample 3x
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
            wraplength=600,
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
    wyswietl_rzut(stan.get("ostatni_rzut"))

    # WAZNE: najpierw sprawdzamy flage zakonczone wezla.
    # Dzieki temu wezly konczace gre fabularnie (np. atak_potwora z hp -100,
    # final_szalenstwo z sanity -100) pokazuja swoj wlasny tekst i obrazek
    # zanim zadziala fallback przez 0 HP / 0 Sanity.
    if czy_koniec(wezel):
        typ = wezel.get("zakonczenie", "dobry")
        ekran_koncowy(typ)
    elif stan["hp"] <= 0 or stan["sanity"] <= 0:
        # Fallback gdyby gracz utracil wszystko poza wezlem zakonczeniowym.
        ekran_koncowy("zly")
    else:
        wyswietl_wybory(wezel["wybory"])

    # Czyscimy informacje o rzucie - ma zostac pokazana tylko raz.
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
    global root, ramka_menu, ramka_gra, ramka_rzut
    global etykieta_obrazka, etykieta_kosci, etykieta_rzut_tekst
    global etykieta_tekst, etykieta_hp, etykieta_sanity, ramka_wyborow

    root = tk.Tk()
    root.title("Cien nad Arkham")
    root.geometry("820x780")
    root.configure(bg="#1a0f0a")

    # ── Menu glowne ──────────────────────────────────────────────
    ramka_menu = tk.Frame(root, bg="#1a0f0a")

    tk.Label(
        ramka_menu, text="CIEN NAD ARKHAM",
        font=("Georgia", 26, "bold"),
        bg="#1a0f0a", fg="#c8a96e",
    ).pack(pady=80)

    tk.Label(
        ramka_menu, text="Tekstowe RPG w klimacie Cthulhu",
        font=("Georgia", 12, "italic"),
        bg="#1a0f0a", fg="#888",
    ).pack(pady=10)

    tk.Button(
        ramka_menu, text="START",
        font=("Georgia", 13, "bold"),
        bg="#4a2a1e", fg="#e8d5b0", relief="flat",
        width=20, height=2,
        command=nowa_gra,
    ).pack(pady=20)

    tk.Button(
        ramka_menu, text="WYJSCIE",
        font=("Georgia", 11),
        bg="#2a1a0e", fg="#888", relief="flat",
        width=20, height=2,
        command=root.quit,
    ).pack(pady=4)

    # ── Ekran gry ────────────────────────────────────────────────
    ramka_gra = tk.Frame(root, bg="#1a0f0a")

    ramka_stat = tk.Frame(ramka_gra, bg="#0d0705")
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

    # Obrazek sceny
    etykieta_obrazka = tk.Label(ramka_gra, bg="#1a0f0a")

    # Ramka rzutu (kosci + tekst). Pack/pack_forget zalezy od stanu.
    ramka_rzut = tk.Frame(ramka_gra, bg="#0d0705")
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
        ramka_gra, text="",
        font=("Georgia", 12),
        bg="#1a0f0a", fg="#e8d5b0",
        wraplength=740, justify="left", anchor="w",
    )
    etykieta_tekst.pack(fill="x", padx=20, pady=10)

    tk.Frame(ramka_gra, bg="#3a2a1e", height=1).pack(fill="x", padx=20, pady=4)

    # Przyciski wyborow
    ramka_wyborow = tk.Frame(ramka_gra, bg="#1a0f0a")
    ramka_wyborow.pack(fill="both", expand=True, pady=10)

    ramka_menu.pack(fill="both", expand=True)
    return root


if __name__ == "__main__":
    okno = utworz_okno()
    okno.mainloop()
