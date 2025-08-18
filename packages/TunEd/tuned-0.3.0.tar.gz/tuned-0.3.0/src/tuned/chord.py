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
import bisect
from dataclasses import replace

from .sound import Sound
from .music_theory import frequency_to_midi

# Dictionary of chord formulas (intervals in semitones from the root)
# We start simple with major and minor triads.
CHORD_FORMULAS = {
    # Accords a 3 sons
    "Maj": (0, 4, 7), # F 3 5
    "min": (0, 3, 7), # F 3m 5
    "sus4": (0, 5, 7), # F 4 5
    "sus2": (0, 2, 7), # F 2 5
    "dim": (0, 3, 6), # F 3m b5
    "aug": (0, 4, 8), # F 3 #5
    # Accords a 4 sons
    # "7": (0,), # F 3 5 7
    # "Maj7": (0, 4, 7, 11), # F 3 5 Maj7
    # "min7": (0, 3, 7, 11), # F 3m 5 7
}


class Chord:
    """
    Represents a musical chord, analyzed from a list of sounds.
    It can identify which sounds are harmonics and stores this information
    within each Sound object.
    """

    def __init__(self, sounds: list[Sound], ref_freq: int = 440, identify_harmonics: bool = True):
        self.sounds: list[Sound] = sorted(sounds, key=lambda s: s.frequency)
        self.ref_freq = ref_freq
        
        if identify_harmonics and self.sounds:
            self.sounds = self._identify_harmonics_optimized(self.sounds)

        self.notes = [s for s in self.sounds if not s.is_harmonic]
        self.harmonics = [s for s in self.sounds if s.is_harmonic]
        
        self.bass_note: Sound | None = self.notes[0] if self.notes else None
        self.root: Sound | None = None
        self.quality: str | None = None
        self.name: str = "Unknown"

        if len(self.notes) >= 2:  # We need at least 2 notes for a chord
            self._analyze()
        elif self.bass_note:
            self.name = f"Note {self.bass_note.note}"

    def _identify_harmonics_optimized(self, sounds: list[Sound], tolerance=0.05, max_harmonics=5) -> list[Sound]:
        """
        Identifies harmonic frequencies from a list of sounds using an optimized O(n log n) approach.
        Returns a new list of Sound objects with the `is_harmonic` flag set.
        """
        if len(sounds) < 2:
            return sounds

        # Prepare data structures for efficient lookup
        sorted_freqs = [s.frequency for s in sounds]
        harmonic_freqs = set()

        # Iterate through each sound, considering it as a potential fundamental
        for i, s in enumerate(sounds):
            # If this sound has already been identified as a harmonic of a lower fundamental, skip it.
            if s.frequency in harmonic_freqs:
                continue

            # For the current fundamental, search for its harmonics in the rest of the list.
            for n in range(2, max_harmonics + 1):
                target_harmonic = s.frequency * n
                
                # Define the search range based on tolerance
                lower_bound = target_harmonic * (1 - tolerance)
                upper_bound = target_harmonic * (1 + tolerance)

                # Use binary search (bisect) to find potential matches efficiently.
                # Find the insertion point for the lower bound.
                start_index = bisect.bisect_left(sorted_freqs, lower_bound, lo=i + 1)

                # Check all frequencies from the start index until they exceed the upper bound.
                for j in range(start_index, len(sorted_freqs)):
                    candidate_freq = sorted_freqs[j]
                    if candidate_freq > upper_bound:
                        # We've gone past the search window for this harmonic.
                        break
                    
                    # We found a harmonic.
                    harmonic_freqs.add(candidate_freq)

        # Build the final list with updated Sound objects
        final_sounds = []
        for s in sounds:
            if s.frequency in harmonic_freqs:
                final_sounds.append(replace(s, is_harmonic=True))
            else:
                final_sounds.append(s)
        
        return final_sounds

    def _analyze(self):
        """
        The main logic to identify the root and quality of the chord.
        This method operates on the fundamental notes.
        """
        # Get the unique MIDI numbers of each fundamental note
        midi_notes = sorted(list(set([frequency_to_midi(s.frequency, self.ref_freq) for s in self.notes])))

        # Try each note as a potential root
        for i, potential_root_midi in enumerate(midi_notes):
            # Calculate the intervals relative to this root
            intervals = tuple(sorted([(note - potential_root_midi) % 12 for note in midi_notes]))

            # Compare with our known formulas
            for quality, formula in CHORD_FORMULAS.items():
                if intervals == formula:
                    # We found it!
                    self.quality = quality
                    # The root is the note corresponding to the MIDI we were testing
                    self.root = self.notes[i]
                    self.name = f"{self.root.note} {self.quality}"
                    return  # Stop the analysis

        # If we didn't find anything, name the chord by its bass note
        if self.bass_note:
            self.name = f"Chord bass {self.bass_note.note}"