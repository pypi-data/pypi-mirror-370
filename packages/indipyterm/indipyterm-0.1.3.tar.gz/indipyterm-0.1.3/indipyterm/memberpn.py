from rich.text import Text

from textual.widgets import Static, Button, Input, Switch, RadioButton, RadioSet
from textual.reactive import reactive
from textual.containers import Container
from textual.message import Message
from textual.widget import Widget
from textual.css.query import NoMatches

from decimal import Decimal

from indipyclient import getfloat

from .filechooser import ChooseFileSc


class TextLabel(Static):

    DEFAULT_CSS = """
        TextLabel {
            width: 1fr;
            height: 3;
            content-align: center middle;
        }
        """

class ROTextLabel(Static):

    DEFAULT_CSS = """
        ROTextLabel {
            width: 1fr;
            content-align: center middle;
        }
        """

class TextValue(Static):

    DEFAULT_CSS = """
        TextValue {
            width: 1fr;
        }
        """


class ShowText(Container):

    DEFAULT_CSS = """
        ShowText {
            layout: vertical;
            width: 2fr;
            height: auto;
            }

        TextValue {
            width: 1fr;
            padding: 1;
            }

        .textinput {
            layout: horizontal;
            height: auto;
            }

        Button {
            width: auto;
            height: auto;
            }

        """


    def __init__(self, member):
        self.member = member
        super().__init__()

    def compose(self):
        # permission is wo or rw, so show value with editing capbility
        yield TextValue(self.member.membervalue)
        with Container(classes="textinput"):
            yield TextInputField(self.member)
            yield Button("Clear")



class TextMemberPane(Widget):

    DEFAULT_CSS = """
        TextMemberPane {
            layout: horizontal;
            background: $panel;
            margin-left: 1;
            margin-bottom: 1;
            height: auto;
            }
        """

    class SetValue(Message):

        def __init__(self, value):
            self.value = value
            super().__init__()

    def __init__(self, vector, member):
        self.member = member
        self.vector = vector
        member_id = self.app.itemid.set_id(vector.name, member.name)
        super().__init__(id=member_id)


    def compose(self):
        "Draw the member"
        if self.vector.perm == "ro":
            yield ROTextLabel(self.member.label)
            yield TextValue(self.member.membervalue)
            return
        yield TextLabel(self.member.label)
        yield ShowText(self.member)


    def on_text_member_pane_set_value(self, message: SetValue) -> None:
        showtextvalue = self.query_one(TextValue)
        showtextvalue.update(message.value)

    def on_button_pressed(self, event):
        "Clear text input field"
        infld = self.query_one(TextInputField)
        infld.placeholder="Input new text"
        infld.clear()
        event.stop()


class TextInputField(Input):

    DEFAULT_CSS = """
        TextInputField {
            width: 1fr;
            }
        """

    def __init__(self, member):
        self.member = member
        super().__init__(placeholder="Input new text")

    def on_blur(self, event):
        # self.value is the new value input
        if self.value.isprintable():
            checkedvalue = self.value
        else:
            checkedvalue = "Invalid string"
        self.clear()
        self.insert_text_at_cursor(checkedvalue)

    def on_key(self, event):
        if event.character is None:
            return
        # a printable key is pressed
        self.placeholder=""

    def action_submit(self):
        self.screen.focus_next('*')


class LightLabel(Static):

    DEFAULT_CSS = """
        LightLabel {
            width: 1fr;
            height: 3;
            content-align: center middle;
        }
        """

class LightValue(Static):

    DEFAULT_CSS = """
        LightValue {
            padding: 1;
            width: auto;
            height: auto;
        }
        """

    mvalue = reactive("")


    def watch_mvalue(self, mvalue):
        if mvalue:
            if mvalue == "Ok":
                self.styles.background = "darkgreen"
                self.styles.color = "white"
            elif mvalue == "Alert":
                self.styles.background = "red"
                self.styles.color = "white"
            elif mvalue == "Busy":
                self.styles.background = "yellow"
                self.styles.color = "black"
            elif mvalue == "Idle":
                self.styles.background = "black"
                self.styles.color = "white"
            else:
                mvalue = "?"
                self.styles.background = "black"
                self.styles.color = "white"
            self.update(mvalue)


class LightMemberPane(Widget):

    DEFAULT_CSS = """
        LightMemberPane {
            layout: horizontal;
            background: $panel;
            margin-left: 1;
            margin-bottom: 1;
            height: auto;
        }

        LightMemberPane > Container {
            width: 1fr;
            height: auto;
            align: center middle;
            }
        """

    class SetValue(Message):

        def __init__(self, value):
            self.value = value
            super().__init__()

    mvalue = reactive("")

    def __init__(self, vector, member):
        self.member = member
        self.vector = vector
        member_id = self.app.itemid.set_id(vector.name, member.name)
        super().__init__(id=member_id)


    def compose(self):
        "Draw the member"

        if self.member.membervalue:
            self.mvalue = self.member.membervalue

        yield LightLabel(self.member.label)
        with Container():
            yield LightValue().data_bind(LightMemberPane.mvalue)

    def on_light_member_pane_set_value(self, message: SetValue) -> None:
        self.mvalue = message.value


class NumberLabel(Static):

    DEFAULT_CSS = """
        NumberLabel {
            width: 1fr;
            height: 3;
            content-align: center middle;
        }
        """

class NumberValue(Static):

    DEFAULT_CSS = """
        NumberValue {
            width: 1fr;
            height: 3;
            content-align: center middle;
        }
        """

    mvalue = reactive("")

    def watch_mvalue(self, mvalue):
        if mvalue:
            self.update(mvalue)


class NumberMemberPane(Widget):

    DEFAULT_CSS = """
        NumberMemberPane {
            layout: horizontal;
            background: $panel;
            margin-left: 1;
            margin-bottom: 1;
            height: auto;
            }

        NumberMemberPane > Container {
            layout: horizontal;
            width: 2fr;
            height: auto;
            align: center middle;
            }
        """

    class SetValue(Message):

        def __init__(self, value):
            self.value = value
            super().__init__()

    mvalue = reactive("")

    def __init__(self, vector, member):
        self.member = member
        self.vector = vector
        member_id = self.app.itemid.set_id(vector.name, member.name)
        super().__init__(id=member_id)


    def compose(self):
        "Draw the member"
        self.mvalue = self.member.getformattedvalue()
        yield NumberLabel(self.member.label)
        yield NumberValue().data_bind(NumberMemberPane.mvalue)
        if self.vector.perm != "ro":
            with Container():
                yield NumberInputField(self.member, placeholder="Input new number")
                yield Button("Clear")

    def on_button_pressed(self, event):
        "Clear number input field"
        infld = self.query_one(NumberInputField)
        infld.clear()
        event.stop()

    def on_number_member_pane_set_value(self, message: SetValue) -> None:
        self.mvalue = message.value



class NumberInputField(Input):

    DEFAULT_CSS = """

        NumberInputField {
            width: 1fr;
            }
        """

    def __init__(self, member, placeholder):
        self.member = member
        super().__init__(placeholder=placeholder)

    def on_blur(self, event):
        # self.value is the new value input
        if not self.value:
            return
        try:
            newfloat = getfloat(self.value)
        except (ValueError, TypeError):
            self.clear()
            checkedvalue = self.member.getformattedvalue()
            self.insert_text_at_cursor(checkedvalue)
            return
        # check step, and round newfloat to nearest step value
        stepvalue = getfloat(self.member.step)
        minvalue = getfloat(self.member.min)
        if stepvalue:
            stepvalue = Decimal(str(stepvalue))
            difference = newfloat - minvalue
            newfloat = minvalue + float(int(Decimal(str(difference)) / stepvalue) * stepvalue)
        # check not less than minimum
        if newfloat < minvalue:
            # reset input to be the minimum, and accept this
            self.clear()
            checkedvalue = self.member.getformattedstring(minvalue)
            self.insert_text_at_cursor(checkedvalue)
            return
        if self.member.max != self.member.min:
            maxvalue = getfloat(self.member.max)
            if newfloat > maxvalue:
                # reset input to be the maximum, and accept this
                self.clear()
                checkedvalue = self.member.getformattedstring(maxvalue)
                self.insert_text_at_cursor(checkedvalue)
                return
        # reset input to the correct format, and accept this
        self.clear()
        checkedvalue = self.member.getformattedstring(newfloat)
        self.insert_text_at_cursor(checkedvalue)


    def action_submit(self):
        self.screen.focus_next('*')



class BLOBLabel(Static):

    DEFAULT_CSS = """
        BLOBLabel {
            width: 1fr;
            content-align: center middle;
        }
        """

class BLOBRxValue(Static):

    DEFAULT_CSS = """
        BLOBRxValue {
            width: 2fr;
        }
        """

    mvalue = reactive("")

    def watch_mvalue(self, mvalue):
        if mvalue:
            self.update(f"RX data: {mvalue}")


class BLOBTxValue(Static):

    DEFAULT_CSS = """
        BLOBTxValue {
            width: 2fr;
        }
        """


class BlobMemberPane(Widget):

    DEFAULT_CSS = """
        BlobMemberPane {
            layout: horizontal;
            background: $panel;
            margin-left: 1;
            margin-bottom: 1;
            height: auto;
            }

        BlobMemberPane > Container {
            layout: vertical;
            background: $panel;
            width: 2fr;
            height: auto;
            }

        Button {
            margin: 1;
            width: auto;
            height: auto;
            }
        """

    class SetValue(Message):

        def __init__(self, value):
            self.value = value
            super().__init__()

    mvalue = reactive("")

    def __init__(self, vector, member):
        self.member = member
        self.vector = vector
        member_id = self.app.itemid.set_id(vector.name, member.name)
        super().__init__(id=member_id)


    def compose(self):
        "Draw the member"
        yield BLOBLabel(self.member.label)
        # The last filename sent is stored in the member user string
        last_filename = self.member.user_string
        with Container():
            if self.vector.perm == "wo":
                yield BLOBRxValue("RX data: N/A -- Write only --").data_bind(BlobMemberPane.mvalue)
            elif not self.app.blobfolder:
                yield BLOBRxValue("RX data: -- BLOB Folder not set --").data_bind(BlobMemberPane.mvalue)
            elif not self.member.filename:
                yield BLOBRxValue("RX data: -- Nothing yet received --").data_bind(BlobMemberPane.mvalue)
            else:
                yield BLOBRxValue(f"RX data: {self.member.filename}").data_bind(BlobMemberPane.mvalue)
            if self.vector.perm == "ro":
                yield BLOBTxValue("TX data: N/A -- Read only --")
            elif last_filename:
                yield BLOBTxValue(f"TX data: {last_filename}")
                yield Button("Send File")
            else:
                yield BLOBTxValue("TX data: -- No file sent --")
                yield Button("Send File")


    def on_blob_member_pane_set_value(self, message: SetValue) -> None:
        self.mvalue = message.value


    async def on_button_pressed(self, event):
        "Open file chooser screen"
        async def send_path(path):
            if path is not None:
                # memberdict of {membername:(value, blobsize, blobformat)}
                await self.vector.send_newBLOBVector(members={self.member.name:(path, 0, "")})
                self.member.user_string = path.name
                path_text = self.query_one(BLOBTxValue)
                path_text.update(f"TX data: {path.name}")
                # set state to busy
                self.parent.parent.vstate = "Busy"
        self.app.push_screen(ChooseFileSc(), send_path)
        event.stop()



class SwitchLabel(Static):

    DEFAULT_CSS = """
        SwitchLabel {
            width: 1fr;
            height: 3;
            content-align: center middle;
        }
        """


class SwitchValue(Static):

    DEFAULT_CSS = """
        SwitchValue {
            width: auto;
            padding: 1;
            height: auto;
            }
        """

    mvalue = reactive("")

    def watch_mvalue(self, mvalue):
        if mvalue:
            if mvalue == "On":
                self.styles.background = "darkgreen"
                self.styles.color = "white"
            elif mvalue == "Off":
                self.styles.background = "red"
                self.styles.color = "white"
            else:
                mvalue = "?"
                self.styles.background = "black"
                self.styles.color = "white"
            self.update(mvalue)



class SwitchMemberPane(Widget):

    DEFAULT_CSS = """
        SwitchMemberPane {
            layout: horizontal;
            background: $panel;
            margin-left: 1;
            margin-bottom: 1;
            height: auto;
        }

        SwitchMemberPane > Container {
            width: 1fr;
            height: auto;
            align: center middle;
        }
        """

    class SetValue(Message):

        def __init__(self, value):
            self.value = value
            super().__init__()

    mvalue = reactive("")

    def __init__(self, vector, member):
        self.member = member
        self.vector = vector
        member_id = self.app.itemid.set_id(vector.name, member.name)
        super().__init__(id=member_id)


    def compose(self):
        "Draw the member"
        if self.member.membervalue:
            self.mvalue = self.member.membervalue

        yield SwitchLabel(self.member.label)
        with Container():
            yield SwitchValue().data_bind(SwitchMemberPane.mvalue)
        with Container():
            if self.member.membervalue == "On":
                if self.vector.perm == "ro":
                    yield Switch(value=True, disabled=True)
                else:
                    yield Switch(value=True)
            else:
                if self.vector.perm == "ro":
                    yield Switch(value=False, disabled=True)
                else:
                    yield Switch(value=False)

    def watch_mvalue(self, mvalue):
        "Alter switches as values received"
        # The displayed SwitchValue will automatically follow mvalue
        # so does not have to be set here.
        # However the switch objects are set here as values are received
        # from iclient
        if self.vector.perm != "ro":
            return
        # Only bother changing switch states if ro
        if not  mvalue:
            return
        try:
            switch = self.query_one(Switch)
        except NoMatches:
            # presumably this vector has not been displayed yet
            return
        if mvalue == "On":
            switch.value = True
        else:
            switch.value = False

    def on_switch_member_pane_set_value(self, message: SetValue) -> None:
        self.mvalue = message.value


class RadioMembers(Container):

    DEFAULT_CSS = """
        RadioMembers > RadioSet {
            background: $panel;
            }
        RadioMembers > RadioSet > RadioButton {
            margin: 1;
            }
        """

    class ResetValue(Message):
        pass


    # this boolean value is toggled to initiate a recompose
    mvalue = reactive(False, recompose=True)

    def __init__(self, members):
        self.members = members
        super().__init__()

    def compose(self):
        "Draw the radio buttons"
        with RadioSet():
            for member in self.members.values():
                if member.membervalue == "On":
                    chosenlabel = Text.from_markup(f"{member.label} :green_circle:")
                    yield RadioButton(chosenlabel, value=True)
                else:
                    yield RadioButton(member.label)

    def on_radio_members_reset_value(self, message: ResetValue) -> None:
        # Toggle mvalue to cause a recompose of the RadioMembers
        self.mvalue = not self.mvalue
