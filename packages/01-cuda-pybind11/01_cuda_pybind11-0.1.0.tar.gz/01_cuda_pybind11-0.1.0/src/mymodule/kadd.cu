#include <cuda_runtime.h>

__global__ void kadd(float *tab, int n)
{
    const int NB_THREAD = blockDim.x * gridDim.x;
    const int TID = threadIdx.x + blockIdx.x * blockDim.x;

    int s = TID;
    while (s < n)
    {
        tab[s] += 1.0f;
        s += NB_THREAD;
    }
}