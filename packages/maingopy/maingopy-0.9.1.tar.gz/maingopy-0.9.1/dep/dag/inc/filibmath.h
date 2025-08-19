#ifndef FILIBMATH_H
#define FILIBMATH_H

#include "dagdatatypes.h"
#include <cmath>

namespace SVT_DAG {

	namespace filibMath
	{
		I_cpu inline pow(I_cpu x, int exp) {
			double LB = x.inf(), UB = x.sup();
			if (exp == 0) {
				return I_cpu(1., 1.);
			}
			else if (exp % 2 == 0) { // Even exponents
				if (LB < 0 && UB < 0) return I_cpu(std::pow(UB, exp), std::pow(LB, exp));
				else if (LB > 0 && UB > 0) return I_cpu(std::pow(LB, exp), std::pow(UB, exp));
				else return I_cpu(0., std::pow(std::max(-LB, UB), exp));
			}
			else {// Odd exponents
				return I_cpu(std::pow(LB, exp), std::pow(UB, exp));
			}
		}
	} // namespace filibMath

} // namespace SVT_DAG
#endif // FILIBMATH_H