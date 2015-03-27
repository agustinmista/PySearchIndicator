import webbrowser
from gi.repository import Gtk, GLib, GObject
try:
       from gi.repository import AppIndicator3 as AppIndicator
except:
       from gi.repository import AppIndicator

class IndicatorSearch:
    def __init__(self, engines):
        # param1: identifier of this indicator
        # param2: name of icon
        # param3: category
        self.ind = AppIndicator.Indicator.new("indicator-search", "search",
                            AppIndicator.IndicatorCategory.OTHER)

        self.ind.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.menu = Gtk.Menu()

        # Add the list of search engines
        for key in sorted(engines):
            item = Gtk.MenuItem(key)
            item.set_label(key)
            item.connect("activate", self.handler_menu_search)
            item.show()
            self.menu.append(item)

        # Separator
        item = Gtk.SeparatorMenuItem()
        item.show()
        self.menu.append(item)

        # Edit the search engines list
        item = Gtk.MenuItem()
        item.set_label("Edit engines")
        item.connect("activate", self.handler_edit_engines)
        item.show()
        self.menu.append(item)

        # Reload the indicator
        item = Gtk.MenuItem()
        item.set_label("Reload")
        item.connect("activate", self.handler_reload)
        item.show()
        self.menu.append(item)

        # Exit the app
        item = Gtk.MenuItem()
        item.set_label("Quit")
        item.connect("activate", self.handler_menu_exit)
        item.show()
        self.menu.append(item)

        self.menu.show()
        self.ind.set_menu(self.menu)

    def handler_menu_search(self, evt):
        win = EntryWindow(evt.get_label(), engines)
        win.connect("delete-event", Gtk.main_quit)
        win.show_all()
        Gtk.main()

    def handler_edit_engines(self, evt):
        webbrowser.open("engines.list")

    def handler_reload(self, evt):
        self.menu.destroy()
        engines = get_engines()
        self.__init__(engines)

    def handler_menu_exit(self, evt):
        Gtk.main_quit()


    def main(self):
        Gtk.main()

class EntryWindow(Gtk.Window):

    def __init__(self, engine, engines):
        Gtk.Window.__init__(self, title="Search on "+engine)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.get_focus()
        self.set_icon_name("search")
        self.set_size_request(300, 50)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        self.entry = Gtk.Entry()
        self.entry.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, Gtk.STOCK_FIND)
        self.entry.connect("activate", self.handler_search, engine)
        self.entry.connect("key-release-event", self.on_key_release)
        vbox.pack_start(self.entry, True, True, 0)

        self.button = Gtk.Button("Search")
        self.button.connect("clicked", self.handler_search, engine)
        vbox.pack_start(self.button, True, True, 0)

    def handler_search(self, widget, engine):
        query = self.entry.get_text()
        print "Searching for '"+query+"' at "+engine
        query = query.replace(' ', '+')
        webbrowser.open(engines[engine]+query)
        self.destroy()

    def on_key_release(self, widget, ev, data=None):
        if ev.keyval == 65307: #ESC key
            self.destroy()


def get_engines():
    print "Loading search engines:"
    eng = {}
    with open("engines.list") as f:
        for line in f:
            line = line.split()
            if len(line) > 0:
                if line[0][0] is not '#' and len(line) == 2:
                    (key, val) = line
                    eng[key] = val
                    print "Added: '"+key+"' -> '"+val+"'"

    return eng

if __name__ == "__main__":
    engines = get_engines()
    ind = IndicatorSearch(engines)
    ind.main()
