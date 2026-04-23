# Intefejs graficzny: Osoba 4 (cabaja_nra)import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk

# --- KONFIGURACJA ŚCIEŻKI ---
# Użyj tutaj obrazka z kaktusem podaj ścieżkę pliku gdzie się znajduje 
SCIEZKA_FOTO = r"C:\Users\cabaj\Desktop\game\pobrane.jpg"

def wybierz_tlo():
    sciezka = filedialog.askopenfilename(filetypes=[("Obrazy", "*.jpg *.png")])
    if sciezka:
        global bg_image
        nowy = Image.open(sciezka)

        # Pobranie rozdzielczości ekranu
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()

        # Dopasowanie obrazu do ekranu
        nowy = nowy.resize((screen_w, screen_h), Image.LANCZOS)

        bg_image = ImageTk.PhotoImage(nowy)
        background_label.config(image=bg_image)

def uruchom_gre():
    print("Gra startuje...")
    # Tutaj w przyszłości dodasz okno gry

root = tk.Tk()
root.title("Menu z Twoim Tłem")
root.geometry("1920x1080")

# 1. Załadowanie obrazka z Twojej ścieżki
try:
    image = Image.open(SCIEZKA_FOTO)

    # Pobranie rozdzielczości ekranu
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    # Dopasowanie obrazu do ekranu
    image = image.resize((screen_w, screen_h), Image.LANCZOS)

    bg_image = ImageTk.PhotoImage(image)
except Exception as e:
    print(f"Błąd ładowania: {e}")
    # Tło awaryjne, jeśli plik pod tym adresem nie istnieje
    bg_image = ImageTk.PhotoImage(Image.new('RGB', (1920, 1080), color='gray'))

# 2. Utworzenie tła
background_label = tk.Label(root, image=bg_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# 3. Napisy i przyciski
btn_start = ttk.Button(root, text="START GRY", width=40, command=uruchom_gre)
btn_start.place(relx=0.5, rely=0.8, anchor="center", width=400, height=60)

btn_wyjscie = tk.Button(root, text="WYJŚCIE", width=60, bg="yellow", command=root.quit)
btn_wyjscie.place(relx=0.5, rely=0.94, anchor="center", width=400, height=60)

root.mainloop()
