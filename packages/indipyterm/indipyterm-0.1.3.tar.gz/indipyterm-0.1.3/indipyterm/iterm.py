
import pathlib

from textual.app import App
from textual import on
from textual.app import ComposeResult
from textual.widgets import Footer, Static, Button, Log, Input
from textual.screen import Screen
from textual.containers import Container, HorizontalScroll, VerticalScroll, Center, Horizontal
from textual.message import Message

from .iclient import ItemID, IClient, localtimestring

from .devicesc import DeviceSc

version = "0.1.3"



class DevicePane(VerticalScroll):

    DEFAULT_CSS = """

            DevicePane {
                width: 30%;
                background: $panel;
                border: dodgerblue;
                }

            DevicePane > Static {
                background: $boost;
                color: auto;
                margin-bottom: 1;
                padding: 1;
                }

             DevicePane > Button {
                width: 100%;
                }
        """

    class NewButton(Message):
        """Add a new button."""

        def __init__(self, devicename: str) -> None:
            self.devicename = devicename
            super().__init__()

    class ClearDevices(Message):
        pass

    class DelButton(Message):
        """Delete a button."""

        def __init__(self, deviceid: str) -> None:
            self.deviceid = deviceid
            super().__init__()

    def compose(self):
        self.border_title = "Devices"
        if self.app.indiclient is None:
            devices = 0
        else:
            devices = self.app.indiclient.enabledlen()
        # The number of enabled devices
        if not devices:
            yield Static("No Devices found", id="no-devices")
        else:
            for devicename in self.app.indiclient:
                deviceid = self.app.itemid.set_devicid(devicename)
                yield Button(devicename, variant="primary", classes="devices", id=deviceid)


    def on_device_pane_new_button(self, message: NewButton) -> None:
        devicename = message.devicename
        deviceid = self.app.itemid.set_devicid(devicename)
        self.remove_children("#no-devices")
        self.mount(Button(devicename, variant="primary", classes="devices", id=deviceid))

    def on_device_pane_clear_devices(self, message: ClearDevices) -> None:
        if self.query(".devices"):
            self.remove_children(".devices")
            self.mount(Static("No Devices found", id="no-devices"))

    def on_device_pane_del_button(self, message: DelButton) -> None:
        deviceid = message.deviceid
        self.remove_children(f"#{deviceid}")


    @on(Button.Pressed, ".devices")
    def choose_device(self, event):
        "Choose device from the button pressed"
        iclient = self.app.indiclient
        if iclient is None:
            return
        devicename = self.app.itemid.get_devicename(event.button.id)
        if not devicename:
            return
        if devicename not in iclient:
            # An unknown device
            return
        if not iclient[devicename].enable:
            # This device is disabled
            return
        # create a device screen, and store a reference to it
        # in the indiclient 'cliendata' dictionary
        iclient.clientdata['devicesc'] = DeviceSc(devicename)
        # push the devicesc to the top of the stack
        self.app.push_screen(iclient.clientdata['devicesc'])


class BlobPane(HorizontalScroll):

    DEFAULT_CSS = """

        BlobPane {
            height: 40%;
            min-height: 8;
            background: $panel;
            border: greenyellow;
            }

        BlobPane > #blob-input {
            margin: 1;
            }


        """

    def compose(self):
        self.border_title = "Set BLOB folder"
        yield BlobInput(placeholder="Set a Folder to receive BLOBs", id="blob-input")

    def on_mount(self):
        iclient = self.app.indiclient
        if iclient is None:
            self.border_subtitle = "Received BLOBs disabled"
            return
        if iclient.BLOBfolder:
            self.border_subtitle = "Received BLOBs enabled"
        else:
            self.border_subtitle = "Received BLOBs disabled"


class BlobInput(Input):

    def on_mount(self):
        if self.app.blobfolder:
            self.insert_text_at_cursor(str(self.app.blobfolder))

    def on_blur(self, event):
        iclient = self.app.indiclient
        if not self.value:
            self.app.blobfolder = None
            if iclient is not None:
                iclient.BLOBfolder = None
            self.clear()
            self.insert_text_at_cursor('')
            self.parent.border_subtitle = "Received BLOBs disabled"
            return

        blobfolder = pathlib.Path(self.value).expanduser().resolve()
        if not blobfolder.is_dir():
            self.app.blobfolder = None
            if iclient is not None:
                iclient.BLOBfolder = None
            self.clear()
            self.insert_text_at_cursor('Invalid Folder')
            self.parent.border_subtitle = "Received BLOBs disabled"
            return

        self.app.blobfolder = blobfolder
        if iclient is not None:
            iclient.BLOBfolder = blobfolder
        self.clear()
        self.insert_text_at_cursor(str(blobfolder))
        self.parent.border_subtitle = "Received BLOBs enabled"


    def action_submit(self):
        self.screen.focus_next('*')



class MessagesPane(Container):

    DEFAULT_CSS = """

        MessagesPane {
            width: 100%;
            background: $panel;
            border: mediumvioletred;
            }

        MessagesPane > Log {
            width: 100%;
            background: $panel;
            scrollbar-background: $panel;
            scrollbar-corner-color: $panel;
            }
        """

    class ShowLogs(Message):
        """pass messages to the pane."""

        def __init__(self, messagelog: str) -> None:
            self.messagelog = messagelog
            super().__init__()

    def compose(self):
        self.border_title = "System Messages"
        yield Log(id="system-messages")

    def on_messages_pane_show_logs(self, message: ShowLogs) -> None:
        log = self.query_one("#system-messages")
        if log.line_count < 32:
            log.write_line(message.messagelog)
            return
        # if greater than 32, clear logs, and show the last eight
        # stored as a deque in indiclient
        log.clear()
        if self.app.indiclient is not None:
            messages = list(self.app.indiclient.messages)
            mlist = reversed([ localtimestring(t) + "  " + m for t,m in messages ])
            log.write_lines(mlist)



class ConnectionPane(Container):

    DEFAULT_CSS = """

        ConnectionPane {
            height: 60%;
            min-height: 12;
            background: $panel;
            border: mediumvioletred;
            align: center middle;
            }

        ConnectionPane > Static {
            margin: 1;
            }
        """


    def compose(self):
        self.border_title = "Set INDI Server"
        con_input = ConInput(placeholder="Host:Port", id="con-input")
        con_status = Static("Host:Port not set", id="con-status")
        con_button = Button("Connect", id="con-button")
        if self.app.indiclient is None:
            # No indiclient exists, enable the input field to accept a host and port
            con_input.disabled = False
            con_button.label = "Connect"
            if (not self.app.indihost) or (not self.app.indiport):
                con_status.update("Host:Port not set")
                con_button.disabled = True
            else:
                con_status.update(f"Current server : {self.app.indihost}:{self.app.indiport}")
                con_button.disabled = False
        else:
            # An indiclient instance exists, disable the input field
            # and set the button to 'Disconnect"
            con_input.disabled = True
            con_status.update(f"Current server : {self.app.indiclient.indihost}:{self.app.indiclient.indiport}")
            con_button.label = "Disconnect"
            con_button.disabled = False
        yield con_input
        yield con_status
        with Center():
            yield con_button


    async def on_button_pressed(self, event):
        con_input = self.query_one("#con-input")
        con_status = self.query_one("#con-status")
        con_button = self.query_one("#con-button")
        if self.app.indiclient is None:
            # call for connection
            # create an indiclient
            self.app.indiclient = IClient(indihost=self.app.indihost, indiport=self.app.indiport, app=self.app)
            if self.app.blobfolder:
                self.app.indiclient.BLOBfolder = self.app.blobfolder
            con_input.disabled = True
            con_status.update(f"Current server : {self.app.indiclient.indihost}:{self.app.indiclient.indiport}")
            con_button.label = "Disconnect"
            con_button.disabled = False
            # clear the messages pane
            mess_pane = self.parent.query_one("#sys-messages-pane")
            log = mess_pane.query_one("#system-messages")
            log.clear()
            # and run indiclient.asyncrun()
            self.app.run_worker(self.app.indiclient.asyncrun(), exclusive=True)
        else:
            # call for disconnection
            self.app.indiclient.shutdown()
            # and wait for it to shutdown
            await self.app.indiclient.stopped.wait()
            self.app.indiclient = None
            con_input.disabled = False
            con_status.update("Host:Port not set")
            con_button.label = "Connect"
            if (not self.app.indihost) or (not self.app.indiport):
                con_status.update("Host:Port not set")
                con_button.disabled = True
            else:
                con_status.update(f"Current server : {self.app.indihost}:{self.app.indiport}")
                con_button.disabled = False
            # clear the list of device buttons
            device_pane = self.parent.query_one("#device-pane")
            if device_pane.query(".devices"):
                device_pane.remove_children(".devices")
                device_pane.mount(Static("No Devices found", id="no-devices"))
            # clear the messages pane, leving a single 'DISCONNECTED' message
            mess_pane = self.parent.query_one("#sys-messages-pane")
            log = mess_pane.query_one("#system-messages")
            log.clear()
            log.write_line("DISCONNECTED")
            # and clear all item id's
            self.app.itemid.clear()



class ConInput(Input):

    def on_blur(self, event):

        hostport = self.value.strip()
        if hostport:
            hostportlist = hostport.split(":")
            if len(hostportlist) == 2:
                host = hostportlist[0].strip()
                port = hostportlist[1].strip()
                if not host:
                    host = "localhost"
                if not port.isdigit():
                    port = "7624"
                hostport = f"{host}:{port}"
            else:
                host = hostportlist[0].strip()
                if host:
                    hostport = host +":7624"
                else:
                    hostport = "localhost:7624"
        else:
            hostport = "localhost:7624"
        self.clear()
        self.insert_text_at_cursor(hostport)
        # set this new host and port into self.app.indihost, self.app.indiport
        self.app.indihost, self.app.indiport = hostport.split(":")
        # and enable the connection button
        con_button = self.parent.query_one("#con-button")
        con_button.disabled = False

    def action_submit(self):
        self.screen.focus_next('*')





class StartSc(Screen):
    """The top start screen."""

    DEFAULT_CSS = """


        StartSc > #title {
           background: $primary;
           color: $text;
           padding-left: 2;
           dock: top;
           }

        StartSc > #startsc-grid {
            height: 70%;
            }

        StartSc > #sys-messages-pane {
            height: 30%;
           }


        """
    ENABLE_COMMAND_PALETTE = False

    def __init__(self):
        super().__init__()


    def compose(self) -> ComposeResult:
        yield Static(f"INDI Terminal {version}", id="title")
        with Horizontal(id="startsc-grid"):
            yield DevicePane(id="device-pane")
            with VerticalScroll(id="startsc-v"):
                yield ConnectionPane(id="con-pane")
                yield BlobPane(id="blob-pane")
        yield MessagesPane(id="sys-messages-pane")
        yield Footer()


class IPyTerm(App):
    """An INDI terminal."""

    SCREENS = {"startsc": StartSc}

    BINDINGS = [("q", "quit", "Quit"), ("d", "toggle_dark", "Toggle dark mode")]

    ENABLE_COMMAND_PALETTE = False

    def __init__(self, host="localhost", port=7624, blobfolder=None):
        self.indihost = host
        self.indiport = port
        if blobfolder:
            bf = pathlib.Path(blobfolder).expanduser().resolve()
            if bf.is_dir():
                self.blobfolder = bf
            else:
                self.blobfolder = None
        else:
            self.blobfolder = None
        self.itemid = ItemID()
        self.indiclient = IClient(indihost=host, indiport=port, app=self)
        if self.blobfolder:
            self.indiclient.BLOBfolder = self.blobfolder
        super().__init__()


    def on_mount(self) -> None:
        """Start the worker which runs self.indiclient.asyncrun()
           and show the start screen"""
        self.push_screen('startsc')
        self.run_worker(self.indiclient.asyncrun(), exclusive=True)



    async def action_quit(self) -> None:
        """An action to quit the program."""
        if self.indiclient is not None:
            self.indiclient.shutdown()
            # and wait for it to shutdown
            await self.indiclient.stopped.wait()
        self.exit(0)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
            )
