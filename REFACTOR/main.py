# main.py  (wersja REFACTOR)
# Punkt wejscia nowej wersji gry. Uruchamiac:  python REFACTOR/main.py
# Dane (data/) i grafiki scen (tiles/) sa wspolne ze stara wersja - czytane
# z katalogu glownego projektu. Ramka (tiles/frame.png) jest lokalna dla REFACTOR.

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)


def _dane(nazwa):
    # Dane nowej wersji (REFACTOR/data) maja pierwszenstwo, inaczej wspolne (../data).
    lokalna = os.path.join(SCRIPT_DIR, "data", nazwa)
    if os.path.exists(lokalna):
        return lokalna
    return os.path.join(ROOT, "data", nazwa)


def sprawdz_pliki():
    # Sprawdza czy istnieja wymagane pliki danych.
    wymagane = [_dane("config.json"), _dane("story.json")]
    brakujace = []
    for sciezka in wymagane:
        if not os.path.exists(sciezka):
            brakujace.append(sciezka)
    if len(brakujace) > 0:
        print("BLAD: brakuje plikow:")
        for sciezka in brakujace:
            print("  -", sciezka)
        sys.exit(1)


def uruchom():
    sprawdz_pliki()
    # zeby "from gui import ..." znalazlo gui.py z katalogu REFACTOR
    if SCRIPT_DIR not in sys.path:
        sys.path.insert(0, SCRIPT_DIR)
    from gui import utworz_okno
    print("Uruchamianie Cien nad Arkham (REFACTOR)...")
    okno = utworz_okno()
    okno.mainloop()
    print("Gra zakonczona.")


if __name__ == "__main__":
    uruchom()
