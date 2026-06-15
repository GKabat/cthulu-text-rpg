def inicjalizuj_stan(config: dict) -> dict:
    """
    Tworzy nowy stan gry na podstawie config.json dostarczonego przez Osobę 1.
 
    Oczekiwana struktura config.json:
    {
        "tytul": "Cień nad Arkham",
        "wersja": "1.0",
        "postac": {"nazwa": "Badacz", "hp": 100, "sanity": 100},
        "start_wezel": "start"
    }
 
    Zwraca słownik stanu gry współdzielony przez wszystkie moduły.
    """
    character = config.get("postac", {})
    state = {
        "obecny_wezel":    config.get("start_wezel", "start"),
        "hp":              character.get("hp", 100),
        "sanity":          character.get("sanity", 100),
        "odwiedzone":      [config.get("start_wezel", "start")],
        "nazwa_postaci":   character.get("nazwa", "Badacz"),
    }
    return state
 
 
def aktualizuj_stan(state: dict, effect: dict) -> dict:
    """
    Aplikuje efekt węzła na stan gry (zmiana HP, Sanity).
    Wywoływane przez engine.py po wejściu do węzła z polem "efekt".
 
    Przykład efektu: {"sanity": -10, "hp": -5}
 
    Wartości HP i Sanity są przycinane do przedziału [0, 100].
    """
    if effect is None:
        return state
 
    if "hp" in effect:
        state["hp"] = max(0, min(100, state["hp"] + effect["hp"]))
    if "sanity" in effect:
        state["sanity"] = max(0, min(100, state["sanity"] + effect["sanity"]))
 
    return state
 
 
def pobierz_stan(state: dict) -> dict:
    """
    Zwraca kopię aktualnego stanu.
    Używane przez GUI (Osoba 4) do wyświetlenia HP/Sanity i przez inne moduły
    gdy potrzebują tylko odczytać stan bez ryzyka jego zmiany.
    """
    return state.copy()