"""
Allow blackduck to be executable as a module with python -m blackduck.
"""

from .game import main

if __name__ == "__main__":
    main()
