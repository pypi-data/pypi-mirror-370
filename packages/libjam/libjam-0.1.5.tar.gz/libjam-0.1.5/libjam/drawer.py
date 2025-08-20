# Imports
import os
import sys
import shutil
import pathlib
import tempfile
import zipfile
import rarfile
import patoolib
import platform
import subprocess
import math


# Internal functions
def outpath(path: str or list) -> str or list:
  if type(path) is str:
    return path.replace(os.sep, '/')
  elif type(path) is list:
    result_list = []
    for item in path:
      result_list.append(item.replace(os.sep, '/'))
    return result_list


HOME = outpath(str(pathlib.Path.home()))
PLATFORM = platform.system()
joinpath = os.path.join


def realpath(path: str) -> str:
  if path.startswith('~'):
    path = path.replace('~', HOME)
  return os.path.normpath(path)


def realpaths(path: list) -> list:
  result_list = []
  for item in path:
    result_list.append(realpath(item))
  return result_list


# Deals with files.
class Drawer:
  # General:

  # Converts the given path to an absolute path.
  def absolute_path(self, path) -> str:
    path = realpath(path)
    return outpath(path)

  # Useful variables:

  # Returns the user's home folder.
  def get_home(self) -> str:
    return outpath(HOME)

  # Returns the system's temporary folder.
  def get_temp(self) -> str:
    temp = str(tempfile.gettempdir())
    return outpath(temp)

  # Returns host OS name.
  # Common values: 'Linux', 'Windows', 'Darwin'.
  def get_platform(self) -> str:
    return PLATFORM

  # File checking:

  # Returns True if path exists.
  def exists(self, path: str) -> bool:
    path = realpath(path)
    return os.path.exists(path)

  # Returns True if given a path to a file.
  def is_file(self, path: str) -> bool:
    path = realpath(path)
    return os.path.isfile(path)

  # Returns True if given a path to a folder.
  def is_folder(self, path: str) -> bool:
    if path == '':
      return False
    path = realpath(path)
    return os.path.isdir(path)

  # File gathering:

  # Returns a list of files and folders in a given path.
  def get_all(self, path: str) -> list:
    path = realpath(path)
    relative_files = os.listdir(path)
    absolute_files = []
    for file in relative_files:
      file = joinpath(path, file)
      absolute_files.append(file)
    return outpath(absolute_files)

  # Returns a list of files in a given folder.
  def get_files(self, path: str) -> list:
    everything = self.get_all(path)
    files = []
    for item in everything:
      if self.is_file(item):
        files.append(item)
    return files

  # Returns a list of folders in a given folder.
  def get_folders(self, path: str) -> list:
    folders = []
    for item in self.get_all(path):
      if self.is_folder(item):
        folders.append(item)
    return outpath(folders)

  # Returns a list of all files in a given folder.
  def get_files_recursive(self, path: str) -> list:
    path = realpath(path)
    files = []
    for folder in os.walk(path, topdown=True):
      for file in folder[2]:
        file = joinpath(folder[0], file)
        files.append(file)
    return outpath(files)

  # Returns a list of all folders in a given folder.
  def get_folders_recursive(self, path: str) -> list:
    path = realpath(path)
    folders = []
    for folder in os.walk(path, topdown=True):
      for subfolder in folder[1]:
        subfolder = joinpath(folder[0], subfolder)
        folders.append(subfolder)
    return outpath(folders)

  # File creation:

  # Creates a new file.
  def make_file(self, path: str) -> str:
    path = realpath(path)
    new = open(path, 'w')
    new.close()
    return outpath(path)

  # Creates a new folder.
  def make_folder(self, path: str) -> str:
    path = realpath(path)
    path = os.mkdir(path)
    return outpath(path)

  # Non-destructive file operations:

  # Copies given file/folder.
  def copy(self, source: str, destination: str, overwrite=False) -> str:
    source = realpath(source)
    destination = realpath(destination)
    if self.is_file(source):
      shutil.copy(source, destination)
    elif self.is_folder(source):
      shutil.copytree(source, destination, dirs_exist_ok=overwrite)
    else:
      raise FileNotFoundError(f"File '{source}' does not exist.")
    return outpath(destination)

  # Renames a given file in a given path.
  def rename(self, folder: str, old_filename: str, new_filename: str) -> str:
    if not folder.endswith('/'):
      folder = folder + '/'
    old_file, new_file = folder + old_filename, folder + new_filename
    old_file, new_file = realpath(old_file), realpath(new_file)
    os.rename(old_file, new_file)
    return outpath(new_file)

  # File removal:

  # Deletes a given file/folder.
  def delete_path(self, path: str) -> str:
    if self.is_file(path):
      remove_function = os.remove
    elif self.is_folder(path):
      remove_function = shutil.rmtree
    path = realpath(path)
    remove_function(path)
    return outpath(path)

  # Deletes given files/folders.
  def delete_paths(self, paths: list) -> list:
    return_list = []
    for path in paths:
      return_list.append(self.delete_path(path))
    return return_list

  # Deletes a given file.
  def delete_file(self, file: str) -> str:
    file = realpath(file)
    if self.is_file(file):
      os.remove(file)
      return outpath(file)
    else:
      raise IsADirectoryError(f"Attempted to delete a folder at '{file}'.")

  # Deletes given files.
  def delete_files(self, files: list) -> list:
    return_list = []
    for file in files:
      return_list.append(self.delete_file(file))
    return return_list

  # Deletes a given folder.
  def delete_folder(self, folder: str) -> str:
    if self.is_folder(folder):
      folder = realpath(folder)
      shutil.rmtree(folder)
    else:
      raise NotADirectoryError(f"Attempted to delete file at '{folder}'.")
    return outpath(folder)

  # Deletes given folders.
  def delete_folders(self, folders: list) -> list:
    return_list = []
    for folder in folders:
      return_list.append(self.delete_folder(folder))
    return return_list

  # Sends given file/folder to trash.
  def trash_path(self, path: str) -> str:
    # Need to check the file ourselves because send2trash raises an OSError
    # instead of a FileNotFoundError
    if not self.exists(path):
      raise FileNotFoundError(f"File at '{path}' does not exist.")
    # Send2Trash can take a long time to import on systems that use GIO due
    # to how long it takes to import GObject and GIO, so doing it on-demand
    # is generally better
    if 'send2trash' not in sys.modules:
      import send2trash
    send2trash = sys.modules.get('send2trash')
    path = realpath(path)
    try:
      send2trash.send2trash(path)
    except send2trash.exceptions.TrashPermissionError:
      raise PermissionError(
        f"Attempted to trash path '{path}' with insufficient permissions."
      )
    return outpath(path)

  # Sends given files/folders to trash.
  def trash_paths(self, paths: list) -> list:
    return_list = []
    for path in paths:
      return_list.append(self.trash_path(path))
    return return_list

  # Path parts:

  # Returns a given file's/folder's basename.
  def get_basename(self, path: str) -> str:
    path = realpath(path)
    if self.is_folder(path):
      path = os.path.basename(os.path.normpath(path))
    else:
      path = path.rsplit(os.sep, 1)[-1]
    return outpath(path)

  # Given a list of paths, returns a list of their basenames.
  def get_basenames(self, paths: list) -> list:
    return_list = []
    for path in paths:
      return_list.append(self.get_basename(path))
    return return_list

  # Returns the parent folder of given file/folder.
  def get_parent(self, path: str) -> str:
    basename = self.get_basename(path)
    parent = path.removesuffix(basename)
    parent = parent.removesuffix('/')
    return parent

  def get_parents(self, paths: list) -> list:
    return_list = []
    for path in paths:
      return_list.append(self.get_parent(path))
    return return_list

  # Path parameters:

  # Returns depth of given file/folder.
  def get_depth(self, path: str) -> int:
    depth = len(path.split('/'))
    return depth

  # Returns the extension of a given file.
  def get_filetype(self, path: str) -> str:
    if self.is_folder(path):
      return 'folder'
    basename = self.get_basename(path)
    filetype = os.path.splitext(basename)[1].removeprefix('.')
    return filetype

  # File statistics:

  # Returns the weight of a given file/folder, in bytes.
  def get_filesize(self, path: str) -> int:
    path = realpath(path)
    if self.is_file(path):
      size = os.path.getsize(path)
    elif self.is_folder(path):
      size = 0
      subfiles = self.get_files_recursive(path)
      for file in subfiles:
        size += os.path.getsize(file)
    return size

  # Given a number of bytes, returns a human readable filesize, as a tuple.
  # Tuple format: (value: float, short_unit_name: str, long_unit_name: str)
  # Example tuple: (6.986356, 'mb', 'megabytes')
  def get_readable_filesize(self, filesize: int) -> tuple:
    filesize_orders = [
      ('b', 'bytes'),
      ('kb', 'kilobytes'),
      ('mb', 'megabytes'),
      ('gb', 'gigabytes'),
      ('tb', 'terabytes'),
      ('eb', 'exabytes'),
      ('zb', 'zettabytes'),
      ('yb', 'yottabytes'),
      ('rb', 'ronnabytes'),
      ('qb', 'quettabytes'),
    ]
    filesize_order = math.floor(math.log(filesize, 1000))
    filesize = filesize / (1000**filesize_order)
    return (filesize,) + filesize_orders[filesize_order]

  # Archive extraction:

  # Given a path to an archive, returns whether archive's extraction is supported.
  def is_archive_supported(self, path: str) -> bool:
    supported_archive_types = ['zip', 'rar', '7z']
    filetype = self.get_filetype(path)
    return filetype in supported_archive_types

  # Extracts a given archive to a specified location.
  # progress_function is called every time a file is extracted from the archive.
  # progress_function is only supported for ZIP and RAR archives.
  # Example definition of a progress_function:
  # def progress_function(done: int, total: int):
  #   print(f"Extracted {done} files out of {total} files total")
  def extract_archive(
    self,
    archive: str,
    extract_location: str,
    progress_function: callable = None,
  ) -> str:
    if not self.is_archive_supported(archive):
      raise NotImplementedError(
        f"Attempted extraction of archive at '{archive}'."
      )
    archive_type = self.get_filetype(archive)
    archive_basename = self.get_basename(archive).removesuffix(
      f'.{archive_type}'
    )
    extract_location = f'{extract_location}/{archive_basename}'
    archive, extract_location = realpath(archive), realpath(extract_location)
    if archive_type == '7z':
      try:
        patoolib.extract_archive(archive, outdir=extract_location, verbosity=-1)
      except patoolib.util.PatoolError:
        raise RuntimeError(
          'It appears that 7Zip is not installed on this system.'
        )
    elif archive_type in ('zip', 'rar'):
      if archive_type == 'zip':
        archive_object = zipfile.ZipFile(archive)
      elif archive_type == 'rar':
        archive_object = rarfile.RarFile(archive)
      archived_files = archive_object.namelist()
      to_extract = len(archived_files)
      extracted = 0
      for archived_file in archived_files:
        archive_object.extract(archived_file, path=extract_location)
        extracted += 1
        if progress_function is not None:
          progress_function(extracted, to_extract)
    return outpath(extract_location)

  # Same as xdg-open, but platform-independent.
  def open(self, argument: str, is_path: bool = True) -> int:
    if is_path:
      argument = realpath(argument)
    open_by_platform = {
      'Linux': 'xdg-open',
      'Windows': 'start',
      'Darwin': 'open',
    }
    if PLATFORM in open_by_platform:
      open_command = open_by_platform.get(PLATFORM)
    else:
      raise NotImplementedError(f"Platform '{platform}' is not supported.")
    return subprocess.run([open_command, argument], check=True).returncode
