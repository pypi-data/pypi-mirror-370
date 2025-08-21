# LogNGraph
*A Python 3.12 package for easily drawing primitives and saving log files*

## Functionality
> ⚠️ You're entering WIP territory ⚠️

### Logs
1. Create Logger instance:
    ```python
    from logngraph.log import Logger
    from logngraph.log.levels import *
    logger = Logger(__name__, filename="my_log_file.txt", level=TRACE)  # Look for everything
                                                          # By default, log level is INFO
    ```
2. Then just log!
    ```python
    logger.trace("When you need to know EVERY detail")
    logger.debug("Diagnosing or troubleshooting an issue")
    logger.info("Something has happened, e.g. started a server")
    logger.warn("Something unexpected has happened,"
                " but code will continue running")
    logger.error("App hit an issue that prevents a certain "
                 "function from working, e.g. payment system is offline"
                 "but the program can still continue running")
    logger.fatal("Something crucial has stopped working, e.g"
                 "lost connection to the main server, can't"
                 "continue running")
    ```
That's it!
You can also change the log level:
```python
logger.set_level(WARNING)
# WARNING was imported earlier from logngraph.log.levels
```

> ⚠️ Here's a hierarchy of log levels: ⚠️
> - TRACE   - e.g. what packets client received from the server
> - DEBUG   - e.g. game server froze, and you need to see why
> - INFO    - e.g. someone said something in chat, and you saved it in logs
> - WARNING - e.g. lost connection to the server temporarily
> - ERROR   - e.g. lost connection to the server completely (timeout, etc.)
> - FATAL   - e.g. client could not find models for the characters
> - NONE    - e.g. you don't want logs ¯\\\_(ツ)\_/¯

> ⚠️ Write to file happens when one of the log methods is called ⚠️

### Graphics
1. Create a Window instance:
    ```python
    from logngraph.graph import Window
    window = Window("My title", "800x800", resizable=True)
    ```
2. Draw primitives:
    ```python
    window.fill("#000000")  # fills whole window with color
    window.rect(0, 0, 100, 100, color="#777777")
    window.rect((10, 10), (250, 50), color="#ff00ff")   # or like this
    window.circle(25, 20, 15)   # at (25, 20) with radius 15
    window.ellipse(0, 0, 80, 100)  # from (0, 0) to (80, 100)
    window.line(0, 0, 800, 900, color="#0000ff")
    window.polygon(750, 750, 800, 400, 35, 600, color="#ff0000")
    # Also you can display text!
   # (font is path to the font file)
    window.write(60, 150, text="Hello, World!", color="#ffffff", bg_color="#000000", antialias=True, size=32, font="Arial.ttf")
    ```
3. And update the screen:
    ```python
    window.update()
    ```
    ⚠️ And if doing this in loop don't forget to `window.handle_quit()`! ⚠️
4. You can also save the screen:
    ```python
    window.screenshot("screenshot.png")
    ```
That's all!

# Installation
Use pip:
```bash
# without graphics
pip install logngraph
# with graphics
pip install logngraph[graph]
```
