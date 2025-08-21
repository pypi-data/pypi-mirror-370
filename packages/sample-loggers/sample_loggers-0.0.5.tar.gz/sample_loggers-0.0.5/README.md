# Deep Learning Tools for Pytorch

[![Python >= 3.8](https://img.shields.io/badge/python->=3.8-blue.svg)](https://www.python.org/downloads/release/)

This package provides some common configurations to quickly create your own logger through the logging library. 

## Installation

```bash
pip install sample_loggers
```

## Example for using
To ues the logger directly, you can use the `logger` object provided by the package. 
```python
import os
from sample_loggers import logger

# you can set the log dir and log file name through environment variables.
os.environ["LOG_DIR"] = "./output/log"
os.environ["LOG_FILE_NAME"] = "log.txt"

logger.info("hello world")
```

To define your own logger, you can use the `create_logger` method. This method allows you to specify the name of the logger and the log level.
```python
from sample_loggers import create_logger, LEVEL

# The format can be defined as a string, 
# you can refer to the official website 
# https://docs.python.org/3/library/logging.html#logrecord-attributes.
define_format = "Define your own format here, you can use the default format or define your own format."

logger = create_logger(
    logger_name="logger",
    log_level=LEVEL.INFO,
    log_file_name="log.txt",
    output_dir="./output/log",
    format_type="default",
    define_format=define_format
)
```

## Update
- 0.0.5 - improve the default logger.
- 0.0.4post1 - Fix the bug.
- 0.0.4 - Samplify thr method to create logger and provide the default logger that can be used directly.
- 0.0.3post1 - Fix the bug.
- 0.0.3 - Add the level definition.
- 0.0.2post2 - Fix the bug.
- 0.0.2post1 - Fix the bug.
- 0.0.2 - Add the summery and throughput method.
- 0.0.1 - We provide the common config for logging to create logger.

## License

Sample Loggers is MIT licensed. See the [LICENSE](LICENSE) for details.

