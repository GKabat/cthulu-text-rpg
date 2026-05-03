# main.py
# Punkt wejscia gry. Uruchamia okno GUI.

import os
import sys


def sprawdz_pliki():
    # Sprawdza czy istnieja wymagane pliki danych.
    wymagane = ["data/config.json", "data/story.json"]
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
    from gui import utworz_okno
    print("Uruchamianie Cien nad Arkham...")
    okno = utworz_okno()
    okno.mainloop()
    print("Gra zakonczona.")


if __name__ == "__main__":
    uruchom()
