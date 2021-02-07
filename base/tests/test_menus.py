from django.test import TestCase
from django.conf import settings
from django.utils import translation
from wagtail.core.models import Page, Site
from wagtailtrans.models import Language, TranslatablePage

from .factories import MenuFactory, MenuItemFactory, StandardPageFactory
from base.templatetags.navigation_tags import get_menu
from base.models import Menu, MenuItem


class TestMenus(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(is_default_site=True, root_page=Page.get_first_root_node())
        cls.page1 = StandardPageFactory(show_in_menus=True)
        cls.menu = MenuFactory()
        # for the menu-items we need to establish a sort order (class Orderable)
        cls.menuitem_ordinary = MenuItemFactory(
            menu=cls.menu, sort_order=1, title="Ordinary", link_url='/ordinary/', show_when='always'
        )
        cls.menuitem_guest = MenuItemFactory(
            menu=cls.menu, sort_order=2, title="Guest", link_url='/guest/', show_when='not_logged_in'
        )
        cls.menuitem_page1 = MenuItemFactory(menu=cls.menu, sort_order=3, link_page=cls.page1)
        # switch on a second language
        cls.foreign_language_code = [code for code, lang in settings.LANGUAGES if code != settings.LANGUAGE_CODE][0]
        cls.foreign_language = Language.objects.get_or_create(code=cls.foreign_language_code)[0]
        # note: Wagtailtrans automatically creates a language tree for every language that is defined
        cls.foreign_page1 = TranslatablePage.objects.get(language=cls.foreign_language, canonical_page=cls.page1)

    def test_get_handmade_menu(self):
        menu = get_menu(self.menu.slug, None, True)
        self.assertEqual(menu[0]['title'], 'Ordinary')
        # the expected url is in the current language
        expected_url = '/' + translation.get_language() + '/ordinary/'
        self.assertEqual(menu[0]['url'], expected_url)

    def test_get_menu_logged_in(self):
        menu = get_menu(self.menu.slug, None, True)
        self.assertEqual(len(menu), 2)

    def test_get_menu_not_logged_in(self):
        menu = get_menu(self.menu.slug, None, False)
        self.assertEqual(len(menu), 3)

    def test_menuitem_trans_page_for_foreign_language(self):
        self.assertEqual(self.menuitem_page1.trans_page(self.foreign_language_code).url, self.foreign_page1.url)

    def test_menuitem_trans_page_for_canonical_language(self):
        self.assertEqual(self.menuitem_page1.trans_page(settings.LANGUAGE_CODE).url, self.page1.url)

    def test_menuitem_trans_url_method(self):
        self.assertEqual(self.menuitem_page1.trans_url(self.foreign_language_code), self.foreign_page1.url)

    def test_menu_str(self):
        menu = Menu.objects.first()
        self.assertEqual(str(menu), "Menu 0")

    def test_menu_item_str(self):
        menu_item = MenuItem.objects.first()
        self.assertEqual(str(menu_item), "Ordinary")
