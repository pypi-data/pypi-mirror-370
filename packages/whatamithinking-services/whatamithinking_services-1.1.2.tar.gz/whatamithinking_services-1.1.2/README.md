# WhatAmIThinking-Services

Cross-platform service library for building platform services that integrate with platform tooling and can be installed/started/stopped/uninstalled from the command line.

## Table of Contents

<!-- TOC -->

- [WhatAmIThinking-Services](#whatamithinking-services)
  - [Table of Contents](#table-of-contents)
  - [Code Usage](#code-usage)
  - [CLI](#cli)
    - [Main](#main)
    - [Install Subcommand](#install-subcommand)
    - [Uninstall Subcommand](#uninstall-subcommand)
    - [Start Subcommand](#start-subcommand)
    - [Stop Subcommand](#stop-subcommand)
  - [Platforms](#platforms)
    - [Windows](#windows)

<!-- /TOC -->

## Code Usage

You should subclass `PlatformService` and override the following methods:

-   `run`: put your core blocking logic for running your service here
    -   call `self.started()` just before you start blocking in this method to signal to the platform that your service has started
    -   call `self.stopped()` just before this returns to signal to the platform your service has stopped
-   `stop`: send signal to stop your service and wait for it to be stopped.

```python
import time
import threading

from whatamithinking.services import PlatformService


class MyService(PlatformService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._event = threading.Event()
        self._exited = threading.Event()

    def run(self):
        self.started()
        self._event.wait()
        self._exited.set()
        self.stopped()

    def stop(self):
        self._event.set()
        self._exited.wait()


if __name__ == '__main__':
    # this will handle commandline params and run your service
    MyService.execute()
```

## CLI

A CLI is included in the service class `execute` method, so you can perform operations such as `install`, `uninstall`, etc.
The following is an example showing the CLI.

### Main

```
usage: My Service [-h] {install,uninstall,start,stop} ...

Description of my service

options:
  -h, --help            show this help message and exit

subcommand:
  {install,uninstall,start,stop}
```

### Install Subcommand

```
usage: My Service install [-h] [--username USERNAME] [--password PASSWORD]

install the service on this machine

options:
  -h, --help           show this help message and exit
  --username USERNAME  domain\username of the account to run the service under
  --password PASSWORD  password of the account to run the service under
```

### Uninstall Subcommand

```
usage: My Service uninstall [-h]

uninstall the service from the machine

options:
  -h, --help  show this help message and exit
```

### Start Subcommand

```
usage: My Service start [-h]

start the service if it is installed or throw error if not

options:
  -h, --help  show this help message and exit
```

### Stop Subcommand

```
usage: My Service stop [-h]

stop the service if it is installed or throw error if not

options:
  -h, --help  show this help message and exit
```

## Platforms

### Windows

NOTE: obscure bug was found when trying to run installer to update
and event viewer was open at same time. servicemanager.pyd file becomes locked up.
turns out event viewer does this. closing event viewer removes this lock.
see: https://mail.python.org/pipermail/python-win32/2004-December/002736.html
