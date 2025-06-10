# main_app.py
import tkinter as tk
from tkinter import ttk
from constants import CPU_FREQ_DEFAULT
from forward_timer_calcs import ForwardTimerCalculations
from uart_calcs import UartCalculator
from adc_calcs import AdcCalculator
from clock_cycle_calcs import ClockCycleTab
from number_systems_tab import NumberSystemsTab
from mega2560_stack_tab import Mega2560StackTab
from c_asm_converter_tab import CAsmConverterTab
from Bit_Shift_Rotate_Tab import BitShiftRotateTab
from reverse_calc_tab import ReverseCalculatorTab
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("AVR Calculator Suite")
        self.root.geometry("800x1050") # Adjust size as needed

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True, fill="both")

        self.forward_calc_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.forward_calc_tab, text="Timer Indstillinger")
        self.forward_timer_calculations = ForwardTimerCalculations(self.forward_calc_tab)
        # Initialize other calculator tabs
        self.uart_calculator = UartCalculator(self.notebook, CPU_FREQ_DEFAULT)
        self.adc_calculator = AdcCalculator(self.notebook)
        self.clock_cycle_calculator = ClockCycleTab(self.notebook) # Initialize the new tab
        self.number_systems_tab = NumberSystemsTab(self.notebook, tab_title="Number Systems")
        self.mega2560_stack_tab = Mega2560StackTab(self.notebook, tab_title="Mega2560 Stack")
        self.c_asm_converter_tab = CAsmConverterTab(self.notebook, tab_title="C <-> ASM Converter")
        self.bit_shift_rotate_tab = BitShiftRotateTab(self.notebook, tab_title="Bit Shift/Rotate")
        self.reverse_calc_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reverse_calc_tab, text="Reverse Calc")
        self.reverse_timer_calculator = ReverseCalculatorTab(self.reverse_calc_tab)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()