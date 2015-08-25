import webbrowser, sys, os
from gi.repository import Gtk, GLib, GObject, Gdk
try:
       from gi.repository import AppIndicator3 as AppIndicator
except:
       from gi.repository import AppIndicator

class PySearchIndicator:
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
        item.set_label("Edit engines...")
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
        Gtk.main()


    def handler_edit_engines(self, evt):
        webbrowser.open(os.path.join(__location__, "engines.list"))

    def handler_reload(self, evt):
        self.menu.destroy()
        engines = get_engines()
        self.__init__(engines)

    def handler_menu_exit(self, evt):
        Gtk.main_quit()
        sys.exit(1)

    def main(self):
        Gtk.main()

class EntryWindow(Gtk.Window):

    def __init__(self, engine, engines):
        Gtk.Window.__init__(self)
        self.set_resizable(False)
        self.set_size_request(300, 50)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_type_hint(Gdk.WindowTypeHint.NOTIFICATION)
        self.set_keep_above(True)
        self.set_icon_name("search")
        self.connect("delete-event", Gtk.main_quit)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        # Entry
        self.entry = Gtk.Entry()
        self.entry.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, Gtk.STOCK_FIND)
        self.entry.set_text("Search on "+engine)
        self.entry.connect("activate", self.handler_search, engine)
        self.entry.connect("focus-out-event", self.handler_exit)
        self.entry.connect("changed", self.on_text_change)
        self.entry.connect("key-release-event", self.on_key_release)
        vbox.pack_start(self.entry, True, True, 0)

        # Button
        self.button = Gtk.Button("Exit")
        self.button.connect("clicked", self.handler_search, engine)
        vbox.pack_start(self.button, True, True, 0)

        self.show_all()

    def on_text_change(self, string):
        if self.entry.get_text_length() is 0:
            self.button.set_label("Exit")
        else:
            self.button.set_label("Search")

    def handler_exit(self, event, user_param1):
        if not self.has_toplevel_focus():
            self.destroy()

    def handler_search(self, widget, engine):
        if self.button.get_label() == "Search":
            query = self.entry.get_text()
            print "Searching for '"+query+"' at "+engine
            query = query.replace(' ', '+')
            webbrowser.open(engines[engine]+query)
            self.destroy()
        else:
            self.destroy()

    def on_key_release(self, widget, ev, data=None):
        if ev.keyval == 65307: #ESC key
            self.destroy()


def get_engines():
    print "Loading search engines:"
    eng = {}
    with open(os.path.join(__location__, "engines.list")) as f:
        for line in f:
            line = line.split()
            if len(line) > 0:
                if line[0][0] is not '#' and len(line) >= 2:
                    key = " ".join(line[0:len(line)-1])
                    val = line[len(line)-1]
                    eng[key] = val
                    print "Added: '"+key+"' -> '"+val+"'"

    return eng

if __name__ == "__main__":

    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

    engines = get_engines()
    ind = PySearchIndicator(engines)
    ind.main()
