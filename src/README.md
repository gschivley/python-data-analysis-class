# About the `src` folder
This folder is where you keep scripts and functions. For the purpose of this workshop we will use it to stash functions for use in notebooks.

## Structure
Notice that both `src` and all sub-folders have an `__init__.py` file. These files let us treat `src` as a module and easily import functions from it. Read more [in the official documentation][1].

Organize your scripts into sub-folders (each with their own `__init__.py`) rather than lumping all of your scripts into `src`. It'll make the logic of what different scripts and functions are used for more clear for someone else (including your future self).



[1]: https://docs.python.org/3/tutorial/modules.html#packages
