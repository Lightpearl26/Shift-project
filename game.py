#!venv/Scripts/python.exe
#-*- coding: utf-8 -*-

"""
SHIFT PROJECT
____________________________________________________________________________________________________
project name : Shift Project
authors      : Lafiteau Franck | Castaing Guillaume
version      : a0.1
____________________________________________________________________________________________________
This project is a fanmade game where two players are playing a platformer game. One of the player is
controlling the main character trying to pass the game and the other plays his sidekick that is here
to help him during his journey
____________________________________________________________________________________________________
copyrights: (c) Franck Lafiteau (code)
            (c) Guillaume Castaing (main idea, level design, graphics)
"""

# import libs
from libs import logger as l

# Create main function of the script
def main() -> None:
    """
    Main function of the script
    this function is called when launching the script
    """
    logger = l.Logger()
    logger.info("Hello World !")
    logger.save()

if __name__ == "__main__":
    main()
