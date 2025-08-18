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
import numpy as np
import scipy.fft
from scipy.signal import find_peaks

from tuned.chord import Chord
from tuned.sound import Sound
from tuned.music_theory import frequency_to_midi, midi_to_ansi_note, midi_to_frequency 


class AudioAnalyzer:
    """
    A class dedicated to audio signal analysis to detect musical notes.
    This class is designed to be used within a separate processing thread.
    It takes raw audio data, processes it, and returns note information.
    It does not handle audio streaming or threading itself.
    """

    ZERO_PADDING = 3  # times the buffer length
    NUM_HPS = 3  # Harmonic Product Spectrum

    def __init__(self,
                 detection_mode='note',  # 'note' or 'chord'
                 ref_freq=440,
                 sampling_rate=48000,
                 chunk_size=1024,
                 buffer_times=50,
                 identify_harmonics=True):
        """
        Initializes the analyzer with audio processing parameters.
        """
        if detection_mode not in ['note', 'chord']:
            raise ValueError("detection_mode must be 'note' or 'chord'")
        self.detection_mode = detection_mode
        self.ref_freq = ref_freq
        self.SAMPLING_RATE = sampling_rate
        self.CHUNK_SIZE = chunk_size
        self.BUFFER_TIMES = buffer_times
        self.identify_harmonics = identify_harmonics

        # Initialize buffer, hanning window, and FFT frequencies
        self.buffer = np.zeros(self.CHUNK_SIZE * self.BUFFER_TIMES)
        self.hanning_window = np.hanning(len(self.buffer))
        fft_len = len(self.buffer) * (1 + self.ZERO_PADDING)
        self.frequencies = scipy.fft.fftfreq(fft_len, 1. / self.SAMPLING_RATE)

    def process_data(self, decoded_frame):
        """
        Processes a chunk of audio data to detect the note.
        This is the core method to be called by the processing thread.
        """
        # 1. Update the internal buffer with the new frame
        self.buffer = np.roll(self.buffer, -self.CHUNK_SIZE)
        self.buffer[-self.CHUNK_SIZE:] = decoded_frame

        # 2. Apply windowing, padding, and perform FFT
        pad = np.pad(self.buffer * self.hanning_window, (0, len(self.buffer) * self.ZERO_PADDING), "constant")
        fft = scipy.fft.fft(pad)
        magnitude_data = abs(fft)
        magnitude_data = magnitude_data[:len(magnitude_data) // 2]

        # 3. Apply Harmonic Product Spectrum (HPS) for fundamental frequency enhancement.
        # This is crucial for real-world sounds where harmonics can be louder
        # than the fundamental frequency.
        magnitude_data_orig = magnitude_data.copy()
        for i in range(2, self.NUM_HPS + 1, 1):
            hps_len = int(np.ceil(len(magnitude_data) / i))
            magnitude_data[:hps_len] *= magnitude_data_orig[::i]

        # 4. Detect the note from the processed spectrum
        if self.detection_mode == 'note':
            sounds = self.note_detection(magnitude_data, self.frequencies, fft)
        else:  # 'chord'
            sounds = self.chord_detection(magnitude_data, self.frequencies, fft)

        return sounds

    def note_detection(self, magnitude_data, frequencies, fft_data) -> list[Sound]:
        """
        Finds the loudest frequency and converts it to a musical note.
        """
        magnitude = np.max(magnitude_data)
        magnitude_to_db = 20 * np.log10(magnitude + 1e-9)
        index_loudest = np.argmax(magnitude_data)
        frequency = round(frequencies[index_loudest], 2)
        phase = np.angle(fft_data[index_loudest])
        midi_note = frequency_to_midi(frequency, self.ref_freq)
        note, octave = midi_to_ansi_note(midi_note)
        offset = self.compute_frequency_offset(frequency, midi_note)
        return Sound(
            magnitude=magnitude,
            magnitude_to_db=0 if np.isnan(magnitude_to_db) else magnitude_to_db,
            phase=phase,
            frequency=frequency,
            note=note,
            octave=octave,
            offset=offset
        )

    def chord_detection(self, magnitude_data, frequencies, fft_data) -> Chord:
        """
        Finds all prominent frequencies and passes them to the Chord class for analysis.
        """
        # Use a lower prominence since HPS has already amplified the fundamentals.
        # Distance helps to avoid detecting multiple peaks on the same broad note.
        peaks, _ = find_peaks(magnitude_data, prominence=10000, distance=50) # prominence=1000>=60db, prominence=10000>=80db, prominence=100000>=100db

        detected_sounds = []
        for peak_index in peaks:
            frequency = round(frequencies[peak_index], 2)
            if frequency == 0:
                continue

            magnitude = magnitude_data[peak_index]
            magnitude_to_db = 20 * np.log10(magnitude + 1e-9)
            phase = np.angle(fft_data[peak_index])
            midi_note = frequency_to_midi(frequency, self.ref_freq)
            note, octave = midi_to_ansi_note(midi_note)
            offset = self.compute_frequency_offset(frequency, midi_note)

            sound = Sound(
                magnitude=magnitude,
                magnitude_to_db=0 if np.isnan(magnitude_to_db) else magnitude_to_db,
                phase=phase,
                frequency=frequency,
                note=note,
                octave=octave,
                offset=offset
            )
            detected_sounds.append(sound)

        return Chord(detected_sounds, ref_freq=self.ref_freq, identify_harmonics=self.identify_harmonics)

    def compute_frequency_offset(self, frequency, midi_note):
        """
        Calculates the offset of a frequency from the nearest perfect semitone.
        """
        nearest_midi_note_frequency = midi_to_frequency(midi_note, self.ref_freq)
        frequency_offset = nearest_midi_note_frequency - frequency
        if frequency_offset == 0:
            return 0
        next_note = midi_note
        if frequency_offset > 0:
            next_note += 1
        elif frequency_offset < 0:
            next_note -= 1
        semitone_step = abs((nearest_midi_note_frequency - midi_to_frequency(next_note, self.ref_freq)) / 100)
        if semitone_step == 0:
            return 0
        offset = round(frequency_offset / semitone_step)
        return offset
