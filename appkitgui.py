"""Create a simple macOS app with AppKit & pyobjc"""

from __future__ import annotations

import os
from typing import Callable

import objc
from AppKit import (
    NSApp,
    NSApplication,
    NSApplicationActivationPolicyRegular,
    NSApplicationMain,
    NSAttributedString,
    NSBackingStoreBuffered,
    NSBox,
    NSBoxSeparator,
    NSButton,
    NSButtonCell,
    NSButtonTypeMomentaryChange,
    NSButtonTypeMomentaryPushIn,
    NSButtonTypeRadio,
    NSButtonTypeSwitch,
    NSColor,
    NSComboBox,
    NSCursor,
    NSCursorAttributeName,
    NSFileHandlingPanelOKButton,
    NSForegroundColorAttributeName,
    NSImage,
    NSImageAlignTopLeft,
    NSImageScaleProportionallyDown,
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
    NSModalPanelWindowLevel,
    NSMutableAttributedString,
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
    NSStatusBar,
    NSTextField,
    NSTextView,
    NSTitledWindowMask,
    NSTrackingActiveAlways,
    NSTrackingArea,
    NSTrackingInVisibleRect,
    NSTrackingMouseEnteredAndExited,
    NSUnderlineStyleAttributeName,
    NSUnderlineStyleSingle,
    NSUserInterfaceLayoutOrientationHorizontal,
    NSUserInterfaceLayoutOrientationVertical,
    NSVariableStatusItemLength,
    NSViewMaxXMargin,
    NSViewMaxYMargin,
    NSViewMinXMargin,
    NSViewMinYMargin,
    NSViewWidthSizable,
    NSWindow,
    NSWindowStyleMaskClosable,
    NSWindowStyleMaskResizable,
    NSWindowStyleMaskTitled,
    NSWorkspace,
)
from Foundation import NSURL, NSMakeRange, NSMakeRect
from objc import objc_method, python_method, super

# constants
EDGE_INSET = 20
EDGE_INSETS = (EDGE_INSET, EDGE_INSET, EDGE_INSET, EDGE_INSET)


# helper functions to create AppKit objects
def hstack(
    align: int = NSLayoutAttributeCenterY, distribute: int = NSStackViewDistributionFill
) -> NSStackView:
    """Create a horizontal NSStackView"""
    hstack = NSStackView.stackViewWithViews_(None).autorelease()
    hstack.setSpacing_(8)
    hstack.setOrientation_(NSUserInterfaceLayoutOrientationHorizontal)
    hstack.setDistribution_(distribute)
    hstack.setAlignment_(align)
    return hstack


def vstack(
    align: int = NSLayoutAttributeLeft, distribute: int = NSStackViewDistributionFill
) -> NSStackView:
    """Create a vertical NSStackView"""
    vstack = NSStackView.stackViewWithViews_(None).autorelease()
    vstack.setSpacing_(8)
    vstack.setOrientation_(NSUserInterfaceLayoutOrientationVertical)
    vstack.setDistribution_(distribute)
    vstack.setAlignment_(align)
    return vstack


def label(value: str) -> NSTextField:
    """Create a label"""
    label = NSTextField.labelWithString_(value).autorelease()
    label.setEditable_(False)
    label.setBordered_(False)
    label.setBackgroundColor_(NSColor.clearColor())
    return label


class LinkLabel(NSTextField):
    """Uneditable text field that displays a clickable link"""

    def initWithText_URL_(self, text: str, url: str):
        self = super().init()

        if not self:
            return

        attr_str = self.attributedStringWithLinkToURL_text_(url, text)
        self.setAttributedStringValue_(attr_str)
        self.url = NSURL.URLWithString_(url)
        self.setBordered_(False)
        self.setSelectable_(False)
        self.setEditable_(False)
        self.setBezeled_(False)
        self.setDrawsBackground_(False)

        return self

    def resetCursorRects(self):
        self.addCursorRect_cursor_(self.bounds(), NSCursor.pointingHandCursor())

    def mouseDown_(self, event):
        print("mouseDown:", event)
        NSWorkspace.sharedWorkspace().openURL_(self.url)

    def mouseEntered_(self, event):
        NSCursor.pointingHandCursor().push()

    def mouseExited_(self, event):
        NSCursor.pop()

    def attributedStringWithLinkToURL_text_(self, url: str, text: str):
        linkAttributes = {
            NSLinkAttributeName: NSURL.URLWithString_(url),
            NSUnderlineStyleAttributeName: NSUnderlineStyleSingle,
            NSForegroundColorAttributeName: NSColor.linkColor(),
            # NSCursorAttributeName: NSCursor.pointingHandCursor(),
        }
        return NSAttributedString.alloc().initWithString_attributes_(
            text, linkAttributes
        )


def link(text: str, url: str) -> NSTextField:
    """Create a clickable link label"""
    return LinkLabel.alloc().initWithText_URL_(text, url)


def button(title: str, target: NSObject, action: Callable | str | None) -> NSButton:
    """Create a button"""
    button = NSButton.buttonWithTitle_target_action_(
        title, target, action
    ).autorelease()
    return button


def checkbox(title: str, target: NSObject, action: Callable | str | None) -> NSButton:
    """Create a checkbox button"""
    checkbox = NSButton.buttonWithTitle_target_action_(
        title, target, action
    ).autorelease()
    checkbox.setButtonType_(NSButtonTypeSwitch)  # Switch button type
    return checkbox


def radio_button(
    title: str, target: NSObject, action: Callable | str | None
) -> NSButton:
    """Create a radio button"""
    radio_button = NSButton.buttonWithTitle_target_action_(
        title, target, action
    ).autorelease()
    radio_button.setButtonType_(NSRadioButton)
    return radio_button


def combo_box(
    values: list[str] | None,
    target: NSObject,
    action: Callable | str | None,
    delegate: NSObject | None = None,
) -> NSComboBox:
    """Create a combo box"""

    # TODO: the size of the combo box is not preserved--it always resizes to the contents
    combo_box = (
        NSComboBox.alloc().initWithFrame_(NSMakeRect(0, 0, 100, 25)).autorelease()
    )
    combo_box.setTarget_(target)
    if values:
        combo_box.addItemsWithObjectValues_(values)
        combo_box.selectItemAtIndex_(0)
    if delegate:
        combo_box.setDelegate_(delegate)
    if action:
        combo_box.setAction_(action)
    combo_box.setCompletes_(True)
    combo_box.setEditable_(False)
    return combo_box


def hseparator() -> NSBox:
    """Create a horizontal separator"""
    separator = NSBox.alloc().init().autorelease()
    separator.setBoxType_(NSBoxSeparator)
    separator.setTranslatesAutoresizingMaskIntoConstraints_(False)
    return separator


def image_view(
    path: str | os.PathLike, width: int | None = None, height: int | None = None
) -> NSImageView:
    """Create an image from a file"""
    image = NSImage.alloc().initByReferencingFile_(str(path)).autorelease()
    image_view = NSImageView.imageViewWithImage_(image).autorelease()
    image_view.setImageScaling_(NSImageScaleProportionallyUpOrDown)
    image_view.setImageAlignment_(NSImageAlignTopLeft)
    if width:
        image_view.widthAnchor().constraintEqualToConstant_(width).setActive_(True)
    if height:
        image_view.heightAnchor().constraintEqualToConstant_(height).setActive_(True)
    return image_view


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
        main_view.setSpacing_(8)
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
            self.hstack2 = hstack()
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

            # add a combo box; set the delegate to self so we can handle
            # selection changes via the delegate method comboBoxSelectionDidChange_
            # TODO: the size of the combo box is not preserved--it always resizes to the contents
            self.combo_box = combo_box(
                ["Combo 1", "Combo 2", "Combo 3"], self, self.comboBoxAction_, self
            )
            self.hstack2.addArrangedSubview_(self.combo_box)

            # add a horizontal separator
            self.hsep = hseparator()
            self.main_view.addArrangedSubview_(self.hsep)
            # constrain the separator to the left and right edges of the main view, inset by EDGE_INSET
            self.hsep.rightAnchor().constraintEqualToAnchor_constant_(
                self.main_view.rightAnchor(), -EDGE_INSET
            ).setActive_(True)

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
        """Handle combo box action"""
        # This gets called when the user hits return in the combo box
        # which they cannot do if the combo box is not editable
        print("Combo box: ", sender.objectValueOfSelectedItem())

    def comboBoxSelectionDidChange_(self, notification):
        """Handle combo box selection change"""
        # This is a delegate method and is called when the user selects
        # an item in the combo box
        # For this to work, the combo box delegate must be set to self
        if not getattr(self, "combo_box", None):
            return
        print(
            "Combo box selection changed: ", self.combo_box.objectValueOfSelectedItem()
        )

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
