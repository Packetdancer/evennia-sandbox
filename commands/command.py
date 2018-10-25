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
    def notify(self, text, style="response", **kwargs):
        """
        Displays the given text via the Notification class, as a shortcut.
        :param text: The text to display.
        :param style: The style to use; the default is 'response'
        :param kwargs: Any additional arguments to pass to the Notification, as documented in the Notification class.
        :return:
        """
        Notification.msg(self.caller, text, style=style, command=self.cmdstring, **kwargs)