#include <torch/extension.h>

void hostCuda(float *ptrTab, int n);

torch::Tensor add_one(torch::Tensor x)
{
    TORCH_CHECK(x.dtype() == torch::kFloat32, "x must be float32");
    TORCH_CHECK(x.is_contiguous(), "x must be contiguous");

    int64_t n = x.numel();
    float *data = x.data_ptr<float>();

    hostCuda(data, static_cast<int>(n));

    return x;
}

PYBIND11_MODULE(cuda, m)
{
    m.doc() = "pybind11 example module";
    m.def("add_one", &add_one, "Add one to each element (CUDA)");
}