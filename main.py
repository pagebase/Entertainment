import re
import os
import tkinter as tk
from tkinter import ttk, messagebox

# ==========================================
# BACKEND LOGIC
# ==========================================

def filter_name(name):
    """Removes symbols and spaces for searching"""
    return re.sub(r"[^a-z0-9]", "", name.lower())

def get_filename(category):
    """Routes the dropdown choice to the correct Markdown file"""
    files = {
        "Movie": "Movies.md", 
        "TV Show": "TV_Shows.md", 
        "Book": "Books.md" # This replaces your "Option 6" logic!
    }
    return files.get(category)

def add_entry(category, name, url):
    """Handles Adding Movies, TV Shows, and Books based on category chosen"""
    file_name = get_filename(category)
    try:
        # Create file if it doesn't exist to prevent errors
        if not os.path.exists(file_name):
            with open(file_name, 'w', encoding="utf-8") as f:
                pass
                
        # Read the file to figure out the next serial number
        with open(file_name, 'r', encoding="utf-8") as f1:
            text = f1.read()
            patt = r"(\d+\.)"
            raw_sr_number = re.findall(patt, text)
            
            if raw_sr_number:
                temp = re.sub(r"[^0-9]", '', raw_sr_number[-1])
                temp = int(temp) + 1
            else:
                temp = 1 # Start at 1 if the file is completely empty
                
        # Append the new entry
        with open(file_name, 'a', encoding="utf-8") as f2:
            f2.write(f"{temp}. [{name}]({url})\n")
            
        return True, f"Successfully added '{name}' to {category}s."
    except Exception as e:
        return False, str(e)

def search_entry(category, search_term):
    """Handles searching across all categories"""
    file_name = get_filename(category)
    
    # If the file hasn't been created yet, return nothing
    if not os.path.exists(file_name):
        return []

    try:
        with open(file_name, "r", encoding="utf-8") as file:
            file_content = file.read()
            
        pattern = r"\[(.*?)\]"
        filtered_file_content = re.findall(pattern, file_content)
        
        filtered_search = filter_name(search_term)
        key_value_pair = {filter_name(item): item for item in filtered_file_content}
        
        # Return all matching items
        result = [value for key, value in key_value_pair.items() if filtered_search in key]
        return result
    except Exception as e:
        print(e)
        return []

# ==========================================
# GUI APPLICATION (FRONTEND)
# ==========================================

class MediaManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Manager")
        self.root.geometry("500x450")
        self.root.config(padx=20, pady=20)

        # Style
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 11))
        style.configure("TButton", font=("Arial", 10))

        # Variables
        self.category_var = tk.StringVar(value="Movie")
        self.name_var = tk.StringVar()
        self.url_var = tk.StringVar()

        # --- UI Elements ---
        
        # Category Dropdown (Notice "Book" is included here)
        ttk.Label(root, text="Select Category:").grid(row=0, column=0, sticky="w", pady=5)
        self.category_dropdown = ttk.Combobox(root, textvariable=self.category_var, values=["Movie", "TV Show", "Book"], state="readonly")
        self.category_dropdown.grid(row=0, column=1, sticky="ew", pady=5)

        # Name Input
        ttk.Label(root, text="Name (Title):").grid(row=1, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(root, textvariable=self.name_var, width=40)
        self.name_entry.grid(row=1, column=1, sticky="ew", pady=5)

        # URL Input
        ttk.Label(root, text="Trailer/Link URL:\n(Leave blank if searching)").grid(row=2, column=0, sticky="w", pady=5)
        self.url_entry = ttk.Entry(root, textvariable=self.url_var, width=40)
        self.url_entry.grid(row=2, column=1, sticky="ew", pady=5)

        # Buttons Frame
        btn_frame = ttk.Frame(root)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)

        ttk.Button(btn_frame, text="Search", command=self.handle_search, width=15).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Add New", command=self.handle_add, width=15).pack(side="left", padx=10)

        # Output Text Area
        ttk.Label(root, text="Output / Results:").grid(row=4, column=0, sticky="w", pady=5)
        self.output_text = tk.Text(root, height=10, width=50, state="disabled", font=("Courier", 10))
        self.output_text.grid(row=5, column=0, columnspan=2, sticky="ew")

        # Make column 1 expand with the window size
        root.grid_columnconfigure(1, weight=1)

    def log_output(self, text):
        """Helper to write to the text widget"""
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.config(state="disabled")

    def handle_search(self):
        category = self.category_var.get()
        search_term = self.name_var.get().strip()
        
        if not search_term:
            messagebox.showwarning("Input Error", "Please enter a name to search.")
            return

        results = search_entry(category, search_term)
        
        if results:
            output_msg = f"--- Search Results for '{search_term}' ---\n\n"
            for res in results:
                output_msg += f"- {res}\n"
            self.log_output(output_msg)
        else:
            self.log_output(f"No {category} found matching '{search_term}'.")

    def handle_add(self):
        category = self.category_var.get()
        name = self.name_var.get().strip().capitalize()
        url = self.url_var.get().strip()

        if not name or not url:
            messagebox.showwarning("Input Error", "Both Name and URL are required to add an entry.")
            return

        success, message = add_entry(category, name, url)
        
        if success:
            self.log_output(message)
            # Clear inputs on success
            self.name_var.set("")
            self.url_var.set("")
        else:
            messagebox.showerror("Error", f"Failed to add entry:\n{message}")

# ==========================================
# ENTRY POINT
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = MediaManagerApp(root)
    root.mainloop()
