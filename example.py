"""Create a simple macOS app with AppKit & pyobjc

This makes use of the appkitgui toolkit which simplifies widget creation and layout
"""

from __future__ import annotations

import datetime

import AppKit
import objc
from AppKit import (
    NSApp,
    NSApplication,
    NSBezierPath,
    NSButton,
    NSColor,
    NSMenu,
    NSMenuItem,
    NSObject,
    NSOnState,
    NSOpenPanel,
    NSProcessInfo,
    NSRectFill,
    NSStackView,
    NSView,
    NSWindow,
)
from Foundation import NSMakeRect, NSMutableArray
from objc import objc_method, python_method, super
from PyObjCTools import AppHelper

from appkitgui import (
    MenuItem,
    StackView,
    button,
    checkbox,
    color_well,
    combo_box,
    constrain_stacks_side_by_side,
    constrain_stacks_top_to_bottom,
    constrain_to_height,
    constrain_to_parent_width,
    constrain_to_width,
    constrain_to_width_height,
    date_picker,
    hseparator,
    hspacer,
    hstack,
    image_view,
    label,
    link,
    main_view,
    menu_bar,
    menu_item,
    menu_main,
    menu_with_submenu,
    menus_from_dict,
    nsdate_to_datetime,
    popup_button,
    radio_button,
    search_field,
    slider,
    stepper,
    text_field,
    text_view,
    time_picker,
    vstack,
    window,
)

# constants
EDGE_INSET = 20
EDGE_INSETS = (EDGE_INSET, EDGE_INSET, EDGE_INSET, EDGE_INSET)
PADDING = 8
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


class DotView(NSView):
    """Draw a colored dot on the screen

    This code based on an example by @vsquared: https://github.com/vsquared
    """

    def initWithFrame_(self, frame):
        super().initWithFrame_(frame)
        self.radius = 25
        self.color = NSColor.orangeColor()
        return self

    def changeRadius_(self, sender):
        self.radius = sender.value()
        self.setNeedsDisplay_(True)

    def changeColor_(self, sender):
        self.color = sender.color()
        self.setNeedsDisplay_(True)

    def drawRect_(self, rect):
        NSColor.whiteColor().set()
        NSRectFill(self.bounds())
        self.dotRect = NSMakeRect(
            self.bounds().size.width / 2 - self.radius,
            self.bounds().size.height / 2 - self.radius,
            self.radius * 2,
            self.radius * 2,
        )
        self.color.set()
        NSBezierPath.bezierPathWithOvalInRect_(self.dotRect).fill()


class DemoWindow(NSObject):
    """Demo window showing how to display widgets"""

    @python_method
    def create_window(self) -> NSWindow:
        """Create the NSWindow object"""
        # use @python_method decorator to tell objc this is called using python
        # conventions, not objc conventions
        return window("Demo Window", (WINDOW_WIDTH, WINDOW_HEIGHT))

    @python_method
    def create_main_view(self, window: NSWindow) -> NSStackView:
        """Create the main NStackView for the app and add it to the window"""
        return main_view(window, padding=PADDING, edge_inset=EDGE_INSETS)

    def create_menus(self) -> dict:
        menu_dict = {
            "File": [
                MenuItem("Open", None, self.openMenuAction_, "o"),
                MenuItem("New", None, self.newMenuAction_, "n"),
            ],
            "Edit": [
                MenuItem("Copy", None, None, "c"),  # no target so Copy will be disabled
                {"Format": [MenuItem("Bold", None, self.boldMenuAction_, "b")]},
            ],
        }
        return menus_from_dict(menu_dict, self)

    def show(self):
        """Create and show the window"""

        # TODO: This is a mess... I need to clean this up

        with objc.autorelease_pool():
            # create the window
            self.window = self.create_window()
            self.main_view = self.create_main_view(self.window)

            self.menus = self.create_menus()

            self.hstack0 = hstack()
            self.main_view.append(self.hstack0)
            self.hstack0_0 = hstack()
            self.hstack0_1 = hstack()
            self.hstack0.extend([self.hstack0_0, self.hstack0_1])
            self.label_hello = label("Hello World")
            self.hstack0_0.append(self.label_hello)
            self.link = link(
                "AppKitGUI on GitHub", "https://github.com/RhetTbull/appkitgui"
            )
            self.hstack0_1.append(self.link)

            # constraint the two side-by-side stacks so that they are the same width
            constrain_stacks_side_by_side(
                self.hstack0_0, self.hstack0_1, padding=PADDING
            )
            # constrain hstack0 to the width of the main view so that it resizes when the window does
            constrain_to_parent_width(
                self.hstack0, self.main_view, edge_inset=EDGE_INSET
            )

            # add a horizontal NSStackView to hold widgets side by side
            # and add it to the main view
            self.hstack1 = hstack()
            self.main_view.append(self.hstack1)

            # add a button that activates a file chooser panel
            # the method chooseFile_ does not actually exist in this class
            # self.choose_file() is mapped via @objc_method to "chooseFile:"
            # via the objc bridge -- see self.choose_file() definition
            # this is done here just as an example of how the objc bridge works
            # the string, "chooseFile:" could also be passed directly to the
            # action parameter of the button instead of the callable
            self.choose_file_button = button("Choose File", self, self.chooseFile_)
            self.hstack1.append(self.choose_file_button)

            # create a label which will be updated by choose_file when user chooses a file
            self.label_file = label("")
            self.hstack1.append(self.label_file)

            # create side by side vertical NSStackViews to hold checkboxes and radio buttons
            self.hstack2 = hstack(align=AppKit.NSLayoutAttributeTop)
            self.main_view.append(self.hstack2)

            self.vstack1 = vstack()
            self.hstack2.append(self.vstack1)

            self.checkbox1 = checkbox("Checkbox 1", self, self.checkbox_action)
            self.checkbox2 = checkbox("Checkbox 2", self, self.checkbox_action)
            self.checkbox3 = checkbox("Checkbox 3", self, self.checkbox_action)
            self.vstack1.extend([self.checkbox1, self.checkbox2, self.checkbox3])

            self.vstack2 = vstack()
            self.hstack2.append(self.vstack2)

            self.radio1 = radio_button("Radio 1", self, self.radioAction_)
            self.radio2 = radio_button("Radio 2", self, self.radioAction_)
            self.radio3 = radio_button("Radio 3", self, self.radioAction_)
            self.vstack2.extend([self.radio1, self.radio2, self.radio3])
            self.radio1.setState_(NSOnState)

            # add an uneditable combo box
            self.combo_box_1 = combo_box(
                ["Combo 1", "Combo 2", "Combo 3"],
                self,
                editable=False,
                action_change=self.comboBoxAction_,
            )
            self.hstack2.append(self.combo_box_1)

            # add an editable combo box
            self.combo_box_2 = combo_box(
                ["Edit me and hit return", "Combo 2", "Combo 3"],
                self,
                editable=True,
                # you can also pass a string to be used as the selector
                # which must be name of a method in the target object (self in this case)
                action_change="comboBoxAction:",
                action_return="comboBoxEdited:",
                width=175,
            )
            self.hstack2.append(self.combo_box_2)

            # add a popup button
            self.popup_button = popup_button(
                ["Item 1", "Item 2", "Item 3"], self, self.popUpButtonAction_
            )
            self.hstack2.append(self.popup_button)

            # add a stepper and an associated value field
            # the text field used to show value must be created first
            # so that it can be used as the target of the stepper
            self.stepper_field = text_field((40, 24), "0", self)
            self.stepper = stepper(
                min_value=0,
                max_value=100,
                target=self.stepper_field,
                action="takeIntValueFrom:",
                value=1,
                increment=1,
                editable=False,
                selectable=False,
                alignment=AppKit.NSCenterTextAlignment,
            )
            self.stepper_field.takeStringValueFrom_(self.stepper)
            self.hstack2.append(self.stepper)
            self.hstack2.append(self.stepper_field)

            # add a horizontal separator
            self.hsep = hseparator()
            self.main_view.append(self.hsep)
            # constrain the separator to the left and right edges of the main view, inset by EDGE_INSET
            constrain_to_parent_width(self.hsep, self.main_view, EDGE_INSET)

            # add an image
            self.hstack3 = hstack(align=AppKit.NSLayoutAttributeCenterY)
            self.main_view.append(self.hstack3)
            self.image = image_view(
                "image.jpeg", width=150, align=AppKit.NSImageAlignCenter
            )
            self.hstack3.append(self.image)

            # # add a vertical stack to hold buttons
            self.vstack3 = vstack()
            self.hstack3.append(self.vstack3)
            self.button_add = button("Add", self, self.button_add_to_stack)
            self.button_remove = button("Remove", self, self.button_remove_from_stack)
            self.button_array = NSMutableArray.alloc().init()
            self.button_list = []
            self.label_stack = label(
                "Click Add / Remove to\nadd or remove items\nfrom the stack."
            )
            self.vstack3.extend([self.button_add, self.label_stack, self.button_remove])

            self.vstack4 = vstack(vscroll=True)
            constrain_to_width(self.vstack4, 100)
            self.hstack3.append(self.vstack4)

            # add DotView with slider and color well
            self.dot_view = DotView.alloc().initWithFrame_(NSMakeRect(0, 0, 100, 100))
            constrain_to_width_height(self.dot_view, 100, 100)
            self.color_well = color_well(
                NSColor.orangeColor(), self.dot_view, "changeColor:", 50, 30
            )
            self.slider = slider(0, 60, self.dot_view, "changeRadius:", 25, width=150)
            self.hstack3.append(self.slider)
            self.hstack3.append(self.color_well)
            self.hstack3.append(self.dot_view)

            self.hsep2 = hseparator()
            self.main_view.append(self.hsep2)

            self.label_array = NSMutableArray.alloc().init()
            for x in range(20):
                self.label_array.append(label(f"Label {x}"))
            self.hstack4 = hstack(hscroll=True, views=self.label_array)
            constrain_to_height(self.hstack4, 50)
            self.main_view.append(self.hstack4)

            self.hsep3 = hseparator()
            self.main_view.append(self.hsep3)

            self.hstack5 = hstack(align=AppKit.NSLayoutAttributeTop)
            self.main_view.append(self.hstack5)
            self.date_picker = date_picker(target=self, action="datePickerAction:")
            self.hstack5.append(self.date_picker)

            self.label_date = label(
                f"Date: {self.date_picker.dateValue().strftime('%Y-%m-%d')}"
            )
            self.hstack5.append(self.label_date)

            self.time_picker = time_picker(
                time=datetime.time(8, 0, 0), target=self, action="timePickerAction:"
            )
            self.hstack5.append(self.time_picker)

            self.search_field = search_field(target=self, action="searchFieldAction:")
            self.hstack5.append(self.search_field)

            self.hsep4 = hseparator()
            self.main_view.append(self.hsep4)
            self.hstack6 = hstack(align=AppKit.NSLayoutAttributeTop)
            self.main_view.append(self.hstack6)
            self.text_field = text_field(
                placeholder="Type some text here",
                target=self,
                action="textFieldAction:",
            )
            self.hstack6.append(self.text_field)
            self.text_view = text_view(
                (200, 100), string="Hello World!\nThis is a scrollable text view."
            )
            self.hstack6.append(self.text_view)

            # finish setting up the window
            self.window.makeKeyAndOrderFront_(None)
            self.window.setIsVisible_(True)
            self.window.setLevel_(AppKit.NSNormalWindowLevel)
            self.window.setReleasedWhenClosed_(False)
            return self.window

    @objc_method(selector=b"checkboxAction:")
    def checkbox_action(self, sender: NSButton):
        """Handle checkbox checked/unchecked"""
        # when passing a python style method to the objc bridge
        # you need to mark it as an objc method
        # the selector is the method name passed to the bridge and
        # the number of : in the name must match the number of arguments
        # this method could also be called as self.checkboxAction_() once
        # the decorator is applied
        print("Checkbox changed: ", sender.title(), sender.state())

    def radioAction_(self, sender):
        """Handle radio button selected"""
        # This method name conforms to the objc calling convention therefore
        # the @objc_method decorator is not needed
        print("Radio button selected: ", sender.selectedCell().title())

    def comboBoxAction_(self, sender):
        """Handle combo box selection change"""
        # This gets called when the user selects an item in the combo box
        print("Combo box selection: ", sender.objectValueOfSelectedItem())

    def comboBoxEdited_(self, sender):
        """Handle combo box return"""
        # This gets called when user hits return in the combo box
        print("Combo box edited: ", sender.stringValue())

    def popUpButtonAction_(self, sender):
        """Handle popup button selection change"""
        # This gets called when the user selects an item in the popup button
        print("Pop up button selection: ", sender.selectedItem().title())

    def sliderAction_(self, sender):
        """Handle slider action"""
        print(f"{sender=}")

    def datePickerAction_(self, sender):
        """Handle date picker change"""
        # This gets called when the user changes the date in the date picker
        # Normally, PyObjC handles the conversion of NSDate to datetime.date
        # However, when a function is called directly from objc, the conversion
        # must be done manually
        date = nsdate_to_datetime(sender.dateValue()).date()
        self.label_date.setStringValue_(f"Date: {date.strftime('%Y-%m-%d')}")

    def timePickerAction_(self, sender):
        """Handle time picker change"""
        # This gets called when the user changes the date in the date picker
        # Normally, PyObjC handles the conversion of NSDate to datetime.date
        # However, when a function is called directly from objc, the conversion
        # must be done manually
        time = nsdate_to_datetime(sender.dateValue()).time()
        print(f"Time: {time.strftime('%H:%M:%S')}")

    def searchFieldAction_(self, sender):
        """Handle serach field action"""
        print("Search field:", sender.stringValue())

    def textFieldAction_(self, sender):
        """Handle text field change"""
        # This gets called when the user changes the text in the text field
        print("Text field: ", sender.stringValue())

    def openWindow_(self, sender):
        print("openWindow")
        self.window.setIsVisible_(True)
        self.window.makeKeyAndOrderFront_(None)
        self.window.setLevel_(5)
        print("opened")

    @objc_method(selector=b"chooseFile:")
    def choose_file(self, sender):
        """Present file chooser panel"""
        # use @objc_method decorator to tell objc to call this method when chooseFile: selector is called
        open_panel = NSOpenPanel.openPanel()
        open_panel.setCanChooseFiles_(True)
        open_panel.setCanChooseDirectories_(False)
        open_panel.setAllowsMultipleSelection_(False)
        if open_panel.runModal() == AppKit.NSFileHandlingPanelOKButton:
            file_url = open_panel.URLs()[0].fileSystemRepresentation().decode("utf-8")
            self.label_file.setStringValue_(file_url)
            print(f"choose_file: {file_url}")
        else:
            print("choose_file: Canceled")

    @objc_method(selector=b"buttonAddToStack:")
    def button_add_to_stack(self, sender):
        # _label_stack_list is a list to keep a reference to the labels
        if not getattr(self, "_label_stack_list", None):
            self._label_stack_list = []

        i = len(self._label_stack_list)
        new_label = label(f"Item {i}")

        # keep a reference to the label
        self._label_stack_list.append(new_label)

        # add it to the stack view
        self.vstack4.append(new_label)

    @objc_method(selector=b"buttonRemoveFromStack:")
    def button_remove_from_stack(self, sender):
        # _label_stack_list is a list to keep a reference to the labels
        if not getattr(self, "_label_stack_list", None):
            return
        label_to_remove = self._label_stack_list.pop()
        label_to_remove.setHidden_(True)
        self.vstack4.removeArrangedSubview_(label_to_remove)
        label_to_remove.removeFromSuperview()

    def openMenuAction_(self, sender):
        """Handle the File > Open menu"""
        print("Open!")

    def newMenuAction_(self, sender):
        """Handle the File > New menu"""
        print("New!")

    def boldMenuAction_(self, sender):
        """Handle the Edit | Format | Bold menu"""
        # toggle the checkmark (on/off state) for the Bold menu
        state = not sender.state()
        sender.setState_(state)
        print(f"Bold is {'on' if state else 'off'}")


class AppDelegate(NSObject):
    """Minimalist app delegate."""

    def applicationDidFinishLaunching_(self, notification):
        """Create a window programmatically, without a NIB file."""
        self.window = DemoWindow.alloc().init()
        self.window.show()

    def applicationShouldTerminateAfterLastWindowClosed_(self, sender):
        return True


class App:
    """Create a minimalist app to test the window."""

    def run(self):
        with objc.autorelease_pool():
            # create the app
            NSApplication.sharedApplication()
            NSApp.setActivationPolicy_(AppKit.NSApplicationActivationPolicyRegular)

            # create the menu bar and attach it to the app
            menubar = menu_bar()

            # add a menu item to the menu to quit the app
            # the app's main menu will have the process name
            # and this does not need to be specified
            app_menu = menu_with_submenu(None, menubar)
            app_name = NSProcessInfo.processInfo().processName()
            quit_menu_item = menu_item(
                title=f"Quit {app_name}",
                parent=app_menu,
                action="terminate:",
                target=None,
                key="q",
            )

            # create the delegate and attach it to the app
            delegate = AppDelegate.alloc().init()
            NSApp.setDelegate_(delegate)

            # run the app
            NSApp.activateIgnoringOtherApps_(True)

            # Use AppHelper.runEventLoop() to run the app instead of NSApp.run() to let pyobjc handle the event loop
            AppHelper.runEventLoop(installInterrupt=True)


def main():
    App().run()


if __name__ == "__main__":
    main()
