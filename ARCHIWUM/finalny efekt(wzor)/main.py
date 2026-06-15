# main.py
# Osoba 5: Integrator i QA
# Punkt wejścia gry — łączy wszystkie moduły.
# Ten plik NIE zawiera logiki gry ani rysowania GUI.

import sys
import os

def sprawdz_zaleznosci():
    """Sprawdza czy wszystkie wymagane biblioteki są zainstalowane."""
    try:
        from PIL import Image
    except ImportError:
        print("[main] BŁĄD: Brak biblioteki Pillow.")
        print("       Zainstaluj ją wpisując: pip install pillow")
        sys.exit(1)

def sprawdz_pliki():
    """Sprawdza czy wymagane pliki danych istnieją przed uruchomieniem."""
    wymagane = [
        "data/config.json",
        "data/story.json",
    ]
    brakujace = [p for p in wymagane if not os.path.exists(p)]
    if brakujace:
        print("[main] BŁĄD: Brakuje następujących plików:")
        for p in brakujace:
            print(f"       - {p}")
        print("\n       Upewnij się że folder 'data/' zawiera config.json i story.json.")
        sys.exit(1)

def uruchom_gre():
    """Punkt wejścia: inicjalizuje i uruchamia grę."""
    sprawdz_zaleznosci()
    sprawdz_pliki()

    from gui import utworz_okno

    print("[main] Uruchamianie Cień nad Arkham...")
    okno = utworz_okno()
    okno.mainloop()
    print("[main] Gra zakończona.")

if __name__ == "__main__":
    uruchom_gre()