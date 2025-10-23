import tkinter as tk
from tkinter import filedialog
import re
import subprocess
import os

cwd = os.getcwd()

KEYWORDS = ["int", "string", "byte", "null"]
VARS = ["var", "uvar", "resvar"]
FUNCTIONS = ["output", "read", "subroutine", "exit", "inc", "set", "bset", "bcopy", "scopy", "add", "sub", "cresvar"]
LOGICAL_OPERATORS = ["i==", "b==", "i>", "if", "else"]
WORKFLOW_OPERATORS = ["finish", "ret", "goto", "run", "return", "exit"]
INSERTS = ["<<"]
BOOLEANS = ["true", "false", "btrue", "bfalse"]

open_project = ""

THEME_LIGHT = {
    "background": "#ffffff",
    "foreground": "#000000",
    "editor_bg": "#ffffff",
    "editor_fg": "#000000",
    "output_bg": "#f0f0f0",
    "output_fg": "#000000",
    "highlight": {
        "keyword": "#ff007f",
        "vars": "#7506ba",
        "functions": "#0b8f04",
        "logical": "#048f81",
        "workflow": "#8f0404",
        "inserts": "#8f044e",
        "booleans": "#27048f",
        "string": "#a67b05",
        "number": "#0000ff",
    },
}

THEME_DARK = {
    "background": "#1e1e1e",
    "foreground": "#ffffff",
    "editor_bg": "#1e1e1e",
    "editor_fg": "#ffffff",
    "output_bg": "#252526",
    "output_fg": "#d4d4d4",
    "highlight": {
        "keyword": "#ff79c6",
        "vars": "#7506ba",
        "functions": "#50fa7b",
        "logical": "#8be9fd",
        "workflow": "#ff5555",
        "inserts": "#ffb86c",
        "booleans": "#8be9fd",
        "string": "#f1fa8c",
        "number": "#0000ff",
    },
}

current_theme = THEME_LIGHT
dark_mode = False

def build_project():
    if open_project != "":
        filepath = open_project
    else:
        filepath = filedialog.askopenfilename(
            filetypes=[("MyLang Files", "*.pok"), ("All Files", "*.*")]
        )
    if not filepath:
        return
    
    filepath = filepath.replace(".pok", "")

    commands = [
        f"python compiler.py {filepath}"
    ]

    output_text.delete("1.0", tk.END)
    for cmd in commands:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            output_text.insert(tk.END, f"> {cmd}\n")
            output_text.insert(tk.END, result.stdout)
            if result.stderr:
                output_text.insert(tk.END, result.stderr)
        except Exception as e:
            output_text.insert(tk.END, f"Error running command: {e}\n")


def highlight(event=None):
    text = editor.get("1.0", tk.END)
    for tag in editor.tag_names():
        editor.tag_remove(tag, "1.0", tk.END)

    colors = current_theme["highlight"]

    def highlight_words(words, color, bold=False):
        for word in words:
            if re.match(r'^[A-Za-z0-9_]+$', word):
                pattern = rf'\b{re.escape(word)}\b'
            else:
                pattern = re.escape(word)

            for match in re.finditer(pattern, text):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                editor.tag_add(word, start, end)
                font = ("Consolas", 12, "bold") if bold else ("Consolas", 12)
                editor.tag_config(word, foreground=color, font=font)

    highlight_words(KEYWORDS, colors["keyword"], bold=True)
    highlight_words(VARS, colors["vars"], bold=True)
    highlight_words(FUNCTIONS, colors["functions"])
    highlight_words(LOGICAL_OPERATORS, colors["logical"])
    highlight_words(WORKFLOW_OPERATORS, colors["workflow"])
    highlight_words(INSERTS, colors["inserts"])
    highlight_words(BOOLEANS, colors["booleans"])

    for match in re.finditer(r'\boutput\b.*', text):
        output_keyword_len = len('output ')
        start_index = match.start() + output_keyword_len
        end_index = match.end()
        start = f"1.0 + {start_index} chars"
        end = f"1.0 + {end_index} chars"
        editor.tag_add("string", start, end)
        editor.tag_config("string", foreground=colors["string"])

    for match in re.finditer(r'\b\d+\b', text):
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        editor.tag_add("number", start, end)
        editor.tag_config("number", foreground=colors["number"])


def save_file():
    global open_project

    if open_project != "":
        filepath = open_project
    else:
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pok",
            filetypes=[("pok Files", "*.pok"), ("All Files", "*.*")]
        )

        open_project = filepath

    if filepath:
        with open(filepath, "w") as file:
            file.write(editor.get("1.0", tk.END))

def load_file():
    global open_project

    filepath = filedialog.askopenfilename(
        filetypes=[("pok Files", "*.pok"), ("All Files", "*.*")]
    )

    if filepath:
        with open(filepath, "r") as file:
            content = file.read()
        editor.delete("1.0", tk.END)
        editor.insert(tk.END, content)
        highlight()

        open_project = filepath


def toggle_dark_mode():
    global dark_mode, current_theme
    dark_mode = not dark_mode
    current_theme = THEME_DARK if dark_mode else THEME_LIGHT
    apply_theme()


def apply_theme():
    colors = current_theme
    root.config(bg=colors["background"])
    editor.config(
        bg=colors["editor_bg"],
        fg=colors["editor_fg"],
        insertbackground=colors["foreground"]
    )
    output_text.config(
        bg=colors["output_bg"],
        fg=colors["output_fg"],
        insertbackground=colors["foreground"]
    )
    highlight()

root = tk.Tk()
root.title("pok IDE")
root.geometry("800x600")

editor_frame = tk.Frame(root)
editor_frame.pack(fill="both", expand=True)

scrollbar = tk.Scrollbar(editor_frame)
scrollbar.pack(side="right", fill="y")

editor = tk.Text(editor_frame, wrap="word", font=("Consolas", 12))
editor.pack(fill="both", expand=True)
editor.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=editor.yview)

editor.bind("<KeyRelease>", highlight)

menu = tk.Menu(root)

file_menu = tk.Menu(menu, tearoff=0)
file_menu.add_command(label="Open", command=load_file)
file_menu.add_command(label="Save", command=save_file)
menu.add_cascade(label="File", menu=file_menu)

view_menu = tk.Menu(menu, tearoff=0)
view_menu.add_checkbutton(label="Dark Mode", command=toggle_dark_mode)
menu.add_cascade(label="View", menu=view_menu)

root.config(menu=menu)

bottom_frame = tk.Frame(root)
bottom_frame.pack(fill="x")

build_button = tk.Button(bottom_frame, text="Build", command=build_project)
build_button.pack(side="left", padx=5, pady=5)

output_text = tk.Text(bottom_frame, height=10, font=("Consolas", 10))
output_text.pack(fill="both", expand=True, padx=5, pady=5)

apply_theme()
root.mainloop()
