from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

setup(
    name="mymodule",
    version="0.1",
    ext_modules=[
        CUDAExtension(
            name="mymodule.cuda",
            sources=[
                "src/mymodule/mymodule_host.cpp",
                "src/mymodule/host_cuda.cu",
            ],
        )
    ],
    cmdclass={"build_ext": BuildExtension},
)
