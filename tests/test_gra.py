# test_gra.py - proste testy logiki gry (bez okna)
# Uruchamiac z katalogu projektu:  python tests/test_gra.py
# Sprawdzamy silnik, kosci, stan gry, dane fabuly i podpowiedzi - czyli to,
# co nie wymaga klikania w oknie. Kazdy test to funkcja z assertami.

import os
import sys
import json

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TESTS_DIR)
sys.path.insert(0, os.path.join(ROOT, "app", "src"))

import engine
import game_state
import mechanics
import gui

STORY = os.path.join(ROOT, "app", "data", "story.json")
CONFIG = os.path.join(ROOT, "app", "data", "config.json")

# wczytujemy raz, uzywamy w testach
fabula = engine.wczytaj_fabule(STORY)
config = json.load(open(CONFIG, "r", encoding="utf-8"))
gui.fabula = fabula   # podpowiedz_efektu korzysta z globalnej fabuly


# ---- mechanika i silnik (sekcja C) ----

def test_rzut_zakres():
    for _ in range(1000):
        w = mechanics.rzut_koscia(20)
        assert 1 <= w <= 20

def test_sprawdz_rzut_sukces():
    assert mechanics.sprawdz_rzut(12, 12) is True   # wynik = prog

def test_sprawdz_rzut_porazka():
    assert mechanics.sprawdz_rzut(11, 12) is False

def test_wczytaj_fabule():
    f = engine.wczytaj_fabule(STORY)
    assert isinstance(f, dict)
    assert len(f) == 17

def test_pobierz_wezel_istnieje():
    w = engine.pobierz_wezel(fabula, "rozdroze")
    assert w is not None
    assert "wybory" in w

def test_pobierz_wezel_brak():
    assert engine.pobierz_wezel(fabula, "nie_ma_takiego") is None

def test_warunek_none():
    assert engine.sprawdz_warunek(None, {"sanity": 100}) is True

def test_warunek_min_sanity():
    assert engine.sprawdz_warunek({"min_sanity": 50}, {"sanity": 55}) is True
    assert engine.sprawdz_warunek({"min_sanity": 50}, {"sanity": 40}) is False

def test_warunek_rzut_zapisuje_wynik():
    stan = {"sanity": 100, "ostatni_rzut": None}
    engine.sprawdz_warunek({"rzut_koscia": True, "prog": 12}, stan)
    r = stan["ostatni_rzut"]
    assert r is not None
    assert r["prog"] == 12
    assert "wynik" in r and "sukces" in r

def test_wykonaj_wybor_porazka():
    # wymuszamy porazke wysokim progiem, wybor ma cel_porazka -> chata_porazka (HP -10)
    stan = game_state.inicjalizuj_stan(config)
    stan["obecny_wezel"] = "rozdroze"
    wybor = {"tekst": "x", "cel": "chata",
             "warunek": {"rzut_koscia": True, "prog": 999},
             "cel_porazka": "chata_porazka"}
    engine.wykonaj_wybor(fabula, wybor, stan)
    assert stan["obecny_wezel"] == "chata_porazka"
    assert stan["hp"] == 90   # 100 - 10

def test_czy_koniec():
    assert engine.czy_koniec(fabula["walka_z_cieniem"]) is True
    assert engine.czy_koniec(fabula["rozdroze"]) is False


# ---- stan gry i dane (sekcja D) ----

def test_inicjalizuj_stan():
    s = game_state.inicjalizuj_stan(config)
    assert s["hp"] == 100
    assert s["sanity"] == 100
    assert s["obecny_wezel"] == "intro"
    assert s["odwiedzone"] == []
    assert s["ekwipunek"] == []
    assert s["ostatni_rzut"] is None

def test_aktualizuj_hp():
    s = {"hp": 100, "sanity": 100, "ekwipunek": []}
    game_state.aktualizuj_stan(s, {"hp": -25})
    assert s["hp"] == 75

def test_clamp_dolny_hp():
    s = {"hp": 10, "sanity": 100, "ekwipunek": []}
    game_state.aktualizuj_stan(s, {"hp": -100})
    assert s["hp"] == 0   # nie schodzi ponizej 0

def test_clamp_gorny_sanity():
    s = {"hp": 50, "sanity": 90, "ekwipunek": []}
    game_state.aktualizuj_stan(s, {"sanity": 20})
    assert s["sanity"] == 100   # nie przekracza 100

def test_dodaj_przedmiot():
    s = {"hp": 50, "sanity": 50, "ekwipunek": []}
    game_state.aktualizuj_stan(s, {"dodaj_przedmiot": "kiel wilka"})
    assert s["ekwipunek"] == ["kiel wilka"]

def test_efekt_none_bez_zmian():
    s = {"hp": 50, "sanity": 50, "ekwipunek": []}
    przed = dict(s)
    game_state.aktualizuj_stan(s, None)
    assert s == przed

def test_pobierz_stan_kopia():
    s = game_state.inicjalizuj_stan(config)
    kopia = game_state.pobierz_stan(s)
    kopia["hp"] = 1
    assert s["hp"] == 100   # oryginal bez zmian

def test_story_integralnosc():
    f = json.load(open(STORY, "r", encoding="utf-8"))
    assert len(f) == 17
    assert config["start_wezel"] in f

def test_story_brak_martwych_linkow():
    for nazwa, wezel in fabula.items():
        for c in wezel["wybory"]:
            for pole in ("cel", "cel_porazka"):
                if pole in c and c[pole] is not None:
                    assert c[pole] in fabula, "zly cel w " + nazwa

def test_story_spojnosc_regul():
    for nazwa, wezel in fabula.items():
        for c in wezel["wybory"]:
            w = c.get("warunek")
            if w and w.get("rzut_koscia"):
                assert "prog" in w
        if wezel.get("zakonczone"):
            assert wezel.get("zakonczenie") in ("dobry", "zly")


# ---- podpowiedzi efektow (sekcja B) ----

def test_opis_efektu_hp():
    assert gui.opis_efektu({"hp": -25}) == "HP -25"

def test_opis_efektu_sanity_plus():
    assert gui.opis_efektu({"sanity": 20}) == "Sanity +20"

def test_podpowiedz_sanity():
    wybor = [c for c in fabula["rozdroze"]["wybory"] if c["cel"] == "jaskinia"][0]
    assert gui.podpowiedz_efektu(wybor) == "Sanity -10"

def test_podpowiedz_rzut():
    wybor = [c for c in fabula["rozdroze"]["wybory"] if c.get("cel") == "chata"][0]
    p = gui.podpowiedz_efektu(wybor)
    assert p.startswith("rzut k20 >= 12")
    assert "porażka: HP -10" in p

def test_podpowiedz_bez_zmian():
    wybor = [c for c in fabula["rozdroze"]["wybory"] if c["cel"] == "polana"][0]
    assert gui.podpowiedz_efektu(wybor) == "bez zmian"


# ---- uruchomienie wszystkich testow ----

testy = [
    test_rzut_zakres, test_sprawdz_rzut_sukces, test_sprawdz_rzut_porazka,
    test_wczytaj_fabule, test_pobierz_wezel_istnieje, test_pobierz_wezel_brak,
    test_warunek_none, test_warunek_min_sanity, test_warunek_rzut_zapisuje_wynik,
    test_wykonaj_wybor_porazka, test_czy_koniec,
    test_inicjalizuj_stan, test_aktualizuj_hp, test_clamp_dolny_hp,
    test_clamp_gorny_sanity, test_dodaj_przedmiot, test_efekt_none_bez_zmian,
    test_pobierz_stan_kopia, test_story_integralnosc,
    test_story_brak_martwych_linkow, test_story_spojnosc_regul,
    test_opis_efektu_hp, test_opis_efektu_sanity_plus, test_podpowiedz_sanity,
    test_podpowiedz_rzut, test_podpowiedz_bez_zmian,
]

if __name__ == "__main__":
    ok = 0
    for t in testy:
        try:
            t()
            print("OK   ", t.__name__)
            ok = ok + 1
        except AssertionError as e:
            print("BLAD ", t.__name__, "->", e)
    print()
    print("PRZESZLO", ok, "/", len(testy))
    if ok != len(testy):
        sys.exit(1)
