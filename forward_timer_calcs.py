import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango

from timer0_calc import Timer0Calculator
from timer1_calc import Timer1Calculator
from timer2_calc import Timer2Calculator
from constants import CPU_FREQ_DEFAULT, PRESCALERS_T0_T1_T2
from utils import parse_hex_bin_int, show_error, show_warning

class ForwardTimerCalculations(Gtk.Box):
    """
    GTK4 container for various forward timer calculation sub-sections (Timer0, Timer1, Timer2).
    This class uses an internal Gtk.Stack and Gtk.StackSwitcher to provide tab-like navigation.
    """
    def __init__(self, cpu_freq_entry):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_valign(Gtk.Align.FILL)

        self.cpu_freq_entry = cpu_freq_entry
        self._create_widgets()

    def _create_widgets(self):
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content_box.set_hexpand(True)
        content_box.set_vexpand(True)
        self.append(content_box)

        self.timer_stack_switcher = Gtk.StackSwitcher()
        self.timer_stack_switcher.set_hexpand(True)
        self.timer_stack_switcher.set_halign(Gtk.Align.FILL)

        self.timer_stack = Gtk.Stack()
        self.timer_stack.set_hexpand(True)
        self.timer_stack.set_vexpand(True)
        self.timer_stack.set_valign(Gtk.Align.FILL)

        self.timer_stack_switcher.set_stack(self.timer_stack)
        content_box.append(self.timer_stack_switcher)
        content_box.append(self.timer_stack)

        # Timer0 Tab
        self.timer0_calculator = Timer0Calculator(self, self.cpu_freq_entry)
        timer0_scrolled = Gtk.ScrolledWindow()
        timer0_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)  # Resize before scrolling
        timer0_scrolled.set_child(self.timer0_calculator)
        timer0_scrolled.set_hexpand(True)
        timer0_scrolled.set_vexpand(True)
        self.timer_stack.add_titled(timer0_scrolled, "timer0", "Timer0")

        # Timer1 Tab
        self.timer1_calculator = Timer1Calculator(self, self.cpu_freq_entry)
        timer1_scrolled = Gtk.ScrolledWindow()
        timer1_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        timer1_scrolled.set_child(self.timer1_calculator)
        timer1_scrolled.set_hexpand(True)
        timer1_scrolled.set_vexpand(True)
        self.timer_stack.add_titled(timer1_scrolled, "timer1", "Timer1")

        # Timer2 Tab
        self.timer2_calculator = Timer2Calculator(self, self.cpu_freq_entry)
        timer2_scrolled = Gtk.ScrolledWindow()
        timer2_scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        timer2_scrolled.set_child(self.timer2_calculator)
        timer2_scrolled.set_hexpand(True)
        timer2_scrolled.set_vexpand(True)
        self.timer_stack.add_titled(timer2_scrolled, "timer2", "Timer2")

        self.timer_stack.set_visible_child_name("timer0")