

from textual.widgets import Static, Button, Switch, RadioSet
from textual.reactive import reactive
from textual.containers import Container
from textual.widget import Widget
from textual.message import Message

from .iclient import localtimestring

from .memberpn import SwitchMemberPane, TextMemberPane, LightMemberPane, NumberMemberPane, BlobMemberPane, NumberInputField, TextInputField, RadioMembers




class VectorTime(Static):

    DEFAULT_CSS = """
        VectorTime {
            margin-left: 1;
            margin-right: 1;
            width: auto;
        }
        """

    vtime = reactive("")


    def watch_vtime(self, vtime):
        if vtime:
            self.update(vtime)


class VectorState(Static):

    DEFAULT_CSS = """
        VectorState {
            margin-right: 1;
            width: auto;
            }
        """

    vstate = reactive("")

    def watch_vstate(self, vstate):
        if vstate == "Ok":
            self.styles.background = "darkgreen"
            self.styles.color = "white"
        elif vstate == "Alert":
            self.styles.background = "red"
            self.styles.color = "white"
        elif vstate == "Busy":
            self.styles.background = "yellow"
            self.styles.color = "black"
        elif vstate == "Idle":
            self.styles.background = "black"
            self.styles.color = "white"
        else:
            return
        self.update(vstate)



class VectorTimeState(Widget):

    DEFAULT_CSS = """
        VectorTimeState {
            layout: horizontal;
            align: right top;
            height: 1;
            }

        VectorTimeState > Static {
            width: auto;
            }
        """

    vtime = reactive("")
    vstate = reactive("")

    def compose(self):
        "Draw the timestamp and state"
        yield Static("State:")
        yield VectorTime().data_bind(VectorTimeState.vtime)
        yield VectorState().data_bind(VectorTimeState.vstate)


class VectorMessage(Static):

    DEFAULT_CSS = """
        VectorMessage {
            margin-left: 1;
            margin-right: 1;
            height: 2;
            }
        """

    vmessage = reactive("")

    def watch_vmessage(self, vmessage):
        if vmessage:
            self.update(vmessage)


class VectorPane(Widget):

    DEFAULT_CSS = """
        VectorPane {
            layout: vertical;
            height: auto;
            background: $panel;
            border: mediumvioletred;
            }
        """

    vtime = reactive("")
    vstate = reactive("")
    vmessage = reactive("")


    class ShowTimestamp(Message):

        def __init__(self, timestamp: str) -> None:
            self.timestamp = timestamp
            super().__init__()


    class ShowState(Message):

        def __init__(self, state: str) -> None:
            self.state = state
            super().__init__()


    class ShowVmessage(Message):

        def __init__(self, vmessage: str) -> None:
            self.vmessage = vmessage
            super().__init__()

    class SubmitButtonmessage(Message):

        def __init__(self, sbmessage: str) -> None:
            self.sbmessage = sbmessage
            super().__init__()


    def __init__(self, vector):
        "This VectorPane has attribute self.vector and id of the vectorid"
        self.vector = vector
        vectorid = self.app.itemid.set_id(vector.name)
        super().__init__(id=vectorid)


    def compose(self):
        "Draw the vector"
        self.border_title = self.vector.label

        self.vtime = localtimestring(self.vector.timestamp)
        self.vstate = self.vector.state

        vts = VectorTimeState()
        vts.data_bind(VectorPane.vtime)
        vts.data_bind(VectorPane.vstate)

        yield vts

        # create vector message
        if self.vector.message:
            self.vmessage = localtimestring(self.vector.message_timestamp) + "  " + self.vector.message

        yield VectorMessage().data_bind(VectorPane.vmessage)

        if self.vector.vectortype == "SwitchVector" and self.vector.rule == "OneOfMany":
            yield RadioVector(self.vector)
        elif self.vector.vectortype == "SwitchVector":
            yield SwitchVector(self.vector)
        elif self.vector.vectortype == "LightVector":
            yield LightVector(self.vector)
        elif self.vector.vectortype == "TextVector":
            yield TextVector(self.vector)
        elif self.vector.vectortype == "NumberVector":
            yield NumberVector(self.vector)
        elif self.vector.vectortype == "BLOBVector":
            yield BLOBVector(self.vector)


    def on_vector_pane_show_timestamp(self, message: ShowTimestamp) -> None:
        self.vtime = message.timestamp

    def on_vector_pane_show_state(self, message: ShowState) -> None:
        self.vstate = message.state

    def on_vector_pane_show_vmessage(self, message: ShowVmessage) -> None:
        self.vmessage = message.vmessage

    def on_vector_pane_submit_buttonmessage(self, message: SubmitButtonmessage) -> None:
        "Get the submit button status message, and update it"
        if self.vector.vectortype == "BLOBVector":
            # BLOB vectors do not have a submit button, so set message
            # in vector message space
            self.vmessage = message.sbmessage
            return
        vectorid = self.app.itemid.get_id(self.vector.name)
        buttonstatus = self.query_one(f"#{vectorid}_submitmessage")
        buttonstatus.update(message.sbmessage)




class SwitchVector(Widget):

    DEFAULT_CSS = """
        SwitchVector {
            height: auto;
            }
        SwitchVector > .submitbutton {
            layout: horizontal;
            align: right middle;
            height: auto;
            }
        SwitchVector > .submitbutton > Button {
            margin-right: 1;
            width: auto;
            }
        SwitchVector > .submitbutton > Static {
            margin-right: 4;
            width: auto;
            }

        """

    def __init__(self, vector):
        self.vector = vector
        super().__init__()

    def compose(self):
        "Draw the switch vector members"
        members = self.vector.members()
        # draw a switch for each vector member
        for member in members.values():
            yield SwitchMemberPane(self.vector, member)

        # After the switches, for rw or wo vectors, create a submit button

        if self.vector.perm != "ro":
            with Container(classes="submitbutton"):
                # create a static string with submit button
                # the string will hold any buttonstatus message required on an update being
                # submitted and will have id vectorid_submitmessage
                yield Static("", id=f"{self.app.itemid.get_id(self.vector.name)}_submitmessage")
                yield Button("Submit")


    def on_switch_changed(self, event):
        """Enforce the rule, OneOfMany AtMostOne AnyOfMany"""
        if self.vector.perm == "ro":
            # ignore switch changes for read only vectors
            return
        # clear buttonstatus message
        buttonstatus = self.query_one(f"#{self.app.itemid.get_id(self.vector.name)}_submitmessage")
        buttonstatus.update("")
        if self.vector.rule == "AnyOfMany":
            # No need to enforce this
            return
        if not event.value:
            # switch turned off
            return
        switches = self.query(Switch)
        for s in switches:
            if s is event.switch:
                # s is the switch changed
                continue
            if s.value:
                # any switch other than the one changed must be off
                s.value = False


    async def on_button_pressed(self, event):
        "Get membername:value dictionary and send it to the server"
        if self.vector.perm == "ro":
            # No submission for read only vectors
            return
        buttonstatus = self.query_one(f"#{self.app.itemid.get_id(self.vector.name)}_submitmessage")
        switchpanes = self.query(SwitchMemberPane)
        memberdict = {}
        for sp in switchpanes:
            membername = sp.member.name
            switch = sp.query_one(Switch)
            if switch.value:
                memberdict[membername] = "On"
            else:
                memberdict[membername] = "Off"
        # Check at least one pressed if rule is OneOfMany
        if self.vector.rule == "OneOfMany":
            oncount = list(memberdict.values()).count("On")
            if oncount != 1:
                buttonstatus.update("Invalid, OneOfMany rule requires one On switch")
                return
        # Check no more than one pressed if rule is AtMostOne
        if self.vector.rule == "AtMostOne":
            oncount = list(memberdict.values()).count("On")
            if oncount > 1:
                buttonstatus.update("Invalid, AtMostOne rule allows only one On switch")
                return
        # send this to the server
        buttonstatus.update("")
        # set state to busy
        self.parent.vstate = "Busy"
        await self.vector.send_newSwitchVector(members=memberdict)


class RadioVector(Widget):

    DEFAULT_CSS = """
        RadioVector {
            height: auto;
            }
        RadioVector > RadioMembers {
            layout: horizontal;
            align: center middle;
            height: auto;
            margin: 1;
            }
        RadioVector > .submitbutton {
            layout: horizontal;
            align: right middle;
            height: auto;
            }
        RadioVector > .submitbutton > Button {
            margin-right: 1;
            width: auto;
            }
        RadioVector > .submitbutton > Static {
            margin-right: 4;
            width: auto;
            }
        """


    def __init__(self, vector):
        self.vector = vector
        super().__init__()

    def compose(self):
        "Draw the radio buttons"
        # draw a radio button for each vector member
        yield RadioMembers( self.vector.members() )

        # After the switches, for rw or wo vectors, create a submit button

        if self.vector.perm != "ro":
            with Container(classes="submitbutton"):
                # create a static string with submit button
                # the string will hold any buttonstatus message required on an update being
                # submitted and will have id vectorid_submitmessage
                yield Static("", id=f"{self.app.itemid.get_id(self.vector.name)}_submitmessage")
                yield Button("Submit")


    async def on_button_pressed(self, event):
        "Get membername:value dictionary and send it to the server"
        if self.vector.perm == "ro":
            # No submission for read only vectors
            return
        buttonstatus = self.query_one(f"#{self.app.itemid.get_id(self.vector.name)}_submitmessage")
        radiobtns = self.query_one(RadioSet)
        pressed_index = radiobtns.pressed_index
        memberdict = {}
        members = self.vector.members()
        for idx, membername in enumerate(members.keys()):
            if idx == pressed_index:
                memberdict[membername] = "On"
            else:
                memberdict[membername] = "Off"
        # send this to the server
        buttonstatus.update("")
        # set state to busy
        self.parent.vstate = "Busy"
        await self.vector.send_newSwitchVector(members=memberdict)



class TextVector(Widget):

    DEFAULT_CSS = """
        TextVector {
            height: auto;
            }

        TextVector > .submitbutton {
            layout: horizontal;
            align: right middle;
            height: auto;
            }
        TextVector > .submitbutton > Button {
            margin-right: 1;
            width: auto;
            }
        TextVector > .submitbutton > Static {
            margin-right: 4;
            width: auto;
            }

        """

    def __init__(self, vector):
        self.vector = vector
        super().__init__()

    def compose(self):
        "Draw the number vector members"
        members = self.vector.members()
        for member in members.values():
            yield TextMemberPane(self.vector, member)

        if self.vector.perm != "ro":
            with Container(classes="submitbutton"):
                yield Static("", id=f"{self.app.itemid.get_id(self.vector.name)}_submitmessage")
                yield Button("Submit")

    async def on_button_pressed(self, event):
        "Get membername:value dictionary"
        if self.vector.perm == "ro":
            # No submission for read only vectors
            return
        buttonstatus = self.query_one(f"#{self.app.itemid.get_id(self.vector.name)}_submitmessage")
        textpanes = self.query(TextMemberPane)
        memberdict = {}
        for tp in textpanes:
            membername = tp.member.name
            textfield = tp.query_one(TextInputField)
            if textfield.placeholder:
                continue
            memberdict[membername] = textfield.value
        # send this to the server
        buttonstatus.update("")
        # set state to busy
        self.parent.vstate = "Busy"
        await self.vector.send_newTextVector(members=memberdict)



class LightVector(Widget):

    DEFAULT_CSS = """
        LightVector {
            height: auto;
            }
        """

    def __init__(self, vector):
        self.vector = vector
        super().__init__()

    def compose(self):
        "Draw the light vector"
        members = self.vector.members()
        for member in members.values():
            yield LightMemberPane(self.vector, member)


class NumberVector(Widget):

    DEFAULT_CSS = """
        NumberVector {
            height: auto;
            }

        NumberVector > .submitbutton {
            layout: horizontal;
            align: right middle;
            height: auto;
            }
        NumberVector > .submitbutton > Button {
            margin-right: 1;
            width: auto;
            }
        NumberVector > .submitbutton > Static {
            margin-right: 4;
            width: auto;
            }

        """

    def __init__(self, vector):
        self.vector = vector
        super().__init__()

    def compose(self):
        "Draw the number vector members"
        members = self.vector.members()
        for member in members.values():
            yield NumberMemberPane(self.vector, member)

        if self.vector.perm != "ro":
            with Container(classes="submitbutton"):
                yield Static("", id=f"{self.app.itemid.get_id(self.vector.name)}_submitmessage")
                yield Button("Submit")

    async def on_button_pressed(self, event):
        "Get membername:value dictionary"
        if self.vector.perm == "ro":
            # No submission for read only vectors
            return
        buttonstatus = self.query_one(f"#{self.app.itemid.get_id(self.vector.name)}_submitmessage")
        numberpanes = self.query(NumberMemberPane)
        memberdict = {}
        for np in numberpanes:
            membername = np.member.name
            numberfield = np.query_one(NumberInputField)
            if not numberfield.value:
                continue
            memberdict[membername] = numberfield.value
        # send this to the server
        buttonstatus.update("")
        # set state to busy
        self.parent.vstate = "Busy"
        await self.vector.send_newNumberVector(members=memberdict)



class BLOBVector(Widget):

    DEFAULT_CSS = """
        BLOBVector {
            height: auto;
            }
        """

    def __init__(self, vector):
        self.vector = vector
        super().__init__()

    def compose(self):
        "Draw the BLOB vector"
        members = self.vector.members()
        for member in members.values():
            yield BlobMemberPane(self.vector, member)
