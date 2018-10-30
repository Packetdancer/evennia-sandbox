from paxforms.commands import PaxformCommand
from .form import TestForm


class CmdTestForm(PaxformCommand):

    key = "@formtest"
    locks = "cmd:all()"
    form_class = TestForm

    def func(self):
        if "htmlform" in self.switches:
            webform = self.form.web_form
            current_values = self.form.serialize()
            webform_instance = webform(initial=current_values)
            self.msg(webform_instance)
            return

        super(CmdTestForm,self).func()
