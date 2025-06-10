# clock_cycle_calcs.py
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import scrolledtext
import re # For parsing assembly lines

class ClockCycleCalculator:
    def __init__(self, notebook):
        self.notebook = notebook
        self.current_sequence_cycles = 0  # Initialize current_sequence_cycles here
        self._setup_clock_cycle_tab()

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import re

class ClockCycleTab:
    def __init__(self, notebook):
        # Create a frame for the tab
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Clock Cycle Calculator")

        self.instruction_cycles = {
            "ADD": 1, "ADC": 1, "SUB": 1, "SBC": 1, "AND": 1, "OR": 1, "EOR": 1,
            "MOV": 1, "LDI": 1, "INC": 1, "DEC": 1, "CLR": 1, "SET": 1,
            "CBR": 1, "SBR": 1, "COM": 1, "NEG": 1, "SWAP": 1, "ROR": 1,
            "LPM": 3, "LD": 2, "ST": 2, "PUSH": 2, "POP": 2,
            "MUL": 2, "MULS": 2, "MULSU": 2, "RJMP": 2, "RCALL": 3,
            "JMP": 3, "CALL": 4, "RET": 4, "RETI": 4,
            "BR": {"taken": 2, "not_taken": 1}, "BREQ": {"taken": 2, "not_taken": 1},
            "BRNE": {"taken": 2, "not_taken": 1}, "BRGE": {"taken": 2, "not_taken": 1},
            "BRLT": {"taken": 2, "not_taken": 1}, "BRBC": {"taken": 2, "not_taken": 1},
            "BRBS": {"taken": 2, "not_taken": 1}, "BRCC": {"taken": 2, "not_taken": 1},
            "BRCS": {"taken": 2, "not_taken": 1}, "BRHC": {"taken": 2, "not_taken": 1},
            "BRHS": {"taken": 2, "not_taken": 1}, "BRID": {"taken": 2, "not_taken": 1},
            "BRIE": {"taken": 2, "not_taken": 1}, "BRMI": {"taken": 2, "not_taken": 1},
            "BRPL": {"taken": 2, "not_taken": 1}, "BRVC": {"taken": 2, "not_taken": 1},
            "BRVS": {"taken": 2, "not_taken": 1}, "BRTC": {"taken": 2, "not_taken": 1},
            "BRTS": {"taken": 2, "not_taken": 1}, "BRSH": {"taken": 2, "not_taken": 1},
            "BRLO": {"taken": 2, "not_taken": 1}, "NOP": 1
        }

        self.current_sequence_cycles = 0
        self.sequence_info = []
        self.registers = {}  # Track register values, e.g., {'R16': 0, 'R17': 0}

        # GUI Elements
        self.multi_instr_label = tk.Label(self.tab, text="Indsæt Assembly Kode Her (inkl. labels og kommentarer):")
        self.multi_instr_label.pack(pady=5)
        self.multi_instr_text = scrolledtext.ScrolledText(self.tab, width=70, height=12, wrap=tk.WORD)
        self.multi_instr_text.pack(pady=5)
        self.multi_instr_text.insert(tk.END, """    CLR R16
    CLR R17
IGEN: NOP
    DEC R16
    BRNE IGEN
    INC R17
    BRNE IGEN""")

        self.add_multi_button = tk.Button(self.tab, text="Analyser & Tilføj Indsat Kode til Sekvens", command=self.add_multiple_instructions)
        self.add_multi_button.pack(pady=10)

        self.separator = tk.Frame(self.tab, height=2, bd=1, relief=tk.SUNKEN)
        self.separator.pack(fill=tk.X, padx=5, pady=5)

        self.instr_label = tk.Label(self.tab, text="Tilføj Enkelt Instruktion:")
        self.instr_label.pack(pady=5)
        self.instr_entry = tk.Entry(self.tab, width=30)
        self.instr_entry.pack(pady=5)
        self.instr_entry.bind("<Return>", lambda event: self.add_instruction())

        self.reps_label = tk.Label(self.tab, text="Antal gentagelser (for loops, standard 1):")
        self.reps_label.pack(pady=5)
        self.reps_entry = tk.Entry(self.tab, width=10)
        self.reps_entry.insert(0, "1")
        self.reps_entry.pack(pady=5)
        self.reps_entry.bind("<Return>", lambda event: self.add_instruction())

        self.branch_var = tk.StringVar(self.tab)
        self.branch_var.set("Normal")
        self.branch_options = ["Normal", "Branch Taken", "Branch Not Taken"]
        self.branch_menu_label = tk.Label(self.tab, text="Branch adfærd (kun for BR-instruktioner):")
        self.branch_menu_label.pack(pady=5)
        self.branch_menu = tk.OptionMenu(self.tab, self.branch_var, *self.branch_options)
        self.branch_menu.pack(pady=5)

        self.add_button = tk.Button(self.tab, text="Tilføj Enkelt Instruktion til Sekvens", command=self.add_instruction)
        self.add_button.pack(pady=10)

        self.separator2 = tk.Frame(self.tab, height=2, bd=1, relief=tk.SUNKEN)
        self.separator2.pack(fill=tk.X, padx=5, pady=5)

        self.sequence_display_label = tk.Label(self.tab, text="Instruktionssekvens:")
        self.sequence_display_label.pack(pady=5)
        self.sequence_text_widget = scrolledtext.ScrolledText(self.tab, width=70, height=10, state='disabled')
        self.sequence_text_widget.pack(pady=5)

        self.total_cycles_label = tk.Label(self.tab, text=f"Total Clock Cycles: {self.current_sequence_cycles}")
        self.total_cycles_label.config(font=("Arial", 14, "bold"))
        self.total_cycles_label.pack(pady=10)

        self.reset_button = tk.Button(self.tab, text="Nulstil Sekvens", command=self.reset_sequence)
        self.reset_button.pack(pady=5)

        self.help_button = tk.Button(self.tab, text="Instruktioner & Cycles (Hint)", command=self.show_help)
        self.help_button.pack(pady=5)

    def _parse_line(self, line):
        """Parses a single line of assembly code to extract instruction and label."""
        line = line.strip()
        if not line:
            return None, None, None
        if ';' in line:
            line = line.split(';', 1)[0].strip()
            if not line: return None, None, None
        label_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*):', line)
        if label_match:
            label = label_match.group(1).upper()
            line = line[len(label_match.group(0)):].strip()
        else:
            label = None
        if not line:
            return label, None, None
        parts = re.split(r'\s+', line, 1)
        instruction = parts[0].upper()
        operand = parts[1] if len(parts) > 1 else None
        return label, instruction, operand

    def _simulate_register(self, instr, operand, reg_values):
        """Simulate register updates for CLR, DEC, INC to estimate loop iterations."""
        if instr == "CLR" and operand:
            reg = operand.strip().upper()
            reg_values[reg] = 0
        elif instr == "DEC" and operand:
            reg = operand.strip().upper()
            if reg not in reg_values:
                reg_values[reg] = 0  # Assume 0 if not initialized
            reg_values[reg] = (reg_values[reg] - 1) & 0xFF  # 8-bit wraparound
        elif instr == "INC" and operand:
            reg = operand.strip().upper()
            if reg not in reg_values:
                reg_values[reg] = 0
            reg_values[reg] = (reg_values[reg] + 1) & 0xFF  # 8-bit wraparound

    def _estimate_loop_iterations(self, instr, operand, labels, line_num, processed_lines, current_reg_values):
        """Estimate loop iterations based on register values and branch instruction."""
        if not operand or not instr.startswith("BR"):
            return 1, "Normal", "Normal"
        target_label = operand.split()[0].upper()
        if target_label not in labels or labels[target_label] >= line_num:
            return 1, "Branch Not Taken", "Branch Not Taken"  # Forward jump or no loop

        # Backward jump: potential loop
        if instr == "BRNE" and operand:
            loop_start = labels[target_label]
            reg = None
            for i in range(loop_start, line_num):
                loop_line = processed_lines[i]
                if loop_line['instr'] in ("DEC", "INC") and loop_line['operand']:
                    reg = loop_line['operand'].strip().upper()
                    break
            if reg and reg in current_reg_values:
                start_value = current_reg_values.get(reg, 0)
                if loop_line['instr'] == "DEC":
                    iterations = start_value if start_value > 0 else 256
                else:  # INC
                    iterations = (256 - start_value) % 256 if start_value != 0 else 256
                return iterations, "Branch Taken", "Branch Not Taken"
        return 256, "Branch Taken", "Branch Not Taken"

    def add_instruction(self):
        instr_raw = self.instr_entry.get().strip()
        reps_str = self.reps_entry.get().strip()
        branch_behavior = self.branch_var.get()

        if not instr_raw:
            messagebox.showwarning("Input Fejl", "Indtast venligst en instruktion.")
            return
        try:
            reps = int(reps_str)
            if reps <= 0:
                messagebox.showwarning("Input Fejl", "Antal gentagelser skal være et positivt heltal.")
                return
        except ValueError:
            messagebox.showwarning("Input Fejl", "Antal gentagelser skal være et gyldigt heltal.")
            return

        _label, instr_mnemonic, _operand = self._parse_line(instr_raw)
        if not instr_mnemonic:
            messagebox.showwarning("Input Fejl", f"Kunne ikke genkende instruktion fra '{instr_raw}'.")
            return
        self._process_single_instruction_and_add_to_sequence(instr_mnemonic, reps, branch_behavior)
        self.instr_entry.delete(0, tk.END)
        self.reps_entry.delete(0, tk.END)
        self.reps_entry.insert(0, "1")
        self.branch_var.set("Normal")

    def add_multiple_instructions(self):
        pasted_code = self.multi_instr_text.get(1.0, tk.END).strip()
        if not pasted_code:
            messagebox.showwarning("Input Fejl", "Indsæt venligst assembly kode i tekstboksen.")
            return

        lines = pasted_code.split('\n')
        self.registers = {}  # Reset registers for new simulation
        processed_lines = []
        labels = {}

        # First pass: parse lines, identify labels
        for i, line_text in enumerate(lines):
            label, instr_mnemonic, operand = self._parse_line(line_text)
            if label:
                labels[label] = i
            if instr_mnemonic:
                processed_lines.append({
                    'line_num': i,
                    'original_text': line_text,
                    'instr': instr_mnemonic,
                    'operand': operand,
                    'reps': 1,
                    'branch_behavior': 'Normal',
                    'cycles': 0,
                    'is_loop_branch': False,
                    'loop_target_label': None,
                    'is_label': False
                })
            elif label:
                processed_lines.append({
                    'line_num': i,
                    'original_text': line_text,
                    'instr': None,
                    'operand': None,
                    'reps': 1,
                    'branch_behavior': 'Normal',
                    'cycles': 0,
                    'is_loop_branch': False,
                    'loop_target_label': None,
                    'is_label': True
                })

        self.temp_processed_lines = processed_lines
        self.temp_labels = labels
        self.current_processing_index = 0
        self._process_next_pasted_line()

    def _process_next_pasted_line(self):
        reg_values = self.registers.copy()  # Track register state for simulation
        outer_loop_detected = False
        outer_iterations = 1
        outer_loop_line = None

        # First pass to detect outer loop and estimate its iterations
        for i in range(len(self.temp_processed_lines)):
            line_data = self.temp_processed_lines[i]
            instr = line_data['instr']
            operand = line_data['operand']
            line_num = line_data['line_num']
            if instr and instr.startswith("BR"):
                iterations, loop_behavior, final_behavior = self._estimate_loop_iterations(
                    instr, operand, self.temp_labels, line_num, self.temp_processed_lines, reg_values
                )
                self._simulate_register(instr, operand, reg_values)
                if iterations > 1 and line_num > self.temp_labels.get(operand.split()[0].upper(), -1):
                    if not outer_loop_detected or line_num > outer_loop_line:
                        outer_loop_detected = True
                        outer_iterations = iterations
                        outer_loop_line = line_num
            if instr:
                self._simulate_register(instr, operand, reg_values)

        self.current_processing_index = 0
        while self.current_processing_index < len(self.temp_processed_lines):
            line_data = self.temp_processed_lines[self.current_processing_index]
            if line_data['is_label'] and not line_data['instr']:
                self._add_to_sequence_display(line_data['original_text'], 1, 0, is_label=True)
                self.current_processing_index += 1
                continue

            instr = line_data['instr']
            operand = line_data['operand']
            line_num = line_data['line_num']

            if instr and instr.startswith("BR"):
                iterations, loop_behavior, final_behavior = self._estimate_loop_iterations(
                    instr, operand, self.temp_labels, line_num, self.temp_processed_lines, self.registers
                )
                if iterations > 1 and line_num == outer_loop_line and outer_loop_detected:
                    self._handle_outer_loop(line_num, outer_iterations, loop_behavior, final_behavior)
                    self.current_processing_index = len(self.temp_processed_lines)  # Skip to end after outer loop
                    break
                elif iterations > 1:
                    self._handle_loop_automatically(line_num, iterations, loop_behavior, final_behavior)
                else:
                    self._process_single_instruction_and_add_to_sequence(instr, 1, loop_behavior, display_prefix=f"(L{line_num}) ")
            elif instr:
                self._process_single_instruction_and_add_to_sequence(instr, 1, "Normal", display_prefix=f"(L{line_num}) ")
            self._simulate_register(instr, operand, self.registers)
            self.current_processing_index += 1

        self._finalise_pasted_code_processing()

    def _handle_loop_automatically(self, line_num, iterations, loop_behavior, final_behavior):
        """Process an inner loop."""
        loop_branch_data = next((item for item in self.temp_processed_lines if item['line_num'] == line_num and item['instr']), None)
        if not loop_branch_data:
            self._process_single_instruction_and_add_to_sequence(loop_branch_data['instr'], 1, "Normal", display_prefix=f"(L{line_num}) ")
            return

        loop_target_label = loop_branch_data['operand'].split()[0].upper()
        loop_start_index = self.temp_labels[loop_target_label]
        loop_instructions_data = []
        for i in range(loop_start_index, line_num + 1):
            if self.temp_processed_lines[i]['instr']:
                loop_instructions_data.append(self.temp_processed_lines[i])

        if not loop_instructions_data:
            messagebox.showwarning("Loop Fejl", f"Ingen instruktioner fundet i loopet fra {loop_target_label} til linje {line_num}. Behandler branch som enkelt.")
            self._process_single_instruction_and_add_to_sequence(loop_branch_data['instr'], 1, "Normal", display_prefix=f"(L{line_num}) ")
            return

        cycles_per_loop_iteration = 0
        for instr_data in loop_instructions_data:
            instr_mnemonic = instr_data['instr']
            instr_info = self.instruction_cycles.get(instr_mnemonic)
            if instr_info is None:
                messagebox.showwarning("Ukendt Instruktion", f"Ukendt instruktion '{instr_mnemonic}' i loop. Fortsætter.")
                continue
            if instr_data == loop_branch_data:
                key = "taken" if loop_behavior == "Branch Taken" else "not_taken"
                cycles_per_instr = instr_info[key]
            elif isinstance(instr_info, dict):
                cycles_per_instr = instr_info["not_taken"]
            else:
                cycles_per_instr = instr_info
            cycles_per_loop_iteration += cycles_per_instr

        total_loop_cycles = (cycles_per_loop_iteration * (iterations - 1))
        last_iteration_cycles = 0
        for instr_data in loop_instructions_data:
            instr_mnemonic = instr_data['instr']
            instr_info = self.instruction_cycles.get(instr_mnemonic)
            if instr_info is None:
                continue
            if instr_data == loop_branch_data:
                key = "taken" if final_behavior == "Branch Taken" else "not_taken"
                last_iteration_cycles += instr_info[key]
            elif isinstance(instr_info, dict):
                last_iteration_cycles += instr_info["not_taken"]
            else:
                last_iteration_cycles += instr_info
        total_loop_cycles += last_iteration_cycles

        self.current_sequence_cycles += total_loop_cycles
        loop_display_text = f"Loop ({loop_target_label} til L{line_num}) x{iterations} ({total_loop_cycles} cycles)"
        self.sequence_info.append({
            'instr': 'LOOP_BLOCK',
            'reps': iterations,
            'cycles': total_loop_cycles,
            'display_text': loop_display_text
        })
        self._update_sequence_display()

    def _handle_outer_loop(self, line_num, outer_iterations, loop_behavior, final_behavior):
        """Process the outer loop, including nested inner loops."""
        loop_branch_data = next((item for item in self.temp_processed_lines if item['line_num'] == line_num and item['instr']), None)
        if not loop_branch_data:
            self._process_single_instruction_and_add_to_sequence(loop_branch_data['instr'], 1, "Normal", display_prefix=f"(L{line_num}) ")
            return

        loop_target_label = loop_branch_data['operand'].split()[0].upper()
        loop_start_index = self.temp_labels[loop_target_label]
        loop_instructions_data = []
        for i in range(loop_start_index, line_num + 1):
            if self.temp_processed_lines[i]['instr']:
                loop_instructions_data.append(self.temp_processed_lines[i])

        if not loop_instructions_data:
            messagebox.showwarning("Loop Fejl", f"Ingen instruktioner fundet i loopet fra {loop_target_label} til linje {line_num}. Behandler branch som enkelt.")
            self._process_single_instruction_and_add_to_sequence(loop_branch_data['instr'], 1, "Normal", display_prefix=f"(L{line_num}) ")
            return

        # Calculate cycles for the inner loop (e.g., DEC R16, BRNE IGEN)
        inner_loop_cycles = 0
        inner_iterations = 1
        reg_values = self.registers.copy()
        for i in range(loop_start_index, line_num):
            instr_data = self.temp_processed_lines[i]
            instr = instr_data['instr']
            operand = instr_data['operand']
            if instr and instr.startswith("BR"):
                inner_iterations, inner_loop_behavior, inner_final_behavior = self._estimate_loop_iterations(
                    instr, operand, self.temp_labels, instr_data['line_num'], self.temp_processed_lines, reg_values
                )
                if inner_iterations > 1:
                    inner_loop_end = instr_data['line_num']
                    inner_loop_instructions = []
                    for j in range(loop_start_index, inner_loop_end + 1):
                        if self.temp_processed_lines[j]['instr']:
                            inner_loop_instructions.append(self.temp_processed_lines[j])
                    for inner_instr_data in inner_loop_instructions:
                        instr_mnemonic = inner_instr_data['instr']
                        instr_info = self.instruction_cycles.get(instr_mnemonic)
                        if instr_info is None:
                            continue
                        if inner_instr_data['line_num'] == inner_loop_end:
                            key = "taken" if inner_loop_behavior == "Branch Taken" else "not_taken"
                            inner_loop_cycles += instr_info[key] * (inner_iterations - 1)
                            key = "taken" if inner_final_behavior == "Branch Taken" else "not_taken"
                            inner_loop_cycles += instr_info[key]
                        elif isinstance(instr_info, dict):
                            inner_loop_cycles += instr_info["not_taken"] * inner_iterations
                        else:
                            inner_loop_cycles += instr_info * inner_iterations
            self._simulate_register(instr, operand, reg_values)

        # Calculate cycles for the outer loop iteration (including inner loop)
        cycles_per_outer_iteration = inner_loop_cycles
        for instr_data in loop_instructions_data:
            instr_mnemonic = instr_data['instr']
            instr_info = self.instruction_cycles.get(instr_mnemonic)
            if instr_info is None:
                messagebox.showwarning("Ukendt Instruktion", f"Ukendt instruktion '{instr_mnemonic}' i loop. Fortsætter.")
                continue
            if instr_data == loop_branch_data:
                key = "taken" if loop_behavior == "Branch Taken" else "not_taken"
                cycles_per_outer_iteration += instr_info[key]
            elif isinstance(instr_info, dict):
                cycles_per_outer_iteration += instr_info["not_taken"]
            else:
                cycles_per_outer_iteration += instr_info

        total_outer_cycles = (cycles_per_outer_iteration * (outer_iterations - 1))
        last_iteration_cycles = inner_loop_cycles
        for instr_data in loop_instructions_data:
            instr_mnemonic = instr_data['instr']
            instr_info = self.instruction_cycles.get(instr_mnemonic)
            if instr_info is None:
                continue
            if instr_data == loop_branch_data:
                key = "taken" if final_behavior == "Branch Taken" else "not_taken"
                last_iteration_cycles += instr_info[key]
            elif isinstance(instr_info, dict):
                last_iteration_cycles += instr_info["not_taken"]
            else:
                last_iteration_cycles += instr_info
        total_outer_cycles += last_iteration_cycles

        self.current_sequence_cycles += total_outer_cycles
        loop_display_text = f"Loop ({loop_target_label} til L{line_num}) x{outer_iterations} ({total_outer_cycles} cycles)"
        self.sequence_info.append({
            'instr': 'LOOP_BLOCK',
            'reps': outer_iterations,
            'cycles': total_outer_cycles,
            'display_text': loop_display_text
        })
        self._update_sequence_display()

    def _finalise_pasted_code_processing(self):
        messagebox.showinfo("Klar", f"Indsat kode er blevet behandlet. Total Clock Cycles opdateret.")
        self.multi_instr_text.delete(1.0, tk.END)

    def _process_single_instruction_and_add_to_sequence(self, instr_mnemonic, reps, branch_behavior, display_prefix=""):
        """Helper method to process a single instruction's cycles and add to sequence."""
        cycles_per_instr = 0
        instr_name_for_display = instr_mnemonic

        if instr_mnemonic in self.instruction_cycles:
            instr_info = self.instruction_cycles[instr_mnemonic]
            if isinstance(instr_info, dict):
                if branch_behavior == "Branch Taken":
                    cycles_per_instr = instr_info["taken"]
                    instr_name_for_display += " (Branch taget)"
                elif branch_behavior == "Branch Not Taken":
                    cycles_per_instr = instr_info["not_taken"]
                    instr_name_for_display += " (Branch ikke taget)"
                else:
                    messagebox.showwarning("Input Fejl", f"Vælg 'Branch Taken' eller 'Branch Not Taken' for {instr_mnemonic}.")
                    return
            else:
                cycles_per_instr = instr_info
        else:
            messagebox.showwarning("Ukendt Instruktion", f"Instruktion '{instr_mnemonic}' er ikke kendt eller understøttet i denne beregner.")
            return

        total_cycles_for_this_entry = cycles_per_instr * reps
        self.current_sequence_cycles += total_cycles_for_this_entry
        display_text = f"{display_prefix}{instr_name_for_display} x{reps} ({total_cycles_for_this_entry} cycles)"
        self.sequence_info.append({
            'instr': instr_mnemonic,
            'reps': reps,
            'cycles': total_cycles_for_this_entry,
            'display_text': display_text
        })
        self._update_sequence_display()

    def _add_to_sequence_display(self, display_text, reps, cycles, is_label=False):
        """Adds a pre-formatted string to the sequence display."""
        item = {
            'instr': 'RAW_TEXT',
            'reps': reps,
            'cycles': cycles,
            'display_text': display_text if not is_label else f"{display_text}"
        }
        self.sequence_info.append(item)
        self._update_sequence_display()

    def _update_sequence_display(self):
        self.sequence_text_widget.config(state='normal')
        self.sequence_text_widget.delete(1.0, tk.END)
        display_content = "\n".join([item['display_text'] for item in self.sequence_info])
        self.sequence_text_widget.insert(tk.END, display_content)
        self.sequence_text_widget.see(tk.END)
        self.sequence_text_widget.config(state='disabled')
        self.total_cycles_label.config(text=f"Total Clock Cycles: {self.current_sequence_cycles}")

    def reset_sequence(self):
        self.current_sequence_cycles = 0
        self.sequence_info = []
        self.registers = {}
        self._update_sequence_display()
        messagebox.showinfo("Nulstillet", "Sekvensen er nulstillet.")

    def show_help(self):
        help_text = "Dette er en cheat-sheet beregner for typiske AVR Assembly clock cycles.\n\n"
        help_text += "Du kan tilføje instruktioner enkeltvis eller indsætte flere linjer med kode.\n\n"
        help_text += "For enkelt instruktioner: Indtast instruktion, gentagelser, og vælg branch adfærd for BR-instruktioner.\n\n"
        help_text += "For indsat kode (Mere Kompleks): \n"
        help_text += "  - Indsæt din assembly kode i den store tekstboks. Inkluder labels og kommentarer.\n"
        help_text += "  - Appen detekterer automatisk baglæns 'BR'-instruktioner (f.eks. BRNE, BREQ) som loops.\n"
        help_text += "  - Loop-iterationer estimeres baseret på registerændringer (CLR, DEC, INC) og BRNE.\n"
        help_text += "  - Antager 8-bit registre; f.eks. CLR R16 -> 0, DEC R16 loops 256 gange til 0.\n"
        help_text += "  - Branch adfærd sættes automatisk: 'Branch Taken' for loop-iterationer, 'Branch Not Taken' for sidste.\n"
        help_text += "  - Labels (f.eks. 'IGEN:') og kommentarer (startende med ';') ignoreres i cyklusberegningen, men vises.\n"
        help_text += "  - Andre branch-instruktioner (f.eks. fremlæns spring) behandles som 'Branch Not Taken'.\n"
        help_text += "  - NB: Beregninger er estimater; tjek AVR datablad for præcise cycles!\n\n"
        help_text += "Typiske instruktioner & Cycles (varierer med specifik MCU - tjek datablad!):\n"
        for instr, cycles_info in self.instruction_cycles.items():
            if isinstance(cycles_info, dict):
                help_text += f"- {instr}: {cycles_info['taken']} (taken) / {cycles_info['not_taken']} (not taken)\n"
            else:
                help_text += f"- {instr}: {cycles_info} cycle(s)\n"
        messagebox.showinfo("Instruktioner & Cycles", help_text)

# Example usage with a Tkinter Notebook
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Multi-Tab Application")
    root.geometry("800x900")

    # Create a notebook (tab container)
    notebook = ttk.Notebook(root)
    notebook.pack(pady=10, expand=True, fill='both')

    # Add the clock cycle calculator tab
    clock_cycle_tab = ClockCycleTab(notebook)

    # Add another sample tab for demonstration
    sample_tab = ttk.Frame(notebook)
    notebook.add(sample_tab, text="Sample Tab")
    tk.Label(sample_tab, text="This is a sample tab for demonstration.").pack(pady=20)

    root.mainloop()