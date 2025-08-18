import datetime
import time

PRETTY_SHORT_FORMAT: str = '%Y-%m-%d %H:%M'

class Duration(int):
    """
    A Duration represents some length in time in milliseconds.
    """

    def to_secs(self) -> float:
        """ Convert the duration to float seconds. """

        return self / 1000.0

    def to_msecs(self) -> int:
        """ Convert the duration to integer milliseconds. """

        return self

class Timestamp(int):
    """
    A Timestamp represent a moment in time (sometimes called "datetimes").
    Timestamps are internally represented by the number of milliseconds since the
    (Unix Epoch)[https://en.wikipedia.org/wiki/Unix_time].
    This is sometimes referred to as "Unix Time".
    Since Unix Time is in UTC, timestamps do not need to carry timestamp information with them.

    Note that timestamps are just integers with some decoration,
    so they respond to all normal int functionality.
    """

    def sub(self, other: 'Timestamp') -> Duration:
        """ Return a new duration that is the difference of this and the given duration. """

        return Duration(self - other)

    def to_pytime(self, timezone: datetime.timezone = datetime.timezone.utc) -> datetime.datetime:
        """ Convert this timestamp to a Python datetime in the given timezone (UTC by default). """

        return datetime.datetime.fromtimestamp(self / 1000, timezone)

    def to_local_pytime(self) -> datetime.datetime:
        """ Convert this timestamp to a Python datetime in the system timezone. """

        local_timezone = datetime.datetime.now().astimezone().tzinfo
        if ((local_timezone is None) or (not isinstance(local_timezone, datetime.timezone))):
            raise ValueError("Could not discover local timezone.")

        return self.to_pytime(timezone = local_timezone)

    def pretty(self, short: bool = False, timezone: datetime.timezone = datetime.timezone.utc) -> str:
        """
        Get a "pretty" string representation of this timestamp.
        There is no guarantee that this representation can be parsed back to its original form.
        """

        pytime = self.to_pytime(timezone = timezone)

        if (short):
            return pytime.strftime(PRETTY_SHORT_FORMAT)

        return pytime.isoformat(timespec = 'milliseconds')

    @staticmethod
    def from_pytime(pytime: datetime.datetime) -> 'Timestamp':
        """ Convert a Python datetime to a timestamp. """

        return Timestamp(int(pytime.timestamp() * 1000))

    @staticmethod
    def now() -> 'Timestamp':
        """ Get a Timestamp that represents the current moment. """

        return Timestamp(time.time() * 1000)
