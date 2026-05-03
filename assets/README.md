# Folder assets/ - grafiki sceny

Tu wrzucasz pliki PNG dla scen. Nazwy musza pasowac do tego co jest w `data/story.json`
w polu `obrazek` (np. `assets/start.png`).

Lista wymaganych plikow (12 sztuk):

- `start.png`         - skraj obozu, mgla, trzy sciezki
- `jaskinia.png`      - wejscie do jaskini
- `oboz.png`          - opuszczony oboz, koc, dziennik
- `przed_chata.png`   - zamknieta chata w lesie
- `chata.png`         - wnetrze chaty z mapa
- `glebiny.png`       - mroczne glebiny jaskini, ksztalt potwora
- `ucieczka.png`      - ucieczka w panice
- `rozstaje.png`      - rozstaje, starzec w plaszczu
- `szept.png`         - twarz starca, szepty
- `final_dobry.png`   - latarnia morska, swit
- `final_zly.png`     - mgla, ciemnosc

Format: PNG (tkinter natywnie obsluguje PNG od Pythona 3.9). Zalecany rozmiar: 400x250 px.

Jezeli plik PNG nie istnieje, gra po prostu pomija obrazek - dziala dalej.
