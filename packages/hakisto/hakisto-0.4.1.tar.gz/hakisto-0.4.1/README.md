# Hakisto

The name: **Hakisto** means Logger in Esperanto.

## Logging reimagined...

## Simple...

```python
from hakisto import logger

logger.warning('something is fishy...')
```

Starts logging to console and file.

### Example output

```
hakisto-demo-color
```

![](https://gitlab.com/hakisto/logger/-/raw/main/docs/images/demo-color.png)

```
hakisto-demo-critical
```

![](https://gitlab.com/hakisto/logger/-/raw/main/docs/images/demo-critical.png)

```
hakisto-demo-traceback
```

![](https://gitlab.com/hakisto/logger/-/raw/main/docs/images/demo-traceback.png)

## Installation

```
pip install hakisto
```

or get the source from [gitlab.com/hakisto/logger](https://gitlab.com/hakisto/logger/).

## Documentation

[Read the Docs](https://hakisto.readthedocs.io)

## Changes

|   Version | Changes                                                                                                                         |
|----------:|---------------------------------------------------------------------------------------------------------------------------------|
| `0.3.4a0` | Additional options for Click                                                                                                    |
|   `0.3.3` | Option to force location output when logging.                                                                                   |
|   `0.3.2` | Yanked                                                                                                                          |
|   `0.3.1` | Make Logger thread-save.<br />Add legacy logger (alpha).                                                                        |
|   `0.3.0` | Rename setting kwargs keys.<br />Add Click integration.<br />Add environment variables `HAKISTO_COLORS` and `HAKISTO_SEVERITY`. |
|   `0.2.2` | Fix missing import of `rotate_file`.                                                                                            |
|   `0.2.1` | Fix **OSError: [Errno 22] Invalid argument: '<frozen runpy>.log'** when running `hakisto-demo-critical`.                        |
|   `0.2.0` | Add `set_date_format()` to `Logger` and `logger`.                                                                               |
|   `0.1.1` | No functional changes, just making **README** and **Read the Docs** work.                                                       |

splitting to submodules