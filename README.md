# Evennia Sandbox

## Goals

This is a simple Evennia game meant to be approachable for folks coming from a MUSH background; it provides several MUSH-like commands such as `where` and `finger`, as well as a customized `who`.  

The idea is to provide some basic code people can hack on, tinker with, and otherwise destroy or modify while learning Evennia, while still focusing on the general concepts and look/feel of a game that should be familiar to those with a MUSH background.

## Useful Places to Start

### Commands

The basic MUSH-like commands are in a `mushlike.py` file in the `commands` directory.  This is probably the most interesting place to look, and is by far the best-documented.

### Notifications

There is a simple `Notification` utility class in the `utils/notifications.py` file which provides a standard way to do notifications from systems (such as upcoming events or new bboard posts) or command responses.  

It also has customizable colors and prefixes; the prefixes are intended to let you put something at the beginning of notifications so that you can strip them out of logs if you want.

Right now, there are no commands to manage notification customization, but the Notification class is used for display of the existing custom commands.  Sadly, this class is not as well-documented as it might be.  (Or, really, at all.)

### PaxCommand

There is also a `PaxCommand` subclass of the standard Evennia `MuxCommand` class, which still uses MUX/MUSH style command parsing but provides some convenience functions (mostly around `Notification`).  You can find `PaxCommand` in `commands/command.py`

### Paxforms

There is a `paxforms` package that allows you build forms that can be easily filled out.  In the future, these forms will be able to be used akin to a Django form -- they'll have a way to be put onto the website to let people fill them out -- but right now they just have an automatically-generated command which can be used to fill them out.  Check out `commands/formtest.py` for an example of using a form, and see `help @formtest` on-game for an example of the automatically-generated helpfiles.

## Installation

Once you've cloned this into a directory and have an Evennia 0.7 or 0.8 environment available, go into the directory and type

	evennia migrate
	
If you're running a current development version of Evennia 0.8, you can recreate the missing files by doing:

	evennia --initmissing
	
Once the database is created and you have the logs directory created, type

	evennia start
	
...and follow the prompts.  You may have to recreate the server logs directory.  (Evennia 0.8 will eventually have an `evennia --initmissing` command which will recreate all the missing files for you.)

Once this is done, connect with your favorite tool!  If you'd like to edit the project in PyCharm, just open the directory as a project.

## TODO

* Add a calendar system (`when`), and ideally demonstrate how to expose it on the website.
* Add a bboard system, and ideally expose it on the website.
* Other things?