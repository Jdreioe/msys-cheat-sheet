import tkinter as tk
from tkinter import messagebox

def parse_hex_bin_int(value_str):
    """Helper to parse hex (0x...), binary (0b...), or decimal strings."""
    value_str = value_str.strip()
    if not value_str:
        return 0 # Default to 0 for empty input to avoid ValueError later
    try:
        if value_str.lower().startswith("0x"):
            return int(value_str, 16)
        elif value_str.lower().startswith("0b"):
            return int(value_str, 2)
        else:
            return int(value_str)
    except ValueError:
        raise ValueError(f"Ugyldigt talformat: '{value_str}'")

def show_error(title, message):
    messagebox.showerror(title, message)

def show_warning(title, message):
    messagebox.showwarning(title, message)