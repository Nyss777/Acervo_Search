import os
import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.effects.scroll import ScrollEffect
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.metrics import dp



# Ensure the working directory is the script’s directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from Search import search, registroSearch
from Parser import parse, parse_Registro_html

class ClickableLabel(ButtonBehavior, Label):
    pass

class CopyLabel(ButtonBehavior, Label):
    def on_press(self):
        slices = self.text.split('\n')
        if len(slices) == 10:
            Clipboard.copy(slices[-1].split()[-1])
        else:
            Clipboard.copy(slices[0].replace("[b]Título:[/b] ", ""))


class SearchScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        # Root layout
        root = BoxLayout(orientation='vertical', padding=20, spacing=30)

        # Row 1: “General Search:” label + TextInput
        row1 = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        row1.add_widget(Label(text="General Search:", size_hint_x=None, width='120dp'))
        self.general_input = TextInput(multiline=False)
        row1.add_widget(self.general_input)
        root.add_widget(row1)

        # Row 2: “How many results?” label + TextInput
        row2 = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        row2.add_widget(Label(text="How many results?", size_hint_x=None, width='120dp'))
        self.number_input = TextInput(multiline=False, input_filter='int')
        row2.add_widget(self.number_input)
        root.add_widget(row2)

        # Row 3: “Sorting:” label + Spinner
        row3 = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        row3.add_widget(Label(text="Sorting:", size_hint_x=None, width='120dp'))
        self.sort_spinner = Spinner(
            text="Descending",
            values=["Descending", "Ascending"],
            size_hint=(None, None),
            size=('150dp', '40dp')
        )
        row3.add_widget(self.sort_spinner)
        root.add_widget(row3)

        # Row 4: Search button
        self.search_button = Button(text="Search", size_hint_y=None, height='40dp')
        self.search_button.bind(on_release=self.on_search_button)
        root.add_widget(self.search_button)

        # Row 5: Table header
        header = GridLayout(cols=2, size_hint_y=None, height='30dp')
        header.add_widget(Label(text="Título", bold=True, size_hint_x=0.8))
        header.add_widget(Label(text="Data", bold=True, size_hint_x=0.2))
        root.add_widget(header)

        # Row 6: Scrollable area for results
        self.scrollview = ScrollView(effect_cls=ScrollEffect)
        self.results_grid = GridLayout(cols=2, spacing=5, size_hint_y=None)
        self.results_grid.bind(minimum_height=self.results_grid.setter('height'))
        self.scrollview.add_widget(self.results_grid)
        root.add_widget(self.scrollview)

        self.add_widget(root)

    def on_search_button(self, instance):
        query = self.general_input.text.strip()
        N_R = self.number_input.text.strip()

        # Validate query
        if not query:
            self.show_error("Please enter a search query.")
            return

        # Validate number of results
        if not N_R:
            N_R = 200

        N_R = int(N_R)

        if N_R <= 0 or N_R > 10000:
            self.show_error(f"Number of results must be between 1 and 10,000 (you entered {N_R}).")
            return

        sort_order = self.sort_spinner.text

        # Perform the search and parse
        try:
            raw_results = search(query, N_R, sort_order)
            results = parse(raw_results, sort_order)
        except Exception as e:
            self.show_error(f"An error occurred while searching:\n{e}")
            return

        if not results:
            self.show_error("No results found.")
            return

        # Populate the scrollable grid
        self.results_grid.clear_widgets()
        for title, date, element_id in results:
            lbl_title = ClickableLabel(
                text=title,
                size_hint_x=0.8,
                size_hint_y=None,
                height='30dp',
                halign='left',
                valign='middle',
                text_size=(None, None),
                shorten=True,
                shorten_from='right'
            )
            lbl_title.bind(
                width=lambda instance, value: setattr(instance, 'text_size', (value, None)),
                on_release=lambda instance, t=title,d=date,e=element_id: self.manager.get_screen('details').show_details(t, d, e)
            )
            lbl_date = Label(text=date, size_hint_y=None, size_hint_x=0.2, height='30dp')
            self.results_grid.add_widget(lbl_title)
            self.results_grid.add_widget(lbl_date)

    def show_error(self, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        btn = Button(text="OK", size_hint_y=None, height='40dp')
        content.add_widget(btn)
        popup = Popup(title="Error", content=content, size_hint=(None, None), size=('400dp', '200dp'))
        btn.bind(on_release=popup.dismiss)
        popup.open()

class DetailsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Label to show the main details (Title, Author, etc.)
        self.label = CopyLabel(text="", halign="left", valign="top", padding=(20, 20), markup=True)
        self.label.bind(size=self.label.setter("text_size"))
        
        # Back button
        btn_back = Button(text="X", bold=True, size_hint=(None, None), size=(dp(60), dp(40)))
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'search'))

        # Main layout for this screen
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(btn_back)
        self.layout.add_widget(self.label)
        self.add_widget(self.layout)
        
        # Placeholder for the scrollable table
        self.scrollview = None

    def _build_and_populate_table(self, elements):
        """
        This internal method builds the entire table, including the header and data rows,
        inside a single GridLayout to ensure perfect alignment.
        """
        # --- Define layout properties based on screen size ---
        ratios = [0.32, 0.09, 0.21, 0.21, 0.1, 0.07]
        min_widths_dp = [297, 48, 151, 151, 90, 63]
        min_widths_px = [dp(x) for x in min_widths_dp]
        headers = ["Localização", "Biblioteca", "Material", "Regulamento", "Disponível", "Total"]

        screen_w = Window.width
        total_min = sum(min_widths_px)

        # --- Create the single grid for both header and data ---
        grid_params = {'cols': 6, 'spacing': dp(2), 'size_hint_y': None}
        grid_params['size_hint_x'] = None
        grid_params['width'] = total_min

        results_grid = GridLayout(**grid_params)
        results_grid.bind(minimum_height=results_grid.setter('height'))

        # --- Populate Header Row ---
        for idx, text in enumerate(headers):
            label_params = {
                'text': text, 'bold': True, 'size_hint_y': None,
                'height': dp(40), 'halign': 'center', 'valign': 'middle'
            }
            label_params['size_hint_x'] = None
            label_params['width'] = min_widths_px[idx]

            header_label = Label(**label_params)
            header_label.bind(width=lambda l, w: setattr(l, 'text_size', (w, None)))
            results_grid.add_widget(header_label)

        # --- Populate Data Rows ---
        for row_data in elements[0]:
            for idx, value in enumerate(row_data):
                cell_params = {
                    'text': str(value), 'size_hint_y': None, 'halign': 'left',
                    'valign': 'middle', 'padding': (dp(10),0)
                }
                cell_params['size_hint_x'] = None
                cell_params['width'] = min_widths_px[idx]

                cell_label = Label(**cell_params)
                # Enable text wrapping and dynamic height adjustment
                cell_label.bind(width=lambda l, w: setattr(l, 'text_size', (w, None)))
                cell_label.bind(texture_size=lambda l, ts: setattr(l, 'height', ts[1] + dp(10)))
                results_grid.add_widget(cell_label)

        # --- Setup ScrollView to contain the grid ---
        self.scrollview = ScrollView(
            do_scroll_x=True, do_scroll_y=True,
            size_hint=(1, 1), effect_cls=ScrollEffect
        )
        self.scrollview.add_widget(results_grid)
        self.layout.add_widget(self.scrollview)

    def show_details(self, title, date, element_id):
        self.manager.current = 'details'
        
        # --- Fetch and parse data ---
        try:
            response = registroSearch(element_id)
            elements = parse_Registro_html(response)
            autor = elements[1] if len(elements) > 1 else "N/A"
            href_a = elements[2] if len(elements) > 2 else None
        except Exception as e:
            self.label.text = f"[b]Error fetching details:[/b]\n{e}"
            if self.scrollview and self.scrollview.parent:
                self.layout.remove_widget(self.scrollview)
            return

        # --- Update the main details label ---
        self.label.text = (
            f"[b]Título:[/b] {title}\n"
            f"[b]Autor:[/b] {autor}\n"
            f"[b]Ano:[/b] {date}\n"
            f"[b]Id:[/b] {element_id}\n"
        )

        # --- Clear old table and build new one ---
        if self.scrollview and self.scrollview.parent:
            self.layout.remove_widget(self.scrollview)
        
        if elements and elements[0]:
            self._build_and_populate_table(elements)
            if href_a:
                self.label.text += f"\n[b]Acesso Eletrônico: [/b] {href_a}"
        else:
            self.label.text += "\n\nNenhum Exemplar disponível para este livro."


class SearchApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SearchScreen(name='search'))
        sm.add_widget(DetailsScreen(name='details'))
        return sm

if __name__ == '__main__':
    SearchApp().run()
