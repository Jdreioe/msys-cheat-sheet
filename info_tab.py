import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango

class InfoTab(Gtk.ScrolledWindow):
    """
    GTK4 tab providing information on ATMega2560 timer interrupts,
    reading settings, and configuring different timer modes,
    formatted using Gtk.TextBuffer and tags.
    """
    def __init__(self):
        super().__init__()
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC) # Show scrollbars as needed

        # Use a Gtk.TextView for rich text formatting with tags
        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(False)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.text_buffer = self.text_view.get_buffer()

        # Define tags for formatting
        self.bold_tag = self.text_buffer.create_tag("bold", weight=Pango.Weight.BOLD)
        self.large_bold_tag = self.text_buffer.create_tag("large_bold", weight=Pango.Weight.BOLD, size_points=24) # Larger title, e.g., 24 points
        self.monospace_tag = self.text_buffer.create_tag("monospace", family="monospace")
        self.heading_tag = self.text_buffer.create_tag("heading", weight=Pango.Weight.BOLD, size_points=14) # For sub-headings, e.g., 14 points
        self.sub_heading_tag = self.text_buffer.create_tag("sub_heading", weight=Pango.Weight.BOLD) # For smaller sub-headings like "A. Normal Mode"

        self.set_child(self.text_view) # Set the TextView as the child of the ScrolledWindow

        # Populate the text view
        self._populate_info_content()

    def append_text_with_tags(self, text_segment, bold_keywords=[], monospace_segments=[], is_heading=False, is_sub_heading=False, is_main_title=False):
        start_iter = self.text_buffer.get_end_iter()
        self.text_buffer.insert(start_iter, text_segment)
        end_iter = self.text_buffer.get_end_iter()

        if is_main_title:
            self.text_buffer.apply_tag(self.large_bold_tag, start_iter, end_iter)
        elif is_heading:
            self.text_buffer.apply_tag(self.heading_tag, start_iter, end_iter)
        elif is_sub_heading:
            self.text_buffer.apply_tag(self.sub_heading_tag, start_iter, end_iter)

        # Apply bolding to keywords within the segment
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
        
        # Apply monospace to specific segments
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
        
        # Add padding/newline after each segment for better readability, unless it's a code block
        # This check might need refinement if your monospace_segments can also contain non-code text
        # For simplicity, if *any* segment starts and ends with '`' (like markdown code), we avoid the newline
        if not any(s.strip().startswith("`") and s.strip().endswith("`") for s in monospace_segments):
             self.text_buffer.insert(self.text_buffer.get_end_iter(), "\n")


    def _populate_info_content(self):
        # Clear existing content
        self.text_buffer.set_text("")

        self.append_text_with_tags(
            "Information om Timere på ATMega2560\n\n",
            is_main_title=True
        )
        self.append_text_with_tags(
            "---",
            monospace_segments=["---"]
        )
        self.append_text_with_tags("\n")


        self.append_text_with_tags(
            "1. Aktivering af Interrupts i Timere\n",
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
        self.text_buffer.insert(self.text_buffer.get_end_iter(), "\n") # Extra newline for spacing
        self.append_text_with_tags(
            "---",
            monospace_segments=["---"]
        )
        self.append_text_with_tags("\n")

        self.append_text_with_tags(
            "2. Aflæsning af Timerindstillinger\n",
            is_heading=True
        )
        self.append_text_with_tags(
            "For at aflæse en timers nuværende indstillinger skal du læse indholdet af dens kontrol- og tællerregistre.\n\n"
            "Vigtigste Registre at Aflæse:\n",
            bold_keywords=["Vigtigste Registre at Aflæse"]
        )
        self.append_text_with_tags(
            "* TCCRxA, TCCRxB, TCCRxC: Timer/Counter Control Register. Indeholder Waveform Generation Mode (WGM) bits, Compare Output Mode (COM) bits og Clock Select (CS) bits (prescaler).\n"
            "* TCNTx: Timer/Counter Register. Den aktuelle tællerstand.\n"
            "* OCRxA, OCRxB, OCRxC: Output Compare Register. Bruges til at sætte en sammenligningsværdi for Output Compare Match interrupts og PWM-cyklus.\n"
            "* ICRx: Input Capture Register (kun 16-bit timere). Bruges til at gemme tællerstanden ved et Input Capture Event.\n"
            "* TIMSKx: Timer Interrupt Mask Register. Viser hvilke interrupts der er aktiveret for timeren.\n"
            "* TIFRx: Timer Interrupt Flag Register. Indeholder flag, der sættes, når et interrupt udløses. Disse skal ofte cleares manuelt (ved at skrive en 1 til flag-biten).\n\n"
            "Eksempel (Aflæsning af Timer1):\n",
            bold_keywords=["TCCRxA", "TCCRxB", "TCCRxC", "Timer/Counter Control Register", "Waveform Generation Mode", "WGM", "Compare Output Mode", "COM", "Clock Select", "CS", "prescaler", "TCNTx", "Timer/Counter Register", "OCRxA", "OCRxB", "OCRxC", "Output Compare Register", "ICRx", "Input Capture Register", "TIMSKx", "Timer Interrupt Mask Register", "TIFRx", "Timer Interrupt Flag Register", "Eksempel (Aflæsning af Timer1)"]
        )
        self.append_text_with_tags(
            "`unsigned char tccr1a_val = TCCR1A;`\n"
            "`unsigned char tccr1b_val = TCCR1B;`\n"
            "`unsigned int tcnt1_val = TCNT1;   // Læs LAV så HØJ for 16-bit`\n"
            "`unsigned int ocr1a_val = OCR1A;`\n"
            "`unsigned int icr1_val = ICR1;`\n"
            "`unsigned char timsk1_val = TIMSK1;`\n"
            "`unsigned char tifr1_val = TIFR1;`\n\n",
            monospace_segments=["`unsigned char tccr1a_val = TCCR1A;`", "`unsigned char tccr1b_val = TCCR1B;`", "`unsigned int tcnt1_val = TCNT1;`", "`unsigned int ocr1a_val = OCR1A;`", "`unsigned int icr1_val = ICR1;`", "`unsigned char timsk1_val = TIMSK1;`", "`unsigned char tifr1_val = TIFR1;`"]
        )
        self.append_text_with_tags(
            "Bemærk: For 16-bit timere (Timer1, Timer3, Timer4, Timer5) skal du læse TCNTx, OCRx og ICRx på en specifik måde for at undgå datakorruption, da registrene er to 8-bit registre, der aflæses som ét 16-bit ord. Det anbefales at læse LAV-byte først og derefter HØJ-byte, eller bruge de indbyggede C-makroer hvis tilgængelige.\n",
            bold_keywords=["Bemærk", "Timer1", "Timer3", "Timer4", "Timer5", "TCNTx", "OCRx", "ICRx", "datakorruption", "LAV-byte", "HØJ-byte"]
        )
        self.text_buffer.insert(self.text_buffer.get_end_iter(), "\n") # Extra newline for spacing
        self.append_text_with_tags(
            "---",
            monospace_segments=["---"]
        )
        self.append_text_with_tags("\n")

        self.append_text_with_tags(
            "3. Konfiguration af Timer Tilstande (WGM)\n",
            is_heading=True
        )
        self.append_text_with_tags(
            "Waveform Generation Mode (WGM) bits bestemmer timerens funktionalitet (Normal, CTC, PWM, Fast PWM, Phase Correct PWM). Disse bits findes i TCCRxA og TCCRxB registre.\n\n"
            "Generel Struktur af WGM Bits:\n",
            bold_keywords=["Waveform Generation Mode (WGM)", "Normal", "CTC", "PWM", "Fast PWM", "Phase Correct PWM", "TCCRxA", "TCCRxB", "Generel Struktur af WGM Bits"]
        )
        self.append_text_with_tags(
            "* Timer0/Timer2 (8-bit): WGMx2 (TCCRxB), WGMx1, WGMx0 (TCCRxA)\n"
            "* Timer1 (16-bit): WGMx3, WGMx2 (TCCRxB), WGMx1, WGMx0 (TCCRxA)\n\n"
            "Fremgangsmåde:\n",
            bold_keywords=["Timer0", "Timer2", "Timer1", "WGMx2", "WGMx1", "WGMx0", "WGMx3", "TCCRxB", "TCCRxA", "Fremgangsmåde"]
        )
        self.append_text_with_tags(
            "1. Sæt WGM-bits: Se databladet for de specifikke bitkombinationer for hver tilstand. Vores 'constants.py' fil indeholder også disse informationer.\n"
            "2. Sæt Prescaler: Vælg en prescaler via Clock Select (CS) bits i TCCRxB for at styre timerens hastighed.\n"
            "3. Sæt TOP-værdi (hvis relevant): I CTC og PWM tilstande skal en TOP-værdi defineres. Dette kan være et fast tal (f.eks. 0xFF for 8-bit timere), OCRxA/ICRx, eller programmeres via TCNTx.\n\n",
            bold_keywords=["Sæt WGM-bits", "Sæt Prescaler", "Clock Select (CS)", "TCCRxB", "Sæt TOP-værdi", "CTC", "PWM", "OCRxA/ICRx", "TCNTx"]
        )

        # Mode A: Normal Mode
        self.append_text_with_tags(
            "A. Normal Mode:\n",
            is_sub_heading=True
        )
        self.append_text_with_tags(
            "* Tæller fra 0 til MAX (`0xFF` for 8-bit, `0xFFFF` for 16-bit) og starter forfra.\n"
            "* WGM-bits: `0b000` (alle 0).\n"
            "* Frekvens (Overflow): `F_CPU / (Prescaler * (MAX_VALUE + 1))`\n",
            bold_keywords=["MAX", "0xFF", "0xFFFF", "Frekvens (Overflow)"],
            monospace_segments=["`0b000`", "`F_CPU / (Prescaler * (MAX_VALUE + 1))`"]
        )
        self.append_text_with_tags(
            "Eksempel (Timer0 Normal Mode):\n",
            bold_keywords=["Eksempel (Timer0 Normal Mode)"]
        )
        self.append_text_with_tags(
            "`TCCR0A = 0x00; // WGM01=0, WGM00=0`\n"
            "`TCCR0B = 0x00; // WGM02=0`\n"
            "`// Optional: TCNT0 = 0; // Nulstil tæller`\n"
            "`// Indstil prescaler, f.eks. clk/1024 (CS02=1, CS01=0, CS00=1 -> 0b101)`\n"
            "`TCCR0B |= (1 << CS02) | (1 << CS00);`\n\n",
            monospace_segments=[
                "`TCCR0A = 0x00; // WGM01=0, WGM00=0`",
                "`TCCR0B = 0x00; // WGM02=0`",
                "`// Optional: TCNT0 = 0; // Nulstil tæller`",
                "`// Indstil prescaler, f.eks. clk/1024 (CS02=1, CS01=0, CS00=1 -> 0b101)`",
                "`TCCR0B |= (1 << CS02) | (1 << CS00);`"
            ]
        )

        # Mode B: CTC Mode
        self.append_text_with_tags(
            "B. CTC Mode (Clear Timer on Compare Match):\n",
            is_sub_heading=True
        )
        self.append_text_with_tags(
            "* Tæller fra 0 til en defineret TOP-værdi (f.eks. OCRxA), hvorefter den nulstilles.\n"
            "* Frekvens (OCF-flag/toggle): `F_CPU / (2 * Prescaler * (TOP + 1))`\n"
            "* WGM-bits: `0b010` (WGMx2=0, WGMx1=1, WGMx0=0)\n",
            bold_keywords=["TOP-værdi", "OCRxA", "Frekvens (OCF-flag/toggle)"],
            monospace_segments=["`F_CPU / (2 * Prescaler * (TOP + 1))`", "`0b010`"]
        )
        self.append_text_with_tags(
            "Eksempel (Timer0 CTC Mode, TOP=OCR0A):\n",
            bold_keywords=["Eksempel (Timer0 CTC Mode, TOP=OCR0A)"]
        )
        self.append_text_with_tags(
            "`TCCR0A = (1 << WGM01); // WGM01=1, WGM00=0`\n"
            "`TCCR0B = 0x00;         // WGM02=0`\n"
            "`OCR0A = 124;           // Sæt TOP-værdi for 1ms med 16MHz/1024`\n"
            "`// Indstil prescaler, f.eks. clk/1024`\n"
            "`TCCR0B |= (1 << CS02) | (1 << CS00);`\n"
            "`// Aktiver interrupt (valgfrit)`\n"
            "`TIMSK0 |= (1 << OCIE0A);`\n\n",
            monospace_segments=[
                "`TCCR0A = (1 << WGM01); // WGM01=1, WGM00=0`",
                "`TCCR0B = 0x00;         // WGM02=0`",
                "`OCR0A = 124;           // Sæt TOP-værdi for 1ms med 16MHz/1024`",
                "`// Indstil prescaler, f.eks. clk/1024`",
                "`TCCR0B |= (1 << CS02) | (1 << CS00);`",
                "`// Aktiver interrupt (valgfrit)`",
                "`TIMSK0 |= (1 << OCIE0A);`"
            ]
        )

        # Mode C: Fast PWM Mode
        self.append_text_with_tags(
            "C. Fast PWM Mode:\n",
            is_sub_heading=True
        )
        self.append_text_with_tags(
            "* Tæller fra 0 til TOP (`0xFF` for 8-bit, eller OCRx/ICRx for 16-bit), tæller hurtigt op.\n"
            "* Duty Cycle styres af OCRxB (eller OCRxA for Timer0/2).\n"
            "* Frekvens: `F_CPU / (Prescaler * (TOP + 1))`\n"
            "* WGM-bits for Timer0/2: `0b011` (WGMx2=0, WGMx1=1, WGMx0=1)\n"
            "* WGM-bits for Timer1 (TOP=0x03FF): `0b0111` (WGM13=0, WGM12=1, WGM11=1, WGM10=1)\n",
            bold_keywords=["TOP", "0xFF", "OCRx/ICRx", "Duty Cycle", "OCRxB", "OCRxA", "Frekvens"],
            monospace_segments=[
                "`F_CPU / (Prescaler * (TOP + 1))`", "`0b011`",
                "`0b0111`"
            ]
        )
        self.append_text_with_tags(
            "Eksempel (Timer0 Fast PWM, Non-Inverting på OC0A):\n",
            bold_keywords=["Eksempel (Timer0 Fast PWM, Non-Inverting på OC0A)"]
        )
        self.append_text_with_tags(
            "`TCCR0A = (1 << COM0A1) | (1 << WGM01) | (1 << WGM00); // Non-inv, WGM01=1, WGM00=1`\n"
            "`TCCR0B = 0x00; // WGM02=0`\n"
            "`OCR0A = 127;   // 50% duty cycle (127/255)`\n"
            "`// Indstil prescaler, f.eks. clk/64`\n"
            "`TCCR0B |= (1 << CS01) | (1 << CS00);`\n"
            "`// DDRD |= (1 << PD6); // Sæt OC0A (PD6) som output`\n\n",
            monospace_segments=[
                "`TCCR0A = (1 << COM0A1) | (1 << WGM01) | (1 << WGM00);`",
                "`TCCR0B = 0x00; // WGM02=0`",
                "`OCR0A = 127;   // 50% duty cycle (127/255)`",
                "`// Indstil prescaler, f.eks. clk/64`",
                "`TCCR0B |= (1 << CS01) | (1 << CS00);`",
                "`// DDRD |= (1 << PD6); // Sæt OC0A (PD6) som output`"
            ]
        )

        # Mode D: Phase Correct PWM Mode
        self.append_text_with_tags(
            "D. Phase Correct PWM Mode:\n",
            is_sub_heading=True
        )
        self.append_text_with_tags(
            "* Tæller fra 0 til TOP, derefter ned til 0. Symmetrisk bølgeform.\n"
            "* Frekvens: `F_CPU / (2 * Prescaler * TOP)` (Bemærk: TOP, ikke TOP+1)\n"
            "* WGM-bits for Timer0/2: `0b001` (WGMx2=0, WGMx1=0, WGMx0=1)\n"
            "* WGM-bits for Timer1 (TOP=0x03FF): `0b0011` (WGM13=0, WGM12=0, WGM11=1, WGM10=1)\n",
            bold_keywords=["TOP", "Frekvens", "Bemærk"],
            monospace_segments=[
                "`F_CPU / (2 * Prescaler * TOP)`", "`0b001`",
                "`0b0011`"
            ]
        )
        self.append_text_with_tags(
            "Eksempel (Timer0 Phase Correct PWM, Non-Inverting på OC0B):\n",
            bold_keywords=["Eksempel (Timer0 Phase Correct PWM, Non-Inverting på OC0B)"]
        )
        self.append_text_with_tags(
            "`TCCR0A = (1 << COM0B1) | (1 << WGM00); // Non-inv, WGM00=1, WGM01=0`\n"
            "`TCCR0B = 0x00; // WGM02=0`\n"
            "`OCR0B = 63;   // 25% duty cycle (63/255)`\n"
            "`// Indstil prescaler, f.eks. clk/8`\n"
            "`TCCR0B |= (1 << CS01);`\n"
            "`// DDRD |= (1 << PD5); // Sæt OC0B (PD5) som output`\n\n",
            monospace_segments=[
                "`TCCR0A = (1 << COM0B1) | (1 << WGM00);`",
                "`TCCR0B = 0x00; // WGM02=0`",
                "`OCR0B = 63;   // 25% duty cycle (63/255)`",
                "`// Indstil prescaler, f.eks. clk/8`",
                "`TCCR0B |= (1 << CS01);`",
                "`// DDRD |= (1 << PD5); // Sæt OC0B (PD5) som output`"
            ]
        )
        self.text_buffer.insert(self.text_buffer.get_end_iter(), "\n") # Extra newline for spacing
        self.append_text_with_tags(
            "---",
            monospace_segments=["---"]
        )
        self.append_text_with_tags("\n")

        self.append_text_with_tags(
            "4. Hvordan man Sætter Bits i Timere (f.eks. WGM, CS)\n",
            is_heading=True
        )
        self.append_text_with_tags(
            "Registerkonfiguration i AVR er primært baseret på bitmanipulation.\n"
            "Du bruger bitvise operatorer til at sætte, cleare eller læse individuelle bits uden at påvirke andre bits i registret.\n\n"
            "Generelle Bitvise Operatorer:\n",
            bold_keywords=["bitmanipulation", "bitvise operatorer", "Generelle Bitvise Operatorer"]
        )
        self.append_text_with_tags(
            "* Sæt en bit: `REGISTER |= (1 << BIT_NUMMER);`\n"
            "  * Eksempel: `TCCR0A |= (1 << WGM01);` (Sætter WGM01-biten i TCCR0A)\n",
            bold_keywords=["Sæt en bit", "Eksempel"],
            monospace_segments=["`REGISTER |= (1 << BIT_NUMMER);`", "`TCCR0A |= (1 << WGM01);`"]
        )
        
        # New section about binary alternative
        self.append_text_with_tags(
            "* Binær alternativ til at sætte specifikke bits:\n"
            "  I stedet for at bruge bit-shift (`1 << BIT_NUMMER`), kan du direkte skrive den binære værdi til registret, hvis du ønsker at sætte alle bits på én gang eller et kendt mønster.\n"
            "  Dette er ofte mindre fleksibelt, hvis du kun vil ændre en enkelt bit uden at påvirke andre, men kan være klarere for komplette registerindstillinger.\n"
            "  * Eksempel (sæt TOIE0 i TIMSK0, hvor TOIE0 er bit 0):\n"
            "    `TIMSK0 = 0b00000001; // Sætter kun TOIE0 (bit 0) og cleares alle andre.`\n"
            "    `// Eller hvis du vil bevare andre bits og kun sætte TOIE0:`\n"
            "    `TIMSK0 = TIMSK0 | 0b00000001;`\n"
            "    `// Dette svarer til TIMSK0 |= (1 << TOIE0); hvis TOIE0 er 0.`\n"
            "  * Eksempel (sæt prescaler til clk/64, WGM01=1, WGM00=1 for Fast PWM i TCCR0A):\n"
            "    `TCCR0A = 0b01000011; // COM0A1=1, WGM01=1, WGM00=1 for Fast PWM på OC0A`\n"
            "    `TCCR0B = 0b00000011; // CS01=1, CS00=1 for clk/64 prescaler`\n\n",
            bold_keywords=["Binær alternativ", "bit-shift", "binære værdi", "komplette registerindstillinger", "Eksempel"],
            monospace_segments=[
                "`TIMSK0 = 0b00000001;`", "`// Sætter kun TOIE0 (bit 0) og cleares alle andre.`",
                "`TIMSK0 = TIMSK0 | 0b00000001;`", "`// Dette svarer til TIMSK0 |= (1 << TOIE0); hvis TOIE0 er 0.`",
                "`TCCR0A = 0b01000011;`", "`TCCR0B = 0b00000011;`"
            ]
        )
        
        self.append_text_with_tags(
            "* Clear en bit: `REGISTER &= ~(1 << BIT_NUMMER);`\n"
            "  * Eksempel: `TCCR0B &= ~(1 << WGM02);` (Cleares WGM02-biten i TCCR0B)\n",
            bold_keywords=["Clear en bit", "Eksempel"],
            monospace_segments=["`REGISTER &= ~(1 << BIT_NUMMER);`", "`TCCR0B &= ~(1 << WGM02);`"]
        )
        self.append_text_with_tags(
            "* Clear flere bits (f.eks. prescaler): `REGISTER &= ~((1 << BIT0) | (1 << BIT1) | ...);`\n"
            "  * Eksempel (clear CS02, CS01, CS00): `TCCR0B &= ~((1 << CS02) | (1 << CS01) | (1 << CS00));`\n",
            bold_keywords=["Clear flere bits", "prescaler", "Eksempel"],
            monospace_segments=["`REGISTER &= ~((1 << BIT0) | (1 << BIT1) | ...);`", "`TCCR0B &= ~((1 << CS02) | (1 << CS01) | (1 << CS00));`"]
        )
        self.append_text_with_tags(
            "* Sæt flere bits (prescaler): Først clear, så sæt de nye bits.\n"
            "  * Eksempel (sæt til clk/64):\n",
            bold_keywords=["Sæt flere bits", "prescaler", "Eksempel"]
        )
        self.append_text_with_tags(
            "    `TCCR0B &= ~((1 << CS02) | (1 << CS01) | (1 << CS00)); // Clear eksisterende prescaler bits`\n"
            "    `TCCR0B |= (1 << CS01) | (1 << CS00);                   // Sæt nye bits for clk/64 (0b011)`\n\n",
            monospace_segments=[
                "`TCCR0B &= ~((1 << CS02) | (1 << CS01) | (1 << CS00)); // Clear eksisterende prescaler bits`",
                "`TCCR0B |= (1 << CS01) | (1 << CS00);                   // Sæt nye bits for clk/64 (0b011)`"
            ]
        )
        self.append_text_with_tags(
            "Vigtige Bit Grupper:\n",
            bold_keywords=["Vigtige Bit Grupper"]
        )
        self.append_text_with_tags(
            "* WGM bits: Styrer Waveform Generation Mode (WGMx0, WGMx1, WGMx2, WGMx3).\n"
            "* COM bits (Compare Output Mode): Styrer output på OCx pins (COMx1, COMx0). Bruges i PWM tilstande.\n"
            "* CS bits (Clock Select): Styrer prescaler og timer start/stop (CSx2, CSx1, CSx0).\n",
            bold_keywords=["WGM bits", "Waveform Generation Mode", "WGMx0", "WGMx1", "WGMx2", "WGMx3", "COM bits (Compare Output Mode)", "OCx", "COMx1", "COMx0", "PWM", "CS bits (Clock Select)", "CSx2", "CSx1", "CSx0"]
        )