import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango


class BitShiftRotateTab(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self._create_widgets()

    def _create_widgets(self):
        # --- Main Title ---
        title_label = Gtk.Label()
        # Set a larger, bold font for the main title using Pango markup
        title_label.set_markup("<span font_desc='Sans Bold 16'>Bit Skift & Rotering Instruktioner (AVR)</span>")
        title_label.set_halign(Gtk.Align.START)
        self.append(title_label)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.append(scrolled_window)

        info_text_view = Gtk.TextView()
        info_text_view.set_editable(False)
        info_text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        info_text_view.set_cursor_visible(False)
        scrolled_window.set_child(info_text_view)

        text_buffer = info_text_view.get_buffer()
        tag_table = text_buffer.get_tag_table()

        # --- Define Text Tags ---
        # Tag for bold text
        bold_tag = Gtk.TextTag(name="bold")
        bold_tag.set_property("weight", Pango.Weight.BOLD)
        tag_table.add(bold_tag)

        # Tag for monospace font (for code examples/diagrams)
        monospace_tag = Gtk.TextTag(name="monospace")
        monospace_tag.set_property("family", "monospace")
        tag_table.add(monospace_tag)

        # --- Define Text Segments and Keywords for Tagging ---
        # Initial paragraphs
        initial_text = (
            "Bit skift- og roteringsinstruktioner er grundlæggende operationer i mikrokontrollerprogrammering til at manipulere individuelle bits i et register eller til at udføre hurtige multiplikationer/divisioner med potenser af 2.\n\n"
            "AVR-arkitekturen inkluderer flere sådanne instruktioner:\n\n"
        )
        
        # LSL Section
        lsl_title = "1.  LSL (Logical Shift Left)\n"
        lsl_desc = (
            "    Beskrivelse: Skubber alle bits i et register én position til venstre. Den mest venstre bit (MSB) flyttes ind i Carry-flagget (C i SREG), og den mest højre bit (LSB) fyldes med en nul.\n"
            "    Formål: Ækvivalent med at multiplicere et usignedt tal med 2 (for hver skift).\n"
            "    Instruktion: LSL Rd\n"
            "    Cycles: 1\n"
            "    Eksempel (8-bit register, før = 0b10010010):\n\n"
        )
        lsl_diagram = (
            "C  7 6 5 4 3 2 1 0  (Bit positions)\n"
            ".  1 0 0 1 0 0 1 0  (Before LSL)\n"
            "     |\n"
            "     v\n"
            "1  0 0 1 0 0 1 0 0  (After LSL)\n\n"
        )
        lsl_flags_use = (
            "    Effekt på flags: Z, N, C, H, V (alle påvirkes)\n"
            "    Hvornår skal den bruges?\n"
            "    Til hurtig multiplikation af usignerede tal med 2.\n"
            "    Når du skal flytte en bit fra MSB-positionen ind i Carry-flagget for senere inspektion eller brug i en multi-byte operation (f.eks. ved overførsel til et andet register via Carry).\n"
            "    Carry-flaggets tidligere værdi har ingen betydning for denne instruktion; det bruges kun som output.\n\n"
        )

        # LSR Section
        lsr_title = "2.  LSR (Logical Shift Right)\n"
        lsr_desc = (
            "    Beskrivelse: Skubber alle bits i et register én position til højre. Den mest højre bit (LSB) flyttes ind i Carry-flagget (C i SREG), og den mest venstre bit (MSB) fyldes med en nul.\n"
            "    Formål: Ækvivalent med at dividere et usignedt tal med 2 (for hver skift).\n"
            "    Instruktion: LSR Rd\n"
            "    Cycles: 1\n"
            "    Eksempel (8-bit register, før = 0b10010010):\n\n"
        )
        lsr_diagram = (
            "C  7 6 5 4 3 2 1 0  (Bit positions)\n"
            "    0  1 0 0 1 0 0 1 0  (Before LSR)\n"
            "    ^\n"
            "    |\n"
            "    0  0 1 0 0 1 0 0 1  (After LSR)\n\n"
        )
        lsr_flags_use = (
            "    Effekt på flags: Z, N, C, H, V (alle påvirkes)\n"
            "    Hvornår skal den bruges?\n"
            "    Til hurtig division af usignerede tal med 2.\n"
            "    Når du skal flytte en bit fra LSB-positionen ind i Carry-flagget (f.eks. for at tjekke, om et tal er ulige, eller for at forberede en multi-byte operation).\n"
            "    Carry-flaggets tidligere værdi har ingen betydning for denne instruktion; det bruges kun som output.\n\n"
        )

        # ROL Section
        rol_title = "3.  ROL (Rotate Left Through Carry)\n"
        rol_desc = (
            "    Beskrivelse: Roterer alle bits i et register én position til venstre. Den mest venstre bit (MSB) flyttes ind i Carry-flagget (C i SREG), OG det eksisterende Carry-flag flyttes ind i den mest højre bit (LSB). Dette er en \"rotation gennem Carry\".\n"
            "    Instruktion: ROL Rd (Eller ADC Rd, Rd som er en ækvivalent instruktion for ROL i mange tilfælde, da den udfører Rd = Rd + Rd + C)\n"
            "    Cycles: 1\n"
        )
        rol_example1_header = "    Eksempel (8-bit register, før = 0b10010010, C-flag = 0):\n\n"
        rol_diagram1 = (
            "C  7 6 5 4 3 2 1 0  (Bit positions)\n"
            "    0  1 0 0 1 0 0 1 0  (Before ROL)\n"
            "    |<-             <-|  (Rotation path)\n"
            "    v               ^\n"
            "    1  0 0 1 0 0 1 0 0  (After ROL)\n\n"
        )
        rol_example2_header = "    Eksempel (8-bit register, før = 0b10010010, C-flag = 1):\n\n"
        rol_diagram2 = (
            "C  7 6 5 4 3 2 1 0  (Bit positions)\n"
            "    1  1 0 0 1 0 0 1 0  (Before ROL)\n"
            "    |<-             <-|  (Rotation path)\n"
            "    v               ^\n"
            "    1  0 0 1 0 0 1 0 1  (After ROL)\n\n"
        )
        rol_flags_use = (
            "    Effekt på flags: Z, N, C, H, V (alle påvirkes)\n"
            "    Hvornår skal den bruges?\n"
            "    Til at udføre multi-byte venstreskift: Start med LSL på det laveste register, derefter ROL på de højere registre. Dette sikrer, at Carry-flagget (som indeholder den bit, der \"skiftede ud\" fra det lavere register) roteres ind i LSB af det næste register.\n"
            "    Til at udføre cirkulære rotationer hvor alle bits (inklusive Carry-flagget) deltager.\n"
            "    Vigtigt: Hvis Carry-flaggets tilstand er ukendt, og du ikke ønsker, at det skal påvirke rotationen, skal du eksplicit rydde det (CLC) eller sætte det (SEC) FØR du udfører ROL. Ellers kan resultatet være uforudsigeligt.\n\n"
        )

        # ROR Section
        ror_title = "4.  ROR (Rotate Right Through Carry)\n"
        ror_desc = (
            "    Beskrivelse: Roterer alle bits i et register én position til højre. Den mest højre bit (LSB) flyttes ind i Carry-flagget (C i SREG), OG det eksisterende Carry-flag flyttes ind i den mest venstre bit (MSB). Dette er en \"rotation gennem Carry\".\n"
            "    Instruktion: ROR Rd\n"
            "    Cycles: 1\n"
        )
        ror_example1_header = "    Eksempel (8-bit register, før = 0b10010010, C-flag = 1):\n\n"
        ror_diagram1 = (
            "C  7 6 5 4 3 2 1 0  (Bit positions)\n"
            "    1  1 0 0 1 0 0 1 0  (Before ROR)\n"
            "    ^               ^\n"
            "    |->             ->|  (Rotation path)\n"
            "    0  1 1 0 0 1 0 0 1  (After ROR)\n\n"
        )
        ror_example2_header = "    Eksempel (8-bit register, før = 0b10010010, C-flag = 0):\n\n"
        ror_diagram2 = (
            "C  7 6 5 4 3 2 1 0  (Bit positions)\n"
            "    0  1 0 0 1 0 0 1 0  (Before ROR)\n"
            "    ^               ^\n"
            "    |->             ->|  (Rotation path)\n"
            "    0  0 1 0 0 1 0 0 1  (After ROR)\n\n"
        )
        ror_flags_use = (
            "    Effekt på flags: Z, N, C, H, V (alle påvirkes)\n"
            "    Hvornår skal den bruges?\n"
            "    Til at udføre multi-byte højreskift: Start med LSR på det højeste register, derefter ROR på de lavere registre. Dette sikrer, at Carry-flagget (som indeholder den bit, der \"skiftede ud\" fra det højere register) roteres ind i MSB af det næste register.\n"
            "    Til at udføre cirkulære rotationer hvor alle bits (inklusive Carry-flagget) deltager.\n"
            "    Vigtigt: Hvis Carry-flaggets tilstand er ukendt, og du ikke ønsker, at det skal påvirke rotationen, skal du eksplicit rydde det (CLC) eller sætte det (SEC) FØR du udfører ROR. Ellers kan resultatet være uforudsigeligt.\n\n"
        )

        # Final section
        carry_flag_importance_title = "Vigtighed af Carry Flag (C):\n"
        carry_flag_importance_content = (
            "For ROL og ROR er Carry-flagget ikke bare en destination for en skubbet bit, men også en kilde for den bit, der roteres ind i den modsatte ende af registret. Dette gør dem yderst nyttige til at håndtere skift og rotationer af tal, der er bredere end et enkelt 8-bit register (f.eks. 16-bit eller 32-bit tal gemt i flere 8-bit registre). Hvis du kun ønsker en simpel bitrotation inden for et 8-bit register uden involvering af Carry-flagget (dvs. den udskiftede bit roteres direkte tilbage til den anden ende af registret), skal du sørge for at rydde Carry-flagget før operationen (CLC).\n"
        )

        # --- Helper function to insert text and apply tags ---
        def append_text_with_tags(text_segment, bold_keywords=[], monospace_segments=[]):
            start_offset = text_buffer.get_end_iter().get_offset()
            text_buffer.insert_at_cursor(text_segment)
            end_offset = text_buffer.get_end_iter().get_offset()

            # Apply bolding to keywords within the segment
            for keyword in bold_keywords:
                current_start = start_offset
                while True:
                    search_start_iter = text_buffer.get_iter_at_offset(current_start)
                    
                    # --- Robust unpacking for forward_search ---
                    search_result = search_start_iter.forward_search(keyword, 0, None)
                    
                    found = False
                    iter_start = None
                    iter_end = None

                    if isinstance(search_result, tuple):
                        if len(search_result) == 3:
                            found, iter_start, iter_end = search_result
                        elif len(search_result) == 2: # Handle the unexpected 2-value case
                            found, iter_start = search_result
                            if found and iter_start: # If found, iter_start should be a valid iterator
                                iter_end = iter_start.copy()
                                iter_end.forward_chars(len(keyword))
                    # --- End of robust unpacking ---
                    
                    if found and iter_start.get_offset() < end_offset:
                        text_buffer.apply_tag(bold_tag, iter_start, iter_end)
                        current_start = iter_end.get_offset()
                    else:
                        break
            
            # Apply monospace to specific segments
            for mono_segment in monospace_segments:
                current_start = start_offset
                while True:
                    search_start_iter = text_buffer.get_iter_at_offset(current_start)
                    
                    # --- Robust unpacking for forward_search ---
                    search_result = search_start_iter.forward_search(mono_segment, 0, None)

                    found = False
                    iter_start = None
                    iter_end = None

                    if isinstance(search_result, tuple):
                        if len(search_result) == 3:
                            found, iter_start, iter_end = search_result
                        elif len(search_result) == 2: # Handle the unexpected 2-value case
                            found, iter_start = search_result
                            if found and iter_start: # If found, iter_start should be a valid iterator
                                iter_end = iter_start.copy()
                                iter_end.forward_chars(len(mono_segment)) # Use mono_segment length
                    # --- End of robust unpacking ---

                    if found and iter_start.get_offset() < end_offset:
                        text_buffer.apply_tag(monospace_tag, iter_start, iter_end)
                        current_start = iter_end.get_offset()
                    else:
                        break

        # --- Insert all text content and apply formatting ---
        text_buffer.insert_at_cursor(initial_text)

        # LSL Section
        text_buffer.insert_at_cursor(lsl_title)
        text_buffer.apply_tag(bold_tag, text_buffer.get_iter_at_offset(text_buffer.get_end_iter().get_offset() - len(lsl_title)), text_buffer.get_end_iter())
        
        append_text_with_tags(lsl_desc, bold_keywords=["Beskrivelse:", "Formål:", "Instruktion:", "Cycles:", "Eksempel (8-bit register, før = 0b10010010):"])
        append_text_with_tags(lsl_diagram, monospace_segments=[lsl_diagram]) # Corrected to use full string
        append_text_with_tags(lsl_flags_use, bold_keywords=["Effekt på flags:", "Hvornår skal den bruges?"])

        # LSR Section
        text_buffer.insert_at_cursor(lsr_title)
        text_buffer.apply_tag(bold_tag, text_buffer.get_iter_at_offset(text_buffer.get_end_iter().get_offset() - len(lsr_title)), text_buffer.get_end_iter())

        append_text_with_tags(lsr_desc, bold_keywords=["Beskrivelse:", "Formål:", "Instruktion:", "Cycles:", "Eksempel (8-bit register, før = 0b10010010):"])
        append_text_with_tags(lsr_diagram, monospace_segments=[lsr_diagram]) # Corrected to use full string
        append_text_with_tags(lsr_flags_use, bold_keywords=["Effekt på flags:", "Hvornår skal den bruges?"])

        # ROL Section
        text_buffer.insert_at_cursor(rol_title)
        text_buffer.apply_tag(bold_tag, text_buffer.get_iter_at_offset(text_buffer.get_end_iter().get_offset() - len(rol_title)), text_buffer.get_end_iter())

        append_text_with_tags(rol_desc, bold_keywords=["Beskrivelse:", "Instruktion:", "Cycles:"])
        
        append_text_with_tags(rol_example1_header, bold_keywords=[rol_example1_header.strip()])
        append_text_with_tags(rol_diagram1, monospace_segments=[rol_diagram1]) # Corrected to use full string

        append_text_with_tags(rol_example2_header, bold_keywords=[rol_example2_header.strip()])
        append_text_with_tags(rol_diagram2, monospace_segments=[rol_diagram2]) # Corrected to use full string

        append_text_with_tags(rol_flags_use, bold_keywords=["Effekt på flags:", "Hvornår skal den bruges?", "Vigtigt:"])

        # ROR Section
        text_buffer.insert_at_cursor(ror_title)
        text_buffer.apply_tag(bold_tag, text_buffer.get_iter_at_offset(text_buffer.get_end_iter().get_offset() - len(ror_title)), text_buffer.get_end_iter())

        append_text_with_tags(ror_desc, bold_keywords=["Beskrivelse:", "Instruktion:", "Cycles:"])

        append_text_with_tags(ror_example1_header, bold_keywords=[ror_example1_header.strip()])
        append_text_with_tags(ror_diagram1, monospace_segments=[ror_diagram1]) # Corrected to use full string

        append_text_with_tags(ror_example2_header, bold_keywords=[ror_example2_header.strip()])
        append_text_with_tags(ror_diagram2, monospace_segments=[ror_diagram2]) # Corrected to use full string

        append_text_with_tags(ror_flags_use, bold_keywords=["Effekt på flags:", "Hvornår skal den bruges?", "Vigtigt:"])

        # Final section
        text_buffer.insert_at_cursor(carry_flag_importance_title)
        text_buffer.apply_tag(bold_tag, text_buffer.get_iter_at_offset(text_buffer.get_end_iter().get_offset() - len(carry_flag_importance_title)), text_buffer.get_end_iter())
        append_text_with_tags(carry_flag_importance_content)