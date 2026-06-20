# engine.py
# Silnik gry: wczytuje fabule i obsluguje przejscia miedzy wezlami.

import json
from game_state import inicjalizuj_stan, aktualizuj_stan
from mechanics import rzut_koscia, sprawdz_rzut


def wczytaj_fabule(sciezka):
    # Otwiera plik JSON i zwraca slownik wezlow.
    plik = open(sciezka, "r", encoding="utf-8")
    fabula = json.load(plik)
    plik.close()
    print("[engine] Wczytano fabule:", len(fabula), "wezlow.")
    return fabula


def pobierz_wezel(fabula, id_wezla):
    # Zwraca slownik wezla po jego id.
    if id_wezla not in fabula:
        print("[engine] BLAD: brak wezla", id_wezla)
        return None
    return fabula[id_wezla]


def sprawdz_warunek(warunek, stan):
    # Sprawdza czy gracz spelnia warunek wyboru.
    # Gdy warunek wymaga rzutu kostka, zapisuje wynik do stan["ostatni_rzut"]
    # zeby GUI mogle pokazac graczowi wynik po dokonaniu wyboru.
    if warunek is None:
        return True

    if "rzut_koscia" in warunek and warunek["rzut_koscia"] == True:
        wynik = rzut_koscia(20)
        prog = warunek.get("prog", 10)
        sukces = sprawdz_rzut(wynik, prog)
        stan["ostatni_rzut"] = {
            "wynik": wynik,
            "prog": prog,
            "sukces": sukces,
        }
        print("[engine] Rzut k20:", wynik, "prog:", prog, "->",
              "SUKCES" if sukces else "PORAZKA")
        return sukces

    if "min_hp" in warunek:
        return stan["hp"] >= warunek["min_hp"]

    if "min_sanity" in warunek:
        return stan["sanity"] >= warunek["min_sanity"]

    print("[engine] Nieznany warunek:", warunek)
    return False


def wykonaj_wybor(fabula, wybor, stan):
    # Sprawdza warunek, przechodzi do nowego wezla i aplikuje efekt.
    warunek = wybor.get("warunek")
    if not sprawdz_warunek(warunek, stan):
        # Warunek niespelniony.
        # Jezeli wybor ma "cel_porazka" - idziemy tam.
        # Inaczej zostajemy w tym samym wezle.
        if "cel_porazka" in wybor:
            stan["obecny_wezel"] = wybor["cel_porazka"]
            nowy = pobierz_wezel(fabula, wybor["cel_porazka"])
            if nowy is not None:
                aktualizuj_stan(stan, nowy.get("efekt"))
            return stan["obecny_wezel"]
        print("[engine] Warunek niespelniony, zostajesz na miejscu.")
        return stan["obecny_wezel"]

    nowy_id = wybor["cel"]
    if stan["obecny_wezel"] not in stan["odwiedzone"]:
        stan["odwiedzone"].append(stan["obecny_wezel"])
    stan["obecny_wezel"] = nowy_id

    nowy = pobierz_wezel(fabula, nowy_id)
    if nowy is not None:
        aktualizuj_stan(stan, nowy.get("efekt"))

    print("[engine] Przejscie ->", nowy_id)
    return nowy_id


def czy_koniec(wezel):
    # Zwraca True jezeli wezel jest oznaczony jako koniec gry.
    return wezel.get("zakonczone", False)


# ── Tryb konsolowy do testow (uruchamiany przez: python engine.py) ────────────

if __name__ == "__main__":
    EDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    plik_konfig = open(os.path.join(EDIR, "data", "config.json"), "r", encoding="utf-8")
    config = json.load(plik_konfig)
    plik_konfig.close()

    fabula = wczytaj_fabule(os.path.join(EDIR, "data", "story.json"))
    stan = inicjalizuj_stan(config)

    print("=== TEST SILNIKA ===")
    print("Gra:", config["tytul"], "v" + config["wersja"])

    while True:
        id_wezla = stan["obecny_wezel"]
        wezel = pobierz_wezel(fabula, id_wezla)
        if wezel is None:
            print("Brak wezla. Koniec.")
            break

        print()
        print("[" + id_wezla + "]")
        print(wezel["tekst"])
        print("HP:", stan["hp"], "| Sanity:", stan["sanity"])

        if stan.get("ostatni_rzut"):
            r = stan["ostatni_rzut"]
            wynik_txt = "SUKCES" if r["sukces"] else "PORAZKA"
            print(">> Rzut k20:", r["wynik"], "/ prog:", r["prog"], "->", wynik_txt)
            stan["ostatni_rzut"] = None

        if czy_koniec(wezel):
            print("=== KONIEC GRY ===")
            break

        if stan["hp"] <= 0 or stan["sanity"] <= 0:
            print("=== KONIEC GRY (HP/Sanity = 0) ===")
            break

        wybory = wezel["wybory"]
        if len(wybory) == 0:
            print("Brak wyborow. Koniec.")
            break

        i = 0
        while i < len(wybory):
            print(" [" + str(i) + "]", wybory[i]["tekst"])
            i = i + 1

        wpis = input("Wybierz numer: ")
        try:
            indeks = int(wpis)
        except ValueError:
            print("Wpisz liczbe.")
            continue

        if indeks < 0 or indeks >= len(wybory):
            print("Zly numer.")
            continue

        wykonaj_wybor(fabula, wybory[indeks], stan)
