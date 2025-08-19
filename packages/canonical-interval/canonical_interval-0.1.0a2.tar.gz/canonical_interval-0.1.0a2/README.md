# `canonical-interval`

**Self-normalizing interval data structure that automatically maintains valid form with useful utility methods.**

The `CanonicalInterval` class represents **left-closed, right-open intervals** (`[start, stop)`) that, given a **comparator** (default: `operator.lt`), automatically enforce the following standardized valid form:

- Guarantees `start <= stop` according to the comparator
  - Empty intervals become `[start, start)`
- All operations maintain canonical form

Key Features:

- Automatic Canonicalization  
- Custom Comparison: Supports any comparator function
- Useful Utility Methods:
  - `__bool__`: Determines if the current interval is empty.
  - `relative_position_of(item)`: Determines if `item` is before/within/after the current interval.
  - `three_way_split(target)`: Split a target interval into three parts:
    - Parts of `target` before current interval
    - Overlapping parts between `target` and current interval
    - Parts of `target` after current interval
- Supports Python 2+

## Installation

```commandline
pip install canonical-interval
```

## Examples

```python
from canonical_interval import CanonicalInterval

# Automatically becomes [20, 20) (empty interval)
assert CanonicalInterval(20, 10).start == 20
assert CanonicalInterval(20, 10).stop == 20
assert not CanonicalInterval(20, 10)
assert 15 not in CanonicalInterval(20, 10)

# Automatically becomes ['z', 'z') (empty interval)
assert CanonicalInterval('z', 'a').start == 'z'
assert CanonicalInterval('z', 'a').stop == 'z'
assert not CanonicalInterval('z', 'a')
assert 'm' not in CanonicalInterval('z', 'a')

# Respects custom comparator
# [20, 10) (non-empty interval)
assert CanonicalInterval(20, 10, comparator=lambda a, b: a > b).start == 20
assert CanonicalInterval(20, 10, comparator=lambda a, b: a > b).stop == 10
assert CanonicalInterval(20, 10, comparator=lambda a, b: a > b)
assert 15 in CanonicalInterval(20, 10, comparator=lambda a, b: a > b)

# Respects custom comparator
# ['z', 'a') (non-empty interval)
assert CanonicalInterval('z', 'a', comparator=lambda a, b: a > b).start == 'z'
assert CanonicalInterval('z', 'a', comparator=lambda a, b: a > b).stop == 'a'
assert CanonicalInterval('z', 'a', comparator=lambda a, b: a > b)
assert 'm' in CanonicalInterval('z', 'a', comparator=lambda a, b: a > b)

# Various three-way splits

## Non-empty current
non_empty_current = CanonicalInterval(0, 2)

### Non-empty targets
assert non_empty_current.three_way_split(CanonicalInterval(-3, -1)) == (
    CanonicalInterval(-3, -1), CanonicalInterval(0, 0), CanonicalInterval(2, 2)
)

assert non_empty_current.three_way_split(CanonicalInterval(-2, 0)) == (
    CanonicalInterval(-2, 0), CanonicalInterval(0, 0), CanonicalInterval(2, 2)
)

assert non_empty_current.three_way_split(CanonicalInterval(-1, 1)) == (
    CanonicalInterval(-1, 0), CanonicalInterval(0, 1), CanonicalInterval(2, 2)
)

assert non_empty_current.three_way_split(CanonicalInterval(0, 2)) == (
    CanonicalInterval(0, 0), CanonicalInterval(0, 2), CanonicalInterval(2, 2)
)

assert non_empty_current.three_way_split(CanonicalInterval(0.5, 1.5)) == (
    CanonicalInterval(0, 0), CanonicalInterval(0.5, 1.5), CanonicalInterval(2, 2)
)

assert non_empty_current.three_way_split(CanonicalInterval(1, 3)) == (
    CanonicalInterval(0, 0), CanonicalInterval(1, 2), CanonicalInterval(2, 3)
)

assert non_empty_current.three_way_split(CanonicalInterval(2, 4)) == (
    CanonicalInterval(0, 0), CanonicalInterval(2, 2), CanonicalInterval(2, 4)
)

assert non_empty_current.three_way_split(CanonicalInterval(3, 5)) == (
    CanonicalInterval(0, 0), CanonicalInterval(2, 2), CanonicalInterval(3, 5)
)

### Empty targets
assert non_empty_current.three_way_split(CanonicalInterval(-1, -1)) == (
    CanonicalInterval(-1, -1), CanonicalInterval(0, 0), CanonicalInterval(2, 2)
)

assert non_empty_current.three_way_split(CanonicalInterval(0, 0)) == (
    CanonicalInterval(0, 0), CanonicalInterval(0, 0), CanonicalInterval(2, 2)
)

assert non_empty_current.three_way_split(CanonicalInterval(1, 1)) == (
    CanonicalInterval(0, 0), CanonicalInterval(1, 1), CanonicalInterval(2, 2)
)

assert non_empty_current.three_way_split(CanonicalInterval(2, 2)) == (
    CanonicalInterval(0, 0), CanonicalInterval(2, 2), CanonicalInterval(2, 2)
)

assert non_empty_current.three_way_split(CanonicalInterval(3, 3)) == (
    CanonicalInterval(0, 0), CanonicalInterval(2, 2), CanonicalInterval(3, 3)
)

## Empty current
empty_current = CanonicalInterval(0, 0)

### Non-empty targets
assert empty_current.three_way_split(CanonicalInterval(-3, -1)) == (
    CanonicalInterval(-3, -1), CanonicalInterval(0, 0), CanonicalInterval(0, 0)
)

assert empty_current.three_way_split(CanonicalInterval(-2, 0))  == (
    CanonicalInterval(-2, 0), CanonicalInterval(0, 0), CanonicalInterval(0, 0)
)

assert empty_current.three_way_split(CanonicalInterval(-1, 1)) == (
    CanonicalInterval(-1, 0), CanonicalInterval(0, 0), CanonicalInterval(0, 1)
)

assert empty_current.three_way_split(CanonicalInterval(0, 2)) == (
    CanonicalInterval(0, 0), CanonicalInterval(0, 0), CanonicalInterval(0, 2)
)

assert empty_current.three_way_split(CanonicalInterval(1, 3)) == (
    CanonicalInterval(0, 0), CanonicalInterval(0, 0), CanonicalInterval(1, 3)
)

### Empty targets
assert empty_current.three_way_split(CanonicalInterval(-1, -1)) == (
    CanonicalInterval(-1, -1), CanonicalInterval(0, 0), CanonicalInterval(0, 0)
)

assert empty_current.three_way_split(CanonicalInterval(0, 0))  == (
    CanonicalInterval(0, 0), CanonicalInterval(0, 0), CanonicalInterval(0, 0)
)

assert empty_current.three_way_split(CanonicalInterval(1, 1)) == (
    CanonicalInterval(0, 0), CanonicalInterval(0, 0), CanonicalInterval(1, 1)
)
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).