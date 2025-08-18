# pyLRCtool

Library to create and modify lrc files.

# Functionality

- parse lrc files and modify them
- export to srt file
- create new lrc files

# Installation

```
git clone https://github.com/varyg1001/pylrctool
cd pylrctool
pip install .
```

# Library usage

```py
from pathlib import Path

import pendulum
from pylrctool import LRCFile, LRCEvent

lrc_file = LRCFile()
file = Path('test.lrc')

# Both statements below are equivalent
lrc_file.from_file(file)
lrc_file.from_string(file.read_text())

event = LRCEvent(
    time=pendulum.duration(minutes=0, seconds=29, milliseconds=130),
    data="And I ain't gon' kill my vibe",
)
lrc_file.add(event)

title = LRCEvent(data="Don't Be Afraid", type=LRCEvent.Type.Title)
lrc_file.add(title)

# saved to out.lrc
output = Path('out.lrc')
srt.dump(output)
```
