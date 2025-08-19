#ifdef CUDA_INSTALLED
#include "dagdatatypes.cuh"
#include "baseoperation.cuh"
#include "baseoperationGPUdealloc.cuh"

namespace SVT_DAG {
	
	BaseOperation opAddition{ Addition{} };
	BaseOperation opSubtraction{ Subtraction{} };
	BaseOperation opMultiplication{ Multiplication{} };
	BaseOperation opDivision{ Division{} };
	BaseOperation opExponential{ Exponential{} };
	BaseOperation opPower{ PowerOperation{} };
	BaseOperation opSquareRoot{ SquareRootOperation{} };
	BaseOperation opSquare{ SquareOperation{} };
	BaseOperation opNegative{ Negative{} };
	BaseOperation opTangensHyperbolicus{ TangensHyperbolicus{} };
	BaseOperation opLogarithmus{ Logarithmus{} };
	BaseOperation opAbsoluteValue{ AbsoluteValue{} };
	BaseOperation opCosinus{ Cosinus{} };
	BaseOperation opSinus{ Sinus{} };
	BaseOperation opInverse{ Inverse{} };
	BaseOperation opMaximum{ Maximum{} };

} // namespace SVT_DAG

#endif // CUDA_INSTALLED