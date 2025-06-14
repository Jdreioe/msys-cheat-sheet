import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, Pango
import sys # Import sys for stderr printing

# Import all your tabs
from Bit_Shift_Rotate_Tab import BitShiftRotateTab
from c_asm_converter_tab import CAsmConverterTab
from clock_cycle_calcs import ClockCycleTab
from prescaler_top_calc import PrescalerTOPCalculator
from forward_timer_calcs import ForwardTimerCalculations
from reverse_calc_tab import ReverseCalculatorTab
from mega2560_stack_tab import Mega2560StackTab
from constants import CPU_FREQ_DEFAULT
from info_tab_main import InfoTab
from uart_calcs import UartCalculator as UartCalculationsTab
class MainWindow(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.AVRTimerCalculator",
                         flags=Gio.ApplicationFlags.HANDLES_OPEN)
        self.window = None
        # Initialize _cpu_freq_entry_internal to None or some placeholder
        self._cpu_freq_entry_internal = None 

    # Use a property to monitor assignments to cpu_freq_entry
    @property
    def cpu_freq_entry(self):
        return self._cpu_freq_entry_internal

    @cpu_freq_entry.setter
    def cpu_freq_entry(self, value):
        old_value = self._cpu_freq_entry_internal
        self._cpu_freq_entry_internal = value
        
        # Log when the type changes or when it's assigned
        if old_value is None:
            print(f"DEBUG: Initial assignment of self.cpu_freq_entry. Type: {type(value)}", file=sys.stderr)
        elif type(old_value) != type(value):
            print(f"DEBUG: !!! TYPE CHANGE !!! self.cpu_freq_entry changed from {type(old_value)} to {type(value)}", file=sys.stderr)
            print(f"DEBUG: New value: {value}", file=sys.stderr)
            # You can even raise an error here if you want to stop immediately
            # if not isinstance(value, Gtk.Entry):
            #     raise TypeError(f"Illegal reassignment of cpu_freq_entry to {type(value)}")
        else:
            print(f"DEBUG: self.cpu_freq_entry reassigned. Type: {type(value)}", file=sys.stderr)


    def do_startup(self):
        Gtk.Application.do_startup(self)

        css_provider = Gtk.CssProvider()
        css_data = """
        textview {
            background-color: lightblue;
            font-family: monospace;
            font-size: 14pt;
            color: darkgreen;
        }
        """
        css_provider.load_from_string(css_data)
        
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def do_activate(self):
        if not self.window:
            self.window = Gtk.ApplicationWindow(application=self)
            self.window.set_title("AVR Timer Beregner (GTK4)")
            self.window.set_default_size(400, 350) # Was 800, 700
            self.window.set_size_request(350, 300) # Was 700, 600

            header_bar = Gtk.HeaderBar()
            self.window.set_titlebar(header_bar)

            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            main_box.set_margin_start(10)
            main_box.set_margin_end(10)
            main_box.set_margin_top(10)
            main_box.set_margin_bottom(10)
            self.window.set_child(main_box)

            # --- CPU Frequency Input (shared) ---
            cpu_freq_frame = Gtk.Frame(label="Global Indstillinger")
            main_box.append(cpu_freq_frame)
            cpu_freq_frame.set_margin_bottom(10)
            
            cpu_freq_grid = Gtk.Grid()
            cpu_freq_grid.set_row_spacing(5)
            cpu_freq_grid.set_column_spacing(5)
            cpu_freq_grid.set_margin_start(5)
            cpu_freq_grid.set_margin_end(5)
            cpu_freq_grid.set_margin_top(5)
            cpu_freq_grid.set_margin_bottom(5)
            cpu_freq_frame.set_child(cpu_freq_grid)

            cpu_freq_grid.attach(Gtk.Label(label="CPU Frekvens (MHz):", xalign=0), 0, 0, 1, 1)
            # This line will now trigger the setter and print debug info
            self.cpu_freq_entry = Gtk.Entry() 
            self.cpu_freq_entry.set_text(str(CPU_FREQ_DEFAULT / 1_000_000))
            cpu_freq_grid.attach(self.cpu_freq_entry, 1, 0, 1, 1)
            self.cpu_freq_entry.set_hexpand(True)

            # --- Main Notebook for Tabs ---
            self.main_notebook = Gtk.Notebook()
            main_box.append(self.main_notebook)
            self.main_notebook.set_hexpand(True)
            self.main_notebook.set_vexpand(True)

            # Add Forward Timer Calculations Tab
            self.forward_calcs_tab = ForwardTimerCalculations(cpu_freq_entry=self.cpu_freq_entry)
            self.main_notebook.append_page(self.forward_calcs_tab, Gtk.Label(label="Forward Beregninger"))

            # Add Reverse Calculator Tab
            # Ensure ReverseCalculatorTab is adapted to expect a Gtk.Entry, not a float
            self.reverse_calcs_tab = ReverseCalculatorTab(cpu_freq_entry=self.cpu_freq_entry) # If cpu_freq expects Gtk.Entry
            # If ReverseCalculatorTab expects a float, you'd do:
            # self.reverse_calcs_tab = ReverseCalculatorTab(cpu_freq=float(self.cpu_freq_entry.get_text()))
            # But the error implies it's expecting a Gtk.Entry.

            self.main_notebook.append_page(self.reverse_calcs_tab, Gtk.Label(label="Reverse Beregninger"))

            # Add Mega2560 Stack Tab
            self.mega2560_stack_tab = Mega2560StackTab()
            self.main_notebook.append_page(self.mega2560_stack_tab, Gtk.Label(label="Mega2560 Stak"))

            # Add Bit Shift & Rotate Tab
            self.bit_shift_rotate_tab = BitShiftRotateTab()
            self.main_notebook.append_page(self.bit_shift_rotate_tab, Gtk.Label(label="Bit Skift/Rotering"))

            # Add C/ASM Converter Tab
            self.c_asm_converter_tab = CAsmConverterTab() # Assuming it doesn't need cpu_freq_entry
            self.main_notebook.append_page(self.c_asm_converter_tab, Gtk.Label(label="C/ASM Konvertering"))

            # Add Clock Cycle Calculations Tab
            self.clock_cycle_tab = ClockCycleTab() # Assuming it doesn't need cpu_freq_entry
            self.main_notebook.append_page(self.clock_cycle_tab, Gtk.Label(label="Clock Cycle Beregninger"))

            # Add Prescaler TOP Calculator Tab
            self.prescaler_top_calc_tab = PrescalerTOPCalculator(cpu_freq_entry=self.cpu_freq_entry) # Ensure it expects Gtk.Entry
            self.main_notebook.append_page(self.prescaler_top_calc_tab, Gtk.Label(label="Prescaler TOP Beregner"))

            # Add Info Tab
            self.info_tab = InfoTab()
            self.main_notebook.append_page(self.info_tab, Gtk.Label(label="Info-tab"))



            self.uart_calculations_tab = UartCalculationsTab(cpu_freq_entry=self.cpu_freq_entry)
            self.main_notebook.append_page(self.uart_calculations_tab, Gtk.Label(label="UART"))
            # Set the default tab to Forward Calculations
            self.main_notebook.set_show_tabs(True)
            self.main_notebook.set_show_border(True)
            self.main_notebook.set_current_page(0)
        self.window.present()

# Run the application
if __name__ == '__main__':
    app = MainWindow()
    app.run()

