
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
import re

class ClockCycleTab(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

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
        self.registers = {}

        # Multi-line input
        multi_instr_label = Gtk.Label(label="Indsæt Assembly Kode Her (inkl. labels og kommentarer):")
        self.append(multi_instr_label)

        multi_instr_scroll = Gtk.ScrolledWindow()
        multi_instr_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        multi_instr_scroll.set_vexpand(True)
        self.multi_instr_text = Gtk.TextView()
        self.multi_instr_text.set_wrap_mode(Gtk.WrapMode.WORD)
        self.multi_instr_text.set_monospace(True)
        multi_instr_scroll.set_child(self.multi_instr_text)
        self.append(multi_instr_scroll)

        # Set default text
        multi_buffer = self.multi_instr_text.get_buffer()
        multi_buffer.set_text("""    CLR R16
    CLR R17
IGEN: NOP
    DEC R16
    BRNE IGEN
    INC R17
    BRNE IGEN""")

        add_multi_button = Gtk.Button(label="Analyser & Tilføj Indsat Kode til Sekvens")
        add_multi_button.connect("clicked", self.on_add_multi_clicked)
        self.append(add_multi_button)

        separator1 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.append(separator1)

        # Single instruction input
        instr_label = Gtk.Label(label="Tilføj Enkelt Instruktion:")
        self.append(instr_label)

        self.instr_entry = Gtk.Entry()
        self.instr_entry.set_placeholder_text("e.g., ADD R16, R17")
        self.instr_entry.connect("activate", self.on_instr_entry_activate)
        self.append(self.instr_entry)

        reps_label = Gtk.Label(label="Antal gentagelser (for loops, standard 1):")
        self.append(reps_label)

        self.reps_entry = Gtk.Entry()
        self.reps_entry.set_text("1")
        self.reps_entry.set_max_width_chars(10)
        self.reps_entry.connect("activate", self.on_instr_entry_activate)
        self.append(self.reps_entry)

        branch_label = Gtk.Label(label="Branch adfærd (kun for BR-instruktioner):")
        self.append(branch_label)

        self.branch_combo = Gtk.ComboBoxText()
        for option in ["Normal", "Branch Taken", "Branch Not Taken"]:
            self.branch_combo.append_text(option)
        self.branch_combo.set_active(0)  # Default to "Normal"
        self.append(self.branch_combo)

        add_button = Gtk.Button(label="Tilføj Enkelt Instruktion til Sekvens")
        add_button.connect("clicked", self.on_add_clicked)
        self.append(add_button)

        separator2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.append(separator2)

        # Sequence display
        sequence_label = Gtk.Label(label="Instruktionssekvens:")
        self.append(sequence_label)

        sequence_scroll = Gtk.ScrolledWindow()
        sequence_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sequence_scroll.set_vexpand(True)
        self.sequence_text = Gtk.TextView()
        self.sequence_text.set_editable(False)
        self.sequence_text.set_monospace(True)
        sequence_scroll.set_child(self.sequence_text)
        self.append(sequence_scroll)

        self.total_cycles_label = Gtk.Label(label=f"Total Clock Cycles: {self.current_sequence_cycles}")
        self.total_cycles_label.set_markup(f'<span size="large" weight="bold">Total Clock Cycles: {self.current_sequence_cycles}</span>')
        self.append(self.total_cycles_label)

        reset_button = Gtk.Button(label="Nulstil Sekvens")
        reset_button.connect("clicked", self.on_reset_clicked)
        self.append(reset_button)

        help_button = Gtk.Button(label="Instruktioner & Cycles (Hint)")
        help_button.connect("clicked", self.on_help_clicked)
        self.append(help_button)

    def _parse_line(self, line):
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
        if instr == "CLR" and operand:
            reg = operand.strip().upper()
            reg_values[reg] = 0
        elif instr == "DEC" and operand:
            reg = operand.strip().upper()
            if reg not in reg_values:
                reg_values[reg] = 0
            reg_values[reg] = (reg_values[reg] - 1) & 0xFF
        elif instr == "INC" and operand:
            reg = operand.strip().upper()
            if reg not in reg_values:
                reg_values[reg] = 0
            reg_values[reg] = (reg_values[reg] + 1) & 0xFF

    def _estimate_loop_iterations(self, instr, operand, labels, line_num, processed_lines, current_reg_values):
        if not operand or not instr.startswith("BR"):
            return 1, "Normal", "Normal"
        target_label = operand.split()[0].upper()
        if target_label not in labels or labels[target_label] >= line_num:
            return 1, "Branch Not Taken", "Branch Not Taken"

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

    def on_add_clicked(self, widget):
        self.add_instruction()

    def on_add_multi_clicked(self, widget):
        self.add_multiple_instructions()

    def on_instr_entry_activate(self, widget):
        self.add_instruction()

    def on_reset_clicked(self, widget):
        self.reset_sequence()

    def on_help_clicked(self, widget):
        self.show_help()

    def add_instruction(self):
        instr_raw = self.instr_entry.get_text().strip()
        reps_str = self.reps_entry.get_text().strip()
        branch_behavior = self.branch_combo.get_active_text()

        if not instr_raw:
            self.show_warning("Input Fejl", "Indtast venligst en instruktion.")
            return
        try:
            reps = int(reps_str)
            if reps <= 0:
                self.show_warning("Input Fejl", "Antal gentagelser skal være et positivt heltal.")
                return
        except ValueError:
            self.show_warning("Input Fejl", "Antal gentagelser skal være et gyldigt heltal.")
            return

        _label, instr_mnemonic, _operand = self._parse_line(instr_raw)
        if not instr_mnemonic:
            self.show_warning("Input Fejl", f"Kunde ikke genkende instruktion fra '{instr_raw}'.")
            return
        self._process_single_instruction_and_add_to_sequence(instr_mnemonic, reps, branch_behavior)
        self.instr_entry.set_text("")
        self.reps_entry.set_text("1")
        self.branch_combo.set_active(0)

    def add_multiple_instructions(self):
        multi_buffer = self.multi_instr_text.get_buffer()
        start_iter, end_iter = multi_buffer.get_bounds()
        pasted_code = multi_buffer.get_text(start_iter, end_iter, False).strip()
        if not pasted_code:
            self.show_warning("Input Fejl", "Indsæt venligst assembly kode i tekstboksen.")
            return

        lines = pasted_code.split('\n')
        self.registers = {}
        processed_lines = []
        labels = {}

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
        reg_values = self.registers.copy()
        outer_loop_detected = False
        outer_iterations = 1
        outer_loop_line = None

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
                    self.current_processing_index = len(self.temp_processed_lines)
                    break
                elif iterations > 1:
                    self._handle_loop_automatically(line_num, iterations, loop_behavior, final_behavior)
                else:
                    self._process_single_instruction_and_add_to_sequence(instr, 1, loop_behavior, f"(L{line_num}) ")
            elif instr:
                self._process_single_instruction_and_add_to_sequence(instr, 1, "Normal", f"(L{line_num}) ")
            self._simulate_register(instr, operand, self.registers)
            self.current_processing_index += 1

        self._finalise_pasted_code_processing()

    def _handle_loop_automatically(self, line_num, iterations, loop_behavior, final_behavior):
        loop_branch_data = next((item for item in self.temp_processed_lines if item['line_num'] == line_num and item['instr']), None)
        if not loop_branch_data:
            self._process_single_instruction_and_add_to_sequence(loop_branch_data['instr'], 1, "Normal", f"(L{line_num}) ")
            return

        loop_target_label = loop_branch_data['operand'].split()[0].upper()
        loop_start_index = self.temp_labels[loop_target_label]
        loop_instructions_data = []
        for i in range(loop_start_index, line_num + 1):
            if self.temp_processed_lines[i]['instr']:
                loop_instructions_data.append(self.temp_processed_lines[i])

        if not loop_instructions_data:
            self.show_warning("Loop Fejl", f"Ingen instruktioner fundet i loopet fra {loop_target_label} til linje {line_num}. Behandler branch som enkelt.")
            self._process_single_instruction_and_add_to_sequence(loop_branch_data['instr'], 1, "Normal", f"(L{line_num}) ")
            return

        cycles_per_loop_iteration = 0
        for instr_data in loop_instructions_data:
            instr_mnemonic = instr_data['instr']
            instr_info = self.instruction_cycles.get(instr_mnemonic)
            if instr_info is None:
                self.show_warning("Ukendt Instruktion", f"Ukendt instruktion '{instr_mnemonic}' i loop. Fortsætter.")
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
        loop_branch_data = next((item for item in self.temp_processed_lines if item['line_num'] == line_num and item['instr']), None)
        if not loop_branch_data:
            self._process_single_instruction_and_add_to_sequence(loop_branch_data['instr'], 1, "Normal", f"(L{line_num}) ")
            return

        loop_target_label = loop_branch_data['operand'].split()[0].upper()
        loop_start_index = self.temp_labels[loop_target_label]
        loop_instructions_data = []
        for i in range(loop_start_index, line_num + 1):
            if self.temp_processed_lines[i]['instr']:
                loop_instructions_data.append(self.temp_processed_lines[i])

        if not loop_instructions_data:
            self.show_warning("Loop Fejl", f"Ingen instruktioner fundet i loopet fra {loop_target_label} til linje {line_num}. Behandler branch som enkelt.")
            self._process_single_instruction_and_add_to_sequence(loop_branch_data['instr'], 1, "Normal", f"(L{line_num}) ")
            return

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

        cycles_per_outer_iteration = inner_loop_cycles
        for instr_data in loop_instructions_data:
            instr_mnemonic = instr_data['instr']
            instr_info = self.instruction_cycles.get(instr_mnemonic)
            if instr_info is None:
                self.show_warning("Ukendt Instruktion", f"Ukendt instruktion '{instr_mnemonic}' i loop. Fortsætter.")
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
        self.show_info("Klar", "Indsat kode er blevet behandlet. Total Clock Cycles opdateret.")
        self.multi_instr_text.get_buffer().set_text("")

    def _process_single_instruction_and_add_to_sequence(self, instr_mnemonic, reps, branch_behavior, display_prefix=""):
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
                    self.show_warning("Input Fejl", f"Vælg 'Branch Taken' eller 'Branch Not Taken' for {instr_mnemonic}.")
                    return
            else:
                cycles_per_instr = instr_info
        else:
            self.show_warning("Ukendt Instruktion", f"Instruktion '{instr_mnemonic}' er ikke kendt eller understøttet i denne beregner.")
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
        item = {
            'instr': 'RAW_TEXT',
            'reps': reps,
            'cycles': cycles,
            'display_text': display_text if not is_label else f"{display_text}"
        }
        self.sequence_info.append(item)
        self._update_sequence_display()

    def _update_sequence_display(self):
        sequence_buffer = self.sequence_text.get_buffer()
        sequence_buffer.set_text("\n".join([item['display_text'] for item in self.sequence_info]))
        self.total_cycles_label.set_markup(f'<span size="large" weight="bold">Total Clock Cycles: {self.current_sequence_cycles}</span>')

    def reset_sequence(self):
        self.current_sequence_cycles = 0
        self.sequence_info = []
        self.registers = {}
        self._update_sequence_display()
        self.show_info("Nulstillet", "Sekvensen er nulstillet.")

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
        self.show_info("Instruktioner & Cycles", help_text)

    def show_warning(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text=title,
            secondary_text=message
        )
        dialog.connect("response", lambda d, _: d.destroy())
        dialog.present()

    def show_info(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title,
            secondary_text=message
        )
        dialog.connect("response", lambda d, _: d.destroy())
        dialog.present()