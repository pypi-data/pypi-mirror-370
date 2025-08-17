import re, pyfiglet, getpass
from typing import Union
from pyfiglet import FigletFont

class CliMeta(type):
    def __getattr__(cls, name: str) -> str:
        parts = name.split("_")
        ansi_seq = ""
        symbol = None

        for part in parts:
            if part in cls.COLORS:
                ansi_seq += cls.COLORS[part]
            elif part in cls.STYLES:
                ansi_seq += cls.STYLES[part]
            elif part in cls.SYMBOLS:
                symbol = cls.SYMBOLS[part]

        if symbol:
            if symbol in ("?", "!", "<", ">", "#", "$"):
                return f"[{ansi_seq}{symbol}{cls.COLORS['reset']}]"
            return f"{ansi_seq}{symbol}{cls.COLORS['reset']}"

        return ansi_seq or cls.COLORS["reset"]

class cli(metaclass=CliMeta):
    COLORS = {
        "black": "\033[30m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "gray": "\033[90m",
        "brown": "\033[33m",
        "pink": "\033[95m",
        "purple": "\033[35m",
        "orange": "\033[38;5;208m",
        "violet": "\033[38;5;93m",
        "reset": "\033[0m",
    }

    STYLES = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "faint": "\033[2m",
        "italic": "\033[3m",
        "underline": "\033[4m",
        "blink": "\033[5m",
        "bg": "\033[7m",
        "hidden": "\033[8m",
        "strike": "\033[9m",
        "overline": "\033[53m",
    }

    SYMBOLS = {
        "dot": "●",
        "line": "┃",
        "q": "?",
        "warning": "!",
        "leftarrow": "<",
        "rightarrow": ">",
        "hash": "#",
        "dollar": "$",
    }

    @staticmethod
    def banner(
        logo,
        style=5,
        align="center",
        top_space=0,
        bottom_space=0,
        text=None,
        text_align="left",
        text_top_space=0,
        text_bottom_space=0,
        width=80,
        logo_color="white",  
        text_color="white",
    ):
        fonts = FigletFont.getFonts()
        font_count = len(fonts)
        choice = style
        if 1 <= choice <= font_count:
            font_name = fonts[choice - 1]
        else:
            font_name = "slant"

        logo = pyfiglet.figlet_format(logo, font=font_name)

        def pad(text: str, width: int, mode: str = "left") -> str:
            vis_len = len(re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]").sub("", text))
            if mode == "left":
                return text + " " * (width - vis_len)
            elif mode == "right":
                return " " * (width - vis_len) + text
            elif mode == "center":
                space = width - vis_len
                left = space // 2
                right = space - left
                return " " * left + text + " " * right
            else:
                return text + " " * (mode - vis_len)

        if top_space > 0:
            logo = "\n".join([" " * width] * top_space + logo.split("\n"))

        if bottom_space > 0:
            logo = "\n".join(logo.split("\n") + [" " * width] * bottom_space)

        lines = logo.split("\n")

        if isinstance(align, int):
            lines = [pad(line, align, "left") for line in lines]
        elif align in ["left", "right", "center"]:
            lines = [pad(line, width, align) for line in lines]
        else:
            raise ValueError("align should be 'left', 'right', 'center' or integer")

        color_code = cli.COLORS.get(logo_color, cli.COLORS["white"])
        reset_code = cli.COLORS["reset"]
        logo = "\n".join([f"{color_code}{line}{reset_code}" for line in lines])

        if text:
            aligned_text = []
            if text_top_space > 0:
                aligned_text.extend([" " * width] * text_top_space)
            for line in text:
                if isinstance(text_align, int):
                    padded = pad(line, text_align, "left")
                elif text_align in ["left", "right", "center"]:
                    padded = pad(line, width, text_align)
                else:
                    raise ValueError("text_align should be 'left', 'right', 'center' or integer")

                aligned_text.append(f"{cli.COLORS.get(text_color, cli.COLORS['white'])}{padded}{reset_code}")

            if text_bottom_space > 0:
                aligned_text.extend([" " * width] * text_bottom_space)

            if text_top_space == 0:
                logo = "\n".join([logo] + aligned_text)
            else:
                logo = "\n".join([logo, *aligned_text])

        print(logo)

    @staticmethod
    def text(
        message: str,
        left_padding: int = 0,
        top_margin: int = 0,
        bottom_margin: int = 0,) -> None:

        for _ in range(top_margin):print()
        
        print(f"{' ' * left_padding} {message}{cli.COLORS['reset']}")
        
        for _ in range(bottom_margin):print()

    @staticmethod
    def _visible_len(text: str) -> int:
        return len(re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]').sub('', text))

    @staticmethod
    def table_box(
        *tables,
        width: Union[int, str] = 'auto',
        content_color: str = COLORS['white'],
        title_color: str = COLORS['white'],
        line_color: str = COLORS['white'],
        left_padding: int = 0,
        top_margin: int = 0,
        bottom_margin: int = 0,
        style: str = "smooth",
        spacing: int = 0,
    ) -> None:

        tables = [tables] if not isinstance(tables[0], (list, tuple)) else tables

        styles = {
            "box":    {"tl": "┌─", "tr": "┐", "bl": "└─", "br": "┘", "h": "─", "v": "│"},
            "box1":   {"tl": "+-", "tr": "+", "bl": "+", "br": "+", "h": "-", "v": "|"},
            "smooth": {"tl": "╭─", "tr": "╮", "bl": "╰─", "br": "╯", "h": "─", "v": "│"},
            "plain": {"tl": " ", "tr": " ", "bl": " ", "br": " ", "h": " ", "v": " ",},
            "simple": {"tl": "-", "tr": " ", "bl": "", "br": " ", "h": "-", "v": " ",},
            "simple1": {"tl": "─", "tr": " ", "bl": "", "br": " ", "h": "─", "v": " ",},
            "simple2": {"tl": "=", "tr": " ", "bl": "", "br": " ", "h": "=", "v": " ",},
            "simple3": {"tl": "▼", "tr": " ", "bl": "", "br": " ", "h": "▼", "v": " ",},
            "simple4": {"tl": "↕", "tr": " ", "bl": "", "br": " ", "h": "↕", "v": " ",},
            "simple5": {"tl": "↹", "tr": " ", "bl": "", "br": " ", "h": "↹", "v": " ",},
            "simple6": {"tl": "⍼", "tr": " ", "bl": "", "br": " ", "h": "⍼", "v": " ",},
            "simple7": {"tl": "⤢", "tr": " ", "bl": "", "br": " ", "h": "⤢", "v": " ",},
            "simple8": {"tl": "░", "tr": " ", "bl": "", "br": " ", "h": "░", "v": " "},
            "bold_box": {"tl": "┏━", "tr": "┓", "bl": "┗━", "br": "┛", "h": "━", "v": "┃"},
            "double_box": {"tl": "╔═", "tr": "╗", "bl": "╚═", "br": "╝", "h": "═", "v": "║"},
        }
        
        s = styles.get(style, styles["smooth"])

        def render_table(title: str, lines: list, pad_left: bool = False) -> list:
            expanded = []
            for ln in lines:
                if isinstance(ln, str) and "\n" in ln:
                    expanded.extend(ln.strip("\n").splitlines())
                else:
                    expanded.append(ln)
            lines = expanded

            if width == "auto":
                max_line_length = max((cli._visible_len(line) for line in lines), default=0)
                title_length = cli._visible_len(title) + 4 if title else 0
                box_width = max(max_line_length + 4, title_length + 4)
            else:
                box_width = width

            inner_width = box_width - 2
            left_space = " " * left_padding if pad_left else ""

            if title:
                padding = inner_width - cli._visible_len(title) - 2
                if padding < 1:
                    padding = 1
                top = (
                    f"{left_space}{s['tl']} {title_color}{title}{cli.reset} "
                    f"{line_color}{s['h'] * (padding - 1)}{s['tr']}{cli.reset}"
                )
            else:
                top = f"{left_space}{s['tl']}{s['h'] * (inner_width-1)}{s['tr']}"

            content = []
            for line in lines:
                spaces = " " * (inner_width - 2 - cli._visible_len(line))
                content.append(
                    f"{left_space}{line_color}{s['v']}{cli.reset} "
                    f"{content_color}{line}{cli.reset}{spaces} "
                    f"{line_color}{s['v']}{cli.reset}"
                )

            if not style in ('box1', 'simple', 'simple1', 'simple2', 'simple3', 'simple4', 'simple5', 'simple6', 'simple7', 'simple8'):
                bottom = f"{left_space}{s['bl']}{s['h'] * (inner_width - 1)}{s['br']}"
            else:
                bottom = f"{left_space}{s['bl']}{s['h'] * (inner_width)}{s['br']}"

            return [line_color + top + cli.reset] + content + [line_color + bottom + cli.reset]

        rendered_tables = []
        for idx, table in enumerate(tables):
            if table and table[0] is None:
                title = None
                lines = table[1:]
            else:
                title = table[0] if table else None
                lines = table[1:] if title else table
            rendered_tables.append(render_table(title, list(lines), pad_left=(idx == 0)))

        max_height = max(len(t) for t in rendered_tables)
        for i, t in enumerate(rendered_tables):
            if len(t) < max_height:
                rendered_tables[i] += [" " * len(t[0])] * (max_height - len(t))

        final_lines = []
        for row_idx in range(max_height):
            row_parts = [tbl[row_idx] for tbl in rendered_tables]
            final_lines.append((" " * spacing).join(row_parts))

        output = ("\n" * top_margin) + "\n".join(final_lines) + ("\n" * bottom_margin)
        print(output)


    @staticmethod
    def input(prompt: str, default: str = "", password: bool = False, allow_empty: bool = True, allow_none: bool = False, left_padding: int = 0, top_margin: int = 0) -> str:
        padding = " " * left_padding

        full_prompt = (("\n" * top_margin) + f"{padding}{cli.green_q} {prompt} ")

        if password:
            data = getpass.getpass(full_prompt)
        else:
            data = input(full_prompt)

        if not data.strip():
            if default:
                return default
            if allow_none:
                return None
            if not allow_empty:
                while not data.strip():
                    if password:
                        data = getpass.getpass(full_prompt)
                    else:
                        data = input(full_prompt)

        return data
