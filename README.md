# Evennia Sandbox

## Goals

This is a simple Evennia game meant to be approachable for folks coming from a MUSH background; it provides several MUSH-like commands such as `where` and `finger`, as well as a customized `who`.  

The idea is to provide some basic code people can hack on, tinker with, and otherwise destroy or modify while learning Evennia, while still focusing on the general concepts and look/feel of a game that should be familiar to those with a MUSH background.

## Notifications

There is also a simple `Notification` utility class which creates nicely-formatted, bordered notifications.  It also has customizable colors and prefixes; the prefixes are intended to let you put something at the beginning of notifications so that you can strip them out of logs if you want.

Right now, there are no commands to manage notification customization, but the Notification class is used for display of the existing custom commands.

## Installation

Once you've cloned this into a directory and have an Evennia 0.7 or 0.8 environment available, go into the directory and type

	evennia migrate
	
Once the database is created, type

	evennia start
	
...and follow the prompts.  Then connect with your favorite tool!  If you'd like to edit the project in PyCharm, just open the directory as a project.

## TODO

* Add a calendar system (`when`), and ideally demonstrate how to expose it on the website.
* Add a bboard system, and ideally expose it on the website.