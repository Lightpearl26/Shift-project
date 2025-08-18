import pygame
from libs.pygame_ui import Popup, Selector, TextList

pygame.init()
screen = pygame.display.set_mode((800, 600))
screen.fill((100, 150, 200))
pygame.display.flip()

popup_rect = pygame.Rect(0, 0, 600, 500)
popup_rect.center = screen.get_rect().center
popup = Popup(screen, popup_rect, title="Propriétés entité", height=1000)
selector = Selector(
    popup,
    pygame.Rect(0, 0, 600, 42),
    [
        ("brush", pygame.image.load("assets/Editor/brush.png").convert_alpha()),
        ("fill", pygame.image.load("assets/Editor/fill.png").convert_alpha()),
        ("rectangle", pygame.image.load("assets/Editor/rectangle.png").convert_alpha())
    ],
    orientation="horizontal"
)
text_list = TextList(
    parent=popup,
    pos=(50, 50),
    width=300,
    items=["Épée", "Bouclier", "Potion", "Arc", "Sort de feu", "les", "tests", "c'est", "bien", "les", "amis"]
)

popup.run()
