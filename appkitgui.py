"""Utilities to help create a native macOS GUI with AppKit"""


from __future__ import annotations

import os
from typing import Callable

import objc
from AppKit import (
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
    NSFloatingWindowLevel,
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
    NSLayoutConstraint,
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
    NSOffState,
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
    NSStackViewGravityLeading,
    NSStackViewGravityTop,
    NSTextField,
    NSUnderlineStyleAttributeName,
    NSUnderlineStyleSingle,
    NSUserInterfaceLayoutOrientationHorizontal,
    NSUserInterfaceLayoutOrientationVertical,
    NSView,
    NSWindow,
    NSWindowStyleMaskClosable,
    NSWindowStyleMaskResizable,
    NSWindowStyleMaskTitled,
    NSWorkspace,
)
from Foundation import NSURL, NSMakeRect
from objc import objc_method, python_method, super

# constants

# margin between window edge and content
EDGE_INSET = 20

# padding between elements
PADDING = 8


# helper functions to create AppKit objects
def hstack(
    align: int = NSLayoutAttributeCenterY, distribute: int | None = None
) -> NSStackView:
    """Create a horizontal NSStackView"""
    distribute = None
    hstack = NSStackView.stackViewWithViews_(None).autorelease()
    hstack.setSpacing_(PADDING)
    hstack.setOrientation_(NSUserInterfaceLayoutOrientationHorizontal)
    if distribute is not None:
        hstack.setDistribution_(distribute)
    hstack.setAlignment_(align)
    return hstack


def vstack(
    align: int = NSLayoutAttributeLeft, distribute: int | None = None
) -> NSStackView:
    """Create a vertical NSStackView"""
    vstack = NSStackView.stackViewWithViews_(None).autorelease()
    vstack.setSpacing_(PADDING)
    vstack.setOrientation_(NSUserInterfaceLayoutOrientationVertical)
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

        NSLayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
            stack,
            NSLayoutAttributeWidth,
            NSLayoutRelationEqual,
            stacks[min_index],
            NSLayoutAttributeWidth,
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
