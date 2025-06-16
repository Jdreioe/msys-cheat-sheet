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
    Organized into multiple sub-tabs using a sidebar (Gtk.StackSidebar + Gtk.Stack).
    """
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_homogeneous(True)
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(12)
        self.set_margin_bottom(12)

        # --- Sidebar and Content Area ---
        content_area_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        content_area_box.set_hexpand(True) # Allow the content area to expand horizontally
        content_area_box.set_vexpand(True) # Allow the content area to expand vertically
        self.append(content_area_box)

        self.stack = Gtk.Stack()
        self.stack.set_hexpand(True) # Allow stack to expand horizontally
        self.stack.set_vexpand(True) # Allow stack to expand vertically
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(300) # milliseconds

        self.sidebar = Gtk.StackSidebar(stack=self.stack)
        self.sidebar.set_vexpand(True) # Allow sidebar to expand vertically
        
        self.sidebar.set_size_request(200, -1)
        content_area_box.append(self.sidebar)
        content_area_box.append(self.stack)

        self._add_content_to_stack()

    def _add_content_to_stack(self):
        sub_tab_definitions = [
            ("interrupts", "Aktivering af Interrupts"),
            ("read_settings", "Aflæsning af Timerindstillinger"),
            ("timer_modes", "Konfiguration af Timer Tilstande"),
            ("bit_manipulation", "Sætning af Bits"),
            ("number_systems", "Tal- og Bit Systemer"),
            ("mega2560_stack_overview", "ATMega2560 Stack og Registeroversigt")
        ]

        self.stack.add_titled(InterruptInfoTab(), "interrupts", "Aktivering af Interrupts")
        self.stack.add_titled(ReadSettingsInfoTab(), "read_settings", "Aflæsning af Timerindstillinger")
        self.stack.add_titled(TimerModesInfoTab(), "timer_modes", "Konfiguration af Timer Tilstande")
        self.stack.add_titled(BitManipulationInfoTab(), "bit_manipulation", "Sætning af Bits")
        self.stack.add_titled(NumberSystemsTab(), "number_systems", "Tal- og Bit Systemer")
        self.stack.add_titled(Mega2560StackTab(), "mega2560_stack_overview", "ATMega2560 Stack og Registeroversigt")
        self.stack.set_visible_child_name("interrupts")
