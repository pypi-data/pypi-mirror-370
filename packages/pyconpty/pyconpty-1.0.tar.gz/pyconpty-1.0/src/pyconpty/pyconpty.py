# This code is part of the PyConPTY python package.
# PyConPTY: A Python wrapper for the ConPTY (Windows Pseudo-console) API
# Copyright (C) 2025  MELWYN FRANCIS CARLO

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# For queries, contact me at: melwyncarlo@gmail.com


# pylint: disable=too-many-lines
# pylint: disable=too-many-arguments
# pylint: disable=unidiomatic-typecheck
# pylint: disable=too-many-public-methods
# pylint: disable=use-implicit-booleaness-not-comparison-to-zero


"""
PyConPTY: A Python wrapper for the ConPTY (Windows Pseudo-console) API
------------------------------------------------------------------------------
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
------------------------------------------------------------------------------

This package contains only one module: pyconpty
This module contains only one class: ConPTY

Usage: from pyconpty import ConPTY
"""

import time
import platform
import dataclasses
from enum import Enum
import _pyconptyinternal


class ConPTY:
    """
    This is the main  class for interacting with the ConPTY
    (Windows Pseudo-console) API.
    This class creates a ConPTY instance for communicating with ConHost.

    Attributes:
    --------------------------------------------------------------------------
        1.  isinitialized  (bool) :  Indicates whether or not the
                                     initialization was successful.
        2.  lasterror     (Error) :  Indicates either success or reason for
                                     error for the last operation.
        3.  width           (int) :  Indicates the pseudo-console's width in
                                     number of characters.
        4.  height          (int) :  Indicates the pseudo-console's height in
                                     number of characters.
        5.  isrunning      (bool) :  Indicates whether or not a process is
                                     currently running.
        6.  exitcode        (int) :  Indicates the exit/return code for the
                                     previously run process.
    """

    ##########################################################################
    ##  PUBLIC GLOBAL VARIABLES                                             ##
    ##########################################################################

    SIZE_4B_MAX = 4294967295

    class Error(Enum):
        """
        This is an enumeration class enumerating a list of operational errors.

        Constants:
        ----------------------------------------------------------------------
             (0)  NONE
             (1)  CONSOLE_WIDTH_NOT_INT
             (2)  CONSOLE_HEIGHT_NOT_INT
             (3)  NOT_WINDOWS_OS
             (4)  INCOMPATIBLE_WINDOWS_OS
             (5)  COMMAND_LONGER_THAN_32766_CHARS
             (6)  CONPTY_UNINITIALIZED
             (7)  PROCESS_ALREADY_RUNNING
             (8)  NO_PROCESS_FOUND
             (9)  KILL_PROCESS_ERROR
            (10)  READ_ERROR
            (11)  WRITE_INTERNAL_ERROR
            (12)  WRITE_TIMEOUT
            (13)  RESIZE_ERROR
            (14)  RUNTIME_SUCCESS
            (15)  RUNTIME_ERROR
            (16)  FORCED_TERMINATION
            (17)  RUN_INTERNAL_ERROR
            (18)  RUN_PROGRAM_NOT_FOUND
            (19)  RUN_PROGRAM_ACCESS_DENIED
            (20)  RUN_PROGRAM_NAME_TOO_LONG
            (21)  RUN_PROGRAM_ERROR
            (22)  DATA_NOT_A_STRING
            (23)  COMMAND_NOT_A_STRING
            (24)  MIN_READ_BYTES_NOT_AN_INT
            (25)  MAX_READ_BYTES_NOT_AN_INT
            (26)  MIN_READ_LINES_NOT_AN_INT
            (27)  MAX_READ_LINES_NOT_AN_INT
            (28)  MIN_MORE_THAN_MAX_READ_BYTES
            (29)  MIN_MORE_THAN_MAX_READ_LINES
            (30)  DATA_NOT_A_LIST_OF_STRINGS
            (31)  WAITTILLSENT_NOT_A_BOOLEAN
            (32)  WAITFOR_NOT_A_NUMBER
            (33)  TIMEDELTA_NOT_A_NUMBER
            (34)  INTERNALTIMEDELTA_NOT_A_NUMBER
            (35)  POSTENDDELAY_NOT_A_NUMBER
            (36)  RAWDATA_NOT_A_BOOLEAN
            (37)  STRIPINPUT_NOT_A_BOOLEAN
            (38)  TRAILINGSPACES_NOT_A_BOOLEAN
            (39)  CONSOLE_MODE_ERROR
        """

        # fmt: off
        NONE                            = 0
        CONSOLE_WIDTH_NOT_INT           = 1
        CONSOLE_HEIGHT_NOT_INT          = 2
        NOT_WINDOWS_OS                  = 3
        INCOMPATIBLE_WINDOWS_OS         = 4
        COMMAND_LONGER_THAN_32766_CHARS = 5
        CONPTY_UNINITIALIZED            = 6
        PROCESS_ALREADY_RUNNING         = 7
        NO_PROCESS_FOUND                = 8
        KILL_PROCESS_ERROR              = 9
        READ_ERROR                      = 10
        WRITE_INTERNAL_ERROR            = 11
        WRITE_TIMEOUT                   = 12
        RESIZE_ERROR                    = 13
        RUNTIME_SUCCESS                 = 14
        RUNTIME_ERROR                   = 15
        FORCED_TERMINATION              = 16
        RUN_INTERNAL_ERROR              = 17
        RUN_PROGRAM_NOT_FOUND           = 18
        RUN_PROGRAM_ACCESS_DENIED       = 19
        RUN_PROGRAM_NAME_TOO_LONG       = 20
        RUN_PROGRAM_ERROR               = 21
        DATA_NOT_A_STRING               = 22
        COMMAND_NOT_A_STRING            = 23
        MIN_READ_BYTES_NOT_AN_INT       = 24
        MAX_READ_BYTES_NOT_AN_INT       = 25
        MIN_READ_LINES_NOT_AN_INT       = 26
        MAX_READ_LINES_NOT_AN_INT       = 27
        MIN_MORE_THAN_MAX_READ_BYTES    = 28
        MIN_MORE_THAN_MAX_READ_LINES    = 29
        DATA_NOT_A_LIST_OF_STRINGS      = 30
        WAITTILLSENT_NOT_A_BOOLEAN      = 31
        WAITFOR_NOT_A_NUMBER            = 32
        TIMEDELTA_NOT_A_NUMBER          = 33
        INTERNALTIMEDELTA_NOT_A_NUMBER  = 34
        POSTENDDELAY_NOT_A_NUMBER       = 35
        RAWDATA_NOT_A_BOOLEAN           = 36
        STRIPINPUT_NOT_A_BOOLEAN        = 37
        TRAILINGSPACES_NOT_A_BOOLEAN    = 38
        CONSOLE_MODE_ERROR              = 39
        # fmt: on

    @dataclasses.dataclass
    class PrivateStatus:
        """Private Class! Do NOT use!"""

        isinitialized: bool
        islasterrorreserved: bool
        lasterror: "ConPTY.Error"
        hasanyprocessrunyet: bool
        exitcode: int | None
        forcedtermination: bool

    @dataclasses.dataclass
    class PrivateSize:
        """Private Class! Do NOT use!"""

        width: int | None
        height: int | None

    @dataclasses.dataclass
    class PrivateInternal:
        """Private Class! Do NOT use!"""

        vtsmode: int
        twspaces: str
        cursorx: int
        cursory: int

    @property
    def isinitialized(self):
        """
        An attribute/property of the class ConPTY.

        If `False`, then check the `lasterror` attribute/property to determine
        the reason for failure.

        Check this property post-initialization as a safety-check, if the
        initialization arguments are dynamic and not static.

        Using class functions when `isinitialized = False` results in error
        set by the property `lasterror = ConPTY.Error.CONPTY_UNINITIALIZED`.

        Returns:
        ----------------------------------------------------------------------
            isinitialized  (bool) :  Indicates whether or not the
                                     initialization was successful.

        Possible Errors:
        ----------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED, NOT_WINDOWS_OS,
            INCOMPATIBLE_WINDOWS_OS, CONSOLE_WIDTH_NOT_INT,
            CONSOLE_HEIGHT_NOT_INT
        """
        if not self.__status.isinitialized:
            if not self.__status.islasterrorreserved:
                self.__status.lasterror = ConPTY.Error.CONPTY_UNINITIALIZED
        else:
            self.__status.lasterror = ConPTY.Error.NONE
        return self.__status.isinitialized

    @property
    def lasterror(self):
        """
        An attribute/property of the class ConPTY.

        This value is one of the many `Error` Enumerations that is generated
        after each function call.

        This value indicates whether a function call succeeded or failed.

        If a function call failed, then this value indicates the reason for
        its failure.

        This property is volatile and it must be read/copied immediately
        after a function returns.

        Returns:
        ----------------------------------------------------------------------
            lasterror  (Error) :  Indicates either success or reason for error
                                  for the last operation.

        Possible Errors:
        ----------------------------------------------------------------------
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
        """
        error_code = self.__status.lasterror
        if self.__status.islasterrorreserved:
            self.__status.islasterrorreserved = False
            if not self.__status.isinitialized:  # pragma: no branch
                error_code = self.__status.lasterror
            # import typing
            # typing.assert_never(typing.Never)
        self.__status.lasterror = ConPTY.Error.NONE
        return error_code

    @property
    def width(self):
        """
        An attribute/property of the class ConPTY.

        Returns `None` if class initialization failed.

        Returns:
        ----------------------------------------------------------------------
            width  (int or None) :  Indicates the pseudo-console's width in
                                    number of characters.

        Possible Errors:
        ----------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED
        """
        self.__status.lasterror = ConPTY.Error.NONE
        self.__status.islasterrorreserved = False
        if not self.isinitialized:
            return None
        return self.__size.width

    @property
    def height(self):
        """
        An attribute/property of the class ConPTY.

        Returns `None` if class initialization failed.

        Returns:
        ----------------------------------------------------------------------
            height  (int or None) :  Indicates the pseudo-console's height in
                                     number of characters.

        Possible Errors:
        ----------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED
        """
        self.__status.lasterror = ConPTY.Error.NONE
        self.__status.islasterrorreserved = False
        if not self.isinitialized:
            return None
        return self.__size.height

    @property
    def isrunning(self):
        """
        An attribute/property of the class ConPTY.

        Returns:
        ----------------------------------------------------------------------
            isrunning  (bool) :  Indicates whether or not the pseudo-console
                                 is currently running.

        Possible Errors:
        ----------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED
        """
        self.__status.lasterror = ConPTY.Error.NONE
        self.__status.islasterrorreserved = False
        if not self.isinitialized:
            return False
        return self.__pyconptyinternal.get_is_console_running()

    @property
    def processended(self):
        """
        An attribute/property of the class ConPTY.

        At this point, the pseudo-console might yet not have
        released any final pending program output, if any.

        This property is particularly helpful on Windows 10,
        where a relevant Windows ConPTY bug exists.

        Following a short delay, the pseudo-console may be terminated
        by calling the `kill()` function.

        Returns:
        ----------------------------------------------------------------------
            processended  (bool) :  Indicates whether or not the currently
                                    running process has truly ended.

        Possible Errors:
        ----------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED
        """
        self.__status.lasterror = ConPTY.Error.NONE
        self.__status.islasterrorreserved = False
        if not self.isinitialized:
            return True
        return self.__pyconptyinternal.get_has_process_ended()

    @property
    def inputsent(self):
        """
        An attribute/property of the class ConPTY.

        Returns:
        ----------------------------------------------------------------------
            inputsent  (bool) :  Indicates whether or not all input has been
                                 sent to the pseudo-console.

        Possible Errors:
        ----------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED
        """
        self.__status.lasterror = ConPTY.Error.NONE
        self.__status.islasterrorreserved = False
        if not self.isinitialized:
            return False
        return self.__pyconptyinternal.get_is_input_sent()

    @property
    def exitcode(self):
        """
        An attribute/property of the class ConPTY.

        If no process has been run since the initialization of the ConPTY
        class, then `None` is returned.
        If a process is currently running, then `None` is returned.

        This property is volatile and it must be read/copied immediately
        after a function completes/terminates.

        You may refer to [MS-ERREF].pdf or utilize the [Microsoft Error
        Lookup Tool] (both of which are availabile on the Microsoft
        website) to know more about specific codes.

        Returns:
        ----------------------------------------------------------------------
            exitcode  (int or None) :  Indicates the exit/return code for the
                                       previously run process.

        Possible Errors:
        ----------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED, NO_PROCESS_FOUND, FORCED_TERMINATION,
            PROCESS_ALREADY_RUNNING, RUNTIME_SUCCESS, RUNTIME_ERROR
        """
        self.__status.islasterrorreserved = False
        if not self.isinitialized:
            return None
        if not self.__status.hasanyprocessrunyet:
            self.__status.lasterror = ConPTY.Error.NO_PROCESS_FOUND
            return None
        if self.__status.exitcode != -1:
            self.__status.exitcode = None
        if self.__status.exitcode is None:
            self.__status.lasterror = ConPTY.Error.NO_PROCESS_FOUND
            return None
        if self.__status.forcedtermination:
            self.__status.lasterror = ConPTY.Error.FORCED_TERMINATION
            self.__status.exitcode = 1
            return self.__status.exitcode
        if self.isrunning:
            self.__status.lasterror = ConPTY.Error.PROCESS_ALREADY_RUNNING
            return None
        self.__status.exitcode = (
            self.__pyconptyinternal.get_process_exit_code()
        )
        # pylint: disable-next=use-implicit-booleaness-not-comparison-to-zero
        if self.__status.exitcode == 0:
            self.__status.lasterror = ConPTY.Error.RUNTIME_SUCCESS
        else:
            self.__status.lasterror = ConPTY.Error.RUNTIME_ERROR
        return self.__status.exitcode

    ##########################################################################
    ##  PUBLIC FUNCTIONS                                                    ##
    ##########################################################################

    def __init__(self, width=80, height=24):
        """
         What do I do?
         ---------------------------------------------------------------------
         Construct/initialize the ConPTY class.

         The ConPTY class is the main  class for interacting with the ConPTY
        (Windows Pseudo-console) API.
         This class creates a ConPTY instance for communicating with ConHost.

         Check the `isinitialized` class attribute/property to confirm the
         initialization's success.

        `width` and `height` determine the I/O's internal buffer size
         and display.

         Note that out-of-bounds values are automatically capped to their
         respective limits.

         Parameters:
         ---------------------------------------------------------------------
            1.  width   (int) :  The width (1 to 32767) of the pseudo-console
                                 in number of characters. (default = 32767)
            2.  height  (int) :  The height (1 to 32767) of the pseudo-console
                                 in number of characters. (default = 32767)

         No Return.
         ---------------------------------------------------------------------

         Possible Errors:
         ---------------------------------------------------------------------
            NONE, NOT_WINDOWS_OS, INCOMPATIBLE_WINDOWS_OS,
            CONSOLE_WIDTH_NOT_INT, CONSOLE_HEIGHT_NOT_INT
        """
        self.__status = ConPTY.PrivateStatus(
            isinitialized=False,
            islasterrorreserved=True,
            lasterror=ConPTY.Error.NONE,
            hasanyprocessrunyet=False,
            exitcode=None,
            forcedtermination=False,
        )
        self.__size = ConPTY.PrivateSize(
            width=None,
            height=None,
        )
        self.__internal = ConPTY.PrivateInternal(
            vtsmode=0,
            twspaces="",
            cursorx=1,
            cursory=1,
        )
        if platform.system().lower().strip() != "windows":  # pragma: no cover
            self.__status.lasterror = ConPTY.Error.NOT_WINDOWS_OS
            return
        version_info_list = list(map(int, platform.version().split(".")))
        # Windows 10 Version 1809 Build 17763 (Windows 10.0.17763) Check
        # pylint: disable-next=duplicate-code
        if not (
            version_info_list[0] >= 10
            and version_info_list[1] >= 0
            and version_info_list[2] >= 17763
        ):  # pragma: no cover
            self.__status.lasterror = ConPTY.Error.INCOMPATIBLE_WINDOWS_OS
            return
        if not self.__validate_terminal_size_input(width, height):
            return
        width, height = self.__adjust_terminal_size_input(width, height)
        self.__size.width = width
        self.__size.height = height
        self.__status.isinitialized = True
        self.__status.hasanyprocessrunyet = False
        self.__status.lasterror = ConPTY.Error.NONE
        self.__status.islasterrorreserved = False
        self.__pyconptyinternal = _pyconptyinternal.ConPTYInternalObject(
            self.__size.width, self.__size.height
        )

    def run(
        self,
        command,
        *,
        waitfor=0,
        timedelta=0.1,
        stripinput=False,
        internaltimedelta=100,
        postenddelay=-1,
    ):
        """
         What do I do?
         ---------------------------------------------------------------------
         Run a command or program.

        `waitfor =  0` sets it to `waitfor = 1e-3`.
        `waitfor =  0` indicates non-blocking mode.
        `waitfor =  N` indicates blocking for N seconds.
        `waitfor = -1` indicates indefinite blocking mode.
                       (until the pseudo-console closes itself)
        `waitfor = -2` indicates indefinite blocking mode.
                       (until the currently running program terminates)

         Set `waitfor = -1` or `waitfor = -2` only if program auto-termination
         is guaranteed.

        `timedelta` governs the accuracy of the `waitfor` time period.

        `0 <= internaltimedelta < 1` implies that the value is in seconds,
                                     truncated to 3 decimal places.
        `internaltimedelta >= 1` implies that the value is in milliseconds.

        `0 <= postenddelay < 1` implies that the value is in seconds,
                                truncated to 3 decimal places.
        `postenddelay >= 1` implies that the value is in milliseconds.
        `postenddelay = -1` is equivalent to `postenddelay = SIZE_4B_MAX`.

         Set `internaltimedelta = 0` with caution.
         Set `postenddelay > -1` with caution.

         Note that `stripinput` is attempted, and its success not guaranteed.
         Note that, 1e-3 seconds = 0.001 seconds = 1 millisecond.
         Note that, SIZE_4B_MAX = 4294967295 = 4 Bytes = 32 Bits.
         Note that out-of-bounds values are automatically capped to their
         respective limits, unless stated otherwise.

         Parameters:
         ---------------------------------------------------------------------
            1.  command            (str) : A command or program name. (Length
                                           must not exceed 32,766 characters)
            2.  waitfor   (int or float) : Minimum amount of time, in seconds,
                                           to wait for program completion.
                                           (1e-3 to SIZE_4B_MAX) (default = 0)
            3.  timedelta (int or float) : Time lapse (delay), in seconds,
                                           (1e-3 to SIZE_4B_MAX) between any
                                           two consecutive process-status
                                           checks. (default = 0.1)
            4.  stripinput        (bool) : Whether or not the input data is
                                           stripped off from the output data.
                                           (default = False)
            5.  internaltimedelta        : Time lapse (delay), in seconds or
               (int or float)              milliseconds, (0 to SIZE_4B_MAX)
                                           for internal process loops.
                                           (default = 100)
            5.  postenddelay             : Minimum amount of time lapse/delay,
               (int or float)              in seconds or milliseconds, (0 to
                                           SIZE_4B_MAX) after a program ends,
                                           but just before shutting down the
                                           I/O buffer and releasing resources.
                                           (default = -1)

         Returns:
         ---------------------------------------------------------------------
            Result  (bool) :  Indicates run success/failure.
                             (whether or not a process started successfully)

                              If `False`, then check the `lasterror` class
                              attribute/property to determine the reason for
                              failure.

         Possible Errors:
         ---------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED, COMMAND_NOT_A_STRING,
            WAITFOR_NOT_A_NUMBER, TIMEDELTA_NOT_A_NUMBER,
            STRIPINPUT_NOT_A_BOOLEAN, INTERNALTIMEDELTA_NOT_A_NUMBER,
            POSTENDDELAY_NOT_A_NUMBER, COMMAND_LONGER_THAN_32766_CHARS,
            RUN_INTERNAL_ERROR, RUN_PROGRAM_NOT_FOUND,
            RUN_PROGRAM_ACCESS_DENIED, RUN_PROGRAM_NAME_TOO_LONG,
            RUN_PROGRAM_ERROR
        """
        self.__status.islasterrorreserved = False
        self.__status.exitcode = None
        self.__status.forcedtermination = False
        if not self.__check_run_arguments(
            command,
            waitfor=waitfor,
            timedelta=timedelta,
            stripinput=stripinput,
            internaltimedelta=internaltimedelta,
            postenddelay=postenddelay,
        ):
            return False
        if waitfor <= -2:
            wait_till_console_dies = False
        else:
            wait_till_console_dies = True
        if waitfor < 0:
            waitfor = ConPTY.SIZE_4B_MAX
        timedelta = max(timedelta, 1e-3)
        if internaltimedelta != 0 and internaltimedelta <= 1e-3:
            internaltimedelta = 1
        elif internaltimedelta < 1:
            internaltimedelta *= 1000
        internaltimedelta = int(internaltimedelta)
        if postenddelay < 0:
            postenddelay = ConPTY.SIZE_4B_MAX
        elif postenddelay != 0 and postenddelay <= 1e-3:
            postenddelay = 1
        elif postenddelay < 1:
            postenddelay *= 1000
        postenddelay = int(postenddelay)
        self.__internal.vtsmode = 0
        self.__internal.twspaces = ""
        run_result = self.__pyconptyinternal.run_process(
            command, stripinput, internaltimedelta, postenddelay
        )
        errors_list = [
            ConPTY.Error.NONE,
            ConPTY.Error.RUN_INTERNAL_ERROR,
            ConPTY.Error.RUN_PROGRAM_NOT_FOUND,
            ConPTY.Error.RUN_PROGRAM_ACCESS_DENIED,
            ConPTY.Error.RUN_PROGRAM_NAME_TOO_LONG,
            ConPTY.Error.RUN_PROGRAM_ERROR,
        ]
        self.__status.lasterror = errors_list[run_result]
        if run_result != 0:
            return False
        total_time_elapsed = 0
        while (
            self.__check_is_op_ongoing(wait_till_console_dies)
            and total_time_elapsed < waitfor
        ):
            time.sleep(timedelta)
            total_time_elapsed += timedelta
        self.__status.hasanyprocessrunyet = True
        self.__status.exitcode = -1
        return True

    def runandwait(
        self,
        command,
        *,
        timedelta=0.1,
        stripinput=False,
        internaltimedelta=100,
        postenddelay=-1,
    ):
        """
         What do I do?
         ---------------------------------------------------------------------
         Run a command or program, and wait for it to complete.

        `timedelta` governs the accuracy of the `waitfor` time period.

        `0 <= internaltimedelta < 1` implies that the value is in seconds,
                                     truncated to 3 decimal places.
        `internaltimedelta >= 1` implies that the value is in milliseconds.

        `0 <= postenddelay < 1` implies that the value is in seconds,
                                truncated to 3 decimal places.
        `postenddelay >= 1` implies that the value is in milliseconds.
        `postenddelay = -1` is equivalent to `postenddelay = SIZE_4B_MAX`.

         Set `internaltimedelta = 0` with caution.
         Set `postenddelay > -1` with caution.

         Note that `stripinput` is attempted, and its success not guaranteed.
         Note that, 1e-3 seconds = 0.001 seconds = 1 millisecond.
         Note that, SIZE_4B_MAX = 4294967295 = 4 Bytes = 32 Bits.
         Note that out-of-bounds values are automatically capped to their
         respective limits, unless stated otherwise.

         Parameters:
         ---------------------------------------------------------------------
            1.  command            (str) : A command or program name. (Length
                                           must not exceed 32,766 characters)
            2.  timedelta (int or float) : Time lapse (delay), in seconds,
                                           (1e-3 to SIZE_4B_MAX) between any
                                           two consecutive process-status
                                           checks. (default = 0.1)
            3.  stripinput        (bool) : Whether or not the input data is
                                           stripped off from the output data.
                                           (default = False)
            4.  internaltimedelta        : Time lapse (delay), in seconds or
               (int or float)              milliseconds, (0 to SIZE_4B_MAX)
                                           for internal process loops.
                                           (default = 100)
            5.  postenddelay             : Minimum amount of time lapse/delay,
               (int or float)              in seconds or milliseconds, (0 to
                                           SIZE_4B_MAX) after a program ends,
                                           but just before shutting down the
                                           I/O buffer and releasing resources.
                                           (default = -1)

         Returns:
         ---------------------------------------------------------------------
            Result  (bool) :  Indicates run success/failure.
                             (whether or not a process started successfully)

                              If `False`, then check the `lasterror` class
                              attribute/property to determine the reason for
                              failure.

         Possible Errors:
         ---------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED, COMMAND_NOT_A_STRING,
            WAITFOR_NOT_A_NUMBER, TIMEDELTA_NOT_A_NUMBER,
            STRIPINPUT_NOT_A_BOOLEAN, INTERNALTIMEDELTA_NOT_A_NUMBER,
            POSTENDDELAY_NOT_A_NUMBER, COMMAND_LONGER_THAN_32766_CHARS,
            RUN_INTERNAL_ERROR, RUN_PROGRAM_NOT_FOUND,
            RUN_PROGRAM_ACCESS_DENIED, RUN_PROGRAM_NAME_TOO_LONG,
            RUN_PROGRAM_ERROR
        """
        return self.run(
            command,
            waitfor=(-2 if postenddelay == -1 else -1),
            timedelta=timedelta,
            stripinput=stripinput,
            internaltimedelta=internaltimedelta,
            postenddelay=postenddelay,
        )

    def waittocomplete(self, *, waitfor=-2, timedelta=0.1):
        """
         What do I do?
         ---------------------------------------------------------------------
         I wait for a command or program to partially or fully complete.

        `waitfor =  0` sets it to `waitfor = 1e-3`.
        `waitfor =  0` indicates non-blocking mode.
        `waitfor =  N` indicates blocking for N seconds.
        `waitfor = -1` indicates indefinite blocking mode.
                      (until the pseudo-console closes itself)
        `waitfor = -2` indicates indefinite blocking mode.
                      (until the currently running program terminates)

         Set `waitfor = -1` or `waitfor = -2` only if program auto-termination
         is guaranteed.

        `timedelta` governs the accuracy of the `waitfor` time period.

         Note that, 1e-3 seconds = 0.001 seconds = 1 millisecond.
         Note that out-of-bounds values are automatically capped to their
         respective limits.

         Parameters:
         ---------------------------------------------------------------------
            1.  waitfor   (int or float) : Minimum amount of time, in seconds,
                                           to wait for program completion.
                                           (1e-3 to SIZE_4B_MAX)
                                           (default = -2)
            2.  timedelta (int or float) : Time lapse (delay), in seconds,
                                           (1e-3 to SIZE_4B_MAX) between any
                                           two consecutive process-status
                                           checks. (default = 0.1)

         Returns:
         ---------------------------------------------------------------------
            Result  (bool) :  Indicates wait success/failure.
                             (whether or not the wait conditions were
                              satisfied)

                              If `False`, then check the `lasterror` class
                              attribute/property to determine the reason for
                              failure.

         Possible Errors:
         ---------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED, WAITFOR_NOT_A_NUMBER,
            TIMEDELTA_NOT_A_NUMBER, RESIZE_ERROR
        """
        self.__status.islasterrorreserved = False
        if not self.isinitialized:
            return False
        if type(waitfor) not in (int, float):
            self.__status.lasterror = ConPTY.Error.WAITFOR_NOT_A_NUMBER
            return False
        if type(timedelta) not in (int, float):
            self.__status.lasterror = ConPTY.Error.TIMEDELTA_NOT_A_NUMBER
            return False
        if waitfor <= -2:
            wait_till_console_dies = False
        else:
            wait_till_console_dies = True
        if waitfor < 0:
            waitfor = ConPTY.SIZE_4B_MAX
        timedelta = max(timedelta, 1e-3)
        total_time_elapsed = 0
        while (
            self.__check_is_op_ongoing(wait_till_console_dies)
            and total_time_elapsed < waitfor
        ):
            time.sleep(timedelta)
            total_time_elapsed += timedelta
        self.__status.lasterror = ConPTY.Error.NONE
        return True

    def resize(self, width, height):
        """
        What do I do?
        ----------------------------------------------------------------------
        Resize the pseudo-console.

        It is recommended to resize either at initialization (best),
        or after the read buffer has been cleared.

        Note that out-of-bounds values are automatically capped to their
        respective limits.

        Parameters:
        ----------------------------------------------------------------------
            1.  width   (int) :  The width (1 to 32767) of the pseudo-console
                                 in number of characters.
            2.  height  (int) :  The height (1 to 32767) of the pseudo-console
                                 in number of characters.

        Returns:
        ----------------------------------------------------------------------
            Result  (bool) :  Indicates resize success/failure.

        Possible Errors:
        ----------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED, CONSOLE_WIDTH_NOT_INT,
            CONSOLE_HEIGHT_NOT_INT, RESIZE_ERROR
        """
        self.__status.islasterrorreserved = False
        if not self.isinitialized:
            return False
        if not self.__validate_terminal_size_input(width, height):
            return False
        width, height = self.__adjust_terminal_size_input(width, height)
        self.__size.width = width
        self.__size.height = height
        if not self.__pyconptyinternal.resize_pseudoconsole(
            width, height
        ):  # pragma: no cover
            self.__status.lasterror = ConPTY.Error.RESIZE_ERROR
            return False
        self.__status.lasterror = ConPTY.Error.NONE
        return True

    def read(
        self,
        *,
        max_bytes_to_read=-1,
        waitfor=0,
        rawdata=False,
        timedelta=0.1,
        trailingspaces=False,
        min_bytes_to_read=0,
    ):
        """
         What do I do?
         ---------------------------------------------------------------------
         Read a stream of output from the pseudo-console, if available, else
         an empty string.

         The number of bytes returned could be less than `max_bytes_to_read`
         subject to the availability of data.

        `max_bytes_to_read =  0` returns an empty string.
        `max_bytes_to_read =  N` returns a string of N characters.
        `max_bytes_to_read = -1` returns the entire saved buffer.

         For ASCII/ANSI encoding, 1 byte = 1 character.

        `waitfor =  0` sets it to `waitfor = 1e-3`.
        `waitfor =  0` indicates non-blocking mode.
        `waitfor =  N` indicates blocking for N seconds.
        `waitfor = -1` indicates indefinite blocking mode.

         Set `waitfor = -1` only if output is guaranteed.

        `timedelta` governs the accuracy of the `waitfor` time period.

        `min_bytes_to_read` number of bytes are read until the `waitfor`
         time has run out.

         Note that, 1e-3 seconds = 0.001 seconds = 1 millisecond.
         Note that out-of-bounds values are automatically capped to their
         respective limits.

         Parameters:
         ---------------------------------------------------------------------
            1.  max_bytes_to_read  (int) : Maximum number of output bytes to
                                           read (-1 to SIZE_4B_MAX) from the
                                           saved buffer. (default = -1)
            2.  waitfor   (int or float) : Minimum amount of time, in seconds,
                                           to wait for incoming data (1e-3 to
                                           SIZE_4B_MAX). (default = 0)
            3.  rawdata           (bool) : Whether or not the output is in its
                                           raw format, i.e., containing
                                           Virtual Terminal Sequences, aka,
                                           VTS. (default = False)
            4.  timedelta (int or float) : Time lapse (delay), in seconds,
                                           (1e-3 to SIZE_4B_MAX) between any
                                           two consecutive read-status checks.
                                           (default = 0.1)
            5.  trailingspaces    (bool) : Whether or not trailing whitespace
                                           characters, if any, should be
                                           included in the output.
                                           (default = False)
            6.  min_bytes_to_read  (int) : Minimum number of output bytes to
                                           read (0 to SIZE_4B_MAX) from the
                                           saved buffer. (default = 0)

         Returns:
         ---------------------------------------------------------------------
            Result  (str or None) :  Returns a text (string) upon success,
                                     or None upon failure.

         Possible Errors:
         ---------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED, NO_PROCESS_FOUND,
            MAX_READ_BYTES_NOT_AN_INT, WAITFOR_NOT_A_NUMBER,
            RAWDATA_NOT_A_BOOLEAN, TIMEDELTA_NOT_A_NUMBER,
            TRAILINGSPACES_NOT_A_BOOLEAN, MIN_READ_BYTES_NOT_AN_INT,
            MIN_MORE_THAN_MAX_READ_BYTES, READ_ERROR
        """
        self.__status.islasterrorreserved = False
        if not self.__check_read_arguments(
            max_bytes_to_read=max_bytes_to_read,
            waitfor=waitfor,
            rawdata=rawdata,
            timedelta=timedelta,
            trailingspaces=trailingspaces,
            min_bytes_to_read=min_bytes_to_read,
        ):
            return None
        if max_bytes_to_read < 0:
            max_bytes_to_read = ConPTY.SIZE_4B_MAX
        min_bytes_to_read = max(min_bytes_to_read, 0)
        if min_bytes_to_read > max_bytes_to_read:
            self.__status.lasterror = ConPTY.Error.MIN_MORE_THAN_MAX_READ_BYTES
            return None
        if waitfor < 0:
            waitfor = ConPTY.SIZE_4B_MAX
        elif waitfor < 1e-3:
            waitfor = 1e-3
        timedelta = max(timedelta, 1e-3)
        total_data = ""
        if max_bytes_to_read:
            total_time_elapsed = 0
            while total_time_elapsed < waitfor:
                result_bundle = self.__pyconptyinternal.read_from_buffer(
                    False,
                    0,
                    max_bytes_to_read,
                    rawdata,
                    self.__internal.vtsmode,
                    self.__internal.twspaces,
                    self.__internal.cursorx,
                    self.__internal.cursory,
                )
                if result_bundle is None:  # pragma: no cover
                    self.__internal.vtsmode = 0
                    self.__internal.twspaces = ""
                    self.__status.lasterror = ConPTY.Error.READ_ERROR
                    return None
                data = ""
                if result_bundle != 0:
                    (
                        data,
                        self.__internal.vtsmode,
                        self.__internal.twspaces,
                        self.__internal.cursorx,
                        self.__internal.cursory,
                    ) = result_bundle
                total_data += data
                if trailingspaces and self.__internal.twspaces.isspace():
                    total_data += self.__internal.twspaces
                    self.__internal.twspaces = ""
                if data:
                    if len(total_data) >= min_bytes_to_read:
                        break
                time.sleep(timedelta)
                total_time_elapsed += timedelta
        self.__status.lasterror = ConPTY.Error.NONE
        return total_data

    def getoutput(
        self,
        *,
        waitfor=-1,
        rawdata=False,
        timedelta=0.1,
        trailingspaces=True,
        min_bytes_to_read=0,
    ):
        """
         What do I do?
         ---------------------------------------------------------------------
         Read the entire stream of current output from the pseudo-console,
         if available, else an empty string.
         I am an alias for the `read` or `read(-1)` function.

        `waitfor =  0` sets it to `waitfor = 1e-3`.
        `waitfor =  0` indicates non-blocking mode.
        `waitfor =  N` indicates blocking for N seconds.
        `waitfor = -1` indicates indefinite blocking mode.

         Set `waitfor = -1` only if output is guaranteed.

        `timedelta` governs the accuracy of the `waitfor` time period.

        `min_bytes_to_read` number of bytes are read until the `waitfor`
         time has run out.

         Note that, 1e-3 seconds = 0.001 seconds = 1 millisecond.
         Note that out-of-bounds values are automatically capped to their
         respective limits.

         Parameters:
         ---------------------------------------------------------------------
            1.  waitfor   (int or float) : Minimum amount of time, in seconds,
                                           to wait for incoming data (1e-3 to
                                           SIZE_4B_MAX). (default = -1)
            2.  rawdata           (bool) : Whether or not the output is in its
                                           raw format, i.e., containing
                                           Virtual Terminal Sequences, aka,
                                           VTS. (default = False)
            3.  timedelta (int or float) : Time lapse (delay), in seconds,
                                           (1e-3 to SIZE_4B_MAX) between any
                                           two consecutive read-status checks.
                                           (default = 0.1)
            4.  trailingspaces    (bool) : Whether or not trailing whitespace
                                           characters, if any, should be
                                           included in the output.
                                           (default = True)
            5.  min_bytes_to_read  (int) : Minimum number of output bytes to
                                           read (0 to SIZE_4B_MAX) from the
                                           saved buffer. (default = 0)

         Returns:
         ---------------------------------------------------------------------
            Result  (str or None) :  Returns a text (string) upon success,
                                     or None upon failure.

         Possible Errors:
         ---------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED, NO_PROCESS_FOUND,
            MAX_READ_BYTES_NOT_AN_INT, WAITFOR_NOT_A_NUMBER,
            RAWDATA_NOT_A_BOOLEAN, TIMEDELTA_NOT_A_NUMBER,
            TRAILINGSPACES_NOT_A_BOOLEAN, MIN_READ_BYTES_NOT_AN_INT,
            MIN_MORE_THAN_MAX_READ_BYTES, READ_ERROR
        """
        return self.read(
            max_bytes_to_read=-1,
            waitfor=waitfor,
            rawdata=rawdata,
            timedelta=timedelta,
            trailingspaces=trailingspaces,
            min_bytes_to_read=min_bytes_to_read,
        )

    def readline(self, *, waitfor=0, rawdata=False, timedelta=0.1):
        """
         What do I do?
         ---------------------------------------------------------------------
         Read a line of output from the pseudo-console, if available, else,
         an empty string.

         If the trailing data in the saved buffer does not contain a newline
         character:
         - If a process is running, then that trailing data is considered
           unavailable.
         - If no process is running, then that trailing data is considered
           available.

        `waitfor =  0` sets it to `waitfor = 1e-3`.
        `waitfor =  0` indicates non-blocking mode.
        `waitfor =  N` indicates blocking for N seconds.
        `waitfor = -1` indicates indefinite blocking mode.

         Set `waitfor = -1` only if output is guaranteed.

        `timedelta` governs the accuracy of the `waitfor` time period.

         Note that, 1e-3 seconds = 0.001 seconds = 1 millisecond.
         Note that out-of-bounds values are automatically capped to their
         respective limits.

         Parameters:
         ---------------------------------------------------------------------
            1.  waitfor   (int or float) : Minimum amount of time, in seconds,
                                           to wait for incoming data (1e-3 to
                                           SIZE_4B_MAX). (default = 0)
            2.  rawdata           (bool) : Whether or not the output is in its
                                           raw format, i.e., containing
                                           Virtual Terminal Sequences, aka,
                                           VTS. (default = False)
            3.  timedelta (int or float) : Time lapse (delay), in seconds,
                                           (1e-3 to SIZE_4B_MAX) between any
                                           two consecutive read-status checks.
                                           (default = 0.1)

         Returns:
         ---------------------------------------------------------------------
            Result  (str or None) :  Returns a line of text (string) upon
                                     success, or None upon failure.

         Possible Errors:
         ---------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED, NO_PROCESS_FOUND,
            WAITFOR_NOT_A_NUMBER, RAWDATA_NOT_A_BOOLEAN,
            TIMEDELTA_NOT_A_NUMBER, READ_ERROR
        """
        self.__status.islasterrorreserved = False
        if not self.__is_process_initialised_and_running(True):
            return None
        if type(waitfor) not in (int, float):
            self.__status.lasterror = ConPTY.Error.WAITFOR_NOT_A_NUMBER
            return None
        if type(rawdata) is not bool:
            self.__status.lasterror = ConPTY.Error.RAWDATA_NOT_A_BOOLEAN
            return None
        if type(timedelta) not in (int, float):
            self.__status.lasterror = ConPTY.Error.TIMEDELTA_NOT_A_NUMBER
            return None
        if waitfor < 0:
            waitfor = ConPTY.SIZE_4B_MAX
        elif waitfor < 1e-3:
            waitfor = 1e-3
        timedelta = max(timedelta, 1e-3)
        data = ""
        total_time_elapsed = 0
        while total_time_elapsed < waitfor:
            result_bundle = self.__pyconptyinternal.read_from_buffer(
                True,
                1,
                0,
                rawdata,
                self.__internal.vtsmode,
                self.__internal.twspaces,
                self.__internal.cursorx,
                self.__internal.cursory,
            )
            if result_bundle is None:  # pragma: no cover
                self.__internal.vtsmode = 0
                self.__internal.twspaces = ""
                self.__status.lasterror = ConPTY.Error.READ_ERROR
                return None
            data = ""
            if result_bundle != 0:
                (
                    data,
                    self.__internal.vtsmode,
                    self.__internal.twspaces,
                    self.__internal.cursorx,
                    self.__internal.cursory,
                ) = result_bundle
            if data:
                break
            time.sleep(timedelta)
            total_time_elapsed += timedelta
        self.__status.lasterror = ConPTY.Error.NONE
        return data.strip()

    def readlines(
        self,
        *,
        max_lines_to_read=-1,
        waitfor=0,
        rawdata=False,
        timedelta=0.1,
        min_lines_to_read=0,
    ):
        """
         What do I do?
         ---------------------------------------------------------------------
         Read a list of lines of output from the pseudo-console, if available,
         else, an empty list.

         If the trailing data in the saved buffer does not contain a newline
         character:
         - If a process is running, then that trailing data is considered
           unavailable.
         - If no process is running, then that trailing data is considered
           available.

         The number of lines returned could be less than `max_bytes_to_read`
         subject to the availability of data.

        `max_lines_to_read =  0` returns an empty list.
        `max_lines_to_read =  N` returns a list of N text (string) elements.
        `max_lines_to_read = -1` returns a list of the entire saved buffer.

        `waitfor =  0` sets it to `waitfor = 1e-3`.
        `waitfor =  0` indicates non-blocking mode.
        `waitfor =  N` indicates blocking for N seconds.
        `waitfor = -1` indicates indefinite blocking mode.

         Set `waitfor = -1` only if output is guaranteed.

        `timedelta` governs the accuracy of the `waitfor` time period.

        `min_lines_to_read` number of lines are read until the `waitfor`
         time has run out.

         Note that, 1e-3 seconds = 0.001 seconds = 1 millisecond.
         Note that out-of-bounds values are automatically capped to their
         respective limits.

         Parameters:
         ---------------------------------------------------------------------
            1.  max_lines_to_read  (int) : Maximum number of output lines to
                                           read (-1 to SIZE_4B_MAX) from the
                                           saved buffer. (default = -1)
            2.  waitfor   (int or float) : Minimum amount of time, in seconds,
                                           to wait for incoming data (1e-3 to
                                           SIZE_4B_MAX). (default = 0)
            3.  rawdata           (bool) : Whether or not the output is in its
                                           raw format, i.e., containing
                                           Virtual Terminal Sequences, aka,
                                           VTS. (default = False)
            4.  timedelta (int or float) : Time lapse (delay), in seconds,
                                           (1e-3 to SIZE_4B_MAX) between any
                                           two consecutive read-status checks.
                                           (default = 0.1)
            5.  min_lines_to_read  (int) : Minimum number of output lines to
                                           read (0 to SIZE_4B_MAX) from the
                                           saved buffer. (default = 0)

         Returns:
         ---------------------------------------------------------------------
            Result  (list or None) :  Returns a list of lines of text (string)
                                      upon success, or None upon failure.

         Possible Errors:
         ---------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED, NO_PROCESS_FOUND,
            MAX_READ_LINES_NOT_AN_INT, WAITFOR_NOT_A_NUMBER,
            RAWDATA_NOT_A_BOOLEAN, TIMEDELTA_NOT_A_NUMBER,
            MIN_READ_LINES_NOT_AN_INT, MIN_MORE_THAN_MAX_READ_LINES,
            READ_ERROR
        """
        self.__status.islasterrorreserved = False
        if not self.__check_readlines_arguments(
            max_lines_to_read=max_lines_to_read,
            waitfor=waitfor,
            rawdata=rawdata,
            timedelta=timedelta,
            min_lines_to_read=min_lines_to_read,
        ):
            return None
        if max_lines_to_read < 0:
            max_lines_to_read = ConPTY.SIZE_4B_MAX
        min_lines_to_read = max(min_lines_to_read, 0)
        if min_lines_to_read > max_lines_to_read:
            self.__status.lasterror = ConPTY.Error.MIN_MORE_THAN_MAX_READ_LINES
            return None
        if waitfor < 0:
            waitfor = ConPTY.SIZE_4B_MAX
        elif waitfor < 1e-3:
            waitfor = 1e-3
        timedelta = max(timedelta, 1e-3)
        total_lines = []
        if max_lines_to_read:
            total_time_elapsed = 0
            while total_time_elapsed < waitfor:
                result_bundle = self.__pyconptyinternal.read_from_buffer(
                    True,
                    max_lines_to_read,
                    0,
                    rawdata,
                    self.__internal.vtsmode,
                    self.__internal.twspaces,
                    self.__internal.cursorx,
                    self.__internal.cursory,
                )
                if result_bundle is None:  # pragma: no cover
                    self.__internal.vtsmode = 0
                    self.__internal.twspaces = ""
                    self.__status.lasterror = ConPTY.Error.READ_ERROR
                    return None
                lines = []
                if result_bundle != 0:
                    (
                        lines,
                        self.__internal.vtsmode,
                        self.__internal.twspaces,
                        self.__internal.cursorx,
                        self.__internal.cursory,
                    ) = result_bundle
                if lines:
                    total_lines.extend(lines.splitlines())
                    if len(total_lines) >= min_lines_to_read:
                        break
                time.sleep(timedelta)
                total_time_elapsed += timedelta
        self.__status.lasterror = ConPTY.Error.NONE
        return total_lines

    def write(
        self, data_to_write, *, waittillsent=False, waitfor=0, timedelta=0.1
    ):
        """
         What do I do?
         ---------------------------------------------------------------------
         Write a stream of input to the pseudo-console.

         If the input does not end with a new-line character, it implies:
         do not hit enter (i.e., do not send yet).

         Note that an empty string send nothing.

        `waitfor =  0` sets it to `waitfor = 1e-3`.
        `waitfor =  0` indicates non-blocking mode.
        `waitfor =  N` indicates blocking for N seconds.
        `waitfor = -1` indicates indefinite blocking mode.

         Set `waitfor = -1` only if input (NOT output) is guaranteed.

        `timedelta` governs the accuracy of the `waitfor` time period.

         Note that, 1e-3 seconds = 0.001 seconds = 1 millisecond.
         Note that out-of-bounds values are automatically capped to their
         respective limits.

         Parameters:
         ---------------------------------------------------------------------
            1.  data_to_write      (str) : Your input stream of data.
            2.  waittillsent      (bool) : Whether or not to wait until the
                                           input has truly been sent to the
                                           requesting process.
                                           (default = False)
            3.  waitfor   (int or float) : Minimum amount of time, in seconds,
                                           to wait until data has been sent.
                                           (1e-3 to SIZE_4B_MAX) (default = 0)
            4.  timedelta (int or float) : Time lapse (delay), in seconds,
                                           (1e-3 to SIZE_4B_MAX) between any
                                           two consecutive write-status
                                           checks. (default = 0.1)

         Returns:
         ---------------------------------------------------------------------
            Result  (bool) :  Indicates write success/failure.

         Possible Errors:
         ---------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED, NO_PROCESS_FOUND, DATA_NOT_A_STRING,
            WAITTILLSENT_NOT_A_BOOLEAN, WAITFOR_NOT_A_NUMBER,
            TIMEDELTA_NOT_A_NUMBER, WRITE_INTERNAL_ERROR, WRITE_TIMEOUT
        """
        self.__status.islasterrorreserved = False
        if not self.__check_write_arguments(
            data_to_write,
            waittillsent=waittillsent,
            waitfor=waitfor,
            timedelta=timedelta,
        ):
            return False
        if waitfor < 0:
            waitfor = ConPTY.SIZE_4B_MAX
        elif waitfor < 1e-3:
            waitfor = 1e-3
        timedelta = max(timedelta, 1e-3)
        if data_to_write:
            result_code = self.__pyconptyinternal.write_to_buffer(
                ("\r\n".join(("_" + data_to_write + "_").splitlines()))[1:-1]
            )
            if result_code == 0:  # pragma: no cover
                self.__status.lasterror = ConPTY.Error.WRITE_INTERNAL_ERROR
                return False
            if waittillsent:
                total_time_elapsed = 0
                while not self.inputsent and total_time_elapsed < waitfor:
                    time.sleep(timedelta)
                    total_time_elapsed += timedelta
                if not self.inputsent:  # pragma: no cover
                    self.__status.lasterror = ConPTY.Error.WRITE_TIMEOUT
                    return False
        self.__status.lasterror = ConPTY.Error.NONE
        return True

    def writeline(
        self,
        dataline_to_write,
        *,
        waittillsent=False,
        waitfor=0,
        timedelta=0.1,
    ):
        """
         What do I do?
         ---------------------------------------------------------------------
         Write a line of input to the pseudo-console, and hit enter
        (i.e., send).

        `waitfor =  0` sets it to `waitfor = 1e-3`.
        `waitfor =  0` indicates non-blocking mode.
        `waitfor =  N` indicates blocking for N seconds.
        `waitfor = -1` indicates indefinite blocking mode.

         Set `waitfor = -1` only if input (NOT output) is guaranteed.

        `timedelta` governs the accuracy of the `waitfor` time period.

         Note that, 1e-3 seconds = 0.001 seconds = 1 millisecond.
         Note that out-of-bounds values are automatically capped to their
         respective limits.

         Parameters:
         ---------------------------------------------------------------------
            1.  dataline_to_write  (str) : Your input line of data.
                                           Similar to the `write` function,
                                           with a new-line character being
                                           appended to it at the end.
            2.  waittillsent      (bool) : Whether or not to wait until the
                                           input has truly been sent to the
                                           requesting process.
                                           (default = False)
            3.  waitfor   (int or float) : Minimum amount of time, in seconds,
                                           to wait until data has been sent.
                                           (1e-3 to SIZE_4B_MAX) (default = 0)
            4.  timedelta (int or float) : Time lapse (delay), in seconds,
                                           (1e-3 to SIZE_4B_MAX) between any
                                           two consecutive write-status
                                           checks. (default = 0.1)

         Returns:
         ---------------------------------------------------------------------
            Result  (bool) :  Indicates write success/failure.

         Possible Errors:
         ---------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED, NO_PROCESS_FOUND, DATA_NOT_A_STRING,
            WAITTILLSENT_NOT_A_BOOLEAN, WAITFOR_NOT_A_NUMBER,
            TIMEDELTA_NOT_A_NUMBER, WRITE_INTERNAL_ERROR, WRITE_TIMEOUT
        """
        self.__status.islasterrorreserved = False
        if type(dataline_to_write) is not str:
            self.__status.lasterror = ConPTY.Error.DATA_NOT_A_STRING
            return False
        return self.write(
            f"{dataline_to_write}\r\n",
            waittillsent=waittillsent,
            waitfor=waitfor,
            timedelta=timedelta,
        )

    def sendinput(
        self, input_to_send, *, waittillsent=False, waitfor=0, timedelta=0.1
    ):
        """
         What do I do?
         ---------------------------------------------------------------------
         Write a line of input to the pseudo-console, and hit enter
        (i.e., send). I am an alias for the `writeline` function.

         Note that an empty string does nothing.

        `waitfor =  0` sets it to `waitfor = 1e-3`.
        `waitfor =  0` indicates non-blocking mode.
        `waitfor =  N` indicates blocking for N seconds.
        `waitfor = -1` indicates indefinite blocking mode.

         Set `waitfor = -1` only if input (NOT output) is guaranteed.

        `timedelta` governs the accuracy of the `waitfor` time period.

         Note that, 1e-3 seconds = 0.001 seconds = 1 millisecond.
         Note that out-of-bounds values are automatically capped to their
         respective limits.

         Parameters:
         ---------------------------------------------------------------------
            1.  input_to_send      (str) : Your input line of data.
                                           Similar to the `write` function,
                                           with a new-line character being
                                           appended to it at the end.
            2.  waittillsent      (bool) : Whether or not to wait until the
                                           input has truly been sent to the
                                           requesting process.
                                           (default = False)
            3.  waitfor   (int or float) : Minimum amount of time, in seconds,
                                           to wait until data has been sent.
                                           (1e-3 to SIZE_4B_MAX) (default = 0)
            4.  timedelta (int or float) : Time lapse (delay), in seconds,
                                           (1e-3 to SIZE_4B_MAX) between any
                                           two consecutive write-status
                                           checks. (default = 0.1)

         Returns:
         ---------------------------------------------------------------------
            Result  (bool) :  Indicates write success/failure.

         Possible Errors:
         ---------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED, NO_PROCESS_FOUND, DATA_NOT_A_STRING,
            WAITTILLSENT_NOT_A_BOOLEAN, WAITFOR_NOT_A_NUMBER,
            TIMEDELTA_NOT_A_NUMBER, WRITE_INTERNAL_ERROR, WRITE_TIMEOUT
        """
        return self.writeline(
            input_to_send,
            waittillsent=waittillsent,
            waitfor=waitfor,
            timedelta=timedelta,
        )

    def writelines(
        self,
        datalines_list_to_write,
        *,
        waittillsent=False,
        waitfor=0,
        timedelta=0.1,
    ):
        """
         What do I do?
         ---------------------------------------------------------------------
         Write multiple lines of input to the pseudo-console, hitting enter
         after each line of input.

         Note that an empty list or empty strings within the list do nothing.

        `waitfor =  0` sets it to `waitfor = 1e-3`.
        `waitfor =  0` indicates non-blocking mode.
        `waitfor =  N` indicates blocking for N seconds.
        `waitfor = -1` indicates indefinite blocking mode.

         Set `waitfor = -1` only if input (NOT output) is guaranteed.

        `timedelta` governs the accuracy of the `waitfor` time period.

         Note that, 1e-3 seconds = 0.001 seconds = 1 millisecond.
         Note that out-of-bounds values are automatically capped to their
         respective limits.

         Parameters:
         ---------------------------------------------------------------------
            1.  datalines_list_to_write  : Your list of input lines of data.
               (list)                      Similar to the `writeline`
                                           function, but for multiple lines.
                                           A new-line character is appended at
                                           the end of each line in the list.
            2.  waittillsent      (bool) : Whether or not to wait until the
                                           input has truly been sent to the
                                           requesting process.
                                           (default = False)
            3.  waitfor   (int or float) : Minimum amount of time, in seconds,
                                           to wait until data has been sent.
                                           (1e-3 to SIZE_4B_MAX) (default = 0)
            4.  timedelta (int or float) : Time lapse (delay), in seconds,
                                           (1e-3 to SIZE_4B_MAX) between any
                                           two consecutive write-status
                                           checks. (default = 0.1)

         Returns:
         ---------------------------------------------------------------------
            Result  (bool) :  Indicates write success/failure.

         Possible Errors:
         ---------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED, NO_PROCESS_FOUND,
            DATA_NOT_A_LIST_OF_STRINGS, WAITTILLSENT_NOT_A_BOOLEAN,
            WAITFOR_NOT_A_NUMBER, TIMEDELTA_NOT_A_NUMBER,
            WRITE_INTERNAL_ERROR, WRITE_TIMEOUT
        """
        self.__status.islasterrorreserved = False
        if type(datalines_list_to_write) is not list:
            self.__status.lasterror = ConPTY.Error.DATA_NOT_A_LIST_OF_STRINGS
            return False
        if not all(type(item) is str for item in datalines_list_to_write):
            self.__status.lasterror = ConPTY.Error.DATA_NOT_A_LIST_OF_STRINGS
            return False
        return self.write(
            "\r\n".join(datalines_list_to_write) + "\r\n",
            waittillsent=waittillsent,
            waitfor=waitfor,
            timedelta=timedelta,
        )

    def kill(self):
        """
        What do I do?
        ----------------------------------------------------------------------
        Terminate (kill) the currently running program/process.

        If `False`, check the `lasterror` class attribute/property to
        determine the reason for failure.

        No Parameters.
        ----------------------------------------------------------------------

        Returns:
        ----------------------------------------------------------------------
            Result  (bool) :  Indicates termination success/failure.
                              (whether or not the process was terminated)

        Possible Errors:
        ----------------------------------------------------------------------
            NONE, CONPTY_UNINITIALIZED, NO_PROCESS_FOUND,
            RUNTIME_SUCCESS, FORCED_TERMINATION, KILL_PROCESS_ERROR
        """
        self.__status.islasterrorreserved = False
        if not self.__is_process_initialised_and_running():
            return False
        if self.__pyconptyinternal.kill_process():  # pragma: no branch
            exit_code = None
            while exit_code is None:
                exit_code = self.__pyconptyinternal.get_process_exit_code()
            if self.__pyconptyinternal.get_process_exit_code() == 0:
                self.__status.lasterror = ConPTY.Error.RUNTIME_SUCCESS
            else:
                self.__status.lasterror = ConPTY.Error.FORCED_TERMINATION
                self.__status.forcedtermination = True
            return True
        self.__status.lasterror = (
            ConPTY.Error.KILL_PROCESS_ERROR
        )  # pragma: no cover
        return False  # pragma: no cover

    def enablevts(self):
        """
        What do I do?
        ----------------------------------------------------------------------
        Enable Virtual Terminal Sequences (VTS), aka, Escape Code Sequences
        for your terminal display.

        No Parameters.
        ----------------------------------------------------------------------

        Returns:
        ----------------------------------------------------------------------
            Result  (bool) :  Indicates enable success/failure.
                              (whether or not VTS was enabled)

        Possible Errors:
        ----------------------------------------------------------------------
            NONE, CONSOLE_MODE_ERROR
        """
        if self.__pyconptyinternal.set_vts_display(True):  # pragma: no branch
            self.__status.lasterror = ConPTY.Error.NONE
            return True
        self.__status.lasterror = (
            ConPTY.Error.CONSOLE_MODE_ERROR
        )  # pragma: no cover
        return False  # pragma: no cover

    def disablevts(self):
        """
        What do I do?
        ----------------------------------------------------------------------
        Disable Virtual Terminal Sequences (VTS), aka, Escape Code Sequences
        for your terminal display.

        No Parameters.
        ----------------------------------------------------------------------

        Returns:
        ----------------------------------------------------------------------
            Result  (bool) :  Indicates disable success/failure.
                              (whether or not VTS was disabled)

        Possible Errors:
        ----------------------------------------------------------------------
            NONE, CONSOLE_MODE_ERROR
        """
        if self.__pyconptyinternal.set_vts_display(False):  # pragma: no branch
            self.__status.lasterror = ConPTY.Error.NONE
            return True
        self.__status.lasterror = (
            ConPTY.Error.CONSOLE_MODE_ERROR
        )  # pragma: no cover
        return False  # pragma: no cover

    def resetdisplay(self):
        """
        What do I do?
        ----------------------------------------------------------------------
        Reset your terminal display.
        I am an alias for the `disablevts` function.

        No Parameters.
        -----------------------------------------------------------------------

        Returns:
        ----------------------------------------------------------------------
           Result  (bool) :  Indicates reset success/failure.
                             (whether or not the terminal display was reset)

        Possible Errors:
        ----------------------------------------------------------------------
            NONE, CONSOLE_MODE_ERROR
        """
        return self.disablevts()

    ##########################################################################
    ##  PRIVATE FUNCTIONS                                                   ##
    ##########################################################################

    def __validate_terminal_size_input(self, width, height):
        """Private Function! Do NOT use!"""
        if type(width) is not int:
            self.__status.lasterror = ConPTY.Error.CONSOLE_WIDTH_NOT_INT
            return False
        if type(height) is not int:
            self.__status.lasterror = ConPTY.Error.CONSOLE_HEIGHT_NOT_INT
            return False
        return True

    def __adjust_terminal_size_input(self, width, height):
        """Private Function! Do NOT use!"""
        width  = max(1, min(width,  32767)) # fmt: skip
        height = max(1, min(height, 32767))
        return (width, height)

    def __is_process_initialised_and_running(self, pasttense=False):
        """Private Function! Do NOT use!"""
        if not self.isinitialized:
            return False
        if (pasttense and not self.__status.hasanyprocessrunyet) or (
            not pasttense and not self.isrunning
        ):
            self.__status.lasterror = ConPTY.Error.NO_PROCESS_FOUND
            return False
        return True

    def __check_is_op_ongoing(self, waittillconsoledies=False):
        """Private Function! Do NOT use!"""
        if waittillconsoledies:
            return self.isrunning
        return not self.processended

    def __check_run_arguments(
        self,
        command,
        *,
        waitfor,
        timedelta,
        stripinput,
        internaltimedelta,
        postenddelay,
    ):
        """Private Function! Do NOT use!"""
        if not self.isinitialized:
            error_found = True
        elif type(command) is not str:
            self.__status.lasterror = ConPTY.Error.COMMAND_NOT_A_STRING
            error_found = True
        elif type(waitfor) not in (int, float):
            self.__status.lasterror = ConPTY.Error.WAITFOR_NOT_A_NUMBER
            error_found = True
        elif type(timedelta) not in (int, float):
            self.__status.lasterror = ConPTY.Error.TIMEDELTA_NOT_A_NUMBER
            error_found = True
        elif type(stripinput) is not bool:
            self.__status.lasterror = ConPTY.Error.STRIPINPUT_NOT_A_BOOLEAN
            error_found = True
        elif type(internaltimedelta) not in (int, float):
            self.__status.lasterror = (
                ConPTY.Error.INTERNALTIMEDELTA_NOT_A_NUMBER
            )
            error_found = True
        elif type(postenddelay) not in (int, float):
            self.__status.lasterror = ConPTY.Error.POSTENDDELAY_NOT_A_NUMBER
            error_found = True
        elif len(command) > 32766:
            self.__status.lasterror = (
                ConPTY.Error.COMMAND_LONGER_THAN_32766_CHARS
            )
            error_found = True
        else:
            error_found = False
        return not error_found

    def __check_read_arguments(
        self,
        *,
        max_bytes_to_read,
        waitfor,
        rawdata,
        timedelta,
        trailingspaces,
        min_bytes_to_read,
    ):
        """Private Function! Do NOT use!"""
        if not self.__is_process_initialised_and_running(True):
            error_found = True
        elif type(max_bytes_to_read) is not int:
            self.__status.lasterror = ConPTY.Error.MAX_READ_BYTES_NOT_AN_INT
            error_found = True
        elif type(waitfor) not in (int, float):
            self.__status.lasterror = ConPTY.Error.WAITFOR_NOT_A_NUMBER
            error_found = True
        elif type(rawdata) is not bool:
            self.__status.lasterror = ConPTY.Error.RAWDATA_NOT_A_BOOLEAN
            error_found = True
        elif type(timedelta) not in (int, float):
            self.__status.lasterror = ConPTY.Error.TIMEDELTA_NOT_A_NUMBER
            error_found = True
        elif type(trailingspaces) is not bool:
            self.__status.lasterror = ConPTY.Error.TRAILINGSPACES_NOT_A_BOOLEAN
            error_found = True
        elif type(min_bytes_to_read) is not int:
            self.__status.lasterror = ConPTY.Error.MIN_READ_BYTES_NOT_AN_INT
            error_found = True
        else:
            error_found = False
        return not error_found

    def __check_readlines_arguments(
        self,
        *,
        max_lines_to_read,
        waitfor,
        rawdata,
        timedelta,
        min_lines_to_read,
    ):
        """Private Function! Do NOT use!"""
        if not self.__is_process_initialised_and_running(True):
            error_found = True
        elif type(max_lines_to_read) is not int:
            self.__status.lasterror = ConPTY.Error.MAX_READ_LINES_NOT_AN_INT
            error_found = True
        elif type(waitfor) not in (int, float):
            self.__status.lasterror = ConPTY.Error.WAITFOR_NOT_A_NUMBER
            error_found = True
        elif type(rawdata) is not bool:
            self.__status.lasterror = ConPTY.Error.RAWDATA_NOT_A_BOOLEAN
            error_found = True
        elif type(timedelta) not in (int, float):
            self.__status.lasterror = ConPTY.Error.TIMEDELTA_NOT_A_NUMBER
            error_found = True
        elif type(min_lines_to_read) is not int:
            self.__status.lasterror = ConPTY.Error.MIN_READ_LINES_NOT_AN_INT
            error_found = True
        else:
            error_found = False
        return not error_found

    def __check_write_arguments(
        self,
        data_to_write,
        *,
        waittillsent,
        waitfor,
        timedelta,
    ):
        """Private Function! Do NOT use!"""
        if not self.__is_process_initialised_and_running():
            error_found = True
        elif type(data_to_write) is not str:
            self.__status.lasterror = ConPTY.Error.DATA_NOT_A_STRING
            error_found = True
        elif type(waittillsent) is not bool:
            self.__status.lasterror = ConPTY.Error.WAITTILLSENT_NOT_A_BOOLEAN
            error_found = True
        elif type(waitfor) not in (int, float):
            self.__status.lasterror = ConPTY.Error.WAITFOR_NOT_A_NUMBER
            error_found = True
        elif type(timedelta) not in (int, float):
            self.__status.lasterror = ConPTY.Error.TIMEDELTA_NOT_A_NUMBER
            error_found = True
        else:
            error_found = False
        return not error_found
