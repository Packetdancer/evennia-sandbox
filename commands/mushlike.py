"""
MUSH-like Commands

This file contains commands that implement some basic MUSH-like functionality.
In particular, a finger command (which reads db attributes and displays them
as a form), a who command (which iterates across the users and displays some
text), and a where command (which shows you where all the currently connected
users are).

All of our commands are classes which descend from Evennia's MuxCommand class,
which provides a MUX/MUSH style command parser.  Information on commands in
general can be found at:
https://github.com/evennia/evennia/wiki/Commands

The class documentation for MuxCommand itself can be found at:
https://github.com/evennia/evennia/wiki/evennia.commands.default.muxcommand

"""

from evennia.server.sessionhandler import SESSIONS
from evennia.utils import utils, evtable, search
from utils.notifications import Notification as Note
from commands.command import PaxCommand
import time
import datetime
import string

# All our commands descend from PaxCommand, which is a subclass of MuxCommand
# with some helper functions on it.  In particular, we use self.notify in place
# of the default self.msg, so that all messages pass through the Notification
# class and can have standardized appearances.


class CmdFinger(PaxCommand):
    """
    finger [user]
    finger/setname [value]
    finger/setaliases [value]
    finger/set <field>=[value]

    Displays information on the given user.  If you don't provide a user, displays
    information for you yourself.

    The second form of the command will set a longer name for yourself, which will
    show in place of your actual character name in the finger output.  If you don't
    provide a value, it will reset to just showing your character name.

    The third form of the command will set your aliases, which should be a comma-
    delimited list of what you want them to be.  If you don't provide a value,
    your aliases will be cleared.

    The last form of the command will set a custom finger field to be displayed,
    such as your timezone or RP preferences, or perhaps your favorite cookie flavor.

    """

    key = "finger"
    locks = "cmd:all()"

    def func(self):
        """
        This function needs to be overridden for each command we write, and
        contains the main 'logic' of the function.

        The command parser has set a few fields for us:

        * self.caller is the character running the command
        * self.cmdstring is what command you typed ('finger') to run this.
        * self.switches is an array containing any switches you passed
        * self.args is everything you passed to the command
        * self.lhs is the left-hand side of args, if there was an = sign
        * self.rhs is the right-hand side of args, if there was an = sign
        """

        if "set" in self.switches:
            # We're setting a custom field.

            if not self.lhs:
                self.notify("You must provide a finger field to set.")
                return

            # We store fields as lowercase
            fieldname = self.lhs.lower()

            # Get our fields, or an empty dictionary if it doesn't exist
            fields = self.caller.db.finger_extra_fields or {}

            if not self.rhs:
                if fieldname in fields:
                    del fields[fieldname]
                    self.notify("Cleared '" + fieldname + "' field.")
                else:
                    self.notify("No such field '" + fieldname + "'.")
                    return
            else:
                fields[fieldname] = self.rhs
                self.notify("Set '" + fieldname + "' to: " + self.rhs)

            # Now we have our updated fields dictionary, set it on
            # our caller.
            self.caller.db.finger_extra_fields = fields

        elif "setname" in self.switches:

            # We're setting the longname.  It's pretty straightforward.

            if not self.args:
                del self.caller.db.long_name
                self.notify("Long name cleared.")
            else:
                self.caller.db.long_name = self.args
                self.notify("Long name set: " + self.args)

        elif "setaliases" in self.switches:

            # We're going to edit the AliasHandler that stores aliases for
            # the calling object.  First we'll clear the aliases, so that
            # each time you provide the list, that's the entire set.

            self.caller.aliases.clear()

            # If you provided an argument, turn all the aliases lowercase and
            # add them to the AliasHandler.  If you didn't provide an argument,
            # we're already done.
            if self.args:
                new_aliases = [alias.strip().lower() for alias in self.args.split(',') if alias.strip()]
                self.caller.aliases.add(new_aliases)
                self.notify("Aliases set: " + str(self.caller.aliases))
            else:
                self.notify("Aliases cleared.")

        else:
            # This is the default finger command without switches

            target_player = None

            if self.args:
                # Our caller has a search() function which works somewhat like
                # the locate() function on MUSH, and searches through any Evennia
                # objects -- i.e., anything descending from Object -- for something
                # with a name or alias that matches.
                #
                # If we don't find anything, this function actually sends 'Could not
                # find <whatever>' to the searcher, by default; let's add quiet=True
                # to change that.
                #
                target_players = self.caller.search(self.args, global_search=True, quiet=True,
                                                    use_nicks=True,
                                                    typeclass="typeclasses.characters.Character")

                # Since this is a queryset, we need to pull an object out of it.
                # It should be a queryset of one, however, so we just get the first element.
                target_player = target_players.first()

            else:
                # If you don't provide a player, let's just finger ourselves
                target_player = self.caller

            if not target_player:
                self.notify("Could not find a player named '" + self.args + "'.")
                return

            # The Notification class is a helper we've defined over in utils/notifications.py
            # It lets us create user-customizable notifications, where you can alter prefixes
            # or colors.
            notification = self.get_notification(border=True, header="Player Info")

            notification.add_line("|w" + target_player.key.upper() + "|n", align="center")
            notification.add_divider()

            if target_player.db.long_name:
                notification.add_line(" |wName:|n    " + target_player.db.long_name)
            else:
                notification.add_line(" |wName:|n    " + target_player.key)

            if len(target_player.aliases.all()) > 0:
                notification.add_line(" |wAliases:|n " + str(target_player.aliases))

            # Get the sessions for the target player
            sessions_list = target_player.sessions.get()
            if sessions_list:
                sessions_list = sorted(sessions_list, key=lambda s: s.cmd_last_visible)
                idle_time = time.time() - sessions_list[0].cmd_last_visible
                last_on = "Online now, idle for " + utils.time_format(idle_time, 1) + "."
            else:
                # If you check typeclasses/characters.py, you'll see we put some special
                # logic in at_post_unpuppet to store the last time someone logged out.
                last_logout = target_player.db.last_logout
                if last_logout:
                    date = datetime.datetime.fromtimestamp(last_logout)
                    last_on = "Offline, last seen " + date.strftime("%Y/%m/%d") + "."
                else:
                    last_on = "Offline."

            notification.add_line(" |wStatus:|n  " + last_on)

            if target_player.db.finger_extra_fields:
                notification.add_divider(title="Other Info")

                # To make our 'Other Info' align nicely, we're going to use an EvTable
                table = evtable.EvTable(border=None, width=notification.width)

                # First let's find out what our widest field name is.
                widest_field = 5
                for field, _ in target_player.db.finger_extra_fields.iteritems():
                    if len(field) > widest_field:
                        widest_field = len(field)

                # Now we're adding a column to the table that has the appropriate
                # width, so it's as small as it can be.
                table.add_column(width=widest_field + 4)

                # Now we add a row for each field in our custom fields
                for field, value in target_player.db.finger_extra_fields.iteritems():
                    table.add_row("|w" + field.capitalize() + ":|n", value)

                # Yes, we can stuff tables into a Notification without issue
                notification.add_line(str(table))

            # Send the notification to the user.
            notification.send(self.caller)


class CmdWho(PaxCommand):
    """
    who [prefix]
    doing [prefix]
    doing/set [pithy quote]

    This command shows who is presently online.  If a prefix is given, it will
    only show the accounts whose names start with that prefix.  For admins, if
    you wish to see the player-side list, type 'doing'.  For all players, if
    you'd like to set a pithy quote to show up in the last column, use
    'doing/set'.  If you don't provide a value to doing/set, it will clear yours.
    """

    key = "who"
    aliases = ["doing", ]
    locks = "cmd:all()"

    def func(self):
        """
        This function needs to be overridden for each command we write, and
        contains the main 'logic' of the function.

        The command parser has set a few fields for us:

        * self.caller is the character running the command
        * self.cmdstring is what command you typed ('finger') to run this.
        * self.switches is an array containing any switches you passed
        * self.args is everything you passed to the command
        * self.lhs is the left-hand side of args, if there was an = sign
        * self.rhs is the right-hand side of args, if there was an = sign
        """

        # First, let's check if someone is setting their "doing" value.
        if self.cmdstring == "doing" and "set" in self.switches:

            if self.args == "":
                self.notify("Doing field cleared.")
                self.account.db.who_doing = None
            else:
                self.notify("Doing field set: {}".format(self.args))
                self.account.db.who_doing = self.args

            # If we were just setting our doing, we're done now, so return
            return

        if self.args:
            session_list = [session for session in SESSIONS.get_sessions()
                            if session.get_account().key.startswith(self.args)]
        else:
            session_list = SESSIONS.get_sessions()

        # Sort the list by the time connected
        #
        # To read more on lambdas, check out:
        # https://www.programiz.com/python-programming/anonymous-function
        #
        session_list = sorted(session_list, key=lambda sess: sess.conn_time)

        # If our command was 'doing', we never show the admin version of things.
        # Otherwise, we check if the account has Developer or Admins permissions.
        #
        if self.cmdstring == "doing":
            show_admin_data = False
        else:
            show_admin_data= self.account.check_permstring("Developer") or self.account.check_permstring("Admins")

        naccounts = SESSIONS.account_count()
        if naccounts == 1:
            footer = "1 player online."
        else:
            footer = str(naccounts) + " players online."

        # Build a notification using our Notification helper class.  You can find
        # the helper class in utils/notifications.py
        #
        notification = self.get_notification(border=True, header="Who's Online", footer=footer)

        # Now we build a table to put in the notification
        table = evtable.EvTable(border=None, width=notification.width)
        table.add_column("|wAccount Name|n", width=22)
        table.add_column("|wOn For|n")
        table.add_column("|wIdle|n")
        if show_admin_data:
            table.add_column("|wRoom|n")
            table.add_column("|wClient|n")
            table.add_column("|wAddress|n")
        else:
            table.add_column("|wDoing|n")

        # Iterate across the sessions
        for session in session_list:

            # If this session isn't logged in -- i.e. is at the login screen
            # or something -- just skip it.
            if not session.logged_in:
                continue

            # How long has it been since their last command?
            #
            delta_cmd = time.time() - session.cmd_last_visible

            # How long has this session been connected?
            #
            delta_conn = time.time() - session.conn_time

            account = session.get_account()
            account_name = account.key

            # If the 'who_doing' Evennia attribute on the account isn't empty,
            # let's store it in a new variable called doing_string, otherwise
            # let's store an empty string.
            #
            # The format we're using here is called a 'ternary conditional operator',
            # and you can read a bit more about it at:
            # https://www.pythoncentral.io/one-line-if-statement-in-python-ternary-conditional-operator/
            #
            doing_string = account.db.who_doing if account.db.who_doing else ""

            # Get the Character that this Account is using.
            character = session.get_puppet()

            # Now we have all our data gathered!  Let's add a row to the table
            if show_admin_data:
                if session.protocol_key == "websocket":
                    client_name = "Web Client"
                else:
                    # Get a sane client name to display.
                    client_name = session.protocol_flags['CLIENTNAME'].capitalize()
                    if not client_name:
                        client_name = session.protocol_flags['TERM']
                    if client_name.upper().endswith("-256COLOR"):
                        client_name = client_name[:-9]

                table.add_row(utils.crop(account_name, 20),
                              utils.time_format(delta_conn, 0),
                              utils.time_format(delta_cmd, 1),
                              "#{}".format(character.location.id) if character else "",
                              client_name,
                              session.address[0] if isinstance(session.address, tuple) else session.address)
            else:
                table.add_row(utils.crop(account_name, 20),
                              utils.time_format(delta_conn, 0),
                              utils.time_format(delta_cmd, 1),
                              doing_string)

        # Send the table to our user as a notification
        notification.add_line(str(table))

        # We can actually use the notification like a string if we want to!
        self.msg(notification)


class CmdWhere(PaxCommand):
    """
    where

    This command shows you where all the online players are gathered.  It
    could stand to be made more advanced.
    """

    key = "where"
    locks = "cmd:all()"

    def func(self):
        """
        This function needs to be overridden for each command we write, and
        contains the main 'logic' of the function.

        The command parser has set a few fields for us:

        * self.caller is the character running the command
        * self.cmdstring is what command you typed ('finger') to run this.
        * self.switches is an array containing any switches you passed
        * self.args is everything you passed to the command
        * self.lhs is the left-hand side of args, if there was an = sign
        * self.rhs is the right-hand side of args, if there was an = sign
        """

        # Create a notification using our Notification helper class.
        #
        # To read up on the Notification class, you can check out
        # utils/notifications.py
        notification = self.get_notification(header="Where Is Everyone?", border=True)

        # Get a list of all the rooms for online players
        rooms = [session.get_puppet().location for session in SESSIONS.get_sessions() if session.get_puppet()]

        # Turn our list into a set, so each room only appears once
        rooms = set(rooms)

        # Create a table to display our list.
        table = evtable.EvTable(border="none", width=notification.width)

        for room in rooms:
            # Get our players
            players = [obj for obj in room.contents if obj.is_typeclass("typeclasses.characters.Character")]
            # Get their names, and join them into a comma-delimited list
            player_names = string.join([player.key for player in players], ", ")
            table.add_row("|w" + room.key + ":|n", player_names)

        # Stuff our table into the notification
        notification.add_line(str(table))

        # Send the notification to our user
        self.msg(notification)