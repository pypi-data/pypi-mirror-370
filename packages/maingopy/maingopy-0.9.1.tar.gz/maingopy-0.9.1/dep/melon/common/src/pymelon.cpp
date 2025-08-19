/**********************************************************************************
 * Copyright (c) 2019 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#include "gp.h"
#include "gpData.h"
#include "ffnet.h"
#include "svm.h"		
#include "modelParser.h"
#include "ffunc.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>

namespace py = pybind11;


// Definition of the actual Python module called pymelon
PYBIND11_MODULE(pymelon, m) {
    m.doc() = "MeLOn - Machine-Learning models for Optimization";

	//----------------------------------------------------------------------------------------
	// MelonModel
	//----------------------------------------------------------------------------------------

	py::class_< melon::MelonModel<mc::FFVar>>(m, "MelonModel")
		.def("load_model", py::overload_cast<std::string, std::string, melon::MODEL_FILE_TYPE>(&melon::MelonModel<mc::FFVar>::load_model))
		.def("load_model", py::overload_cast<std::shared_ptr<const ModelData>>(&melon::MelonModel<mc::FFVar>::load_model));


	// enums

	py::enum_<melon::SCALER_TYPE>(m, "SCALER_TYPE")
		.value("IDENTIY", melon::SCALER_TYPE::IDENTITY)
		.value("MINMAX", melon::SCALER_TYPE::MINMAX)
		.value("STANDARD", melon::SCALER_TYPE::STANDARD)
		.export_values();

	py::enum_<melon::MODEL_FILE_TYPE>(m, "MODEL_FILE_TYPE")
		.value("CSV", melon::MODEL_FILE_TYPE::CSV)
		.value("XML", melon::MODEL_FILE_TYPE::XML)
		.value("JSON", melon::MODEL_FILE_TYPE::JSON)
		.export_values();

	py::enum_<melon::SCALER_PARAMETER>(m, "SCALER_PARAMETER")
		.value("LOWER_BOUNDS", melon::SCALER_PARAMETER::LOWER_BOUNDS)
		.value("UPPER_BOUNDS", melon::SCALER_PARAMETER::UPPER_BOUNDS)
		.value("STD_DEV", melon::SCALER_PARAMETER::STD_DEV)
		.value("MEAN", melon::SCALER_PARAMETER::MEAN)
		.value("SCALED_LOWER_BOUNDS", melon::SCALER_PARAMETER::SCALED_LOWER_BOUNDS)
		.value("SCALED_UPPER_BOUNDS", melon::SCALER_PARAMETER::SCALED_UPPER_BOUNDS)
		.export_values(); 


	// data

	py::class_<ModelData, std::shared_ptr<ModelData>>(m, "ModelData"); 

	py::class_<melon::kernel::KernelData,  std::shared_ptr<melon::kernel::KernelData>>(m, "KernelData")
		.def(py::init<>())
		.def_readwrite("sf2", &melon::kernel::KernelData::sf2)
		.def_readwrite("ell", &melon::kernel::KernelData::ell); 

	py::class_<melon::ScalerData, std::shared_ptr<melon::ScalerData>>(m, "ScalerData")
		.def(py::init<>())
		.def_readwrite("type", &melon::ScalerData::type)
		.def_readwrite("parameters", &melon::ScalerData::parameters); 

	

	//----------------------------------------------------------------------------------------
	// Gaussian process
	//----------------------------------------------------------------------------------------

	// model

	py::class_<melon::GaussianProcess<mc::FFVar>, melon::MelonModel<mc::FFVar> >(m, "GaussianProcess")
		.def(py::init<>())
		.def(py::init <std::string >())
		.def(py::init< std::string, std::string >())
		.def("calculate_prediction_reduced_space", &melon::GaussianProcess<mc::FFVar>::calculate_prediction_reduced_space)
		.def("calculate_variance_reduced_space", &melon::GaussianProcess<mc::FFVar>::calculate_variance_reduced_space)
		.def("calculate_prediction_full_space", &melon::GaussianProcess<mc::FFVar>::calculate_prediction_full_space)
		.def("calculate_variance_full_space", &melon::GaussianProcess<mc::FFVar>::calculate_variance_full_space)
		.def("calculate_prediction_and_variance_full_space", &melon::GaussianProcess<mc::FFVar>::calculate_prediction_and_variance_full_space)
		.def("get_input_dimension", &melon::GaussianProcess<mc::FFVar>::get_input_dimension)
		.def("get_number_of_training_data_points", &melon::GaussianProcess<mc::FFVar>::get_number_of_training_data_points)
		.def("get_minimum_of_training_data_outputs", &melon::GaussianProcess<mc::FFVar>::get_minimum_of_training_data_outputs)
		.def("get_maximum_of_training_data_outputs", &melon::GaussianProcess<mc::FFVar>::get_maximum_of_training_data_outputs)
		.def("get_number_of_full_space_variables_prediction", &melon::GaussianProcess<mc::FFVar>::get_number_of_full_space_variables_prediction)
		.def("get_full_space_variables_prediction", &melon::GaussianProcess<mc::FFVar>::get_full_space_variables_prediction)
		.def("get_number_of_full_space_variables_variance", &melon::GaussianProcess<mc::FFVar>::get_number_of_full_space_variables_variance)
		.def("get_full_space_variables_variance", &melon::GaussianProcess<mc::FFVar>::get_full_space_variables_variance)
		.def("get_number_of_full_space_variables_prediction_and_variance", &melon::GaussianProcess<mc::FFVar>::get_number_of_full_space_variables_prediction_and_variance)
		.def("get_full_space_variables_prediction_and_variance", &melon::GaussianProcess<mc::FFVar>::get_full_space_variables_prediction_and_variance)
		.def("get_observations", &melon::GaussianProcess<mc::FFVar>::get_observations)
		.def("get_normalized_observations", &melon::GaussianProcess<mc::FFVar>::get_normalized_observations); 
	

	// data 

	py::class_<melon::GPData, ModelData, std::shared_ptr<melon::GPData>>(m, "GPData")
		.def(py::init<>())
		.def_readwrite("kernelData", &melon::GPData::kernelData)
		.def_readwrite("nX", &melon::GPData::nX)
		.def_readwrite("DX", &melon::GPData::DX)
		.def_readwrite("DY", &melon::GPData::DY)
		.def_readwrite("matern", &melon::GPData::matern)
		.def_readwrite("inputScalerData", &melon::GPData::inputScalerData)
		.def_readwrite("predictionScalerData", &melon::GPData::predictionScalerData)
		.def_readwrite("X", &melon::GPData::X)
		.def_readwrite("Y", &melon::GPData::Y)
		.def_readwrite("K", &melon::GPData::K)
		.def_readwrite("invK", &melon::GPData::invK)
		.def_readwrite("stdOfOutput", &melon::GPData::stdOfOutput)
		.def_readwrite("meanFunction", &melon::GPData::meanfunction);


	//----------------------------------------------------------------------------------------
	// Feed forward network
	//----------------------------------------------------------------------------------------
	py::class_<melon::FeedForwardNet<mc::FFVar>, melon::MelonModel<mc::FFVar> >(m, "FeedForwardNet")
		.def(py::init<>())
		.def(py::init <std::string, melon::MODEL_FILE_TYPE >())
		.def(py::init< std::string, std::string, melon::MODEL_FILE_TYPE >())
		.def("calculate_prediction_reduced_space", &melon::FeedForwardNet<mc::FFVar>::calculate_prediction_reduced_space)
		.def("calculate_prediction_full_space", &melon::FeedForwardNet<mc::FFVar>::calculate_prediction_full_space)
		.def("set_tanh_formulation", &melon::FeedForwardNet<mc::FFVar>::set_tanh_formulation)
		.def("get_number_of_full_space_variables", &melon::FeedForwardNet<mc::FFVar>::get_number_of_full_space_variables)
		.def("get_full_space_variables", &melon::FeedForwardNet<mc::FFVar>::get_full_space_variables);

	py::enum_<melon::TANH_REFORMULATION>(m, "TANH_REFORMULATION")
		.value("TANH_REF_0", melon::TANH_REFORMULATION::TANH_REF_0)
		.value("TANH_REF1", melon::TANH_REFORMULATION::TANH_REF1)
		.value("TANH_REF2", melon::TANH_REFORMULATION::TANH_REF2)
		.value("TANH_REF3", melon::TANH_REFORMULATION::TANH_REF3)
		.value("TANH_REF4", melon::TANH_REFORMULATION::TANH_REF4)
		.export_values();

	//----------------------------------------------------------------------------------------
	// Support vector machines
	//----------------------------------------------------------------------------------------
	py::class_<melon::SupportVectorMachine<mc::FFVar>, melon::MelonModel<mc::FFVar> >(m, "SupportVectorMachine")
		.def("calculate_prediction_reduced_space", &melon::SupportVectorMachine<mc::FFVar>::calculate_prediction_reduced_space)
		.def("calculate_prediction_full_space", &melon::SupportVectorMachine<mc::FFVar>::calculate_prediction_full_space)
		.def("get_number_of_full_space_variables", &melon::SupportVectorMachine<mc::FFVar>::get_number_of_full_space_variables)
		.def("get_fullspace_variables", &melon::SupportVectorMachine<mc::FFVar>::get_fullspace_variables);

	py::class_<melon::SupportVectorRegression<mc::FFVar>, melon::SupportVectorMachine<mc::FFVar> >(m, "SupportVectorRegression")
		.def(py::init<>())
		.def(py::init <std::string >())
		.def(py::init< std::string, std::string >());

	py::class_<melon::SupportVectorMachineOneClass<mc::FFVar>, melon::SupportVectorMachine<mc::FFVar> >(m, "SupportVectorMachineOneClass")
		.def(py::init<>())
		.def(py::init <std::string >())
		.def(py::init< std::string, std::string >());
}