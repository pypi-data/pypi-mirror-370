import os
import sys
import io
import traceback
from contextlib import redirect_stdout

# On Windows, Python 3.8+ needs help finding DLLs in a venv
# This code adds the venv's library paths to the DLL search path
# It must be at the top, before the interpreter is imported.
if os.name == 'nt':
    try:
        # Get the path to the current python environment
        venv_path = sys.prefix
        # Add the relevant bin directories to the DLL search path
        os.add_dll_directory(os.path.join(venv_path, 'Library', 'bin'))
        os.add_dll_directory(os.path.join(venv_path, 'Scripts'))
    except (AttributeError, FileNotFoundError):
        # os.add_dll_directory is Python 3.8+
        # If it fails, we just continue and hope for the best
        pass

# We wrap the import in a try/except to log startup crashes
try:
    from interpreter.core import Interpreter
    INTERPRETER_INSTANCE = Interpreter()
    IMPORT_ERROR = None
except Exception:
    INTERPRETER_INSTANCE = None
    # Write the full traceback to a log file for debugging
    with open("kernel_crash.log", "w") as f:
        traceback.print_exc(file=f)
    IMPORT_ERROR = traceback.format_exc()

from ipykernel.kernelbase import Kernel

class MLScriptKernel(Kernel):
    implementation = 'mlscript'
    implementation_version = '1.0.0'
    language = 'mlscript'
    language_version = '0.8'
    language_info = {
        'name': 'mlscript',
        'mimetype': 'text/plain',
        'file_extension': '.ms',
    }
    banner = "mlscript Kernel"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.interp = INTERPRETER_INSTANCE

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        # If the interpreter failed to import during startup, report the error
        if self.interp is None:
            error_text = "Kernel failed to start. See kernel_crash.log for details.\n---\n" + (IMPORT_ERROR or "Unknown error")
            error_content = {'name': 'stderr', 'text': error_text}
            self.send_response(self.iopub_socket, 'stream', error_content)
            return {'status': 'error', 'execution_count': self.execution_count,
                    'ename': 'ImportError', 'evalue': 'Failed to import backend', 'traceback': []}
        
        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}

        f = io.StringIO()

        try:
            with redirect_stdout(f):
                self.interp.run(code)
            
            output = f.getvalue()
            if not silent:
                stream_content = {'name': 'stdout', 'text': output}
                self.send_response(self.iopub_socket, 'stream', stream_content)
        
        except Exception as e:
            error_content = {'name': 'stderr', 'text': str(e)}
            self.send_response(self.iopub_socket, 'stream', error_content)
            return {'status': 'error', 'execution_count': self.execution_count,
                    'ename': type(e).__name__, 'evalue': str(e), 'traceback': []}

        return {'status': 'ok', 'execution_count': self.execution_count,
                'payload': [], 'user_expressions': {}}