import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango

# Make NumberSystemsTab inherit from Gtk.Box
class NumberSystemsTab(Gtk.Box):
    def __init__(self): # Remove notebook and tab_title from __init__ as it will be the child itself
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)

        # We will no longer append_page here; the calling code will append *this instance*
        self._create_widgets()

    def _create_widgets(self):
        # GTK Labels support Pango markup for basic formatting, but for a
        # full text view with multiple styles, Gtk.TextView is better.
        title_label = Gtk.Label()
        title_label.set_markup("<span font_desc='Arial Bold 16'>Talsystemer i Digital Elektronik</span>")
        title_label.set_halign(Gtk.Align.CENTER) # Center the title
        self.append(title_label) # Add to *this* Gtk.Box (self)

        # For scrolled text, we use Gtk.TextView inside a Gtk.ScrolledWindow
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(False)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        # Margins are now set on the main Gtk.Box (self) so removed from here
        
        self.text_buffer = self.text_view.get_buffer()

        # Define Gtk.TextTag objects for formatting
        self.bold_tag = self.text_buffer.create_tag("bold", weight=Pango.Weight.BOLD)
        self.monospace_tag = self.text_buffer.create_tag("monospace", family="monospace")
        self.formula_tag = self.text_buffer.create_tag("formula", weight=Pango.Weight.BOLD, size_points=11)
        self.table_header_tag = self.text_buffer.create_tag("table_header", weight=Pango.Weight.BOLD)

        self.scrolled_window.set_child(self.text_view)
        self.append(self.scrolled_window) # Add the scrolled window to *this* Gtk.Box (self)

        self._populate_info_content()

    def _populate_info_content(self):
        # Clear existing content
        self.text_buffer.set_text("")

        # Helper to append text with tags
        def append_formatted_text(text_segment, bold_keywords=[], monospace_segments=[], formula_segments=[]):
            start_iter = self.text_buffer.get_end_iter()
            self.text_buffer.insert(start_iter, text_segment)
            end_iter = self.text_buffer.get_end_iter()

            # Apply bolding
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

            # Apply monospace
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
            
            # Apply formula styling
            for formula_segment in formula_segments:
                search_start_iter = self.text_buffer.get_iter_at_offset(start_iter.get_offset())
                while True:
                    found_tuple = search_start_iter.forward_search(formula_segment, 0, end_iter)
                    if found_tuple:
                        found, match_start, match_end = found_tuple
                        if found and match_start.get_offset() < end_iter.get_offset():
                            self.text_buffer.apply_tag(self.formula_tag, match_start, match_end)
                            search_start_iter = match_end.copy()
                        else:
                            break
                    else:
                        break
            
            # Add a newline after each segment for better readability
            self.text_buffer.insert(self.text_buffer.get_end_iter(), "\n")

        # --- Content for Unsigned ---
        start_iter = self.text_buffer.get_end_iter()
        self.text_buffer.insert(start_iter, "1. Usigned (Unsigned Integer)\n")
        end_iter = self.text_buffer.get_end_iter()
        self.text_buffer.apply_tag(self.bold_tag, start_iter, end_iter)
        
        append_formatted_text(
            "* Beskrivelse: Repræsenterer kun ikke-negative heltal (fra 0 og op). Alle bits bruges til at repræsentere værdien.",
            bold_keywords=["Beskrivelse"]
        )
        append_formatted_text(
            "* Eksempel (8-bit):",
            bold_keywords=["Eksempel (8-bit)"]
        )
        append_formatted_text(
            "    * Binary: `00000000` = 0",
            monospace_segments=["`00000000`"]
        )
        append_formatted_text(
            "    * Binary: `11111111` = 255",
            monospace_segments=["`11111111`"]
        )
        append_formatted_text(
            "* Range (N bits): 0 to 2^N - 1",
            bold_keywords=["Range (N bits)"],
            formula_segments=["2^N - 1"]
        )
        append_formatted_text(
            "* Anvendelse: Tællere, adresseværdier, og andre situationer hvor negative tal ikke er relevante.",
            bold_keywords=["Anvendelse"]
        )
        self.text_buffer.insert(self.text_buffer.get_end_iter(), "\n") # Extra newline for spacing

        # --- Content for Signed Magnitude ---
        start_iter = self.text_buffer.get_end_iter()
        self.text_buffer.insert(start_iter, "2. Signed Magnitude (Fortegns-magnitude)\n")
        end_iter = self.text_buffer.get_end_iter()
        self.text_buffer.apply_tag(self.bold_tag, start_iter, end_iter)

        append_formatted_text(
            "* Beskrivelse: Den mest venstre bit (Most Significant Bit, MSB) bruges som fortegnsbit (0 for positiv, 1 for negativ). De resterende bits repræsenterer tallets absolutte værdi (magnitude).",
            bold_keywords=["Beskrivelse", "Most Significant Bit", "MSB", "fortegnsbit", "absolutte værdi", "magnitude"]
        )
        append_formatted_text(
            "* Eksempel (8-bit):",
            bold_keywords=["Eksempel (8-bit)"]
        )
        append_formatted_text(
            "    * Binary: `00000001` = +1",
            monospace_segments=["`00000001`"]
        )
        append_formatted_text(
            "    * Binary: `10000001` = -1",
            monospace_segments=["`10000001`"]
        )
        append_formatted_text(
            "    * Ulemper: Har to repræsentationer for nul (`00000000` og `10000000`). Komplicerer addition/subtraktion.",
            bold_keywords=["Ulemper"],
            monospace_segments=["`00000000`", "`10000000`"]
        )
        append_formatted_text(
            "* Range (N bits): -(2^(N-1) - 1) to 2^(N-1) - 1",
            bold_keywords=["Range (N bits)"],
            formula_segments=["-(2^(N-1) - 1)", "2^(N-1) - 1"]
        )
        self.text_buffer.insert(self.text_buffer.get_end_iter(), "\n")

        # --- Content for 1's Complement ---
        start_iter = self.text_buffer.get_end_iter()
        self.text_buffer.insert(start_iter, "3. 1's Complement (1-Komplement)\n")
        end_iter = self.text_buffer.get_end_iter()
        self.text_buffer.apply_tag(self.bold_tag, start_iter, end_iter)

        append_formatted_text(
            "* Beskrivelse: Positive tal repræsenteres som i usigned. Negative tal dannes ved at invertere alle bits (0 bliver 1, 1 bliver 0) af det tilsvarende positive tal.",
            bold_keywords=["Beskrivelse", "invertere alle bits"]
        )
        append_formatted_text(
            "* Eksempel (8-bit):",
            bold_keywords=["Eksempel (8-bit)"]
        )
        append_formatted_text(
            "    * Binary: `00000001` = +1",
            monospace_segments=["`00000001`"]
        )
        append_formatted_text(
            "    * For -1: Tag +1 (`00000001`), inverter alle bits -> `11111110`",
            monospace_segments=["`00000001`", "`11111110`"]
        )
        append_formatted_text(
            "    * Ulemper: Har også to repræsentationer for nul (`00000000` og `11111111`). Kræver \"end-around carry\" ved addition.",
            bold_keywords=["Ulemper", "end-around carry"],
            monospace_segments=["`00000000`", "`11111111`"]
        )
        append_formatted_text(
            "* Range (N bits): -(2^(N-1) - 1) to 2^(N-1) - 1",
            bold_keywords=["Range (N bits)"],
            formula_segments=["-(2^(N-1) - 1)", "2^(N-1) - 1"]
        )
        self.text_buffer.insert(self.text_buffer.get_end_iter(), "\n")

        # --- Content for 2's Complement ---
        start_iter = self.text_buffer.get_end_iter()
        self.text_buffer.insert(start_iter, "4. 2's Complement (2-Komplement)\n")
        end_iter = self.text_buffer.get_end_iter()
        self.text_buffer.apply_tag(self.bold_tag, start_iter, end_iter)

        append_formatted_text(
            "* Beskrivelse: Den mest udbredte metode til repræsentation af fortegnsbestemte heltal i computere. Positive tal er som usigned. Negative tal dannes ved at tage 1's komplement og derefter lægge 1 til.",
            bold_keywords=["Beskrivelse", "1's komplement"]
        )
        append_formatted_text(
            "* Fordele: Har kun én repræsentation for nul. Addition og subtraktion udføres ved standard binær addition, hvilket forenkler hardware.",
            bold_keywords=["Fordele"]
        )
        append_formatted_text(
            "* Eksempel (8-bit):",
            bold_keywords=["Eksempel (8-bit)"]
        )
        append_formatted_text(
            "    * Binary: `00000001` = +1",
            monospace_segments=["`00000001`"]
        )
        append_formatted_text(
            "    * For -1:",
        )
        append_formatted_text(
            "        1. Start med +1: `00000001`",
            monospace_segments=["`00000001`"]
        )
        append_formatted_text(
            "        2. Inverter (1's complement): `11111110`",
            monospace_segments=["`11111110`"]
        )
        append_formatted_text(
            "        3. Læg 1 til: `11111110 + 1 = 11111111`",
            monospace_segments=["`11111110 + 1 = 11111111`"]
        )
        append_formatted_text(
            "    * `11111111` = -1",
            monospace_segments=["`11111111`"]
        )
        append_formatted_text(
            "    * `10000000` = -128 (for 8-bit) - dette er det mest negative tal.",
            monospace_segments=["`10000000`"]
        )
        append_formatted_text(
            "* Range (N bits): -2^(N-1) to 2^(N-1) - 1",
            bold_keywords=["Range (N bits)"],
            formula_segments=["-2^(N-1)", "2^(N-1) - 1"]
        )
        self.text_buffer.insert(self.text_buffer.get_end_iter(), "\n")

        # --- Table Overview ---
        start_iter = self.text_buffer.get_end_iter()
        self.text_buffer.insert(start_iter, "Tabeloversigt (8-bit eksempel):\n")
        end_iter = self.text_buffer.get_end_iter()
        self.text_buffer.apply_tag(self.bold_tag, start_iter, end_iter)

        # For the table, we'll insert it row by row, applying tags manually.
        # This is more involved than in Tkinter but gives fine-grained control.
        # Headers
        headers = ["Decimal", "Usigned", "Signed Magnitude", "1's Complement", "2's Complement"]
        header_text = "| " + " | ".join(headers) + " |\n"
        # Apply table_header_tag (which is bold) to the headers
        start_iter = self.text_buffer.get_end_iter()
        self.text_buffer.insert(start_iter, header_text)
        end_iter = self.text_buffer.get_end_iter()
        self.text_buffer.apply_tag(self.table_header_tag, start_iter, end_iter)

        # Separator line for the table
        start_iter = self.text_buffer.get_end_iter()
        self.text_buffer.insert(start_iter, "|---------|---------|------------------|----------------|----------------|\n")
        end_iter = self.text_buffer.get_end_iter()
        self.text_buffer.apply_tag(self.monospace_tag, start_iter, end_iter)

        # Data rows
        data_rows = [
            ["0", "00000000", "00000000", "00000000", "00000000"],
            ["+1", "00000001", "00000001", "00000001", "00000001"],
            ["+127", "01111111", "01111111", "01111111", "01111111"],
            ["-1", "N/A", "10000001", "11111110", "11111111"],
            ["-127", "N/A", "11111111", "10000000", "10000001"],
            ["-128", "N/A", "N/A", "N/A", "10000000"],
            ["255", "11111111", "N/A", "N/A", "N/A"]
        ]

        for row in data_rows:
            row_text = "| " + " | ".join(row) + " |\n"
            start_iter = self.text_buffer.get_end_iter()
            self.text_buffer.insert(start_iter, row_text)
            end_iter = self.text_buffer.get_end_iter()
            self.text_buffer.apply_tag(self.monospace_tag, start_iter, end_iter)


        # Set text buffer to read-only after content is inserted
        self.text_view.set_editable(False)