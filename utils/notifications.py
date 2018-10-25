from evennia.utils import ansi
from evennia.server.sessionhandler import SESSIONS
import string


class Notification:
    """
    A class which encapsulates a notification to a player.  This will let you
    filter lines of text or add prefixes to notifications, or block various
    notifications entirely.
    """

    lines = []
    caller = None
    border = False
    header_title = None
    footer_title = None
    width = 78
    style = "normal"
    command = None

    def __init__(self, caller, notification_type="general", style="normal", command=None, border=False, header=None, footer=None, width=78):
        self.notification_type = notification_type
        self.caller = caller
        self.border = border
        self.header_title = header
        self.footer_title = footer
        self.lines = []
        self.width = width
        self.style = style
        self.command = command

    def __str__(self):
        result = ""

        prefix = self.get_prefix()
        if self.command:
            prefix = prefix + "|w" + self.command + ":|n "

        if self.style == "response":
            single_color = self.caller.db.notification_response or "|n"

            for line in self.lines:
                result = "\n" + prefix + single_color + line

        else:
            border_color = self.caller.db.notification_border or "|B"
            if self.border:
                result = "\n"
                if not self.header_title:
                    result = result + prefix + border_color + ("=" * self.width) + "|n"
                else:
                    raw_header = ansi.strip_ansi(self.header_title)
                    line = border_color + ("=" * 5) + "|w[ " + self.header_title + " ]" + border_color
                    line = line + "=" * (self.width - (len(raw_header) + 9))
                    result = result + prefix + line + "|n"

            for line in self.lines:
                result = result + "\n" + prefix + line

            if self.border:
                if not self.footer_title:
                    result = result + "\n" + prefix + border_color + ("=" * self.width) + "|n\n"
                else:
                    raw_footer = ansi.strip_ansi(self.footer_title)
                    line = border_color + "=" * (self.width - (len(raw_footer) + 9))
                    line = line + "|w[ " + self.footer_title + " ]" + border_color + ("=" * 5)
                    result = result + "\n" + prefix + line

        return result

    @classmethod
    def msg(cls, caller, text, style="response", **kwargs):
        """
        Convenience function that creates a one-line notification and sends it all in one go.
        :param caller: The person to receive this message
        :param text: The text to send
        :param kwargs: Normal Notification initialization arguments
        """
        notice = cls(caller, style=style, **kwargs)
        notice.add_line(text)
        notice.send(caller)

    def get_prefix(self):
        """
        Get the user's chosen prefix for this notification type
        """
        if not self.caller or self.caller.db.notification_prefixes is None:
            return ""

        prefix = self.caller.db.notification_prefixes[self.notification_type]
        return prefix and prefix + "|n " or ""

    def add_line(self, text, align="left"):
        """
        Add a line of text to this notification.

        :param text: The line of text to add.
        :param align: "left", "right", or "center" -- defaults to left
        """

        temp_lines = text.split("\n")
        if len(temp_lines) > 1:
            for subline in temp_lines:
                self.add_line(subline)
        else:
            line = text

            if align == "right":
                line = " " * (self.width - len(ansi.strip_ansi(text))) + text
            elif align == "center":
                padding = (self.width - len(ansi.strip_ansi(text))) / 2
                line = " " * padding + line

            self.lines.append(line)

    def add_divider(self, title=None):
        """
        Adds a divider line to the Notification instance.
        """

        if not title:
            self.add_line("-" * self.width)
        else:
            self.add_line(("-" * 5) + "[ |w" + title + "|n ]" +
                          ("-" * (self.width - (len(ansi.strip_ansi(title)) + 9))))

    def send(self, caller):
        """
        Sends to the given caller, with their customizations, if and only if
        they have not disabled the notifications in question.

        :param caller: The recipient of the message.
        """
        if not caller:
            return

        # If this is an account, go to all their connected players
        if caller.is_typeclass("typeclasses.accounts.Account"):
            for session in caller.sessions:
                self.send(session.get_puppet())

        self.caller = caller

        if self.caller.db.notification_ignores and \
                self.notification_type in self.caller.db.notification_ignores:
            # We have this notification type set to ignore, so don't
            # send anything
            return

        self.caller.msg(str(self))

    def send_all(self, list=None):
        """
        For every connected session, sends this to any Character they're using
        that hasn't ignored this notification.  Do this so we get the Character's
        preferences.

        If they aren't logged into a Character, just send directly to the Account

        :param list: A list of specific Characters or Accounts to send to, optional.
        """

        if not list:
            for session in SESSIONS.get_sessions():
                puppet = session.get_puppet()
                if puppet:
                    self.send(puppet)
                else:
                    # Give up and send to the account, which won't have puppet prefs
                    self.send(session.get_account())
        else:
            for recipient in list:
                self.send(recipient)