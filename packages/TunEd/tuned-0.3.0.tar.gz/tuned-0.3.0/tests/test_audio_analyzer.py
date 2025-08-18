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

import unittest
import numpy as np
from tuned.audio_analyzer import AudioAnalyzer


class TestAudioAnalyzer(unittest.TestCase):

    def setUp(self):
        """Set up a default AudioAnalyzer instance for testing."""
        self.analyzer = AudioAnalyzer(
            ref_freq=440,
            sampling_rate=48000,
            chunk_size=1024,
            buffer_times=50
        )

    def test_compute_frequency_offset(self):
        """Test the calculation of frequency offset in cents."""
        # Test with a frequency slightly sharp
        # A4 is 440Hz, A#4 is ~466.16Hz. The difference is ~26.16Hz.
        # 1 cent step is ~0.26Hz
        # 441Hz is ~+4 cents from 440Hz
        offset = self.analyzer.compute_frequency_offset(441.0, 69) # 441Hz, MIDI for A4
        self.assertEqual(offset, -4) # Sharp means negative offset in this implementation

        # Test with a frequency slightly flat
        offset = self.analyzer.compute_frequency_offset(439.0, 69)
        self.assertEqual(offset, 4) # Flat means positive offset

        # Test with perfect frequency
        offset = self.analyzer.compute_frequency_offset(440.0, 69)
        self.assertEqual(offset, 0)

    def test_process_data_with_harmonics(self):
        """
        Test the full processing pipeline with a generated signal containing a
        fundamental frequency and a louder harmonic. This simulates a real
        instrument and tests the effectiveness of the HPS algorithm.
        """
        # --- Signal Generation ---
        # We generate a signal for A3 (220Hz) but make its first harmonic
        # (A4 at 440Hz) 1.5 times louder. A simple peak-finding algorithm
        # would fail and detect A4. HPS should correctly identify A3.
        sampling_rate = self.analyzer.SAMPLING_RATE
        buffer_length = self.analyzer.CHUNK_SIZE * self.analyzer.BUFFER_TIMES
        
        # Use a frequency that fits the FFT bins to avoid leakage
        fft_len = buffer_length * (1 + self.analyzer.ZERO_PADDING)
        freq_resolution = sampling_rate / fft_len
        
        fundamental_hz = 220.0
        fundamental_bin = round(fundamental_hz / freq_resolution)
        perfect_fundamental_freq = fundamental_bin * freq_resolution
        
        harmonic_freq = perfect_fundamental_freq * 2

        t = np.linspace(0., float(buffer_length) / sampling_rate, buffer_length, endpoint=False)
        
        # Fundamental tone (amplitude 1.0)
        signal = 1.0 * np.sin(2. * np.pi * perfect_fundamental_freq * t)
        # Louder harmonic (amplitude 1.5)
        signal += 1.5 * np.sin(2. * np.pi * harmonic_freq * t)


        # --- Processing ---
        # Simulate feeding the signal chunk by chunk
        chunk_size = self.analyzer.CHUNK_SIZE
        num_chunks = self.analyzer.BUFFER_TIMES
        sound_result = {}
        for i in range(num_chunks):
            chunk = signal[i * chunk_size : (i + 1) * chunk_size]
            sound_result = self.analyzer.process_data(chunk)

        # --- Assertions ---
        # The result should be the fundamental note (A3), not the louder harmonic (A4)
        self.assertIsNotNone(sound_result)
        self.assertEqual(sound_result.note, 'A')
        self.assertEqual(sound_result.octave, 3)
        self.assertAlmostEqual(sound_result.frequency, perfect_fundamental_freq, delta=2.0)
        self.assertLessEqual(abs(sound_result.offset), 10)


class TestAudioAnalyzer442Hz(unittest.TestCase):

    def setUp(self):
        """Set up an AudioAnalyzer instance with a 442Hz reference frequency."""
        self.analyzer = AudioAnalyzer(
            ref_freq=442,
            sampling_rate=48000,
            chunk_size=1024,
            buffer_times=50
        )

    def test_compute_offset_442hz(self):
        """Test frequency offset calculation relative to 442Hz."""
        # A 440Hz signal should be detected as flat (~-8 cents) relative to A4=442Hz
        offset = self.analyzer.compute_frequency_offset(440.0, 69)
        self.assertEqual(offset, 8)

        # A 443Hz signal should be sharp
        offset = self.analyzer.compute_frequency_offset(443.0, 69)
        self.assertEqual(offset, -4)

    def test_process_data_with_harmonics_442hz(self):
        """Test the HPS algorithm with a 442Hz reference."""
        # Signal fundamental is A3 (221Hz for A4=442Hz ref)
        # Louder harmonic is A4 (442Hz)
        sampling_rate = self.analyzer.SAMPLING_RATE
        buffer_length = self.analyzer.CHUNK_SIZE * self.analyzer.BUFFER_TIMES
        fft_len = buffer_length * (1 + self.analyzer.ZERO_PADDING)
        freq_resolution = sampling_rate / fft_len

        fundamental_hz = 221.0
        fundamental_bin = round(fundamental_hz / freq_resolution)
        perfect_fundamental_freq = fundamental_bin * freq_resolution
        harmonic_freq = perfect_fundamental_freq * 2

        t = np.linspace(0., float(buffer_length) / sampling_rate, buffer_length, endpoint=False)
        signal = 1.0 * np.sin(2. * np.pi * perfect_fundamental_freq * t)
        signal += 1.5 * np.sin(2. * np.pi * harmonic_freq * t)

        # --- Processing ---
        chunk_size = self.analyzer.CHUNK_SIZE
        num_chunks = self.analyzer.BUFFER_TIMES
        sound_result = {}
        for i in range(num_chunks):
            chunk = signal[i * chunk_size : (i + 1) * chunk_size]
            sound_result = self.analyzer.process_data(chunk)

        # --- Assertions ---
        # Should detect A3 relative to the 442Hz tuning standard
        self.assertEqual(sound_result.note, 'A')
        self.assertEqual(sound_result.octave, 3)
        self.assertAlmostEqual(sound_result.frequency, perfect_fundamental_freq, delta=2.0)

