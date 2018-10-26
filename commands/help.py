"""
The help command. The basic idea is that help texts for commands
are best written by those that write the commands - the admins. So
command-help is all auto-loaded and searched from the current command
set. The normal, database-tied help system is used for collaborative
creation of other help topics such as RP help or game-world aides.
"""

from evennia.utils.evtable import EvTable
from evennia.commands.default.help import CmdHelp
from utils.notifications import Notification
import string

# We're just subclassing the help command to change the formatting slightly.
class CmdPaxHelp(CmdHelp):
    """
    View help or a list of topics

    Usage:
      help <topic or command>
      help list
      help all

    This will search for help on commands and other
    topics related to the game.
    """
    key = "help"
    aliases = ['?']
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def format_help_entry(self, title, help_text, aliases=None, suggested=None):
        """
        This visually formats the help entry.
        This method can be overriden to customize the way a help
        entry is displayed.

        Args:
            title (str): the title of the help entry.
            help_text (str): the text of the help entry.
            aliases (list of str or None): the list of aliases.
            suggested (list of str or None): suggested reading.

        Returns the formatted string, ready to be sent.

        """
        notice = Notification(self.caller, border=True)

        if title or aliases:
            notice.add_line("")

        if title:
            notice.add_line("|w" + title.upper() + "|n")
        if aliases:
            notice.add_line("|wAliases:|n " + string.join(aliases,", "))
        if help_text:
            notice.add_line(help_text)
        if suggested:
            notice.add_line("|wSuggested:|n " + string.join(suggested, ", "))
            if title or aliases:
                notice.add_line("")

        return str(notice)

    def format_help_list(self, hdict_cmds, hdict_db):
        """
        Output a category-ordered list. The input are the
        pre-loaded help files for commands and database-helpfiles
        respectively.  You can override this method to return a
        custom display of the list of commands and topics.
        """
        notice = Notification(self.caller, border=True, header="Help Entries")
        notice.add_line("")

        if hdict_cmds and any(hdict_cmds.values()):
            if hdict_db and any(hdict_db.values()):
                notice.add_divider(title="|wCommands|n")
            table = EvTable(width=notice.width - 4, border=None)
            for category in sorted(hdict_cmds.keys()):
                table.add_row("|w" + category.capitalize())
                row = string.join(sorted(hdict_cmds[category])) + "\n"
                table.add_row(row)
            notice.add_line(str(table))
            notice.add_line("")
        if hdict_db and any(hdict_db.values()):
            if hdict_cmds and any(hdict_cmds.values()):
                notice.add_divider(title="|wOther Entries|n")
            table = EvTable(width=notice.width - 4, border=None)
            for category in sorted(hdict_db.keys()):
                table.add_row("|w" + category.capitalize() + "|n")
                row = string.join(sorted(hdict_db[category])) + "\n"
                table.add_row(row)
            notice.add_line(str(table))
            notice.add_line("")

        return str(notice)

