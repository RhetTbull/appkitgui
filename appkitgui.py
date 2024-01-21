"""Toolkit to help create a native macOS GUI with AppKit"""


from __future__ import annotations

import os
from typing import Callable

import AppKit
from AppKit import (
    NSBox,
    NSButton,
    NSComboBox,
    NSImageView,
    NSStackView,
    NSTextField,
    NSView,
)
from Foundation import NSURL, NSMakeRect, NSObject
from objc import objc_method, super

# constants

# margin between window edge and content
EDGE_INSET = 20

# padding between elements
PADDING = 8


# helper functions to create AppKit objects
def hstack(
    align: int = AppKit.NSLayoutAttributeCenterY, distribute: int | None = None
) -> NSStackView:
    """Create a horizontal NSStackView"""
    distribute = None
    hstack = NSStackView.stackViewWithViews_(None).autorelease()
    hstack.setSpacing_(PADDING)
    hstack.setOrientation_(AppKit.NSUserInterfaceLayoutOrientationHorizontal)
    if distribute is not None:
        hstack.setDistribution_(distribute)
    hstack.setAlignment_(align)
    return hstack


def vstack(
    align: int = AppKit.NSLayoutAttributeLeft, distribute: int | None = None
) -> NSStackView:
    """Create a vertical NSStackView"""
    vstack = NSStackView.stackViewWithViews_(None).autorelease()
    vstack.setSpacing_(PADDING)
    vstack.setOrientation_(AppKit.NSUserInterfaceLayoutOrientationVertical)
    if distribute is not None:
        vstack.setDistribution_(distribute)
    vstack.setAlignment_(align)
    return vstack


def hspacer() -> NSStackView:
    """Create a horizontal spacer"""
    return vstack()


def label(value: str) -> NSTextField:
    """Create a label"""
    label = NSTextField.labelWithString_(value).autorelease()
    label.setEditable_(False)
    label.setBordered_(False)
    label.setBackgroundColor_(AppKit.NSColor.clearColor())
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
        self.addCursorRect_cursor_(self.bounds(), AppKit.NSCursor.pointingHandCursor())

    def mouseDown_(self, event):
        print("mouseDown:", event)
        AppKit.NSWorkspace.sharedWorkspace().openURL_(self.url)

    def mouseEntered_(self, event):
        AppKit.NSCursor.pointingHandCursor().push()

    def mouseExited_(self, event):
        AppKit.NSCursor.pop()

    def attributedStringWithLinkToURL_text_(self, url: str, text: str):
        linkAttributes = {
            AppKit.NSLinkAttributeName: NSURL.URLWithString_(url),
            AppKit.NSUnderlineStyleAttributeName: AppKit.NSUnderlineStyleSingle,
            AppKit.NSForegroundColorAttributeName: AppKit.NSColor.linkColor(),
            # AppKit.NSCursorAttributeName: AppKit.NSCursor.pointingHandCursor(),
        }
        return AppKit.NSAttributedString.alloc().initWithString_attributes_(
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
    checkbox.setButtonType_(AppKit.NSButtonTypeSwitch)  # Switch button type
    return checkbox


def radio_button(
    title: str, target: NSObject, action: Callable | str | None
) -> NSButton:
    """Create a radio button"""
    radio_button = NSButton.buttonWithTitle_target_action_(
        title, target, action
    ).autorelease()
    radio_button.setButtonType_(AppKit.NSRadioButton)
    return radio_button


class ComboBoxDelegate(NSObject):
    """Helper class to handle combo box events"""

    def initWithTarget_Action_(self, target: NSObject, action: Callable | str | None):
        self = super().init()
        if not self:
            return

        self.target = target
        self.action_change = action
        return self

    @objc_method
    def comboBoxSelectionDidChange_(self, notification):
        if self.action_change:
            if type(self.action_change) == str:
                self.target.performSelector_withObject_(
                    self.action_change, notification.object()
                )
            else:
                self.action_change(notification.object())

    # this is not currently used, handled by action_return
    # @objc_method
    # def comboBox_textView_doCommandBySelector_(
    #     self, combo_box, text_view, command_selector
    # ):
    #     if command_selector == b"insertNewline:":
    #         if self.action_return:
    #             self.action_return()
    #         return True
    #     return False


class ComboBox(NSComboBox):
    """NSComboBox that stores a reference it's delegate

    Note:
        This is required to maintain a reference to the delegate, otherwise it will
        not be retained after the ComboBox is created.
    """

    def setDelegate_(self, delegate: NSObject | None):
        self.delegate = delegate
        if delegate is not None:
            super().setDelegate_(delegate)


def combo_box(
    values: list[str] | None,
    target: NSObject,
    editable: bool = False,
    action_return: Callable | str | None = None,
    action_change: Callable | str | None = None,
    delegate: NSObject | None = None,
    width: float | None = None,
) -> NSComboBox:
    """Create a combo box

    Args:
        values: list of values to populate the combo box with
        target: target to send action to
        editable: whether the combo box is editable
        action_return: action to send when return is pressed (only called if editable is True)
        action_change: action to send when the selection is changed
        delegate: delegate to handle events; if not provided a default delegate is automatically created
        width: width of the combo box; if None, the combo box will resize to the contents


    Note:
        In order to handle certain events such as return being pressed, a delegate is
        required. If a delegate is not provided, a default delegate is automatically
        created which will call the action_return callback when return is pressed.
        If a delegate is provided, it may implement the following methods:

                - comboBoxSelectionDidChange
                - comboBox_textView_doCommandBySelector
    """

    combo_box = ComboBox.alloc().initWithFrame_(NSMakeRect(0, 0, 100, 25)).autorelease()
    combo_box.setTarget_(target)
    delegate = delegate or ComboBoxDelegate.alloc().initWithTarget_Action_(
        target, action_change
    )
    combo_box.setDelegate_(delegate)
    if values:
        combo_box.addItemsWithObjectValues_(values)
        combo_box.selectItemAtIndex_(0)
    if action_return:
        combo_box.setAction_(action_return)
    combo_box.setCompletes_(True)
    combo_box.setEditable_(editable)

    if width is not None:
        constrain_to_width(combo_box, width)
    return combo_box


def hseparator() -> NSBox:
    """Create a horizontal separator"""
    separator = NSBox.alloc().init().autorelease()
    separator.setBoxType_(AppKit.NSBoxSeparator)
    separator.setTranslatesAutoresizingMaskIntoConstraints_(False)
    return separator


def image_view(
    path: str | os.PathLike, width: int | None = None, height: int | None = None
) -> NSImageView:
    """Create an image from a file"""
    image = AppKit.NSImage.alloc().initByReferencingFile_(str(path)).autorelease()
    image_view = NSImageView.imageViewWithImage_(image).autorelease()
    image_view.setImageScaling_(AppKit.NSImageScaleProportionallyUpOrDown)
    image_view.setImageAlignment_(AppKit.NSImageAlignTopLeft)
    if width:
        image_view.widthAnchor().constraintEqualToConstant_(width).setActive_(True)
    if height:
        image_view.heightAnchor().constraintEqualToConstant_(height).setActive_(True)
    return image_view


def min_with_index(values: list[float]) -> tuple[int, int]:
    """Return the minimum value and index of the minimum value in a list"""
    min_value = min(values)
    min_index = values.index(min_value)
    return min_value, min_index


def constrain_stacks_side_by_side(
    *stacks: NSStackView,
    weights: list[float] | None = None,
    parent: NSStackView | None = None,
    padding: int = 0,
    edge_inset: int = 0,
):
    """Constrain a list of NSStackViews to be side by side and equal width or weighted widths

    Args:
        *stacks: NSStackViews to constrain
        weights: weights to use for each stack; if None, all stacks are equal width
        parent: NSStackView to constrain the stacks to; if None, uses stacks[0].superview()
        padding: padding between stacks
        edge_inset: padding between stacks and parent


    Note:
        If weights are provided, the stacks will be constrained to be side by side with
        widths proportional to the weights. For example, if 2 stacks are provided with
        weights = [1, 2], the first stack will be half the width of the second stack.
    """

    if len(stacks) < 2:
        raise ValueError("Must provide at least two stacks")

    parent = parent or stacks[0].superview()

    if weights is not None:
        min_weight, min_index = min_with_index(weights)
    else:
        min_weight, min_index = 1.0, 0

    for i, stack in enumerate(stacks):
        if i == 0:
            stack.leadingAnchor().constraintEqualToAnchor_constant_(
                parent.leadingAnchor(), edge_inset
            ).setActive_(True)
        else:
            stack.leadingAnchor().constraintEqualToAnchor_constant_(
                stacks[i - 1].trailingAnchor(), padding
            ).setActive_(True)
        if i == len(stacks) - 1:
            stack.trailingAnchor().constraintEqualToAnchor_constant_(
                parent.trailingAnchor(), -edge_inset
            ).setActive_(True)
        stack.topAnchor().constraintEqualToAnchor_constant_(
            parent.topAnchor(), edge_inset
        ).setActive_(True)
        stack.bottomAnchor().constraintEqualToAnchor_constant_(
            parent.bottomAnchor(), -edge_inset
        ).setActive_(True)

        if weights is not None:
            weight = weights[i] / min_weight
        else:
            weight = 1.0

        AppKit.NSLayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
            stack,
            AppKit.NSLayoutAttributeWidth,
            AppKit.NSLayoutRelationEqual,
            stacks[min_index],
            AppKit.NSLayoutAttributeWidth,
            weight,
            0.0,
        ).setActive_(
            True
        )


def constrain_to_parent_width(
    view: NSView, parent: NSView | None = None, edge_inset: int = 0
):
    """Constrain an NSView to the width of its parent

    Args:
        view: NSView to constrain
        parent: NSView to constrain the control to; if None, uses view.superview()
        edge_inset: margin between control and parent
    """
    parent = parent or view.superview()
    view.rightAnchor().constraintEqualToAnchor_constant_(
        parent.rightAnchor(), -edge_inset
    ).setActive_(True)
    view.leftAnchor().constraintEqualToAnchor_constant_(
        parent.leftAnchor(), edge_inset
    ).setActive_(True)


def constrain_to_width(view: NSView, width: float | None = None):
    """Constrain an NSView to a fixed width

    Args:
        view: NSView to constrain
        width: width to constrain to; if None, does not apply a width constraint
    """
    if width is not None:
        view.widthAnchor().constraintEqualToConstant_(width).setActive_(True)
