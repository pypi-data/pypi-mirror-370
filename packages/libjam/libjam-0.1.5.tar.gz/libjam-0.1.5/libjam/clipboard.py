# Deals with lists and such.
class Clipboard:
  # Returns items present in both given lists.
  def get_duplicates(self, input_list1: list, input_list2: list) -> list:
    result_list = []
    for item in input_list1:
      if item in input_list2:
        result_list.append(item)
    result_list = self.deduplicate(result_list)
    return result_list

  # Removes duplicates from a given list.
  def deduplicate(self, input_list: list) -> list:
    result_list = list(set(input_list))
    return result_list

  def remove_duplicates(self, input_list1: list, input_list2: list) -> list:
    result_list = []
    duplicates = self.get_duplicates(input_list1, input_list2)
    for item in input_list1:
      if item not in duplicates:
        result_list.append(item)
    return result_list

  # Returns first list without any items from second list.
  def filter(self, input_list: list, filter_list: list) -> list:
    result_list = []
    for item in input_list:
      if item not in filter_list:
        result_list.append(item)
    return result_list

  # Returns a list of strings which contain a substring.
  def match_substring(self, input_list: list, substring: str) -> list:
    matching = []
    for item in input_list:
      if substring in item:
        matching.append(item)
    return matching

  # Returns a list of strings which start with input_prefix
  def match_prefix(self, input_list: list, input_prefix: str) -> list:
    result_list = []
    for item in input_list:
      if item.startswith(input_prefix):
        result_list.append(item)
    return result_list

  # Removes a prefix from every string in list.
  def remove_prefix(self, input_list: list, input_prefix: str) -> list:
    result_list = []
    for item in input_list:
      result_list.append(item.removeprefix(input_prefix))
    return result_list

  # Returns a list of strings which ends with input_suffix.
  def match_suffix(self, input_list: list, input_suffix: str) -> list:
    result_list = []
    for item in input_list:
      if item.endswith(input_suffix):
        result_list.append(item)
    return result_list

  # Returns a list of strings which ends with input_suffix.
  def match_suffixes(self, input_list: list, input_suffixes: list) -> list:
    result_list = []
    for suffix in input_suffixes:
      result_list += self.match_suffix(input_list, suffix)
    return result_list

  # Returns a list with lower-case strings.
  def lower(self, input_list: list) -> list:
    result_list = []
    for item in input_list:
      result_list.append(item.lower())
    return result_list

  # Returns a list with upper-case strings.
  def upper(self, input_list: list) -> list:
    result_list = []
    for item in input_list:
      result_list.append(item.upper())
    return result_list

  # Returns a list of strings containing given string, ignores case.
  def search(self, input_list: list, search_term: str) -> list:
    result_list = []
    search_term = search_term.lower()
    for item in input_list:
      if search_term in item.lower():
        result_list.append(item)
    return result_list

  # Find & Replace for a list.
  def replace(self, input_list: list, old_string: str, new_string: str) -> list:
    result_list = []
    for item in input_list:
      item = item.replace(old_string, new_string)
      result_list.append(item)
    return result_list
