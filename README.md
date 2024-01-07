# AppKit GUI

This is an example script showing how to create a native macOS GUI application using Python and the [PyObjC](https://github.com/ronaldoussoren/pyobjc) bridge. It uses the [AppKit](https://developer.apple.com/documentation/appkit) framework to create a simple application that demonstrates the use of several GUI controls which are created programmatically.

## Rationale

I wrote this to help me learn how to programmatically create a GUI application using native macOS controls without using XCode / Interface Builder. I could not find many examples of how to do this so I created this to help me learn how to do it.

I'm certain there are better ways to do this. The AppKit framework provides many different ways to create and use native controls. I've experimented and found something that worked but it may not be optimal. I welcome any feedback or suggestions for improvement.

## Requirements

Requires Python 3.9 or later and the [PyObjC](https://github.com/ronaldoussoren/pyobjc) bridge. You can install PyObjC using pip:

```bash
pip3 install -r requirements.txt
```

## Usage

Run the script:

```bash
python3 appkitgui.py
```

## LICENSE

MIT License
