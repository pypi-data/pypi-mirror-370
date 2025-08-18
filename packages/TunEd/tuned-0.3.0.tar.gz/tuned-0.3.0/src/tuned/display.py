"""
Copyright (C) 2025 drd <drd.ltt000@gmail.com>

This file is part of TunEd.

TunEd is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

TunEd is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import random
from .sound import Sound
from .chord import Chord
from .color import Color

GRADIENTS = {
    5: Color.fg.green,
    10: Color.fg.rgb(63, 192, 0),
    15: Color.fg.rgb(127, 128, 0),
    20: Color.fg.rgb(192, 63, 0),
    21: Color.fg.red
}
LEVELS = [" ", " ", "▂", "▃", "▄", "▅", "▇", "█"]
EGGS = ['🯅', '🯆', '🯇', '🯈']

class TerminalDisplay:
    
    def __init__(self, to_display_items: list[str], detection_mode: str = 'note'):
        self.to_display_items = to_display_items
        self.detection_mode = detection_mode
        
    def format_output(self, result: Sound | Chord, execution_time: float) -> str:
        """
        Formats the complete output string
        """
        to_display = f""
        # In chord mode, the result is a Chord object. In note mode, it's a Sound.
        if self.detection_mode == 'chord' and isinstance(result, Chord):
            to_display = self.format_chord(result)
        elif self.detection_mode == 'note' and isinstance(result, Sound):
            to_display = self.format_note(result)
                            
        to_display_dict = {
            'execution_time': self._display_execution_time(execution_time),
            'egg': self._display_egg()
        }
        
        active_display_items = [f"[{to_display_dict[d]}]" for d in self.to_display_items if d in to_display_dict and to_display_dict[d]]
        
        return f"{to_display} {''.join(active_display_items)}"
    
    def format_note(self, sound: Sound) -> str:
        """
        Formats the complete output string for note mode.
        """
        to_display_dict = {
            'tuner': self._display_tuner(sound),
            'precision': self._display_precision(sound),
            'frequency': self._display_frequency(sound),
            'phase': self._display_phase(sound),
            'signal_level': self._display_signal_level(sound),
        }
        active_display_items = [f"[{to_display_dict[d]}]" for d in self.to_display_items if d in to_display_dict and to_display_dict[d]]
                
        return "".join(active_display_items)
    
    def format_chord(self, chord: Chord) -> str:
        """
        Formats the complete output string for chord mode.
        """
        to_display_dict = {
            'chord': self._display_identified_chord(chord),
            'notes': self._display_chord_notes(chord)
        }
        
        active_display_items = [f"{to_display_dict[d]}" for d in self.to_display_items if d in to_display_dict and to_display_dict[d]]
        
        return "".join(active_display_items)
        
    def _display_tuner(self, sound: Sound) -> str:
        """
        Generates the visual tuner string.
        ❱ ₋₄₅ │││││││││││┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃ G 1 │││││││││││││││││││││││││││││││││││││││││││││ ₊₄₅ ❰
        """
        abs_offset = abs(sound.offset)
        color = Color.fg.red
        if 0 <= abs_offset <= 5: color = GRADIENTS[5]
        elif 6 <= abs_offset <= 10: color = GRADIENTS[10]
        elif 11 <= abs_offset <= 15: color = GRADIENTS[15]
        elif 16 <= abs_offset <= 20: color = GRADIENTS[20]

        if abs_offset > 45: abs_offset = 45
        add = 45 - abs_offset
        left_offset = right_offset = 0
        right_add = left_add = 45
        l_arrow_color = l_max_color = r_max_color = r_arrow_color = Color.fg.darkgrey
        if sound.offset < 0:
            left_offset, right_offset = abs_offset, 0
            left_add, right_add = add, 45
            l_arrow_color = color
            if sound.offset <= -45: l_max_color = color
        elif sound.offset > 0:
            left_offset, right_offset = 0, abs_offset
            left_add, right_add = 45, add
            r_arrow_color = color
            if sound.offset >= 45: r_max_color = color

        l_arrow = f"{l_arrow_color}❱{Color.reset}"
        l_max = f"{l_max_color}₋₄₅{Color.reset}"
        l_offset = f"{Color.fg.darkgrey}{'│' * left_add}{color}{'┃' * left_offset}{Color.reset}"
        r_offset = f"{color}{'┃' * right_offset}{Color.fg.darkgrey}{'│' * right_add}{Color.reset}"
        c_note = f"{color}{sound.note:^2}{Color.reset}"
        c_octave = f"{color}{sound.octave:1}{Color.reset}"
        r_max = f"{r_max_color}₊₄₅{Color.reset}"
        r_arrow = f"{r_arrow_color}❰{Color.reset}"

        return f"{l_arrow} {l_max} {l_offset} {c_note}{c_octave} {r_offset} {r_max} {r_arrow}"
    
    def _display_identified_chord(self, chord: Chord) -> str:
        """
        Formats the output string for identified chord
            [ ¯\\_(ツ)_/¯ ]
            [   A sus4    ]
        """
        chord_name = f"[{Color.fg.red}¯\\_(ツ)_/¯{Color.reset}]"
        
        if chord.quality:
            chord_name = f"[{chord.name:^10}]"
            
        return f"{Color.bold}{chord_name}{Color.reset}"
    
    def _display_chord_notes(self, chord: Chord) -> str:
        """
        Formats the output string for the notes composing chord
            [E 1 +15¢][A 1 +12¢][D 2  +4¢][G 2  +8¢]
            [E 1 +15¢  41.02㎐ 115.0㏈][A 1 +12¢  54.84㎐ 112.0㏈][D 2  +4¢  73.59㎐ 135.0㏈][G 2  +8¢  97.97㎐ 131.0㏈]
        """
        chord_parts = []
        for sound in chord.notes:
            abs_offset = abs(sound.offset)
            color = Color.fg.red
            if 0 <= abs_offset <= 5: color = GRADIENTS[5]
            elif 6 <= abs_offset <= 10: color = GRADIENTS[10]
            elif 11 <= abs_offset <= 15: color = GRADIENTS[15]
            elif 16 <= abs_offset <= 20: color = GRADIENTS[20]
            
            note_str = f"{Color.bold}{color}{sound.note:^2}{sound.octave:1}{Color.reset}"
            
            to_display_dict = {
                'precision': self._display_precision(sound),
                'frequency': self._display_frequency(sound),
                'phase': self._display_phase(sound),
                'signal_level': self._display_signal_level(sound),
            }

            active_display_items = [f"{to_display_dict[d]}" for d in self.to_display_items if d in to_display_dict and to_display_dict[d]]
            chord_parts.append(f"[{note_str} {' '.join(active_display_items)}]")
        
        notes_display = "".join(chord_parts)
        
        return f"{notes_display}"
    
    @staticmethod
    def _display_precision(sound: Sound) -> str:
        """
        Formats the output string for precision
        """
        abs_offset = abs(sound.offset)
        color = Color.fg.red
        if 0 <= abs_offset <= 5: color = GRADIENTS[5]
        elif 6 <= abs_offset <= 10: color = GRADIENTS[10]
        elif 11 <= abs_offset <= 15: color = GRADIENTS[15]
        elif 16 <= abs_offset <= 20: color = GRADIENTS[20]
        
        return f"{color}{sound.offset:+3}¢{Color.reset}"
    
    @staticmethod
    def _display_frequency(sound: Sound) -> str:
        """
        Formats the output string for frequency
        """
        return f"∿ {sound.frequency:6}㎐"
    
    @staticmethod
    def _display_signal_level(sound: Sound) -> str:
        """
        Formats the output string for signal level
        """
        db = round(sound.magnitude_to_db, 0)
        level_index = min(int(abs(db // 15)), len(LEVELS) - 1)
        
        return f"{LEVELS[level_index]} {db:5}㏈"
    
    @staticmethod    
    def _display_phase(sound: Sound) -> str:
        """
        Formats the output string for phase
        """
        return f"φ {round(sound.phase, 0):+2}㎭"
    
    @staticmethod
    def _display_execution_time(execution_time) -> str:
        """
        Formats the output string for execution time
        """
        return f"⧖ {execution_time:8}″"
    
    @staticmethod
    def _display_egg() -> str:
        """
        Formats the output string for easter egg
        """
        return f"{random.choice(list(GRADIENTS.values()))}{random.choice(EGGS)}{Color.reset}"
    
    def print_line(self, text: str):
        """Prints a line of text to the console, overwriting the current line."""
        # Using ANSI escape code \033[K to clear the line from cursor to end
        print(f"\r{text}\033[K", end='')

    def print_startup_message(self, ref_freq: int):
        """Prints the initial message when the application starts."""
        print(f"{Color.bold} {self.detection_mode} @ {ref_freq}㎐{Color.reset}")