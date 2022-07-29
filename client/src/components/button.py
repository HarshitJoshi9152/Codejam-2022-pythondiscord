from typing import Callable

import pygame


class Button:
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        text: str,
        font_size: int,
        bgColor: pygame.Color,
        color: pygame.Color,
        onclick: Callable,
        screen_surface: pygame.surface,
    ):
        self.text = text
        self.font_size = font_size
        self.bgColor = bgColor
        self.color = color if color is not None else pygame.Color(0, 0, 0)
        self.screen_surface = screen_surface
        self.onclick = onclick
        self.rect = pygame.Rect(x, y, w, h)
        self.text_rect = pygame.Rect(x, y, w, h)

        # centering the text inside the rect
        font = pygame.font.SysFont(None, font_size)
        t_w, t_h = font.size(text)  # text width , height

        # if t_w > w:
        #     print("ERROR: text doesn't fit inside the rect !")

        padding_x = (w - t_w) / 2
        padding_y = (h - t_h) / 2

        self.text_rect = pygame.Rect(x + padding_x, y + padding_y, w, h)

        self.img = font.render(text, True, self.color)  # we dont need to store text btw

    def update(self, events_list):
        for event in events_list:
            if event.type == pygame.MOUSEBUTTONUP:
                # checking if click is inside the rect
                x, y = pygame.mouse.get_pos()
                if self.rect.x < x and x < self.rect.x + self.rect.width:
                    if self.rect.y < y and y < self.rect.y + self.rect.height:
                        self.onclick()

    def render(self):
        pygame.draw.rect(
            self.screen_surface, self.bgColor, self.rect, 0
        )  # 0 borderWidth means fill

        self.screen_surface.blit(self.img, self.text_rect)
