<!--
This code is part of the PyConPTY python package.
PyConPTY: A Python wrapper for the ConPTY (Windows Pseudo-console) API
Copyright (C) 2025  MELWYN FRANCIS CARLO

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

For queries, contact me at: melwyncarlo@gmail.com
-->

# PyConPTY

A Python-based interface for the ConPTY (Windows Pseudo-console) API. <sub>[Check out the PyPI package](https://pypi.org/project/pyconpty/)</sub>

> Your ultimate space to get immensely creative with unique terminals, remote accesses, and interactive and automated processes.
>
> &nbsp; &ndash; &nbsp; Melwyn Francis Carlo

_**Cool Facts:**_
 - No Dependencies!
 - **Thread-safe** <sub>Subject to one thread per ConPTY class instance, i.e., no sharing instances between threads.</sub>
 - 5820 out of 5820 tests passed _(100%)_ <sub>[Check out the tests in action](https://youtu.be/WnRAkLy9tRg)</sub>
 - 100% total coverage <sub>Note that, a few lines of unreachable code have been excluded from coverage as including them involves purposefully introducing errors in the main code.</sub>
 - No one is perfect. <sub>So, kindly report issues or bugs; when submitting issues, it is recommended to append a sample code that is capable of reproducing the bug.</sub>
<br/><br/>

### Pre-requisites

Windows 10 Version 1809 Build 17763 (Windows 10.0.17763)

_Oh, do not worry! The installation process will tell you if it is a match or not. But this is the minimum required._
<br/>

### Install

First, launch one of the following programs:\
[Command Prompt _(cmd.exe)_](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmd), [PowerShell](https://learn.microsoft.com/en-us/powershell/), or [Windows Terminal](https://github.com/microsoft/terminal).

It is always a good practice to call the following command beforehand:

```
pip install --upgrade pip
```
Then, install using the following command:
```
pip install pyconpty
```
If `pip` does not work, then replace `pip` with either `py -m pip`, `python -m pip` or `python3 -m pip` _(whichever works first)_.

If you are still facing issues, then maybe _Python_ is not installed in the first place (as _Pip_ comes bundled with _Python_). In that case, [click here to download Python](https://www.python.org/downloads/).

If you face any issues while using `pyconpty`, you may uninstall it and then try building from source using the following commands:
```
pip uninstall pyconpty
pip install pyconpty --no-cache-dir --no-binary pyconpty
```
<br/>

### Use

- **Example #1**
```py
# Filename: ipconfig_example.py

from pyconpty import ConPTY

console = ConPTY()
console.run("ipconfig")
print(console.getoutput())
```

![Example #1: IPConfig Example - Output](https://raw.githubusercontent.com/melwyncarlo/PyConPTY/refs/heads/main/examples/ipconfig_example.png "Example #1: IPConfig Example - Output")
<br/><br/>

- **Example #2**
```py
# Filename: factorial_example.py

from pyconpty import ConPTY

console = ConPTY()
console.run("factorial.exe", stripinput=True)
number = input(console.getoutput())

if number[0] == "-":
    number_without_minus = number[1:]
else:
    number_without_minus = number

if number_without_minus.isdigit():
    console.sendinput(str(number))
    print(console.getoutput())
else:
    print(" Only integer numbers accepted!\n")

if console.isrunning:
    console.kill()
```

```c
/* Filename: factorial_example.c                           */
/* Build: gcc factorial_example.c -o factorial_example.exe */

#include <stdio.h>

int get_factorial(int number) {
    if (number < 0) {
        return -1;
    } else if ((number == 0) || (number == 1)) {
        return 1;
    } else {
        int factorial = 1;
        for (int i = 1; i <= number; i++) {
            factorial *= i;
        }
        return factorial;
    }
}

int main() {
    int number;
    printf("\n Compute the factorial of: ");
    scanf("%d", &number);
    const int factorial = get_factorial(number);
    if (factorial == -1) {
        printf(" !%d = %s\n", number, "undefined");
    } else {
        printf(" !%d = %d\n", number, factorial);
    }
    return 0;
}
```

![Example #2: Factorial Example - Output](https://raw.githubusercontent.com/melwyncarlo/PyConPTY/refs/heads/main/examples/factorial_example.png "Example #1: Factorial Example - Output")
<br/><br/><br/>

### Make <sub>_(for the mavericks out there)_</sub>

1. Download the [PyConPTY source]() (bundled in a ZIP file).
2. Extract the ZIP file to a folder of your choice.
3. Enter the extracted _PyConPTY_ folder.
4. Launch one of the following programs:\
Command Prompt _(cmd.exe)_, PowerShell, or Windows Terminal.
5. Clean, build and install the package locally:
```
py make.py
```
6. Format the Python files appropriately using [black](https://pypi.org/project/black/):
```
py -m black --diff --color .
```
7. Check the python code syntax using [pylint](https://pypi.org/project/pylint/):
```
py -m pylint .
```
8. Perform relevant tests for the python code using [pytest](https://pypi.org/project/pytest/), [pytest-repeat](https://pypi.org/project/pytest-repeat/), [pytest-rerunfailures](https://pypi.org/project/pytest-rerunfailures/), and [pytest-timeout](https://pypi.org/project/pytest-timeout/):
```
py -m pytest .
```
The test files are located in the `tests` folder.

If unnoticeable problems exist, then you may also rely on the [Microsoft Console Debugger (CDB)](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/debugging-using-cdb-and-ntsd) by downloading the [Windows SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/) and only installing the _Debugging Tools_. [py-spy](https://pypi.org/project/py-spy/) also helps.

After installing the debugging tools, add the following (or similar) filepath to the System/User Environment Path Variables, as it contains the `cdb.exe` program:
`C:\Program Files (x86)\Windows Kits\10\Debuggers\x64`.
<br/>

<u>Testing via CDB</u>:
```
cls; cdb -y "cache*C:\Symbols;srv*http://msdl.microsoft.com/download/symbols;FOLDER_PATH_TO_PDB_FILE" -srcpath "FOLDER_PATH_TO_C_FILE" -lines -c "sxd av; g" python -m pytest .
```

<u>Note that</u>:
- `FOLDER_PATH_TO_PDB_FILE` is the folder location where the Program Database _(\*.pdb)_ file exists.
  - In my case, it was `C:/Users/Admin/AppData/Roaming/Python/Python313/site-packages`.
- `FOLDER_PATH_TO_C_FILE` is the folder location where the Python Extension C _(\*.c)_ file exists.
  - In my case, it was `C:/Users/Admin/Documents/Miscellaneous/PyConPTY/PyPI/src/pyconpty`.

Upon encountering a crash, obtain the line number in the source file pertaining to the crash:
```
kn  (for the current thread in focus)
~*k (for all running threads)
```

For analyzing memory-related issues via the [AddressSanitizer \(ASAN\)](https://learn.microsoft.com/en-us/cpp/sanitizers/asan?view=msvc-170) tool, you will have to copy the _ASAN_ dynamically linked libraries (_DLL_'s) from the Microsoft Visual Studio's Build Tools folder into the `FOLDER_PATH_TO_PDB_FILE` folder.
- In my case, the Microsoft Visual Studio's Build Tools folder was: `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.42.34433\bin\Hostx64\x64`
- In my case, the files copied were:
  - `clang_rt.asan_dynamic-x86_64.dll`
  - `clang_rt.asan_dbg_dynamic-x86_64.dll`
  - `clang_rt.asan_dbg_dynamic-x86_64.pdb`
  - `clang_rt.asan_dynamic-x86_64.pdb`

9. Repeat steps #5 to #8 until successfull.

Note that if the command `py` does not work, then replace it with `python` or `python3` _(whichever works first)_.
<br/><br/><br/>

## Documentation

#### 1. &nbsp; ConPTY *(Class)*
```
ConPTY(width = 80, height = 24)
```
| return | ConPTY |
| - | - |
| width | Integer (1 to 32767) |
| height | Integer (1 to 32767) |

This class creates a ConPTY instance for communicating with ConHost.

Check the [`isinitialized`](#2--isinitialized-property) property to confirm the initialization's success.

`width` and `height` are the pseudo-console's (terminal's) width and height, measured in 'number of characters'. They determine the I/O's internal buffer size and display. If you need the output unwrapped for _N_ characters, then set `width = N + 1`.

Note that out-of-bounds values are automatically capped to their respective limits.

<u>DO NOT</u> share a ConPTY class instance across different threads in multi-threaded environments. Use a different instance instead.

```
Possible Errors:

NONE, NOT_WINDOWS_OS, INCOMPATIBLE_WINDOWS_OS,
CONSOLE_WIDTH_NOT_INT, CONSOLE_HEIGHT_NOT_INT
```
<br/>

#### 2. &nbsp; isinitialized *(Property)*
| return | Boolean |
| - | - |

`True`, if the class ConPTY initialized properly, else `False`.

If `False`, then check the [`lasterror`](#3--lasterror-property) property to determine the reason for failure.

Check this property post-initialization as a safety-check, if the initialization arguments are dynamic and not static.

Using class functions when `isinitialized = False` results in error set by the property `lasterror = ConPTY.Error.CONPTY_UNINITIALIZED`.

```
Possible Errors:

NONE, CONPTY_UNINITIALIZED, NOT_WINDOWS_OS,
INCOMPATIBLE_WINDOWS_OS, CONSOLE_WIDTH_NOT_INT,
CONSOLE_HEIGHT_NOT_INT
```
<br/>

#### 3. &nbsp; lasterror *(Property)*
| return | ConPTY.Error |
| - | - |

This value is one of the many [Error Enumerations](#26--error-enumerations-enum-class) that is generated after each function call. The information for each function in this documentation is appended with a list of possible errors for your reference.

This value indicates whether a function call succeeded or failed.\
If a function call failed, then this value indicates the reason for its failure.

This property is volatile and it must be read/copied immediately after a function returns.

```
Possible Errors:

NONE, CONSOLE_WIDTH_NOT_INT, CONSOLE_HEIGHT_NOT_INT,
NOT_WINDOWS_OS, INCOMPATIBLE_WINDOWS_OS,
COMMAND_LONGER_THAN_32766_CHARS, CONPTY_UNINITIALIZED,
PROCESS_ALREADY_RUNNING, NO_PROCESS_FOUND, KILL_PROCESS_ERROR,
READ_ERROR, WRITE_INTERNAL_ERROR, WRITE_TIMEOUT, RESIZE_ERROR,
RUNTIME_SUCCESS, RUNTIME_ERROR, FORCED_TERMINATION,
RUN_INTERNAL_ERROR, RUN_PROGRAM_NOT_FOUND,
RUN_PROGRAM_ACCESS_DENIED, RUN_PROGRAM_ERROR, DATA_NOT_A_STRING,
COMMAND_NOT_A_STRING, MIN_READ_BYTES_NOT_AN_INT,
MAX_READ_BYTES_NOT_AN_INT, MIN_READ_LINES_NOT_AN_INT,
MAX_READ_LINES_NOT_AN_INT, MIN_MORE_THAN_MAX_READ_BYTES,
MIN_MORE_THAN_MAX_READ_LINES, DATA_NOT_A_LIST_OF_STRINGS,
WAITTILLSENT_NOT_A_BOOLEAN, WAITFOR_NOT_A_NUMBER,
TIMEDELTA_NOT_A_NUMBER, INTERNALTIMEDELTA_NOT_A_NUMBER,
POSTENDDELAY_NOT_A_NUMBER, RAWDATA_NOT_A_BOOLEAN,
STRIPINPUT_NOT_A_BOOLEAN, TRAILINGSPACES_NOT_A_BOOLEAN,
CONSOLE_MODE_ERROR
```
<br/>

#### 4. &nbsp; width *(Property)*
| return | Integer |
| - | - |

Returns the pseudo-console's width.\
Returns `None` if class initialization failed.

```
Possible Errors:

NONE, CONPTY_UNINITIALIZED
```
<br/>

#### 5. &nbsp; height *(Property)*
| return | Integer |
| - | - |

Returns the pseudo-console's height.\
Returns `None` if class initialization failed.

```
Possible Errors:

NONE, CONPTY_UNINITIALIZED
```
<br/>

#### 6. &nbsp; isrunning *(Property)*
| return | Boolean |
| - | - |

Returns `True`, if the pseudo-console is currently running, else `False`.

```
Possible Errors:

NONE, CONPTY_UNINITIALIZED
```
<br/>

#### 7. &nbsp; processended *(Property)*
| return | Boolean |
| - | - |

Returns `True`, if the currently running process has truly ended, else `False`.

At this point, the pseudo-console might yet not have released any final pending program output, if any.

This property is particularly helpful on Windows 10, where a relevant Windows ConPTY bug exists.

Following a short delay, the pseudo-console may be terminated by calling the `kill()` function.

```
Possible Errors:

NONE, CONPTY_UNINITIALIZED
```
<br/>

#### 8. &nbsp; inputsent *(Property)*
| return | Boolean |
| - | - |

Returns `True`, if all input has been sent to the pseudo-console, else `False`.

```
Possible Errors:

NONE, CONPTY_UNINITIALIZED
```
<br/>

#### 9. &nbsp; exitcode *(Property)*
| return | Integer or None |
| - | - |

Returns the exitcode of the previously run process.

If no process has been run since the initialization of the ConPTY class, then `None` is returned.\
If a process is currently running, then `None` is returned.

This property is volatile and it must be read/copied immediately after a function completes/terminates.

You may refer to [\[MS-ERREF\].pdf](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-erref/1bc92ddf-b79e-413c-bbaa-99a5281a6c90) or utilize the [Microsoft Error Lookup Tool](https://learn.microsoft.com/en-us/windows/win32/debug/system-error-code-lookup-tool) to know more about specific codes.

```
Possible Errors:

NONE, CONPTY_UNINITIALIZED, NO_PROCESS_FOUND, FORCED_TERMINATION,
PROCESS_ALREADY_RUNNING, RUNTIME_SUCCESS, RUNTIME_ERROR
```
<br/>

#### 10. &nbsp; run *(Function)*
```
run(command, waitfor = 0, timedelta = 0.1, stripinput = False, internaltimedelta = 100, postenddelay = -1)
```
| return | Boolean |
| - | - |
| command | String |
| waitfor | Integer or Float (1E-3 to SIZE_4B_MAX) |
| timedelta | Integer or Float (1E-3 to SIZE_4B_MAX) |
| stripinput | Boolean |
| internaltimedelta | Integer or Float (0 to SIZE_4B_MAX) |
| postenddelay | Integer or Float (1E-3 to SIZE_4B_MAX) |

Runs the given command or program, and then conditionally waits for its completion.\
Returns `True` if the process started successfully, else immediately returns `False`.

The command string's length must not exceed 32,766 characters.

If `False`, check the [`lasterror`](#3--lasterror-property) property to determine the reason for failure.

`waitfor` states the minimum amount of time, in seconds, to wait for incoming data.

`waitfor = 0` sets it to `waitfor = 1E-3`.\
`waitfor = 0` indicates non-blocking mode.\
`waitfor = N` indicates blocking for N seconds.\
`waitfor = -1` indicates indefinite blocking mode. (until the pseudo-console closes itself)\
`waitfor = -2` indicates indefinite blocking mode. (until the currently running program terminates)

Set `waitfor = -1` or `waitfor = -2` only if program auto-termination is guaranteed.

`timedelta` is the time lapse (delay), in seconds, between any two consecutive process-status checks. It governs the accuracy of the `waitfor` time period.

`stripinput` determines whether or not the input data is stripped off from the output data.

`internaltimedelta` is the time lapse (delay), in seconds or milliseconds, for internal process loops.

`0 <= internaltimedelta < 1` implies that the value is in seconds.\
`internaltimedelta >= 1` implies that the value is in milliseconds.

`postenddelay` is the minimum amount of time lapse/delay, in seconds or milliseconds, after a program ends, but just before shutting down the I/O buffer and releasing resources.

`0 <= postenddelay < 1` implies that the value is in seconds, truncated to 3 decimal places.
`postenddelay >= 1` implies that the value is in milliseconds.
`postenddelay = -1` is equivalent to `postenddelay = SIZE_4B_MAX`.

Set `internaltimedelta = 0` with caution.
Set `postenddelay > -1` with caution.

Note that `stripinput` is attempted and its success not guaranteed.
Note that, 1E-3 seconds = 0.001 seconds = 1 millisecond.\
Note that, `SIZE_4B_MAX` = 4294967295 = 4 Bytes = 32 Bits
Note that out-of-bounds values are automatically capped to their respective limits, unless stated otherwise.

```
Possible Errors:

NONE, CONPTY_UNINITIALIZED, COMMAND_NOT_A_STRING,
WAITFOR_NOT_A_NUMBER, TIMEDELTA_NOT_A_NUMBER,
STRIPINPUT_NOT_A_BOOLEAN, INTERNALTIMEDELTA_NOT_A_NUMBER,
POSTENDDELAY_NOT_A_NUMBER, COMMAND_LONGER_THAN_32766_CHARS,
RUN_INTERNAL_ERROR, RUN_PROGRAM_NOT_FOUND,
RUN_PROGRAM_ACCESS_DENIED, RUN_PROGRAM_NAME_TOO_LONG,
RUN_PROGRAM_ERROR
```
<br/>

#### 11. &nbsp; runandwait *(Function)*
```
runandwait(command, timedelta = 0.1, stripinput = False, internaltimedelta = 100, postenddelay = -1)
```
| return | Boolean |
| - | - |
| command | String |
| timedelta | Integer or Float (1E-3 to SIZE_4B_MAX) |
| stripinput | Boolean |
| internaltimedelta | Integer or Float (1E-3 to SIZE_4B_MAX) |
| postenddelay | Integer or Float (1E-3 to SIZE_4B_MAX) |

Runs the given command or program, and then waits for its completion.\
Returns `True` if the process started successfully, else immediately returns `False`.\
This is an _alias_ for the [`run(command, waitfor=-1, ...)`](#10--run-function) function.

If `False`, check the [`lasterror`](#3--lasterror-property) property to determine the reason for failure.

Refer to the [`run()`](#10--run-function) function for more details on the `command`, `timedelta`, `stripinput`, `internaltimedelta`, and `postenddelay` parameters, and for possible errors.
<br/>

#### 12. &nbsp; waittocomplete *(Function)*
```
waittocomplete(waitfor = -2, timedelta = 0.1)
```
| return | Boolean |
| - | - |
| waitfor | Integer or Float (1E-3 to SIZE_4B_MAX) |
| timedelta | Integer or Float (1E-3 to SIZE_4B_MAX) |

Waits for a command or program to partially or fully complete.\
Returns `True` if the wait conditions were satisfied, else immediately returns `False`.

If `False`, check the [`lasterror`](#3--lasterror-property) property to determine the reason for failure.

Refer to the [`run()`](#10--run-function) function for more details on the `waitfor` and `timedelta` parameters.

```
Possible Errors:

NONE, CONPTY_UNINITIALIZED, WAITFOR_NOT_A_NUMBER,
TIMEDELTA_NOT_A_NUMBER, RESIZE_ERROR
```
<br/>

#### 13. &nbsp; resize *(Function)*
```
resize(width, height)
```
| return | Boolean |
| - | - |
| width | Integer (1 to 32767) |
| height | Integer (1 to 32767) |

Resizes the pseudo-console.\
It is recommended to resize either at initialization (best), or after the read buffer has been cleared.

`width` and `height` are the pseudo-console's (terminal's) width and height, measured in 'number of characters'. They determine the I/O's internal buffer size and display. If you need the output unwrapped for _N_ characters, then set `width = N + 1`.

Note that out-of-bounds values are automatically capped to their respective limits.

```
Possible Errors:

NONE, CONPTY_UNINITIALIZED, CONSOLE_WIDTH_NOT_INT,
CONSOLE_HEIGHT_NOT_INT, RESIZE_ERROR
```
<br/>

#### 14. &nbsp; read *(Function)*
```
read(max_bytes_to_read = -1, waitfor = 0, rawdata = False, timedelta = 0.1, trailingspaces = False, min_bytes_to_read = 0)
```
| return | String |
| - | - |
| max_bytes_to_read | Integer (-1 to SIZE_4B_MAX) |
| waitfor | Integer or Float (1E-3 to SIZE_4B_MAX) |
| rawdata | Boolean |
| timedelta | Integer or Float (1E-3 to SIZE_4B_MAX) |
| trailingspaces | Boolean |
| min_bytes_to_read | Integer (0 to SIZE_4B_MAX) |

Returns data outputted by the pseudo-console, if available, else an empty string.

The number of bytes returned could be less than `max_bytes_to_read` subject to the availability of data.

`max_bytes_to_read = 0` returns an empty string.\
`max_bytes_to_read = N` returns a string of N characters.\
`max_bytes_to_read = -1` returns the entire saved buffer.

For ASCII/ANSI encoding, 1 byte = 1 character.

`waitfor` states the minimum amount of time, in seconds, to wait for incoming data.

`waitfor = 0` sets it to `waitfor = 1E-3`.\
`waitfor = 0` indicates non-blocking mode.\
`waitfor = N` indicates blocking for N seconds.\
`waitfor = -1` indicates indefinite blocking mode.

Set `waitfor = -1` only if output is guaranteed.

`rawdata` determines whether or not the output is in its raw format. The raw format contains [Virtual Terminal Sequences (VTS)](https://learn.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences) alongside normal text.

`timedelta` is the time lapse (delay), in seconds, between any two consecutive read-status checks. It governs the accuracy of the `waitfor` time period.

`trailingspaces` determines whether or not trailing whitespace characters, if any, should be included in the output.\
For now, this is prone to incorrect number of spaces.

`min_bytes_to_read` number of bytes are read until the `waitfor` time has run out.

Note that, 1E-3 seconds = 0.001 seconds = 1 millisecond.\
Note that out-of-bounds values are automatically capped to their respective limits.

```
Possible Errors:

NONE, CONPTY_UNINITIALIZED, NO_PROCESS_FOUND,
MAX_READ_BYTES_NOT_AN_INT, WAITFOR_NOT_A_NUMBER,
RAWDATA_NOT_A_BOOLEAN, TIMEDELTA_NOT_A_NUMBER,
TRAILINGSPACES_NOT_A_BOOLEAN, MIN_READ_BYTES_NOT_AN_INT,
MIN_MORE_THAN_MAX_READ_BYTES, READ_ERROR
```
<br/>

#### 15. &nbsp; getoutput *(Function)*
```
getoutput(waitfor = -1, rawdata = False, timedelta = 0.1, trailingspaces = True, min_bytes_to_read = 0)
```
| return | String |
| - | - |
| waitfor | Integer or Float (1E-3 to SIZE_4B_MAX) |
| rawdata | Boolean |
| timedelta | Integer or Float (1E-3 to SIZE_4B_MAX) |
| trailingspaces | Boolean |
| min_bytes_to_read | Integer (0 to SIZE_4B_MAX) |

Returns all the data currently outputted by the pseudo-console, if available, else an empty string.\
This is an _alias_ for the [`read()`](#14--read-function) or `read(-1)` function.

Refer to the [`read()`](#14--read-function) function for more details on the `waitfor`, `rawdata`, `timedelta`, `trailingspaces`, and `min_bytes_to_read` parameters, and for possible errors.
<br/>

#### 16. &nbsp; readline *(Function)*
```
readline(waitfor = 0, rawdata = False, timedelta = 0.1)
```
| return | String |
| - | - |
| waitfor | Integer or Float (1E-3 to SIZE_4B_MAX) |
| rawdata | Boolean |
| timedelta | Integer or Float (1E-3 to SIZE_4B_MAX) |

Returns a line of data outputted by the pseudo-console, if available, else, an empty string.

If the trailing data in the saved buffer does not contain a newline character:
- If a process is running, then that trailing data is considered unavailable.
- If no process is running, then that trailing data is considered available.

Refer to the [`read()`](#14--read-function) function for more details on the `waitfor`, `rawdata`, and `timedelta` parameters.

```
Possible Errors:

NONE, CONPTY_UNINITIALIZED, NO_PROCESS_FOUND,
WAITFOR_NOT_A_NUMBER, RAWDATA_NOT_A_BOOLEAN,
TIMEDELTA_NOT_A_NUMBER, READ_ERROR
```
<br/>

#### 17. &nbsp; readlines *(Function)*
```
readlines(max_lines_to_read = -1, waitfor = 0, rawdata = False, timedelta = 0.1, min_lines_to_read = 0)
```
| return | List of String |
| - | - |
| max_lines_to_read | Integer (-1 to SIZE_4B_MAX) |
| waitfor | Integer or Float (1E-3 to SIZE_4B_MAX) |
| rawdata | Boolean |
| timedelta | Integer or Float (1E-3 to SIZE_4B_MAX) |
| min_lines_to_read | Integer (0 to SIZE_4B_MAX) |

Returns a list of lines of data outputted by the pseudo-console, if available, else, an empty list.

If the trailing data in the saved buffer does not contain a newline character:
- If a process is running, then that trailing data is considered unavailable.
- If no process is running, then that trailing data is considered available.

The number of lines returned could be less than `max_lines_to_read` subject to the availability of data.

`max_lines_to_read =  0` returns an empty list.\
`max_lines_to_read =  N` returns a list of N text (string) elements.\
`max_lines_to_read = -1` returns a list of the entire saved buffer.

`min_lines_to_read` number of lines are read until the `waitfor` time has run out.

Refer to the [`read()`](#14--read-function) function for more details on the `waitfor`, `rawdata`, and `timedelta` parameters.

```
Possible Errors:

NONE, CONPTY_UNINITIALIZED, NO_PROCESS_FOUND,
MAX_READ_LINES_NOT_AN_INT, WAITFOR_NOT_A_NUMBER,
RAWDATA_NOT_A_BOOLEAN, TIMEDELTA_NOT_A_NUMBER,
MIN_READ_LINES_NOT_AN_INT, MIN_MORE_THAN_MAX_READ_LINES,
READ_ERROR
```
<br/>

#### 18. &nbsp; write *(Function)*
```
write(data_to_write, waitfor = 0, timedelta = 0.1, waittillsent = False)
```
| return | None |
| - | - |
| data_to_write | String |
| waittillsent | Boolean |
| waitfor | Integer or Float (1E-3 to SIZE_4B_MAX) |
| timedelta | Integer or Float (1E-3 to SIZE_4B_MAX) |

Write an input to the pseudo-console.

If the input does not end with a new-line character, it implies: do not hit enter (i.e., do not send yet).

Note that an empty string sends nothing.

`waittillsent` determines whether or not to wait until the input has truly been sent to the requesting process.

`waitfor` determines the minimum amount of time, in seconds, to wait until the data has been sent.

`waitfor = 0` sets it to `waitfor = 1E-3`.\
`waitfor = 0` indicates non-blocking mode.\
`waitfor = N` indicates blocking for N seconds.\
`waitfor = -1` indicates indefinite blocking mode.

Set `waitfor = -1` only if _input_ (NOT output) is guaranteed.

`timedelta` is the time lapse (delay), in seconds, between any two consecutive write-status checks. It governs the accuracy of the `waitfor` time period.

```
Possible Errors:

NONE, CONPTY_UNINITIALIZED, NO_PROCESS_FOUND, DATA_NOT_A_STRING,
WAITTILLSENT_NOT_A_BOOLEAN, WAITFOR_NOT_A_NUMBER,
TIMEDELTA_NOT_A_NUMBER, WRITE_INTERNAL_ERROR, WRITE_TIMEOUT
```
<br/>

#### 19. &nbsp; writeline *(Function)*
```
writeline(dataline_to_write, waitfor = 0, timedelta = 0.1, waittillsent = False)
```
| return | None |
| - | - |
| dataline_to_write | String |
| waittillsent | Boolean |
| waitfor | Integer or Float (1E-3 to SIZE_4B_MAX) |
| timedelta | Integer or Float (1E-3 to SIZE_4B_MAX) |

Write an input to the pseudo-console, and hit enter (i.e., send).

Refer to the [`read()`](#14--read-function) function for more details on the `waittillsent`, `waitfor`, and `timedelta` parameters.\
Refer to the [`write()`](#18--write-function) function for possible errors.
<br/>

#### 20. &nbsp; sendinput *(Function)*
```
sendinput(input_to_send, waitfor = 0, timedelta = 0.1, waittillsent = False)
```
| return | None |
| - | - |
| input_to_send | String |
| waittillsent | Boolean |
| waitfor | Integer or Float (1E-3 to SIZE_4B_MAX) |
| timedelta | Integer or Float (1E-3 to SIZE_4B_MAX) |

Write an input to the pseudo-console, and hit enter (i.e., send).\
This is an _alias_ for the [`writeline`](#19--writeline-function) function.

Refer to the [`read()`](#14--read-function) function for more details on the `waittillsent`, `waitfor`, and `timedelta` parameters.\
Refer to the [`write()`](#18--write-function) function for possible errors.
<br/>

#### 21. &nbsp; writelines *(Function)*
```
writelines(datalines_list_to_write, waitfor = 0, timedelta = 0.1, waittillsent = False)
```
| return | None |
| - | - |
| datalines_list_to_write | List of String |
| waittillsent | Boolean |
| waitfor | Integer or Float (1E-3 to SIZE_4B_MAX) |
| timedelta | Integer or Float (1E-3 to SIZE_4B_MAX) |

Write a list of inputs to the pseudo-console, hitting enter after each line of input.

Refer to the [`read()`](#14--read-function) function for more details on the `waittillsent`, `waitfor`, and `timedelta` parameters.

```
Possible Errors:

NONE, CONPTY_UNINITIALIZED, NO_PROCESS_FOUND,
DATA_NOT_A_LIST_OF_STRINGS, WAITTILLSENT_NOT_A_BOOLEAN,
WAITFOR_NOT_A_NUMBER, TIMEDELTA_NOT_A_NUMBER,
WRITE_INTERNAL_ERROR, WRITE_TIMEOUT
```
<br/>

#### 22. &nbsp; kill *(Function)*
```
kill()
```
| return | Boolean |
| - | - |

Terminates (kills) the currently running process, and returns `True` if the process was terminated, else `False`.

If `False`, check the [`lasterror`](#3--lasterror-property) property to determine the reason for failure.

```
Possible Errors:

NONE, CONPTY_UNINITIALIZED, NO_PROCESS_FOUND,
RUNTIME_SUCCESS, FORCED_TERMINATION, KILL_PROCESS_ERROR
```
<br/>

#### 23. &nbsp; enablevts *(Function)*
```
enablevts()
```
| return | Boolean |
| - | - |

Enables Virtual Terminal Sequences (VTS), aka, Escape Code Sequences for the terminal display, and returns `True` if VTS is successfully enabled, else `False`.

If `False`, then [`lasterror = ConPTY.Error.CONSOLE_MODE_ERROR`](#3--lasterror-property).

```
Possible Errors:

NONE, CONSOLE_MODE_ERROR
```
<br/>

#### 24. &nbsp; disablevts *(Function)*
```
disablevts()
```
| return | Boolean |
| - | - |

Disables Virtual Terminal Sequences (VTS), aka, Escape Code Sequences for the terminal display, and returns `True` if VTS is successfully disabled, else `False`.

If `False`, then [`lasterror = ConPTY.Error.CONSOLE_MODE_ERROR`](#3--lasterror-property).

Refer to the [`enablevts()`](#23--enablevts-function) function for possible errors.
<br/>

#### 25. &nbsp; resetdisplay *(Function)*
```
resetdisplay()
```
| return | Boolean |
| - | - |

Resets the terminal display.\
This is an _alias_ for the [`disablevts()`](#24--disablevts-function) function.

If `False`, then [`lasterror = ConPTY.Error.CONSOLE_MODE_ERROR`](#3--lasterror-property).

Refer to the [`enablevts()`](#23--enablevts-function) function for possible errors.
<br/>

#### 26. &nbsp; Error Enumerations *(Enum Class)*
```
Error.*
```
| Code | Info |
| -: | :- |
| 0 | NONE |
| 1 | CONSOLE_WIDTH_NOT_INT |
| 2 | CONSOLE_HEIGHT_NOT_INT |
| 3 | NOT_WINDOWS_OS |
| 4 | INCOMPATIBLE_WINDOWS_OS |
| 5 | COMMAND_LONGER_THAN_32766_CHARS |
| 6 | CONPTY_UNINITIALIZED |
| 7 | PROCESS_ALREADY_RUNNING |
| 8 | NO_PROCESS_FOUND |
| 9 | KILL_PROCESS_ERROR |
| 10 | READ_ERROR |
| 11 | WRITE_INTERNAL_ERROR |
| 12 | WRITE_TIMEOUT |
| 13 | RESIZE_ERROR |
| 14 | RUNTIME_SUCCESS |
| 15 | RUNTIME_ERROR |
| 16 | FORCED_TERMINATION |
| 17 | RUN_INTERNAL_ERROR |
| 18 | RUN_PROGRAM_NOT_FOUND |
| 19 | RUN_PROGRAM_ACCESS_DENIED |
| 20 | RUN_PROGRAM_NAME_TOO_LONG |
| 21 | RUN_PROGRAM_ERROR |
| 22 | DATA_NOT_A_STRING |
| 23 | COMMAND_NOT_A_STRING |
| 24 | MIN_READ_BYTES_NOT_AN_INT |
| 25 | MAX_READ_BYTES_NOT_AN_INT |
| 26 | MIN_READ_LINES_NOT_AN_INT |
| 27 | MAX_READ_LINES_NOT_AN_INT |
| 28 | MIN_MORE_THAN_MAX_READ_BYTES |
| 29 | MIN_MORE_THAN_MAX_READ_LINES |
| 30 | DATA_NOT_A_LIST_OF_STRINGS |
| 31 | WAITTILLSENT_NOT_A_BOOLEAN |
| 32 | WAITFOR_NOT_A_NUMBER |
| 33 | TIMEDELTA_NOT_A_NUMBER |
| 34 | INTERNALTIMEDELTA_NOT_A_NUMBER |
| 35 | POSTENDDELAY_NOT_A_NUMBER |
| 36 | RAWDATA_NOT_A_BOOLEAN |
| 37 | STRIPINPUT_NOT_A_BOOLEAN |
| 38 | TRAILINGSPACES_NOT_A_BOOLEAN |
| 39 | CONSOLE_MODE_ERROR |

<br/>

## More to do

- Fixing bugs, if any, relevant to the current codebase.
  - Tackling edge-case race conditions, if and when found.
    - For example, conducting multiple _(\>100)_ read-write tests very quickly and simulataneously causes a test or two to fail on occasion. I believe that either running outside of Python's Global Interpreter Lock (GIL) is what is causing this problem, or a pytest limitation of testing threads, or a Windows ConPTY limitation. I think this one could be referred to as a [_Heisenbug_](https://en.wikipedia.org/wiki/Heisenbug).
    - This is especially visible if your system is working very fast and under pressure, and involves multiple ConPTY instances in a multi-threaded environment.
    - Workaround is to slow down the processing by introducing slight delays (in the range of milliseconds) and tuning the `timedelta` and `internaltimedelta` options accordingly.
  - Note that, when submitting issues, it is recommended to append a sample code that is capable of reproducing the bug.
- Fix `trailingspaces` option feature, if possible, or discard it.
  - Involves parsing certain VTS's, keeping track of current cursor position, and root-cause analysis of trailing spaces.
  - This option ensures output fidelity, but it is not required for ordinary use-cases.
- Separation of output and error data.
  - Either find a reliable method to prevent printing error data onto the pseudo-console, or devise a reliable algorithm to strip off error data from output data.
- Verifying scope for Unicode (UTF-16) environment.
- Confirming the minimum Windows version where the write handle closure related Windows ConPTY bug has been fixed.
  - So that the `runandwait()` function could be done away with the need for the post-`kill()` function.
  - I have attempted two fixes (both of which are unreliable solutions):
    1. Introduce a time delay before (force) closing the pseudo-console.
       - Here, the time delay may be too long for quick, lightweight programs, and too short for some other programs, i.e., the final output may sometimes be delayed and thus inadvertently be discarded.
       - I have therefore decided to cede control over to the user:
         - via the `postenddelay` option.
         - by manually checking the `processended` property, and then calling the `kill` function.
    2. Peek into the read buffer before deciding whether to continue receiving output or to terminate.
       - Here, too, under certain system load conditions, there may be an internal delay while sending data. This causes the premature peek attempt to naively assume that there is no more incoming output and that it is time to terminate.
- Option for truly unwrapped output while reading the output.
  - This involves parsing different encodings.
  - This involves detecting various printable characters and character sequences.
  - Current workaround is to increase the pseudo-console width.
<br/><br/>

## License

GNU General Public License version 3 (GPL v3).\
Refer to [LICENSE](https://github.com/melwyncarlo/PyConPTY/blob/main/LICENSE) to know more.
