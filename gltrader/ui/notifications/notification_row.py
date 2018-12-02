"""
This lists a raw balances response from the API
"""

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.properties    import NumericProperty
from kivy.graphics import Color, Rectangle
from ..buttons import SingleMarketButton, RemoveNotificationButton, ActionDoButton
from ...notification import *

from pprint import pprint as pp
import datetime

class NotificationRow(GridLayout):
    """
    The display Widget for individual notifications
    """
    market=None
    note=None
    status=NumericProperty()
    action=None
    order=None

    def __init__(self, notification, **kwargs):
        """
        :param notification: (Notification) the notification object that is associated with this widget
        """
        self.note=notification
        self.widgets={}
        super(NotificationRow, self).__init__(**kwargs, rows=1, size_hint=(1, 30))
        self.refresh()
        self.padding = [10,0,0,0]
        self.bind(status=self.refresh)
        # App.get_running_app().trader.notifications[id(self)] = self


    def refresh(self):
        #=======================================================================
        # Appends each element of the notification row in order if it has not already been added.
        # In order:
        #     - Remove Button
        #     - Timestamp
        #     - Message ( different colors depending on integer "Notification.level" )
        #     - Action Button / Spacer ( Displayed if Notification.sender is Action
        #       and actions are not set to automatically execute.  Executes action )
        #     - Market Button / Spacer ( Display if Notification.sender is Market. Shows individual market window )
        #=======================================================================
        if "remove" not in self.widgets:
            self.widgets["remove"] = RemoveNotificationButton(self.note)
            self.add_widget(self.widgets["remove"])

        if "timestamp" not in self.widgets:
            try:
                self.widgets["timestamp"] = Label(text=self.note.time.strftime("%Y-%m-%d@%H:%M"),
                                                  size_hint_x=None, width=200, color=[.5,.5,.5,1])
                self.add_widget(self.widgets["timestamp"])
            except Exception as e:
                pp(self.note)

        if "message" not in self.widgets:
            # Set colour - Error
            if self.note.level == 9:
                msgColour = [1, .2, .2, 1]
            # Set colour - Alert
            elif self.note.level == 6:
                msgColour = [1, 1, .4, 1]
            # Set colour - Success
            elif self.note.level == 3:
                msgColour = [.2, 1, .2, 1]
            # Set colour - Default
            else:
                msgColour = [1, 1, 1, 1]

            try:
                self.widgets["message"] = Label(text=self.note.message, color=msgColour)
                self.widgets["message"].canvas.before.clear()
                self.add_widget(self.widgets["message"])
                
            except Exception as e:
                pp(self.note)

        if self.note.action:
            # if not self.action.done:
                if "actionbutton" not in self.widgets:
                    self.widgets["actionbutton"] = ActionDoButton(self.note.action, size_hint_x=None, width=75)
                    self.add_widget(self.widgets["actionbutton"])
                else:
                    self.widgets["actionbutton"].refresh()
            # else:
            #     Error("Bad action button", self.note.action)
        else:
                if "actionspacer" not in self.widgets:
                    self.widgets["actionspacer"] = Label(width=25, size_hint_x=None)
                    self.add_widget(self.widgets["actionspacer"])

        if self.note.market:
            # if self.note.market.checkUpToDate():
                if "marketbutton" not in self.widgets:
                    self.widgets["marketbutton"] = SingleMarketButton(self.note.market, size_hint_x=None, width=75)
                    self.add_widget(self.widgets["marketbutton"])
                else:
                    self.widgets["marketbutton"].refresh()

            # else:
            #     Error("Bad market button", self.note.market)
        else:
                if "marketspacer" not in self.widgets:
                    self.widgets["marketspacer"] = Label(width=25, size_hint_x=None)
                    self.add_widget(self.widgets["marketspacer"])
