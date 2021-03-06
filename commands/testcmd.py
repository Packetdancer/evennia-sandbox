from commands.command import PaxCommand
from markdown.parser import MarkdownParser
from evennia.utils.ansi import strip_ansi


class CmdFormatTest(PaxCommand):
    """
    Tests the Markdown functionality.

    Usage:
      fmttest/html <markdown>
      fmttest/text <markdown>

    This will take the given Markdown text and try to convert it into HTML or
    text for testing purposes.
    """

    key = "fmttest"
    locks = "cmd:all()"

    def func(self):

        md = MarkdownParser(self.args)
        if "html" in self.switches:
            html = md.as_html()
            self.msg(html)
            return

        if "text" in self.switches:
            text = md.as_mush()
            self.msg(text)
            return

        self.msg("Provide /html or /text as a switch!")