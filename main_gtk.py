import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, Pango, GObject, Gdk # Import Gdk for Gdk.Display
import sys
import json

# Import all your tabs (assuming these files exist and are correct)
from Bit_Shift_Rotate_Tab import BitShiftRotateTab
# VIRKER IKKE from c_asm_converter_tab import CAsmConverterTab
from prescaler_top_calc import PrescalerTOPCalculator
from forward_timer_calcs import ForwardTimerCalculations
from reverse_calc_tab import ReverseCalculatorTab
from mega2560_stack_tab import Mega2560StackTab
from constants import CPU_FREQ_DEFAULT
from info_tab_main import InfoTab
from uart_calcs import UartCalculator as UartCalculationsTab
from initializer import InitializerTab
# VIRKER IKKE from duty_cycle_tab import DutyCycleCalculatorTab
from adc_calcs import AdcCalculator

class MainWindow(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.AVRTimerCalculator",
                         flags=Gio.ApplicationFlags.HANDLES_OPEN)
        self.window = None
        self._cpu_freq_entry_internal = None
        self.stack = None
        self.config_file = "config.json"
        self.main_paned = None # Store reference to the main Gtk.Paned widget
        self.sidebar_scrolled_window = None # Store reference to the sidebar's scrolled window
        # Stores the last valid position of the paned, used when showing the sidebar again
        self.last_valid_paned_position = 200

    @property
    def cpu_freq_entry(self):
        """Getter for cpu_freq_entry."""
        return self._cpu_freq_entry_internal

    @cpu_freq_entry.setter
    def cpu_freq_entry(self, value):
        """Setter for cpu_freq_entry, with debug prints for type changes."""
        old_value = self._cpu_freq_entry_internal
        self._cpu_freq_entry_internal = value
        if old_value is None:
            print(f"DEBUG: Initial assignment of self.cpu_freq_entry. Type: {type(value)}", file=sys.stderr)
        elif type(old_value) != type(value):
            print(f"DEBUG: !!! TYPE CHANGE !!! self.cpu_freq_entry changed from {type(old_value)} to {type(value)}", file=sys.stderr)
            print(f"DEBUG: New value: {value}", file=sys.stderr)
        else:
            print(f"DEBUG: self.cpu_freq_entry reassigned. Type: {type(value)}", file=sys.stderr)

    def do_startup(self):
        """Called when the application starts up."""
        Gtk.Application.do_startup(self)

        # Load custom CSS for textview and sidebar styling
        css_provider = Gtk.CssProvider()
        css_data = """
        textview {
            background-color: lightblue;
            font-family: monospace;
            font-size: 14pt;
            color: darkgreen;
        }
        stacksidebar {
            min-width: 150px; /* Ensure sidebar labels are readable */
            font-size: 12pt; /* Slightly smaller font for better fit */
            padding: 5px; /* Add padding for better appearance */
        }
        """
        css_provider.load_from_string(css_data)
        # Use Gdk.Display.get_default() for robust display access
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def load_paned_position(self):
        """
        Load the saved paned position from config file.
        Ensures a minimum position of 150 pixels.
        """
        try:
            with open(self.config_file, "r") as f:
                pos = json.load(f).get("paned_position", 200)
                # Update last_valid_paned_position with the loaded or default value
                self.last_valid_paned_position = max(150, pos)
                return self.last_valid_paned_position
        except (FileNotFoundError, json.JSONDecodeError):
            return 200  # Default position if file not found or corrupted

    def save_paned_position(self, paned, param):
        """
        Save the paned position to config file.
        This method is connected to the "notify::position" signal of the paned.
        It only saves the position if the sidebar is currently visible and the
        position is reasonable (>= 150). This prevents saving '0' when the sidebar
        is hidden programmatically.
        """
        current_position = paned.get_position()
        if self.sidebar_scrolled_window and self.sidebar_scrolled_window.get_visible():
            if current_position >= 150:
                self.last_valid_paned_position = current_position
                try:
                    with open(self.config_file, "w") as f:
                        json.dump({"paned_position": self.last_valid_paned_position}, f)
                    print(f"DEBUG: Saved paned position: {self.last_valid_paned_position}", file=sys.stderr)
                except IOError as e:
                    print(f"ERROR: Could not save config file: {e}", file=sys.stderr)

    def on_window_width_changed(self, widget, param):
        """
        Called when the window's width changes (via notify::width signal).
        Handles hiding/showing the sidebar based on the window's allocated width.
        'widget' is the Gtk.ApplicationWindow, and 'param' is the GParamSpec for 'width'.
        """
        window_width = widget.get_width() # Get the current width of the window

        print(f"DEBUG: on_window_width_changed called. Current window_width: {window_width}", file=sys.stderr)

        # Ensure sidebar_scrolled_window is initialized before proceeding
        if self.sidebar_scrolled_window is None:
            print("DEBUG: sidebar_scrolled_window is None, returning.", file=sys.stderr)
            return

        if window_width < 250:
            # Hide sidebar if it's currently visible and window is too narrow
            if self.sidebar_scrolled_window.get_visible():
                self.sidebar_scrolled_window.set_visible(False)
                print(f"DEBUG: Hiding sidebar because window width ({window_width}px) < 250px.", file=sys.stderr)
        else:
            # Show sidebar if it's currently hidden and window is wide enough
            if not self.sidebar_scrolled_window.get_visible():
                self.sidebar_scrolled_window.set_visible(True)
                print(f"DEBUG: Showing sidebar because window width ({window_width}px) >= 250px.", file=sys.stderr)
                # Restore last valid paned position if it was programmatically hidden
                # (i.e., current position is very small, near 0)
                if self.main_paned and self.main_paned.get_position() < 10:
                    self.main_paned.set_position(self.last_valid_paned_position)
                    print(f"DEBUG: Restored paned position to {self.last_valid_paned_position}.", file=sys.stderr)

    def do_activate(self):
        """Called when the application is activated."""
        if not self.window:
            self.window = Gtk.ApplicationWindow(application=self)
            self.window.set_title("AVR Timer Beregner (GTK4)")
            self.window.set_default_size(1000, 700)
            self.window.set_resizable(True)

            # Connect to the "notify::width" signal to handle responsive sidebar behavior
            # This signal will fire automatically when the window is first allocated its size.
            self.window.connect("notify::width", self.on_window_width_changed)

            header_bar = Gtk.HeaderBar()
            self.window.set_titlebar(header_bar)

            # --- Main Layout: Gtk.Paned ---
            self.main_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
            self.main_paned.set_hexpand(True)
            self.main_paned.set_vexpand(True)
            self.main_paned.set_shrink_start_child(False)
            self.main_paned.set_resize_start_child(False)
            self.window.set_child(self.main_paned)

            # --- Left Pane: Sidebar Navigation ---
            self.stack = Gtk.Stack()
            self.stack_sidebar = Gtk.StackSidebar(stack=self.stack)
            self.stack_sidebar.set_vexpand(True)
            self.stack_sidebar.set_hexpand(False)

            self.sidebar_scrolled_window = Gtk.ScrolledWindow()
            self.sidebar_scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            self.sidebar_scrolled_window.set_child(self.stack_sidebar)
            self.sidebar_scrolled_window.set_size_request(150, -1)  # Minimum width for sidebar content
            self.sidebar_scrolled_window.set_hexpand(False)
            self.sidebar_scrolled_window.set_vexpand(True)
            self.main_paned.set_start_child(self.sidebar_scrolled_window)

            # Set initial paned position from config and connect position change handler
            self.main_paned.set_position(self.load_paned_position())
            self.main_paned.connect("notify::position", self.save_paned_position)

            # --- Right Pane: Content Area ---
            content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            content_box.set_margin_start(20)
            content_box.set_margin_end(10)
            content_box.set_margin_top(10)
            content_box.set_margin_bottom(10)
            content_box.set_hexpand(True)
            content_box.set_vexpand(True)

            content_scrolled_window = Gtk.ScrolledWindow()
            content_scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            content_scrolled_window.set_child(content_box)
            content_scrolled_window.set_hexpand(True)
            content_scrolled_window.set_vexpand(True)
            self.main_paned.set_end_child(content_scrolled_window)

            # --- CPU Frequency Input (Global Settings) ---
            cpu_freq_frame = Gtk.Frame(label="Global Indstillinger")
            cpu_freq_frame.set_margin_bottom(10)
            cpu_freq_frame.set_hexpand(True)
            cpu_freq_frame.set_vexpand(False)
            content_box.append(cpu_freq_frame)

            cpu_freq_grid = Gtk.Grid()
            cpu_freq_grid.set_row_spacing(5)
            cpu_freq_grid.set_column_spacing(5)
            cpu_freq_grid.set_margin_start(5)
            cpu_freq_grid.set_margin_end(5)
            cpu_freq_grid.set_margin_top(5)
            cpu_freq_grid.set_margin_bottom(5)
            cpu_freq_grid.set_hexpand(True)
            cpu_freq_grid.set_vexpand(False)
            cpu_freq_frame.set_child(cpu_freq_grid)

            cpu_freq_grid.attach(Gtk.Label(label="CPU Frekvens (MHz):", xalign=0), 0, 0, 1, 1)
            self.cpu_freq_entry = Gtk.Entry()
            self.cpu_freq_entry.set_text(str(CPU_FREQ_DEFAULT / 1_000_000))
            self.cpu_freq_entry.set_width_chars(10)
            cpu_freq_grid.attach(self.cpu_freq_entry, 1, 0, 1, 1)

            # --- Content Stack (Tabs) ---
            tab_names_and_titles = [
                ("forward_beregninger", "Forward Beregninger"),
                ("reverse_beregninger", "Reverse Beregninger"),
                ("mega2560_stak", "Mega2560 Stak"),
                ("bit_shift_rotering", "Bit Skift/Rotering"),
                # ("c_asm_konvertering", "C/ASM Konvertering"),
                ("prescaler_top_beregner", "Prescaler TOP Beregner"),
                ("info_tab", "Info-tab"),
                ("initialiseringsvaerktoej", "Initialiseringsværktøj"),
                ("uart", "UART"),
                # ("duty_cycle", "Duty Cycle"),
                ("adc_calc", "ADC Beregner")
            ]

            tab_widgets = [
                ForwardTimerCalculations(cpu_freq_entry=self.cpu_freq_entry),
                ReverseCalculatorTab(cpu_freq_entry=self.cpu_freq_entry),
                Mega2560StackTab(),
                BitShiftRotateTab(),
                PrescalerTOPCalculator(cpu_freq_entry=self.cpu_freq_entry),
                InfoTab(),
                InitializerTab(cpu_freq_entry=self.cpu_freq_entry),
                UartCalculationsTab(cpu_freq_entry=self.cpu_freq_entry),
                # DutyCycleCalculatorTab(cpu_freq_entry=self.cpu_freq_entry),
                AdcCalculator()
            ]

            self.stack.set_hexpand(True)
            self.stack.set_vexpand(True)
            self.stack.set_valign(Gtk.Align.FILL)

            for (name, title), widget in zip(tab_names_and_titles, tab_widgets):
                self.stack.add_titled(widget, name, title)

            content_box.append(self.stack)
            # Set the initial visible tab
            self.stack.set_visible_child_name(tab_names_and_titles[0][0])

        self.window.present()


# Run the application
if __name__ == '__main__':
    app = MainWindow()
    app.run()
