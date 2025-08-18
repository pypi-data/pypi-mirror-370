#pragma once
#include "kadd.cu"

// Fonction callable depuis C++ / Python
void hostCuda(float *ptrTab, int n)
{
    float *ptrTabGM;
    size_t sizeOctet = sizeof(float) * n;
    cudaMalloc(&ptrTabGM, sizeOctet);
    cudaMemcpy(ptrTabGM, ptrTab, sizeOctet, cudaMemcpyHostToDevice);

    dim3 dg(68, 1, 1);
    dim3 db(128, 1, 1);
    kadd<<<dg, db>>>(ptrTabGM, n);

    cudaMemcpy(ptrTab, ptrTabGM, sizeOctet, cudaMemcpyDeviceToHost);
    cudaFree(ptrTabGM);
}
