# Mobly Android Partner Tools

This is a suite of command-line tools used for Android partner testing based
on the [Mobly framework](https://github.com/google/mobly).

Use cases include the [BeToCQ test suite](https://github.com/android/betocq).

## Requirements

* Python 3.11 or above

## Installation instructions

**If you have already installed a test suite that includes these tools, such as
BeToCQ, you may skip this step.**

Open a new terminal and run the following installation commands.

```bash
# on Linux

python3 -m venv venv
source venv/bin/activate
python3 -m pip install mobly-android-partner-tools
```
```cmd
:: on Windows

python -m venv venv
venv\Scripts\activate
python -m pip install mobly-android-partner-tools
```

## Mobly test runner

The Mobly test runner is a tool that serves as the entry point for executing a
given Mobly test or suite.

Refer to the dedicated [README](src/mobly_runner/README.md) for more details.

## Results uploader

The results uploader is a tool that allows partners to upload test results to
a shared test storage, where they may then review and debug the results with 
Google.

Refer to the dedicated [README](src/results_uploader/README.md) for more details.
