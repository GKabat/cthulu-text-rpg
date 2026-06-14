# mechanics.py
# Proste mechaniki RPG: rzut koscia i sprawdzenie progu.

import random


def rzut_koscia(zakres=20):
    # Losuje liczbe od 1 do "zakres". Domyslnie k20.
    return random.randint(1, zakres)


def sprawdz_rzut(wynik, prog):
    # Zwraca True gdy wynik jest co najmniej rowny progowi.
    # Im wiekszy wynik tym lepiej (jak w klasycznym d20).
    if wynik >= prog:
        return True
    else:
        return False
