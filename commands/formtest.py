from .forms import PaxformCommand


class TestForm(paxform.Paxform):

    form_key = "testform"
    form_purpose = "Test Paxforms."
    form_description = "This command will test the Paxforms system."

    test_choice = [
        (1, "Choice1"),
        (2, "Choice2"),
        (3, "Choice3")
    ]

    one = paxfields.TextField(max_length=20, required=True, full_name="Field One")
    two = paxfields.IntegerField(min_value=10, max_value=30, default=15, full_name="Field Two")
    three = paxfields.BooleanField(required=True, default=False, full_name="Field Three")
    four = paxfields.ChoiceField(choices=test_choice, full_name = "Field Four")

    def submit(self, caller):
        caller.msg("Form submitted!  Values were: {}".format(self.serialize()))


class CmdTestForm(PaxformCommand):

    key = "@formtest"
    locks = "cmd:all()"

    form = TestForm()