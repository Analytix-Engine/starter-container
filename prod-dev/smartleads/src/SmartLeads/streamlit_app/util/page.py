from abc import abstractmethod


class Page:
    def __init__(self, menu_label, menu_icon, catalog):
        """
        Represents a page in the Streamlit UI app.

        Args:
            menu_label (str): The label of the menu item.
            menu_icon (str): The icon of the menu item. All icons are available at https://icons.getbootstrap.com/
            catalog (str): The catalog of the page.
        """
        self.menu_label = menu_label
        self.menu_icon = menu_icon
        self.catalog = catalog

    @abstractmethod
    def view_page(self):
        pass
