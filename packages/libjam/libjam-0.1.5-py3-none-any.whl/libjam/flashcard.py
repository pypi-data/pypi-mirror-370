# Gets user input.
class Flashcard:
  def yn_prompt(self, question: str) -> bool:
    yes_choices = ('yes', 'y')
    no_choices = ('no', 'n')
    while True:
      user_input = input(f'{question} [y/n]: ').lower()
      if user_input in yes_choices:
        return True
      elif user_input in no_choices:
        return False
