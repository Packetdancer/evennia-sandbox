from paxforms.commands import PaxformCommand
from paxforms import forms, fields


class TestForm(forms.Paxform):

    form_key = "testform"
    form_purpose = "Test Paxforms."
    form_description = '''
    This form will test the Paxforms system.  The fields are largely meaningless, 
    they're just examples of a TextField (one), IntegerField (two), BooleanField
    (three), and ChoiceField (four).
    '''

    test_choice = [
        (1, "Choice1"),
        (2, "Choice2"),
        (3, "Choice3")
    ]

    one = fields.TextField(max_length=20, required=True, full_name="Field One")
    two = fields.IntegerField(min_value=10, max_value=30, default=15, full_name="Field Two")
    three = fields.BooleanField(required=True, default=False, full_name="Field Three")
    four = fields.ChoiceField(choices=test_choice, full_name = "Field Four")

    def submit(self, caller, values):
        caller.msg("Form submitted!  Values were: {}".format(values))


class CmdTestForm(PaxformCommand):

    key = "@formtest"
    locks = "cmd:all()"
    form_class = TestForm

    def func(self):
        if "htmlform" in self.switches:
            webform = self.form.web_form
            self.msg(webform)
            return

        super(CmdTestForm,self).func()
