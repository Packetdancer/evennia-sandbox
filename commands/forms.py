from paxforms import paxform
from paxforms import paxfields
from command import PaxCommand


class PaxformCommand(PaxCommand):

    form = None

    def __init__(self):
        super(PaxCommand, self).__init__()
        if not self.__doc__ or len(self.__doc__) == 0:
            self.__doc__ = self.__docstring

    @property
    def __docstring(self):
        cls = self.__class__
        if cls.form is None or not isinstance(cls.form, paxform.Paxform):
            return "Something has gone horribly wrong with this command, and we cannot generate a helpfile."
        result = "\n    "
        result += cls.form.form_purpose or "A useful command."
        result += "\n\n"
        result += "    Usage:\n"
        result += "      {}/create\n".format(cls.key)
        for f in cls.form.fields:
            result += "      {}/{} {}\n".format(cls.key, f.key, f.get_display_params())
        result += "      {}/cancel\n".format(cls.key)
        result += "      {}/submit\n".format(cls.key)
        result += "\n    {}\n".format(cls.form.form_description)
        return result

    def func(self):
        form = self.__class__.form
        if form is None or not isinstance(form, paxform.Paxform):
            self.msg("Form not provided to command!  Please contact your administrator.")
            return

        values = self.caller.attributes.get(form.key, default=None)
        form.deserialize(values)

        if "create" in self.switches:
            self.msg("Creating form...")
            self.caller.attributes.add(form.key, {})
            for f in form.fields:
                if f.get() is not None or f.required:
                    self.msg("|w{}:|n {}".format(f.full_name, str(f.get_display())))
            return

        if values is None:
            self.msg("No form in progress.  Please use {}/create first!".format(self.cmdstring))
            return

        if "cancel" in self.switches:
            if self.caller.attributes.get(form.key) is None:
                self.msg("No {} session was in progress to cancel.".format(self.cmdstring))
                return
            self.msg("Cancelled.")
            self.caller.attributes.remove(form.key)
            return

        if "submit" in self.switches:
            for f in form.fields:
                valid, reason = f.validate()
                if not valid:
                    self.msg(reason)
                    return

            form.submit()
            self.caller.attributes.remove(form.key)
            return

        if len(self.switches) > 0:
            f = form.field_for_key(self.switches[0])
            if not f:
                self.msg("Unknown switch {}".format(self.switches[0]))
                return

            if not self.args:
                f.set(None)
                self.msg("{} cleared.".format(f.full_name))
                return
            else:
                valid, reason = f.set(self.args)
                if not valid:
                    self.msg(reason)
                    return
                self.msg("{} set to: {}".format(f.full_name, self.args.strip(" ")))

            values = form.serialize()
            self.caller.attributes.add(form.key, values)

        else:
            for f in form.fields:
                if f.get() is not None or f.required:
                    self.msg("|w{}:|n {}".format(f.full_name, str(f.get_display())))
            return


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