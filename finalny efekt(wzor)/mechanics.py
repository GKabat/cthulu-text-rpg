# mechanics.py
# Osoba 3: Programista Mechanik RPG
# CZYSTE FUNKCJE — nie modyfikują stanu bezpośrednio, nie wyświetlają tekstu.
# Każda funkcja: wejście → obliczenie → wyjście.

import random


# ── Rzuty kością ──────────────────────────────────────────────────────────────

def rzut_koscia(zakres: int = 20) -> int:
    """
    Zwraca losową liczbę z zakresu 1–zakres (domyślnie k20).

    Przykład: rzut_koscia(6) → rzut k6 (wynik 1–6)
    """
    return random.randint(1, zakres)


def sprawdz_rzut(wynik: int, prog: int) -> bool:
    """
    Sprawdza czy rzut zakończył się sukcesem.
    Mechanika Call of Cthulhu: sukces gdy wynik <= próg (statystyka bohatera).

    Przykład: sprawdz_rzut(8, 12) → True  (8 <= 12, sukces)
              sprawdz_rzut(15, 12) → False (15 > 12, porażka)
    """
    return wynik <= prog


# ── Walka ─────────────────────────────────────────────────────────────────────

def oblicz_obrazenia(atak: int, obrona: int) -> int:
    """
    Oblicza obrażenia zadane przez gracza.

    Parametry:
        atak   – wynik rzutu kością obrażeń (np. k6) + bonus siły
        obrona – redukcja obrażeń przeciwnika (0 jeśli brak pancerza)

    Zwraca obrażenia (minimum 0 — nie można leczyć atakiem).
    """
    return max(0, atak - obrona)


def atak_gracza(player_stats: dict) -> dict:
    """
    Wykonuje pełną akcję ataku gracza (rzut + obrażenia).

    Parametry:
        player_stats – słownik statystyk gracza, wymagane klucze:
                       "walka"    – próg testu walki (rzut musi być <= walka)
                       "sila_bon" – bonus do obrażeń

    Zwraca słownik:
        {
            "rzut":      int,   – wynik rzutu k20
            "sukces":    bool,  – czy trafiono
            "obrazenia": int,   – zadane obrażenia (0 jeśli pudło)
            "opis":      str    – opis wyniku do wyświetlenia przez GUI
        }
    """
    roll = rzut_koscia(20)
    success = sprawdz_rzut(roll, player_stats["walka"])

    if success:
        damage = random.randint(2, 6) + player_stats.get("sila_bon", 0)
        damage = oblicz_obrazenia(damage, 0)
        description = f"Wyrzucono {roll} (próg: {player_stats['walka']}) — TRAFIENIE! {damage} pkt. obrażeń."
    else:
        damage = 0
        description = f"Wyrzucono {roll} (próg: {player_stats['walka']}) — PUDŁO!"

    return {
        "rzut":      roll,
        "sukces":    success,
        "obrazenia": damage,
        "opis":      description,
    }


def atak_potwora(monster_stats: dict) -> dict:
    """
    Wykonuje atak przeciwnika.

    Parametry:
        monster_stats – słownik statystyk potwora, wymagane klucze:
                        "obrazenia_min" – minimalne obrażenia
                        "obrazenia_max" – maksymalne obrażenia

    Zwraca słownik:
        {
            "obrazenia": int,  – zadane obrażenia
            "opis":      str   – opis ataku do wyświetlenia przez GUI
        }
    """
    damage_min = monster_stats.get("obrazenia_min", 1)
    damage_max = monster_stats.get("obrazenia_max", 4)
    damage = random.randint(damage_min, damage_max)

    return {
        "obrazenia": damage,
        "opis":      f"Potwór atakuje i zadaje {damage} pkt. obrażeń!",
    }


def unik_gracza(player_stats: dict) -> dict:
    """
    Wykonuje test uniku gracza.

    Parametry:
        player_stats – słownik statystyk gracza, wymagany klucz:
                       "zrecznosc" – próg testu zręczności

    Zwraca słownik:
        {
            "rzut":   int,   – wynik rzutu k20
            "sukces": bool,  – czy unik się udał
            "opis":   str    – opis wyniku
        }
    """
    roll = rzut_koscia(20)
    success = sprawdz_rzut(roll, player_stats["zrecznosc"])

    description = (
        f"Wyrzucono {roll} (próg: {player_stats['zrecznosc']}) — UNIK! Odskakujesz w ostatniej chwili."
        if success else
        f"Wyrzucono {roll} (próg: {player_stats['zrecznosc']}) — ZA WOLNO! Nie zdążyłeś uniknąć ciosu."
    )

    return {
        "rzut":   roll,
        "sukces": success,
        "opis":   description,
    }


# ── Sanity i stan postaci ─────────────────────────────────────────────────────

def modyfikuj_sanity(typ_zdarzenia: str, state: dict) -> int:
    """
    Oblicza nową wartość Sanity po zdarzeniu.
    NIE modyfikuje stanu bezpośrednio — zwraca nową wartość,
    którą engine.py wpisuje do stanu przez aktualizuj_stan().

    Obsługiwane typy zdarzeń i ich koszty Sanity:
        "spotkanie_potwora"  → -5
        "smierc_sojusznika"  → -8
        "widok_koszmaru"     → -10
        "ucieczka"           → -2
        "zwyciestwo"         →  +3

    Zwraca nową wartość Sanity w przedziale [0, 100].
    """
    sanity_costs = {
        "spotkanie_potwora": -5,
        "smierc_sojusznika": -8,
        "widok_koszmaru":    -10,
        "ucieczka":          -2,
        "zwyciestwo":        +3,
    }

    modifier = sanity_costs.get(typ_zdarzenia, 0)
    new_sanity = max(0, min(100, state["sanity"] + modifier))
    return new_sanity


def czy_zyje(hp: int) -> bool:
    """
    Sprawdza czy postać żyje.
    Zwraca True gdy hp > 0.
    """
    return hp > 0


# ── Przykład użycia (do testowania bez GUI i engine) ─────────────────────────

if __name__ == "__main__":
    artur_stats = {
        "hp":        15,
        "walka":     12,
        "zrecznosc": 10,
        "sila_bon":  2,
    }

    kultista_stats = {
        "hp":           8,
        "obrazenia_min": 1,
        "obrazenia_max": 4,
    }

    print("=== TEST MECHANIK ===\n")

    # Test ataku gracza
    wynik_ataku = atak_gracza(artur_stats)
    print(f"Atak gracza:  {wynik_ataku['opis']}")

    # Test uniku
    wynik_uniku = unik_gracza(artur_stats)
    print(f"Unik gracza:  {wynik_uniku['opis']}")

    # Test ataku potwora
    wynik_potwora = atak_potwora(kultista_stats)
    print(f"Atak potwora: {wynik_potwora['opis']}")

    # Test Sanity
    stan_testowy = {"sanity": 80, "hp": 15}
    nowa_sanity = modyfikuj_sanity("spotkanie_potwora", stan_testowy)
    print(f"\nSanity po spotkaniu potwora: {stan_testowy['sanity']} → {nowa_sanity}")

    # Test czy_zyje
    print(f"\nCzy Artur żyje (hp=15)? {czy_zyje(15)}")
    print(f"Czy Artur żyje (hp=0)?  {czy_zyje(0)}")