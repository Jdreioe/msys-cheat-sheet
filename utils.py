import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio

def show_error(title, message):
    """
    Shows an error dialog with the given title and message.
    GTK4 compatible.
    """
    # GTK4: Gtk.MessageDialog is now a subclass of Gtk.Dialog and Gtk.Window
    # The constructor is simpler.
    dialog = Gtk.MessageDialog(
        # Parent window: It's good practice to set a transient_for window,
        # but for a standalone utility function, it might be omitted if the
        # application's main window isn't directly accessible here.
        # If your app has a main window instance you can pass it, e.g.,
        # transient_for=self.get_application().get_active_window(),
        # or if you have a reference to the main window, transient_for=main_window_instance
        # For now, we'll omit it if it's not readily available.
        # See note below about how to pass the parent if needed.
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.OK,
        text=title # GTK4: Use 'text' for the primary text
    )
    
    # GTK4: Use 'secondary_text' for the secondary message
    dialog.set_property("secondary_text", message) # Set secondary_text property
    
    # Optional: If you want markup in the secondary text (e.g., bold parts)
    # dialog.set_property("secondary_markup", message) 
    # In that case, you'd define message with Pango markup like:
    # message = "This is some <b>bold</b> text."

    dialog.set_modal(True) # Make it modal so user has to interact with it
    dialog.set_resizable(False) # Prevent resizing

    # GTK4: show_all() is deprecated, use present()
    dialog.present()
    
    # GTK4: run() is deprecated. Connect to response signal.
    # The response() method directly returns the response ID, but if you need to
    # keep the dialog alive until the user clicks, use a signal handler and present().
    dialog.connect("response", lambda d, r: d.destroy())

    # If you need to make it transient for the main window, you'd modify
    # your calling code, for example in main_app.py or other tabs,
    # to pass the main window reference:
    #
    # In your calling function (e.g., a method in AVRTimerCalculatorApp):
    # show_error("Fejl", f"En uventet fejl opstod: {e}", parent=self.window)
    #
    # Then modify show_error signature:
    # def show_error(title, message, parent=None):
    #     dialog = Gtk.MessageDialog(...)
    #     if parent:
    #         dialog.set_transient_for(parent)

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio

def parse_hex_bin_int(input_string):
    """
    Parses a string that can be a decimal, hexadecimal (0x prefix),
    or binary (0b prefix) integer.

    Args:
        input_string (str): The string to parse.

    Returns:
        int: The parsed integer.

    Raises:
        ValueError: If the string is not a valid integer format.
    """
    input_string = input_string.strip() # Remove leading/trailing whitespace

    if not input_string:
        raise ValueError("Input string cannot be empty.")

    try:
        if input_string.startswith("0x") or input_string.startswith("0X"):
            return int(input_string, 16) # Hexadecimal
        elif input_string.startswith("0b") or input_string.startswith("0B"):
            return int(input_string, 2)  # Binary
        else:
            return int(input_string)     # Decimal
    except ValueError:
        # Re-raise with a more informative message if parsing fails
        raise ValueError(
            f"Invalid number format: '{input_string}'. "
            "Please use decimal, 0x (hex), or 0b (binary) prefix."
        )

def show_error(title, message):
    """
    Shows an error dialog with the given title and message.
    GTK4 compatible.
    """
    dialog = Gtk.MessageDialog(
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.OK,
        text=title
    )
    
    dialog.set_property("secondary_text", message)
    dialog.set_modal(True)
    dialog.set_resizable(False)

    dialog.present()
    
    dialog.connect("response", lambda d, r: d.destroy())

def show_warning(title, message):
    """
    Shows a warning dialog with the given title and message.
    GTK4 compatible.
    """
    dialog = Gtk.MessageDialog(
        message_type=Gtk.MessageType.WARNING,
        buttons=Gtk.ButtonsType.OK,
        text=title
    )
    dialog.set_property("secondary_text", message)
    dialog.set_modal(True)
    dialog.set_resizable(False)

    dialog.present()
    dialog.connect("response", lambda d, r: d.destroy())