import pygame
from scenes.scene import Scene

WIDTH, HEIGHT = 800, 600
WHITE = pygame.Color(255, 255, 255)

pygame.font.init()


class Loading_screen(Scene):
    def __init__(
        self,
        switch_scene,
    ):
        print("Scene Loading_screen starts !")
        self.screen = pygame.display.get_surface()
        self.scene_ended = False
        # writing Loading on the screen
        font_size = 40
        font = pygame.font.SysFont(None, font_size)
        text = "Loading"
        text_color = WHITE
        self.loading_img = font.render(text, True, text_color)

        t_w, t_h = font.size(text)
        x_padding = 80
        y_padding = 65

        x = WIDTH - t_w - x_padding
        y = HEIGHT - t_h - y_padding

        self.text_rect = pygame.Rect(x, y, 10, 10)

        # loading bars
        self.bars = []
        bar_x = x + t_w + 10
        bar_w = 10
        self.bar_h = t_h - 5
        bar_padding = 5
        bars_count = 3

        for i in range(bars_count):
            bar = pygame.Rect(bar_x, y - 5, bar_w, self.bar_h)
            bar_x += bar_w + bar_padding
            self.bars.append(bar)

        # REGISTERING event to animate the bars
        # Every event type can have a separate timer attached to it. It is
        # best to use the value between pygame.USEREVENT and pygame.NUMEVENTS.
        self.UPDATE_BARS = pygame.USEREVENT + 1
        self.t = 50
        pygame.time.set_timer(self.UPDATE_BARS, self.t)
        self.delta_h = [-2, -3, -4]  # used to reduce the height of the bars

    def render(self):
        self.screen.fill(pygame.Color(0, 0, 0))
        self.screen.blit(self.loading_img, self.text_rect)

        # spinning circle
        for bar_rect in self.bars:
            pygame.draw.rect(self.screen, WHITE, bar_rect, 0)

    def update(self, events_list):
        # animating the loading bars
        for event in events_list:
            # self.UPDATE_BARS event gets fired every self.t ms (250)
            if event.type == self.UPDATE_BARS:
                for i, bar_rect in enumerate(self.bars, 0):
                    bar_rect.height += self.delta_h[i]
                    bar_rect.y -= self.delta_h[i]
                    # toggling increasing and decreasing the bar
                    if bar_rect.height <= 1:
                        self.delta_h[i] = -self.delta_h[i]
                    elif bar_rect.height >= self.bar_h:
                        self.delta_h[i] = -self.delta_h[i]

    def exit(self):
        print("Scene Loading_screen Over !")
        # To disable the timer for an event, set the milliseconds argument to 0.
        pygame.time.set_timer(self.UPDATE_BARS, 0)
        self.scene_ended = True
        return True
