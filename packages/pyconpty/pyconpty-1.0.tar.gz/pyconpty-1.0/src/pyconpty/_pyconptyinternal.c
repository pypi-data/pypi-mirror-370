/*
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
*/

#define _WIN32_WINNT _WIN32_WINNT_WIN10
#define NTDDI_VERSION NTDDI_WIN10_RS5

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <time.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <stdbool.h>
#include <windows.h>
#include <stdatomic.h>

/* ######################################################################## */
/*  PRIVATE GLOBAL VARIABLES                                                */
/* ######################################################################## */

#define STDOUT_PIPE_BUFFER_SIZE 65536
#define STDIN_PIPE_BUFFER_SIZE 8192

static const DWORD MAX_READ_BUFFER_SIZE = STDOUT_PIPE_BUFFER_SIZE;
static const DWORD MAX_WRITE_BUFFER_SIZE = STDIN_PIPE_BUFFER_SIZE;
static const size_t WAIT_NAMED_PIPE_TIMEOUT_MILLIS = 500;

typedef enum {
    NOT_RUNNING,
    STARTING,
    RUNNING,
    GRACEFULLY_TERMINATING,
    GRACEFULLY_TERMINATED,
    FORCEFULLY_TERMINATING
} ProcessStatus;

typedef enum {
    VTSMODE_NONE,
    VTSMODE_ESCAPE,
    VTSMODE_OPENING_SQUARE_BRACKET,
    VTSMODE_CLOSING_SQUARE_BRACKET,
    VTSMODE_OPENING_SQUARE_BRACKET_DIGIT,
    VTSMODE_SKIP_1,
    VTSMODE_SEARCH_ST,
    VTSMODE_SEARCH_LETTER,
    VTSMODE_SEARCH_Hf
} VTSMode;

typedef struct {
    char *data;
    size_t cursor_position;
    size_t data_length;
    size_t max_size;
} ConPTYIOBuffer;

/* Bytes Alignment Padding */
__pragma(warning(disable: 4820))
typedef struct {
    PyObject_HEAD
    STARTUPINFOEXW si;
    ConPTYIOBuffer read_buffer;
    ConPTYIOBuffer write_buffer;
    ConPTYIOBuffer strip_input_buffer;
    ConPTYIOBuffer strip_repeat_buffer;
    PROCESS_INFORMATION pi;
    HPCON hPC;
    HANDLE client_stdout_pipe_handle;
    HANDLE client_stdin_pipe_handle;
    HANDLE kill_lock;
    HANDLE destroy_lock;
    _Atomic ProcessStatus process_status;
    COORD pseudo_console_size;
    DWORD post_end_delay;
    DWORD time_delta;
    volatile DWORD process_exit_code;
    atomic_bool is_read_buffer_available;
    atomic_bool is_write_buffer_available;
    bool has_any_process_run_yet;
} ConPTYBriefcase;
__pragma(warning(default: 4820))

/* ######################################################################## */
/*  FUNCTION DECLARATIONS                                                   */
/* ######################################################################## */

/* Public Functions */
PyMODINIT_FUNC PyInit__pyconptyinternal(void);
static int pyconptyinternal_init(ConPTYBriefcase*, PyObject*, PyObject*);
static PyObject *run_process(ConPTYBriefcase*, PyObject* const*, Py_ssize_t);
static PyObject *resize_pseudoconsole(ConPTYBriefcase*, PyObject* const*,
                                                        Py_ssize_t);
static PyObject *read_from_buffer(ConPTYBriefcase*, PyObject* const*,
                                                    Py_ssize_t);
static PyObject *write_to_buffer(ConPTYBriefcase*, PyObject* const*,
                                                   Py_ssize_t);
static PyObject *get_is_console_running(ConPTYBriefcase*, PyObject*);
static PyObject *get_has_process_ended(ConPTYBriefcase*, PyObject*);
static PyObject *get_is_input_sent(ConPTYBriefcase*, PyObject*);
static PyObject *kill_process(ConPTYBriefcase*, PyObject*);
static PyObject *get_process_exit_code(ConPTYBriefcase*, PyObject*);
static PyObject *set_vts_display(ConPTYBriefcase*, PyObject* const*,
                                             Py_ssize_t);
static void pyconptyinternal_dealloc(ConPTYBriefcase*);

/* Private Functions */
static bool initialize_iobuffer(ConPTYIOBuffer*, bool);
static void free_iobuffer(ConPTYIOBuffer*);
static bool extend_iobuffer(ConPTYIOBuffer*, size_t);
static bool shrink_iobuffer(ConPTYIOBuffer*, size_t, size_t);
static bool set_up_pseudo_console(ConPTYBriefcase*);
static HRESULT create_process(ConPTYBriefcase*, LPWSTR);
static HRESULT prepare_startup_info(HPCON, STARTUPINFOEXW*);
static DWORD WINAPI wait_for_process_completion(LPVOID);
static DWORD WINAPI listen_for_stdin_stream(LPVOID);
static DWORD WINAPI listen_for_stdout_stream(LPVOID);
static HRESULT create_listener_thread(ConPTYBriefcase*,
                                      LPTHREAD_START_ROUTINE);
static HRESULT launch_io_listeners(ConPTYBriefcase*);
static bool strip_vts_from_data(const char* const, size_t*, char **, VTSMode*,
                ConPTYIOBuffer*, const SHORT* const, const SHORT* const,
                                            size_t*, size_t*, bool*);
static bool extend_write_data_buffer(char**, char**, size_t*,
                                    const size_t* const);
static bool append_to_twspaces_buffer(ConPTYIOBuffer*, char);
static int get_number_from_twspaces_buffer(ConPTYIOBuffer*);
static int strstr_internal(char*, char*, size_t, size_t, bool**, bool **,
                size_t*, size_t*, size_t*, ConPTYIOBuffer*, VTSMode*);
static void close_client_io_pipes(ConPTYBriefcase*);
static bool kill_process_internal(ConPTYBriefcase*);
static void destroy_pseudoconsole(ConPTYBriefcase*);
static bool get_is_console_running_internal(ConPTYBriefcase*);

/* ######################################################################## */
/*  PUBLIC GLOBAL VARIABLES                                                 */
/* ######################################################################## */

/* Unsafe Conversion */
__pragma(warning(disable: 4191))
static PyMethodDef pyconptyinternal_methods[] = {
    {"run_process", (PyCFunction) run_process, METH_FASTCALL, NULL},
    {
        "resize_pseudoconsole", (PyCFunction) resize_pseudoconsole,
        METH_FASTCALL, NULL
    },
    {"read_from_buffer", (PyCFunction) read_from_buffer, METH_FASTCALL, NULL},
    {"write_to_buffer",  (PyCFunction) write_to_buffer,  METH_FASTCALL, NULL},
    {
        "get_is_console_running", (PyCFunction) get_is_console_running,
        METH_NOARGS, NULL
    },
    {
        "get_has_process_ended", (PyCFunction) get_has_process_ended,
        METH_NOARGS, NULL
    },
    {
        "get_is_input_sent", (PyCFunction) get_is_input_sent,
        METH_NOARGS, NULL
    },
    {"kill_process", (PyCFunction) kill_process, METH_NOARGS, NULL},
    {
        "get_process_exit_code", (PyCFunction) get_process_exit_code,
        METH_NOARGS, NULL
    },
    {
        "set_vts_display", (PyCFunction) set_vts_display,
        METH_FASTCALL, NULL
    },
    {NULL, NULL, 0, NULL}
};
__pragma(warning(default: 4191))

/* Non-static Runtime DLL Import */
__pragma(warning(disable: 4232))
static PyTypeObject ConPTYInternalObject = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "_pyconptyinternal.ConPTYInternalObject",
    .tp_doc = NULL,
    .tp_basicsize = sizeof(ConPTYBriefcase),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT & ~Py_TPFLAGS_BASETYPE,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc) pyconptyinternal_init,
    .tp_dealloc = (destructor) pyconptyinternal_dealloc,
    .tp_members = NULL,
    .tp_methods = pyconptyinternal_methods
};
__pragma(warning(default: 4232))

static int pyconptyinternal_module_exec(PyObject *m) {
    if (PyType_Ready(&ConPTYInternalObject) < 0) {
        return -1;
    }
    if (PyModule_AddObjectRef(
            m, "ConPTYInternalObject", (PyObject*) &ConPTYInternalObject) < 0
    ) {
        return -1;
    }
    return 0;
}

static PyModuleDef_Slot pyconptyinternal_slots[] = {
    {Py_mod_exec, (void *)pyconptyinternal_module_exec},
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {0, NULL}
};

static struct PyModuleDef pyconptyinternal_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "_pyconptyinternal",
    .m_methods = NULL,
    .m_size = 0,
    .m_slots = pyconptyinternal_slots,
    .m_traverse = NULL,
    .m_clear = NULL,
    .m_free = NULL
};

/* ######################################################################## */
/*  PUBLIC FUNCTIONS                                                        */
/* ######################################################################## */

PyMODINIT_FUNC PyInit__pyconptyinternal(void) {
    return PyModuleDef_Init(&pyconptyinternal_module);
}
static int pyconptyinternal_init(
            ConPTYBriefcase *self, PyObject *args, PyObject *kwds
) {
    UNREFERENCED_PARAMETER(kwds);
    SHORT width, height;
    if (!PyArg_ParseTuple(args, "hh", &width, &height)) {
        return -1;
    }
    ZeroMemory(&self->si, sizeof(STARTUPINFOEXW));
    ZeroMemory(&self->pi, sizeof(PROCESS_INFORMATION));
    self->hPC = NULL;
    self->process_exit_code = (DWORD)-1;
    self->has_any_process_run_yet = false;
    self->process_status = NOT_RUNNING;
    self->is_read_buffer_available = false;
    self->is_write_buffer_available = false;
    self->client_stdout_pipe_handle = NULL;
    self->client_stdin_pipe_handle = NULL;
    self->pseudo_console_size.X = width;
    self->pseudo_console_size.Y = height;
    self->post_end_delay = (DWORD)-1;
    self->time_delta = 100;
    if ((!initialize_iobuffer(&self->read_buffer, true))
     || (!initialize_iobuffer(&self->write_buffer, true))
     || (!initialize_iobuffer(&self->strip_input_buffer, true))
     || (!initialize_iobuffer(&self->strip_repeat_buffer, true))
    ) {
        return -1;
    }
    self->kill_lock = CreateMutex(NULL, FALSE, NULL);
    self->destroy_lock = CreateMutex(NULL, FALSE, NULL);
    return 0;
}

static PyObject *run_process(
        ConPTYBriefcase *self, PyObject *const *args, Py_ssize_t nargs
) {
    static const HRESULT E_FILENOTFOUND = 0x80070002L;
    static const HRESULT E_PATHNOTFOUND = 0x80070003L;
    static const HRESULT E_FILENAMETOOLONG = 0x800700CEL;
    if (nargs != 4) {
        return NULL;
    }
    if ((self->process_status != NOT_RUNNING)
     && (self->process_status != GRACEFULLY_TERMINATED)
    ) {
        return NULL;
    }
    atomic_store(&self->process_status, STARTING);
    self->process_exit_code = (DWORD)-1;
    if (!PyUnicode_Check(args[0])) {
        return NULL;
    }
    LPWSTR unicode_command = PyUnicode_AsWideCharString(args[0], NULL);
    if (unicode_command == NULL) {
        return NULL;
    }
    const int strip_input = PyLong_AsInt(args[1]);
    if (((strip_input != 0) && (strip_input != 1)) || PyErr_Occurred()) {
        return NULL;
    }
    if (strip_input) {
        if (!initialize_iobuffer(&self->strip_input_buffer, false)) {
            destroy_pseudoconsole(self);
            PyMem_Free(unicode_command);
            return PyLong_FromLong(1);
        }
    } else {
        self->strip_input_buffer.data = NULL;
    }
    const DWORD time_delta = PyLong_AsUnsignedLong(args[2]);
    if ((time_delta == (DWORD)-1) && PyErr_Occurred()) {
        return NULL;
    }
    self->time_delta = time_delta;
    const DWORD post_end_delay = PyLong_AsUnsignedLong(args[3]);
    if ((post_end_delay == (DWORD)-1) && PyErr_Occurred()) {
        return NULL;
    }
    self->post_end_delay = post_end_delay;
    if ((!initialize_iobuffer(&self->write_buffer, false)) || 
        (!initialize_iobuffer(&self->read_buffer, false)) || 
        (!initialize_iobuffer(&self->strip_repeat_buffer, false))
    ) {
        destroy_pseudoconsole(self);
        atomic_store(&self->process_status, NOT_RUNNING);
        return PyLong_FromLong(1);
    }
    if (!set_up_pseudo_console(self)) {
        destroy_pseudoconsole(self);
        PyMem_Free(unicode_command);
        return PyLong_FromLong(1);
    }
    HRESULT create_process_result;
    if ((create_process_result = create_process(self, unicode_command))
            != S_OK
    ) {
        PyMem_Free(unicode_command);
        unicode_command = NULL;
        destroy_pseudoconsole(self);
        if (create_process_result == E_FILENOTFOUND) {
            return PyLong_FromLong(2);
        } else if (create_process_result == E_PATHNOTFOUND) {
            return PyLong_FromLong(2);
        } else if (create_process_result == E_ACCESSDENIED) {
            return PyLong_FromLong(3);
        } else if (create_process_result == E_FILENAMETOOLONG) {
            return PyLong_FromLong(4);
        } else {
            return PyLong_FromLong(5);
        }
    }
    PyMem_Free(unicode_command);
    unicode_command = NULL;
    self->is_read_buffer_available = true;
    self->is_write_buffer_available = true;
    if (launch_io_listeners(self) != S_OK) {
        kill_process_internal(self);
        return PyLong_FromLong(1);
    }
    self->has_any_process_run_yet = true;
    return PyLong_FromLong(0);
}

static PyObject *resize_pseudoconsole(
        ConPTYBriefcase *self, PyObject *const *args, Py_ssize_t nargs
) {
    if (nargs != 2) {
        return NULL;
    }
    const int width = PyLong_AsInt(args[0]);
    if ((width <= 0) || PyErr_Occurred()
     || (width > SHRT_MAX) || (width < SHRT_MIN)
    ) {
        return NULL;
    }
    const int height = PyLong_AsInt(args[1]);
    if ((height <= 0) || PyErr_Occurred()
     || (height > SHRT_MAX) || (height < SHRT_MIN)
    ) {
        return NULL;
    }
    self->pseudo_console_size.X = (SHORT)width;
    self->pseudo_console_size.Y = (SHORT)height;
    if (self->process_status == RUNNING) {
        if (ResizePseudoConsole(self->hPC, self->pseudo_console_size)
                == S_OK
        ) {
            Py_RETURN_TRUE;
        } else {
            Py_RETURN_FALSE;
        }
    } else {
        Py_RETURN_TRUE;
    }
}

static PyObject *read_from_buffer(
    ConPTYBriefcase *self, PyObject *const *args, Py_ssize_t nargs
) {
    if (nargs != 8) {
        return NULL;
    }
    const int read_lines = PyLong_AsInt(args[0]);
    if (((read_lines != 0) && (read_lines != 1)) || PyErr_Occurred()) {
        return NULL;
    }
    const size_t max_lines_to_read = PyLong_AsSize_t(args[1]);
    if ((max_lines_to_read == (size_t)-1) && PyErr_Occurred()) {
        return NULL;
    }
    size_t max_bytes_to_read = PyLong_AsSize_t(args[2]);
    if ((max_bytes_to_read == (size_t)-1) && PyErr_Occurred()) {
        return NULL;
    }
    const int raw_data = PyLong_AsInt(args[3]);
    if (((raw_data != 0) && (raw_data != 1)) || PyErr_Occurred()) {
        return NULL;
    }
    const int vts_mode_int = PyLong_AsInt(args[4]);
    if ((vts_mode_int < 0) || PyErr_Occurred()) {
        return NULL;
    }
    VTSMode vts_mode = (VTSMode)vts_mode_int;
    if (!PyUnicode_Check(args[5])) {
        return NULL;
    }
    const char *twspaces_ref_pointer = PyUnicode_AsUTF8(args[5]);
    if (twspaces_ref_pointer == NULL) {
        return NULL;
    }
    const size_t twspaces_length = strlen(twspaces_ref_pointer);
    char *twspaces = (char *)malloc((twspaces_length + 1));
    if (twspaces == NULL) {
        Py_RETURN_NONE;
    }
    twspaces[twspaces_length] = '\0';
    size_t cursorx = PyLong_AsSize_t(args[6]);
    if ((cursorx == (size_t)-1) && PyErr_Occurred()) {
        return NULL;
    }
    size_t cursory = PyLong_AsSize_t(args[7]);
    if ((cursory == (size_t)-1) && PyErr_Occurred()) {
        return NULL;
    }

    char *c_data_to_read = NULL;
    char *c_data_to_write = NULL;
    ConPTYIOBuffer twspaces_buffer = {
        twspaces, 0, twspaces_length, twspaces_length + 1
    };

    bool should_kill_process = false;

    Py_BEGIN_ALLOW_THREADS

    memcpy(&twspaces[0], &twspaces_ref_pointer[0], twspaces_length);

    const DWORD time_delta = self->time_delta;
    while (1) {
        bool expected_value = true;
        if (atomic_compare_exchange_strong(
                &self->is_read_buffer_available,
                &expected_value, false)
        ) {
            if (read_lines) {
                bool is_process_running =
                    get_is_console_running_internal(self);
                const char *new_line_pointer = self->read_buffer.data;
                if (max_lines_to_read == (size_t)-1) {
                    if (is_process_running) {
                        new_line_pointer =
                            strrchr(self->read_buffer.data, '\n');
                        if (new_line_pointer == NULL) {
                            max_bytes_to_read = 0;
                        } else {
                            max_bytes_to_read = ++new_line_pointer
                                              - self->read_buffer.data;
                        }
                    } else {
                        max_bytes_to_read = (size_t)-1;
                    }
                } else {
                    size_t n = 0;
                    max_bytes_to_read = 0;
                    while ((new_line_pointer = strchr(new_line_pointer, '\n'))
                                != NULL
                    ) {
                        max_bytes_to_read = ++new_line_pointer
                                          - self->read_buffer.data;
                        if (++n == max_lines_to_read) {
                            break;
                        }
                    }
                    if ((max_bytes_to_read == 0) && !is_process_running) {
                        max_bytes_to_read = (size_t)-1;
                    }
                }
            }
            if (max_bytes_to_read > self->read_buffer.data_length) {
                max_bytes_to_read = self->read_buffer.data_length;
            }
            if (max_bytes_to_read != 0) {
                if ((c_data_to_read = (char *)malloc(max_bytes_to_read + 1))
                        == NULL
                ) {
                    should_kill_process = true;
                    atomic_store(&self->is_read_buffer_available, true);
                    break;
                }
                c_data_to_read[max_bytes_to_read] = '\0';
                memcpy(c_data_to_read, self->read_buffer.data,
                        max_bytes_to_read);
                if (!shrink_iobuffer(&self->read_buffer, max_bytes_to_read,
                        MAX_READ_BUFFER_SIZE)
                ) {
                    free((void *)c_data_to_read);
                    c_data_to_read = NULL;
                    should_kill_process = true;
                    atomic_store(&self->is_read_buffer_available, true);
                    break;
                }
            }
            atomic_store(&self->is_read_buffer_available, true);
            break;
        }
        Sleep(time_delta);
    }

    if ((c_data_to_read != NULL) && (max_bytes_to_read != 0) && (!raw_data)) {
        if (!strip_vts_from_data(c_data_to_read, &max_bytes_to_read,
                &c_data_to_write, &vts_mode, &twspaces_buffer,
                &self->pseudo_console_size.X, &self->pseudo_console_size.Y,
                &cursorx, &cursory, NULL)
        ) {
            free((void *)c_data_to_read);
            c_data_to_read = NULL;
        }
    }

    if (should_kill_process) {
        kill_process_internal(self);
    }

    Py_END_ALLOW_THREADS

    if (should_kill_process) {
        free((void *)twspaces_buffer.data);
        Py_RETURN_NONE;
    } else if (max_bytes_to_read == 0) {
        free((void *)c_data_to_read);
        free((void *)c_data_to_write);
        free((void *)twspaces_buffer.data);
        return PyLong_FromLong(0);
    } else {
        PyObject *py_result_bundle = PyTuple_New(5);
        PyObject *py_data_to_read = PyUnicode_FromStringAndSize(
            &c_data_to_write[0], max_bytes_to_read);
        PyObject *py_vts_mode = PyLong_FromLong(vts_mode);
        PyObject *py_twspaces = PyUnicode_FromStringAndSize(
            &twspaces_buffer.data[0], twspaces_buffer.data_length);
        PyObject *py_cursorx = PyLong_FromSize_t(cursorx);
        PyObject *py_cursory = PyLong_FromSize_t(cursory);
        if ((py_result_bundle == NULL) || (py_data_to_read == NULL)
                                       || (py_vts_mode == NULL)
                                       || (py_twspaces == NULL)
                                       || (py_cursorx == NULL)
                                       || (py_cursory == NULL)
        ) {
            Py_XDECREF(py_result_bundle);
            Py_XDECREF(py_data_to_read);
            Py_XDECREF(py_vts_mode);
            Py_XDECREF(py_twspaces);
            Py_XDECREF(py_cursorx);
            Py_XDECREF(py_cursory);
            free((void *)c_data_to_read);
            free((void *)c_data_to_write);
            free((void *)twspaces_buffer.data);
            kill_process_internal(self);
            Py_RETURN_NONE;
        }
        free((void *)c_data_to_read);
        free((void *)c_data_to_write);
        free((void *)twspaces_buffer.data);
        PyTuple_SET_ITEM(py_result_bundle, 0, py_data_to_read);
        PyTuple_SET_ITEM(py_result_bundle, 1, py_vts_mode);
        PyTuple_SET_ITEM(py_result_bundle, 2, py_twspaces);
        PyTuple_SET_ITEM(py_result_bundle, 3, py_cursorx);
        PyTuple_SET_ITEM(py_result_bundle, 4, py_cursory);
        return py_result_bundle;
    }
}

static PyObject *write_to_buffer(
        ConPTYBriefcase *self, PyObject *const *args, Py_ssize_t nargs
) {
    if (nargs != 1) {
        return NULL;
    }
    if (!PyUnicode_Check(args[0])) {
        return NULL;
    }
    const char *data_to_write_ref_pointer = PyUnicode_AsUTF8(args[0]);
    if (data_to_write_ref_pointer == NULL) {
        return NULL;
    }
    const size_t data_to_write_length = strlen(data_to_write_ref_pointer);
    if (data_to_write_length == 0) {
        return PyLong_FromLong(1);
    }

    char *data_to_write = (char *)malloc((data_to_write_length + 1));
    if (data_to_write == NULL) {
        return NULL;
    }
    data_to_write[data_to_write_length] = '\0';
    memcpy(&data_to_write[0], &data_to_write_ref_pointer[0],
            data_to_write_length);

    int result_code = 1;

    Py_BEGIN_ALLOW_THREADS

    const DWORD time_delta = self->time_delta;
    while (1) {
        bool expected_value = true;
        if (atomic_compare_exchange_strong(
                &self->is_write_buffer_available,
                &expected_value, false)
        ) {
            if (!extend_iobuffer(&self->write_buffer, data_to_write_length)
            ) {
                result_code = 0;
                free((void *)data_to_write);
                kill_process_internal(self);
                break;
            }
            self->write_buffer.cursor_position = 
                self->write_buffer.data_length;
            memcpy(
                &self->write_buffer.data[self->write_buffer.cursor_position],
                &data_to_write[0], data_to_write_length
            );
            free((void *)data_to_write);
            self->write_buffer.data_length += data_to_write_length;
            self->write_buffer.data[self->write_buffer.data_length] = '\0';
            self->is_write_buffer_available = true;
            break;
        }
        Sleep(time_delta);
    }

    Py_END_ALLOW_THREADS

    return PyLong_FromLong(result_code);
}

static PyObject *get_is_console_running(
        ConPTYBriefcase *self, PyObject *Py_UNUSED(args)
) {
    if (get_is_console_running_internal(self)) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyObject *get_has_process_ended(
        ConPTYBriefcase *self, PyObject *Py_UNUSED(args)
) {
    const ProcessStatus process_status = atomic_load(&self->process_status);
    if ((process_status == GRACEFULLY_TERMINATING)
     || (process_status == GRACEFULLY_TERMINATED)
     || (process_status == NOT_RUNNING)
    ) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyObject *get_is_input_sent(
        ConPTYBriefcase *self, PyObject *Py_UNUSED(args)
) {
    bool is_input_sent = false;
    bool expected_value = true;
    const DWORD time_delta = self->time_delta;
    while (1) {
        if (atomic_compare_exchange_strong(
                &self->is_write_buffer_available,
                &expected_value, false)
        ) {
            if (self->write_buffer.data_length == 0) {
                is_input_sent = true;
            }
            self->is_write_buffer_available = true;
            break;
        } else if (atomic_load(&self->process_status) != RUNNING) {
            break;
        }
        Sleep(time_delta);
    }
    if (is_input_sent) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyObject *kill_process(
        ConPTYBriefcase *self, PyObject *Py_UNUSED(args)
) {
    bool kill_successful;

    Py_BEGIN_ALLOW_THREADS

    kill_successful = kill_process_internal(self);

    Py_END_ALLOW_THREADS

    if (kill_successful) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyObject *get_process_exit_code(
        ConPTYBriefcase *self, PyObject *Py_UNUSED(args)
) {
    if (!self->has_any_process_run_yet) {
        Py_RETURN_NONE;
    }
    if ((self->process_status != GRACEFULLY_TERMINATED)
     && (self->process_status != NOT_RUNNING)
    ) {
        Py_RETURN_NONE;
    }
    return PyLong_FromUnsignedLong(self->process_exit_code);
}

static PyObject *set_vts_display(
        ConPTYBriefcase *self, PyObject *const *args, Py_ssize_t nargs
) {
    UNREFERENCED_PARAMETER(self);
    static const DWORD physical_console_mode_with_vts =
        ENABLE_PROCESSED_OUTPUT | ENABLE_WRAP_AT_EOL_OUTPUT
                                | ENABLE_VIRTUAL_TERMINAL_PROCESSING;
    static const DWORD physical_console_mode_without_vts =
        ENABLE_PROCESSED_OUTPUT | ENABLE_WRAP_AT_EOL_OUTPUT;
    if (nargs != 1) {
        return NULL;
    }
    const int enable_vts_display = PyLong_AsInt(args[0]);
    if (((enable_vts_display != 0) && (enable_vts_display != 1))
        || PyErr_Occurred()
    ) {
        return NULL;
    }
    HANDLE physical_console_stdout = { GetStdHandle(STD_OUTPUT_HANDLE) };
    if ((physical_console_stdout == NULL)
     || (physical_console_stdout == INVALID_HANDLE_VALUE)
    ) {
        Py_RETURN_FALSE;
    }
    if (enable_vts_display) {
        if (!SetConsoleMode(
                physical_console_stdout, physical_console_mode_with_vts)
        ) {
            Py_RETURN_FALSE;
        }
    } else {
        if (!SetConsoleMode(
                physical_console_stdout, physical_console_mode_without_vts)
        ) {
            Py_RETURN_FALSE;
        }
    }
    Py_RETURN_TRUE;
}

static void pyconptyinternal_dealloc(ConPTYBriefcase *self) {
    kill_process_internal(self);
    free_iobuffer(&self->read_buffer);
    free_iobuffer(&self->write_buffer);
    free_iobuffer(&self->strip_input_buffer);
    free_iobuffer(&self->strip_repeat_buffer);
    WaitForSingleObject(self->kill_lock, INFINITE);
    CloseHandle(self->kill_lock);
    WaitForSingleObject(self->destroy_lock, INFINITE);
    CloseHandle(self->destroy_lock);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

/* ######################################################################## */
/*  PRIVATE FUNCTIONS                                                       */
/* ######################################################################## */

static bool initialize_iobuffer(
    ConPTYIOBuffer *iobuffer, bool first_initialization
) {
    if (first_initialization) {
        iobuffer->data = NULL;
    } else {
        free_iobuffer(iobuffer);
    }
    iobuffer->data = (char *)malloc(1);
    if (iobuffer->data == NULL) {
        return false;
    }
    iobuffer->data[0] = '\0';
    iobuffer->cursor_position = 0;
    iobuffer->data_length = 0;
    iobuffer->max_size = 1;
    return true;
}

static void free_iobuffer(ConPTYIOBuffer *iobuffer) {
    if (iobuffer->data != NULL) {
        free((void *)iobuffer->data);
        iobuffer->data = NULL;
    }
    iobuffer->cursor_position = 0;
    iobuffer->data_length = 0;
    iobuffer->max_size = 0;
}

static bool extend_iobuffer(
            ConPTYIOBuffer *iobuffer, size_t required_free_size
) {
    if (required_free_size == 0) {
        return true;
    }
    if (iobuffer->max_size <= iobuffer->data_length) {
        return false;
    }
    const size_t available_free_size = iobuffer->max_size - 1
                                     - iobuffer->data_length;
    if (available_free_size >= required_free_size) {
        return true;
    }
    const size_t incremental_size = required_free_size - available_free_size;
    char *temp_pointer = (char *)realloc(iobuffer->data,
            (iobuffer->max_size + incremental_size));
    if (temp_pointer == NULL) {
        free_iobuffer(iobuffer);
        return false;
    }
    iobuffer->data = temp_pointer;
    iobuffer->max_size += incremental_size;
    return true;
}

static bool shrink_iobuffer(
    ConPTYIOBuffer *iobuffer, size_t unused_size_at_start,
    size_t min_buffer_size
) {
    if (unused_size_at_start == 0) {
        return true;
    }
    if ((iobuffer->max_size - iobuffer->data_length) < 1) {
        return false;
    }
    if (unused_size_at_start > iobuffer->data_length) {
        return false;
    }
    const size_t possibly_new_max_size = iobuffer->max_size
                                       - unused_size_at_start;
    memmove(&iobuffer->data[0], &iobuffer->data[unused_size_at_start],
                possibly_new_max_size);
    iobuffer->data_length -= unused_size_at_start;
    iobuffer->data[iobuffer->data_length] = '\0';
    if ((possibly_new_max_size < min_buffer_size)
     && (iobuffer->max_size > min_buffer_size)
    ) {
        iobuffer->max_size = min_buffer_size;
        char *temp_pointer = (char *)realloc(
                iobuffer->data, min_buffer_size);
        if (temp_pointer == NULL) {
            free_iobuffer(iobuffer);
            return false;
        }
        iobuffer->data = temp_pointer;
    }
    return true;
}

static bool set_up_pseudo_console(ConPTYBriefcase *conptybriefcase_obj) {
    bool is_operation_successful = false;

    Py_BEGIN_ALLOW_THREADS

    HANDLE server_stdout_pipe_handle = NULL;
    HANDLE server_stdin_pipe_handle = NULL;

    if (!CreatePipe(&conptybriefcase_obj->client_stdout_pipe_handle,
            &server_stdout_pipe_handle, NULL, STDOUT_PIPE_BUFFER_SIZE)
    ) {
        goto END_OF_FUNCTION;
    }

    if (!CreatePipe(&server_stdin_pipe_handle,
            &conptybriefcase_obj->client_stdin_pipe_handle, NULL,
            STDIN_PIPE_BUFFER_SIZE)
    ) {
        goto END_OF_FUNCTION;
    }

    if (CreatePseudoConsole(conptybriefcase_obj->pseudo_console_size, 
                            server_stdin_pipe_handle, 
                            server_stdout_pipe_handle, 
                            0, 
                            &conptybriefcase_obj->hPC) != S_OK
    ) {
        goto END_OF_FUNCTION;
    }

    DeleteProcThreadAttributeList(conptybriefcase_obj->si.lpAttributeList);

    if (server_stdout_pipe_handle != NULL) {
        if (server_stdout_pipe_handle == INVALID_HANDLE_VALUE) {
            goto END_OF_FUNCTION;
        }
        CloseHandle(server_stdout_pipe_handle);
    }
    if (server_stdin_pipe_handle != NULL) {
        if (server_stdin_pipe_handle == INVALID_HANDLE_VALUE) {
            goto END_OF_FUNCTION;
        }
        CloseHandle(server_stdin_pipe_handle);
    }

    is_operation_successful = true;

    END_OF_FUNCTION:;

    Py_END_ALLOW_THREADS

    return is_operation_successful;
}

static HRESULT create_process(
        ConPTYBriefcase *conptybriefcase_obj, LPWSTR command
) {
    HRESULT return_result;

    Py_BEGIN_ALLOW_THREADS

    ZeroMemory(&conptybriefcase_obj->si, sizeof(STARTUPINFOEXW));
    ZeroMemory(&conptybriefcase_obj->pi, sizeof(PROCESS_INFORMATION));

    if ((return_result = prepare_startup_info(
            conptybriefcase_obj->hPC, &conptybriefcase_obj->si)) != S_OK
    ) {
        goto END_OF_FUNCTION;
    }

    if (!CreateProcessW(NULL,
                        command,
                        NULL,
                        NULL,
                        FALSE,
                        EXTENDED_STARTUPINFO_PRESENT
                            | CREATE_SUSPENDED
                            | CREATE_UNICODE_ENVIRONMENT,
                        NULL,
                        NULL,
                        &conptybriefcase_obj->si.StartupInfo,
                        &conptybriefcase_obj->pi)
    ) {
        return_result = HRESULT_FROM_WIN32(GetLastError());
        goto END_OF_FUNCTION;
    }

    HANDLE wait_for_process_completion_thread = 
        CreateThread(NULL,
                        0,
                        wait_for_process_completion,
                        conptybriefcase_obj,
                        0,
                        NULL);

    if (wait_for_process_completion_thread == NULL) {
        return_result = HRESULT_FROM_WIN32(GetLastError());
        goto END_OF_FUNCTION;
    } else {
        CloseHandle(wait_for_process_completion_thread);
    }

    return_result = S_OK;

    END_OF_FUNCTION:;

    Py_END_ALLOW_THREADS

    return return_result;
}

static HRESULT prepare_startup_info(HPCON hpc, STARTUPINFOEXW* psi) {
    STARTUPINFOEXW siEx;
    ZeroMemory(&siEx, sizeof(STARTUPINFOEXW));
    siEx.StartupInfo.cb = sizeof(STARTUPINFOEXW);

    size_t bytesRequired;
    InitializeProcThreadAttributeList(NULL, 1, 0, &bytesRequired);

    siEx.lpAttributeList = 
        (PPROC_THREAD_ATTRIBUTE_LIST)HeapAlloc(
            GetProcessHeap(), 0, bytesRequired
        );
    if (!siEx.lpAttributeList)
    {
        return E_OUTOFMEMORY;
    }

    if (!InitializeProcThreadAttributeList(
            siEx.lpAttributeList, 1, 0, &bytesRequired)
    ) {
        HeapFree(GetProcessHeap(), 0, siEx.lpAttributeList);
        return HRESULT_FROM_WIN32(GetLastError());
    }

    if (!UpdateProcThreadAttribute(siEx.lpAttributeList,
                                   0,
                                   PROC_THREAD_ATTRIBUTE_PSEUDOCONSOLE,
                                   hpc,
                                   sizeof(HPCON),
                                   NULL,
                                   NULL))
    {
        HeapFree(GetProcessHeap(), 0, siEx.lpAttributeList);
        return HRESULT_FROM_WIN32(GetLastError());
    }

    *psi = siEx;

    return S_OK;
}

static DWORD WINAPI wait_for_process_completion(LPVOID lpParam) {
    ConPTYBriefcase *conptybriefcase_obj = (ConPTYBriefcase *)lpParam;
    ProcessStatus expected_status = STARTING;
    if (!atomic_compare_exchange_strong(
        &conptybriefcase_obj->process_status, &expected_status, RUNNING)
    ) {
        return 0;
    }
    ResumeThread(conptybriefcase_obj->pi.hThread);
    DWORD res;
    while (
        (res =
            WaitForSingleObject(conptybriefcase_obj->pi.hProcess, INFINITE))
                    != WAIT_OBJECT_0
    ) {
        Sleep(1);
    }
    bool can_terminate = false;
    expected_status = RUNNING;
    if (atomic_compare_exchange_strong(
        &conptybriefcase_obj->process_status,
        &expected_status, GRACEFULLY_TERMINATING)
    ) {
        can_terminate = true;
    }
    if (can_terminate) {
        DWORD code_ref;
        GetExitCodeProcess(conptybriefcase_obj->pi.hProcess, &code_ref);
        conptybriefcase_obj->process_exit_code = code_ref;
        conptybriefcase_obj->is_read_buffer_available = true;
        conptybriefcase_obj->is_write_buffer_available = true;
        if (conptybriefcase_obj->post_end_delay != 0) {
            DWORD delay_count = 0;
            DWORD previous_tickcount = GetTickCount();
            while ((conptybriefcase_obj->process_status
                        != GRACEFULLY_TERMINATED)
                && (conptybriefcase_obj->process_status != NOT_RUNNING)
                && (delay_count <= conptybriefcase_obj->post_end_delay)
            ) {
                const DWORD current_tickcount = GetTickCount();
                delay_count += current_tickcount - previous_tickcount;
                previous_tickcount = current_tickcount;
                Sleep(1);
            }
        }
        kill_process_internal(conptybriefcase_obj);
    }
    return 0;
}

static DWORD WINAPI listen_for_stdin_stream(LPVOID lpParam) {
    ConPTYBriefcase *conptybriefcase_obj = (ConPTYBriefcase *)lpParam;
    atomic_bool send_pending = false;
    ConPTYIOBuffer temp_buffer, dummy_twspaces_buffer;
    if ((!initialize_iobuffer(&temp_buffer, true))
     || (!initialize_iobuffer(&dummy_twspaces_buffer, true))
    ) {
        kill_process_internal(conptybriefcase_obj);
        return 0;
    }
    const DWORD time_delta = conptybriefcase_obj->time_delta;
    while ((conptybriefcase_obj->process_status == STARTING)
        || (conptybriefcase_obj->process_status == RUNNING)
    ) {
        if (atomic_load(&send_pending)) {
            bool can_send = true;
            if (conptybriefcase_obj->strip_input_buffer.data != NULL) {
                bool expected_value = true;
                if (!atomic_compare_exchange_strong(
                        &conptybriefcase_obj->is_read_buffer_available,
                        &expected_value, false)
                ) {
                    can_send = false;
                }
            }
            if (can_send) {
                DWORD sent_output_buffer_size;
                if (!WriteFile(conptybriefcase_obj->client_stdin_pipe_handle,
                        temp_buffer.data, (DWORD)temp_buffer.data_length,
                        &sent_output_buffer_size,
                        NULL)
                ) {
                    if (GetLastError() != ERROR_BROKEN_PIPE) {
                        kill_process_internal(conptybriefcase_obj);
                    }
                    break;
                }
                if (conptybriefcase_obj->strip_input_buffer.data != NULL) {
                    if (!extend_iobuffer(
                            &conptybriefcase_obj->strip_input_buffer,
                            sent_output_buffer_size)
                    ) {
                        kill_process_internal(conptybriefcase_obj);
                        break;
                    }
                    conptybriefcase_obj->strip_input_buffer.cursor_position =
                        conptybriefcase_obj->strip_input_buffer.data_length;
                    memcpy(&conptybriefcase_obj->strip_input_buffer.data[
                        conptybriefcase_obj->
                            strip_input_buffer.cursor_position],
                        temp_buffer.data, sent_output_buffer_size
                    );
                    conptybriefcase_obj->strip_input_buffer.data_length +=
                        sent_output_buffer_size;
                    conptybriefcase_obj->strip_input_buffer.data[
                        conptybriefcase_obj->strip_input_buffer.data_length] =
                            '\0';
                }
                if (sent_output_buffer_size == temp_buffer.data_length) {
                    atomic_store(&send_pending, false);
                }
                if (!shrink_iobuffer(&temp_buffer,
                        sent_output_buffer_size, 1)
                ) {
                    kill_process_internal(conptybriefcase_obj);
                    break;
                }
                if (conptybriefcase_obj->strip_input_buffer.data != NULL) {
                    atomic_store(
                        &conptybriefcase_obj->is_read_buffer_available, true
                    );
                }
                continue;
            }
        } else {
            bool expected_value = true;
            if (atomic_compare_exchange_strong(
                    &conptybriefcase_obj->is_write_buffer_available,
                    &expected_value, false)
            ) {
                if (conptybriefcase_obj->write_buffer.data_length != 0) {
                    conptybriefcase_obj->write_buffer.cursor_position = 0;
                    if (!extend_iobuffer(&temp_buffer,
                            conptybriefcase_obj->write_buffer.data_length)
                    ) {
                        kill_process_internal(conptybriefcase_obj);
                        break;
                    }
                    temp_buffer.data_length =
                        conptybriefcase_obj->write_buffer.data_length;
                    memcpy(temp_buffer.data,
                        &conptybriefcase_obj->write_buffer.data[
                        conptybriefcase_obj->write_buffer.cursor_position],
                        conptybriefcase_obj->write_buffer.data_length
                    );
                    temp_buffer.data[temp_buffer.data_length] = '\0';
                    if (!shrink_iobuffer(&conptybriefcase_obj->write_buffer,
                            conptybriefcase_obj->write_buffer.data_length,
                            MAX_WRITE_BUFFER_SIZE)
                    ) {
                        kill_process_internal(conptybriefcase_obj);
                        break;
                    }
                    atomic_store(&send_pending, true);
                    conptybriefcase_obj->is_write_buffer_available = true;
                    continue;
                }
                conptybriefcase_obj->is_write_buffer_available = true;
            }
        }
        Sleep(time_delta);
    }
    return 0;
}

static DWORD WINAPI listen_for_stdout_stream(LPVOID lpParam) {
    static const char HTAB = '\x09';
    static const char SPACE = '\x20';
    ConPTYBriefcase *conptybriefcase_obj = (ConPTYBriefcase *)lpParam;
    VTSMode dummy_vts_mode;
    bool *is_vts_flags_1 = NULL;
    bool *is_vts_flags_2 = NULL;
    size_t i0, iN, dummy_length;
    int strstr_result;
    ConPTYIOBuffer dummy_twspaces_buffer, temp_buffer;
    if ((!initialize_iobuffer(&dummy_twspaces_buffer, true))
     || (!initialize_iobuffer(&temp_buffer, true))
    ) {
        kill_process_internal(conptybriefcase_obj);
        return 0;
    }
    bool data_available = false;
    const DWORD time_delta = conptybriefcase_obj->time_delta;
    DWORD readfile_error = 0;
    while (1) {
        if (data_available) {
            bool expected_value = true;
            if (atomic_compare_exchange_strong(
                    &conptybriefcase_obj->is_read_buffer_available,
                    &expected_value, false)
            ) {
                size_t total_strip_length = 0;
                if (conptybriefcase_obj->strip_repeat_buffer.data_length
                        != 0
                ) {
                    strstr_result = strstr_internal(temp_buffer.data,
                        conptybriefcase_obj->strip_repeat_buffer.data,
                        temp_buffer.data_length,
                        conptybriefcase_obj->strip_repeat_buffer.data_length,
                        &is_vts_flags_1, &is_vts_flags_2, &i0, &iN,
                        &dummy_length, &dummy_twspaces_buffer,
                        &dummy_vts_mode);
                    if (strstr_result == 1) {
                        total_strip_length = iN + 1;
                    } else if (strstr_result == -1) {
                        kill_process_internal(conptybriefcase_obj);
                        break;
                    }
                    if (!shrink_iobuffer(
                        &conptybriefcase_obj->strip_repeat_buffer,
                        conptybriefcase_obj->strip_repeat_buffer.data_length,
                        1)
                    ) {
                        kill_process_internal(conptybriefcase_obj);
                        break;
                    }
                }
                if (conptybriefcase_obj->strip_input_buffer.data != NULL) {
                    size_t shrink_amount = conptybriefcase_obj->
                                            strip_input_buffer.data_length;
                    char *ref_pointer =
                        &temp_buffer.data[total_strip_length];
                    const size_t ref_pointer_string_length =
                        temp_buffer.data_length - total_strip_length;
                    strstr_result = strstr_internal(ref_pointer,
                        conptybriefcase_obj->strip_input_buffer.data,
                        ref_pointer_string_length,
                        conptybriefcase_obj->strip_input_buffer.data_length,
                        &is_vts_flags_1, &is_vts_flags_2, &i0, &iN,
                        &dummy_length, &dummy_twspaces_buffer,
                        &dummy_vts_mode);
                    if (strstr_result == 1) {
                        total_strip_length += iN + 1;
                    } else if (strstr_result == -1) {
                        kill_process_internal(conptybriefcase_obj);
                        break;
                    } else {
                        strstr_result = strstr_internal(
                            conptybriefcase_obj->strip_input_buffer.data,
                            ref_pointer,
                            conptybriefcase_obj->
                                strip_input_buffer.data_length,
                            ref_pointer_string_length,
                            &is_vts_flags_1, &is_vts_flags_2, &i0, &iN,
                            &dummy_length, &dummy_twspaces_buffer,
                            &dummy_vts_mode);
                        if (strstr_result == 1) {
                            total_strip_length += ref_pointer_string_length;
                            shrink_amount = iN + 1;
                        } else if (strstr_result == -1) {
                            kill_process_internal(conptybriefcase_obj);
                            break;
                        }
                    }
                    if (!shrink_iobuffer(
                            &conptybriefcase_obj->strip_input_buffer,
                            shrink_amount, 1)
                    ) {
                        kill_process_internal(conptybriefcase_obj);
                        break;
                    }
                }
                const size_t read_length = temp_buffer.data_length
                                         - total_strip_length;
                if (read_length != 0) {
                    if (!extend_iobuffer(&conptybriefcase_obj->read_buffer,
                            read_length)
                    ) {
                        kill_process_internal(conptybriefcase_obj);
                        break;
                    }
                    conptybriefcase_obj->read_buffer.cursor_position =
                        conptybriefcase_obj->read_buffer.data_length;
                    memcpy(&conptybriefcase_obj->read_buffer.data[
                            conptybriefcase_obj->read_buffer.cursor_position],
                        &temp_buffer.data[total_strip_length], read_length
                    );
                    conptybriefcase_obj->read_buffer.data_length +=
                        read_length;
                    conptybriefcase_obj->read_buffer.data[
                        conptybriefcase_obj->read_buffer.data_length] = '\0';
                    if (temp_buffer.data[temp_buffer.data_length-1] != '\n') {
                        char *ref_pointer =
                            &temp_buffer.data[total_strip_length];
                        char *last_newline_ponter = NULL;
                        if ((last_newline_ponter =
                                strrchr(ref_pointer, '\n')) != NULL
                        ) {
                            last_newline_ponter++;
                        } else {
                            last_newline_ponter = ref_pointer;
                        }
                        const size_t norepeat_length =
                            last_newline_ponter - ref_pointer;
                        const size_t discarded_length =
                            ref_pointer - temp_buffer.data;
                        const size_t possible_repeat_length =
                            temp_buffer.data_length - discarded_length
                                                    - norepeat_length;
                        if (possible_repeat_length != 0) {
                            if (!extend_iobuffer(
                                    &conptybriefcase_obj->strip_repeat_buffer,
                                    possible_repeat_length)
                            ) {
                                kill_process_internal(conptybriefcase_obj);
                                break;
                            }
                            memcpy(
                                conptybriefcase_obj->strip_repeat_buffer.data,
                                last_newline_ponter, possible_repeat_length
                            );
                            conptybriefcase_obj->
                                strip_repeat_buffer.data_length
                                    = possible_repeat_length;
                            conptybriefcase_obj->
                                strip_repeat_buffer.data[
                                    conptybriefcase_obj->
                                        strip_repeat_buffer.data_length]
                                            = '\0';
                        }
                    }
                }
                if (temp_buffer.data_length != 0) {
                    if (!shrink_iobuffer(&temp_buffer, 
                            temp_buffer.data_length, 1)
                    ) {
                        kill_process_internal(conptybriefcase_obj);
                        break;
                    }
                }
                data_available = false;
                atomic_store(
                    &conptybriefcase_obj->is_read_buffer_available, true
                );
            }
            continue;
        } else {
            if (!extend_iobuffer(&temp_buffer, MAX_READ_BUFFER_SIZE)) {
                kill_process_internal(conptybriefcase_obj);
                break;
            }
            DWORD received_input_buffer_size = 0;
            if (!ReadFile(conptybriefcase_obj->client_stdout_pipe_handle,
                        temp_buffer.data,
                        MAX_READ_BUFFER_SIZE,
                        &received_input_buffer_size,
                        NULL)
            ) {
                readfile_error = GetLastError();
                if (readfile_error != ERROR_BROKEN_PIPE) {
                    kill_process_internal(conptybriefcase_obj);
                }
                break;
            }
            temp_buffer.data_length = received_input_buffer_size;
            temp_buffer.data[temp_buffer.data_length] = '\0';
            if (received_input_buffer_size != 0) {
                data_available = true;
                continue;
            }
        }
        Sleep(time_delta);
    }
    close_client_io_pipes(conptybriefcase_obj);
    if (readfile_error == ERROR_BROKEN_PIPE) {
        while ((conptybriefcase_obj->process_status == STARTING)
            || (conptybriefcase_obj->process_status == RUNNING)
        ) {
            Sleep(1);
        }
        kill_process_internal(conptybriefcase_obj);
    }
    conptybriefcase_obj->is_read_buffer_available = true;
    return 0;
}

static HRESULT create_listener_thread(
            ConPTYBriefcase *conptybriefcase_obj,
            LPTHREAD_START_ROUTINE function_pointer
) {
    HANDLE listener_thread = 
        CreateThread(NULL,
                        0,
                        function_pointer,
                        conptybriefcase_obj,
                        0,
                        NULL);

    if (listener_thread == NULL) {
        return HRESULT_FROM_WIN32(GetLastError());
    } else {
        CloseHandle(listener_thread);
        return S_OK;
    }
}

static HRESULT launch_io_listeners(ConPTYBriefcase *conptybriefcase_obj) {
    HRESULT return_result;

    Py_BEGIN_ALLOW_THREADS

    if ((return_result = create_listener_thread(
            conptybriefcase_obj, listen_for_stdin_stream)) != S_OK
    ) {
        goto END_OF_FUNCTION;
    }

    return_result = create_listener_thread(
            conptybriefcase_obj, listen_for_stdout_stream);

    END_OF_FUNCTION:;

    Py_END_ALLOW_THREADS

    return return_result;
}

static bool strip_vts_from_data(
    const char *const read_data, size_t *data_length, char **write_data,
    VTSMode *vts_mode, ConPTYIOBuffer *twspaces_buffer,
    const SHORT *const bufferwidth, const SHORT *const bufferheight,
    size_t *cursorx, size_t *cursory,
    bool *is_vts_flags
) {
    static const char BELL = '\x07';
    static const char HTAB = '\x09';
    static const char LINEFEED = '\x0A';
    static const char FORMFEED = '\x0C';
    static const char ESCAPE = '\x1B';
    static const char SPACE = '\x20';
    static const char EXCLAMATION_MARK = '\x21';
    static const char OPENING_ROUND_BRACKET = '\x28';
    static const char ZERO = '\x30';
    static const char FOUR = '\x34';
    static const char NINE = '\x39';
    static const char COLON = '\x3A';
    static const char SEMICOLON = '\x3B';
    static const char EQUALS_SIGN = '\x3D';
    static const char GREATER_THAN_SIGN = '\x3E';
    static const char QUESTION_MARK = '\x3F';
    static const char AT_SIGN = '\x40';
    static const char BIG_A = '\x41';
    static const char BIG_C = '\x43';
    static const char BIG_H = '\x48';
    static const char BIG_O = '\x4F';
    static const char BIG_Z = '\x5A';
    static const char OPENING_SQUARE_BRACKET = '\x5B';
    static const char BACKWARD_SLASH = '\x5C';
    static const char CLOSING_SQUARE_BRACKET = '\x5D';
    static const char SMALL_A = '\x61';
    static const char SMALL_F = '\x66';
    static const char SMALL_Z = '\x7A';
    static const char TILDE = '\x7E';
    static const char CTRL_CHAR_START = '\x00';
    static const char CTRL_CHAR_UNIT_SEPARATOR = '\x1F';
    static const char DEL = '\x7F';

    if (*data_length == 0) {
        return true;
    }
    if (!extend_iobuffer(twspaces_buffer, 100)) {
        return false;
    }
    const char *read_pointer = read_data;
    char *write_pointer = NULL;
    size_t write_data_length = *data_length;
    if (is_vts_flags == NULL) {
        if ((*write_data = (char *)malloc(write_data_length + 1)) == NULL) {
            return false;
        }
        write_pointer = *write_data;
    }
    size_t jump_to_row_number = 1;
    for (size_t i = 0; i != *data_length; i++) {
        if (is_vts_flags != NULL) {
            *is_vts_flags = 1;
        }
        switch (*vts_mode) {
            case VTSMODE_NONE: {
                jump_to_row_number = 1;
                size_t k = twspaces_buffer->cursor_position;
                while (--k != (size_t)-1) {
                    if ((twspaces_buffer->data[k] == SPACE)
                     || (twspaces_buffer->data[k] == HTAB)) {
                        break;
                    }
                    twspaces_buffer->data_length--;
                }
                twspaces_buffer->cursor_position =
                    twspaces_buffer->data_length;
                twspaces_buffer->data[twspaces_buffer->data_length] = '\0';
                if (*read_pointer == ESCAPE) {
                    *vts_mode = VTSMODE_ESCAPE;
                } else {
                    const bool wspaces = ((*read_pointer == SPACE)
                                       || (*read_pointer == HTAB));
                    const bool flfeeds = ((*read_pointer == FORMFEED)
                                       || (*read_pointer == LINEFEED));
                    if (((*read_pointer > CTRL_CHAR_UNIT_SEPARATOR)
                      && (*read_pointer != DEL)) || wspaces || flfeeds
                    ) {
                        if (flfeeds) {
                            if (twspaces_buffer->data_length != 0) {
                                twspaces_buffer->data_length = 0;
                                twspaces_buffer->cursor_position = 0;
                            }
                            if (is_vts_flags == NULL) {
                                *write_pointer++ = LINEFEED;
                                if (cursory != NULL) {
                                    if (*cursory < (size_t)*bufferheight) {
                                        (*cursory)++;
                                    }
                                    *cursorx = 1;
                                }
                            } else {
                                *is_vts_flags = 0;
                            }
                        } else if (wspaces) {
                            if ((twspaces_buffer->data_length + 1)
                                    == twspaces_buffer->max_size
                            ) {
                                if (!extend_iobuffer(twspaces_buffer, 100)) {
                                    free((void *)(*write_data));
                                    return false;
                                }
                            }
                            twspaces_buffer->data[
                                twspaces_buffer->cursor_position++] =
                                    *read_pointer;
                            twspaces_buffer->data[
                                twspaces_buffer->cursor_position] = '\0';
                            twspaces_buffer->data_length++;
                        } else {
                            if (twspaces_buffer->data_length != 0) {
                                twspaces_buffer->data[
                                    twspaces_buffer->cursor_position] = '\0';
                                if (is_vts_flags != NULL) {
                                    is_vts_flags -=
                                        twspaces_buffer->data_length;
                                    for (
                                            size_t j = 0;
                                            j < twspaces_buffer->data_length;
                                            j++
                                    ) {
                                        *(is_vts_flags++) = 0;
                                    }
                                } else {
                                    if (!extend_write_data_buffer(write_data,
                                            &write_pointer,
                                            &write_data_length,
                                            &twspaces_buffer->data_length)
                                    ) {
                                        return false;
                                    }
                                    memcpy(
                                        write_pointer,
                                        &twspaces_buffer->data[0],
                                        twspaces_buffer->data_length
                                    );
                                    write_pointer +=
                                        twspaces_buffer->data_length;
                                    if (cursorx != NULL) {
                                        const size_t new_cursorx = *cursorx
                                            + twspaces_buffer->data_length;
                                        if (new_cursorx <=
                                                (size_t)*bufferwidth
                                        ) {
                                            *cursorx = new_cursorx;
                                        }
                                    }
                                }
                                twspaces_buffer->data_length = 0;
                                twspaces_buffer->cursor_position = 0;
                            }
                            if (is_vts_flags == NULL) {
                                *write_pointer++ = *read_pointer;
                                if (cursorx != NULL) {
                                    if (*cursorx < (size_t)*bufferwidth) {
                                        (*cursorx)++;
                                    }
                                }
                            } else {
                                *is_vts_flags = 0;
                            }
                        }
                    }
                }
                break;
            }
            case VTSMODE_ESCAPE: {
                if ((*read_pointer == BIG_O)
                 || (*read_pointer == OPENING_ROUND_BRACKET)
                ) {
                    *vts_mode = VTSMODE_SKIP_1;
                } else if (*read_pointer == OPENING_SQUARE_BRACKET) {
                    *vts_mode = VTSMODE_OPENING_SQUARE_BRACKET;
                } else if (*read_pointer == CLOSING_SQUARE_BRACKET) {
                    *vts_mode = VTSMODE_CLOSING_SQUARE_BRACKET;
                } else {
                    *vts_mode = VTSMODE_NONE;
                }
                break;
            }
            case VTSMODE_OPENING_SQUARE_BRACKET: {
                if (*read_pointer == EXCLAMATION_MARK) {
                    *vts_mode = VTSMODE_SKIP_1;
                } else if ((*read_pointer == QUESTION_MARK)
                        || (*read_pointer == SEMICOLON)
                ) {
                    *vts_mode = VTSMODE_SEARCH_LETTER;
                } else if ((*read_pointer >= ZERO)
                        && (*read_pointer <= NINE)
                ) {
                    if (!append_to_twspaces_buffer(twspaces_buffer,
                            *read_pointer)
                    ) {
                        free((void *)(*write_data));
                        return false;
                    }
                    *vts_mode = VTSMODE_OPENING_SQUARE_BRACKET_DIGIT;
                } else {
                    *vts_mode = VTSMODE_NONE;
                }
                break;
            }
            case VTSMODE_CLOSING_SQUARE_BRACKET: {
                if ((*read_pointer >= ZERO)
                 && (*read_pointer <= NINE)
                ) {
                    *vts_mode = VTSMODE_SEARCH_ST;
                } else {
                    *vts_mode = VTSMODE_NONE;
                }
                break;
            }
            case VTSMODE_OPENING_SQUARE_BRACKET_DIGIT: {
                if (*read_pointer == BIG_C) {
                    const int num =
                        get_number_from_twspaces_buffer(twspaces_buffer);
                    if ((num != 0) && (is_vts_flags == NULL)) {
                        if (!extend_iobuffer(twspaces_buffer, num)) {
                            free((void *)(*write_data));
                            return false;
                        }
                        for (int j = 0; j != num; j++) {
                            twspaces_buffer->data[
                                twspaces_buffer->cursor_position++]
                                    = SPACE;
                            twspaces_buffer->data[
                                twspaces_buffer->cursor_position] = '\0';
                            twspaces_buffer->data_length++;
                            if (twspaces_buffer->data_length
                                    == *data_length
                            ) {
                                break;
                            }
                        }
                    }
                    *vts_mode = VTSMODE_NONE;
                } else if (*read_pointer == SPACE) {
                    get_number_from_twspaces_buffer(twspaces_buffer);
                    *vts_mode = VTSMODE_SKIP_1;
                } else if (*read_pointer == SEMICOLON) {
                    jump_to_row_number =
                        get_number_from_twspaces_buffer(twspaces_buffer);
                    *vts_mode = VTSMODE_SEARCH_Hf;
                } else if ((*read_pointer < ZERO) || (*read_pointer > NINE)) {
                    get_number_from_twspaces_buffer(twspaces_buffer);
                    *vts_mode = VTSMODE_NONE;
                } else {
                    if (!append_to_twspaces_buffer(twspaces_buffer,
                            *read_pointer)
                    ) {
                        free((void *)(*write_data));
                        return false;
                    }
                }
                break;
            }
            case VTSMODE_SKIP_1: {
                *vts_mode = VTSMODE_NONE;
                break;
            }
            case VTSMODE_SEARCH_ST: {
                if (*read_pointer == BELL) {
                    *vts_mode = VTSMODE_NONE;
                } else if (*read_pointer == ESCAPE) {
                    *vts_mode = VTSMODE_SKIP_1;
                }
                break;
            }
            case VTSMODE_SEARCH_LETTER: {
                if (((*read_pointer >= BIG_A) && (*read_pointer <= BIG_Z))
                 || ((*read_pointer >= SMALL_A) && (*read_pointer <= SMALL_Z))
                ) {
                    *vts_mode = VTSMODE_NONE;
                }
                break;
            }
            case VTSMODE_SEARCH_Hf: {
                if ((*read_pointer == BIG_H) || (*read_pointer == SMALL_F)) {
                    const size_t num =
                        get_number_from_twspaces_buffer(twspaces_buffer);
                    if ((cursory != NULL) && (num == 1)) {
                        if ((jump_to_row_number > *cursory)
                         && (jump_to_row_number <= (size_t)*bufferheight)
                        ) {
                            const size_t number_of_rn = jump_to_row_number
                                                      - *cursory;
                            *cursory = jump_to_row_number;
                            *cursorx = 1;
                            if (!extend_write_data_buffer(write_data,
                                    &write_pointer, &write_data_length,
                                    &number_of_rn)
                            ) {
                                return false;
                            }
                            for (size_t j = 0; j < number_of_rn; j++) {
                                *write_pointer++ = LINEFEED;
                            }
                        }
                    }
                    *vts_mode = VTSMODE_NONE;
                } else if ((*read_pointer < ZERO) || (*read_pointer > NINE)) {
                    get_number_from_twspaces_buffer(twspaces_buffer);
                    *vts_mode = VTSMODE_NONE;
                } else {
                    if (!append_to_twspaces_buffer(twspaces_buffer,
                            *read_pointer)
                    ) {
                        free((void *)(*write_data));
                        return false;
                    }
                }
                break;
            }
        }
        read_pointer++;
        if (is_vts_flags != NULL) {
            is_vts_flags++;
        }
    }
    if (is_vts_flags == NULL) {
        *write_pointer = '\0';
        *data_length = write_pointer - *write_data;
    } else if (twspaces_buffer->data_length != 0) {
        for (size_t i = 0; i < twspaces_buffer->data_length; i++) {
            if ((twspaces_buffer->data[i] == SPACE)
             || (twspaces_buffer->data[i] == HTAB)
            ) {
                *(--is_vts_flags) = 0;
            }
        }
    }
    return true;
}

static bool extend_write_data_buffer(
    char **write_data, char **write_pointer,
    size_t *write_data_length,
    const size_t *const additional_size
) {
    const size_t write_offset = *write_pointer - *write_data;
    *write_data_length += *additional_size;
    char *temp_pointer = (char *)realloc(*write_data, *write_data_length);
    if (temp_pointer == NULL) {
        free((void *)(*write_data));
        return false;
    }
    *write_data = temp_pointer;
    *write_pointer = *write_data + write_offset;
    return true;
}

static bool append_to_twspaces_buffer(
    ConPTYIOBuffer *twspaces_buffer, char data
) {
    if ((twspaces_buffer->data_length + 1) ==
            twspaces_buffer->max_size
    ) {
        if (!extend_iobuffer(twspaces_buffer, 100)) {
            return false;
        }
    }
    twspaces_buffer->data[
        twspaces_buffer->cursor_position++] = data;
    twspaces_buffer->data[
        twspaces_buffer->cursor_position] = '\0';
    twspaces_buffer->data_length++;
    return true;
}

static int get_number_from_twspaces_buffer(ConPTYIOBuffer *twspaces_buffer) {
    static const char HTAB = '\x09';
    static const char SPACE = '\x20';
    char num_str[10] = {0};
    size_t m = 9;
    size_t k = twspaces_buffer->cursor_position;
    while (--k != (size_t)-1) {
        if ((twspaces_buffer->data[k] == SPACE)
         || (twspaces_buffer->data[k] == HTAB)) {
            break;
        }
        twspaces_buffer->data_length--;
        num_str[--m] = twspaces_buffer->data[k];
    }
    int num = 0;
    if (m != 9) {
        twspaces_buffer->cursor_position =
            twspaces_buffer->data_length;
        twspaces_buffer->data[
            twspaces_buffer->cursor_position] = '\0';
        num = atoi(&num_str[m]);
    }
    return num;
}

static int strstr_internal(
    char *s1, char *s2, size_t s1_length, size_t s2_length,
    bool **s1_is_vts_flags, bool **s2_is_vts_flags, size_t *i0,
    size_t *iN, size_t *dummy_length,
    ConPTYIOBuffer *dummy_twspaces_buffer, VTSMode *dummy_vts_mode
) {
    int return_code = -1;
    if ((*s1_is_vts_flags = (bool *)malloc(s1_length * sizeof(bool)))
            == NULL
    ) {
        goto CLEANUP;
    }
    if ((*s2_is_vts_flags = (bool *)malloc(s2_length * sizeof(bool)))
            == NULL
    ) {
        goto CLEANUP;
    }
    *dummy_vts_mode = 0;
    *dummy_length = s1_length;
    dummy_twspaces_buffer->data_length = 0;
    dummy_twspaces_buffer->cursor_position = 0;
    if (!strip_vts_from_data(s1, dummy_length, NULL,
            dummy_vts_mode, dummy_twspaces_buffer, 0, 0, NULL, NULL,
            *s1_is_vts_flags)
    ) {
        goto CLEANUP;
    }
    *dummy_vts_mode = 0;
    *dummy_length = s2_length;
    dummy_twspaces_buffer->data_length = 0;
    dummy_twspaces_buffer->cursor_position = 0;
    if (!strip_vts_from_data(s2, dummy_length, NULL,
            dummy_vts_mode, dummy_twspaces_buffer, 0, 0, NULL, NULL,
            *s2_is_vts_flags)
    ) {
        goto CLEANUP;
    }
    return_code = 0;
    if ((s1_length == 0) || (s2_length == 0) || (s2_length > s1_length)) {
        goto CLEANUP;
    }
    *iN = 0;
    size_t j = 0;
    for (size_t i = 0; i < s1_length; i++) {
        if ((*s1_is_vts_flags)[i]) {
            continue;
        }
        while ((*s2_is_vts_flags)[j]) {
            if (++j == s2_length) {
                goto CLEANUP;
            }
        }
        if (s1[i] != s2[j]) {
            return_code = 0;
            break;
        }
        if (*iN == 0) {
            *i0 = i;
        }
        *iN = i;
        return_code = 1;
        if (++j == s2_length) {
            break;
        }
    }

    CLEANUP:;

    if (*s1_is_vts_flags != NULL) {
        free((void *)(*s1_is_vts_flags));
        *s1_is_vts_flags = NULL;
    }
    if (*s2_is_vts_flags != NULL) {
        free((void *)(*s2_is_vts_flags));
        *s2_is_vts_flags = NULL;
    }
    return return_code;
}

static void close_client_io_pipes(ConPTYBriefcase *conptybriefcase_obj) {
    if (conptybriefcase_obj->client_stdout_pipe_handle != NULL) {
        CloseHandle(conptybriefcase_obj->client_stdout_pipe_handle);
        conptybriefcase_obj->client_stdout_pipe_handle = NULL;
    }
    if (conptybriefcase_obj->client_stdin_pipe_handle != NULL) {
        CloseHandle(conptybriefcase_obj->client_stdin_pipe_handle);
        conptybriefcase_obj->client_stdin_pipe_handle = NULL;
    }
}

static bool kill_process_internal(ConPTYBriefcase *conptybriefcase_obj) {
    bool kill_successful = true;
    const DWORD lock_status =
                WaitForSingleObject(conptybriefcase_obj->kill_lock, 0);
    if (lock_status == WAIT_OBJECT_0) {
        ProcessStatus expected_status = RUNNING;
        atomic_compare_exchange_strong(&conptybriefcase_obj->process_status,
                &expected_status, FORCEFULLY_TERMINATING);
        if ((conptybriefcase_obj->process_status == GRACEFULLY_TERMINATING)
         || (conptybriefcase_obj->process_status == FORCEFULLY_TERMINATING)
        ) {
            conptybriefcase_obj->is_write_buffer_available = false;
            if (conptybriefcase_obj->process_status ==
                    FORCEFULLY_TERMINATING
            ) {
                if (!TerminateProcess(conptybriefcase_obj->pi.hProcess,
                        EXIT_FAILURE)
                ) {
                    kill_successful = false;
                } else {
                    DWORD code_ref;
                    GetExitCodeProcess(conptybriefcase_obj->pi.hProcess,
                        &code_ref);
                    conptybriefcase_obj->process_exit_code = code_ref;
                }
            }
            if (kill_successful) {
                destroy_pseudoconsole(conptybriefcase_obj);
            }
        }
        ReleaseMutex(conptybriefcase_obj->kill_lock);
    }

    return kill_successful;
}

static void destroy_pseudoconsole(ConPTYBriefcase *conptybriefcase_obj) {
    const DWORD lock_status =
            WaitForSingleObject(conptybriefcase_obj->destroy_lock, 0);
    if (lock_status == WAIT_OBJECT_0) {
        const ProcessStatus current_process_status =
            atomic_load(&conptybriefcase_obj->process_status);
        if ((current_process_status != GRACEFULLY_TERMINATING)
         && (current_process_status != FORCEFULLY_TERMINATING)
         && (current_process_status != STARTING)
        ) {
            return;
        }
        if (conptybriefcase_obj->pi.hThread != NULL) {
            CloseHandle(conptybriefcase_obj->pi.hThread);
            conptybriefcase_obj->pi.hThread = NULL;
        }
        if (conptybriefcase_obj->pi.hProcess != NULL) {
            CloseHandle(conptybriefcase_obj->pi.hProcess);
            conptybriefcase_obj->pi.hProcess = NULL;
        }
        if (conptybriefcase_obj->hPC != NULL) {
            ClosePseudoConsole(conptybriefcase_obj->hPC);
            conptybriefcase_obj->hPC = NULL;
        }
        if (conptybriefcase_obj->process_status != STARTING) {
            const DWORD time_delta = conptybriefcase_obj->time_delta;
            while (conptybriefcase_obj->client_stdout_pipe_handle != NULL) {
                Sleep(time_delta);
            }
        }
        if (conptybriefcase_obj->si.lpAttributeList != NULL) {
            free((void *)conptybriefcase_obj->si.lpAttributeList);
            conptybriefcase_obj->si.lpAttributeList = NULL;
        }
        if (conptybriefcase_obj->process_status == GRACEFULLY_TERMINATING) {
            atomic_store(&conptybriefcase_obj->process_status,
                GRACEFULLY_TERMINATED);
        } else {
            atomic_store(&conptybriefcase_obj->process_status, NOT_RUNNING);
        }
        ReleaseMutex(conptybriefcase_obj->destroy_lock);
    }
}

static bool get_is_console_running_internal(
    ConPTYBriefcase *conptybriefcase_obj
) {
    const ProcessStatus process_status =
        atomic_load(&conptybriefcase_obj->process_status);
    return ((process_status != GRACEFULLY_TERMINATED)
         && (process_status != NOT_RUNNING));
}
