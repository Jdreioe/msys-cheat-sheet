import tkinter as tk
from tkinter import ttk, scrolledtext
import re

class CAsmConverterTab:
    def __init__(self, notebook, tab_title="C <-> ASM Converter"):
        self.notebook = notebook
        self.tab_frame = ttk.Frame(notebook)
        notebook.add(self.tab_frame, text=tab_title)

        self._create_widgets()

    def _create_widgets(self):
        # C to Assembly Section
        c_to_asm_frame = ttk.LabelFrame(self.tab_frame, text="C til Assembly Konverter")
        c_to_asm_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        tk.Label(c_to_asm_frame, text="Indtast C Kode (simplificeret):").pack(pady=5)
        self.c_input_text = scrolledtext.ScrolledText(c_to_asm_frame, width=60, height=8, wrap=tk.WORD)
        self.c_input_text.pack(pady=5)
        # Updated example C code to be more concise
        self.c_input_text.insert(tk.END, "PORTC = (~PINA) + PINB;") 

        convert_c_button = tk.Button(c_to_asm_frame, text="Konverter C til Assembly", command=self.convert_c_to_asm)
        convert_c_button.pack(pady=5)

        tk.Label(c_to_asm_frame, text="Genereret Assembly Kode:").pack(pady=5)
        self.asm_output_text = scrolledtext.ScrolledText(c_to_asm_frame, width=60, height=8, wrap=tk.WORD, state='disabled')
        self.asm_output_text.pack(pady=5)

        ttk.Separator(self.tab_frame, orient='horizontal').pack(fill='x', padx=5, pady=10)

        # Assembly to C Section
        asm_to_c_frame = ttk.LabelFrame(self.tab_frame, text="Assembly til C Konverter")
        asm_to_c_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        tk.Label(asm_to_c_frame, text="Indtast Assembly Kode (simplificeret):").pack(pady=5)
        self.asm_input_text = scrolledtext.ScrolledText(asm_to_c_frame, width=60, height=8, wrap=tk.WORD)
        self.asm_input_text.pack(pady=5)
        self.asm_input_text.insert(tk.END, "IN R28,PINA\nIN R29,PINB\nCOM R28\nADD R28,R29\nOUT PORTC,R28") # Example Assembly code

        convert_asm_button = tk.Button(asm_to_c_frame, text="Konverter Assembly til C", command=self.convert_asm_to_c)
        convert_asm_button.pack(pady=5)

        tk.Label(asm_to_c_frame, text="Genereret C Kode:").pack(pady=5)
        self.c_output_text = scrolledtext.ScrolledText(asm_to_c_frame, width=60, height=8, wrap=tk.WORD, state='disabled')
        self.c_output_text.pack(pady=5)

        self.conversion_map_asm_to_c = {
            "IN": "{reg} = {port};",
            "OUT": "{port} = {reg};",
            "LDI": "{reg} = {value};",
            "ADD": "{dest_reg} += {src_reg};",
            "SUB": "{dest_reg} -= {src_reg};",
            "AND": "{dest_reg} &= {src_reg};",
            "OR": "{dest_reg} |= {src_reg};",
            "EOR": "{dest_reg} ^= {src_reg};",
            "COM": "{reg} = ~{reg};",
            "MOV": "{dest_reg} = {src_reg};",
            "CLR": "{reg} = 0;",
            "INC": "{reg}++;",
            "DEC": "{reg}--;",
            # This mapping is highly simplified and will miss many cases
        }

        self.conversion_map_c_to_asm = {
            # Assignment with literal
            r"([A-Z_0-9]+)\s*=\s*(0x[0-9a-fA-F]+)\s*;": r"LDI R16, \2\nOUT \1, R16", # PORT = 0xXX
            r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(0x[0-9a-fA-F]+)\s*;": r"LDI R16, \2\nMOV \1, R16", # reg = 0xXX

            # Assignment with variable/port
            r"([A-Z_0-9]+)\s*=\s*([A-Z_0-9]+)\s*;": r"IN R16, \2\nOUT \1, R16", # PORT = PINX, or PORT = PORTY
            r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*;": r"MOV \1, \2", # reg = reg or reg = port

            # Bitwise NOT
            r"([A-Z_0-9]+)\s*=\s*~([A-Z_0-9]+)\s*;": r"IN R16, \2\nCOM R16\nOUT \1, R16", # PORT = ~PINX
            r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*~([a-zA-Z_][a-zA-Z0-9_]*)\s*;": r"MOV R16, \2\nCOM R16\nMOV \1, R16", # reg = ~reg

            # Addition: reg/port = reg/port + reg/port
            r"([A-Z_0-9]+)\s*=\s*([A-Z_0-9]+)\s*\+\s*([A-Z_0-9]+)\s*;": r"IN R16, \2\nIN R17, \3\nADD R16, R17\nOUT \1, R16",
            r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\+\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*;": r"MOV R16, \2\nMOV R17, \3\nADD R16, R17\nMOV \1, R16",
            
            # Specific rule for PORTC = (~PINA) + PINB;
            r"PORTC\s*=\s*\(\s*~PINA\s*\)\s*\+\s*PINB\s*;": "IN R28, PINA\nCOM R28\nIN R29, PINB\nADD R28, R29\nOUT PORTC, R28",
            r"PORTC\s*=\s*~PINA\s*\+\s*PINB\s*;": "IN R28, PINA\nCOM R28\nIN R29, PINB\nADD R28, R29\nOUT PORTC, R28", # Also handle without parentheses

            # Subtraction: reg/port = reg/port - reg/port
            r"([A-Z_0-9]+)\s*=\s*([A-Z_0-9]+)\s*-\s*([A-Z_0-9]+)\s*;": r"IN R16, \2\nIN R17, \3\nSUB R16, R17\nOUT \1, R16",
            r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*-\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*;": r"MOV R16, \2\nMOV R17, \3\nSUB R16, R17\nMOV \1, R16",

            # Increment/Decrement (simplified, assumes variable is also port or register)
            r"([A-Z_0-9]+)\s*\+\+\s*;": r"IN R16, \1\nINC R16\nOUT \1, R16",
            r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\+\+\s*;": r"INC \1",
            r"([A-Z_0-9]+)\s*--\s*;": r"IN R16, \1\nDEC R16\nOUT \1, R16",
            r"([a-zA-Z_][a-zA-Z0-9_]*)\s*--\s*;": r"DEC \1",
            
            # Clear (simplified, assumes variable is also port or register)
            r"([A-Z_0-9]+)\s*=\s*0\s*;": r"CLR R16\nOUT \1, R16",
            r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*0\s*;": r"CLR \1",
        }


    def _update_text_widget(self, widget, content):
        widget.config(state='normal')
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, content)
        widget.config(state='disabled')

    def convert_c_to_asm(self):
        c_code = self.c_input_text.get(1.0, tk.END).strip()
        asm_code_lines = []

        if not c_code:
            self._update_text_widget(self.asm_output_text, "Indtast C-kode for at konvertere.")
            return

        lines = [line.strip() for line in c_code.split('\n') if line.strip()]
        for line in lines:
            converted = False
            for pattern, replacement in self.conversion_map_c_to_asm.items():
                match = re.fullmatch(pattern, line)
                if match:
                    # Replace groups in the replacement string
                    # This is a very basic replacement; real compilers are vastly more complex
                    try:
                        asm_line = replacement
                        for i, group in enumerate(match.groups()):
                            asm_line = asm_line.replace(f"\\{i+1}", group)
                        
                        # Handle register assignments (R16, R17, etc.)
                        # This part assumes a very simple mapping where R16/R17 are temporary.
                        # In real assembly, you'd manage register allocation carefully.
                        if "R16" in asm_line or "R17" in asm_line:
                            # Try to make it a bit more specific if possible.
                            # For the example: PORTC = ~PINA + PINB;
                            # We use R28, R29 for intermediate results.
                            if ("PINA" in line or "pina" in line) and \
                               ("PINB" in line or "pinb" in line) and \
                               ("PORTC" in line or "portc" in line):
                                asm_line = asm_line.replace("R16", "R28").replace("R17", "R29")

                        asm_code_lines.append(asm_line)
                        converted = True
                        break
                    except IndexError: # Not enough groups to replace
                        pass # Try next pattern

            if not converted:
                asm_code_lines.append(f"; TODO: Konvertering for '{line}' er ikke implementeret")
        
        self._update_text_widget(self.asm_output_text, "\n".join(asm_code_lines))

    def convert_asm_to_c(self):
        asm_code = self.asm_input_text.get(1.0, tk.END).strip()
        c_code_lines = []
        register_values = {} # To keep track of what's in registers for better conversion
        # This will store the operation applied to a register for simplification
        register_ops = {} # e.g., {'R28': '~PINA', 'R29': 'PINB'}

        if not asm_code:
            self._update_text_widget(self.c_output_text, "Indtast Assembly-kode for at konvertere.")
            return

        lines = [line.strip() for line in asm_code.split('\n') if line.strip() and not line.startswith(';')]
        for line in lines:
            parts = re.split(r'\s+', line, 1)
            instr = parts[0].upper()
            operand_str = parts[1] if len(parts) > 1 else ""
            operands = [op.strip() for op in operand_str.split(',') if op.strip()]

            converted = False
            if instr in self.conversion_map_asm_to_c:
                template = self.conversion_map_asm_to_c[instr]
                try:
                    if instr == "IN" and len(operands) == 2:
                        reg, port = operands[0].upper(), operands[1].upper()
                        c_line = template.format(reg=reg, port=port)
                        register_values[reg] = port # Track that reg now holds port value
                        register_ops[reg] = port # Store the source operation
                        c_code_lines.append(c_line)
                        converted = True
                    elif instr == "OUT" and len(operands) == 2:
                        port, reg = operands[0].upper(), operands[1].upper()
                        # Try to resolve 'reg' back to its original C expression
                        resolved_reg_expr = register_ops.get(reg, reg)
                        c_line = f"{port} = {resolved_reg_expr};" # Use simplified expression
                        c_code_lines.append(c_line)
                        converted = True
                    elif instr == "LDI" and len(operands) == 2:
                        reg, value = operands[0].upper(), operands[1]
                        c_line = template.format(reg=reg, value=value)
                        register_values[reg] = value # Track literal value
                        register_ops[reg] = value # Store the literal
                        c_code_lines.append(c_line)
                        converted = True
                    elif instr in ["ADD", "SUB", "AND", "OR", "EOR", "MOV"] and len(operands) == 2:
                        dest_reg, src_reg = operands[0].upper(), operands[1].upper()
                        
                        # Resolve source and destination expressions
                        resolved_src_expr = register_ops.get(src_reg, src_reg)
                        resolved_dest_expr = register_ops.get(dest_reg, dest_reg)
                        
                        op_symbol = {
                            "ADD": "+", "SUB": "-", "AND": "&", "OR": "|", "EOR": "^", "MOV": "="
                        }.get(instr, "??")

                        if instr == "MOV":
                            c_line = f"{resolved_dest_expr} = {resolved_src_expr};"
                        else:
                            c_line = f"{resolved_dest_expr} {op_symbol}= {resolved_src_expr};"
                        
                        # Update tracking for dest_reg with the new combined expression
                        if op_symbol == "=":
                             register_ops[dest_reg] = f"{resolved_src_expr}"
                        else:
                             register_ops[dest_reg] = f"({resolved_dest_expr} {op_symbol} {resolved_src_expr})"


                        c_code_lines.append(c_line)
                        converted = True
                        
                    elif instr == "COM" and len(operands) == 1:
                        reg = operands[0].upper()
                        resolved_reg_expr = register_ops.get(reg, reg)
                        c_line = f"{resolved_reg_expr} = ~{resolved_reg_expr};"
                        register_ops[reg] = f"(~{resolved_reg_expr})" # Update expression for further ops
                        c_code_lines.append(c_line)
                        converted = True
                    elif instr in ["INC", "DEC", "CLR"] and len(operands) == 1:
                        reg = operands[0].upper()
                        c_line = template.format(reg=reg)
                        c_code_lines.append(c_line)
                        converted = True
                        # Update register value for these operations as well
                        if instr == "CLR": register_values[reg] = 0; register_ops[reg] = "0"
                        # INC/DEC are harder to track exact value without full sim, keep as is
                        elif instr == "INC": register_ops[reg] = f"{reg}++"
                        elif instr == "DEC": register_ops[reg] = f"{reg}--"


                except IndexError:
                    pass # Not enough operands, or wrong format, try next

            if not converted:
                c_code_lines.append(f"// TODO: Conversion for '{line}' not implemented or too complex.")
        
        # Final pass to simplify expressions. This is the heuristic part.
        final_c_lines = []
        # A simple state to track if a register was the source of a port IN
        # This is a very rough approach to combine lines like (R28 = PINA) + (R29 = PINB) -> PORTC = R28 + R29
        # and then substitute R28, R29 with their sources
        
        # This will be tricky. Let's try to do a single pass and resolve immediately.
        
        # Reset and do another pass for combined conversion. This is still a heuristic.
        combined_c_code = []
        temp_register_expressions = {} # Holds the C expression that a register currently represents
        
        for line in lines:
            parts = re.split(r'\s+', line, 1)
            instr = parts[0].upper()
            operand_str = parts[1] if len(parts) > 1 else ""
            operands = [op.strip() for op in operand_str.split(',') if op.strip()]

            if instr == "IN" and len(operands) == 2:
                reg, port = operands[0].upper(), operands[1].upper()
                temp_register_expressions[reg] = port
            elif instr == "COM" and len(operands) == 1:
                reg = operands[0].upper()
                if reg in temp_register_expressions:
                    temp_register_expressions[reg] = f"(~{temp_register_expressions[reg]})"
                else:
                    temp_register_expressions[reg] = f"(~{reg})" # Fallback if not tracked
            elif instr == "ADD" and len(operands) == 2:
                dest_reg, src_reg = operands[0].upper(), operands[1].upper()
                dest_expr = temp_register_expressions.get(dest_reg, dest_reg)
                src_expr = temp_register_expressions.get(src_reg, src_reg)
                temp_register_expressions[dest_reg] = f"({dest_expr} + {src_expr})"
            elif instr == "OUT" and len(operands) == 2:
                port, reg = operands[0].upper(), operands[1].upper()
                resolved_expr = temp_register_expressions.get(reg, reg)
                combined_c_code.append(f"{port} = {resolved_expr};")
                # Clear expressions for regs that are "consumed" by an OUT
                if reg in temp_register_expressions:
                    del temp_register_expressions[reg]
            else:
                # For any other instruction, just convert it directly using the basic map
                # and don't try to chain expressions for now.
                template = self.conversion_map_asm_to_c.get(instr)
                if template:
                     c_line = ""
                     if instr in ["ADD", "SUB", "AND", "OR", "EOR", "MOV"] and len(operands) == 2:
                        dest_reg, src_reg = operands[0].upper(), operands[1].upper()
                        op_symbol = {
                            "ADD": "+", "SUB": "-", "AND": "&", "OR": "|", "EOR": "^", "MOV": "="
                        }.get(instr, "??")
                        
                        resolved_src = temp_register_expressions.get(src_reg, src_reg)
                        resolved_dest = temp_register_expressions.get(dest_reg, dest_reg)

                        if instr == "MOV":
                            c_line = f"{resolved_dest} = {resolved_src};"
                            temp_register_expressions[dest_reg] = resolved_src
                        else:
                            c_line = f"{resolved_dest} {op_symbol}= {resolved_src};"
                            temp_register_expressions[dest_reg] = f"({resolved_dest} {op_symbol} {resolved_src})"
                     elif instr in ["COM", "INC", "DEC", "CLR"] and len(operands) == 1:
                        reg = operands[0].upper()
                        resolved_reg = temp_register_expressions.get(reg, reg)
                        if instr == "COM":
                            c_line = f"{resolved_reg} = ~{resolved_reg};"
                            temp_register_expressions[reg] = f"(~{resolved_reg})"
                        elif instr == "INC":
                            c_line = f"{resolved_reg}++;"
                            temp_register_expressions[reg] = f"({resolved_reg} + 1)" # Simplified
                        elif instr == "DEC":
                            c_line = f"{resolved_reg}--;"
                            temp_register_expressions[reg] = f"({resolved_reg} - 1)" # Simplified
                        elif instr == "CLR":
                            c_line = f"{resolved_reg} = 0;"
                            temp_register_expressions[reg] = "0"
                     else: # For other simple IN/OUT/LDI not part of the expression chain
                        # This should ideally be caught by previous specific rules
                        # or requires more robust parsing of generic arguments
                        c_line = f"// Unhandled general conversion for: {line}"
                     
                     if c_line:
                        combined_c_code.append(c_line)
                else:
                    combined_c_code.append(f"// TODO: Conversion for '{line}' not implemented or too complex.")

        # Remove duplicate assignments or intermediate register lines that are now consolidated
        # This is very crude and might remove valid lines in complex scenarios.
        # A proper compiler would generate an Abstract Syntax Tree (AST) for this.
        final_output_lines = []
        temp_regs_used_in_last_complex_expr = set()

        for i, line in enumerate(combined_c_code):
            # If the line is an assignment to a temporary register (R28, R29 etc)
            # and that register is part of a complex expression that was just emitted
            # then skip this line.
            skip_line = False
            for reg in ["R16", "R17", "R28", "R29"]: # Expand as needed
                if f"{reg} =" in line and reg not in temp_regs_used_in_last_complex_expr:
                    # If this reg was only for an intermediate step that got consolidated into final output
                    # and it's not reused later in the immediately following lines
                    # This check is very hard without full AST or data flow analysis
                    pass # For now, let's keep all intermediate lines if not auto-combined by OUT logic

            # The current OUT logic already handles the specific example combining everything into one line.
            # So, for the example "IN R28,PINA\nIN R29,PINB\nCOM R28\nADD R28,R29\nOUT PORTC,R28"
            # It should just produce: "PORTC = (~PINA) + PINB;"
            # The way 'temp_register_expressions' works above should achieve this.
            
            # The 'final_c_lines' is already building up the simplified expressions.
            # Let's ensure we only output what's relevant.
            
            # The current logic for `combined_c_code` should only append the final `OUT` lines for chained operations.
            # For standalone operations (like `LDI R16, 0xAF` or `INC R16`), they will be added directly.
            
            final_output_lines.append(line) # This will contain the single combined line for the example

        self._update_text_widget(self.c_output_text, "\n".join(final_output_lines))