import markdown2
from bs4 import BeautifulSoup
from evennia.utils.ansi import strip_ansi


class MarkdownParser:

    def __init__(self, original):
        self.text = ""
        self.tags = []
        self.indent = 0
        self.counters = []

        self.html = None
        self.formatted = None

        if original is None:
            raise ValueError

        text = original.replace("|/", "\n")
        text = text.replace("%r", "\n")
        text = text.replace("|-", "\t")
        text = text.replace("%t", "\t")
        text = text.replace("|_", " ")
        text = text.replace("%b", " ")
        self.original = strip_ansi(text)
        self.html = markdown2.markdown(self.original)
        self.text = None

    def as_html(self):
        return self.html

    def recursive_children(self, x):
        if "childGenerator" in dir(x):
            for child in x.childGenerator():
                name = getattr(child, "name", None)
                if name is not None:
                    name = name.lower()
                    self.tags.append(name)

                if name == "ul":
                    self.indent += 1
                    if len(self.tags) >= 2 and self.tags[-2] == "li":
                        self.text += "|/"
                elif name == "ol":
                    self.indent += 1
                    self.counters.append(1)
                    if len(self.tags) >= 2 and self.tags[-2] == "li":
                        self.text += "|/"
                elif name == "li":
                    if len(self.tags) == 1 or not self.tags[-2] == "ol":
                        self.text += "|/" + ("  " * self.indent) + "* "
                    else:
                        counter = self.counters[self.indent - 1]
                        self.text += "|/" + ("  " * self.indent) + "{}. ".format(counter)
                        self.counters[self.indent - 1] = counter + 1
                elif name == "p":
                    if len(self.tags) == 1 or not self.tags[-2] == "blockquote":
                        self.text += "|/"
                elif name == "pre":
                    self.text += "|/"
                elif name == "blockquote":
                    self.text += "|/> "

                self.recursive_children(child)

                if name is not None:
                    self.tags.pop()
                    if name == "ul":
                        self.text += "|/"
                        self.indent -= 1
                    elif name == "ol":
                        self.text += "|/"
                        self.indent -= 1
                        self.counters.pop()
                    elif name == "li":
                        self.text += "|/"
                    elif name == "p":
                        if len(self.tags) == 0 or not self.tags[-1] == "blockquote":
                            self.text += "|/"
                    elif name == "pre":
                        self.text += "|/"
                    elif name == "blockquote":
                        self.text += "|/"
                    elif name == "a":
                        href = child['href']
                        if href:
                            if self.text[-1] != ' ':
                                self.text += " "
                            self.text += "(" + href + ")"

        else:
            tag = self.tags[-1] if len(self.tags) > 0 else ""
            uptag = self.tags[-2] if len(self.tags) > 1 else ""
            if tag != "pre" and uptag != "pre":
                x = x.replace("\n", " ")
            if not x.isspace():
                if tag == "h1":
                    self.text += "|/|w" + x.upper() + "|n|/"
                elif tag in ["h2", "h3", "h4", "h5"]:
                    self.text += "|/|w" + x + "|n|/"
                elif tag == "em" or tag == "strong":
                    self.text += "|w" + x + "|n"
                else:
                    self.text += x

    def as_mush(self):

        if self.text is None:
            self.text = ""

            html = self.as_html()
            soup = BeautifulSoup(html, "html.parser")
            self.recursive_children(soup)

            text = self.text.strip()
            while text.rstrip().endswith("|/"):
                text = text.rstrip()[:-2]
            self.text = text + "|/"

        return self.text
