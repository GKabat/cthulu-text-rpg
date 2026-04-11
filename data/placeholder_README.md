# Placeholder data/ — co jest w plikach

Wrzucone do `data/` jako rusztowanie, żeby Kløseek i Nowy Johnny Knoxville mogli ruszyć z pracą bez czekania na @barto. Treść jest symboliczna, struktura zgodna z kontraktem z dokumentacji projektu.

## Pliki

- **story.json** — 6 węzłów: `start`, `jaskinia`, `las`, `chata_sukces`, `koniec_dobry`, `koniec_zly`
- **config.json** — postać startowa (HP 100, Sanity 100), tytuł, węzeł startowy

## Co testują te 6 węzłów

| Mechanika | Gdzie |
|---|---|
| Wybór bez warunku | `start` → `jaskinia` / `las` |
| Wybór z warunkiem (rzut kością) | `start` → `chata_sukces` (próg 12) |
| Efekt na stan (Sanity) | `jaskinia` → `sanity: -10` |
| Efekt złożony (HP + Sanity) | `las` → `hp: -5, sanity: -5` |
| Powrót do wcześniejszego węzła | `jaskinia` / `las` → `start` |
| Zakończenie gry (flaga) | `koniec_dobry`, `koniec_zly` → `zakonczone: true` |
| Brak grafiki | wszystkie węzły mają `obrazek: null` |

## Dla Kløseeka

Możesz pisać i testować:

- `wczytaj_fabule("data/story.json")` — czy wczytuje bez błędu
- `pobierz_wezel(fabula, "start")` — czy zwraca dict z 3 wyborami
- `wykonaj_wybor()` — czy poprawnie czyta pole `cel` i przechodzi
- `sprawdz_warunek({"rzut_koscia": true, "prog": 12}, stan)` — czy rozumie format warunku
- `czy_koniec(wezel)` — czy wykrywa `zakonczone: true`

## Dla Nowego Johnny'ego Knoxville

Twoje funkcje są wywoływane w momencie sprawdzenia warunku:

- `rzut_koscia(20)` — gdy w wyborze jest `"rzut_koscia": true`
- `sprawdz_rzut(wynik, prog)` — porównuje wynik rzutu z progiem (tutaj próg 12)

Możesz testować niezależnie, bez czekania na silnik.

## Uwagi

- Brak polskich znaków — celowo, żeby uniknąć problemów z UTF-8 na Windowsie. @barto doda je przy właściwej fabule.
- Wszystkie `obrazek: null` — @cabaja_nra musi obsłużyć przypadek braku grafiki.
- To jest **placeholder**. Gdy @barto dorzuci właściwą treść, struktura może ewoluować — ale na tym etapie wystarczy do napisania i przetestowania całego silnika i mechanik.

---

*Plik wygenerowany przez abcdef jako rusztowanie startowe. Do przejęcia przez @barto.*
