import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import requests
import threading
import os
import sys

# --- Pomocná funkce pro PyInstaller (cesta k prostředkům) ---
def resource_path(relative_path):
    """ Získá absolutní cestu k prostředku, funguje pro vývoj i pro PyInstaller """
    try:
        # PyInstaller vytváří dočasnou složku a ukládá cestu do _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError: # Správnější je chytat AttributeError pro _MEIPASS
        # Pokud _MEIPASS neexistuje (např. při běžném spuštění .py skriptu),
        # použije se aktuální pracovní adresář skriptu.
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Globální proměnná pro data o státech ---
countries_data = []

# --- Funkce pro načítání a zpracování dat ---
def fetch_countries_data():
    """
    Načte data o státech z REST Countries API.
    Tato funkce běží v samostatném vlákně, aby neblokovala GUI.
    """
    global countries_data
    try:
        # Zkontrolujeme, zda status_label existuje, než ho použijeme
        # (je definován později v GUI části)
        if 'status_label' in globals() and status_label:
            status_label.config(text="⏳ Loading country data...") # UI zůstává anglicky
        if 'root' in globals() and root: # Zajistíme, že root existuje
            root.update_idletasks() # Okamžitá aktualizace GUI
        
        response = requests.get("https://restcountries.com/v3.1/all?fields=name,population,cca2", timeout=15)
        response.raise_for_status()  # Zkontroluje, zda požadavek proběhl úspěšně
        data = response.json()

        countries_data = sorted(
            [{"name": country["name"]["common"], "population": country["population"], "code": country["cca2"]} for country in data],
            key=lambda x: x["name"]
        )
        # Ujistíme se, že listbox existuje před aktualizací
        if 'countries_listbox' in globals() and countries_listbox:
            update_countries_listbox() # Aktualizuje seznam států v GUI
        
        if 'status_label' in globals() and status_label:
            status_label.config(text="✅ Data loaded successfully.") # UI zůstává anglicky
            
    except requests.exceptions.Timeout:
        messagebox.showerror("Error", "The request timed out while loading data. Please try again later.") # UI zůstává anglicky
        if 'status_label' in globals() and status_label:
            status_label.config(text="❌ Error: Timeout loading data.") # UI zůstává anglicky
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to load data: {e}") # UI zůstává anglicky
        if 'status_label' in globals() and status_label:
            status_label.config(text="❌ Error loading data.") # UI zůstává anglicky
    except Exception as e: # Zachytí jakékoli jiné neočekávané chyby
        messagebox.showerror("Error", f"An unexpected error occurred: {e}") # UI zůstává anglicky
        if 'status_label' in globals() and status_label:
            status_label.config(text="❌ An unexpected error occurred.") # UI zůstává anglicky

def update_countries_listbox(filter_text=""):
    """
    Aktualizuje seznam států v Listboxu na základě filtrovaného textu.
    """
    # Tato funkce předpokládá, že countries_listbox již existuje
    countries_listbox.delete(0, tk.END)  # Vymaže aktuální seznam
    
    if not countries_data and not filter_text: # Pokud data ještě nebyla načtena
        countries_listbox.insert(tk.END, "Loading data, please wait...") # UI zůstává anglicky
        return

    filtered_countries = [
        country for country in countries_data 
        if filter_text.lower() in country["name"].lower()
    ]
    
    if not filtered_countries:
        countries_listbox.insert(tk.END, "No countries found for the given filter.") # UI zůstává anglicky
    else:
        for country in filtered_countries:
            countries_listbox.insert(tk.END, country["name"])

def on_country_select(event):
    """
    Zobrazí populaci vybraného státu.
    Spustí se při kliknutí na stát v Listboxu.
    """
    # Tato funkce předpokládá, že countries_listbox a population_label již existují
    selected_indices = countries_listbox.curselection()
    if not selected_indices: # Pokud nic není vybráno
        return

    try:
        selected_country_name = countries_listbox.get(selected_indices[0])
    except tk.TclError:
        population_label.config(text="Population: -") # UI zůstává anglicky
        return

    if selected_country_name in ["Loading data, please wait...", "No countries found for the given filter."]: # UI zůstává anglicky
        population_label.config(text="Population: -") # UI zůstává anglicky
        return

    # Tato funkce předpokládá, že search_var již existuje
    filter_text = search_var.get()
    target_list = [c for c in countries_data if filter_text.lower() in c["name"].lower()] if filter_text else countries_data
    
    country_data = next((country for country in target_list if country["name"] == selected_country_name), None)

    if country_data:
        population_label.config(text=f"Population: {country_data['population']:,}") # UI zůstává anglicky
    else:
        population_label.config(text="Population: Data not found") # UI zůstává anglicky

def on_search_change(*args):
    """
    Aktualizuje seznam států při změně textu ve vyhledávacím poli.
    """
    # Tato funkce předpokládá, že search_var, countries_listbox a population_label již existují
    filter_text = search_var.get()
    update_countries_listbox(filter_text)
    if not filter_text: 
        population_label.config(text="Population: -") 
    elif not countries_listbox.size() or countries_listbox.get(0) == "No countries found for the given filter.": # UI zůstává anglicky
        population_label.config(text="Population: -")

# --- Nastavení hlavního okna ---
root = ThemedTk(theme="arc") 
root.title("World Countries Information") # UI zůstává anglicky
root.geometry("600x650") 

# --- Nastavení ikony okna ---
# Ujisti se, že soubor 'app_icon.ico' je ve stejné složce jako skript,
# nebo pokud používáš PyInstaller s --onefile, že jsi ho přidal přes --add-data
# a že název souboru zde odpovídá.
ikona_soubor_pro_okno = 'app_icon.ico' 
try:
    path_to_icon = resource_path(ikona_soubor_pro_okno)
    root.iconbitmap(path_to_icon)
    print(f"INFO: Pokus o nastavení ikony okna z '{path_to_icon}' byl proveden.") # Ladící výpis
except tk.TclError as e:
    print(f"CHYBA při nastavování ikony okna: {e}")
    print(f"Ujisti se, že soubor '{ikona_soubor_pro_okno}' (očekávaná cesta: '{path_to_icon if 'path_to_icon' in locals() else 'neznámá'}')")
    print("existuje a je to platný .ico soubor (není poškozený, má správný formát).")
    print("Pokud používáš PyInstaller (--onefile), ujisti se, že je ikona přidána přes --add-data.")
except Exception as e_general:
    print(f"Obecná CHYBA při nastavování ikony: {e_general}")

# --- Styly ---
style = ttk.Style()
# Můžeš si pohrát s fonty globálně pro ttk widgety, pokud to téma dovolí
# style.configure('.', font=('Segoe UI', 10)) 

# --- Definice GUI Prvků ---
# Hlavní rámeček
main_frame = ttk.Frame(root, padding="15 15 15 15") 
main_frame.pack(fill=tk.BOTH, expand=True)

# Rámeček pro vyhledávání
search_frame = ttk.Frame(main_frame, padding="0 0 0 10") 
search_frame.pack(fill=tk.X)

ttk.Label(search_frame, text="🔎 Search Country:", font=('Segoe UI', 11)).pack(side=tk.LEFT, padx=(0, 8)) # UI zůstává anglicky
search_var = tk.StringVar() # Proměnná pro text z vyhledávacího pole
search_var.trace_add("write", on_search_change) 
search_entry = ttk.Entry(search_frame, textvariable=search_var, font=('Segoe UI', 11), width=40)
search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
search_entry.focus() 

# Rámeček pro seznam států
list_frame = ttk.Frame(main_frame, padding="0 10 0 10")
list_frame.pack(fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
listbox_font = ('Segoe UI', 12)
countries_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=15,
                               selectmode=tk.SINGLE, font=listbox_font,
                               relief=tk.FLAT, borderwidth=1,
                               highlightthickness=1, highlightbackground="#cccccc") 

# Pokus o nastavení barev Listboxu, aby ladily s tématem
try:
    bg_color = style.lookup('TFrame', 'background')
    fg_color = style.lookup('TLabel', 'foreground')
    select_bg = style.lookup('TCombobox', 'selectbackground') 
    select_fg = style.lookup('TCombobox', 'selectforeground')
    countries_listbox.configure(bg=bg_color, fg=fg_color,
                                selectbackground=select_bg, selectforeground=select_fg)
except tk.TclError:
    pass # Použijí se výchozí barvy, pokud téma nelze přečíst

scrollbar.config(command=countries_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
countries_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
countries_listbox.bind("<<ListboxSelect>>", on_country_select) # Při výběru položky zavolá on_country_select

# Popisek pro zobrazení populace
population_label = ttk.Label(main_frame, text="Population: -", font=("Segoe UI", 16, "bold"), anchor=tk.CENTER, padding="10 15 10 10") # UI zůstává anglicky
population_label.pack(fill=tk.X)

# Stavový řádek
status_frame = ttk.Frame(root, relief=tk.SUNKEN, padding=0) 
status_frame.pack(side=tk.BOTTOM, fill=tk.X)
status_label = ttk.Label(status_frame, text="Ready.", padding="5 2 5 2", anchor=tk.W, font=('Segoe UI', 9)) # UI zůstává anglicky
status_label.pack(fill=tk.X)

# --- Spuštění načítání dat na pozadí ---
# Vlákno se spustí až poté, co jsou všechny GUI prvky (včetně status_label) definovány
threading.Thread(target=fetch_countries_data, daemon=True).start()

# --- Spuštění hlavní smyčky aplikace (pouze jednou na konci) ---
root.mainloop()