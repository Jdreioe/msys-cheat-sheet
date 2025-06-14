import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango

class InterruptInfoTab(Gtk.ScrolledWindow):
    def __init__(self):
        super().__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(False)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.text_buffer = self.text_view.get_buffer()

        self.bold_tag = self.text_buffer.create_tag("bold", weight=Pango.Weight.BOLD)
        self.monospace_tag = self.text_buffer.create_tag("monospace", family="monospace")
        self.heading_tag = self.text_buffer.create_tag("heading", weight=Pango.Weight.BOLD, size_points=14)
        self.sub_heading_tag = self.text_buffer.create_tag("sub_heading", weight=Pango.Weight.BOLD)

        self.set_child(self.text_view)
        self._populate_content()

    def append_text_with_tags(self, text_segment, bold_keywords=[], monospace_segments=[], is_heading=False, is_sub_heading=False):
        start_iter = self.text_buffer.get_end_iter()
        self.text_buffer.insert(start_iter, text_segment)
        end_iter = self.text_buffer.get_end_iter()

        if is_heading:
            self.text_buffer.apply_tag(self.heading_tag, start_iter, end_iter)
        elif is_sub_heading:
            self.text_buffer.apply_tag(self.sub_heading_tag, start_iter, end_iter)

        for keyword in bold_keywords:
            search_start_iter = self.text_buffer.get_iter_at_offset(start_iter.get_offset())
            while True:
                found_tuple = search_start_iter.forward_search(keyword, 0, end_iter)
                if found_tuple:
                    found, match_start, match_end = found_tuple
                    if found and match_start.get_offset() < end_iter.get_offset():
                        self.text_buffer.apply_tag(self.bold_tag, match_start, match_end)
                        search_start_iter = match_end.copy()
                    else:
                        break
                else:
                    break

        for mono_segment in monospace_segments:
            search_start_iter = self.text_buffer.get_iter_at_offset(start_iter.get_offset())
            while True:
                found_tuple = search_start_iter.forward_search(mono_segment, 0, end_iter)
                if found_tuple:
                    found, match_start, match_end = found_tuple
                    if found and match_start.get_offset() < end_iter.get_offset():
                        self.text_buffer.apply_tag(self.monospace_tag, match_start, match_end)
                        search_start_iter = match_end.copy()
                    else:
                        break
                else:
                    break
        self.text_buffer.insert(self.text_buffer.get_end_iter(), "\n")

    def _populate_content(self):
        self.text_buffer.set_text("")
        self.append_text_with_tags(
            "Aktivering af Interrupts i Timere\n",
            is_heading=True
        )
        self.append_text_with_tags(
            "Interrupts er afgørende for at udføre kode asynkront, når en timer når en bestemt tilstand (f.eks. overflow eller match med en sammenligningsværdi).\n"
            "For ATMega2560 styrer man interrupts via TIMSKx (Timer Interrupt Mask Register) og EIMSK (External Interrupt Mask Register).\n\n"
            "Fremgangsmåde:\n",
            bold_keywords=["Interrupts", "TIMSKx", "Timer Interrupt Mask Register", "EIMSK", "External Interrupt Mask Register", "Fremgangsmåde"]
        )
        self.append_text_with_tags(
            "1. Aktiver Global Interrupts: Dette gøres ved at sætte I-bit (bit 7) i SREG (Status Register).\n"
            "   Dette er et generelt krav for alle interrupts.\n",
            bold_keywords=["I-bit", "SREG", "Status Register"]
        )
        self.append_text_with_tags(
            "   `sei(); // Sæt I-bit i SREG for at aktivere globale interrupts`\n\n",
            monospace_segments=["`sei(); // Sæt I-bit i SREG for at aktivere globale interrupts`"]
        )
        self.append_text_with_tags(
            "2. Aktiver specifikke Timer Interrupts i TIMSKx: Hver timer (Timer0, Timer1, Timer2, Timer3, Timer4, Timer5) har sit eget TIMSK-register.\n\n"
            "   Generelt:\n",
            bold_keywords=["Aktiver specifikke Timer Interrupts i TIMSKx", "Timer0", "Timer1", "Timer2", "Timer3", "Timer4", "Timer5", "TIMSK-register", "Generelt"]
        )
        self.append_text_with_tags(
            "* TOIEx: Timer Overflow Interrupt Enable. Aktiverer interrupt, når timeren løber over (TCNTx når MAX).\n"
            "* OCIExA: Output Compare Match A Interrupt Enable. Aktiverer interrupt, når TCNTx matcher OCRxA.\n"
            "* OCIExB: Output Compare Match B Interrupt Enable. (Kun på visse timere, f.eks. Timer0, Timer1, Timer3, Timer4, Timer5)\n"
            "* ICIEx: Input Capture Interrupt Enable. (Kun på Timer1, Timer3, Timer4, Timer5)\n\n"
            "   Eksempler:\n",
            bold_keywords=["TOIEx", "Timer Overflow Interrupt Enable", "TCNTx", "MAX", "OCIExA", "Output Compare Match A Interrupt Enable", "OCRxA", "OCIExB", "Output Compare Match B Interrupt Enable", "ICIEx", "Input Capture Interrupt Enable", "Eksempler"]
        )
        self.append_text_with_tags(
            "   * Timer0: 8-bit timer\n",
            bold_keywords=["Timer0"]
        )
        self.append_text_with_tags(
            "     `TIMSK0 |= (1 << TOIE0);   // Aktiver Timer0 Overflow Interrupt`\n"
            "     `TIMSK0 |= (1 << OCIE0A);  // Aktiver Timer0 Output Compare Match A Interrupt`\n"
            "     `TIMSK0 |= (1 << OCIE0B);  // Aktiver Timer0 Output Compare Match B Interrupt`\n\n",
            monospace_segments=["`TIMSK0 |= (1 << TOIE0);`", "`TIMSK0 |= (1 << OCIE0A);`", "`TIMSK0 |= (1 << OCIE0B);`"]
        )
        self.append_text_with_tags(
            "   * Timer1: 16-bit timer\n",
            bold_keywords=["Timer1"]
        )
        self.append_text_with_tags(
            "     `TIMSK1 |= (1 << TOIE1);   // Aktiver Timer1 Overflow Interrupt`\n"
            "     `TIMSK1 |= (1 << OCIE1A);  // Aktiver Timer1 Output Compare Match A Interrupt`\n"
            "     `TIMSK1 |= (1 << OCIE1B);  // Aktiver Timer1 Output Compare Match B Interrupt`\n"
            "     `TIMSK1 |= (1 << ICIE1);   // Aktiver Timer1 Input Capture Interrupt`\n\n",
            monospace_segments=["`TIMSK1 |= (1 << TOIE1);`", "`TIMSK1 |= (1 << OCIE1A);`", "`TIMSK1 |= (1 << OCIE1B);`", "`TIMSK1 |= (1 << ICIE1);`"]
        )
        self.append_text_with_tags(
            "   * Timer2: 8-bit timer med separat asynkron prescaler (f.eks. for real-time clock)\n",
            bold_keywords=["Timer2"]
        )
        self.append_text_with_tags(
            "     `TIMSK2 |= (1 << TOIE2);   // Aktiver Timer2 Overflow Interrupt`\n"
            "     `TIMSK2 |= (1 << OCIE2A);  // Aktiver Timer2 Output Compare Match A Interrupt`\n"
            "     `TIMSK2 |= (1 << OCIE2B);  // Aktiver Timer2 Output Compare Match B Interrupt`\n\n",
            monospace_segments=["`TIMSK2 |= (1 << TOIE2);`", "`TIMSK2 |= (1 << OCIE2A);`", "`TIMSK2 |= (1 << OCIE2B);`"]
        )
        self.append_text_with_tags(
            "3. Implementer Interrupt Service Routine (ISR): Du skal skrive en funktion, der kører, når interruptet udløses.\n"
            "   Brug de korrekte vektornavne.\n\n"
            "   Eksempler:\n",
            bold_keywords=["Implementer Interrupt Service Routine (ISR)", "Eksempler"]
        )
        self.append_text_with_tags(
            "   `// For Timer0 Overflow`\n"
            "   `ISR(TIMER0_OVF_vect) {`\n"
            "   `  // Din kode her`\n"
            "   `}`\n\n",
            monospace_segments=["`// For Timer0 Overflow`", "`ISR(TIMER0_OVF_vect) {`", "`  // Din kode her`", "`}`"]
        )
        self.append_text_with_tags(
            "   `// For Timer1 Output Compare Match A`\n"
            "   `ISR(TIMER1_COMPA_vect) {`\n"
            "   `  // Din kode her`\n"
            "   `}`\n\n",
            monospace_segments=["`// For Timer1 Output Compare Match A`", "`ISR(TIMER1_COMPA_vect) {`", "`  // Din kode her`", "`}`"]
        )
        self.append_text_with_tags(
            "   `// For Timer2 Compare Match B`\n"
            "   `ISR(TIMER2_COMPB_vect) {`\n"
            "   `  // Din kode her`\n"
            "   `}`\n\n",
            monospace_segments=["`// For Timer2 Compare Match B`", "`ISR(TIMER2_COMPB_vect) {`", "`  // Din kode her`", "`}`"]
        )