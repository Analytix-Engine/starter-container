# System imports

# Third party imports

# Local imports
from SmartLeads.streamlit_app.util.page import Page


class TestPage:
    page = Page(
        menu_label="mocked_menu_label",
        menu_icon="mocked_menu_icon",
        catalog="mocked_catalog",
    )

    def test_should_have_menu_label(self):
        assert self.page.menu_label == "mocked_menu_label"

    def test_should_have_menu_icon(self):
        assert self.page.menu_icon == "mocked_menu_icon"

    def test_should_have_abstract_catalog_property(self):
        assert self.page.catalog == "mocked_catalog"

    def test_should_have_abstract_view_page_method(self):
        assert hasattr(self.page, "view_page")
