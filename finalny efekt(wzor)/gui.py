# gui.py
# Osoba 4: Programista Interfejsu
# Interfejs graficzny Tkinter podłączony do engine.py i game_state.py

import json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from engine import wczytaj_fabule, pobierz_wezel, wykonaj_wybor, czy_koniec
from game_state import inicjalizuj_stan, pobierz_stan

# ── Stałe ─────────────────────────────────────────────────────────────────────

CONFIG_PATH = "data/config.json"
STORY_PATH  = "data/story.json"
DOMYSLNE_TLO = "assets/tlo.jpg"   # zmień na swoją ścieżkę lub zostaw — kod to obsłuży

# ── Stan globalny GUI ─────────────────────────────────────────────────────────
# Te zmienne są współdzielone między funkcjami GUI

story  = None
state  = None
root   = None
bg_image         = None
scene_image      = None
lbl_tekst        = None
lbl_hp           = None
lbl_sanity       = None
lbl_obrazek      = None
frame_wybory     = None
frame_gra        = None
frame_menu       = None


# ── Inicjalizacja danych ──────────────────────────────────────────────────────

def zaladuj_dane():
    """Wczytuje config.json i story.json, inicjalizuje stan gry."""
    global story, state
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    story = wczytaj_fabule(STORY_PATH)
    state = inicjalizuj_stan(config)


# ── Ekrany ────────────────────────────────────────────────────────────────────

def pokaz_menu():
    """Wyświetla ekran głównego menu."""
    frame_gra.pack_forget()
    frame_menu.pack(fill="both", expand=True)


def pokaz_gre():
    """Przełącza na ekran gry i wyświetla pierwszy węzeł."""
    frame_menu.pack_forget()
    frame_gra.pack(fill="both", expand=True)
    odswiez_scene()


# ── Główna logika GUI ─────────────────────────────────────────────────────────

def odswiez_scene():
    """
    Odświeża wszystkie elementy ekranu gry na podstawie aktualnego węzła.
    Wywołuje się po każdym wyborze gracza.
    """
    node_id = state["obecny_wezel"]
    node    = pobierz_wezel(story, node_id)

    # Tekst sceny
    lbl_tekst.config(text=node["tekst"])

    # Statystyki
    aktualizuj_statystyki(state["hp"], state["sanity"])

    # Obrazek sceny
    wyswietl_obrazek(node.get("obrazek"))

    # Koniec gry
    if czy_koniec(node):
        typ = "dobry" if state["hp"] > 0 and state["sanity"] > 0 else "zły"
        ekran_koncowy(typ, node["tekst"])
        return

    # Przyciski wyborów
    wyswietl_wybory(node.get("wybory", []))


def wyswietl_wybory(lista_wyborow: list):
    """Generuje przyciski dynamicznie na podstawie listy wyborów z węzła."""
    # Usuń stare przyciski
    for widget in frame_wybory.winfo_children():
        widget.destroy()

    for i, choice in enumerate(lista_wyborow):
        tekst_przycisku = choice["tekst"]
        # Zamknięcie zmiennej w lambdzie przez domyślny argument
        btn = tk.Button(
            frame_wybory,
            text=tekst_przycisku,
            font=("Georgia", 12),
            bg="#2a1a0e",
            fg="#e8d5b0",
            activebackground="#4a2a1e",
            activeforeground="white",
            relief="flat",
            padx=20, pady=8,
            wraplength=600,
            command=lambda c=choice: obsluz_wybor(c)
        )
        btn.pack(fill="x", pady=4, padx=20)


def obsluz_wybor(choice: dict):
    """
    Callback wywoływany po kliknięciu przycisku wyboru.
    Przekazuje wybór do silnika, a potem odświeża GUI.
    """
    wykonaj_wybor(story, choice, state)
    odswiez_scene()


def aktualizuj_statystyki(hp: int, sanity: int):
    """Odświeża etykiety HP i Sanity."""
    kolor_hp     = "#e05555" if hp < 30     else "#7ec87e"
    kolor_sanity = "#e05555" if sanity < 30 else "#7eb8e0"
    lbl_hp.config(    text=f"❤ HP: {hp}",         fg=kolor_hp)
    lbl_sanity.config(text=f"🧠 Sanity: {sanity}", fg=kolor_sanity)


def wyswietl_obrazek(sciezka: str | None):
    """Ładuje i wyświetla obrazek sceny. Jeśli brak — ukrywa widget."""
    global scene_image
    if sciezka:
        try:
            img = Image.open(sciezka).resize((400, 250), Image.LANCZOS)
            scene_image = ImageTk.PhotoImage(img)
            lbl_obrazek.config(image=scene_image)
            lbl_obrazek.pack(pady=10)
        except Exception:
            lbl_obrazek.pack_forget()
    else:
        lbl_obrazek.pack_forget()


def ekran_koncowy(typ: str, tekst: str):
    """Wyświetla ekran zakończenia gry (dobry/zły) z opcją powrotu do menu."""
    for widget in frame_wybory.winfo_children():
        widget.destroy()

    kolor = "#7ec87e" if typ == "dobry" else "#e05555"
    naglowek = "🏆 ZWYCIĘSTWO!" if typ == "dobry" else "💀 KONIEC GRY"

    tk.Label(
        frame_wybory,
        text=naglowek,
        font=("Georgia", 18, "bold"),
        bg="#1a0f0a", fg=kolor
    ).pack(pady=10)

    tk.Button(
        frame_wybory,
        text="Zagraj ponownie",
        font=("Georgia", 12),
        bg="#2a1a0e", fg="#e8d5b0",
        relief="flat", padx=20, pady=8,
        command=nowa_gra
    ).pack(pady=6, padx=20, fill="x")

    tk.Button(
        frame_wybory,
        text="Wróć do menu",
        font=("Georgia", 12),
        bg="#2a1a0e", fg="#e8d5b0",
        relief="flat", padx=20, pady=8,
        command=pokaz_menu
    ).pack(pady=6, padx=20, fill="x")


def nowa_gra():
    """Resetuje stan gry i zaczyna od nowa."""
    global state
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    state = inicjalizuj_stan(config)
    pokaz_gre()


# ── Budowa okna ───────────────────────────────────────────────────────────────

def utworz_okno():
    """Inicjalizuje okno Tkinter z layoutem gry."""
    global root, frame_menu, frame_gra
    global lbl_tekst, lbl_hp, lbl_sanity, lbl_obrazek, frame_wybory

    root = tk.Tk()
    root.title("Cień nad Arkham")
    root.geometry("800x700")
    root.configure(bg="#1a0f0a")
    root.resizable(True, True)

    # ── EKRAN MENU ────────────────────────────────────────────────────────────
    frame_menu = tk.Frame(root, bg="#1a0f0a")

    # Tło menu
    try:
        tlo = Image.open(DOMYSLNE_TLO)
        tlo = tlo.resize((800, 700), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(tlo)
        lbl_tlo = tk.Label(frame_menu, image=bg_photo)
        lbl_tlo.image = bg_photo  # zapobiegaj garbage collection
        lbl_tlo.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception:
        pass  # brak tła — szare okno, nic się nie sypie

    tk.Label(
        frame_menu,
        text="CIEŃ NAD ARKHAM",
        font=("Georgia", 28, "bold"),
        bg="#1a0f0a", fg="#c8a96e"
    ).place(relx=0.5, rely=0.35, anchor="center")

    tk.Label(
        frame_menu,
        text="Tekstowe RPG w klimacie Call of Cthulhu",
        font=("Georgia", 12, "italic"),
        bg="#1a0f0a", fg="#888"
    ).place(relx=0.5, rely=0.44, anchor="center")

    tk.Button(
        frame_menu,
        text="START GRY",
        font=("Georgia", 14, "bold"),
        bg="#4a2a1e", fg="#e8d5b0",
        activebackground="#6a3a2e",
        relief="flat", width=20, height=2,
        command=lambda: [zaladuj_dane(), pokaz_gre()]
    ).place(relx=0.5, rely=0.60, anchor="center")

    tk.Button(
        frame_menu,
        text="WYJŚCIE",
        font=("Georgia", 12),
        bg="#2a1a0e", fg="#888",
        activebackground="#3a2a1e",
        relief="flat", width=20, height=2,
        command=root.quit
    ).place(relx=0.5, rely=0.72, anchor="center")

    # ── EKRAN GRY ─────────────────────────────────────────────────────────────
    frame_gra = tk.Frame(root, bg="#1a0f0a")

    # Pasek statystyk (góra)
    frame_stats = tk.Frame(frame_gra, bg="#0d0705", pady=6)
    frame_stats.pack(fill="x")

    lbl_hp = tk.Label(
        frame_stats, text="❤ HP: 100",
        font=("Georgia", 12, "bold"),
        bg="#0d0705", fg="#7ec87e"
    )
    lbl_hp.pack(side="left", padx=20)

    lbl_sanity = tk.Label(
        frame_stats, text="🧠 Sanity: 100",
        font=("Georgia", 12, "bold"),
        bg="#0d0705", fg="#7eb8e0"
    )
    lbl_sanity.pack(side="left", padx=20)

    tk.Button(
        frame_stats, text="Menu",
        font=("Georgia", 10),
        bg="#2a1a0e", fg="#888",
        relief="flat", padx=10,
        command=pokaz_menu
    ).pack(side="right", padx=10)

    # Obrazek sceny
    lbl_obrazek = tk.Label(frame_gra, bg="#1a0f0a")
    # (pack/pack_forget wywoływany dynamicznie w wyswietl_obrazek)

    # Pole tekstu sceny
    frame_tekst = tk.Frame(frame_gra, bg="#1a0f0a", padx=20, pady=10)
    frame_tekst.pack(fill="x")

    lbl_tekst = tk.Label(
        frame_tekst,
        text="",
        font=("Georgia", 13),
        bg="#1a0f0a", fg="#e8d5b0",
        wraplength=720,
        justify="left",
        anchor="w"
    )
    lbl_tekst.pack(fill="x")

    # Separator
    tk.Frame(frame_gra, bg="#3a2a1e", height=1).pack(fill="x", padx=20, pady=4)

    # Przyciski wyborów
    frame_wybory = tk.Frame(frame_gra, bg="#1a0f0a")
    frame_wybory.pack(fill="both", expand=True, pady=10)

    # Pokaż menu na start
    frame_menu.pack(fill="both", expand=True)

    return root


# ── Punkt wejścia ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    okno = utworz_okno()
    okno.mainloop()