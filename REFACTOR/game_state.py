# game_state.py
# Stan gry trzymany w slowniku. Funkcje go tworza i zmieniaja.


def inicjalizuj_stan(config):
    # Tworzy nowy stan gry na podstawie config.json.
    postac = config["postac"]
    stan = {
        "obecny_wezel": config["start_wezel"],
        "hp": postac["hp"],
        "sanity": postac["sanity"],
        "nazwa_postaci": postac["nazwa"],
        "odwiedzone": [],
        "ekwipunek": [],
        # Informacja o ostatnim rzucie kostka. None gdy nic nie rzucalismy.
        # Ustawiana w engine.sprawdz_warunek, czyszczona przez gui po wyswietleniu.
        "ostatni_rzut": None,
    }
    return stan


def aktualizuj_stan(stan, efekt):
    # Zmienia HP, Sanity i ekwipunek wedlug efektu.
    if efekt is None:
        return stan

    if "hp" in efekt:
        stan["hp"] = stan["hp"] + efekt["hp"]
        if stan["hp"] < 0:
            stan["hp"] = 0
        if stan["hp"] > 100:
            stan["hp"] = 100

    if "sanity" in efekt:
        stan["sanity"] = stan["sanity"] + efekt["sanity"]
        if stan["sanity"] < 0:
            stan["sanity"] = 0
        if stan["sanity"] > 100:
            stan["sanity"] = 100

    if "dodaj_przedmiot" in efekt:
        stan["ekwipunek"].append(efekt["dodaj_przedmiot"])

    return stan


def pobierz_stan(stan):
    # Zwraca kopie stanu (zeby nikt z zewnatrz nie zepsul oryginalu).
    return stan.copy()
