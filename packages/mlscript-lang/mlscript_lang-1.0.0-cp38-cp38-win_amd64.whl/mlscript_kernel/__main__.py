from .kernel import MLScriptKernel
from ipykernel.kernelapp import IPKernelApp

if __name__ == '__main__':
    IPKernelApp.launch_instance(kernel_class=MLScriptKernel)