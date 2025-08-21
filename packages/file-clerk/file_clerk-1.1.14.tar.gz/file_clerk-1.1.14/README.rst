file-clerk
==========

A collection of functions for dealing with files and file content.

This was a library I created for previous projects that deal with files
and file paths in order to get code from files, lists of files in
project folders, file extensions, and allows us to capture just files
of a particular type. I also developed my projects on Windows OS, so
these functions were designed to work with the file paths on Windows,
Mac, and Linux (Windows is the one with backslashes - wacky, I know.).

Typical usage example:
----------------------

:code:`extension = get_file_type("path/to/file.js")`

:code:`code_string = file_to_string("path/to/file.html")`

:code:`project_path = "path/to/project"`
:code:`all_project_files = get_all_project_files(project_path)`
:code:`just_css_files = get_all_files_of_type(project_path, "css")`
