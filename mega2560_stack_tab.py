import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango

class Mega2560StackTab(Gtk.Box):
    """
    GTK4 tab displaying information about the ATmega2560 Hardware Stack.
    """
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)

        self._create_widgets()

    def _create_widgets(self):
        title_label = Gtk.Label(label="ATmega2560 Hardware Stack")
        title_label.set_markup("<span font_desc='Arial Bold 16'>ATmega2560 Hardware Stack</span>")
        title_label.set_halign(Gtk.Align.CENTER)
        self.append(title_label)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        self.append(scrolled_window)

        info_text_view = Gtk.TextView()
        info_text_view.set_editable(False)
        info_text_view.set_cursor_visible(False)
        info_text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        
        scrolled_window.set_child(info_text_view)

        # Get the GtkTextBuffer to insert content
        text_buffer = info_text_view.get_buffer()
        tag_table = text_buffer.get_tag_table()

        # --- Define Text Tags ---
        # Tag for bold text
        bold_tag = Gtk.TextTag(name="bold")
        bold_tag.set_property("weight", Pango.Weight.BOLD)
        tag_table.add(bold_tag)

        # Tag for monospace font
        monospace_tag = Gtk.TextTag(name="monospace")
        monospace_tag.set_property("family", "monospace")
        monospace_tag.set_property("size", Pango.units_from_double(9 * Pango.SCALE)) # Slightly smaller for code
        tag_table.add(monospace_tag)

        # --- Helper function to insert text and apply tags ---
        def append_text_with_tags(text_segment, bold_keywords=[], monospace_segments=[]):
            start_iter = text_buffer.get_end_iter()
            text_buffer.insert(start_iter, text_segment)
            end_iter = text_buffer.get_end_iter()

            # Apply bolding to keywords within the segment
            for keyword in bold_keywords:
                search_start_iter = text_buffer.get_iter_at_offset(start_iter.get_offset())
                while True:
                    found_tuple = search_start_iter.forward_search(keyword, 0, end_iter)
                    
                    if found_tuple:
                        found, match_start, match_end = found_tuple
                        if found and match_start.get_offset() < end_iter.get_offset():
                            text_buffer.apply_tag(bold_tag, match_start, match_end)
                            search_start_iter = match_end.copy() 
                        else:
                            break
                    else:
                        break
            
            # Apply monospace to specific segments
            for mono_segment in monospace_segments:
                search_start_iter = text_buffer.get_iter_at_offset(start_iter.get_offset())
                while True:
                    found_tuple = search_start_iter.forward_search(mono_segment, 0, end_iter)
                    
                    if found_tuple:
                        found, match_start, match_end = found_tuple
                        if found and match_start.get_offset() < end_iter.get_offset():
                            text_buffer.apply_tag(monospace_tag, match_start, match_end)
                            search_start_iter = match_end.copy() 
                        else:
                            break
                    else:
                        break

        # --- Define content segments ---
        intro_text = (
            "ATmega2560 (og andre AVR-mikrocontrollere) bruger en hardware-implementeret stak til midlertidig lagring af data, især ved subrutinekald og afbrydelser. Stakken vokser nedad i hukommelsen (mod lavere adresser).\n\n"
        )
        what_is_stack_title = "Hvad er Stakken?\n"
        what_is_stack_content = (
            "* Et område i SRAM (Static RAM) der fungerer som et LIFO (Last-In, First-Out) lager.\n"
            "* Bruges til at gemme returadresser for subrutiner og afbrydelser, samt til at gemme midlertidige data (f.eks. registerværdier) under funktionseksekvering.\n\n"
        )
        sp_title = "Stack Pointer (SP)\n"
        sp_content = (
            "* En 16-bit register, der altid peger på den *næste ledige* adresse på stakken.\n"
            "* På ATmega2560 er SP en kombination af to 8-bit I/O-registre: SPH (Stack Pointer High) og SPL (Stack Pointer Low).\n"
            "* Initialiseres typisk til det højeste SRAM-adresse (end RAM). Eksempel: LDI R16, HIGH(RAMEND); OUT SPH, R16; LDI R16, LOW(RAMEND); OUT SPL, R16;\n\n"
        )
        stack_ops_title = "Stakoperationer:\n\n"
        push_title = "1.  PUSH (Læg på stakken)\n"
        push_content = (
            "    * PUSH Rr: Indholdet af register Rr lægges på stakken.\n"
            "    * Sekvens:\n"
            "        1.  SP dekrementeres (SP = SP - 1).\n"
            "        2.  Indholdet af Rr gemmes på den adresse, som SP nu peger på.\n"
            "    * Cycles: 2 cycles\n\n"
        )
        pop_title = "2.  POP (Tag fra stakken)\n"
        pop_content = (
            "    * POP Rd: Indholdet fra stakken tages og lægges i register Rd.\n"
            "    * Sekvens:\n"
            "        1.  Indholdet fra den adresse, som SP peger på, lægges i Rd.\n"
            "        2.  SP inkrementeres (SP = SP + 1).\n"
            "    * Cycles: 2 cycles\n\n"
        )
        subroutine_interrupt_title = "Subrutinekald og Afbrydelser:\n\n"
        call_content = (
            "* CALL k (Kald subrutine):\n"
            "    * Lægger den 22-bit returadresse (PC + 1) på stakken (3 bytes).\n"
            "    * Springer til adressen k.\n"
            "    * SP dekrementeres med 3.\n"
            "    * Cycles: 4 cycles\n\n"
        )
        rcall_content = (
            "* RCALL k (Relativt kald subrutine):\n"
            "    * Lægger den 22-bit returadresse (PC + 1) på stakken (3 bytes).\n"
            "    * Springer til PC + k.\n"
            "    * SP dekrementeres med 3.\n"
            "    * Cycles: 3 cycles\n\n"
        )
        ret_content = (
            "* RET (Return fra subrutine):\n"
            "    * Tager returadressen fra stakken.\n"
            "    * SP inkrementeres med 3.\n"
            "    * Spring til den hentede adresse.\n"
            "    * Cycles: 4 cycles\n\n"
        )
        interrupt_content = (
            "* Afbrydelse (Interrupt):\n"
            "    * Automatisk PUSH af returadresse og Status Register (SREG).\n"
            "    * Springer til afbrydelsesvektoren.\n\n"
        )
        reti_content = (
            "* RETI (Return fra afbrydelse):\n"
            "    * Automatisk POP af SREG og returadresse.\n"
            "    * Spring til den hentede adresse.\n"
            "    * Cycles: 4 cycles\n\n"
        )
        important_points_title = "Vigtige punkter:\n"
        important_points_content = (
            "* Stakoverløb (Stack Overflow): Hvis stakken vokser ud over det tildelte SRAM-område og kolliderer med andre variable, kan det forårsage uforudsigelig adfærd.\n"
            "* Stakunderløb (Stack Underflow): Hvis du popper mere data end du har pushet, kan du hente meningsløse værdier eller forsøge at læse fra ugyldige hukommelsesadresser.\n"
            "* Stakken og SREG: Ved afbrydelser pushes SREG automatisk for at bevare CPU-status. Ved normal subrutine brug skal du selv gemme SREG (PUSH Rr) hvis din subrutine ændrer statusflag.\n"
        )

        # --- Insert all text content and apply formatting using tags ---
        append_text_with_tags(intro_text)

        append_text_with_tags(what_is_stack_title, bold_keywords=["Hvad er Stakken?"])
        append_text_with_tags(what_is_stack_content, bold_keywords=["SRAM", "LIFO"])

        append_text_with_tags(sp_title, bold_keywords=["Stack Pointer (SP)"])
        append_text_with_tags(sp_content, bold_keywords=["SPH", "SPL"],
                              monospace_segments=["LDI R16, HIGH(RAMEND); OUT SPH, R16; LDI R16, LOW(RAMEND); OUT SPL, R16;"])
        
        append_text_with_tags(stack_ops_title, bold_keywords=["Stakoperationer:"])

        append_text_with_tags(push_title, bold_keywords=["PUSH (Læg på stakken)"])
        append_text_with_tags(push_content, bold_keywords=["PUSH Rr", "Sekvens:", "Cycles:"],
                              monospace_segments=["PUSH Rr", "SP = SP - 1"])
        
        append_text_with_tags(pop_title, bold_keywords=["POP (Tag fra stakken)"])
        append_text_with_tags(pop_content, bold_keywords=["POP Rd", "Sekvens:", "Cycles:"],
                              monospace_segments=["POP Rd", "SP = SP + 1"])
        
        append_text_with_tags(subroutine_interrupt_title, bold_keywords=["Subrutinekald og Afbrydelser:"])

        append_text_with_tags(call_content, bold_keywords=["CALL k (Kald subrutine):", "Cycles:"],
                              monospace_segments=["CALL k"])
        
        append_text_with_tags(rcall_content, bold_keywords=["RCALL k (Relativt kald subrutine):", "Cycles:"],
                              monospace_segments=["RCALL k"])
        
        append_text_with_tags(ret_content, bold_keywords=["RET (Return fra subrutine):", "Cycles:"])

        append_text_with_tags(interrupt_content, bold_keywords=["Afbrydelse (Interrupt):", "SREG"])

        append_text_with_tags(reti_content, bold_keywords=["RETI (Return fra afbrydelse):", "SREG", "Cycles:"])

        append_text_with_tags(important_points_title, bold_keywords=["Vigtige punkter:"])
        append_text_with_tags(important_points_content, bold_keywords=["Stakoverløb (Stack Overflow):", "Stakunderløb (Stack Underflow):", "Stakken og SREG:", "PUSH Rr"])