
#pragma once

// include DAG files
#include "dag.h"
#include "modelvar.h"
#include "modeloperations.h"
#include "dagprinting.h"
#include "dagevaluation.h"
#include "dagevaluation.cuh"

#include <chrono>
#include <vector>
#include <cmath>

#include <cuda_runtime.h>


namespace performanceTest
{
	template <typename T> T goldstein_price_X_nD(T* X, int maxLoop, int dim);
	template <typename T> __device__ T goldstein_price_X_nD_gpu(T* X, int maxLoop, int dim);
	void DAG_golstein_price_nD(Dag& dag, int maxLoop, int dim);
}

#ifndef FUNCTION_COMPLEXITY
#define FUNCTION_COMPLEXITY 10
#endif // !FUNCTION_COMPLEXITY


double rand_double(double LB, double UB) {
	int r = rand();
	return LB + (UB - LB) * ((rand() % 10000) * 1.) / 10000;
}

I_cpu rand_filibInterval(double LB, double UB)
{
	double low = rand_double(LB, UB);
	double up = rand_double(low, UB);
	return I_cpu(low, up);
}

inline double my_pow(double x, int y) { return std::pow(x, y); }
inline I_cpu my_pow(I_cpu x, int y) { return filibMath::pow(x, y); }
inline ModelVar my_pow(ModelVar x, int y) { return pow(x, y); }
__device__ inline I_gpu my_pow(I_gpu x, int y) { return pow(x, y); }

template <typename T>
__global__ void evaluate_DAG_kernel(GpuDag dag,T* independentVarValues, T* dagVarValues, T* resultValues, int id)
{
	evaluate(dag, independentVarValues, dagVarValues);
	resultValues[id] = dagVarValues[dag.numVars - 1];
}

template <typename T>
__global__ void evaluate_DAG_kernel(Dag* dag, T* independentVarValues, T* dagVarValues, T* resultValues, int id)
{
	GpuDag gpudag(dag);
	evaluate(gpudag, independentVarValues, dagVarValues);
	resultValues[id] = dagVarValues[dag->numVars - 1];
}

__global__ void evaluate_template_kernel(I_gpu* inputValues, I_gpu* resultValue, int id)
{
	resultValue[id] = performanceTest::goldstein_price_X_nD_gpu(inputValues, FUNCTION_COMPLEXITY, 2);
}

void test_DAG() {
	Dag dag;
	ModelVar x, y, a;
	dag.add_independent_variable(x);
	dag.add_independent_variable(y);
	dag.add_independent_variable(a);
	ModelVar z = 2.5 + x;
	ModelVar w(dag);
	w = 4;
	w = pow(w, 2);
	z = z - w;

	print(dag);

	dag.synchronize_var_vectors_and_var_arrays();

	dag.copy_to_gpu();

	/*I_cpu X(-1, 1), Y(0, 2), A(-2, 0);

	std::vector<I_cpu> values{ X, Y, A };
	std::vector<I_cpu> results(evaluate(dag, values));

	I_cpu arrValues[3] = { X,Y,A };
	I_cpu* arrResults = evaluate(dag, arrValues);*/

	/*double X = 5, Y = 3, A = 2;

	std::vector<double> values{ X, Y, A };
	std::vector<double> results(evaluate(dag, values));

	double arrValues[3] = { X, Y, A };
	double* arrResult = evaluate(dag, arrValues);*/

	I_gpu X(-1, 1), Y(0, 2), A(-2, 0);

	I_gpu *arrValues, *arrResults, * d_arrValues, *d_arrResults;
	
	cudaMalloc(&d_arrValues, 3 * sizeof(I_gpu));
	cudaMalloc(&d_arrResults, 11 * sizeof(I_gpu));
	
	arrValues = (I_gpu*)malloc(3 * sizeof(I_gpu));
	arrResults = (I_gpu*)malloc(11 * sizeof(I_gpu));

	arrValues[0] = X;
	arrValues[1] = Y;
	arrValues[2] = A;

	CUDA_ERROR_CHECK(cudaMemcpy(d_arrValues, arrValues, 3 * sizeof(I_gpu), cudaMemcpyHostToDevice));

	//evaluate_DAG_kernel << <1, 1 >> > (dag, d_arrValues, d_arrResults, d_arrResults, dag.numVars - 1);
	CUDA_ERROR_CHECK(cudaDeviceSynchronize());

	CUDA_ERROR_CHECK(cudaMemcpy(arrResults, d_arrResults, 11 * sizeof(I_gpu), cudaMemcpyDeviceToHost));

	I_cpu sum1(0.);
	I_cpu sum2(0.);
	for (std::size_t i = 0; i < 9; ++i)
	{
		//std::cout << "DagVar #" << i << ": " << arrResults[i] << std::endl;
		std::cout << "DagVar #" << i << ": [" << arrResults[i].lower() << ", " << arrResults[i].upper() << "]" << std::endl;
		/*std::cout << "DagVar #" << i << ": " << results[i] << " " << arrResult[i] << std::endl;
		sum1 = sum1 + results[i];
		sum2 = sum2 + arrResult[i];*/
	}




	//const std::vector<double> input{ 1, 1 };
	//const std::vector<double> result = evaluate(goldstein_dag, input);
}

template <typename T>
T perform_operation(int opID, T x, T y)
{
	T z;
	switch (opID)
	{
	case 0:
		z = x + y; break;

	case 1:
		z = x - y; break;

	case 2:
		z = x * y; break;

	case 3:
		z = x / y; break;

	case 4: 
		z = exp(x); break;

	case 5:
		z = my_pow(x, 6); break;
	}
	return z;
}

void print_operation(int opID)
{
	printf(" ");
	switch (opID)
	{
	case 0:
		printf("+"); break;

	case 1:
		printf("-"); break;

	case 2:
		printf("*"); break;

	case 3:
		printf("/"); break;

	case 4:
		printf("exp"); break;

	case 5:
		printf("pow"); break;

	}
	printf(" ");
}

void test_DAG_operations()
{
	int imax = 20;
	int LB = -100;
	int UB = 100;
	int nOperations = 6;
	for (int op = 0; op < nOperations; op++)
	{
		for (int i = 0; i < imax; i++)
		{
			// Test operation with two independent variables
			Dag dag1, dag2;
			ModelVar x, y,z(dag2);
			dag1.add_independent_variable(x);			
			dag1.add_independent_variable(y);
			perform_operation(op, x, y);

			//I_cpu X = rand_filibInterval(LB, UB);
			I_cpu X(LB,UB);
			I_cpu Y = rand_filibInterval(LB, UB);

			std::vector<I_cpu> vec1{ X,Y };
			I_cpu arr1[2] = { X,Y };

			std::vector<I_cpu> res_vec1 = evaluate(dag1, vec1);			
			I_cpu* res_arr1 = evaluate(dag1, arr1);
			I_cpu res1 = perform_operation(op, X, Y);

			int last = res_vec1.size()-1;
			if (res_vec1[last] != res1 || res1 != res_arr1[last]) {
				I_cpu res11 = res_vec1[last];
				I_cpu res12 = res_arr1[last];
				double res13 = pow(X.inf(), 6);
				double res14 = std::pow(X.inf(), 6);
				std::cout << "Error: " << X;
				print_operation(op);
				std::cout << Y << " = " << res1 << " | vec " << res_vec1[last] << " | arr " << res_arr1[last] << "\n";
			}

			// Test operation with one constant variable
			dag2.add_independent_variable(x);
			double Z = rand_double(LB, UB);
			z = Z;
			perform_operation(op,x, z);

			std::vector<I_cpu> vec2{ X };
			I_cpu arr2[1] = { X };

			std::vector<I_cpu> res_vec2 = evaluate(dag2, vec2);
			I_cpu* res_arr2 = evaluate(dag2, arr2);
			I_cpu res2 = perform_operation(op, X, I_cpu(Z));

			if (res_vec2[last] != res2 || res2 != res_arr2[last]) {
				std::cout << "Error: " << X;
				print_operation(op);
				std::cout << Y << " = " << res2 << " | vec " << res_vec2[last] << " | arr " << res_arr2[last] << "\n";
			}
		}
	}	
}

void performance_DAG_double() {
	// **************************** Testing efficiency of DAG - double **************************** 	
	printf("\nTesting efficiency of goldstein-price DAG with double-values\n");
	int nElm = 1e3;
	int LB = -2;
	int UB = 2;
	steady_clock::time_point _t_start1, _t_end1, _t_start2, _t_end2, _t_start3, _t_end3;


	// Initialize DAG
	Dag goldstein_dag;
	performanceTest::DAG_golstein_price_nD(goldstein_dag, FUNCTION_COMPLEXITY, 2);

	// Initialize random inputs	
	printf(" Started initializing inputs for DAG using vectors\n");
	std::vector<std::vector<double>> dagInputs;
	std::vector<double> dagResults{};
	for (int i = 0; i < nElm; i++) {
		std::vector<double> tempVec{rand_double(LB, UB), rand_double(LB, UB)};
		//std::vector<double> tempVec{ -1, 0 };
		dagInputs.push_back(tempVec);
	}
	printf(" Started initializing inputs for template\n");
	double* regularInputs = new double[nElm * 2];
	std::vector<double> templateResults{};
	for (int i = 0; i < nElm; i++) {
		regularInputs[2 * i] = dagInputs[i][0];
		regularInputs[2 * i + 1] = dagInputs[i][1];
	}

	// Evaluate DAG with vectors
	printf(" Started evaluation of DAG with vectors\n");
	double sum1 = 0;
	double sum = 0;
	_t_start1 = steady_clock::now();
	for (int i = 0; i < nElm; i++) {
		sum1 += evaluate(goldstein_dag, dagInputs[i]).back();
	}
	_t_end1 = steady_clock::now();	

	// Evaluate template function
	printf(" Started evaluation of template\n");
	double sum2 = 0;
	_t_start2 = steady_clock::now();
	for (int i = 0; i < nElm; i++) {
		double* funcInput = &regularInputs[2 * i];
		sum2 += performanceTest::goldstein_price_X_nD(funcInput, FUNCTION_COMPLEXITY, 2);
		//templateResults.push_back(obj_func::goldstein_price_X_nD(funcInput, 10, 2));
	}
	_t_end2 = steady_clock::now();

	// Evaluate DAG with arrays
	printf(" Started evaluation of DAG with arrays\n");
	goldstein_dag.synchronize_var_vectors_and_var_arrays();
	_t_start3 = steady_clock::now();
	for (int i = 0; i < nElm; i++) {
		double* funcInput = &regularInputs[2 * i];
		evaluate(goldstein_dag, funcInput);
	}
	_t_end3 = steady_clock::now();
	printf(" Done\n");

	//if (templateResults.back() != dagResults.back()) printf("\n Different last result!\n");
	if (sum1 != sum2) {
		printf("\n Different result sums! <------------------------ double\n");
	}

	// Calculate time per evaluation
	double _t_total1 = (duration_cast<nanoseconds> (_t_end1 - _t_start1).count() * 1.) / 1000000;
	double _t_per_evaluation1 = _t_total1 / nElm * 1000000;

	double _t_total2 = (duration_cast<nanoseconds> (_t_end2 - _t_start2).count() * 1.) / 1000000;
	double _t_per_evaluation2 = _t_total2 / nElm * 1000000;

	double _t_total3 = (duration_cast<nanoseconds> (_t_end3 - _t_start3).count() * 1.) / 1000000;
	double _t_per_evaluation3 = _t_total3 / nElm * 1000000;

	printf("\n*** DAG with vectors ***\n");
	printf("Total time:          %8.3f ms\n", _t_total1);
	printf("Time per evaluation: %8.3f ns\n", _t_per_evaluation1);

	printf("\n*** DAG with arrays ***\n");
	printf("Total time:          %8.3f ms\n", _t_total3);
	printf("Time per evaluation: %8.3f ns\n", _t_per_evaluation3);

	printf("\n*** Template ***\n");
	printf("Total time:          %8.3f ms\n", _t_total2);
	printf("Time per evaluation: %8.3f ns\n", _t_per_evaluation2);


	delete[] regularInputs;
}



void performance_DAG_interval() {
	// **************************** Testing efficiency of DAG - filib ****************************
	printf("\nTesting efficiency of goldstein-price DAG with intervals\n");
	int nElm = 1e3;
	double LB = -2;
	double UB = 2;
	double mid = (UB - LB) / 2;
	steady_clock::time_point _t_start1, _t_end1, _t_start2, _t_end2, _t_start3, _t_end3, _t_start4, _t_end4, _t_start5, _t_end5;


	// Initialize DAG
	Dag goldstein_dag;
	performanceTest::DAG_golstein_price_nD(goldstein_dag, FUNCTION_COMPLEXITY, 2);

	// Initialize random inputs	
	printf(" Started initializing inputs for DAG\n");
	std::vector<std::vector<I_cpu>> dagInputs;
	std::vector<I_cpu> dagResults{};
	for (int i = 0; i < nElm; i++) {
		std::vector<I_cpu> tempVec{rand_filibInterval(LB,UB), rand_filibInterval(LB,UB) };
		//std::vector<I_cpu> tempVec{ I_cpu(-1.,0.), I_cpu(0.,1.) };
		dagInputs.push_back(tempVec);
	}
	printf(" Started initializing inputs for template\n");
	I_cpu* regularInputs = new I_cpu[nElm * 2];
	std::vector<I_cpu> templateResults{};
	for (int i = 0; i < nElm; i++) {
		regularInputs[2 * i] = dagInputs[i][0];
		regularInputs[2 * i + 1] = dagInputs[i][1];
	}

	// Evaluate DAG
	printf(" Started evaluation of DAG with vectors\n");
	I_cpu sum1 = 0;
	I_cpu sum = 0;
	_t_start1 = steady_clock::now();
	for (int i = 0; i < nElm; i++) {
		//sum1 = sum1 + evaluate(goldstein_dag, dagInputs[i]).back();
		
		dagResults.push_back(evaluate(goldstein_dag, dagInputs[i]).back());

		/*I_cpu* funcInput = &regularInputs[2 * i];
		dagResults.push_back(performanceTest::goldstein_price_X_nD(funcInput, 10, 2));
		sum = sum + dagResults.back();

		int last = dagResults.size() - 1;
		double LB1 = dagResults[last - 1].inf();
		double UB1 = dagResults[last - 1].sup();
		double LB2 = dagResults[last].inf();
		double UB2 = dagResults[last].sup();
		if (LB1 != LB2 || UB1 != UB2) {	
			std::cout << "Error in iteration " << i << " :\n X = " << dagInputs[i][0] << " | Y = " << dagInputs[i][1] <<"\n";			
			printf("     DagResult = [%20.12f, %20.12f]\n", LB1, UB1);
			printf("TemplateResult = [%20.12f, %20.12f]\n\n", LB2, UB2);
		}
		else {
			std::cout << "-> Correct in iteration " << i << " :\n X = " << dagInputs[i][0] << " | Y = " << dagInputs[i][1] << "\n\n";
		}*/
	}
	_t_end1 = steady_clock::now();

	// Evaluate template function
	printf(" Started evaluation of template\n");
	I_cpu sum2 = 0;
	_t_start2 = steady_clock::now();
	for (int i = 0; i < nElm; i++) {
		I_cpu* funcInput = &regularInputs[2 * i];
		sum2 = sum2 + performanceTest::goldstein_price_X_nD(funcInput, FUNCTION_COMPLEXITY, 2);
		//templateResults.push_back(obj_func::goldstein_price_X_nD(funcInput, 10, 2));
	}
	_t_end2 = steady_clock::now();

	// Evaluate DAG with arrays
	printf(" Started evaluation of DAG with arrays\n");
	goldstein_dag.synchronize_var_vectors_and_var_arrays();
	_t_start3 = steady_clock::now();
	for (int i = 0; i < nElm; i++) {
		I_cpu* funcInput = &regularInputs[2 * i];
		evaluate(goldstein_dag, funcInput);
	}
	_t_end3 = steady_clock::now();
	printf(" Done\n");

	// Evaluate DAG on GPU
	printf(" Prepare evaluation of DAG on GPU\n");
	goldstein_dag.copy_to_gpu();
	I_gpu* inputsGPU, *d_dagVarValues, *resultsGPU, *h_resultsGPU, *h_inputsGPU;
	Dag* d_dag;
	
	size_t bytesInput = 2 * nElm * sizeof(I_gpu);
	size_t bytesResult = nElm * sizeof(I_gpu);
	size_t bytesDagVarValues = goldstein_dag.numVars * sizeof(I_gpu);
	size_t bytesDag = sizeof(Dag);
	
	cudaMalloc(&inputsGPU, bytesInput);
	h_inputsGPU = (I_gpu*)malloc(bytesInput);
	cudaMalloc(&resultsGPU, bytesResult);
	cudaMalloc(&d_dagVarValues, bytesDagVarValues);
	cudaMalloc(&d_dag, bytesDag);

	h_resultsGPU = new I_gpu[nElm];

	for (int i = 0; i < nElm; i++) 
		h_inputsGPU[i] = I_gpu(regularInputs[i].inf(), regularInputs->sup());

	cudaMemcpy(inputsGPU, h_inputsGPU, bytesInput, cudaMemcpyHostToDevice);
	cudaMemcpy(d_dag, &goldstein_dag, bytesDag, cudaMemcpyHostToDevice);

	// Prepare unified memory
	I_gpu* inputsUnifiedMemory, *dagVarValuesUnifiedMemory, *resultsUnifiedMemory;

	cudaMallocManaged(&inputsUnifiedMemory, bytesInput);
	cudaMallocManaged(&dagVarValuesUnifiedMemory, bytesDagVarValues);
	cudaMallocManaged(&resultsUnifiedMemory, bytesResult);

	for (int i = 0; i < nElm; i++)
		inputsUnifiedMemory[i] = h_inputsGPU[i];
	
	GpuDag gpudag(goldstein_dag);

	printf(" Start evaluation of DAG on GPU\n");
	_t_start4 = steady_clock::now();
	for (int i = 0; i < nElm; i++) {
		I_gpu* funcInput = &inputsGPU[2 * i];
		//I_gpu* funcInput = &inputsUnifiedMemory[2 * i];
		//evaluate_DAG_kernel << <1, 1 >> > (d_dag, funcInput, d_dagVarValues, resultsGPU, i);
		evaluate_DAG_kernel << <1, 1 >> > (gpudag, funcInput, d_dagVarValues, resultsGPU, i);
		//evaluate_DAG_kernel << <1, 1 >> > (goldstein_dag, evalInfo, resultsGPU, i);
		CUDA_ERROR_CHECK(cudaDeviceSynchronize());
	}
	_t_end4 = steady_clock::now();

	cudaMemcpy(h_resultsGPU, resultsGPU, bytesResult, cudaMemcpyDeviceToHost);

	printf(" Start evaluation of template on GPU\n");
	_t_start5 = steady_clock::now();
	for (int i = 0; i < nElm; i++) {
		I_gpu* funcInput = &inputsGPU[2 * i];
		evaluate_template_kernel << <1, 1 >> > (funcInput, resultsGPU, i);
		cudaDeviceSynchronize();
	}
	_t_end5 = steady_clock::now();

	cudaMemcpy(h_resultsGPU, resultsGPU, bytesResult, cudaMemcpyDeviceToHost);

	// Calculate time per evaluation
	double _t_total1 = (duration_cast<nanoseconds> (_t_end1 - _t_start1).count() * 1.) / 1000000;
	double _t_per_evaluation1 = _t_total1 / nElm * 1000000;

	double _t_total2 = (duration_cast<nanoseconds> (_t_end2 - _t_start2).count() * 1.) / 1000000;
	double _t_per_evaluation2 = _t_total2 / nElm * 1000000;

	double _t_total3 = (duration_cast<nanoseconds> (_t_end3 - _t_start3).count() * 1.) / 1000000;
	double _t_per_evaluation3 = _t_total3 / nElm * 1000000;

	double _t_total4 = (duration_cast<nanoseconds> (_t_end4 - _t_start4).count() * 1.) / 1000000;
	double _t_per_evaluation4 = _t_total4 / nElm * 1000000;

	double _t_total5 = (duration_cast<nanoseconds> (_t_end5 - _t_start5).count() * 1.) / 1000000;
	double _t_per_evaluation5 = _t_total5 / nElm * 1000000;

	printf("\n*** DAG with vectors ***\n");
	printf("Total time:          %8.3f ms\n", _t_total1);
	printf("Time per evaluation: %8.3f ns\n", _t_per_evaluation1);

	printf("\n*** DAG with arrays ***\n");
	printf("Total time:          %8.3f ms\n", _t_total3);
	printf("Time per evaluation: %8.3f ns\n", _t_per_evaluation3);

	printf("\n*** Template ***\n");
	printf("Total time:          %8.3f ms\n", _t_total2);
	printf("Time per evaluation: %8.3f ns\n", _t_per_evaluation2);

	printf("\n*** DAG on GPU ***\n");
	printf("Total time:          %8.3f ms\n", _t_total4);
	printf("Time per evaluation: %8.3f ns\n", _t_per_evaluation4);

	printf("\n*** Template on GPU ***\n");
	printf("Total time:          %8.3f ms\n", _t_total5);
	printf("Time per evaluation: %8.3f ns\n", _t_per_evaluation5);

	cudaFree(inputsGPU);
	cudaFree(resultsGPU);

	delete[] regularInputs;
}

// ************************************ n-dimensional Goldstein-Price function **********************************************
namespace performanceTest
{
	template <typename T>
	T goldstein_price_X_nD(T* X, int maxLoop, int dim) {
		T res(0.);
		for (int iter_dim = 0; iter_dim < dim; iter_dim = iter_dim + 2) {
			T temp_res(0.);
			for (int i = 0; i < maxLoop; i++) {
				T x = X[iter_dim], y = X[iter_dim + 1];
				// 1 + (x + y + 1)^2 * (19 - 14x + 3x^2 - 14y + 6xy + 3y^2)
				T temp1 = my_pow(x + y + T(1.), 2); // (x + y + 1)^2
				T temp2 = T(19.) - 14. * x + 3. * x * x - 14. * y + 6. * x * y + 3. * y * y; // 19 - 14x + 3x^2 - 14y + 6xy + 3y^2
				T first = T(1.) + temp1 * temp2;

				// 30 + (2x - 3y)^2 * (18 - 32x + 12x^2 + 48y - 36xy + 27y^2)
				temp1 = my_pow(2. * x - 3. * y, 2); // (2x - 3y)^2
				temp2 = T(18.) - 32. * x + 12. * x * x + 48. * y - 36. * x * y + 27. * y * y; // 18 - 32x + 12x^2 + 48y - 36xy + 27y^2
				T second = T(30.) + temp1 * temp2;

				temp_res = temp_res + first * second;
			}
			res = res + temp_res;
		}
		return res;
	}

	template <typename T>
	__device__
	T goldstein_price_X_nD_gpu(T* X, int maxLoop, int dim) {
		T res(0.);
		for (int iter_dim = 0; iter_dim < dim; iter_dim = iter_dim + 2) {
			T temp_res(0.);
			for (int i = 0; i < maxLoop; i++) {
				T x = X[iter_dim], y = X[iter_dim + 1];
				// 1 + (x + y + 1)^2 * (19 - 14x + 3x^2 - 14y + 6xy + 3y^2)
				T temp1 = my_pow(x + y + T(1.), 2); // (x + y + 1)^2
				T temp2 = T(19.) - 14. * x + 3. * x * x - 14. * y + 6. * x * y + 3. * y * y; // 19 - 14x + 3x^2 - 14y + 6xy + 3y^2
				T first = T(1.) + temp1 * temp2;

				// 30 + (2x - 3y)^2 * (18 - 32x + 12x^2 + 48y - 36xy + 27y^2)
				temp1 = my_pow(2. * x - 3. * y, 2); // (2x - 3y)^2
				temp2 = T(18.) - 32. * x + 12. * x * x + 48. * y - 36. * x * y + 27. * y * y; // 18 - 32x + 12x^2 + 48y - 36xy + 27y^2
				T second = T(30.) + temp1 * temp2;

				temp_res = temp_res + first * second;
			}
			res = res + temp_res;
		}
		return res;
	}

	void DAG_golstein_price_nD(Dag& dag, int maxLoop, int dim) {
		std::vector<ModelVar> X;
		X.resize(dim);

		for (int i = 0; i < dim; i++)
			dag.add_independent_variable(X[i]);

		ModelVar res(dag);
		res = 0;

		for (int iter_dim = 0; iter_dim < dim; iter_dim = iter_dim + 2) {
			ModelVar temp_res(dag);
			temp_res = 0.;
			for (int i = 0; i < maxLoop; i++) {
				ModelVar x = X[iter_dim], y = X[iter_dim + 1];
				// 1 + (x + y + 1)^2 * (19 - 14x + 3x^2 - 14y + 6xy + 3y^2)
				ModelVar temp1 = my_pow(x + y + 1., 2); // (x + y + 1)^2
				ModelVar temp2 = 19. - 14. * x + 3. * x * x - 14. * y + 6. * x * y + 3. * y * y; // 19 - 14x + 3x^2 - 14y + 6xy + 3y^2
				ModelVar first = 1. + temp1 * temp2;

				// 30 + (2x - 3y)^2 * (18 - 32x + 12x^2 + 48y - 36xy + 27y^2)
				temp1 = my_pow(2. * x - 3. * y, 2); // (2x - 3y)^2
				temp2 = 18. - 32. * x + 12. * x * x + 48. * y - 36. * x * y + 27. * y * y; // 18 - 32x + 12x^2 + 48y - 36xy + 27y^2
				ModelVar second = 30. + temp1 * temp2;

				temp_res = temp_res + first * second;
			}
			res = res + temp_res;
		}
	}
}