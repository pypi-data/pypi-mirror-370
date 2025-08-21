import pygame
from logngraph.errors import *

__all__ = [
    "Window",
]

class Window:
    def __init__(self, title: str = "Window", width: int = 800, height: int = 600, resizable: bool = True) -> None:
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE if resizable else 0)
        pygame.display.set_caption(title)

        self.running = True

    def fill(self, color: tuple[int, int, int] | str) -> None:
        self.screen.fill(color)

    def update(self) -> None:
        if self.running:
            pygame.display.flip()

    def stop(self) -> None:
        self.running = False

    def handle_quit(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def screenshot(self, filename: str) -> None:
        pygame.image.save(self.screen, filename)

    def rect(self, *args: float | tuple[float, float], color="#ffffff") -> None:
        if len(args) == 4:
            x1, y1, x2, y2 = args
        elif len(args) == 2:
            (x1, y1), (x2, y2) = args
        else:
            raise InvalidArgsError(f"Could not unpack args: {args}")
        pygame.draw.rect(self.screen, color, (x1, y1, x2, y2))

    def ellipse(self, *args: float | tuple[float, float], color="#ffffff") -> None:
        if len(args) == 4:
            x1, y1, x2, y2 = args
        elif len(args) == 2:
            (x1, y1), (x2, y2) = args
        else:
            raise InvalidArgsError(f"Could not unpack args: {args}")
        pygame.draw.ellipse(self.screen, color, (x1, y1, x2, y2))

    def circle(self, *args: float | tuple[float, float], color="#ffffff") -> None:
        if len(args) == 3:
            x, y, r = args
        elif len(args) == 2:
            (x, y), r = args
        else:
            raise InvalidArgsError(f"Could not unpack args: {args}")
        r = float(r)
        pygame.draw.circle(self.screen, color, (x, y), r)

    def line(self, *args: float | tuple[float, float], color="#ffffff") -> None:
        if len(args) == 4:
            x1, y1, x2, y2 = args
        elif len(args) == 2:
            (x1, y1), (x2, y2) = args
        else:
            raise InvalidArgsError(f"Could not unpack args: {args}")
        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2))

    def polygon(self, *args: float | tuple[float, float], color="#ffffff") -> None:
        if len(args) % 2 == 0:
            points = []
            for i in range(0, len(args), 2):
                points.append((args[i], args[i + 1]))
        else:
            raise InvalidArgsError(f"Could not unpack args: {args}")
        pygame.draw.polygon(self.screen, color, points)

    def write(self, *args: int | tuple[int, int], text: str = "", color="#ffffff", bg_color="#000000", antialias: bool = True, font: pygame.font.Font | str = "font.ttf", size: int = 16) -> None:
        if type(font) is str:
            font = pygame.font.Font(font, size)
        text = font.render(text, antialias, color, bg_color)
        textRect = text.get_rect()
        if len(args) == 2:
            textRect.center = (args[0], args[1])
        elif len(args) == 1:
            textRect.center = args[0]
        else:
            raise InvalidArgsError(f"Could not unpack args: {args}")
        self.screen.blit(text, textRect)

