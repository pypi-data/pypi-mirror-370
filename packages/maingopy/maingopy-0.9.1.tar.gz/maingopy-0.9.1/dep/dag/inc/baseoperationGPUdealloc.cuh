
#ifdef CUDA_INSTALLED
#pragma once
// #include "baseoperation.h"

namespace SVT_DAG {
    __global__ void deallocate_memory_on_GPU(Concept** d_ptrToSpecificOperation)
    {
        if (threadIdx.x + blockDim.x * blockIdx.x == 0)
            delete (*d_ptrToSpecificOperation);
    }

    BaseOperation:: ~BaseOperation() {
                delete _conceptPointerToSpecificOperation;
                //Dealllocate the momery on GPU when BaseOperation is destroyed.
                deallocate_memory_on_GPU <<<1,1>>> (_d_conceptPointerToSpecificOperation);
                cudaFree(_d_conceptPointerToSpecificOperation);
                CUDA_ERROR_CHECK(cudaDeviceSynchronize());
                //std::cout << "The destructor of BaseOperation class is called!" <<std::endl;
            }
}
#endif //CUDA_INSTALLED