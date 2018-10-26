from evennia.utils import ansi
from evennia.server.sessionhandler import SESSIONS


class Notification:
    """
    A class which encapsulates a notification to a player.  This will let you
    filter lines of text or add prefixes to notifications, or block various
    notifications entirely.

    For initialization or sending, there are several keyword arguments you can provide:

    * notification_type: The class of notification, or 'general'.  This might be 'bboard'
                         'event' or something similar; send_all will use this to determine if
                         a user wants those notifications or not.  If not provided, defaults to
                         'general'
    * style: 'normal' or 'response'; 'response' will have the 'command' field prepended to the
             result if a command was given.
    * command: The command which generated this notification, or None.  Defaults to None
    * border: True or False, as to whether a border should be drawn around this command.
    * header: If provided, a title that will be added to the decorative border.
    * footer: If provided, a footer that will be added to the decorative border.
    * width: How wide this notification should be allowed to be, and how wide the border
             will be.  Defaults to 78 if not given.
    """

    notification_types = {'general': 'General command output, such as from who or finger.',
                          'test': 'Pax\'s test message type.'}

    def __init__(self, caller, notification_type="general", style="normal", command=None, border=False, header=None, footer=None, width=None):
        self.notification_type = notification_type
        self.caller = caller
        self.border = border
        self.header_title = header
        self.footer_title = footer
        self.lines = []
        self.width = width or self.get_config("width", default=78)
        self.style = style
        self.command = command

    def __str__(self):
        result = ""

        prefix = self.get_prefix()
        if self.style == "response":
            if self.command:
                prefix = prefix + "|w" + self.command + ":|n "

            single_color = self.get_config("response_color") or "|n"

            for line in self.lines:
                result = "\n" + prefix + single_color + line

        else:
            border_color = self.get_config("border_color", "|[B")
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
                    result = result + "\n" + prefix + border_color + ("=" * self.width) + "|n"
                else:
                    raw_footer = ansi.strip_ansi(self.footer_title)
                    line = border_color + "=" * (self.width - (len(raw_footer) + 9))
                    line = line + "|w[ " + self.footer_title + " ]" + border_color + ("=" * 5) + "|n"
                    result = result + "\n" + prefix + line

        return result

    def get_prefix(self):
        """
        Get the user's chosen prefix for this notification type
        """
        prefixes = self.get_config("prefixes", default={})
        
        return prefixes[self.notification_type] if self.notification_type in prefixes else ""

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

        if self.style is not "response":
            ignores = self.get_config("ignored", default=[])

            if self.notification_type in ignores:
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

    def get_config(self, key, default=None):
        """
        Retrieves the given notification configuration value for the current notification's caller.

        :param key:
        :param default:
        :return:
        """
        return Notification.config(self.caller, key, default=default)

    @classmethod
    def config(cls, caller, key, default=None):
        """
        Retrieves the given notification configuration preference for the provided caller.  This can
        be called as a class function instead of requiring a specific notification.

        :param caller: The caller whose preference should be retrieved.
        :param key: The name of the preference, such as 'width'
        :param default: A default value to use if none is set.
        :return: The value for the configuration key given.
        """

        if not caller:
            return default

        prefs = caller.db.notification_prefs or {}
        if key == "width" and not "width" in prefs:
            # Special case for our default
            sessions = caller.sessions.get()
            if len(sessions) > 0:
                result = (sessions[0].protocol_flags['SCREENWIDTH'][0] - 2) if sessions[0].protocol_flags.has_key(
                    'SCREENWIDTH') else default
        else:
            result = prefs[key] if key in prefs else default

        return result

    @classmethod
    def set_config(cls, caller, key, value):
        """
        Sets a Notification preference value for the given caller.

        :param caller: The caller whose preference should be set
        :param key: The key to set or clear.
        :param value: The value, or None to clear the key.
        :return:
        """

        if not caller:
            return

        prefs = caller.db.notification_prefs or {}

        if value:
            prefs[key] = value
        elif key in prefs:
            del prefs[key]

        caller.db.notification_prefs = prefs

    @classmethod
    def known_types(cls):
        """
        Returns a dictionary of all known notification types.  The key will be the notification
        name, while the value will be a description of the notification type suitable for display
        to the user.
        :return: A dictionary of all known notification types.
        """
        return cls.notification_types

    @classmethod
    def add_type(cls, name, description):
        """
        Adds a new notification type to the list of known types.
        :param name: The name of this notification type, such as 'general'.
        :param description: The description for this notification type.
        """
        cls.notification_types[name.lower()] = description
