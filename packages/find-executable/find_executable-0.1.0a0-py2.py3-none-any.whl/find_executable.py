import os

from posix_or_nt import posix_or_nt


def seqtok(string, separators):
    """Mimics the behavior of C's strtok() function:

    - Consecutive separators are treated as a single separator
    - Leading/trailing separators are ignored (no empty tokens)
    - Returns tokens one at a time via iteration

    But with crucial differences:

    - State is encapsulated in the generator instance (no global state)
        - No thread safety concerns from global state
    - Each iterator maintains independent state (safe for separate instances)
        - Multiple tokenizers can operate simultaneously
    """
    last_char_is_separator = True
    char_buffer = []

    for char in string:
        if last_char_is_separator:
            if char not in separators:
                # State transition
                last_char_is_separator = False
                char_buffer.append(char)
        else:
            if char not in separators:
                char_buffer.append(char)
            else:
                # State transition
                last_char_is_separator = True
                yield ''.join(char_buffer)
                char_buffer = []

    if char_buffer:
        yield ''.join(char_buffer)


def iterate_path_entries():
    path = os.getenv('PATH')
    if path is not None:
        for path_entry in seqtok(path, {os.pathsep}):
            if path_entry:
                yield path_entry


if posix_or_nt() == 'nt':
    import itertools
    import ntpath


    def iterate_path_extensions():
        pathext = os.getenv('PATHEXT')
        if pathext is not None:
            for pathext_entry in seqtok(pathext, {os.pathsep}):
                if pathext_entry:
                    yield pathext_entry


    def find_executable(executable_name):
        """Yield full paths for all executables matching the given name.

        Args:
            executable_name (str): The name of the executable to search for.

        Yields:
            str: Absolute path to the matching executable.
        """
        path_extensions = set(iterate_path_extensions())
        candidate_executable_names_with_extensions = set()

        # Does `string_executable_name` include an extension?
        _, extension = ntpath.splitext(executable_name)
        if extension:
            # Is it already a path to an executable?
            if os.access(executable_name, os.X_OK):
                yield ntpath.realpath(executable_name)
            else:
                candidate_executable_names_with_extensions.add(executable_name)
        else:
            for path_extension in path_extensions:
                candidate_executable_names_with_extensions.add(executable_name + path_extension)

        # Look in the current directory first, then directories in PATH
        for directory in itertools.chain(('.',), iterate_path_entries()):
            for candidate_executable_name_with_extension in candidate_executable_names_with_extensions:
                candidate_executable_path = ntpath.join(directory, candidate_executable_name_with_extension)
                if os.access(candidate_executable_path, os.X_OK):
                    yield ntpath.realpath(candidate_executable_path)
else:
    import posixpath


    def find_executable(executable_name):
        """Yield full paths for all executables matching the given name.

        Args:
            executable_name (str): The name of the executable to search for.

        Yields:
            str: Absolute path to the matching executable.
        """
        # Does `string_executable_name` contain a slash?
        # Then we treat `string_executable_name` as the path to an executable
        if '/' in executable_name:
            if os.access(executable_name, os.X_OK):
                yield posixpath.realpath(executable_name)
        # Elsewise, we do a path lookup
        else:
            for path_entry in iterate_path_entries():
                potential_executable_path = posixpath.join(path_entry, executable_name)
                if os.access(potential_executable_path, os.X_OK):
                    yield posixpath.realpath(potential_executable_path)
