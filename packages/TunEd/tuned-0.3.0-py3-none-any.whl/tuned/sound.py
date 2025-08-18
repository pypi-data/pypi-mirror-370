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
from dataclasses import dataclass, field


@dataclass(frozen=True, order=True)
class Sound:
    """Represents a detected musical sound with its properties."""
    magnitude: float = field(repr=False)
    magnitude_to_db: float
    phase: float = field(repr=False)
    frequency: float
    note: str
    octave: int
    offset: int = field(repr=False)
    is_harmonic: bool = field(default=False, repr=False)

    def is_in_tune(self, tolerance_cents: int = 10) -> bool:
        """Checks if the note is in tune within a given tolerance."""
        return abs(self.offset) <= tolerance_cents