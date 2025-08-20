# libjam
A library jam for Python.

## Installing
libjam is available on [PyPI](https://pypi.org/project/libjam/), and can be installed using pip.
```
pip install libjam
```
To install the latest bleeding edge:
```
pip install git+https://github.com/philippkosarev/libjam.git
```

## Modules

### Captain
Makes creating command line interfaces easy.

### Drawer
Responsible for file operations. Accepts the '/' as the file separator, regardless the OS.

### Typewriter
Transforms text and prints to the terminal.

### Clipboard
Provides some useful and commonly used list operations.

### Notebook
Simplifies and standardises reading and writing configuration files.

### Flashcard
Useful for getting user input from the command line.

## Example CLI project
example.py:
```python
# Imports
from libjam import captain

# Defining function
def my_print(args: list, options: dict):
  text = ' '.join(args)
  if options.get('world'):
    text += ' world!'
  print(text)

# Setting commands and options
description = 'An example CLI for the libjam library'
commands = {
  'print': {
    'function': my_print,
    'description': 'Prints the given input',
    'arguments': ['*text'],
  },
}
options = {
  'world': {
    'long': ['world'], 'short': ['w'],
    'description': "Appends ' world!' to the end of the string",
  },
}

# Running
function, arguments, options = captain.sail(description, commands, options)
function(arguments, options)
```

Output:
```
$ ./example.py
No command specified.
Try 'example.py --help' for more information.
$ ./example.py print Hello
Hello
$ ./example.py print Hello --world
Hello world!
$ ./example.py help
Synopsis:
  example.py [OPTIONS] [COMMAND]
Description:
  An example CLI for the libjam library.
Commands:
  print - Prints the given input.
Options:
  -w, --world - Appends ' world!' to the end of the string.
  -h, --help  - Prints help.
```
