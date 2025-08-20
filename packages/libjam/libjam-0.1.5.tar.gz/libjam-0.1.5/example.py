#!/usr/bin/env python3

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
