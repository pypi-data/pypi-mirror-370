# Imports
import sys

# Internal imports
from .drawer import Drawer
from .typewriter import Typewriter

drawer = Drawer()
typewriter = Typewriter()


# Helper functions
def on_invalid_option(script: str, option: str):
  print(
    f"""Invalid option '{option}'.
Try '{script} --help' for more information."""
  )
  sys.exit(-1)


def on_command_not_recognised(script: str, command: str, commands: list):
  available_commands = ', '.join(commands)
  print(
    f"""{script}: command '{command}' not recognised.
Available commands: {available_commands}"""
  )
  sys.exit(-1)


def get_raw_args() -> tuple:
  args = sys.argv.copy()
  script = drawer.get_basename(args[0])
  args.pop(0)
  return script, args


def parse_args(script: str, raw_args: list) -> tuple:
  # Initialising vars
  command = None
  command_args = []
  short_flags = []
  long_flags = []
  # Categorising args
  for arg in raw_args:
    if arg.startswith('--'):
      if arg == '--':
        on_invalid_option(script, arg)
      long_flags.append(arg.removeprefix('--'))
    elif arg.startswith('-'):
      if arg == '-':
        on_invalid_option(script, arg)
      short_flags += list(arg.removeprefix('-'))
    else:
      if command is None:
        command = arg
      else:
        command_args.append(arg)
  return command, command_args, short_flags, long_flags


# Returns item from dict if it exists and it is not empty, otherwise
# returns None
def get_existing(dictionary: dict, item: str):
  if item in dictionary:
    item = dictionary.get(item)
    if item is not None:
      if len(item) > 0:
        return item
  return None


# Generates the help pages.
class Helper:
  def get_help_section(self, title: str, content: str or list) -> str:
    offset = 2
    offset_string = ' ' * offset
    section = f'{typewriter.bolden(title + ":")}\n'
    if type(content) is str:
      content = content.replace('\n', '\n' + offset_string)
      section += f'{offset_string}{content}\n'
    elif type(content) is list:
      columns = 2
      section += typewriter.list_to_columns(content, columns, offset) + '\n'
    else:
      raise NotImplementedError()
    return section.rstrip()

  def sections_to_help(self, sections: list) -> str:
    help = ''
    for title, content in sections:
      help += self.get_help_section(title, content) + '\n'
    return help.rstrip()

  def get_command_usage(
    self,
    script: str,
    command: str,
    command_info: dict,
  ) -> str:
    required_args = get_existing(command_info, 'arguments')
    usage_string = f'{script} {command}'
    if required_args is not None:
      arbitrary_args = required_args[-1][0] == '*'
      if arbitrary_args:
        required_args[-1] = required_args[-1].removeprefix('*')
      usage_string += ' ' + ' '.join(f'<{item}>' for item in required_args)
      if arbitrary_args:
        usage_string += '...'
    return usage_string

  # Prints the help page for a specific command.
  def print_command_help(
    self,
    script: str,
    command: str,
    command_info: dict,
  ):
    usage_string = self.get_command_usage(script, command, command_info)
    description = command_info.get('description') + '.'
    sections = [
      ('Usage', usage_string),
      ('Description', description),
    ]
    print(self.sections_to_help(sections))

  # Returns a help page for a CLI program.
  def print_help(
    self,
    script: str,
    description: str,
    commands: dict,
    options: dict = None,
  ):
    # Getting info
    commands_list = []
    for command in commands:
      command_info = commands.get(command)
      command_description = command_info.get('description')
      commands_list.append(f'{command}')
      commands_list.append(f'- {command_description}.')
    # Sections
    sections = [
      ('Synopsis', f'{script} [OPTIONS] [COMMAND]'),
    ]
    sections += [
      ('Description', description + '.'),
      ('Commands', commands_list),
    ]
    # Adding options
    if options is not None:
      options_list = []
      for option in options:
        option_desc = options.get(option).get('description')
        long = ', --'.join(options.get(option).get('long'))
        short = ', -'.join(options.get(option).get('short'))
        options_list.append(f'-{short}, --{long}')
        options_list.append(f'- {option_desc}.')
      option_section = ('Options', options_list)
      sections.append(option_section)
    # Printing
    print(self.sections_to_help(sections))


helper = Helper()


def process_options(
  script: str,
  options: dict,
  short_flags: list,
  long_flags: list,
) -> dict:
  # Creating option bools
  processed_options = {}
  for option in options:
    processed_options[option] = False
  # Flags
  for prefix, flags, flag_type in [
    ('-', short_flags, 'short'),
    ('--', long_flags, 'long'),
  ]:
    for flag in flags:
      if options is not None:
        found = False
        for option in options:
          opt_keyword = options.get(option).get(flag_type)
          if flag in opt_keyword:
            processed_options[option] = True
            found = True
            break
        if not found:
          on_invalid_option(script, prefix + flag)
      elif len(flags) > 0:
        on_invalid_option(script, prefix + flag)
  return processed_options


def process_command_arguments(
  script: str, command: str, command_info: dict, command_args: list
) -> list:
  required_arguments = get_existing(command_info, 'arguments')
  n_given_args = len(command_args)
  if required_arguments is not None:
    required_arguments = required_arguments.copy()
    arbitrary_args = required_arguments[-1][0] == '*'
    if arbitrary_args:
      required_arguments[-1] = required_arguments[-1].removeprefix('*')
    n_required_args = len(required_arguments)
    if not arbitrary_args:
      if n_given_args > n_required_args:
        print(f'{script} {command}: too many arguments')
        sys.exit(-1)
    if n_given_args < n_required_args:
      missing_arg = required_arguments[n_given_args]
      missing_arg = f'<{missing_arg}>'
      if arbitrary_args and missing_arg == required_arguments[-1]:
        missing_arg += '...'
      print(f'{script} {command}: missing argument {missing_arg}')
      sys.exit(-1)
    if len(required_arguments) == 1 and not arbitrary_args:
      return command_args[0]
    return command_args
  elif n_given_args > 0:
    print(
      f"""{script}: '{command}' does not take arguments.
Try '{script} {command} --help' for more information."""
    )
    sys.exit(-1)
  return None


# Processes command line arguments.
class Captain:
  # See the example in the readme for proper info.
  def sail(
    self,
    description: str,
    commands: dict,
    options: dict = None,
  ) -> tuple:
    # Adding help to options
    options['help'] = {
      'long': ['help'],
      'short': ['h'],
      'description': 'Prints help',
    }
    # Getting input args
    script, args = get_raw_args()
    command, command_args, short_flags, long_flags = parse_args(script, args)
    # Processing options
    processed_options = process_options(
      script, options, short_flags, long_flags
    )
    # Checking if command is specified
    if command is None:
      if processed_options.get('help'):
        helper.print_help(script, description, commands, options)
        sys.exit(0)
      else:
        print(
          f"""No command specified.
Try '{script} --help' for more information."""
        )
        sys.exit(-1)
    # Getting command info
    command_info = None
    for item in commands:
      if command == item:
        command_info = commands.get(item)
    # Checking if command is recognised
    if command_info is None:
      on_command_not_recognised(script, command, commands)
    else:
      if processed_options.get('help'):
        helper.print_command_help(script, command, command_info)
        sys.exit(0)
    command_args = process_command_arguments(
      script, command, command_info, command_args
    )
    command_function = command_info.get('function')
    return_tuple = (command_function, command_args)
    if processed_options is not None:
      return_tuple += (processed_options,)
    return return_tuple
