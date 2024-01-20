"""Create a simple macOS app with AppKit & pyobjc"""

from __future__ import annotations

from typing import Callable

import objc
from AppKit import (
    NSApp,
    NSApplication,
    NSApplicationActivationPolicyRegular,
    NSAttributedString,
    NSBackingStoreBuffered,
    NSBox,
    NSBoxSeparator,
    NSButton,
    NSButtonTypeSwitch,
    NSColor,
    NSComboBox,
    NSCursor,
    NSFileHandlingPanelOKButton,
    NSForegroundColorAttributeName,
    NSImage,
    NSImageAlignTopLeft,
    NSImageScaleProportionallyUpOrDown,
    NSImageView,
    NSLayoutAttributeBottom,
    NSLayoutAttributeCenterX,
    NSLayoutAttributeCenterY,
    NSLayoutAttributeFirstBaseline,
    NSLayoutAttributeHeight,
    NSLayoutAttributeLastBaseline,
    NSLayoutAttributeLeading,
    NSLayoutAttributeLeft,
    NSLayoutAttributeNotAnAttribute,
    NSLayoutAttributeRight,
    NSLayoutAttributeTop,
    NSLayoutAttributeTrailing,
    NSLayoutAttributeWidth,
    NSLayoutConstraintOrientationVertical,
    NSLayoutPriorityDefaultHigh,
    NSLayoutPriorityDefaultLow,
    NSLayoutPriorityDragThatCannotResizeWindow,
    NSLayoutPriorityDragThatCanResizeWindow,
    NSLayoutPriorityFittingSizeCompression,
    NSLayoutPriorityRequired,
    NSLayoutPriorityWindowSizeStayPut,
    NSLayoutRelationEqual,
    NSLayoutRelationGreaterThanOrEqual,
    NSLayoutRelationLessThanOrEqual,
    NSLineBreakByTruncatingTail,
    NSLinkAttributeName,
    NSMakeRect,
    NSMenu,
    NSMenuItem,
    NSNormalWindowLevel,
    NSObject,
    NSOnState,
    NSOpenPanel,
    NSProcessInfo,
    NSRadioButton,
    NSStackView,
    NSStackViewDistributionEqualCentering,
    NSStackViewDistributionEqualSpacing,
    NSStackViewDistributionFill,
    NSStackViewDistributionFillEqually,
    NSStackViewDistributionFillProportionally,
    NSStackViewDistributionGravityAreas,
    NSStackViewGravityTop,
    NSTextField,
    NSUnderlineStyleAttributeName,
    NSUnderlineStyleSingle,
    NSUserInterfaceLayoutOrientationHorizontal,
    NSUserInterfaceLayoutOrientationVertical,
    NSWindow,
    NSWindowStyleMaskClosable,
    NSWindowStyleMaskResizable,
    NSWindowStyleMaskTitled,
    NSWorkspace,
)
from Foundation import NSMakeRect
from objc import objc_method, python_method

from appkitgui import (
    button,
    checkbox,
    combo_box,
    constrain_to_parent_width,
    hseparator,
    hstack,
    image_view,
    label,
    link,
    radio_button,
    vstack,
)

# constants
EDGE_INSET = 20
EDGE_INSETS = (EDGE_INSET, EDGE_INSET, EDGE_INSET, EDGE_INSET)
PADDING = 8


class DemoWindow(NSObject):
    """Demo window showing how to display widgets"""

    @python_method
    def create_window(self) -> NSWindow:
        """Create the NSWindow object"""
        # use @python_method decorator to tell objc this is called using python
        # conventions, not objc conventions
        window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, 600, 600),
            NSWindowStyleMaskTitled
            | NSWindowStyleMaskClosable
            | NSWindowStyleMaskResizable,
            NSBackingStoreBuffered,
            False,
        )
        window.center()
        window.setTitle_("Demo Window")
        return window

    @python_method
    def create_main_view_(self, window: NSWindow) -> NSStackView:
        """Create the main NStackView for the app and add it to the window"""
        main_view = NSStackView.stackViewWithViews_(None)
        main_view.setOrientation_(NSUserInterfaceLayoutOrientationVertical)
        main_view.setSpacing_(PADDING)
        main_view.setEdgeInsets_(EDGE_INSETS)
        main_view.setDistribution_(NSStackViewDistributionFill)
        main_view.setAlignment_(NSLayoutAttributeLeft)

        window.contentView().addSubview_(main_view)
        top_constraint = main_view.topAnchor().constraintEqualToAnchor_(
            main_view.superview().topAnchor()
        )
        top_constraint.setActive_(True)
        # bottom_constraint = main_view.bottomAnchor().constraintEqualToAnchor_(
        #     main_view.superview().bottomAnchor()
        # )
        # bottom_constraint.setActive_(True)
        left_constraint = main_view.leftAnchor().constraintEqualToAnchor_(
            main_view.superview().leftAnchor()
        )
        left_constraint.setActive_(True)
        right_constraint = main_view.rightAnchor().constraintEqualToAnchor_(
            main_view.superview().rightAnchor()
        )
        right_constraint.setActive_(True)
        return main_view

    def show(self):
        """Create and show the window"""
        with objc.autorelease_pool():
            # create the window
            self.window = self.create_window()
            self.main_view = self.create_main_view_(self.window)

            self.label_hello = label("Hello World")
            self.main_view.addArrangedSubview_(self.label_hello)

            self.link = link(
                "AppKitGUI on GitHub", "https://github.com/RhetTbull/appkitgui"
            )
            self.main_view.addArrangedSubview_(self.link)

            # add a horizontal NSStackView to hold widgets side by side
            # and add it to the main view
            self.hstack1 = hstack()
            self.main_view.addArrangedSubview_(self.hstack1)

            # add a button that activates a file chooser panel
            # the method chooseFile_ does not actually exist in this class
            # self.choose_file() is mapped via @objc_method to "chooseFile:"
            # via the objc bridge -- see self.choose_file() definition
            # this is done here just as an example of how the objc bridge works
            # the string, "chooseFile:" could also be passed directly to the
            # action parameter of the button instead of the callable
            self.choose_file_button = button("Choose File", self, self.chooseFile_)
            self.hstack1.addArrangedSubview_(self.choose_file_button)

            # create a label which will be updated by choose_file when user chooses a file
            self.label_file = label("")
            self.hstack1.addArrangedSubview_(self.label_file)

            # create side by side vertical NSStackViews to hold checkboxes and radio buttons
            self.hstack2 = hstack(align=NSLayoutAttributeTop)
            self.main_view.addArrangedSubview_(self.hstack2)

            self.vstack1 = vstack()
            self.hstack2.addArrangedSubview_(self.vstack1)

            self.checkbox1 = checkbox("Checkbox 1", self, self.checkbox_action)
            self.vstack1.addArrangedSubview_(self.checkbox1)
            self.checkbox2 = checkbox("Checkbox 2", self, self.checkbox_action)
            self.vstack1.addArrangedSubview_(self.checkbox2)
            self.checkbox3 = checkbox("Checkbox 3", self, self.checkbox_action)
            self.vstack1.addArrangedSubview_(self.checkbox3)

            self.vstack2 = vstack()
            self.hstack2.addArrangedSubview_(self.vstack2)

            self.radio1 = radio_button("Radio 1", self, self.radioAction_)
            self.radio2 = radio_button("Radio 2", self, self.radioAction_)
            self.radio3 = radio_button("Radio 3", self, self.radioAction_)
            self.vstack2.addArrangedSubview_(self.radio1)
            self.vstack2.addArrangedSubview_(self.radio2)
            self.vstack2.addArrangedSubview_(self.radio3)
            self.radio1.setState_(NSOnState)

            # add an uneditable combo box
            # TODO: the size of the combo box is not preserved--it always resizes to the contents
            self.combo_box_1 = combo_box(
                ["Combo 1", "Combo 2", "Combo 3"],
                self,
                editable=False,
                action_change=self.comboBoxAction_,
            )
            self.hstack2.addArrangedSubview_(self.combo_box_1)

            # add an editable combo box
            self.combo_box_2 = combo_box(
                ["Edit me and hit return", "Combo 2", "Combo 3"],
                self,
                editable=True,
                # you can also pass a string to be used as the selector
                # which must be name of a method in the target object (self in this case)
                action_change="comboBoxAction:",
                action_return="comboBoxEdited:",
            )
            self.hstack2.addArrangedSubview_(self.combo_box_2)

            # add a horizontal separator
            self.hsep = hseparator()
            self.main_view.addArrangedSubview_(self.hsep)
            # constrain the separator to the left and right edges of the main view, inset by EDGE_INSET
            constrain_to_parent_width(self.hsep, self.main_view, EDGE_INSET)

            # add an image
            self.image = image_view("image.jpeg", width=200)
            self.main_view.addArrangedSubview_(self.image)

            # finish setting up the window
            self.window.makeKeyAndOrderFront_(None)
            self.window.setIsVisible_(True)
            self.window.setLevel_(NSNormalWindowLevel)
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
        if open_panel.runModal() == NSFileHandlingPanelOKButton:
            file_url = open_panel.URLs()[0].fileSystemRepresentation().decode("utf-8")
            self.label_file.setStringValue_(file_url)
            print(f"choose_file: {file_url}")
        else:
            print("choose_file: Canceled")


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
            NSApp.setActivationPolicy_(NSApplicationActivationPolicyRegular)

            # create the menu bar and attach it to the app
            menubar = NSMenu.alloc().init().autorelease()
            app_menu_item = NSMenuItem.alloc().init().autorelease()
            menubar.addItem_(app_menu_item)
            NSApp.setMainMenu_(menubar)
            app_menu = NSMenu.alloc().init().autorelease()

            # add a menu item to the menu to quit the app
            app_name = NSProcessInfo.processInfo().processName()
            quit_title = f"Quit {app_name}"
            quit_menu_item = (
                NSMenuItem.alloc()
                .initWithTitle_action_keyEquivalent_(quit_title, "terminate:", "q")
                .autorelease()
            )
            app_menu.addItem_(quit_menu_item)
            app_menu_item.setSubmenu_(app_menu)

            # create the delegate and attach it to the app
            delegate = AppDelegate.alloc().init()
            NSApp.setDelegate_(delegate)

            # run the app
            NSApp.activateIgnoringOtherApps_(True)
            return NSApp.run()


def main():
    App().run()


if __name__ == "__main__":
    main()
