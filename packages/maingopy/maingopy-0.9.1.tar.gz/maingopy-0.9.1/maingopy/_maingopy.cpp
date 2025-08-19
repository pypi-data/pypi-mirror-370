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

#include "MAiNGO.h"
#include "MAiNGOmodel.h"
#include "MAiNGOmodelEpsCon.h"
#include "MAiNGOException.h"
#include "functionWrapper.h"
#include "instrumentor.h"
#include "mpiUtilities.h"

#include "babOptVar.h"

#include "ffunc.hpp"

#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

namespace py = pybind11;

// make pre-processor variable HAVE_MAiNGO_MPI available for Python API
bool
haveMPI()
{

#ifdef HAVE_MAiNGO_MPI
    return true;
#else
    return false;
#endif
}

struct BufferPair {
    std::streambuf* coutBuf;
    std::streambuf* cerrBuf;
};


BufferPair
muteWorkerOutput()
{
    BufferPair originalBuffer = {std::cout.rdbuf(), std::cerr.rdbuf()};
#ifdef HAVE_MAiNGO_MPI

    int _rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &_rank);

    // Mute cout for workers to avoid multiple outputs
    std::ostringstream mutestream;

    MAiNGO_IF_BAB_WORKER
        std::cout.rdbuf(mutestream.rdbuf());
        std::cerr.rdbuf(mutestream.rdbuf());
    MAiNGO_END_IF
#endif
    return originalBuffer;
}


void
unmuteWorkerOutput(BufferPair originalBuffer)
{
    std::cout.rdbuf(originalBuffer.coutBuf);
    std::cerr.rdbuf(originalBuffer.cerrBuf);
    return;
}

// First, create a dummy class that is needed later to expose the MAiNGOmodel base class
// so that it can be used and inherited from in Python
class PyMAiNGOmodel: public maingo::MAiNGOmodel {
  public:
    using maingo::MAiNGOmodel::MAiNGOmodel;

    std::vector<maingo::OptimizationVariable> get_variables() override
    {
        PYBIND11_OVERLOAD_PURE(
            std::vector<maingo::OptimizationVariable>, /* Return type */
            maingo::MAiNGOmodel,                       /* Parent class */
            get_variables,                             /* Name of function in C++ (must match Python name) */
                                                       /* Argument(s) - here none */
        );
    }

    maingo::EvaluationContainer evaluate(const std::vector<mc::FFVar>& vars) override
    {
        PYBIND11_OVERLOAD_PURE(
            maingo::EvaluationContainer, /* Return type */
            maingo::MAiNGOmodel,         /* Parent class */
            evaluate,                    /* Name of function in C++ (must match Python name) */
            vars                         /* Argument(s) */
        );
    }

    std::vector<double> get_initial_point() override
    {
        PYBIND11_OVERLOAD(
            std::vector<double>, /* Return type */
            maingo::MAiNGOmodel, /* Parent class */
            get_initial_point,   /* Name of function in C++ (must match Python name) */
                                 /* Argument(s) - here none */
        );
    }
};


class PyTwoStageModel: public maingo::TwoStageModel {
  public:
    using maingo::TwoStageModel::TwoStageModel;  /* Inherit the constructors */
    using NamedVar = std::pair<Var, std::string>;

    std::vector<maingo::OptimizationVariable> get_variables() override
    {
        PYBIND11_OVERLOAD_PURE(
            std::vector<maingo::OptimizationVariable>, /* Return type */
            maingo::TwoStageModel,                     /* Parent class */
            get_variables,                             /* Name of function in C++ (must match Python name) */
                                                       /* Argument(s) - here none */
        );
    }


    std::vector<double> get_initial_point() override
    {
        PYBIND11_OVERRIDE(
            std::vector<double>,   /* Return type */
            maingo::TwoStageModel, /* Parent class */
            get_initial_point,     /* Name of function in C++ (must match Python name) */
                                   /* Argument(s) - here none */
        );
    }

	mc::FFVar f1_func(const std::vector<mc::FFVar> & x) override {
		PYBIND11_OVERRIDE(
			mc::FFVar,             /* Return type */
			maingo::TwoStageModel, /* Parent class */
			f1_func,               /* Name of function in C++ (must match Python name) */
			x                      /* Argument(s) */
		);
	}

	mc::FFVar f2_func(const std::vector<mc::FFVar> & x,
		const std::vector<mc::FFVar> & ys,
		const std::vector<double> &ps) override {
		PYBIND11_OVERRIDE(
			mc::FFVar,             /* Return type */
			maingo::TwoStageModel, /* Parent class */
			f2_func,               /* Name of function in C++ (must match Python name) */
			x, ys, ps              /* Argument(s) */
		);
	}

    std::vector<std::vector<NamedVar>> g1_func(const std::vector<mc::FFVar> & x) override {
        PYBIND11_OVERRIDE(
            std::vector<std::vector<NamedVar>>, /* Return type */
            maingo::TwoStageModel,               /* Parent class */
            g1_func,                             /* Name of function in C++ (must match Python name) */
            x                                    /* Argument(s) */
        );
    }

    std::vector<std::vector<NamedVar>> g2_func(const std::vector<mc::FFVar> & x,
                                                const std::vector<mc::FFVar> & ys,
                                                const std::vector<double> &ps) override {
        PYBIND11_OVERRIDE(
            std::vector<std::vector<NamedVar>>, /* Return type */
            maingo::TwoStageModel,               /* Parent class */
            g2_func,                             /* Name of function in C++ (must match Python name) */
            x, ys, ps                            /* Argument(s) */
        );
    }

	void _update(const std::vector<mc::FFVar> & vars) override {
		PYBIND11_OVERRIDE(
			void,				   /* Return type */
			maingo::TwoStageModel, /* Parent class */
			_update,               /* Name of function in C++ (must match Python name) */
			vars                   /* Argument(s) */
		);
	}
};

// Definition of the actual Python module called _maingopy
PYBIND11_MODULE(_maingopy, m)
{
    PROFILE_SESSION("MAiNGOpy")

    m.doc() = "An extension module containing MAiNGO and its Python bindings.";

    // First create bindings for the actual MAiNGO object as well as the enums for the return code of the solve method
    py::class_<maingo::MAiNGO>(m, "MAiNGO")
        .def(py::init<std::shared_ptr<maingo::MAiNGOmodel>>())
        .def("solve", &maingo::MAiNGO::solve)
        .def("set_model", &maingo::MAiNGO::set_model)
        .def("set_option", py::overload_cast<const std::string&, const double>(&maingo::MAiNGO::set_option))
        .def("set_option", py::overload_cast<const std::string&, const bool>(&maingo::MAiNGO::set_option))
        .def("set_option", py::overload_cast<const std::string&, const int>(&maingo::MAiNGO::set_option))
        .def("read_settings", &maingo::MAiNGO::read_settings, py::arg("settingsFileName") = "MAiNGOSettings.txt")
        .def("set_log_file_name", &maingo::MAiNGO::set_log_file_name)
        .def("set_result_file_name", &maingo::MAiNGO::set_result_file_name)
        .def("set_solution_and_statistics_csv_file_name", &maingo::MAiNGO::set_solution_and_statistics_csv_file_name)
        .def("set_iterations_csv_file_name", &maingo::MAiNGO::set_iterations_csv_file_name)
        .def("set_json_file_name", &maingo::MAiNGO::set_json_file_name)
        .def("set_bab_file_name", &maingo::MAiNGO::set_bab_file_name)
        .def("write_model_to_file_in_other_language", &maingo::MAiNGO::write_model_to_file_in_other_language,
             py::arg("writingLanguage"), py::arg("fileName") = "MAiNGO_written_model", py::arg("solverName") = "SCIP",
             py::arg("useMinMax") = true, py::arg("useTrig") = true, py::arg("ignoreBoundingFuncs") = false, py::arg("writeRelaxationOnly") = true)
        .def("evaluate_model_at_point", &maingo::MAiNGO::evaluate_model_at_point)
        .def("evaluate_model_at_solution_point", &maingo::MAiNGO::evaluate_model_at_solution_point)
        .def("evaluate_additional_outputs_at_point", &maingo::MAiNGO::evaluate_additional_outputs_at_point)
        .def("evaluate_additional_outputs_at_solution_point", &maingo::MAiNGO::evaluate_additional_outputs_at_solution_point)
        .def("get_cpu_solution_time", &maingo::MAiNGO::get_cpu_solution_time)
        .def("get_final_abs_gap", &maingo::MAiNGO::get_final_abs_gap)
        .def("get_final_LBD", &maingo::MAiNGO::get_final_LBD)
        .def("get_final_rel_gap", &maingo::MAiNGO::get_final_rel_gap)
        .def("get_iterations", &maingo::MAiNGO::get_iterations)
        .def("get_LBP_count", &maingo::MAiNGO::get_LBP_count)
        .def("get_max_nodes_in_memory", &maingo::MAiNGO::get_max_nodes_in_memory)
        .def("get_objective_value", &maingo::MAiNGO::get_objective_value)
        .def("get_solution_point", &maingo::MAiNGO::get_solution_point)
        .def("get_status", &maingo::MAiNGO::get_status)
        .def("get_UBP_count", &maingo::MAiNGO::get_UBP_count)
        .def("get_wallclock_solution_time", &maingo::MAiNGO::get_wallclock_solution_time);
    py::enum_<maingo::RETCODE>(m, "RETCODE")
        .value("GLOBALLY_OPTIMAL", maingo::RETCODE::GLOBALLY_OPTIMAL)
        .value("INFEASIBLE", maingo::RETCODE::INFEASIBLE)
        .value("FEASIBLE_POINT", maingo::RETCODE::FEASIBLE_POINT)
        .value("NO_FEASIBLE_POINT_FOUND", maingo::RETCODE::NO_FEASIBLE_POINT_FOUND)
        .value("BOUND_TARGETS", maingo::RETCODE::BOUND_TARGETS)
        .value("NOT_SOLVED_YET", maingo::RETCODE::NOT_SOLVED_YET)
        .value("JUST_A_WORKER_DONT_ASK_ME", maingo::RETCODE::JUST_A_WORKER_DONT_ASK_ME)
        .export_values();
    py::enum_<maingo::WRITING_LANGUAGE>(m, "WRITING_LANGUAGE")
        .value("LANG_NONE", maingo::WRITING_LANGUAGE::LANG_NONE)
        .value("LANG_ALE", maingo::WRITING_LANGUAGE::LANG_ALE)
        .value("LANG_GAMS", maingo::WRITING_LANGUAGE::LANG_GAMS)
        .export_values();

    // Expose enums for settings
    py::enum_<maingo::VERB>(m, "VERB")
        .value("VERB_NONE", maingo::VERB::VERB_NONE)
        .value("VERB_NORMAL", maingo::VERB::VERB_NORMAL)
        .value("VERB_ALL", maingo::VERB::VERB_ALL)
        .export_values();
    py::enum_<maingo::LOGGING_DESTINATION>(m, "LOGGING_DESTINATION")
        .value("LOGGING_NONE", maingo::LOGGING_DESTINATION::LOGGING_NONE)
        .value("LOGGING_OUTSTREAM", maingo::LOGGING_DESTINATION::LOGGING_OUTSTREAM)
        .value("LOGGING_FILE", maingo::LOGGING_DESTINATION::LOGGING_FILE)
        .value("LOGGING_FILE_AND_STREAM", maingo::LOGGING_DESTINATION::LOGGING_FILE_AND_STREAM)
        .export_values();
    py::enum_<maingo::lbp::LBP_SOLVER>(m, "LBP_SOLVER")
        .value("LBP_SOLVER_MAiNGO", maingo::lbp::LBP_SOLVER::LBP_SOLVER_MAiNGO)
        .value("LBP_SOLVER_INTERVAL", maingo::lbp::LBP_SOLVER::LBP_SOLVER_INTERVAL)
        .value("LBP_SOLVER_CPLEX", maingo::lbp::LBP_SOLVER::LBP_SOLVER_CPLEX)
        .value("LBP_SOLVER_CLP", maingo::lbp::LBP_SOLVER::LBP_SOLVER_CLP)
        .value("LBP_SOLVER_GUROBI", maingo::lbp::LBP_SOLVER::LBP_SOLVER_GUROBI)
        .value("LBP_SOLVER_SUBDOMAIN", maingo::lbp::LBP_SOLVER::LBP_SOLVER_SUBDOMAIN)
        .export_values();
    py::enum_<maingo::lbp::LINP>(m, "LINP")
        .value("LINP_MID", maingo::lbp::LINP_MID)
        .value("LINP_INCUMBENT", maingo::lbp::LINP::LINP_INCUMBENT)
        .value("LINP_KELLEY", maingo::lbp::LINP::LINP_KELLEY)
        .value("LINP_SIMPLEX", maingo::lbp::LINP::LINP_SIMPLEX)
        .value("LINP_RANDOM", maingo::lbp::LINP::LINP_RANDOM)
        .value("LINP_KELLEY_SIMPLEX", maingo::lbp::LINP::LINP_KELLEY_SIMPLEX)
        .export_values();
    py::enum_<maingo::ubp::UBP_SOLVER>(m, "UBP_SOLVER")
        .value("UBP_SOLVER_EVAL", maingo::ubp::UBP_SOLVER::UBP_SOLVER_EVAL)
        .value("UBP_SOLVER_COBYLA", maingo::ubp::UBP_SOLVER::UBP_SOLVER_COBYLA)
        .value("UBP_SOLVER_BOBYQA", maingo::ubp::UBP_SOLVER::UBP_SOLVER_BOBYQA)
        .value("UBP_SOLVER_LBFGS", maingo::ubp::UBP_SOLVER::UBP_SOLVER_LBFGS)
        .value("UBP_SOLVER_SLSQP", maingo::ubp::UBP_SOLVER::UBP_SOLVER_SLSQP)
        .value("UBP_SOLVER_IPOPT", maingo::ubp::UBP_SOLVER::UBP_SOLVER_IPOPT)
        .value("UBP_SOLVER_KNITRO", maingo::ubp::UBP_SOLVER::UBP_SOLVER_KNITRO)
        .export_values();
    py::enum_<maingo::AUGMENTATION_RULE>(m, "AUGMENTATION_RULE")
        .value("AUG_RULE_CONST", maingo::AUGMENTATION_RULE::AUG_RULE_CONST)
        .value("AUG_RULE_SCALING", maingo::AUGMENTATION_RULE::AUG_RULE_SCALING)
        .value("AUG_RULE_OOS", maingo::AUGMENTATION_RULE::AUG_RULE_OOS)
        .value("AUG_RULE_COMBI", maingo::AUGMENTATION_RULE::AUG_RULE_COMBI)
        .value("AUG_RULE_TOL", maingo::AUGMENTATION_RULE::AUG_RULE_TOL)
        .value("AUG_RULE_SCALCST", maingo::AUGMENTATION_RULE::AUG_RULE_SCALCST)
        .value("AUG_RULE_OOSCST", maingo::AUGMENTATION_RULE::AUG_RULE_OOSCST)
        .value("AUG_RULE_COMBICST", maingo::AUGMENTATION_RULE::AUG_RULE_COMBICST)
        .value("AUG_RULE_TOLCST", maingo::AUGMENTATION_RULE::AUG_RULE_TOLCST)
        .export_values();
    py::enum_<maingo::GROWING_APPROACH>(m, "GROWING_APPROACH")
        .value("GROW_APPR_DETERMINISTIC", maingo::GROWING_APPROACH::GROW_APPR_DETERMINISTIC)
        .value("GROW_APPR_SSEHEURISTIC", maingo::GROWING_APPROACH::GROW_APPR_SSEHEURISTIC)
        .value("GROW_APPR_MSEHEURISTIC", maingo::GROWING_APPROACH::GROW_APPR_MSEHEURISTIC)
        .export_values();

    // Expose the MAiNGOmodel class via the dummy class defined above
    py::class_<maingo::MAiNGOmodel, PyMAiNGOmodel, std::shared_ptr<maingo::MAiNGOmodel>>(m, "MAiNGOmodel")
        .def(py::init<>())
        .def("get_variables", &maingo::MAiNGOmodel::get_variables)
        .def("get_initial_point", &maingo::MAiNGOmodel::get_initial_point)
        .def("evaluate", &maingo::MAiNGOmodel::evaluate);

    // Expose the TwoStageModel class
    py::class_<maingo::TwoStageModel, maingo::MAiNGOmodel, PyTwoStageModel, std::shared_ptr<maingo::TwoStageModel>>(m, "TwoStageModel")
        .def(py::init<const unsigned int,                       // Nx
                      const unsigned int,                       // Ny
                      const std::vector<std::vector<double>> &  // data
                      >())
        .def(py::init<const unsigned int,                       // Nx
                      const unsigned int,                       // Ny
                      const std::vector<std::vector<double>> &, // data
                      const std::vector<double> &               // w
                      >())
        .def("get_variables", &maingo::TwoStageModel::get_variables)
        .def("get_initial_point", &maingo::TwoStageModel::get_initial_point)
        .def_readonly("w", &maingo::TwoStageModel::w)
        .def_readonly("data", &maingo::TwoStageModel::data)
        .def_readonly("Nx", &maingo::TwoStageModel::Nx)
        .def_readonly("Ny", &maingo::TwoStageModel::Ny)
        .def_readonly("Ns", &maingo::TwoStageModel::Ns)
        .def_readonly("Nineq1", &maingo::TwoStageModel::Nineq1)
        .def_readonly("Nsquash1", &maingo::TwoStageModel::Nsquash1)
        .def_readonly("Neq1", &maingo::TwoStageModel::Neq1)
        .def_readonly("NineqRelOnly1", &maingo::TwoStageModel::NineqRelOnly1)
        .def_readonly("NeqRelOnly1", &maingo::TwoStageModel::NeqRelOnly1)
        .def_readonly("Nineq2", &maingo::TwoStageModel::Nineq2)
        .def_readonly("Nsquash2", &maingo::TwoStageModel::Nsquash2)
        .def_readonly("Neq2", &maingo::TwoStageModel::Neq2)
        .def_readonly("NineqRelOnly2", &maingo::TwoStageModel::NineqRelOnly2)
        .def_readonly("NeqRelOnly2", &maingo::TwoStageModel::NeqRelOnly2)
        .def("f1_func", &maingo::TwoStageModel::f1_func)
        .def("f2_func", &maingo::TwoStageModel::f2_func)
        .def("g1_func", &maingo::TwoStageModel::g1_func)
        .def("g2_func", &maingo::TwoStageModel::g2_func)
        .def("_update", &maingo::TwoStageModel::_update);

    // Expose everything needed to create variables
    py::class_<babBase::Bounds>(m, "Bounds")
        .def(py::init<const double, const double>());
    py::enum_<babBase::enums::VT>(m, "VT")
        .value("VT_CONTINUOUS", babBase::enums::VT::VT_CONTINUOUS)
        .value("VT_BINARY", babBase::enums::VT::VT_BINARY)
        .value("VT_INTEGER", babBase::enums::VT::VT_INTEGER)
        .export_values();

    py::class_<babBase::OptimizationVariable>(m, "OptimizationVariable")
        .def(py::init<const babBase::Bounds&, const babBase::enums::VT, const unsigned, const std::string>())
        .def(py::init<const babBase::Bounds&, const babBase::enums::VT, const unsigned>())
        .def(py::init<const babBase::Bounds&, const babBase::enums::VT, const std::string>())
        .def(py::init<const babBase::Bounds&, const unsigned, const std::string>())
        .def(py::init<const babBase::Bounds&, const babBase::enums::VT>())
        .def(py::init<const babBase::Bounds&, const unsigned>())
        .def(py::init<const babBase::Bounds&, const std::string>())
        .def(py::init<const babBase::Bounds&>())
        .def(py::init<const babBase::enums::VT, const unsigned, const std::string>())
        .def(py::init<const babBase::enums::VT, const unsigned>())
        .def(py::init<const babBase::enums::VT, const std::string>())
        .def(py::init<const babBase::enums::VT>())
        .def(py::init<const unsigned>())
        .def(py::init<const unsigned, const std::string>())
        .def(py::init<const std::string>())
        .def("get_lower_bound", &babBase::OptimizationVariable::get_lower_bound)
        .def("get_upper_bound", &babBase::OptimizationVariable::get_upper_bound)
        .def("get_name", &babBase::OptimizationVariable::get_name)
        .def("get_branching_priority", &babBase::OptimizationVariable::get_branching_priority)
        ;

    // Expose FFVar along with the overloaded operators - so we can write the evaluate function
    py::class_<mc::FFVar>(m, "FFVar")
        .def("name", &mc::FFVar::name)
        .def("__repr__", [](const mc::FFVar& v) {
                    std::stringstream stream;
                    stream << "<FFVar object";
                    if (v.dag())
                        stream << " of DAG " << v.dag();
                    else
                        stream << " without DAG ";
                    stream << " with id " << v.name();
                    if (v.num().val())
                        stream << " and value " << v.num();
                    stream << " at " << &v << ">";
                    return stream.str(); 
                })
        .def(py::init<>())
        .def(py::init<double>())
        .def(py::init<int>())
        .def(py::self * py::self)
        .def(py::self * float())
        .def(float() * py::self)
        .def(py::self + py::self)
        .def(py::self + float())
        .def(float() + py::self)
        .def(+py::self)
        .def(py::self - py::self)
        .def(py::self - float())
        .def(float() - py::self)
        .def(-py::self)
        .def(py::self / py::self)
        .def(py::self / float())
        .def(float() / py::self)
        .def(py::self == py::self)
        .def(py::self += py::self)
        .def(py::self -= py::self)
        .def(py::self *= py::self)
        .def(py::self /= py::self)
        .def(
            "__rpow__", [](const mc::FFVar& x, const double d) { return mc::pow(d, x); }, py::is_operator())
        .def("__pow__", py::overload_cast<const mc::FFVar&, const double>(&mc::pow), py::is_operator())
        .def("__pow__", py::overload_cast<const mc::FFVar&, const int>(&mc::pow), py::is_operator())
        .def("__pow__", py::overload_cast<const mc::FFVar&, const mc::FFVar&>(&mc::pow), py::is_operator());
    py::implicitly_convertible<double, mc::FFVar>();
    py::implicitly_convertible<int, mc::FFVar>();


    // Expose all intrinsic functions (beyond the operators)
    m.def("inv", py::overload_cast<const mc::FFVar&>(&mc::inv), "Multiplicative inverse function");
    m.def("sqr", py::overload_cast<const mc::FFVar&>(&mc::sqr), "Square function");
    m.def("exp", py::overload_cast<const mc::FFVar&>(&mc::exp), "Exponential function");
    m.def("log", py::overload_cast<const mc::FFVar&>(&mc::log), "Natural logartihm");
    m.def("xlog", py::overload_cast<const mc::FFVar&>(&mc::xlog), "x * log(x)");
    m.def("fabsx_times_x", py::overload_cast<const mc::FFVar&>(&mc::fabsx_times_x), "|x| * x");
    m.def("xexpax", py::overload_cast<const mc::FFVar&, const double>(&mc::xexpax), "x*exp(a*x)");
    m.def("arh", py::overload_cast<const mc::FFVar&, const double>(&mc::arh), "exp(-k/x)");
    m.def("vapor_pressure", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double, const double, const double, const double, const double, const double, const double>(&mc::vapor_pressure), "Vapor pressure",
          py::arg("x"), py::arg("type"), py::arg("p1"), py::arg("p2"), py::arg("p3"), py::arg("p4") = 0, py::arg("p5") = 0, py::arg("p6") = 0, py::arg("p7") = 0, py::arg("p8") = 0, py::arg("p9") = 0, py::arg("p10") = 0);
    m.def("ideal_gas_enthalpy", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double, const double, const double, const double, const double>(&mc::ideal_gas_enthalpy), "Ideal gas enthalpy",
          py::arg("x"), py::arg("0"), py::arg("type"), py::arg("p1"), py::arg("p2"), py::arg("p3"), py::arg("p4"), py::arg("p5"), py::arg("p6") = 0, py::arg("p7") = 0);
    m.def("saturation_temperature", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double, const double, const double, const double, const double, const double, const double>(&mc::saturation_temperature), "Saturation temperature",
          py::arg("x"), py::arg("type"), py::arg("p1"), py::arg("p2"), py::arg("p3"), py::arg("p4") = 0, py::arg("p5") = 0, py::arg("p6") = 0, py::arg("p7") = 0, py::arg("p8") = 0, py::arg("p9") = 0, py::arg("p10") = 0);
    m.def("enthalpy_of_vaporization", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double, const double, const double>(&mc::enthalpy_of_vaporization), "Enthalpy of vaporization",
          py::arg("x"), py::arg("type"), py::arg("p1"), py::arg("p2"), py::arg("p3"), py::arg("p4"), py::arg("p5"), py::arg("p6") = 0);
    m.def("cost_function", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double>(&mc::cost_function), "Cost function");
    m.def("sum_div", py::overload_cast<const std::vector<mc::FFVar>&, const std::vector<double>&>(&mc::sum_div), "sum_div: a*x_0 / (b_0*x*0 + ... + b_n*x_n)");
    m.def("xlog_sum", py::overload_cast<const std::vector<mc::FFVar>&, const std::vector<double>&>(&mc::xlog_sum), "x_0*log(a_0*x_0 + ... + a_n*x_n)");
    m.def("nrtl_tau", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double>(&mc::nrtl_tau), "NRTL tau");
    m.def("nrtl_dtau", py::overload_cast<const mc::FFVar&, const double, const double, const double>(&mc::nrtl_dtau), "NRTL dTau/dT");
    m.def("nrtl_G", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double>(&mc::nrtl_G), "NRTL G");
    m.def("nrtl_Gtau", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double>(&mc::nrtl_Gtau), "NRTL G*tau");
    m.def("nrtl_Gdtau", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double>(&mc::nrtl_Gdtau), "NRTL G*dtau/dT");
    m.def("nrtl_dGtau", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double>(&mc::nrtl_dGtau), "NRTL tau*dG/dT");
    m.def("iapws", py::overload_cast<const mc::FFVar&, const double>(&mc::iapws), "IAPWS (1D)");
    m.def("iapws", py::overload_cast<const mc::FFVar&, const mc::FFVar&, const double>(&mc::iapws), " IAPWS (2D)");
    m.def("p_sat_ethanol_schroeder", py::overload_cast<const mc::FFVar&>(&mc::p_sat_ethanol_schroeder), "psat Ethanol Schroeder");
    m.def("rho_vap_sat_ethanol_schroeder", py::overload_cast<const mc::FFVar&>(&mc::rho_vap_sat_ethanol_schroeder), "rhovap Ethanol Schroeder");
    m.def("rho_liq_sat_ethanol_schroeder", py::overload_cast<const mc::FFVar&>(&mc::rho_liq_sat_ethanol_schroeder), "rholiq Ethanol Schroeder");
    m.def("covariance_function", py::overload_cast<const mc::FFVar&, const double>(&mc::covariance_function), "Covariance function");
    m.def("acquisition_function", py::overload_cast<const mc::FFVar&, const mc::FFVar&, const double, const double>(&mc::acquisition_function), "Acquisition function");
    m.def("gaussian_probability_density_function", py::overload_cast<const mc::FFVar&>(&mc::gaussian_probability_density_function), "Probability density function");
    m.def("regnormal", py::overload_cast<const mc::FFVar&, const double, const double>(&mc::regnormal), "Regnormal: x / sqrt(a+b*x^2)");
    m.def("pos", py::overload_cast<const mc::FFVar&>(&mc::pos), "pos(x) - cuts off convex relaxation at eps>0");
    m.def("neg", py::overload_cast<const mc::FFVar&>(&mc::neg), "neg(x) - cuts off concave relaxation at -eps<0");
    m.def("lb_func", py::overload_cast<const mc::FFVar&, const double>(&mc::lb_func), "lbfunc(x,a) - cuts off convex relaxation at a");
    m.def("ub_func", py::overload_cast<const mc::FFVar&, const double>(&mc::ub_func), "ubfunc(x,a) - cuts off concave relaxation at a");
    m.def("bounding_func", py::overload_cast<const mc::FFVar&, const double, const double>(&mc::bounding_func), "boundingfunc(x,a,b)  - cuts off relaxations to be within [a,b]");
    m.def("squash_node", py::overload_cast<const mc::FFVar&, const double, const double>(&mc::squash_node), "Squashing node");    // this node is meant to be used for better reduced space formulations
    m.def("single_neuron", py::overload_cast<const std::vector<mc::FFVar>&, const std::vector<double>&, const double, const int>(&mc::single_neuron), "single_neuron: tanh(w1*var1+w2*var2+...+b)");
    m.def("sqrt", py::overload_cast<const mc::FFVar&>(&mc::sqrt), "Square root");
    m.def("fabs", py::overload_cast<const mc::FFVar&>(&mc::fabs), "Absolute value");
    m.def("cos", py::overload_cast<const mc::FFVar&>(&mc::cos), "Cosine");
    m.def("sin", py::overload_cast<const mc::FFVar&>(&mc::sin), "Sine");
    m.def("tan", py::overload_cast<const mc::FFVar&>(&mc::tan), "Tangent");
    m.def("acos", py::overload_cast<const mc::FFVar&>(&mc::acos), "Inverse cosine");
    m.def("asin", py::overload_cast<const mc::FFVar&>(&mc::asin), "Inverse sine");
    m.def("atan", py::overload_cast<const mc::FFVar&>(&mc::atan), "Inverse tangent");
    m.def("cosh", py::overload_cast<const mc::FFVar&>(&mc::cosh), "Hyperbolic cosine");
    m.def("sinh", py::overload_cast<const mc::FFVar&>(&mc::sinh), "Hyperbolic sine");
    m.def("tanh", py::overload_cast<const mc::FFVar&>(&mc::tanh), "Hyperbolic tangent");
    m.def("coth", py::overload_cast<const mc::FFVar&>(&mc::coth), "Hyperbolic cotangent");
    m.def("erf", py::overload_cast<const mc::FFVar&>(&mc::erf), "Error function");
    m.def("erfc", py::overload_cast<const mc::FFVar&>(&mc::erfc), "Complementary error function");
    m.def("fstep", py::overload_cast<const mc::FFVar&>(&mc::fstep), "Forward step: fstep(x) = 1 if x>=0, and 0 otherwise");
    m.def("bstep", py::overload_cast<const mc::FFVar&>(&mc::bstep), "Backward step: bstep(x) = 1 if x<0, and o otherwise");
    m.def("pow", py::overload_cast<const mc::FFVar&, const int>(&mc::pow), "x^n, where n is a natural number");
    m.def("pow", py::overload_cast<const mc::FFVar&, const double>(&mc::pow), "x^d, where d is a real number");
    m.def("pow", py::overload_cast<const mc::FFVar&, const mc::FFVar&>(&mc::pow), "x^y, where x and y are both variables");
    m.def("pow", py::overload_cast<const double, const mc::FFVar&>(&mc::pow), "d^x, where d is a real number");
    m.def("cheb", py::overload_cast<const mc::FFVar&, const unsigned>(&mc::cheb), "cheb(x,n) = Chebyshev polynomial of degree n");


    // More intrinsic functions that require a special twist:
    // The py::overload_cast has problems with the combination of template and non-template overloads used in MC++
    // see also https://github.com/pybind/py/issues/1153
    //  --> need to resort to conventional casts
    m.def("max", static_cast<mc::FFVar (*)(const mc::FFVar&, const mc::FFVar&)>(&mc::max), "Maximum of two variables");
    m.def("max", static_cast<mc::FFVar (*)(const double&, const mc::FFVar&)>(&mc::max<double>), "Maximum of a constant and a variable");
    m.def("max", static_cast<mc::FFVar (*)(const mc::FFVar&, const double&)>(&mc::max<double>), "Maximum of a variable and a constant");
    m.def("min", static_cast<mc::FFVar (*)(const mc::FFVar&, const mc::FFVar&)>(&mc::min), "Minimum of two variables");
    m.def("min", static_cast<mc::FFVar (*)(const double&, const mc::FFVar&)>(&mc::min<double>), "Minimum of a constant and a variable");
    m.def("min", static_cast<mc::FFVar (*)(const mc::FFVar&, const double&)>(&mc::min<double>), "Minimum of a variable and a constant");
    m.def("lmtd", static_cast<mc::FFVar (*)(const mc::FFVar&, const mc::FFVar&)>(&mc::lmtd), "Log mean temperature difference: lmtd(x,y)");
    m.def("lmtd", static_cast<mc::FFVar (*)(const double&, const mc::FFVar&)>(&mc::lmtd<double>), "Log mean temperature difference: lmtd(a,x)");
    m.def("lmtd", static_cast<mc::FFVar (*)(const mc::FFVar&, const double&)>(&mc::lmtd<double>), "Log mean temperature difference: lmtd(x,a)");
    m.def("rlmtd", static_cast<mc::FFVar (*)(const mc::FFVar&, const mc::FFVar&)>(&mc::rlmtd), "Inverse of log mean temperature difference: rlmtd(x,y)");
    m.def("rlmtd", static_cast<mc::FFVar (*)(const double&, const mc::FFVar&)>(&mc::rlmtd<double>), "Inverse of log mean temperature difference: rlmtd(a,x)");
    m.def("rlmtd", static_cast<mc::FFVar (*)(const mc::FFVar&, const double&)>(&mc::rlmtd<double>), "Inverse of log mean temperature difference: rlmtd(x,a)");
    m.def("euclidean_norm_2d", static_cast<mc::FFVar (*)(const mc::FFVar&, const mc::FFVar&)>(&mc::euclidean_norm_2d), "Euclidean norm in 2d");
    m.def("euclidean_norm_2d", static_cast<mc::FFVar (*)(const double&, const mc::FFVar&)>(&mc::euclidean_norm_2d<double>), "Euclidean norm in 2d");
    m.def("euclidean_norm_2d", static_cast<mc::FFVar (*)(const mc::FFVar&, const double&)>(&mc::euclidean_norm_2d<double>), "Euclidean norm in 2d");
    m.def("expx_times_y", static_cast<mc::FFVar (*)(const mc::FFVar&, const mc::FFVar&)>(&mc::expx_times_y), "exp(x) * y");
    m.def("expx_times_y", static_cast<mc::FFVar (*)(const double&, const mc::FFVar&)>(&mc::expx_times_y<double>), "exp(a) * x");
    m.def("expx_times_y", static_cast<mc::FFVar (*)(const mc::FFVar&, const double&)>(&mc::expx_times_y<double>), "exp(x) * a");


    // Expose additional function aliases defined in functionWrapper.h
    m.def("xlogx", py::overload_cast<const mc::FFVar&>(&xlogx), "x * log(x)");
    m.def("xexpy", py::overload_cast<const mc::FFVar&, const mc::FFVar&>(&xexpy), "exp(x)*y");
    m.def("norm2", py::overload_cast<const mc::FFVar&, const mc::FFVar&>(&norm2), "Euclidean norm in 2d");
    m.def("xabsx", py::overload_cast<const mc::FFVar&>(&xabsx), "|x| * x");
    m.def("squash", py::overload_cast<const mc::FFVar&, const double, const double>(&squash), "Squashing node");
    m.def("ext_antoine_psat", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double, const double, const double>(&ext_antoine_psat), "Extended Antoine vapor pressure model");
    m.def("ext_antoine_psat", py::overload_cast<const mc::FFVar&, const std::vector<double>>(&ext_antoine_psat), "Extended Antoine vapor pressure model");
    m.def("antoine_psat", py::overload_cast<const mc::FFVar&, const double, const double, const double>(&antoine_psat), "Antoine vapor pressure model");
    m.def("antoine_psat", py::overload_cast<const mc::FFVar&, const std::vector<double>>(&antoine_psat), "Antoine vapor pressure model");
    m.def("wagner_psat", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double, const double>(&wagner_psat), "Wagner vapor pressure model");
    m.def("wagner_psat", py::overload_cast<const mc::FFVar&, const std::vector<double>>(&wagner_psat), "Wagner vapor pressure model");
    m.def("ik_cape_psat", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double, const double, const double, const double, const double, const double>(&ik_cape_psat), "IK Cape vapor pressure model");
    m.def("ik_cape_psat", py::overload_cast<const mc::FFVar&, const std::vector<double>>(&ik_cape_psat), "IK Cape vapor pressure model");
    m.def("antoine_tsat", py::overload_cast<const mc::FFVar&, const double, const double, const double>(&antoine_tsat), "Antoine saturation temperature model");
    m.def("antoine_tsat", py::overload_cast<const mc::FFVar&, const std::vector<double>>(&antoine_tsat), "Antoine saturation temperature model");
    m.def("aspen_hig", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double, const double, const double>(&aspen_hig), "Aspen ideal gas enthalpy model");
    m.def("aspen_hig", py::overload_cast<const mc::FFVar&, const double, const std::vector<double>>(&aspen_hig), "Aspen ideal gas enthalpy model");
    m.def("nasa9_hig", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double, const double, const double, const double>(&nasa9_hig), "NASA 9-coefficient ideal gas enthalpy model");
    m.def("nasa9_hig", py::overload_cast<const mc::FFVar&, const double, const std::vector<double>>(&nasa9_hig), "NASA 9-coefficient ideal gas enthalpy model");
    m.def("dippr107_hig", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double, const double>(&dippr107_hig), "DIPPR-107 ideal gas enthalpy model");
    m.def("dippr107_hig", py::overload_cast<const mc::FFVar&, const double, const std::vector<double>>(&dippr107_hig), "DIPPR-107 ideal gas enthalpy model");
    m.def("dippr127_hig", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double, const double, const double, const double>(&dippr127_hig), "DIPPR-127 ideal gas enthalpy model");
    m.def("dippr127_hig", py::overload_cast<const mc::FFVar&, const double, const std::vector<double>>(&dippr127_hig), "DIPPR-127 ideal gas enthalpy model");
    m.def("watson_dhvap", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double>(&watson_dhvap), "Watson enthalpy of vaporization model");
    m.def("watson_dhvap", py::overload_cast<const mc::FFVar&, const std::vector<double>>(&watson_dhvap), "Watson enthalpy of vaporization model");
    m.def("dippr106_dhvap", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double, const double>(&dippr106_dhvap), "DIPPR106 enthalpy of vaporization model");
    m.def("dippr106_dhvap", py::overload_cast<const mc::FFVar&, const std::vector<double>>(&dippr106_dhvap), "DIPPR106 enthalpy of vaporization model");
    m.def("nrtl_tau", py::overload_cast<const mc::FFVar&, const std::vector<double>>(&nrtl_tau), "NRTL tau");
    m.def("nrtl_dtau", py::overload_cast<const mc::FFVar&, const std::vector<double>>(&nrtl_dtau), "NRTL dtau/dT");
    m.def("nrtl_g", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double>(&nrtl_g), "NRTL G");
    m.def("nrtl_g", py::overload_cast<const mc::FFVar&, const std::vector<double>>(&nrtl_g), "NRTL G");
    m.def("nrtl_gtau", py::overload_cast<const mc::FFVar&, const std::vector<double>>(&nrtl_gtau), "NRTL G*tau");
    m.def("nrtl_gtau", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double>(&nrtl_gtau), "NRTL G*tau");
    m.def("nrtl_gdtau", py::overload_cast<const mc::FFVar&, const std::vector<double>>(&nrtl_gdtau), "NRTL G*dtau/dT");
    m.def("nrtl_gdtau", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double>(&nrtl_gdtau), "NRTL G*dtau/dT");
    m.def("nrtl_dgtau", py::overload_cast<const mc::FFVar&, const std::vector<double>>(&nrtl_dgtau), "NRTL dG/dT*tau");
    m.def("nrtl_dgtau", py::overload_cast<const mc::FFVar&, const double, const double, const double, const double, const double>(&nrtl_dgtau), "NRTL dG/dT*tau");
    m.def("schroeder_ethanol_p", py::overload_cast<const mc::FFVar&>(&schroeder_ethanol_p), "psat Ethanol Schroeder");
    m.def("schroeder_ethanol_rhovap", py::overload_cast<const mc::FFVar&>(&schroeder_ethanol_rhovap), "rhovap Ethanol Schroeder");
    m.def("schroeder_ethanol_rholiq", py::overload_cast<const mc::FFVar&>(&schroeder_ethanol_rholiq), "rholiq Ethanol Schroeder");
    m.def("cost_turton", py::overload_cast<const mc::FFVar&, const std::vector<double>>(&cost_turton), "Turton cost function");
    m.def("cost_turton", py::overload_cast<const mc::FFVar&, const double, const double, const double>(&cost_turton), "Turton cost function");
    m.def("covar_matern_1", py::overload_cast<const mc::FFVar&>(&covar_matern_1), "Matern 1 covariance function");
    m.def("covar_matern_3", py::overload_cast<const mc::FFVar&>(&covar_matern_3), "Matern 3 covariance function");
    m.def("covar_matern_5", py::overload_cast<const mc::FFVar&>(&covar_matern_5), "Matern 5 covariance function");
    m.def("covar_sqrexp", py::overload_cast<const mc::FFVar&>(&covar_sqrexp), "Squared exponential covariance function");
    m.def("af_lcb", py::overload_cast<const mc::FFVar&, const mc::FFVar&, const double>(&af_lcb), "Lower confidence bound acquisition function");
    m.def("af_ei", py::overload_cast<const mc::FFVar&, const mc::FFVar&, const double>(&af_ei), "Expected improvement acquisition function");
    m.def("af_pi", py::overload_cast<const mc::FFVar&, const mc::FFVar&, const double>(&af_pi), "Probability of improvement acquisition function");
    m.def("gpdf", py::overload_cast<const mc::FFVar&>(&gpdf), "Gaussian probability density function");


    // Expose everything needed to return the result of the evaluate function
    py::class_<maingo::EvaluationContainer>(m, "EvaluationContainer")
        .def(py::init<>())
        .def_readwrite("objective", &maingo::EvaluationContainer::objective)
        .def_readwrite("obj", &maingo::EvaluationContainer::objective)
        .def_readwrite("objective_per_data", &maingo::EvaluationContainer::objective_per_data)
        .def_readwrite("objData", &maingo::EvaluationContainer::objective_per_data)
        .def_readwrite("eq", &maingo::EvaluationContainer::eq)
        .def_readwrite("equalities", &maingo::EvaluationContainer::eq)
        .def_readwrite("ineq", &maingo::EvaluationContainer::ineq)
        .def_readwrite("inequalities", &maingo::EvaluationContainer::ineq)
        .def_readwrite("eqRelaxationOnly", &maingo::EvaluationContainer::eqRelaxationOnly)
        .def_readwrite("eqRO", &maingo::EvaluationContainer::eqRelaxationOnly)
        .def_readwrite("equalitiesRelaxationOnly", &maingo::EvaluationContainer::eqRelaxationOnly)
        .def_readwrite("ineqRelaxationOnly", &maingo::EvaluationContainer::ineqRelaxationOnly)
        .def_readwrite("ineqRO", &maingo::EvaluationContainer::ineqRelaxationOnly)
        .def_readwrite("inequalitiesRelaxationOnly", &maingo::EvaluationContainer::ineqRelaxationOnly)
        .def_readwrite("ineqSquash", &maingo::EvaluationContainer::ineqSquash)
        .def_readwrite("inequalitiesSquash", &maingo::EvaluationContainer::ineqSquash)
        .def_readwrite("output", &maingo::EvaluationContainer::output)
        .def_readwrite("out", &maingo::EvaluationContainer::output);
    py::class_<maingo::ModelFunction>(m, "ModelFunction")
        .def(py::init<>())
        .def(py::init<const mc::FFVar>())
        .def(py::init<const mc::FFVar, const std::string&>())
        .def(py::init<const std::vector<mc::FFVar>&>())
        .def("clear", &maingo::ModelFunction::clear)
        .def("push_back", py::overload_cast<const mc::FFVar>(&maingo::ModelFunction::push_back))
        .def("append", py::overload_cast<const mc::FFVar>(&maingo::ModelFunction::push_back))    // Addition to allow for more intuitive use in Python
        .def("push_back", py::overload_cast<const mc::FFVar, const std::string&>(&maingo::ModelFunction::push_back))
        .def("push_back", py::overload_cast<const std::vector<mc::FFVar>&>(&maingo::ModelFunction::push_back))
        .def("push_back", py::overload_cast<const std::vector<mc::FFVar>&, const std::string&>(&maingo::ModelFunction::push_back))
        .def_readwrite("name", &maingo::ModelFunction::name)
        .def_readwrite("value", &maingo::ModelFunction::value)
        .def(py::self == py::self);
    py::implicitly_convertible<mc::FFVar, maingo::ModelFunction>();
    py::implicitly_convertible<std::vector<mc::FFVar>, maingo::ModelFunction>();
    py::class_<maingo::OutputVariable>(m, "OutputVariable")
        .def(py::init<const std::string, const mc::FFVar>())
        .def(py::init<const mc::FFVar, const std::string>())
        .def(py::init<const std::tuple<std::string, mc::FFVar>>())
        .def(py::init<const std::tuple<mc::FFVar, std::string>>())
        .def_readwrite("description", &maingo::OutputVariable::description)
        .def_readwrite("value", &maingo::OutputVariable::value)
        .def(py::self == py::self);

    // MPI
    py::class_<BufferPair>(m, "BufferPair");
    m.def("HAVE_MAiNGO_MPI", &haveMPI, "make pre-processor variable HAVE_MAiNGO_MPI available for Python API");
    m.def("muteWorker", &muteWorkerOutput, "Mute Output for workers to avoid multiple outputs");
    m.def("unmuteWorker", &unmuteWorkerOutput, "Unmute Output for workers");
    //Expose MAiNGOException
    PYBIND11_CONSTINIT static py::gil_safe_call_once_and_store<py::object> exc_storage;
    exc_storage.call_once_and_store_result(
        [&]() { return py::exception<maingo::MAiNGOException>(m, "MAiNGOException"); });
    py::register_exception_translator([](std::exception_ptr p) {
        try {
            if (p)
                std::rethrow_exception(p);
        }
        catch (const maingo::MAiNGOException& e) {
            py::set_error(exc_storage.get_stored(), e.what());
        }
    });
}