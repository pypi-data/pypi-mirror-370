"""
Copyright (C) 2025 drd <drd.ltt000@gmail.com>

This file is part of TunEd.

TunEd is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

TunEd is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS for a PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

class Color:
    """
    A container for ANSI color and style codes for terminal output.
    """
    # Styles
    reset: str = '\033[0m'
    bold: str = '\033[1m'
    dim: str = '\033[2m'  # Corresponds to 'disable' or 'faint'
    underline: str = '\033[4m'
    reverse: str = '\033[7m'  # Swaps foreground and background colors
    strikethrough: str = '\033[9m'
    invisible: str = '\033[8m'  # Hides the text

    class fg:
        """Foreground colors."""
        black: str = '\033[30m'
        red: str = '\033[31m'
        green: str = '\033[32m'
        yellow: str = '\033[33m'
        blue: str = '\033[34m'
        magenta: str = '\033[35m'
        cyan: str = '\033[36m'
        white: str = '\033[37m'
        darkgrey: str = '\033[90m'

        @staticmethod
        def rgb(r: int, g: int, b: int) -> str:
            """
            Returns the ANSI escape code for a 24-bit RGB foreground color.
            
            Args:
                r: Red component (0-255).
                g: Green component (0-255).
                b: Blue component (0-255).
            
            Returns:
                The ANSI escape code string.
            """
            return f"\033[38;2;{r};{g};{b}m"

    class bg:
        """Background colors."""
        black: str = '\033[40m'
        red: str = '\033[41m'
        green: str = '\033[42m'
        yellow: str = '\033[43m'
        blue: str = '\033[44m'
        magenta: str = '\033[45m'
        cyan: str = '\033[46m'
        white: str = '\033[47m'
        darkgrey: str = '\033[100m'

        @staticmethod
        def rgb(r: int, g: int, b: int) -> str:
            """
            Returns the ANSI escape code for a 24-bit RGB background color.
            
            Args:
                r: Red component (0-255).
                g: Green component (0-255).
                b: Blue component (0-255).
            
            Returns:
                The ANSI escape code string.
            """
            return f"\033[48;2;{r};{g};{b}m"
