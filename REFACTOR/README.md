# REFACTOR — nowa wersja projektu "Cień nad Arkham"

Tu zbieramy **nową wersję** gry. Stara (oryginalna) wersja zostaje nietknięta
w katalogu głównym projektu — dzięki temu każdy ma dostęp do **obu wersji naraz**,
bez przełączania gałęzi gita.

- Stara wersja: `../` (główny katalog projektu)
- Nowa wersja: ten katalog (`REFACTOR/`)
- Dane: nowa wersja czyta `REFACTOR/data/` jeśli istnieje (ulepszone
  stylistycznie teksty, klimat Lovecraft/Poe, wersja 2.0), w przeciwnym razie
  wspólne `../data`. Struktura, cele, warunki i efekty są identyczne ze starą
  wersją — zmieniono **wyłącznie teksty i etykiety wyborów**.
- Grafiki scen (`tiles/*.png`) są **wspólne** — czytane z `../tiles`.
- Wyjątek: **`REFACTOR/tiles/frame.png`** jest lokalny dla nowej wersji.
  To ramka z **realnie przezroczystym otworem** (w starej wersji środek był
  wmalowaną, nieprzezroczystą szachownicą). Nowa wersja kładzie ramkę
  na wierzchu Canvasa, a treść gry siedzi w jej przezroczystym otworze.

## Funkcje GUI (nowa wersja)

- **Ramka na wierzchu** (Canvas) z realnie przezroczystym otworem; treść
  osadzona w środku, brązowe tło wypełnia całe okno.
- **Kość** (`tiles/dice_roll.png`) pojawia się pod przyciskami wyborów tylko
  wtedy, gdy w danym przejściu nastąpił rzut — wraz z wynikiem rzutu
  (`Rzut k20: X / prog Y -> SUKCES/PORAŻKA`, kolor zależny od wyniku).
- **Podpowiedzi efektów na przyciskach** — każdy przycisk wyboru ma w treści
  drugą linię z efektem (rzut/próg, skutek sukcesu i porażki), generowaną
  automatycznie z `story.json`. Zawsze włączone.
- **HP / Sanity / Ekwipunek** wyśrodkowane u góry (nie chowają się za ramką).
- **Zapis / wczytanie gry** (jeden slot, `data/save.json`): przyciski
  „Zapisz"/„Wczytaj" na ekranie gry oraz „Kontynuuj" w menu (aktywne tylko gdy
  zapis istnieje). Cały stan to słownik typów JSON, więc zapis to `json.dump`,
  a wczytanie `json.load` — bez dodatkowych bibliotek.

## Uruchomienie nowej wersji

```
cd <katalog projektu>
python REFACTOR/main.py
```

Ścieżki są kotwiczone do położenia plików, więc zadziała z dowolnego katalogu.

## Zatwierdzony podział prac (4 osoby)

Zespół: 4 osoby (jedna osoba zrezygnowała). Podział jest celowo równomierny —
nikt nie bierze całego `gui.py` (416 linii), więc rozbijamy je między A i B.

| Osoba | Sekcja | Zakres |
|-------|--------|--------|
| **A** | Uruchomienie + budowa okna i menu | `main.py` + część `gui.py`: `utworz_okno`, `zaladuj_dane`, `pokaz_menu`, `pokaz_gre`, `nowa_gra`, `sprawdz_pliki` |
| **B** | Renderowanie sceny i ekrany | część `gui.py`: `odswiez_scene`, `wyswietl_scene`, `wyswietl_obrazek`, `wyswietl_rzut`, `wyswietl_wybory`, `obsluz_wybor`, `aktualizuj_statystyki`, `aktualizuj_ekwipunek`, `ekran_koncowy` |
| **C** | Silnik fabuły + mechanika kości | `engine.py` + `mechanics.py` |
| **D** | Stan gry + treść i konfiguracja | `game_state.py` + `data/story.json` + `data/config.json` (+ mapowanie `../tiles/`) |

Każda osoba przygotowuje dla swojej sekcji:
- **1 diagram Use Case (UML)**,
- **dokładnie 10 unikalnych testów**.

## Kolejne kroki

1. [x] Podział prac (zatwierdzony).
2. [ ] Diagramy Use Case (po 1 na osobę).
3. [ ] Testy (po 10 na osobę).
4. [ ] Nowa wersja kodu w tym katalogu.
