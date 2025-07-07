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
from libs.logger import Logger, LoggerInterrupt

# Create main function of the script
def main() -> None:
    """
    Main function of the script
    this function is called when launching the script
    """
    logger = Logger()
    try:
        # Here we execute code
        logger.info("Hello World !")

    except LoggerInterrupt as e:
        logger.traceback(e.__traceback__)
    finally:
        logger.save()

if __name__ == "__main__":
    main()
