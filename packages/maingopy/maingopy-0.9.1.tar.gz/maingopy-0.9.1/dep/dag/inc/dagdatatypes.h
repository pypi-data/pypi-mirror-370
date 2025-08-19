#ifndef DAGDATATYPES_H
#define DAGDATATYPES_H

#pragma once
#include <interval/interval.hpp>
//#include "../../inc/intervalLibrary.h"

typedef filib::interval<double, filib::rounding_strategy::native_switched, filib::interval_mode::i_mode_extended> I_cpu;

namespace SVT_DAG {

#ifndef CUDA_INSTALLED
	int inline convert_to_int(double value) { return (int)value; }
	int inline convert_to_int(int value) { return value; }
	double inline convert_to_double(double x) { return x; }
#endif // CUDA_INSTALLED
	int inline convert_to_int(I_cpu interval)
	{
		if (interval.inf() != interval.sup()) throw std::runtime_error("Error: Can not convert filib-interval to int, because interval LB != interval UB. ");
		return (int)interval.inf();
	}


	//********** Up to now, only convert_to_int is used. All other convertion functions are not used! **********
	//double inline convert_to_double(double value) { return value; }
	//double inline convert_to_double(int value) { return (double)value; }
	//double inline convert_to_double(I_cpu interval)
	//{
	//	if (interval.inf() != interval.sup()) throw std::runtime_error("Error: Can not convert filib-interval to double, because interval LB != interval UB. ");
	//	return (double)interval.inf();
	//}

	//I_cpu inline convert_to_filibInterval(int value) { return I_cpu(value); }
	//I_cpu inline convert_to_filibInterval(double value) { return I_cpu(value); }
	//I_cpu inline convert_to_filibInterval(I_cpu interval) { return interval; }

	//template <typename T> int convert_to_dataType(int type, T value) { return convert_to_int(value); }
	//template <typename T> double convert_to_dataType(double type, T value) { return convert_to_double(value); }
	//template <typename T> I_cpu convert_to_dataType(I_cpu type, T value) { return I_cpu(value); }
} // namespace SVT_DAG

#endif // DAGDATATYPES_H