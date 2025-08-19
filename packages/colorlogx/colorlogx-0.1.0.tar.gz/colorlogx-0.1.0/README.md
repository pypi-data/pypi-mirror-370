# colorlogx

A simple Python logging helper with **colored console output** and **rotating log files per day**.  
Perfect for small projects where you want readable logs without heavy dependencies.

---

## Features

- ✅ Colored output for different log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)  
- ✅ Rotating file logs with daily naming (`YYYY-MM-DD_<loggername>.log`)  
- ✅ Optional size-based rotation per file (default `~1 MB`) with backups  
- ✅ Configurable log level, log directory, file size, and backup count  
- ✅ Colorized console output can be disabled (`use_colors=False`)  
- ✅ Easy drop-in replacement for `logging.getLogger`

---

## Installation

From PyPI (once published):

```bash
pip install colorlogx
```

From TestPyPI (development):

```bash
pip install -i https://test.pypi.org/simple/ colorlogx
```

---

## Usage

```python
from colorlogx import get_logger

# Create a logger
log = get_logger(
    "myapp",           # logger name
    log_level="DEBUG", # default: DEBUG (supports str or int)
    log_dir="logs",    # default: ./logs
    max_bytes=5000*1024,  # ~5 MB per file before rotation
    backup_count=20,      # number of rotated files to keep
    use_colors=True       # enable colored console output
)

log.debug("This is a debug message")
log.info("This is an info message")
log.warning("This is a warning")
log.error("This is an error")
log.critical("This is critical")
```

Console output example:

```
2025-08-18 20:12:30 | myapp | INFO | main.py:12:<module> | This is an info message
2025-08-18 20:12:30 | myapp | ERROR | main.py:13:<module> | This is an error
```

Log files are written into `logs/YYYY-MM-DD_myapp.log`.  
If the size limit is exceeded on the same day, files roll to `YYYY-MM-DD_myapp.log.1`, `.2`, etc.

---

## Configuration Parameters

| Parameter       | Type     | Default       | Description                                                |
|-----------------|----------|---------------|------------------------------------------------------------|
| `name`          | str      | *required*    | Logger name (used in console and log filename)            |
| `log_level`     | str/int  | `DEBUG`       | Minimum log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |
| `log_dir`       | str      | `"logs"`      | Directory for log files                                    |
| `max_bytes`     | int      | `1000*1024`   | Max log file size before rotating                          |
| `backup_count`  | int      | `20`          | Number of rotated files to keep                            |
| `use_colors`    | bool     | `True`        | Enable/disable colored console output                      |

---

## Tips

- To disable colors in CI or when piping output, set `use_colors=False` or rely on your terminal’s color support.
  ```python
  import os, logging
  level = getattr(logging, os.getenv("LOG_LEVEL", "DEBUG").upper(), logging.DEBUG)
  log = get_logger("myapp", log_level=level)
  ```

---

## License

MIT License © 2025 Tobias Auer
