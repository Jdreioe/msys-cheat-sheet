import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango

# Import your GTK4 converted timer calculator classes
from timer0_calc import Timer0Calculator
from timer1_calc import Timer1Calculator
from timer2_calc import Timer2Calculator

# Assuming these are GTK4-compatible or simple Python constants/functions
from constants import CPU_FREQ_DEFAULT, PRESCALERS_T0_T1_T2
from utils import parse_hex_bin_int, show_error, show_warning


class ForwardTimerCalculations(Gtk.Box):
    """
    GTK4 container for various forward timer calculation tabs (Timer0, Timer1, Timer2).
    """
    def __init__(self, cpu_freq_entry):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)

        self.cpu_freq_entry = cpu_freq_entry  # Store the Gtk.Entry widget passed from MainWindow

        self._create_widgets()

    def _create_widgets(self):
        # Notebook for individual timers
        self.notebook = Gtk.Notebook()
        self.append(self.notebook)
        self.notebook.set_hexpand(True)
        self.notebook.set_vexpand(True)

        # Timer0 Tab
        self.timer0_calculator = Timer0Calculator(self, self.cpu_freq_entry)
        self.notebook.append_page(self.timer0_calculator, Gtk.Label(label="Timer0"))

        # Timer1 Tab
        self.timer1_calculator = Timer1Calculator(self, self.cpu_freq_entry)
        self.notebook.append_page(self.timer1_calculator, Gtk.Label(label="Timer1"))

        # Timer2 Tab
        self.timer2_calculator = Timer2Calculator(self, self.cpu_freq_entry)
        self.notebook.append_page(self.timer2_calculator, Gtk.Label(label="Timer2"))