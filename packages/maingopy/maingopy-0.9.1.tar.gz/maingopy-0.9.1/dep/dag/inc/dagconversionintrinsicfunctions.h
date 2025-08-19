#include "dagconversion.h"
#include <vector>

namespace SVT_DAG {
	namespace DagConversionHelpFunctions {
		ModelVar inline cost_function(std::vector<ModelVar>* dagVars, std::vector<int> &operandIndices)
		{
			ModelVar x = (*dagVars)[operandIndices[0]];	// operandIndice[1] is not necessary for function evaluation (see cost_function implemenation in library_of_functions.hpp)
			ModelVar p1 = (*dagVars)[operandIndices[2]];
			ModelVar p2 = (*dagVars)[operandIndices[3]];
			ModelVar p3 = (*dagVars)[operandIndices[4]];

			return pow(10., p1 + p2 * log(x) / std::log(10) + p3 * sqr(log(x) / std::log(10)));
		}
		ModelVar inline saturation_temperature(std::vector<ModelVar>* dagVars, std::vector<int>& operandIndices)
		{
			ModelVar x = (*dagVars)[operandIndices[0]];	// operandIndice[1] is not necessary for function evaluation (see cost_function implemenation in library_of_functions.hpp)
			ModelVar p1 = (*dagVars)[operandIndices[2]];
			ModelVar p2 = (*dagVars)[operandIndices[3]];
			ModelVar p3 = (*dagVars)[operandIndices[4]];

			return p2 / (p1 - log(x) / std::log(10.)) - p3;
		}
		ModelVar inline lmtd(std::vector<ModelVar>* dagVars, std::vector<int>& operandIndices)
		{
			ModelVar x = (*dagVars)[operandIndices[0]];
			ModelVar y = (*dagVars)[operandIndices[1]];

			return (x - y) / (log(x) - log(y));
		}
		ModelVar inline rlmtd(std::vector<ModelVar>* dagVars, std::vector<int>& operandIndices)
		{
			ModelVar x = (*dagVars)[operandIndices[0]];
			ModelVar y = (*dagVars)[operandIndices[1]];

			return (log(x) - log(y)) / (x - y);
		}

	} // namespace DagConversionHelpFunctions
} // namespace SVT_DAG