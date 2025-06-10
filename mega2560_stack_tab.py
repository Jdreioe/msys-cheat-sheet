import tkinter as tk
from tkinter import ttk, scrolledtext

class Mega2560StackTab:
    def __init__(self, notebook, tab_title="Mega2560 Stack"):
        self.notebook = notebook
        self.tab_frame = ttk.Frame(notebook)
        notebook.add(self.tab_frame, text=tab_title)

        self._create_widgets()

    def _create_widgets(self):
        title_label = tk.Label(self.tab_frame, text="ATmega2560 Hardware Stack", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        info_text = scrolledtext.ScrolledText(self.tab_frame, wrap=tk.WORD, width=80, height=25, font=("Arial", 10))
        info_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        content = """
        ATmega2560 (og andre AVR-mikrocontrollere) bruger en hardware-implementeret stak til midlertidig lagring af data, især ved subrutinekald og afbrydelser. Stakken vokser nedad i hukommelsen (mod lavere adresser).

        **Hvad er Stakken?**
        * Et område i SRAM (Static RAM) der fungerer som et LIFO (Last-In, First-Out) lager.
        * Bruges til at gemme returadresser for subrutiner og afbrydelser, samt til at gemme midlertidige data (f.eks. registerværdier) under funktionseksekvering.

        **Stack Pointer (SP)**
        * En 16-bit register, der altid peger på den *næste ledige* adresse på stakken.
        * På ATmega2560 er SP en kombination af to 8-bit I/O-registre: `SPH` (Stack Pointer High) og `SPL` (Stack Pointer Low).
        * Initialiseres typisk til det højeste SRAM-adresse (end RAM). Eksempel: `LDI R16, HIGH(RAMEND); OUT SPH, R16; LDI R16, LOW(RAMEND); OUT SPL, R16;`

        **Stakoperationer:**

        1.  **PUSH (Læg på stakken)**
            * `PUSH Rr`: Indholdet af register `Rr` lægges på stakken.
            * **Sekvens:**
                1.  `SP` dekrementeres (`SP = SP - 1`).
                2.  Indholdet af `Rr` gemmes på den adresse, som `SP` nu peger på.
            * **Cycles:** 2 cycles

        2.  **POP (Tag fra stakken)**
            * `POP Rd`: Indholdet fra stakken tages og lægges i register `Rd`.
            * **Sekvens:**
                1.  Indholdet fra den adresse, som `SP` peger på, lægges i `Rd`.
                2.  `SP` inkrementeres (`SP = SP + 1`).
            * **Cycles:** 2 cycles

        **Subrutinekald og Afbrydelser:**

        * **`CALL k` (Kald subrutine):**
            * Lægger den 22-bit returadresse (PC + 1) på stakken (3 bytes).
            * Springer til adressen `k`.
            * `SP` dekrementeres med 3.
            * **Cycles:** 4 cycles

        * **`RCALL k` (Relativt kald subrutine):**
            * Lægger den 22-bit returadresse (PC + 1) på stakken (3 bytes).
            * Springer til PC + `k`.
            * `SP` dekrementeres med 3.
            * **Cycles:** 3 cycles

        * **`RET` (Return fra subrutine):**
            * Tager returadressen fra stakken.
            * `SP` inkrementeres med 3.
            * Spring til den hentede adresse.
            * **Cycles:** 4 cycles

        * **Afbrydelse (Interrupt):**
            * Automatisk PUSH af returadresse og Status Register (SREG).
            * Spring til afbrydelsesvektoren.

        * **`RETI` (Return fra afbrydelse):**
            * Automatisk POP af SREG og returadresse.
            * Spring til den hentede adresse.
            * **Cycles:** 4 cycles

        **Vigtige punkter:**
        * **Stakoverløb (Stack Overflow):** Hvis stakken vokser ud over det tildelte SRAM-område og kolliderer med andre variable, kan det forårsage uforudsigelig adfærd.
        * **Stakunderløb (Stack Underflow):** Hvis du popper mere data end du har pushet, kan du hente meningsløse værdier eller forsøge at læse fra ugyldige hukommelsesadresser.
        * **Stakken og SREG:** Ved afbrydelser pushes SREG automatisk for at bevare CPU-status. Ved normal subrutine brug skal du selv gemme SREG (PUSH Rr) hvis din subrutine ændrer statusflag.
        """
        info_text.insert(tk.END, content)
        info_text.config(state=tk.DISABLED)