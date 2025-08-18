import sys
import json
import os
from jupyter_client.kernelspec import KernelSpecManager
from IPython.utils.tempdir import TemporaryDirectory

# This argv line is the critical correction.
kernel_json = {
    "argv": [sys.executable, "-m", "mlscript_kernel", "-f", "{connection_file}"],
    "display_name": "mlscript",
    "language": "mlscript",
}

def install_my_kernel_spec(user=True):
    with TemporaryDirectory() as td:
        os.chmod(td, 0o755)
        with open(os.path.join(td, 'kernel.json'), 'w') as f:
            json.dump(kernel_json, f, sort_keys=True)
        
        print('Installing Jupyter kernel spec...')
        KernelSpecManager().install_kernel_spec(td, 'mlscript', user=user, replace=True)

def _is_root():
    try:
        return os.geteuid() == 0
    except AttributeError:
        # os.geteuid is not available on Windows
        return False

def main(argv=None):
    user = not _is_root()
    install_my_kernel_spec(user=user)
    print("mlscript kernel successfully installed.")

if __name__ == '__main__':
    main()