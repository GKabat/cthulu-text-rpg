import json
from game_state import inicjalizuj_stan, aktualizuj_stan, pobierz_stan


# ── Wczytywanie fabuły ────────────────────────────────────────────────────────

def wczytaj_fabule(path: str) -> dict:
   
    try:
        with open(path, "r", encoding="utf-8") as f:
            story = json.load(f)
        print(f"[engine] Wczytano fabułę: {len(story)} węzłów.")
        return story
    except FileNotFoundError:
        raise FileNotFoundError(f"Nie znaleziono pliku fabuły: '{path}'")
    except json.JSONDecodeError as e:
        raise ValueError(f"Błąd składni w pliku story.json: {e}")


# ── Rdzeń silnika ─────────────────────────────────────────────────────────────

def pobierz_wezel(fabula: dict, node_id: str) -> dict:
   
    if node_id not in fabula:
        raise KeyError(f"Węzeł '{node_id}' nie istnieje w fabule!")
    return fabula[node_id]


def wykonaj_wybor(fabula: dict, choice: dict, state: dict) -> str:
   
    condition = choice.get("warunek")

    # Jeśli wybór wymaga sprawdzenia — weryfikuj warunek
    if condition and not sprawdz_warunek(condition, state):
        print(f"[engine] Warunek niespełniony dla wyboru: '{choice['tekst']}'")
        # Zwracamy bieżący węzeł — nic się nie zmienia
        return state["obecny_wezel"]

    next_id = choice["cel"]

    # Zapamiętaj odwiedzony węzeł
    if state["obecny_wezel"] not in state["odwiedzone"]:
        state["odwiedzone"].append(state["obecny_wezel"])

    # Zaktualizuj bieżący węzeł w stanie
    state["obecny_wezel"] = next_id

    # Zastosuj efekt nowego węzła (jeśli istnieje)
    next_node = pobierz_wezel(fabula, next_id)
    effect = next_node.get("efekt")
    if effect:
        aktualizuj_stan(state, effect)
        print(f"[engine] Zastosowano efekt węzła '{next_id}': {effect}")

    print(f"[engine] Przejście → {next_id}")
    return next_id


def sprawdz_warunek(condition: dict, state: dict) -> bool:
   
    if condition is None:
        return True

    # Warunek: rzut kością
    if condition.get("rzut_koscia"):
        from mechanics import rzut_koscia, sprawdz_rzut
        roll_result = rzut_koscia(20)
        threshold = condition.get("prog", 10)
        success = sprawdz_rzut(roll_result, threshold)
        print(f"[engine] Rzut kością: {roll_result} vs próg {threshold} → {'sukces' if success else 'porażka'}")
        return success

    # Warunek: minimalne HP
    if "min_hp" in condition:
        return state["hp"] >= condition["min_hp"]

    # Warunek: minimalna Sanity
    if "min_sanity" in condition:
        return state["sanity"] >= condition["min_sanity"]

    # Nieznany typ warunku — bezpieczny fallback
    print(f"[engine] Ostrzeżenie: nieznany typ warunku: {condition}")
    return False


def czy_koniec(node: dict) -> bool:
    
    return node.get("zakonczone", False)


# ── Uruchomienie z plików JSON ────────────────────────────────────────────────

if __name__ == "__main__":
    import os

    config_path = "data/config.json"
    story_path  = "data/story.json"

    # Wczytaj config
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Nie znaleziono pliku konfiguracji: '{config_path}'")

    # Wczytaj fabułę i zainicjalizuj stan
    story = wczytaj_fabule(story_path)
    state = inicjalizuj_stan(config)

    print("=== TEST SILNIKA ===")
    print(f"Gra: {config.get('tytul')} v{config.get('wersja')}")
    print(f"Stan początkowy: {pobierz_stan(state)}\n")

    # Pętla testowa — gracz wybiera w konsoli
    while True:
        node_id = state["obecny_wezel"]
        node    = pobierz_wezel(story, node_id)

        print(f"\n[{node_id}]")
        print(f"{node['tekst']}")
        print(f"HP: {state['hp']} | Sanity: {state['sanity']}")

        if czy_koniec(node):
            print("\n=== KONIEC GRY ===")
            break

        choices = node["wybory"]
        if not choices:
            print("Brak wyborów — koniec gry.")
            break

        for i, choice in enumerate(choices):
            warunek_info = f" [wymaga: {choice['warunek']}]" if choice.get("warunek") else ""
            print(f"  [{i}] {choice['tekst']}{warunek_info}")

        try:
            indeks = int(input("\nWybierz akcję: "))
            if indeks < 0 or indeks >= len(choices):
                print("Nieprawidłowy wybór, spróbuj ponownie.")
                continue
        except ValueError:
            print("Wpisz numer wyboru.")
            continue

        wykonaj_wybor(story, choices[indeks], state)