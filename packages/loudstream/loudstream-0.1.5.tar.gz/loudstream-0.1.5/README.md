# loudstream

A file-streaming Python API around [libebur128](https://github.com/jiixyj/libebur128/tree/master/ebur128).

## Install

```bash
uv sync
```

## To Use

```python
# To measure
from loudstream import Meter

lufs = Meter().measure("some-file.wav")
```

## Running Tests

```bash
uv run pytest
```

