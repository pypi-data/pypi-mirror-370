import operator
import sys
from enum import Enum

if sys.version_info < (3, 3):
    from collections import Container
else:
    from collections.abc import Container


class RelativePosition(Enum):
    BEFORE = 1
    WITHIN = 2
    AFTER = 3


class CanonicalInterval(Container):
    """A canonical interval with customizable comparison.

    An interval represents all values x where start <= x < stop according to the
    provided comparator. The interval automatically maintains canonical form where
    start <= stop according to the comparator.

    Attributes:
        start: The start of the interval
        stop: The end of the interval
        comparator: The comparison function

    Example:
        >>> interval = CanonicalInterval(10, 20)
        >>> 10 in interval
        True
        >>> 20 in interval
        False
        >>> interval.relative_position_of(15)
        <RelativePosition.WITHIN: 2>
    """
    __slots__ = ('start', 'stop', 'comparator')

    def __new__(cls, start, stop, comparator=operator.lt):
        """Create a new canonical interval instance.

        Ensures the interval is in canonical form where stop is not "less than" start
        according to the comparator.

        Args:
            start: The start of the interval
            stop: The end of the interval (exclusive)
            comparator: Comparison function (default: operator.lt)
        """
        if comparator(stop, start):
            stop = start

        instance = super(CanonicalInterval, cls).__new__(cls)
        instance.start = start
        instance.stop = stop
        instance.comparator = comparator
        return instance

    def __bool__(self):
        return self.comparator(self.start, self.stop)

    def __eq__(self, other):
        if isinstance(other, CanonicalInterval):
            return self.start == other.start and self.stop == other.stop and self.comparator == other.comparator
        return NotImplemented

    def __hash__(self):
        return hash(self.__reduce__())

    def __reduce__(self):
        return self.__class__, (self.start, self.stop, self.comparator)

    def __repr__(self):
        return '%s(%r, %r, %r)' % (type(self).__name__, self.start, self.stop, self.comparator)

    def relative_position_of(self, item):
        """Determine the position of an item relative to the interval.

        Args:
            item: The item to check

        Returns:
            RelativePosition: The position of the item relative to the interval

        Example:
            >>> interval = CanonicalInterval(10, 20)
            >>> interval.relative_position_of(5)
            <RelativePosition.BEFORE: 1>
            >>> interval.relative_position_of(15)
            <RelativePosition.WITHIN: 2>
        """
        if self.comparator(item, self.start):
            return RelativePosition.BEFORE
        elif self.comparator(item, self.stop):
            return RelativePosition.WITHIN
        else:
            return RelativePosition.AFTER

    def __contains__(self, item):
        """Check if an item is contained in the interval.

        Args:
            item: The item to check

        Returns:
            bool: True if item is in the interval, False otherwise
        """
        return self.relative_position_of(item) == RelativePosition.WITHIN

    def three_way_split(self, target):
        """Split a target interval into three parts:
        - Parts of target before current interval
        - Overlapping parts between target and current interval
        - Parts of target after current interval

        Args:
            target: The target interval to split against

        Returns:
            tuple: (before, within, after) CanonicalIntervals, possibly empty (start==stop)

        Raises:
            ValueError: If comparators don't match

        Example:
            >>> i1 = CanonicalInterval(10, 20)
            >>> i2 = CanonicalInterval(15, 25)
            >>> before, within, after = i1.three_way_split(i2)
            >>> before
            (10, 10)
            >>> within.start, within.stop
            (15, 20)
            >>> after.start, after.stop
            (20, 25)
        """
        if self.comparator != target.comparator:
            raise ValueError('self.comparator != target.comparator')

        self_start = self.start
        self_stop = self.stop

        target_start = target.start
        target_stop = target.stop

        comparator = self.comparator

        relative_position_of_target_start = self.relative_position_of(target_start)
        relative_position_of_target_stop = self.relative_position_of(target_stop)

        if relative_position_of_target_start == RelativePosition.BEFORE:
            before_start = target_start

            if relative_position_of_target_stop == RelativePosition.BEFORE:
                before_stop = target_stop

                within_start = self_start
                within_stop = self_start

                after_start = self_stop
                after_stop = self_stop
            elif relative_position_of_target_stop == RelativePosition.WITHIN:
                before_stop = self_start

                within_start = self_start
                within_stop = target_stop

                after_start = self_stop
                after_stop = self_stop
            else:
                before_stop = self_start

                within_start = self_start
                within_stop = self_stop

                after_start = self_stop
                after_stop = target_stop
        elif relative_position_of_target_start == RelativePosition.WITHIN:
            before_start = self_start
            before_stop = self_start

            within_start = target_start

            if relative_position_of_target_stop == RelativePosition.WITHIN:
                within_stop = target_stop

                after_start = self_stop
                after_stop = self_stop
            else:
                within_stop = self_stop

                after_start = self_stop
                after_stop = target_stop
        else:
            before_start = self_start
            before_stop = self_start

            within_start = self_stop
            within_stop = self_stop

            after_start = target_start
            after_stop = target_stop

        return (
            CanonicalInterval(before_start, before_stop, comparator),
            CanonicalInterval(within_start, within_stop, comparator),
            CanonicalInterval(after_start, after_stop, comparator)
        )
