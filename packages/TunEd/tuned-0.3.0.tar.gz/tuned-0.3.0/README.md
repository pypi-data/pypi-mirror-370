# TunEd

## Description

**TunEd** is a command-line tuning tool.

## Dependencies

- Python >= 3.12
- sounddevice >= 0.4.6
- numpy >= 1.26.4
- scypy >= 1.16.1

**TunEd** use **sounddevice** library to stream audio from your computer's microphone.

**sounddevice** need install of **PortAudio**.

- For Debian / Ubuntu Linux:

```bash
~$ apt-get install portaudio19-dev python-all-dev
```

## Installation

Using pip:

```bash
~ $ pip install tuned
```

With source:

```bash
~ $ git clone https://framagit.org/drd/tuned.git
```

Install requirements:

```bash
~ $ pip install -r requirements_dev.txt
```

To create a python package, go to inside tuned directory:

```bash
~ $ cd tuned
```

Build the package in an isolated environment, generating a source-distribution and wheel in the directory dist/ (<https://build.pypa.io/en/stable/>):

```bash
~$ python -m build
```

To install it:

```bash
~ $ pip install ./dist/tuned-0.3.0-py3-none-any.whl
```

## Usage

Launch TunEd with standard tuning frequency (@440㎐):

```bash
~$ tuned
```

To set a different tuning frequency:

```bash
~$ tuned -f 442
```

To change the detection mode:

- Chord detection:

```bash
~$ tuned -m chord
```

- Note detection (default value):

```bash
~$ tuned -m note
```

You can change the information to display:

```bash
~$ tuned -v
```

- **-v**: Show precision (current value between played note and target note).
- **-vv**: Show precision and current note frequency.
- **-vvv**: Show precision, frequency and current level signal.
- **-vvvv**: Show precision, frequency, level signal and the execution time of the played note calculation.

## Authors

- **drd** - <drd.ltt000@gmail.com> - Main developper

## License

TunEd is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

TunEd is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
