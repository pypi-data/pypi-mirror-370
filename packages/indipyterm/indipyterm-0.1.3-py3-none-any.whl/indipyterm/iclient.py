
import logging

import indipyclient as ipc


logger = logging.getLogger()
logger.addHandler(logging.NullHandler())



def localtimestring(t):
    "Return a string of the local time (not date)"
    localtime = t.astimezone(tz=None)
    # convert microsecond to integer between 0 and 100
    ms = localtime.microsecond//10000
    return f"{localtime.strftime('%H:%M:%S')}.{ms:0>2d}"



class ItemID():

    def __init__(self):
        self._itemdict = {}
        self._groupdict = {}
        # Every device, vector, widget will be given an id
        # starting with characters 'id' followed by a string number
        # created by incrementing this self._itemid
        self._itemid = 0

        # devicename needs to be set
        self.devicename = None

    def __bool__(self):
        return bool(self._itemdict)

    def get_group_id(self, groupname):
        if self.devicename is None:
            return
        if not groupname:
            raise KeyError("A group name must be given to get a group id")
        idnumber = self._groupdict.get((self.devicename, groupname))
        if idnumber is None:
            return
        return "gid"+str(idnumber)


    def set_group_id(self, groupname):
        if self.devicename is None:
            return
        if not groupname:
            raise KeyError("A group name must be given to set a group id")
        idnumber = self._groupdict.get((self.devicename, groupname))
        if idnumber is None:
            self._itemid += 1
            self._groupdict[self.devicename, groupname] = self._itemid
            return "gid"+str(self._itemid)
        return "gid"+str(idnumber)


    def unset_group(self, devicename, groupname):
        if not devicename:
            raise KeyError("A devicename must be given to unset a group id")
        if not groupname:
            raise KeyError("A group name must be given to unset a group id")
        self._groupdict[devicename, groupname] = None


    def get_id(self, vectorname=None, membername=None):
        if self.devicename is None:
            return
        if not vectorname:
            vectorname = None
        if not membername:
            membername = None
        if membername and (not vectorname):
            raise KeyError("If a membername is specified, a vectorname must also be given")
        idnumber = self._itemdict.get((self.devicename, vectorname, membername))
        if idnumber is None:
            return
        return "id"+str(idnumber)


    def set_id(self, vectorname=None, membername=None):
        "This create ids for widgets, and returns the id"
        if self.devicename is None:
            return
        if not vectorname:
            vectorname = None
        if not membername:
            membername = None
        if membername and (not vectorname):
            raise KeyError("If a membername is specified, a vectorname must also be given")
        idnumber = self._itemdict.get((self.devicename, vectorname, membername))
        if idnumber is None:
            self._itemid += 1
            self._itemdict[self.devicename, vectorname, membername] = self._itemid
            return "id"+str(self._itemid)
        return "id"+str(idnumber)


    def unset(self, devicename, vectorname=None, membername=None):
        if not vectorname:
            vectorname = None
        if not membername:
            membername = None
        if not devicename:
            raise KeyError("A devicename must be given to unset an id")
        if membername and (not vectorname):
            raise KeyError("If a membername is specified, a vectorname must also be given")
        self._itemdict[devicename, vectorname, membername] = None


    def get_devicid(self, devicename):
        if devicename is None:
            return
        idnumber = self._itemdict.get((devicename, None, None))
        if idnumber is None:
            return
        return "id"+str(idnumber)


    def set_devicid(self, devicename):
        "This create id for a device"
        if devicename is None:
            return
        idnumber = self._itemdict.get((devicename, None, None))
        if idnumber is None:
            self._itemid += 1
            self._itemdict[devicename, None, None] = self._itemid
            return "id"+str(self._itemid)
        return "id"+str(idnumber)


    def clear_device(self, device):
        "clear the id's of device, and its vectors and members"
        self.unset(device.devicename)
        for vectorname in device:
            self.unset(device.devicename, vectorname)
            self.unset_group(device.devicename, device[vectorname].group)
            membernamelist = list(device[vectorname].keys())
            for membername in membernamelist:
                self.unset(device.devicename, vectorname, membername)


    def clear_vector(self, vector):
        "delete the ids of the vector and all its members"
        self.unset(vector.devicename, vector.name)
        membernamelist = list(vector.keys())
        for membername in membernamelist:
            self.unset(vector.devicename, vector.name, membername)


    def get_devicename(self, deviceid):
        "Given an id, get the devicename, or return None if it does not exist"
        idnumber = int(deviceid.strip("id"))
        for key,value in self._itemdict.items():
            if value == idnumber:
                return key[0]

    def clear(self):
        self._itemdict.clear()
        self._groupdict.clear()
        self._itemid = 0



class IClient(ipc.IPyClient):

    async def rxevent(self, event):
        app = self.clientdata['app']
        startsc = app.get_screen('startsc')

        # if the connection is failed
        # ensure the startsc is being shown
        # and all device and vector id's are cleared

        if (not self.connected) and app.itemid :
            # the connection is disconnected
            if not startsc.is_active:
                app.push_screen('startsc')
            device_pane = startsc.query_one("#device-pane")
            device_pane.post_message(device_pane.ClearDevices())
            app.itemid.clear()
            self.clientdata['devicesc'] = None

        # handle received events affecting startsc ################################

        if (event.eventtype == "Define" or event.eventtype == "DefineBLOB"):
            # does this device have an id
            devicename = event.devicename
            if not app.itemid.get_devicid(devicename):
                # it doesn't, so add a button to the devicepane of startsc
                device_pane = startsc.query_one("#device-pane")
                device_pane.post_message(device_pane.NewButton(devicename))
                # As this is a new device, its devicesc cannot be currently showing,
                # but a message can be added to the device, which will appear on devicesc
                event.device.messages.appendleft( (event.timestamp, f"Device discovered: {devicename}") )
                return

            # this devicename already exists, but the Define event will be
            # adding a vector so that is still to do

        if (event.eventtype == "Message") and (not event.devicename):
            # This is a system message and should be added to the messages pane of startsc
            if event.message:
                messagelog = localtimestring(event.timestamp) + "  " + event.message
                messages_pane  = startsc.query_one("#sys-messages-pane")
                messages_pane.post_message(messages_pane.ShowLogs(messagelog))
            # As a system message, there is no change to a devicesc, so nothing further to do
            return

        if (event.eventtype == "Delete") and (not self[event.devicename].enable):
            # As the device has enable False, this Delete event is either requesting an entire
            # device delete, or the last vector of this device is deleted. In either
            # case, this entire device should be deleted
            deviceid = app.itemid.get_devicid(event.devicename)
            if not deviceid:
                # This device is not displayed, nothing to do
                return
            # instruct the startsc to remove the device button
            device_pane = startsc.query_one("#device-pane")
            device_pane.post_message(device_pane.DelButton(deviceid))
            if event.message:
                # show this message as a system message, as there is no device
                # so there is nowhere else to show it
                messagelog = localtimestring(event.timestamp) + "  " + event.message
                messages_pane  = startsc.query_one("#sys-messages-pane")
                messages_pane.post_message(messages_pane.ShowLogs(messagelog))
            # remove all id's associated with this device
            app.itemid.clear_device(event.device)
            # if this device is currently being shown, pop the screen
            if app.itemid.devicename == event.devicename:
                self.clientdata['devicesc'] = None
                app.itemid.devicename = None
                app.pop_screen()
            return


        # handle received events affecting devicesc ################################

        devicesc = self.clientdata.get('devicesc')
        if devicesc is None:
            # A device screen is not currently being shown
            return

        if not event.devicename:
            # This is a system event, already handled
            return

        if not app.itemid.devicename:
            # No device currently being shown
            return

        if event.devicename != app.itemid.devicename:
            # this event refers to a device not currently being shown
            return

        devicename = app.itemid.devicename
        # so this device is currently being shown on devicesc, and the event refers to this device

        # device messages - must be a device message, rather than system message since devicename is given
        if event.eventtype == "Message":
            if event.message:
                messagelog = localtimestring(event.timestamp) + "  " + event.message
                log = devicesc.query_one('#dev-messages-pane')
                log.post_message(log.ShowLogs(messagelog))
            return

        if not event.vectorname:
            return

        vectorid = app.itemid.get_id(event.vectorname)

        if (event.eventtype == "Define" or event.eventtype == "DefineBLOB"):
            if vectorid is None:
                # new vector, add the vector to the tab
                vector = self[devicename][event.vectorname]
                grpid = app.itemid.get_group_id(vector.group)               # if grpid None, a new group has to be created
                if grpid:
                    # The group exists
                    grouptabpane = devicesc.query_one(f"#{grpid}")
                    grouptabpane.post_message(grouptabpane.AddVector(vector))
                else:
                    grouppane = devicesc.query_one("#dev-group-pane")
                    grouppane.post_message(grouppane.AddGroup(vector.group))
                return

        if vectorid is None:
            # no define has been received for this vector, it is not known about
            # should a getproperties be sent here?
            return

        if event.eventtype == "Delete":
            # This vector should be deleted
            vector = self[devicename][event.vectorname]
            grouppane = devicesc.query_one("#dev-group-pane")
            grouppane.post_message(grouppane.DelVector(vector, vectorid))
            # the delete event could include a message, which cannot be displayed on the vector
            # widget, since that will be removed, instead show it on the device message log
            if event.message:
                messagelog = localtimestring(event.timestamp) + "  " + event.message
                log = devicesc.query_one("#dev-messages-pane")
                log.post_message(log.ShowLogs(messagelog))
            return

        # so the vector is currently on display and has a vector pane. The received event may be setting new values
        vectorpane = devicesc.query_one(f"#{vectorid}")

        # Display vector state with timestamp
        if hasattr(event, "state"):
            # shows timestamp and state together
            vectorpane.post_message(vectorpane.ShowTimestamp(localtimestring(event.timestamp)))
            vectorpane.post_message(vectorpane.ShowState(event.state))

        # Display vector message
        if hasattr(event, "message"):
            if event.message:
                vectorpane.post_message(vectorpane.ShowVmessage(localtimestring(event.timestamp) + "  " + event.message))

        if event.eventtype == "TimeOut":
            vectorpane.post_message(vectorpane.SubmitButtonmessage("A Timeout Error has occurred"))
            if vectorpane.vstate == "Busy":
                vectorpane.post_message(vectorpane.ShowTimestamp(localtimestring(event.timestamp)))
                vectorpane.post_message(vectorpane.ShowState("Alert"))
            return


        if event.eventtype not in ("Define", "DefineBLOB", "Set", "SetBLOB"):
            return

        # Only those events with member values now handled

        if event.vector.vectortype == "SwitchVector" and event.vector.rule == "OneOfMany":
            # this is treated differently from the others as each member has not been
            # drawn in its own memberpane, rather all the members are drawn in a special
            # radiomembers container holding a textual radioset.
            # whenever a change is received, ask for this radiomembers to be recomposed
            radiomembers = vectorpane.query_one("RadioMembers")
            radiomembers.post_message(radiomembers.ResetValue())
            return


        # For every member in the event, display its value

        for membername, membervalue in event.items():
            mpid = app.itemid.get_id(event.vectorname, membername)
            if not mpid:
                # This member not defined
                continue
            memberpane = vectorpane.query_one(f"#{mpid}")
            if event.vector.vectortype == "SwitchVector":
                memberpane.post_message(memberpane.SetValue(membervalue))
            elif event.vector.vectortype == "LightVector":
                memberpane.post_message(memberpane.SetValue(membervalue))
            elif event.vector.vectortype == "TextVector":
                memberpane.post_message(memberpane.SetValue(membervalue))
            elif event.vector.vectortype == "NumberVector":
                # display a formatted number string rather than the received number
                fvalue = event.vector.getformattedvalue(membername)
                memberpane.post_message(memberpane.SetValue(fvalue))
            elif event.vector.vectortype == "BLOBVector":
                # display the received filename rather than the binary blob received
                # the vector.member() method returns the member given its name
                fvalue = event.vector.member(membername).filename
                memberpane.post_message(memberpane.SetValue(fvalue))
