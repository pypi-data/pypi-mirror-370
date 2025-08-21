# loudstream

A file-streaming Python API around [libebur128](https://github.com/jiixyj/libebur128/tree/master/ebur128).

## Install

```bash
uv sync
```

## To Use

```python
# To measure
import loudstream as ls
meter = ls.Meter()
lkfs = meter.measure("some-file.wav")

# To normalize
target = -14
ls.normalize("some-file.wav", "output.wav", target)
```

## Running Tests

```bash
uv run pytest
```

