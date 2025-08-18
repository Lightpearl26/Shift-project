# -*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
pygame ui lib
version : 1.0
____________________________________________________________________________________________________
Contains all ui objects for map editor
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import external modules
from typing import Optional, Callable
import pygame

# import package modules


# create objects of the module
class UIWidget:
    """
    Base class of all UI widgets
    """
    def __init__(self, parent: Optional["UIWidget"], rect: pygame.Rect) -> None:
        self.parent: Optional["UIWidget"] = parent
        self.rect: pygame.Rect = rect

        # states of the widget
        self.displayed = True
        self.focused = False
        self.hover = False
        self.pressed = False

        # link to parent
        self.widgets: list[UIWidget] = []
        if self.parent:
            self.parent.widgets.append(self)

    def render(self, surface: pygame.Surface) -> None:
        """
        render on surface
        """
        for child in self.widgets:
            child.render(surface)

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        handles a single event
        """
        if not self.displayed:
            return

        if event.type == pygame.WINDOWLEAVE:
            self.hover = False

        elif event.type == pygame.WINDOWFOCUSLOST:
            self.focused = False

        elif event.type in (pygame.MOUSEMOTION,
                            pygame.MOUSEBUTTONDOWN,
                            pygame.MOUSEBUTTONUP,
                            pygame.MOUSEWHEEL):
            self.handle_mouse_event(event)

        elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
            self.handle_keyboard_event(event)

    def handle_mouse_event(self, event: pygame.event.Event) -> None:
        """
        handle a mouse event
        """
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.hover and event.button == 1:
            self.focused = True
            self.pressed = True
        elif event.type == pygame.MOUSEBUTTONDOWN and not self.hover and event.button == 1:
            self.focused = False
        elif event.type == pygame.MOUSEBUTTONUP:
            self.pressed = False

    def handle_keyboard_event(self, event: pygame.event.Event) -> None:
        """
        handle a keyboard event
        """


class Label(UIWidget):
    """
    Instance of a label widget
    """
    def __init__(self,
                 parent: Optional[UIWidget],
                 pos: tuple[int, int],
                 text: str,
                 font: pygame.font.Font,
                 color: tuple[int, int, int]
                ) -> None:
        self.text = font.render(text, True, color)
        UIWidget.__init__(self, parent, self.text.get_rect(topleft=pos))

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.text, self.rect)


class Button(UIWidget):
    """
    Instance of a button widget
    """
    def __init__(self,
                 parent: Optional[UIWidget],
                 pos: tuple[int, int],
                 text: Optional[str] = None,
                 shape: Optional[tuple[int, int]] = None,
                 text_font: Optional[pygame.font.Font] = None,
                 text_color: Optional[tuple[int, int, int]] = None,
                 text_hover_color: Optional[tuple[int, int, int]] = None,
                 text_pressed_color: Optional[tuple[int, int, int]] = None,
                 bg_color: Optional[tuple[int, ...]] = (0, 0, 0, 0),
                 bg_hover_color: Optional[tuple[int, ...]] = (0, 0, 0, 0),
                 bg_pressed_color: Optional[tuple[int, ...]] = (0, 0, 0, 0),
                 bg_image: Optional[pygame.Surface] = None,
                 bg_hover_image: Optional[pygame.Surface] = None,
                 bg_pressed_image: Optional[pygame.Surface] = None,
                 callback: Optional[tuple[Callable, dict]] = None
                ) -> None:
        UIWidget.__init__(self, parent, pygame.Rect(pos, (0, 0)))
        self.text = text
        self.font = text_font
        if shape:
            self.rect.size = shape
        elif bg_image:
            self.rect.size = bg_image.get_size()
        else:
            text_surf = self.font.render(text, True, text_color)
            self.rect.size = text_surf.get_size()

        self.text_color = text_color
        self.text_hover_color = text_hover_color
        self.text_pressed_color = text_pressed_color

        self.bg_color = bg_color
        self.bg_hover_color = bg_hover_color
        self.bg_pressed_color = bg_pressed_color

        self.bg_image = bg_image
        self.bg_hover_image = bg_hover_image
        self.bg_pressed_image = bg_pressed_image

        if callback:
            self.callback = callback[0]
            self.callback_kwargs = callback[1]
        else:
            self.callback = lambda: None
            self.callback_kwargs = dict()

        self._cache_texts()

    def _render_text(self, color):
        if not self.text or not self.font:
            return None
        return self.font.render(self.text, True, color)

    def _cache_texts(self):
        self.text_surfaces = {
            "normal": self._render_text(self.text_color),
            "hover": self._render_text(self.text_hover_color),
            "pressed": self._render_text(self.text_pressed_color)
        }

    def render(self, surface: pygame.Surface) -> None:
        UIWidget.render(self, surface)
        if self.pressed:
            bg = self.bg_pressed_image if self.bg_pressed_image else None
            text_surf = self.text_surfaces["pressed"]
            bg_color = self.bg_pressed_color
        elif self.hover:
            bg = self.bg_hover_image if self.bg_hover_image else None
            text_surf = self.text_surfaces["hover"]
            bg_color = self.bg_hover_color
        else:
            bg = self.bg_image if self.bg_image else None
            text_surf = self.text_surfaces["normal"]
            bg_color = self.bg_color

        if bg_color:
            surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            surf.fill(bg_color)
            surface.blit(surf, self.rect)

        if bg:
            surface.blit(bg, self.rect)

        if text_surf:
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def handle_mouse_event(self, event):
        UIWidget.handle_mouse_event(self, event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover:
            self.callback(**self.callback_kwargs)


class TextEntry(UIWidget):
    """
    Instance of a Text Entry widget
    """
    def __init__(self,
                 parent: Optional[UIWidget],
                 rect: pygame.Rect,
                 font: pygame.font.Font,
                 default_text: str="",
                 max_length: int = 50
                ) -> None:
        UIWidget.__init__(self, parent, rect)
        self.text: str = default_text
        self.cursor_pos = len(self.text)
        self.font: pygame.font.Font = font
        self.max_length = max_length

    def render(self, surface: pygame.Surface) -> None:
        UIWidget.render(self, surface)
        pygame.draw.rect(surface, (255, 255, 255), self.rect)

        # Texte avant et après le curseur
        text_before = self.font.render(self.text[:self.cursor_pos], True, (0, 0, 0))
        text_full = self.font.render(self.text, True, (0, 0, 0))

        # Position de base du texte
        text_rect = text_full.get_rect(midleft=self.rect.move(10, 0).midleft)
        surface.blit(text_full, text_rect)

        # Affichage du curseur si focus
        if self.focused:
            pygame.draw.rect(surface, (155, 255, 55), self.rect, 2)
            cursor_x = text_rect.x + text_before.get_width()
            pygame.draw.line(surface,
                             (0, 0, 0),
                             (cursor_x, text_rect.top),
                             (cursor_x, text_rect.bottom),
                             2)
        elif self.hover:
            pygame.draw.rect(surface, (255, 155, 55), self.rect, 2)
        else:
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)

    def handle_keyboard_event(self, event: pygame.event.Event) -> None:
        if not self.focused:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.focused = False
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
            elif event.unicode and event.unicode.isprintable() and len(self.text) < self.max_length:
                self.text = self.text[:self.cursor_pos] + event.unicode + \
                            self.text[self.cursor_pos:]
                self.cursor_pos += 1


class SelectorButton(UIWidget):
    """
    Instance of a selector button widget
    """
    def __init__(self,
                 parent: UIWidget,
                 rect: pygame.Rect,
                 name: str,
                 icon: pygame.Surface,
                 callback: Callable,
                 hover_color: Optional[tuple[int, ...]]=(255, 255, 255),
                 active_color: Optional[tuple[int, ...]]=(155, 255, 55)
                ) -> None:
        UIWidget.__init__(self, parent, rect)
        self.name = name
        self.icon = icon
        self.callback = callback
        self.active: bool = False
        self.hover_color = hover_color
        self.active_color = active_color

    def handle_mouse_event(self, event):
        UIWidget.handle_mouse_event(self, event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover:
            self.callback(self.name)

    def render(self, surface: pygame.Surface) -> None:
        color = self.parent.bg_color
        if self.active and self.active_color:
            color = self.active_color
        elif self.hover and self.hover_color:
            color = self.hover_color
        surface.fill(color, self.rect)
        surface.blit(self.icon, self.rect)


class Frame(UIWidget):
    """
    Instance of a Frame widget
    """
    def __init__(self,
                 parent: Optional[UIWidget],
                 rect: pygame.Rect,
                 width: Optional[int]=None,
                 height: Optional[int]=None,
                 bg_color: Optional[tuple[int, ...]]=(0, 0, 0, 0)
                ) -> None:
        UIWidget.__init__(self, parent, rect)
        self.scroll: pygame.Vector2 = pygame.Vector2(0, 0)
        self.size = (width if width else self.rect.width,
                     height if height else self.rect.height)
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)
        self.bg_color = bg_color or (0, 0, 0, 0)

    def handle_mouse_event(self, event):
        UIWidget.handle_mouse_event(self, event)

        if event.type == pygame.MOUSEWHEEL:
            for child in self.widgets:
                child.handle_mouse_event(event)
            if self.hover and not any(child.hover for child in self.widgets):
                if pygame.key.get_mods() & (pygame.KMOD_SHIFT | pygame.KMOD_RSHIFT):
                    self.scroll.x -= event.y*20
                    self.scroll.x = min(self.size[0]-self.rect.width, max(0, self.scroll.x))
                else:
                    self.scroll.y -= event.y*20
                    self.scroll.y = min(self.size[1]-self.rect.height, max(0, self.scroll.y))

        else:
            new_pos = (event.pos[0] - self.rect.x + self.scroll.x,
                       event.pos[1] - self.rect.y + self.scroll.y)
            new_event = pygame.event.Event(event.type, {**event.dict, "pos":new_pos})

            for child in self.widgets:
                child.handle_mouse_event(new_event)

    def draw_scrollbar(self, surface: pygame.Surface) -> None:
        """
        draw scrollbar of the frame
        """
        if self.size[1] > self.rect.height:
            visible_ratio = self.rect.height / self.size[1]
            bar_height = max(20, self.rect.height * visible_ratio)
            max_scroll_y = self.size[1] - self.rect.height
            scroll_ratio = self.scroll.y / max_scroll_y if max_scroll_y else 0
            bar_y = self.rect.y + scroll_ratio * (self.rect.height - bar_height)
            pygame.draw.rect(surface, (100, 100, 100),
                            (self.rect.right - 6, bar_y, 4, bar_height),
                            border_radius=2)

        if self.size[0] > self.rect.width:
            visible_ratio = self.rect.width / self.size[0]
            bar_width = max(20, self.rect.width * visible_ratio)
            max_scroll_x = self.size[0] - self.rect.width
            scroll_ratio = self.scroll.x / max_scroll_x if max_scroll_x else 0
            bar_x = self.rect.x + scroll_ratio * (self.rect.width - bar_width)
            pygame.draw.rect(surface, (100, 100, 100),
                            (bar_x, self.rect.bottom - 6, bar_width, 4),
                            border_radius=2)

    def handle_keyboard_event(self, event):
        for child in self.widgets:
            child.handle_keyboard_event(event)

    def render(self, surface: pygame.Surface) -> None:
        if not self.displayed:
            return

        self.surface.fill(self.bg_color)

        for child in self.widgets:
            child.render(self.surface)

        surface_rect = pygame.Rect(self.scroll, self.rect.size)
        surface.blit(self.surface.subsurface(surface_rect), self.rect)

        self.draw_scrollbar(surface)


class Selector(Frame):
    """
    Instance of a selector widget (vertical or horizontal)
    """
    def __init__(self,
                 parent: Optional[UIWidget],
                 rect: pygame.Rect,
                 tools: list[tuple[str, pygame.Surface]],
                 orientation: str = "vertical",
                 bg_color: Optional[tuple[int, ...]]=None
                ) -> None:
        Frame.__init__(self, parent, rect, bg_color=bg_color)
        self.selected = None
        spacing = 40

        for i, (name, icon) in enumerate(tools):
            if orientation == "vertical":
                pos = pygame.Rect(8, 8+i * spacing, 32, 32)
            else:
                pos = pygame.Rect(8+i * spacing, 8, 32, 32)

            SelectorButton(
                self,
                pos,
                name,
                icon,
                self.select_tool
            )

    def select_tool(self, name: str) -> None:
        """
        select a tool by name
        """
        self.selected = name
        for btn in self.widgets:
            if isinstance(btn, SelectorButton):
                btn.active = btn.name == name


class TextList(Frame):
    """
    A dropdown-style text list widget
    - Replié : montre seulement l’élément sélectionné
    - Déplié (hover) : montre la liste entière (avec limite de hauteur)
    """

    def __init__(
        self,
        parent: UIWidget,
        pos: tuple[int, int],
        width: int,
        items: list[str],
        font: pygame.font.Font | None = None,
        text_color=(255, 255, 255),
        bg_color=(57, 61, 71),
        hover_color=(90, 90, 110),
        active_color=(120, 180, 120),
        max_visible_items: int = 8,
    ):
        self.items = items
        self.font = font or pygame.font.SysFont("consolas", 16)
        self.text_color = text_color
        self.hover_color = hover_color
        self.active_color = active_color

        self.selected_index: int = 0 if items else -1
        self.selected_text: str | None = items[0] if items else None
        self.hover_index: int = -1

        self.item_height = self.font.get_linesize() + 4
        self.max_visible_items = max_visible_items

        Frame.__init__(self,
                       parent,
                       pygame.Rect(pos, (width, self.item_height)),
                       height = len(self.items)*self.item_height,
                       bg_color=bg_color)

        self.collapsed_height = self.item_height
        self.expanded_height = min(len(items), max_visible_items) * self.item_height

        self.expanded = False

    def handle_mouse_event(self, event: pygame.event.Event) -> None:
        Frame.handle_mouse_event(self, event)

        if event.type == pygame.MOUSEMOTION:
            self.expanded = self.hover
            if self.expanded:
                self.rect.height = self.expanded_height
                posy = event.pos[1] - self.rect.y + self.scroll.y
                self.hover_index = int(posy // self.item_height)
            else:
                self.rect.height = self.collapsed_height
                self.hover_index = -1

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.expanded:
            posy = event.pos[1] - self.rect.y + self.scroll.y
            idx = int(posy // self.item_height)
            if 0 <= idx < len(self.items):
                self.selected_index = idx
                self.selected_text = self.items[idx]

    def render(self, surface: pygame.Surface) -> None:
        if not self.displayed:
            return

        self.surface.fill(self.bg_color)

        if self.expanded:
            for i, text in enumerate(self.items):
                y = i * self.item_height
                rect = pygame.Rect(0, y, self.rect.width, self.item_height)

                if i == self.selected_index:
                    pygame.draw.rect(self.surface, self.active_color, rect)
                elif i == self.hover_index:
                    pygame.draw.rect(self.surface, self.hover_color, rect)

                txt_surf = self.font.render(text, True, self.text_color)
                self.surface.blit(txt_surf, (5, y + 2))
        else:
            rect = pygame.Rect(0, 0, self.rect.width, self.item_height)
            pygame.draw.rect(self.surface, self.active_color, rect)
            if self.selected_text:
                txt_surf = self.font.render(self.selected_text, True, self.text_color)
                self.surface.blit(txt_surf, (5, 2))

        surface_rect = pygame.Rect((0, 0), self.rect.size)
        if self.expanded:
            surface_rect.x = self.scroll.x
            surface_rect.y = self.scroll.y
        surface.blit(self.surface.subsurface(surface_rect), self.rect)

        if self.expanded:
            self.draw_scrollbar(surface)
        pygame.draw.rect(surface, (0, 0, 0), self.rect.inflate(2, 2), width=2)


class Popup(Frame):
    """
    Virtual modal popup
    """
    def __init__(self, parent_surface: pygame.Surface, rect: pygame.Rect, title: str="Popup",
                 height: Optional[int]=None,
                 width: Optional[int]=None):
        Frame.__init__(self, None, rect, height=height, width=width)
        self.parent_surface = parent_surface
        self.title = title
        self.running = True

        # generate screen background
        self.bg = self.parent_surface.copy()
        surf = pygame.Surface(self.bg.get_size(), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 128))
        self.bg.blit(surf, (0, 0))

        # colors
        self.bg_color = (255, 255, 240)
        self.border_color = (0, 0, 0)

        # close button hitbox
        self.close_rect = pygame.Rect(rect.width - 25, -25, 20, 20)

    def handle_mouse_event(self, event: pygame.event.Event) -> None:
        Frame.handle_mouse_event(self, event)

        # handle popup cross button
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            new_pos = (event.pos[0]-self.rect.x + self.scroll.x,
                       event.pos[1]-self.rect.y + self.scroll.y)
            if self.close_rect.collidepoint(new_pos):
                self.running = False

    def render(self, surface: pygame.Surface):
        Frame.render(self, surface)

        # header
        pygame.draw.rect(surface,
                         (70, 130, 180),
                         pygame.Rect(self.rect.x, self.rect.y-30, self.rect.width, 30),
                         border_top_left_radius=10,
                         border_top_right_radius=10)

        # title
        font = pygame.font.SysFont(None, 24)
        text = font.render(self.title, True, (0, 0, 0))
        surface.blit(text, self.rect.move(10, -22))

        # close button
        surface.fill((200, 50, 50), self.close_rect.move(*self.rect.topleft))
        cross = font.render("X", True, (255, 255, 255))
        cross_rect = cross.get_rect(center=self.close_rect.center).move(*self.rect.topleft)
        surface.blit(cross, cross_rect)

        pygame.draw.rect(surface, self.border_color, self.rect, 2)

    def run(self):
        """
        Popup loop
        """
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                else:
                    self.handle_event(event)

            self.parent_surface.blit(self.bg, (0, 0))

            self.render(self.parent_surface)

            pygame.display.flip()
