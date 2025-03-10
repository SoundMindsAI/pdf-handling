# Logs Directory

This directory contains log files generated by the PDF processing pipeline and individual scripts. Log files are automatically created with timestamps in their names for easy identification and tracking.

## Log File Format

Log files are named using the format:
```
pdf_processing_YYYYMMDD_HHMMSS.log
```

For example: `pdf_processing_20250226_211530.log`

## Log File Contents

Each log file contains detailed information about the execution of the scripts, including:

- Timestamps for each log entry
- Module names that generated each log entry
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Detailed error tracebacks when exceptions occur
- Step-by-step execution flow
- Command arguments and execution times

## Log Levels

The system uses the following log levels:

- **DEBUG**: Detailed information, typically useful only for diagnosing problems
- **INFO**: Confirmation that things are working as expected
- **WARNING**: Indication that something unexpected happened, but the process can continue
- **ERROR**: Due to a more serious problem, the process couldn't perform a specific function
- **CRITICAL**: A serious error indicating the program itself may be unable to continue running

## Usage

You can adjust the log level when running the pipeline using the `--log-level` argument:

```bash
python pdf_processing_pipeline.py --log-level=DEBUG
```

Options include: DEBUG, INFO, WARNING, ERROR, CRITICAL (default is INFO).

## Log Rotation

Log files are not automatically deleted. If you need to free up space, you can safely remove older log files from this directory.
