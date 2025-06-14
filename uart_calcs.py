import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango # Pango for font styling
import math # For rounding

# Assuming constants.py exists and CPU_FREQ_DEFAULT is defined there
# For this example, I'll define a dummy value:

# Make UartCalculator inherit from Gtk.Box to be a self-contained widget
class UartCalculator(Gtk.Box):
    def __init__(self, cpu_freq_entry): # Removed 'notebook'
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10) # Main box for the tab content
        self.cpu_freq_entry = cpu_freq_entry
        self._setup_uart_tab()

    def _setup_uart_tab(self):
        # Create a Gtk.Box for the content within the tab.
        # This acts similarly to ttk.Frame in this context.
        # Since UartCalculator itself is the tab content (Gtk.Box),
        # we append widgets directly to self.
        
        # Gtk.Frame can be used as a LabelFrame equivalent
        uart_frame = Gtk.Frame()
        # Set the label for the frame using markup for boldness
        # Instead of set_label_align, create a Gtk.Label, set its alignment, and use set_label_widget
        frame_label = Gtk.Label()
        frame_label.set_markup("<b>UART Baud Rate Calculation (Normal Mode)</b>")
        frame_label.set_halign(Gtk.Align.START) # Align the label widget itself to the start (left)
        uart_frame.set_label_widget(frame_label) # Set this custom label widget for the frame
        
        uart_frame.set_css_classes(["card"]) # Optional: style as a card if you have CSS
        
        # A Gtk.Grid is excellent for tabular layouts like your input fields
        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(10)
        grid.set_margin_start(10)
        grid.set_margin_end(10)
        grid.set_margin_top(10)
        grid.set_margin_bottom(10)
        uart_frame.set_child(grid) # Set the grid as the child of the frame
        
        self.append(uart_frame) # Add the frame to this Gtk.Box (self)

        # UI elements
        # CPU Clock Frequency

        # Desired Baud Rate
        desired_baud_label = Gtk.Label(label="Desired Baud Rate (bps):", xalign=0)
        grid.attach(desired_baud_label, 0, 1, 1, 1)
        self.uart_desired_baud_entry = Gtk.Entry()
        uart_desired_baud_rate_default = 9600
        self.uart_desired_baud_entry.set_text(str(uart_desired_baud_rate_default))
        grid.attach(self.uart_desired_baud_entry, 1, 1, 1, 1)

        # Note about U2Xn bit
        note_label = Gtk.Label(label="<i>Note: Assumes U2Xn bit is 0 (Normal Mode).</i>")
        note_label.set_use_markup(True) # Enable markup for italic text
        note_label.set_halign(Gtk.Align.START) # Align to start (left)
        grid.attach(note_label, 0, 2, 2, 1) # Span two columns

        # Calculate Button
        btn_calculate_uart = Gtk.Button(label="Calculate Baud Rate Settings")
        btn_calculate_uart.connect("clicked", self._on_calculate_uart_clicked)
        grid.attach(btn_calculate_uart, 0, 3, 2, 1) # Span two columns

        # Results - using Gtk.Label for display. Text is set directly.
        # UBRRn Value
        grid.attach(Gtk.Label(label="UBRRn Value (approx.):", xalign=0), 0, 4, 1, 1)
        self.uart_result_ubrr_label = Gtk.Label(label="", xalign=0)
        self.uart_result_ubrr_label.set_css_classes(["monospace", "dim-label"]) # Custom CSS class for styling
        grid.attach(self.uart_result_ubrr_label, 1, 4, 1, 1)

        # Actual Baud Rate
        grid.attach(Gtk.Label(label="Actual Baud Rate:", xalign=0), 0, 5, 1, 1)
        self.uart_result_actual_baud_label = Gtk.Label(label="", xalign=0)
        self.uart_result_actual_baud_label.set_css_classes(["success", "monospace"]) # Green-like text
        grid.attach(self.uart_result_actual_baud_label, 1, 5, 1, 1)

        # Baud Rate Error
        grid.attach(Gtk.Label(label="Baud Rate Error:", xalign=0), 0, 6, 1, 1)
        self.uart_result_baud_error_label = Gtk.Label(label="", xalign=0)
        self.uart_result_baud_error_label.set_css_classes(["error", "monospace"]) # Red-like text
        grid.attach(self.uart_result_baud_error_label, 1, 6, 1, 1)

    def _calculate_ubrr(self, cpu_freq_hz, desired_baud_rate):
        """Calculates UBRRn, actual baud rate, and error for UART."""
        # Use a small epsilon to avoid division by zero or near-zero if desired_baud_rate is tiny
        if desired_baud_rate <= 0:
            return None, None, None

        ubrr_float = (cpu_freq_hz / (16 * desired_baud_rate)) - 1

        if ubrr_float < 0:
            return None, None, None # Indicate error if result is negative

        ubrr_int = round(ubrr_float)
        # Check if ubrr_int is within the valid range for UBRRn (0 to 4095 for 12-bit register)
        if not (0 <= ubrr_int <= 4095):
            return None, None, None

        actual_baud_rate = cpu_freq_hz / (16 * (ubrr_int + 1))
        
        # Avoid division by zero if desired_baud_rate is effectively zero
        if desired_baud_rate == 0:
            error_percent = float('inf') # Or handle as a specific error state
        else:
            error_percent = ((actual_baud_rate - desired_baud_rate) / desired_baud_rate) * 100

        return ubrr_int, actual_baud_rate, error_percent

    def _on_calculate_uart_clicked(self, button):
        try:
            cpu_freq_mhz = float(self.cpu_freq_entry.get_text())  
            desired_baud_rate = float(self.uart_desired_baud_entry.get_text())

            cpu_freq_hz = cpu_freq_mhz * 1_000_000

            ubrr_int, actual_baud_rate, error_percent = self._calculate_ubrr(cpu_freq_hz, desired_baud_rate)

            if ubrr_int is None:
                self._show_message_dialog("Error", "Desired Baud Rate is too high/low for the given CPU Frequency, or result is out of UBRRn range (0-4095).", Gtk.MessageType.ERROR)
                self.uart_result_ubrr_label.set_text("N/A")
                self.uart_result_actual_baud_label.set_text("N/A")
                self.uart_result_baud_error_label.set_text("N/A")
                return

            self.uart_result_ubrr_label.set_text(f"{ubrr_int}")
            self.uart_result_actual_baud_label.set_text(f"{actual_baud_rate:.2f} bps")
            self.uart_result_baud_error_label.set_text(f"{error_percent:.2f}%")

            if abs(error_percent) > 2: # Common tolerance for UART baud rates
                self._show_message_dialog("Baud Rate Warning",
                                           f"The calculated baud rate error is {error_percent:.2f}%.\n"
                                           "This might be too high for reliable communication.",
                                           Gtk.MessageType.WARNING)

        except ValueError:
            self._show_message_dialog("Invalid Input", "Please enter valid numbers for CPU Frequency and Desired Baud Rate.", Gtk.MessageType.ERROR)
        except Exception as e:
            self._show_message_dialog("Error", f"An unexpected error occurred: {e}", Gtk.MessageType.ERROR)

    def _show_message_dialog(self, title, message, message_type):
        # Combine title and message into a single text string
        full_message_text = f"<b>{title}</b>\n\n{message}" # Use Pango markup for bold title

        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=message_type,
            buttons=Gtk.ButtonsType.OK,
            text=full_message_text # Pass the combined text here
        )
        # dialog.set_secondary_text(message) # THIS LINE IS REMOVED
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()

# To run this example independently:
if __name__ == "__main__":
    class MainWindow(Gtk.ApplicationWindow):
        def __init__(self, app):
            super().__init__(application=app, title="UART Calculator Example")
            self.set_default_size(500, 400) # Set a default size for the window

            self.notebook = Gtk.Notebook()
            self.set_child(self.notebook) # Set the notebook as the main content of the window

            # Instantiate UartCalculator and append it to the notebook
            uart_calc_tab = UartCalculator(cpu_freq_entry=1_000_000)  # Example CPU frequency in Hz
            self.notebook.append_page(uart_calc_tab, Gtk.Label(label="UART"))

    class App(Gtk.Application):
        def __init__(self):
            super().__init__(application_id="org.example.uartcalculator")

        def do_activate(self):
            win = self.props.active_window
            if not win:
                win = MainWindow(self)
            win.present()

    app = App()
    app.run(None)