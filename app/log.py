import logging
import sys
import typing as t

import settings

from copy import copy

TRACE_LOG_LEVEL = 5

_ansi_colors = {
    'black': 30,
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37,
    'reset': 39,
    'bright_black': 90,
    'bright_red': 91,
    'bright_green': 92,
    'bright_yellow': 93,
    'bright_blue': 94,
    'bright_magenta': 95,
    'bright_cyan': 96,
    'bright_white': 97,
}
_ansi_reset_all = '\033[0m'


def _interpret_color(
    color: int | tuple[int, int, int] | str,
    offset: int = 0
) -> str:
    if isinstance(color, int):
        return f'{38 + offset};5;{color:d}'

    if isinstance(color, (tuple, list)):
        r, g, b = color
        return f'{38 + offset};2;{r:d};{g:d};{b:d}'

    return str(_ansi_colors[color] + offset)


# code from click package
def style(
    text: t.Any,
    fg: t.Optional[int | tuple[int, int, int] | str] = None,
    bg: t.Optional[int | tuple[int, int, int] | str] = None,
    bold: t.Optional[bool] = None,
    dim: t.Optional[bool] = None,
    underline: t.Optional[bool] = None,
    overline: t.Optional[bool] = None,
    italic: t.Optional[bool] = None,
    blink: t.Optional[bool] = None,
    reverse: t.Optional[bool] = None,
    strikethrough: t.Optional[bool] = None,
    reset: bool = True
) -> str:
    """Styles a text with ANSI styles and returns the new string. By
    default the styling is self contained which means that at the end
    of the string a reset code is issued.  This can be prevented by
    passing ``reset=False``.
    Supported color names:
    * ``black`` (might be a gray)
    * ``red``
    * ``green``
    * ``yellow`` (might be an orange)
    * ``blue``
    * ``magenta``
    * ``cyan``
    * ``white`` (might be light gray)
    * ``bright_black``
    * ``bright_red``
    * ``bright_green``
    * ``bright_yellow``
    * ``bright_blue``
    * ``bright_magenta``
    * ``bright_cyan``
    * ``bright_white``
    * ``reset`` (reset the color code only)
    If the terminal supports it, color may also be specified as:
    -   An integer in the interval [0, 255]. The terminal must support
        8-bit/256-color mode.
    -   An RGB tuple of three integers in [0, 255]. The terminal must
        support 24-bit/true-color mode.
    See https://en.wikipedia.org/wiki/ANSI_color and
    https://gist.github.com/XVilka/8346728 for more information.
    :param text: the string to style with ansi codes.
    :param fg: if provided this will become the foreground color.
    :param bg: if provided this will become the background color.
    :param bold: if provided this will enable or disable bold mode.
    :param dim: if provided this will enable or disable dim mode.  This is
                badly supported.
    :param underline: if provided this will enable or disable underline.
    :param overline: if provided this will enable or disable overline.
    :param italic: if provided this will enable or disable italic.
    :param blink: if provided this will enable or disable blinking.
    :param reverse: if provided this will enable or disable inverse
                    rendering (foreground becomes background and the
                    other way round).
    :param strikethrough: if provided this will enable or disable
        striking through text.
    :param reset: by default a reset-all code is added at the end of the
                  string which means that styles do not carry over.  This
                  can be disabled to compose styles.
    """
    if not isinstance(text, str):
        text = str(text)

    bits = []

    if fg:
        try:
            bits.append(f'\033[{_interpret_color(fg)}m')
        except KeyError:
            raise TypeError(f'Unknown color {fg!r}') from None

    if bg:
        try:
            bits.append(f'\033[{_interpret_color(bg, 10)}m')
        except KeyError:
            raise TypeError(f'Unknown color {bg!r}') from None

    if bold is not None:
        bits.append(f'\033[{1 if bold else 22}m')
    if dim is not None:
        bits.append(f'\033[{2 if dim else 22}m')
    if underline is not None:
        bits.append(f'\033[{4 if underline else 24}m')
    if overline is not None:
        bits.append(f'\033[{53 if overline else 55}m')
    if italic is not None:
        bits.append(f'\033[{3 if italic else 23}m')
    if blink is not None:
        bits.append(f'\033[{5 if blink else 25}m')
    if reverse is not None:
        bits.append(f'\033[{7 if reverse else 27}m')
    if strikethrough is not None:
        bits.append(f'\033[{9 if strikethrough else 29}m')

    bits.append(text)

    if reset:
        bits.append(_ansi_reset_all)

    return ''.join(bits)


# code from uvcorn
class ColourizedFormatter(logging.Formatter):
    """
    A custom log formatter class that:
    * Outputs the LOG_LEVEL with an appropriate color.
    * If a log call includes an `extras={"color_message": ...}` it will be used
      for formatting the output, instead of the plain text message.
    """

    _level_name_colors = {
        TRACE_LOG_LEVEL: lambda lev: style(str(lev), fg='blue', bold=True),
        logging.DEBUG: lambda lev: style(str(lev), fg='cyan', bold=True),
        logging.INFO: lambda lev: style(str(lev), fg='green', bold=True),
        logging.WARNING: lambda lev: style(str(lev), fg='yellow', bold=True),
        logging.ERROR: lambda lev: style(str(lev), fg='red', bold=True),
        logging.CRITICAL: lambda lev: style(str(lev), fg='bright_red', bold=True),  # noqa
    }

    def __init__(
        self,
        fmt: t.Optional[str] = None,
        datefmt: t.Optional[str] = None,
        style: t.Literal['%', '{', '$'] = '%',
        use_colors: t.Optional[bool] = None,
    ):
        if use_colors in (True, False):
            self.use_colors = use_colors
        else:
            self.use_colors = sys.stdout.isatty()

        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def color_level_name(self, level_name: str, level_no: int) -> str:
        def default(level_name: str) -> str:
            return str(level_name)

        func = self._level_name_colors.get(level_no, default)

        return func(level_name)

    def formatMessage(self, record: logging.LogRecord) -> str:
        recordcopy = copy(record)
        levelname = recordcopy.levelname

        if self.use_colors:
            levelname = self.color_level_name(levelname, recordcopy.levelno)

            if 'color_message' in recordcopy.__dict__:
                recordcopy.msg = recordcopy.__dict__['color_message']
                recordcopy.__dict__['message'] = recordcopy.getMessage()

        recordcopy.__dict__['levelname'] = levelname

        return super().formatMessage(recordcopy)


def setup_logger() -> logging.Logger:
    from logging import getLogger, INFO, DEBUG, StreamHandler

    logging_format = '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(message)s'  # noqa
    logging_dt_format = '%Y-%m-%dT%H:%M:%S'

    log = getLogger(settings.LOGGER_NAME)
    log.setLevel(DEBUG)

    formatter = ColourizedFormatter(
        logging_format, logging_dt_format, use_colors=False
    )

    stream_handler = StreamHandler(sys.stdout)
    stream_handler.setLevel(DEBUG if settings.DEV_MODE else INFO)
    stream_handler.setFormatter(formatter)

    log.addHandler(stream_handler)

    return log
