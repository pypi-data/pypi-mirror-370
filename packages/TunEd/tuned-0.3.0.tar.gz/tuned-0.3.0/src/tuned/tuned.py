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

import argparse
import sys
import threading
import time
from datetime import timedelta
from queue import Queue, Empty

import numpy as np
import sounddevice as sd

# Import the analyzer and display
from tuned.audio_analyzer import AudioAnalyzer
from tuned.display import TerminalDisplay

# --- Constants and Configuration ---
SAMPLING_RATE = 48000
CHUNK_SIZE = 1024
BUFFER_TIMES = 50

# --- Argument Parsing ---
parser = argparse.ArgumentParser(prog='TunEd', description='Command line Tuner', epilog='')
parser.add_argument('--version', action='version', version='%(prog)s 0.3.0')
parser.add_argument('--verbose', '-v', action='count', default=0, help='Set verbosity level.')
parser.add_argument('--frequency', '-f', action='store', default=440, type=int, help='Set reference frequency.')
parser.add_argument('--mod', '-m', action='store', default='note', choices=['note', 'chord'],
                    help='Set detection mode (note or chord).')
parser.add_argument('--no-harmonics-identification', '-nohi', action='store_false', dest='identify_harmonics',
                    help='Disable harmonic identification for chord detection.')

args = parser.parse_args()

VERBOSE = args.verbose if args.verbose in [0, 1, 2, 3, 4, 6] else 4
REF_FREQ = args.frequency
DETECTION_MODE = args.mod
IDENTIFY_HARMONICS = args.identify_harmonics

if DETECTION_MODE == 'chord':
    default_display = ['chord', 'notes']
else:
    default_display = ['tuner']
    
verbosity_display = {
    0: [],
    1: ['precision'],
    2: ['precision', 'frequency'],
    3: ['precision', 'frequency', 'signal_level'],
    4: ['precision', 'frequency', 'signal_level', 'execution_time'],
    6: ['precision', 'frequency', 'signal_level', 'execution_time', 'egg']
}
to_display = [*default_display, *verbosity_display[VERBOSE]]

# --- Core Application Classes ---

class AudioStreamReader:
    """
    Manages the sounddevice stream. Its sole responsibility is to read raw
    audio data from the microphone and put it into a queue.
    """

    def __init__(self, raw_audio_queue: Queue):
        self.raw_audio_queue = raw_audio_queue
        self.running = False
        self.stream = sd.InputStream(
            samplerate=SAMPLING_RATE,
            blocksize=CHUNK_SIZE,
            channels=1,
            dtype='float32',
            callback=self._callback
        )

    def _callback(self, indata, frames, time, status):
        """This callback is executed in a high-priority thread by sounddevice."""
        if status:
            print(status, file=sys.stderr)
        if self.running:
            self.raw_audio_queue.put(indata.copy())

    def start(self):
        self.running = True
        self.stream.start()

    def stop(self):
        self.running = False
        time.sleep(0.1)
        self.stream.stop()
        self.stream.close()


class ProcessingThread(threading.Thread):
    """
    A thread that consumes raw audio data, processes it using AudioAnalyzer,
    and puts the results into another queue for the UI.
    """

    def __init__(self, raw_audio_queue: Queue, results_queue: Queue, ref_freq: int, detection_mode: str, identify_harmonics: bool):
        super().__init__()
        self.raw_audio_queue = raw_audio_queue
        self.results_queue = results_queue
        self.running = False
        self.analyzer = AudioAnalyzer(
            detection_mode=detection_mode,
            ref_freq=ref_freq,
            sampling_rate=SAMPLING_RATE,
            chunk_size=CHUNK_SIZE,
            buffer_times=BUFFER_TIMES,
            identify_harmonics=identify_harmonics
        )

    def run(self):
        self.running = True
        while self.running:
            try:
                # Get numpy array from the audio reader thread
                raw_frame = self.raw_audio_queue.get(timeout=0.1)
                # The analyzer expects a 1D array, but sounddevice provides a 2D array (frames, channels).
                # .squeeze() removes the singleton dimension (channel) without copying data.
                decoded_frame = raw_frame.squeeze()

                # Perform the heavy computation
                sound = self.analyzer.process_data(decoded_frame)

                # Put the final result in the queue for the UI
                self.results_queue.put(sound)

            except Empty:
                # This is normal if the queue is empty, just continue
                continue

    def stop(self):
        self.running = False


# --- Main Application Logic ---

def tuned():
    """Main function for the TunEd command-line application."""
    raw_audio_queue = Queue()
    results_queue = Queue()
    stream_reader = None
    processing_thread = None
    display = TerminalDisplay(to_display, DETECTION_MODE)

    try:
        # 1. Create and start the audio reader and processing thread
        stream_reader = AudioStreamReader(raw_audio_queue)
        processing_thread = ProcessingThread(raw_audio_queue, results_queue, REF_FREQ, DETECTION_MODE, IDENTIFY_HARMONICS)

        processing_thread.start()
        stream_reader.start()

        display.print_startup_message(REF_FREQ)

        # 2. Main UI loop: get results from the processing thread and display them
        while True:
            start_time = time.perf_counter()
            
            result = results_queue.get()
            
            # Add execution time
            execution_time = timedelta(seconds=time.perf_counter() - start_time).total_seconds()
            
            output_string = display.format_output(result, execution_time)
            display.print_line(output_string)

    except KeyboardInterrupt:
        print("\nExit.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        # 3. Cleanly stop threads and resources
        if processing_thread:
            processing_thread.stop()
            processing_thread.join()  # Wait for the thread to finish
        if stream_reader:
            stream_reader.stop()
        sys.exit()
