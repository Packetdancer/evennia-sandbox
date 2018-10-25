"""
Commands

Commands describe the input the account can do to the game.

"""

from evennia.commands.default.muxcommand import MuxCommand
from utils.notifications import Notification


class PaxCommand(MuxCommand):
    """
    This command class adds a new 'notify' function to the command,
    so that you can use it in place of self.msg as self.notify.  This
    will use the sandbox Notifications class, so that color and appearance
    can be standardized.  Any keyword arguments passed to this function
    will be passed on to Notification appropriately.
    """
    def get_width(self):
        width = 78

        sessions = self.caller.sessions.get()
        if len(sessions) > 0:
            width = sessions[0].protocol_flags['SCREENWIDTH'][0] if sessions[0].protocol_flags.has_key('SCREENWIDTH') else 78

        return width

    def notify(self, text, style="response", **kwargs):
        """
        Displays the given text via the Notification class, as a shortcut.
        :param text: The text to display.
        :param style: The style to use; the default is 'response'
        :param kwargs: Any additional arguments to pass to the Notification, as documented in the Notification class.
        :return:
        """
        Notification.msg(self.caller, text, style=style, command=self.cmdstring, width=self.get_width(), **kwargs)

    def get_notification(self, **kwargs):
        """
        Gets a Notification instance targeted to the current caller, but with the width set to their
        terminal width.

        :param kwargs: Any additional arguments to provide to the notification.
        :return:
        """
        notice = Notification(self.caller, width=self.get_width(), **kwargs)
        return notice
