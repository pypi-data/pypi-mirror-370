from logngraph.graph import *
from time import sleep

window = Window("Windows 12", 900, 900, True)

while window.running:
    window.handle_quit()
    window.fill("#00ff00")
    window.circle(0, 0, 150, color="#999999")
    window.rect(150, 50, 200, 150, color="#ffffff")
    window.ellipse(250, 250, 300, 500, color="#ffff00")
    window.line(0, 0, 800, 900, color="#0000ff")
    window.polygon(750, 750, 800, 400, 35, 600, color="#ff0000")
    window.write(60, 150, text="Hello, World!", color="#ffffff", bg_color="#000000", antialias=True, size=32, font="font.ttf")
    window.update()
    sleep(0.05)
