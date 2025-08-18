from __future__ import annotations

import re
import pendulum
from zlib import crc32
from enum import Enum
from functools import cached_property
from dataclasses import dataclass

from .exceptions import LRCParseError, LRCUnsupportedType, LCRMissingTime
from .regex import LRC_LINE, TIME_TAG


@dataclass(repr=False, eq=False, order=False)
class LRCEvent:
    class Type(str, Enum):
        Comment = "#"  # Comments
        Title = "ti"  # Title of the song
        Artist = "ar"  # Artist performing the song
        Album = "al"  # Album the song is from
        Author = "au"  # Author of the song
        Lyricist = "lr"  # Lyricist of the song
        Length = "length"  # Length of the song (mm:ss)
        FileAuthor = "by"  # Author of the LRC file (not the song)
        Offset = "offset"  # Specifies a global offset value for the lyric times, in milliseconds
        Creator = "re"  # The player or editor that created the LRC file
        Version = "ve"  # The version of the program
        TimedLyric = "lyric"  # [mm:ss.xx]text

    time: pendulum.Duration | None = None
    repeat_time: pendulum.Duration | None = None
    data: str = ""
    type: Type = Type.TimedLyric

    @cached_property
    def is_lyric(self) -> bool:
        return self.type is self.Type.TimedLyric

    @property
    def id(self) -> str:
        """Compute an ID from the LCR data."""
        checksum = crc32(self.compose.encode("utf8"))
        return hex(checksum)

    @property
    def time_code(self) -> str:
        """
        Convert time to LRC time code format [mm:ss.xx].
        :raises LCRMissingTime: If time is not set.
        """
        if self.is_lyric:
            if self.time is None:
                raise LCRMissingTime("Time must be set to generate time code.")
            return self._convert_time_to_code(self.time)

        return ""

    @property
    def repeat_time_code(self) -> str | None:
        """
        Convert repeat time to LRC time code format [mm:ss.xx].
        :return: Repeat time code string in the format [mm:ss.xx] or None if not set.
        """
        if self.is_lyric:
            if self.repeat_time is None:
                return None
            return self._convert_time_to_code(self.repeat_time)

        return ""

    @property
    def compose(self) -> str:
        """
        Compose the LRC event into a string format.
        Returns:
            str: The composed LRC event string.
        :raises LCRMissingTime: If time is required but not set for certain types.
        :raises LRCUnsupportedType: If the type is not recognized.
        """
        if isinstance(self.type, self.Type):
            if self.type == self.Type.TimedLyric:
                if self.time is None:
                    raise LCRMissingTime("Time must be set for timed lyric.")
                if self.repeat_time:
                    return f"[{self.time_code}][{self.repeat_time_code}]{self.data}"
                return f"[{self.time_code}]{self.data}"
            else:
                return f"[{self.type.value}:{self.data}]"

        raise LRCUnsupportedType(f"Unknown LRCEvent type: {self.type}")

    @classmethod
    def from_string(cls, lrc_string: str) -> "LRCEvent" | None:
        """
        Parse a string to create an LRCEvent.
        """
        if not (line_re := re.match(LRC_LINE, lrc_string)):
            raise LRCParseError(f"Invalid LRC event format: {lrc_string}")

        gd = line_re.groupdict()

        # Handle ID tags like [ti:Title]
        if tag := gd.get("tag"):
            return cls(time=None, data=f"{gd['value'].strip()}", type=cls.Type(tag))

        # Handle offset
        if gd.get("offset"):
            return cls(time=None, data=gd["offset"].strip(), type=cls.Type.Offset)

        # Handle comments
        if gd.get("comment"):
            return cls(time=None, data=gd["comment"].strip(), type=cls.Type.Comment)

        if gd.get("lyric") is not None:
            text = gd["lyric"].strip()
            timestamps = re.findall(TIME_TAG, lrc_string)

            time = None
            repeat_time = None

            time = pendulum.duration(
                minutes=int(timestamps[0][0]),
                seconds=int(timestamps[0][1]),
                milliseconds=int(timestamps[0][2] or 0) * 10,
            )

            if len(timestamps) > 1:
                # TODO: Handle repeat time if it can be multiple
                repeat_time = pendulum.duration(
                    minutes=int(timestamps[1][0]),
                    seconds=int(timestamps[1][1]),
                    milliseconds=int(timestamps[1][2] or 0) * 10,
                )

            return cls(time=time, repeat_time=repeat_time, data=text)

        raise LRCParseError(f"Unrecognized LRC event: {lrc_string}")

    def _convert_time_to_code(self, time: pendulum.Duration) -> str:
        """
        Convert a pendulum Duration to LRC time code format [mm:ss.xx].
        :param time: pendulum Duration object.
        :return: Time code string in the format [mm:ss.xx].
        """
        total_seconds = time.total_seconds()
        minutes, seconds = divmod(total_seconds, 60)
        return f"{int(minutes):02}:{seconds:05.2f}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LRCEvent):
            if self.time:
                if not isinstance(other.time, pendulum.Duration):
                    return False

                return (
                    self.time.total_seconds() == other.time.total_seconds()
                    and self.repeat_time == other.repeat_time
                    and self.data == other.data
                    and self.type == other.type
                )
            return self.data == other.data and self.type == other.type
        else:
            raise TypeError("Cannot compare to non-LRCEvent object")

    def __ne__(self, other: object) -> bool:
        eq_result = self.__eq__(other)
        if eq_result is NotImplemented:
            return NotImplemented
        return not eq_result

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, LRCEvent):
            return NotImplemented
        if self.time is None or other.time is None:
            return False
        return self.time < other.time

    def __le__(self, other: object) -> bool:
        if not isinstance(other, LRCEvent):
            return NotImplemented
        if self.time is None or other.time is None:
            return False
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, LRCEvent):
            return NotImplemented
        if self.time is None or other.time is None:
            return False
        return not self.__le__(other)

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, LRCEvent):
            return NotImplemented
        if self.time is None or other.time is None:
            return False
        return not self.__lt__(other)

    def __repr__(self) -> str:
        if self.is_lyric:
            return f"<LRCEvent time={self.time_code} repeat_time={self.repeat_time_code} text={self.data!r} type={self.type.name}>"
        else:
            return f"<LRCEvent text={self.data!r} type={self.type.name}>"
