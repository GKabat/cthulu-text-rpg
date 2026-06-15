# main.py - odpala gre
# uruchamiac z katalogu projektu:  python REFACTOR/main.py

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG = os.path.join(SCRIPT_DIR, "data", "config.json")
STORY = os.path.join(SCRIPT_DIR, "data", "story.json")


def sprawdz_pliki():
    # jak nie ma plikow z danymi to nie ma sensu odpalac gry
    for sciezka in [CONFIG, STORY]:
        if not os.path.exists(sciezka):
            print("BLAD: brakuje pliku:", sciezka)
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
