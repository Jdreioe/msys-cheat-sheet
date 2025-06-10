import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio
from Bit_Shift_Rotate_Tab import BitShiftRotateTab
import sys
from c_asm_converter_tab import CAsmConverterTab
from clock_cycle_calcs import ClockCycleTab
class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("GTK 4 Tabs Demo")
        self.set_default_size(800, 600)

        # Main layout box
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_child(vbox)

        # Stack (holds tab pages)
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_vexpand(True)

        # StackSwitcher (tab selector)
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(self.stack)
        vbox.append(stack_switcher)
        vbox.append(self.stack)

        # Add pages (tabs)
        bit_shift_tab = BitShiftRotateTab()
        self.stack.add_titled(bit_shift_tab, "bitshift", "Bit Shift & Rotate")
        c_asm_tab = CAsmConverterTab()
        self.stack.add_titled(c_asm_tab, "c_asm", "C to ASM Converter")
        clock_cycle_tab = ClockCycleTab()
        self.stack.add_titled(clock_cycle_tab, "clock_cycle", "Clock Cycle Calculations")

        
class TabApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.Gtk4TabsDemo")

    def do_activate(self):
        win = MainWindow(self)
        win.present()

# Run the application
if __name__ == '__main__':
    app = TabApp()
    app.run()