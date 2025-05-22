import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk # Pro tematické GUI
import requests # Pro HTTP požadavky (načítání dat z API)
import threading # Pro načítání dat na pozadí, aby aplikace nezamrzala

# Globální proměnná pro ukládání dat o státech
countries_data = []

def fetch_countries_data():
    """
    Načte data o státech z REST Countries API.
    Tato funkce běží v samostatném vlákně, aby neblokovala GUI.
    """
    global countries_data
    try:
        status_label.config(text="⏳ Loading country data...") # UI zůstává anglicky
        root.update_idletasks() # Okamžitá aktualizace GUI
        # Načítání běžného názvu, populace a cca2 kódu pro všechny státy
        response = requests.get("https://restcountries.com/v3.1/all?fields=name,population,cca2", timeout=15)
        response.raise_for_status()  # Zkontroluje, zda požadavek proběhl úspěšně
        data = response.json()

        # Seřadí státy abecedně podle jejich běžného názvu
        countries_data = sorted(
            [{"name": country["name"]["common"], "population": country["population"], "code": country["cca2"]} for country in data],
            key=lambda x: x["name"]
        )
        update_countries_listbox() # Aktualizuje seznam států v GUI
        status_label.config(text="✅ Data loaded successfully.") # UI zůstává anglicky
    except requests.exceptions.Timeout:
        messagebox.showerror("Error", "The request timed out while loading data. Please try again later.") # UI zůstává anglicky
        status_label.config(text="❌ Error: Timeout loading data.") # UI zůstává anglicky
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to load data: {e}") # UI zůstává anglicky
        status_label.config(text="❌ Error loading data.") # UI zůstává anglicky
    except Exception as e: # Zachytí jakékoli jiné neočekávané chyby
        messagebox.showerror("Error", f"An unexpected error occurred: {e}") # UI zůstává anglicky
        status_label.config(text="❌ An unexpected error occurred.") # UI zůstává anglicky

def update_countries_listbox(filter_text=""):
    """
    Aktualizuje seznam států v Listboxu na základě filtrovaného textu.
    """
    countries_listbox.delete(0, tk.END)  # Vymaže aktuální seznam
    
    if not countries_data and not filter_text: # Pokud data ještě nebyla načtena
        countries_listbox.insert(tk.END, "Loading data, please wait...") # UI zůstává anglicky
        return

    # Filtruje státy na základě vyhledávacího textu (nerozlišuje malá a velká písmena)
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
    selected_indices = countries_listbox.curselection()
    if not selected_indices: # Pokud nic není vybráno
        return

    # Zajistí, aby get() nevyvolal chybu, pokud je listbox prázdný nebo obsahuje zprávu
    try:
        selected_country_name = countries_listbox.get(selected_indices[0])
    except tk.TclError:
        population_label.config(text="Population: -") # UI zůstává anglicky
        return

    # Pokud listbox obsahuje zprávu (např. "Loading data..."), nic nedělej
    if selected_country_name in ["Loading data, please wait...", "No countries found for the given filter."]: # UI zůstává anglicky
        population_label.config(text="Population: -") # UI zůstává anglicky
        return

    # Najde data pro vybraný stát
    # Zohlední aktuálně filtrovaný seznam, pokud je aktivní vyhledávání
    filter_text = search_var.get()
    target_list = [c for c in countries_data if filter_text.lower() in c["name"].lower()] if filter_text else countries_data
    
    country_data = next((country for country in target_list if country["name"] == selected_country_name), None)

    if country_data:
        # Formátuje číslo populace s oddělovači tisíců
        population_label.config(text=f"Population: {country_data['population']:,}") # UI zůstává anglicky
    else:
        # Toto by se ideálně nemělo stát, pokud je seznam synchronizovaný
        population_label.config(text="Population: Data not found") # UI zůstává anglicky


def on_search_change(*args):
    """
    Aktualizuje seznam států při změně textu ve vyhledávacím poli.
    """
    filter_text = search_var.get()
    update_countries_listbox(filter_text)
    if not filter_text: # Pokud je vyhledávací pole prázdné, zobrazí se všechny státy
        population_label.config(text="Population: -") # Resetuje popisek populace
    elif not countries_listbox.size() or countries_listbox.get(0) == "No countries found for the given filter.": # UI zůstává anglicky
        population_label.config(text="Population: -") # Resetuje, pokud nejsou žádné výsledky
    # Jinak ponechá populaci, pokud je něco vybráno a stále viditelné

# --- Nastavení hlavního okna ---
# root = tk.Tk() # Původní
root = ThemedTk(theme="arc") # Použití ttkthemes, zkus např. "plastik", "arc", "ubuntu", "smog"
root.title("World Countries Information") # UI zůstává anglicky
root.geometry("600x650") # Trochu větší okno

# --- Styly ---
style = ttk.Style()
# Můžeš si pohrát s fonty globálně pro ttk widgety, pokud to téma dovolí
# style.configure('.', font=('Segoe UI', 10)) # 'Segoe UI' je pěkný font ve Windows
# style.configure('TLabel', font=('Segoe UI', 10))
# style.configure('TButton', font=('Segoe UI', 10))
# style.configure('TEntry', font=('Segoe UI', 10))

# --- GUI Prvky ---
main_frame = ttk.Frame(root, padding="15 15 15 15") # Hlavní rámeček s odsazením
main_frame.pack(fill=tk.BOTH, expand=True)

# Rámeček pro vyhledávání
search_frame = ttk.Frame(main_frame, padding="0 0 0 10") # (left, top, right, bottom)
search_frame.pack(fill=tk.X)

ttk.Label(search_frame, text="🔎 Search Country:", font=('Segoe UI', 11)).pack(side=tk.LEFT, padx=(0, 8)) # UI zůstává anglicky
search_var = tk.StringVar()
search_var.trace_add("write", on_search_change) # Zavolá on_search_change při každé změně
search_entry = ttk.Entry(search_frame, textvariable=search_var, font=('Segoe UI', 11), width=40)
search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
search_entry.focus() # Nastaví kurzor do vyhledávacího pole při spuštění

# Rámeček pro seznam států a posuvník
list_frame = ttk.Frame(main_frame, padding="0 10 0 10")
list_frame.pack(fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
# Stále používáme tk.Listbox, protože ttk.Treeview je složitější pro jednoduchý seznam
# ale nastavíme mu fonty a barvy, aby lépe ladily s tématem
listbox_font = ('Segoe UI', 12)
countries_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=15,
                               selectmode=tk.SINGLE, font=listbox_font,
                               relief=tk.FLAT, borderwidth=1,
                               highlightthickness=1, highlightbackground="#cccccc") # Jemný okraj

# Pokus o nastavení barev Listboxu tak, aby ladily s ttk tématem
# Tyto hodnoty bude možná potřeba upravit podle zvoleného tématu
try:
    bg_color = style.lookup('TFrame', 'background')
    fg_color = style.lookup('TLabel', 'foreground')
    # Použití barev výběru z TCombobox jako náhrady pro výběr v Listboxu
    select_bg = style.lookup('TCombobox', 'selectbackground') 
    select_fg = style.lookup('TCombobox', 'selectforeground')

    countries_listbox.configure(bg=bg_color, fg=fg_color,
                                selectbackground=select_bg, selectforeground=select_fg)
except tk.TclError:
    # Pokud se nepodaří získat barvy z tématu (např. pro starší témata), použijí se výchozí
    pass

scrollbar.config(command=countries_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
countries_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

countries_listbox.bind("<<ListboxSelect>>", on_country_select) # Zavolá on_country_select při výběru položky

# Popisek pro zobrazení populace
population_label = ttk.Label(main_frame, text="Population: -", font=("Segoe UI", 16, "bold"), anchor=tk.CENTER, padding="10 15 10 10") # UI zůstává anglicky
population_label.pack(fill=tk.X)

# Stavový řádek
status_frame = ttk.Frame(root, relief=tk.SUNKEN, padding=0) # Rámeček pro stavový řádek
status_frame.pack(side=tk.BOTTOM, fill=tk.X)
status_label = ttk.Label(status_frame, text="Ready.", padding="5 2 5 2", anchor=tk.W, font=('Segoe UI', 9)) # UI zůstává anglicky, padding (left, top, right, bottom)
status_label.pack(fill=tk.X)

# --- Spuštění načítání dat na pozadí ---
# Použití vlákna, aby GUI nezamrzlo během načítání dat
threading.Thread(target=fetch_countries_data, daemon=True).start()

# --- Spuštění hlavní smyčky aplikace ---
root.mainloop()