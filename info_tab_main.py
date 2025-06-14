import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango

# Import the individual content tabs
from interrupt_tab import InterruptInfoTab
from timer_info import ReadSettingsInfoTab
from timer_mode_tab import TimerModesInfoTab
from bit_info import BitManipulationInfoTab
from number_systems_tab import NumberSystemsTab
from mega2560_stack_tab import Mega2560StackTab


class InfoTab(Gtk.Box):
    """
    GTK4 tab providing comprehensive information on ATMega2560 timer interrupts,
    reading settings, configuring different timer modes, and bit manipulation.
    Organized into multiple sub-tabs using Gtk.Notebook.
    """
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_homogeneous(False)
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(12)
        self.set_margin_bottom(12)

        # Main title
        main_title_label = Gtk.Label(label="Info-tab")
        main_title_label.add_css_class("title-1") # Apply a CSS class for styling the title
        self.append(main_title_label)

        # Create a Notebook to hold the sub-tabs
        self.notebook = Gtk.Notebook()
        self.append(self.notebook)

        # Add individual content tabs to the notebook
        self._add_content_tabs()

    def _add_content_tabs(self):
        # Tab 1: Aktivering af Interrupts
        interrupt_tab = InterruptInfoTab()
        self.notebook.append_page(interrupt_tab, Gtk.Label(label="Aktivering af Interrupts"))

        # Tab 2: Aflæsning af Timerindstillinger
        read_settings_tab = ReadSettingsInfoTab()
        self.notebook.append_page(read_settings_tab, Gtk.Label(label="Aflæsning af Timerindstillinger"))

        # Tab 3: Konfiguration af Timer Tilstande (WGM)
        timer_modes_tab = TimerModesInfoTab()
        self.notebook.append_page(timer_modes_tab, Gtk.Label(label="Konfiguration af Timer Tilstande"))

        # Tab 4: Hvordan man Sætter Bits i Timere
        bit_manipulation_tab = BitManipulationInfoTab()
        self.notebook.append_page(bit_manipulation_tab, Gtk.Label(label="Sætning af Bits"))

        # Tab 5: Tal- og Bit Systemer
        number_systems_tab = NumberSystemsTab()
        self.notebook.append_page(number_systems_tab, Gtk.Label(label="Tal- og Bit Systemer"))
        # Tab 6: ATMega2560 Stack og Registeroversigt
        mega2560_stack_tab = Mega2560StackTab()
        self.notebook.append_page(mega2560_stack_tab, Gtk.Label(label="ATMega2560 Stack og Registeroversigt"))
        # Set the first tab as the default visible tab
        self.notebook.set_show_tabs(True)
        self.notebook.set_show_border(True)

