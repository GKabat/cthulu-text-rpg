# Cień nad Arkham - pełna specyfikacja fabuły i mechaniki

> Dokument referencyjny opisujący KOMPLETNĄ zawartość gry w sposób jednoznaczny.
> Czytelnik docelowy: inny model językowy (LLM) lub programista, który ma
> w pełni zrozumieć / odtworzyć logikę gry bez dostępu do kodu.
> Źródło prawdy: `app/data/story.json` + `app/data/config.json`.
> Dokument wygenerowany automatycznie z tych plików (sekcje koncepcyjne dopisane ręcznie).

## 1. Czym jest gra

Tekstowa gra paragrafowa (interaktywna fikcja) w klimacie Lovecraft/Poe.
Gracz wciela się w postać badacza, który budzi się bez pamięci w opuszczonym
obozie w lasach wokół Arkham. Celem jest przetrwać noc i dotrzeć do latarni
morskiej (jedyne bezpieczne miejsce). Gra polega na podejmowaniu wyborów
prowadzących między scenami ("węzłami"). Część wyborów uruchamia test losowy
(rzut kością k20) lub test stanu postaci.

Tytuł: **Cień nad Arkham**. Wersja danych: **2.0**. Postać startowa: **Badacz**.

## 2. Model stanu gry

Stan gry to jeden słownik. Pola:

| Pole | Typ | Znaczenie | Wartość startowa |
|---|---|---|---|
| `obecny_wezel` | string | id aktualnej sceny | `intro` |
| `hp` | int 0..100 | punkty życia | 100 |
| `sanity` | int 0..100 | poczytalność | 100 |
| `nazwa_postaci` | string | imię postaci | `Badacz` |
| `odwiedzone` | lista string | id już odwiedzonych węzłów | `[]` |
| `ekwipunek` | lista string | zdobyte przedmioty | `[]` |
| `ostatni_rzut` | obiekt/None | wynik ostatniego rzutu k20 (do UI) | `None` |

## 3. Reguły mechaniki (jednoznacznie)

1. **Efekt węzła stosuje się przy WEJŚCIU do tego węzła** (również gdy
   wchodzi się ścieżką porażki `cel_porazka`).
2. HP i Sanity są **przycinane do zakresu 0..100** po każdej zmianie.
3. **Rzut k20**: losowa liczba całkowita 1..20. Sukces, gdy `wynik >= prog`.
   Sam rzut NIE zmienia statystyk - decyduje tylko, czy iść do `cel` (sukces),
   czy do `cel_porazka` (porażka). Zmiana HP/Sanity pochodzi z efektu węzła docelowego.
4. **Warunki wyboru** (pole `warunek`):
   - `{"rzut_koscia": true, "prog": N}` - test kością k20 z progiem N,
   - `{"min_sanity": N}` - spełniony, gdy Sanity >= N,
   - `{"min_hp": N}` - spełniony, gdy HP >= N,
   - `null` - brak warunku (wybór zawsze prowadzi do `cel`).
5. Gdy warunek NIE jest spełniony: jeśli wybór ma `cel_porazka` - idziemy tam;
   w przeciwnym razie gracz zostaje w tym samym węźle.
6. **Zakończenia**: węzeł z `"zakonczone": true` kończy grę; pole `zakonczenie`
   to `"dobry"` (ekran ZWYCIĘSTWO) lub `"zly"` (ekran KONIEC GRY).
7. **Ciche zakończenie (zły koniec)**: niezależnie od flag, jeśli po wejściu do
   węzła **HP <= 0 lub Sanity <= 0**, gra kończy się ekranem KONIEC GRY (zly).

## 4. Format danych (schemat węzła)

```json
"id_wezla": {
  "tekst": "treść sceny (druga osoba)",
  "obrazek": "tiles/plik.png",
  "wybory": [
    {"tekst": "etykieta", "cel": "id_celu", "warunek": null}
    // opcjonalnie: "warunek": {...}, "cel_porazka": "id_celu_porazki"
  ],
  "efekt": null,            // lub {"hp": -10} / {"sanity": +20} / {"dodaj_przedmiot": "x"}
  "zakonczone": false,      // true dla zakończeń
  "zakonczenie": "dobry"    // tylko gdy zakonczone=true: "dobry" | "zly"
}
```

## 5. Pełny spis węzłów (17)

Kolejność: węzeł startowy, potem reszta w kolejności z pliku.

### `intro`  *(START)*
- **Obrazek:** `tiles/camp.png`
- **Efekt przy wejściu:** brak
- **Zakończenie:** -
- **Tekst:**
  > Budzisz się z głową ciężką jak nasiąknięta deszczem ziemia. Wokół rozpełzł się opuszczony obóz: rozdarty namiot, ognisko zdławione do kilku sennych węgli, ślady stóp grzęznące w mchu i ginące w głębi lasu. Z mgły sączy się szept - cienki, cierpliwy, ułożony w słowa, których twój język wzdraga się powtórzyć. Nie pamiętasz własnego imienia ani tego, co przywiodło cię w to miejsce.
- **Wybory:**
  1. "Podnieść się i ruszyć przed siebie." -> `rozdroze`

### `rozdroze`
- **Obrazek:** `tiles/wood_road.png`
- **Efekt przy wejściu:** brak
- **Zakończenie:** -
- **Tekst:**
  > Ścieżka wije się między spróchniałymi pniami, które stoją zbyt nieruchomo jak na żywy las. Przed tobą rozdziela się na trzy. Po lewej czerń jaskini, z której bije chłód starszy niż kamień. Na wprost ledwie widoczny dukt tonie w mroku. Po prawej drewniane drzwi opuszczonej chaty - wzdęte od wilgoci, jakby od dawna trzymały coś za zawiasami.
- **Wybory:**
  1. "Zejść w czeluść jaskini." -> `jaskinia`
  2. "Pójść leśnym duktem." -> `polana`
  3. "Naprzeć ramieniem na drzwi chaty." -> `chata`  [warunek: rzut k20 >= 12; porażka -> `chata_porazka`]

### `jaskinia`
- **Obrazek:** `tiles/cave_entrance.png`
- **Efekt przy wejściu:** Sanity -10
- **Zakończenie:** -
- **Tekst:**
  > Powietrze pod kamiennym łukiem jest zimne jak dotyk topielca. Z głębi sączy się blask, którego barwy nie nazwie żaden ludzki język - nie żółty, nie zielony, lecz coś, co oko przyjmuje wbrew sobie. Czujesz, jak twoja myśl kurczy się i cofa, jakby już wiedziała, co czeka dalej.
- **Wybory:**
  1. "Zagłębić się ku światłu." -> `glebiny`
  2. "Wycofać się na rozdroże." -> `rozdroze`

### `glebiny`
- **Obrazek:** `tiles/cave_road.png`
- **Efekt przy wejściu:** Sanity -10
- **Zakończenie:** -
- **Tekst:**
  > Tunel rozstępuje się w salę zbyt wielką, by zmieścić ją pod tym wzgórzem. Ściany pokrywają ryte znaki, które pełzną i przestawiają się, ilekroć przestajesz na nie patrzeć. W najdalszym mroku coś otwiera oczy - dwa płomienie bez ciepła, wpatrzone w ciebie z cierpliwością, jaką ma tylko wieczność.
- **Wybory:**
  1. "Wytrzymać to spojrzenie. Musisz zrozumieć." -> `final_szalenstwo`
  2. "Zamknąć oczy i cofać się powoli." -> `jaskinia`

### `polana`
- **Obrazek:** `tiles/wolf.png`
- **Efekt przy wejściu:** brak
- **Zakończenie:** -
- **Tekst:**
  > Dukt wyprowadza cię na polanę zatopioną w sinym świetle bez źródła. Pośród pni stoi wilk - większy od każdego, jakiego widziałeś, z karkiem zjeżonym i wargą uniesioną nad białym kłem. Nie warczy. Patrzy spokojnie, jakby od początku wiedział, że przyjdziesz, i jakby twoje przyjście niczego nie zmieniało.
- **Wybory:**
  1. "Stanąć z nim do walki." -> `triumf_wilk`  [warunek: rzut k20 >= 13; porażka -> `kleski_wilk`]
  2. "Cofać się powoli, obchodząc polanę bokiem." -> `rozstaje`

### `triumf_wilk`
- **Obrazek:** `tiles/wolf.png`
- **Efekt przy wejściu:** dodaj przedmiot: "kieł wilka"
- **Zakończenie:** -
- **Tekst:**
  > Bestia rzuca się na ciebie, lecz ty robisz krok w bok. Dłoń znajduje kamień, kamień znajduje skroń. Wilk osuwa się bez głosu. Klękasz nad stygnącym cielskiem i wyłamujesz jeden z górnych kłów - biały, ciężki, ciepły jeszcze od cudzego życia. Zaciskasz na nim palce jak na talizmanie przeciw czemuś, czego nie umiesz nazwać.
- **Wybory:**
  1. "Ruszyć dalej leśnym duktem." -> `rozstaje`

### `kleski_wilk`
- **Obrazek:** `tiles/wolf.png`
- **Efekt przy wejściu:** HP -25
- **Zakończenie:** -
- **Tekst:**
  > Wilk jest szybszy od myśli. Kły rozcinają ci ramię, nim zdążysz unieść rękę. Padasz w błoto, krew miesza się z deszczem, a ty kulisz się odruchowo, czekając ciosu, który nie nadchodzi. Gdy wreszcie unosisz głowę, wilka już nie ma - cofnął się w mrok między pniami bezgłośnie jak cień, a cisza zdaje się drwić z twojego strachu.
- **Wybory:**
  1. "Zatamować krew i iść dalej." -> `rozstaje`

### `rozstaje`
- **Obrazek:** `tiles/old_man.png`
- **Efekt przy wejściu:** brak
- **Zakończenie:** -
- **Tekst:**
  > Dukt urywa się na rozstajach. Stoi tam starzec owinięty w płaszcz czarny jak wnętrze studni, wsparty o sękaty kij. Spod kaptura patrzą oczy, które odbijają światło, choć tu żadnego światła nie ma. Gdzieś między drzewami niesie się ten sam szept, co na początku - jakbyś nigdy się od niego nie oddalił.
- **Wybory:**
  1. "Zapytać go o drogę do latarni morskiej." -> `final_dobry`  [warunek: wymaga Sanity >= 50; porażka -> `szept`]
  2. "Wsłuchać się w szept dochodzący z lasu." -> `dziwny_szept`
  3. "Rzucić się na niego z pięściami." -> `walka_z_cieniem`

### `dziwny_szept`
- **Obrazek:** `tiles/cave_entrance.png`
- **Efekt przy wejściu:** Sanity -10
- **Zakończenie:** -
- **Tekst:**
  > Wchodzisz między drzewa, idąc za dźwiękiem. Im głębiej, tym jest wyraźniejszy - drapie po wewnętrznej stronie czaszki, sączy się w szczeliny między myślami i układa tam własne. Zaciskasz zęby, próbując oddzielić siebie od głosu, póki jeszcze wiesz, gdzie kończysz się ty, a zaczyna on.
- **Wybory:**
  1. "Spróbować pojąć szept, nie dając się porwać." -> `slodki_smiech`  [warunek: rzut k20 >= 12; porażka -> `krzyki`]

### `slodki_smiech`
- **Obrazek:** `tiles/camp.png`
- **Efekt przy wejściu:** Sanity +20
- **Zakończenie:** -
- **Tekst:**
  > W chaosie szeptu nagle odnajdujesz porządek. Spod niego wyłania się dziecięcy śmiech - jasny, beztroski, niemożliwy w tym lesie i o tej godzinie. Z powodów, których nie umiesz nazwać, śmiech ten nie przeraża cię, lecz koi. Oddychasz głębiej i czujesz, jak rozsypane myśli wracają na swoje miejsca.
- **Wybory:**
  1. "Wrócić na rozstaje." -> `rozstaje`

### `krzyki`
- **Obrazek:** `tiles/evil_eyes.png`
- **Efekt przy wejściu:** Sanity -20
- **Zakończenie:** -
- **Tekst:**
  > Szept pęka jak przegniła tama. Z każdego drzewa, z każdej strony, buchają krzyki - potępieńcze, zlewające się w jeden chór, który wykrzykuje twoje imię i wylicza godzinę twojej śmierci. Cofasz się, potykając się o własne nogi, dłońmi zatykając uszy, lecz głos jest już w środku ciebie.
- **Wybory:**
  1. "Wycofać się na rozstaje." -> `rozstaje`

### `szept`
- **Obrazek:** `tiles/old_man.png`
- **Efekt przy wejściu:** Sanity -30
- **Zakończenie:** -
- **Tekst:**
  > Starzec uchyla wargi. Wypływa z nich dźwięk, który nie należy do żadnej mowy zrodzonej pod słońcem. Zwija się w tobie, schodzi niżej, niż sięga myśl, i odnajduje miejsca, o których istnieniu wolałbyś nigdy się nie dowiedzieć. Coś w tobie otwiera się na oścież i nie da się już domknąć.
- **Wybory:**
  1. "Pozwolić, by słowa wciągnęły cię w głąb." -> `final_szalenstwo`

### `walka_z_cieniem`
- **Obrazek:** `tiles/evil_eyes.png`
- **Efekt przy wejściu:** Sanity -100
- **Zakończenie:** KONIEC GRY (zly)
- **Tekst:**
  > Twoja pięść trafia w pustkę. Płaszcz opada miękko, lecz pod nim nie ma żadnego starca - jest tylko cień, który zaciska się wokół twojej piersi jak zimna obręcz. Czujesz, jak coś w środku ciebie - płomyk, którego nigdy nie nazwałeś - po prostu gaśnie.
- **Wybory:** brak (węzeł końcowy)

### `chata`
- **Obrazek:** `tiles/wood_road.png`
- **Efekt przy wejściu:** brak
- **Zakończenie:** -
- **Tekst:**
  > Drzwi ustępują z głuchym trzaskiem zmurszałego drewna. W środku stół, otwarty dziennik i mapa przyszpilona do ściany rdzawym ostrzem. Zapiski mówią o latarni morskiej na wybrzeżu - jedynym miejscu, którego mgła i to, co w niej mieszka, dotąd nie tknęły. Ktoś podkreślił te słowa tak mocno, że pióro przedarło papier.
- **Wybory:**
  1. "Wyruszyć drogą wskazaną na mapie." -> `final_dobry`

### `chata_porazka`
- **Obrazek:** `tiles/wood_road.png`
- **Efekt przy wejściu:** HP -10
- **Zakończenie:** -
- **Tekst:**
  > Drzwi nie ustępują. Napierasz ramieniem raz, drugi, trzeci, aż w boku coś chrupie sucho i ból rozlewa się po żebrach gorącą falą. Cofasz się, dysząc, a próchno drzwi zdaje się drwić z twojej słabości.
- **Wybory:**
  1. "Wrócić na rozdroże i obmyślić to na nowo." -> `rozdroze`

### `final_dobry`
- **Obrazek:** `tiles/win.png`
- **Efekt przy wejściu:** brak
- **Zakończenie:** ZWYCIĘSTWO (dobry)
- **Tekst:**
  > Latarnia wyrasta z mgły jak biały kieł wbity w gardło nocy. Światło z jej szczytu rozcina mrok, w którym tonęły lasy Arkham, i po raz pierwszy tej nocy czujesz, że ciemność się cofa. Jeśli wciąż ściskasz w dłoni wilczy kieł, dopiero teraz rozluźniasz na nim palce - talizman dotrwał z tobą do końca. Klucznik otwiera ci drzwi bez słowa i bez pytań, jakby od dawna wiedział, że przyjdziesz. Przeżyłeś - a tej nocy to więcej, niż dane było wielu.
- **Wybory:** brak (węzeł końcowy)

### `final_szalenstwo`
- **Obrazek:** `tiles/gone_mad.png`
- **Efekt przy wejściu:** Sanity -100
- **Zakończenie:** KONIEC GRY (zly)
- **Tekst:**
  > Twoje oczy są otwarte, lecz nie widzą już niczego z tego świata. Coś zajęło miejsce za nimi i to ono teraz patrzy przez ciebie - na las, na mgłę, na gwiazdy ułożone w niewłaściwym porządku. Twoje ciało brnie dalej leśnymi ścieżkami, posłuszne i ciche, ale ten, kto nim idzie, nie nosi już twojego imienia.
- **Wybory:** brak (węzeł końcowy)

## 6. Graf przejść (lista sąsiedztwa)

Dla każdego węzła: wszystkie węzły, do których można z niego trafić
(`cel` oraz `cel_porazka`).

| Węzeł | Prowadzi do |
|---|---|
| `intro` | `rozdroze` |
| `rozdroze` | `jaskinia`, `polana`, `chata`, chata_porazka (porażka) |
| `jaskinia` | `glebiny`, `rozdroze` |
| `glebiny` | `final_szalenstwo`, `jaskinia` |
| `polana` | `triumf_wilk`, kleski_wilk (porażka), `rozstaje` |
| `triumf_wilk` | `rozstaje` |
| `kleski_wilk` | `rozstaje` |
| `rozstaje` | `final_dobry`, szept (porażka), `dziwny_szept`, `walka_z_cieniem` |
| `dziwny_szept` | `slodki_smiech`, krzyki (porażka) |
| `slodki_smiech` | `rozstaje` |
| `krzyki` | `rozstaje` |
| `szept` | `final_szalenstwo` |
| `walka_z_cieniem` | - (koniec) |
| `chata` | `final_dobry` |
| `chata_porazka` | `rozdroze` |
| `final_dobry` | - (koniec) |
| `final_szalenstwo` | - (koniec) |

## 7. Testy losowe i warunkowe

| Węzeł | Wybór | Test | Sukces -> | Porażka -> |
|---|---|---|---|---|
| `rozdroze` | Naprzeć ramieniem na drzwi chaty. | rzut k20 >= 12 | `chata` | `chata_porazka` |
| `polana` | Stanąć z nim do walki. | rzut k20 >= 13 | `triumf_wilk` | `kleski_wilk` |
| `rozstaje` | Zapytać go o drogę do latarni morskiej. | wymaga Sanity >= 50 | `final_dobry` | `szept` |
| `dziwny_szept` | Spróbować pojąć szept, nie dając się porwać. | rzut k20 >= 12 | `slodki_smiech` | `krzyki` |

## 8. Zakończenia

- **`walka_z_cieniem`** - KONIEC GRY (zly); efekt wejścia: Sanity -100.
- **`final_dobry`** - ZWYCIĘSTWO (dobry); efekt wejścia: brak.
- **`final_szalenstwo`** - KONIEC GRY (zly); efekt wejścia: Sanity -100.
- **Ciche zakończenie (zly)** - dowolny węzeł, gdy po wejściu HP <= 0 lub Sanity <= 0
  (np. wejście w `kleski_wilk` przy HP <= 25).

## 9. Motywy i ton (wskazówka stylistyczna)

Druga osoba, czas teraźniejszy. Narastający rozkład umysłu, kosmiczna
obojętność (Lovecraft) i gotycko-psychologiczny niepokój (Poe). Powracające
motywy: szept z mgły, niewłaściwe światło/geometria, latarnia jako jedyny
racjonalny ratunek, gwiazdy w niewłaściwym porządku. Sceny krótkie (3-5 zdań).
