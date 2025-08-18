# Logger WIKI

[Ref: Loguru](https://loguru.readthedocs.io/en/stable/)

### Usage
```python
configure_logger()
logger.info(
    "Logs with user",
    ctx={
        "user_id": "123",
        "role": "admin",
        "name": "Name",
        "subject": "123",
    },
    user=User(name="Name", age=20, id=123),
)
logger.info("Logs for Anonymous", user=Anonymous)
logger.info("Simple log")
```
**Result**
```json
2025-01-25 15:04:05.883 | INFO     | main:lifespan:20 - Logs with user (User: Name - 123)
{ 'name': 'Name',
  'role': 'admin',
  'subject': '123',
  'user_id': '123'}
2025-01-25 15:04:05.886 | INFO     | main:lifespan:30 - Logs for Anonymous (Anonymous)
2025-01-25 15:04:29.193 | INFO     | main:lifespan:32 - Simple log
```

### Environment variables
**Default**
```
LOGGER__CONSOLE=True - Enable logs to console(terminal)
LOGGER__CONSOLE_LEVEL="INFO" - Log level for console(terminal)
LOGGER__CONSOLE_TIME_FORMAT="YYYY-MM-DD HH:mm:ss.SSS" - Time format for console view
LOGGER__FILE=True - Enable logs to file
LOGGER__FILE_LEVEL="TRACE" - Log level for file
LOGGER__FILE_ROTATION="1 month" - Rotation for files
LOGGER__FILE_COMPRESSION="zip" - Compression for files
LOGGER__FILE_DIR="logs" - Directory for logs files
LOGGER__FILE_TIME_FORMAT="ddd-DD HH:mm:ss.SSS" - Time format for file view
LOGGER__FILE_NAME="{time:YYYY-MMM-DD}.log" - Logs file name format
LOGGER__CTX_WIDTH=50 - Max print width of context
LOGGER__CTX_INDENT=2 - Indent of context
LOGGER__CTX_UNDERSCORE_NUMBERS=True - Enable underscore in numbers (1_000_000)
LOGGER__CTX_COMPACT=True - Enable compact view - list items in single line
LOGGER__CTX_DEPTH=3 - Max depth of context (for DEBUG is disable)
```