import markdown2
from bs4 import BeautifulSoup


class MarkdownParser:

    def __init__(self):
        self.text = ""
        self.tags = []
        self.indent = 0

    def as_html(self, markdown_string):
        return markdown2.markdown(markdown_string)

    def recursive_children(self, x):
        if "childGenerator" in dir(x):
            for child in x.childGenerator():
                name = getattr(child, "name", None)
                if name is not None:
                    name = name.lower()
                    self.tags.append(name)

                if name == "ul":
                    self.indent += 1
                elif name == "li":
                    self.text += "|/" + ("  " * self.indent) + "* "
                elif name == "p":
                    if len(self.tags) == 1 or not self.tags[-2] == "blockquote":
                        self.text += "|/"
                elif name == "blockquote":
                    self.text += "|/> "

                self.recursive_children(child)

                if name is not None:
                    self.tags.pop()
                    if name == "ul":
                        self.text += "|/"
                        self.indent -= 1
                    elif name == "p":
                        if len(self.tags) == 0 or not self.tags[-1] == "blockquote":
                            self.text += "|/"
                    elif name == "blockquote":
                        self.text += "|/"

        else:
            x = x.replace("\n", " ")
            x = x.rstrip()
            if not x.isspace():
                tag = self.tags[-1] if len(self.tags) > 0 else ""
                if tag == "h1":
                    self.text += "|/|w" + x.upper() + "|n|/"
                elif tag in ["h2", "h3", "h4", "h5"]:
                    self.text += "|/|w" + x + "|n|/"
                elif tag == "em" or tag == "strong":
                    self.text += "|w" + x + "|n"
                else:
                    self.text += x + " "

    def as_mush(self, markdown_string):

        self.text = ""

        html = self.as_html(markdown_string)
        soup = BeautifulSoup(html, "html.parser")
        self.recursive_children(soup)

        return self.text
