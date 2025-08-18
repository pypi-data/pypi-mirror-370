
from ipykernel.kernelapp import IPKernelApp
from .kernel import ISQLRouterKernel

IPKernelApp.launch_instance(kernel_class=ISQLRouterKernel)
