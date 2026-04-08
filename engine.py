import json
import random

# ── Bezpieczne Importy ────────────────────────────────────────────────────────
# Próbujemy zaimportować funkcje od reszty zespołu. 
# Jeśli plików brakuje, silnik użyje własnych wersji roboczych (Mocków).

try:
    from game_state import inicjalizuj_stan, aktualizuj_stan, pobierz_stan
    print("[engine] Połączono z game_state.py")
except ImportError:
    print("[engine] OSTRZEŻENIE: Brak game_state.py. Używam atrap funkcji do testów.")
    def inicjalizuj_stan(conf): return {"obecny_wezel": conf["start_wezel"], "odwiedzone": [], "hp": 100, "sanity": 100}
    def aktualizuj_stan(s, e): s.update(e)
    def pobierz_stan(s): return s

try:
    from mechanics import rzut_koscia, sprawdz_rzut
    print("[engine] Połączono z mechanics.py")
except ImportError:
    print("[engine] OSTRZEŻENIE: Brak mechanics.py. Używam losowania standardowego.")
    def rzut_koscia(s): return random.randint(1, s)
    def sprawdz_rzut(w, p): return w >= p


# ── Wczytywanie fabuły ────────────────────────────────────────────────────────

def wczytaj_fabule(path: str) -> dict:
    """Wczytuje plik story.json i zwraca słownik węzłów."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            story = json.load(f)
        print(f"[engine] Wczytano fabułę: {len(story)} węzłów.")
        return story
    except FileNotFoundError:
        print(f"[engine] BŁĄD: Nie znaleziono pliku '{path}'. Zwracam pustą fabułę.")
        return {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Błąd składni w pliku story.json: {e}")


# ── Rdzeń silnika ─────────────────────────────────────────────────────────────

def pobierz_wezel(fabula: dict, node_id: str) -> dict:
    """Zwraca węzeł fabuły dla podanego id."""
    if node_id not in fabula:
        print(f"[engine] BŁĄD: Węzeł '{node_id}' nie istnieje!")
        return {"tekst": "BŁĄD: Pustka pożarła ten fragment rzeczywistości.", "wybory": [], "zakonczone": True}
    return fabula[node_id]


def wykonaj_wybor(fabula: dict, choice: dict, state: dict) -> str:
    """Przetwarza wybór gracza i zwraca id następnego węzła."""
    condition = choice.get("warunek")

    # Sprawdzanie warunku (jeśli istnieje)
    if condition and not sprawdz_warunek(condition, state):
        print(f"[engine] Warunek niespełniony!")
        return state["obecny_wezel"]

    next_id = choice.get("cel")
    if not next_id:
        return state["obecny_wezel"]

    # Logika zmiany stanu
    if state["obecny_wezel"] not in state["odwiedzone"]:
        state["odwiedzone"].append(state["obecny_wezel"])

    state["obecny_wezel"] = next_id

    # Efekt wejścia do nowego węzła
    next_node = pobierz_wezel(fabula, next_id)
    effect = next_node.get("efekt")
    if effect:
        aktualizuj_stan(state, effect)
    
    return next_id


def sprawdz_warunek(condition: dict, state: dict) -> bool:
    """Weryfikuje czy gracz spełnia wymagania wyboru."""
    if condition is None:
        return True

    # Rzut kością
    if condition.get("rzut_koscia"):
        roll = rzut_koscia(20)
        prog = condition.get("prog", 10)
        return sprawdz_rzut(roll, prog)

    # Statystyki
    if "min_hp" in condition:
        return state.get("hp", 0) >= condition["min_hp"]
    
    if "min_sanity" in condition:
        return state.get("sanity", 0) >= condition["min_sanity"]

    return False


def czy_koniec(node: dict) -> bool:
    """Sprawdza czy to już koniec historii."""
    return node.get("zakonczone", False)


# ── Autotest (Uruchamia się tylko przy bezpośrednim starcie engine.py) ────────

if __name__ == "__main__":
    print("\n=== URUCHAMIANIE TESTU SILNIKA ===")
    
    # Przykładowa fabuła do testów wewnętrznych
    test_story = {
        "start": {
            "tekst": "Widzisz drzwi. Co robisz?",
            "wybory": [
                {"tekst": "Otwórz", "cel": "pokoj"},
                {"tekst": "Wyważ (wymaga rzutu)", "cel": "pokoj", "warunek": {"rzut_koscia": True, "prog": 15}}
            ],
            "zakonczone": False
        },
        "pokoj": {
            "tekst": "Ciemny pokój. To koniec.",
            "wybory": [],
            "zakonczone": True
        }
    }

    test_config = {"start_wezel": "start"}
    state = inicjalizuj_stan(test_config)
    
    print("Stan na starcie:", pobierz_stan(state))
    biezacy_wezel = pobierz_wezel(test_story, state["obecny_wezel"])
    print("Tekst:", biezacy_wezel["tekst"])