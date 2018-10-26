"""
Notifications Commands

This set of commands allows a user to configure their display preferences, such as
what color they'd like borders to be, what color they'd like command responses in,
and to ignore various global notification types.
"""

from commands.command import PaxCommand
from utils.notifications import Notification
from evennia.utils.evtable import EvTable
from evennia.utils.ansi import strip_ansi
import string


class CmdDisplay(PaxCommand):
    """
    display
    display/border [color]
    display/width [columns]
    display/prefix <type>[=<prefix>]
    display/ignore <type>
    display/unignore <type>
    display/types

    This command controls your display preferences.  With no arguments,
    this command will show your current display preferences.  With the border
    switch, the given color string will be used to set the color you'd like
    borders to appear in.  Width will set your preferred display width; if not
    set, it will try to default to your client's width. Prefix will set a
    prefix to be prepended to all notification lines of a given type.  Ignore
    and unignore will prevent you from seeing any unsolicited messages of the
    given type.  The last command will list all known types of display.

    """

    key = "display"
    locks = "cmd:all()"

    def func(self):

        if "types" in self.switches:
            note = self.get_notification(border=True,header="Notification Types")
            table = EvTable(border=None, width=self.get_width())
            min_width = 5
            for k, _ in Notification.known_types().iteritems():
                if len(k) + 4 > min_width:
                    min_width = len(k) + 4
            table.add_column(width=min_width)
            for k, v in Notification.known_types().iteritems():
                table.add_row("|w" + k.capitalize() + "|n", v)
            note.add_line(str(table))
            self.msg(note)

            return

        elif "border" in self.switches:
            if self.args:
                if len(strip_ansi(self.args)) > 0:
                    self.notify("Border color has to contain only color codes.")
                    return
                Notification.set_config(self.caller, "border_color", self.args)
                self.notify("Border color set: " + self.args.replace("|", "||"))
            else:
                Notification.set_config(self.caller, "border_color", None)
                self.notify("Border color reset to default.")

            return

        elif "width" in self.switches:
            if self.args:
                try:
                    width = int(self.args)
                    Notification.set_config(self.caller, "width", width)
                    self.notify("Width set to " + self.args)
                except ValueError:
                    self.notify("Width must be a number.")
                return
            else:
                Notification.set_config(self.caller, "width", None)
                self.notify("Width reset to default behavior.")
                return

        elif "prefix" in self.switches:
            if not self.args:
                self.notify("You must provide at least a notification type.")
                return

            lowertype = self.lhs.lower()
            if lowertype not in Notification.known_types():
                self.notify("'" + lowertype + "' is not a type. " + self.cmdstring + "/types will show you valid options.")
                return

            prefixes = Notification.config(self.caller, "prefixes", {})
            if not self.rhs:
                if lowertype in prefixes:
                    del prefixes[lowertype]
                self.notify("Cleared prefix for '" + lowertype + "'.")
            else:
                prefixes[lowertype] = self.rhs + " "
                self.notify("Set prefix for '" + lowertype + "' to " + self.rhs + "|n")

            Notification.set_config(self.caller, "prefixes", prefixes)
            return

        elif "ignore" in self.switches:
            if not self.args:
                self.notify("You must provide at least a notification type.")
                return

            lowertype = self.args.lower()
            if lowertype not in Notification.known_types():
                self.notify("'" + lowertype + "' is not a type. " + self.cmdstring + "/types will show you valid options.")
                return

            ignored = Notification.config(self.caller, "ignored", [])
            ignored.append(lowertype)
            Notification.set_config(self.caller, "ignored", ignored)
            self.notify("Ignored unsolicited messages of type '" + lowertype + "'.")
            return

        elif "unignore" in self.switches:
            if not self.args:
                self.notify("You must provide at least a notification type.")
                return

            lowertype = self.args.lower()
            if lowertype not in Notification.known_types():
                self.notify("'" + lowertype + "' is not a type. " + self.cmdstring + "/types will show you valid options.")
                return

            ignored = Notification.config(self.caller, "ignored", [])
            ignored.remove(lowertype)
            Notification.set_config(self.caller, "ignored", ignored)
            self.notify("No longer ignoring unsolicited messages of type '" + lowertype + "'.")
            return

        else:
            note = self.get_notification(border=True, header="Display Settings")
            table = EvTable(border=None, width=self.get_width())
            table.add_column("|wSetting|n", width=20)
            table.add_column("|wValue|n")

            border = Notification.config(self.caller, "border", default="Default") or "Default"
            width = Notification.config(self.caller, "width", default=78)
            prefixes = Notification.config(self.caller, "prefixes", default={})
            ignored = Notification.config(self.caller, "ignored", default=[])

            table.add_row("Border Color", border.replace("|", "||"))
            table.add_row("Display Width", str(width))
            if len(prefixes) > 0:
                subtable = EvTable(border=None, width=self.get_width() - 4)
                min_width = 5
                for k, _ in prefixes.iteritems():
                    if len(k) + 4 > min_width:
                        min_width = len(k) + 4
                subtable.add_column(width=min_width)

                for k, v in prefixes.iteritems():
                    subtable.add_row(k.capitalize(), v)

                table.add_row("Prefixes", str(subtable))
            else:
                table.add_row("Prefixes", "None")

            if len(ignored) > 0:
                table.add_row("Ignoring", string.join(ignored, ", "))
            else:
                table.add_row("Ignoring", "None")

            note.add_line(str(table))
            self.msg(note)