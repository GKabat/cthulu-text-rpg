import random


def rzut_koscia():
    return random.randint(1, 20)


def sprawdz_prog(wynik, prog=12):
    if wynik >= prog:
        return True
    else:
        return False


moj_rzut = rzut_koscia()
sukces = sprawdz_prog(moj_rzut)
