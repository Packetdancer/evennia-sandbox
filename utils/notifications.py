from evennia.utils import ansi

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

    def __init__(self, caller, notification_type="general", border=False, header=None, footer=None, width=78):
        self.notification_type = notification_type
        self.caller = caller
        self.border = border
        self.header_title = header
        self.footer_title = footer
        self.lines = []
        self.width = width

    def __str__(self):
        result = ""

        prefix = self.get_prefix()
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