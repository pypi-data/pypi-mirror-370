#pragma once

#include <cuda_runtime.h>
#include <cstddef>
#include <cstdio>
#include <cstdlib>

#define CUDA_CHECK(x)                                                                \
    do {                                                                             \
        cudaError_t err = x;                                                         \
        if (err != cudaSuccess) {                                                    \
            fprintf(stderr, "CUDA error in %s at %s:%d: %s (%s=%d)\n", __FUNCTION__, \
                    __FILE__, __LINE__, cudaGetErrorString(err),                     \
                    cudaGetErrorName(err), err);                                     \
            abort();                                                                 \
        }                                                                            \
    } while (0)

struct cuda_buffer {
    char *data;
    size_t size;
};

struct cuda_ctx {
    cuda_buffer buffer;
    cudaStream_t stream;
};

struct cuda_config {
    int device_id;
    int n_streams;
    size_t n_bytes_per_stream;
};