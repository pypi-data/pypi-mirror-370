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

#pragma once

#include "MAiNGOdebug.h"
#include "MAiNGOmodel.h"
#include "TwoStageModel.h"
#include "constraint.h"
#include "logger.h"
#include "returnCodes.h"
#include "settings.h"

#include "babNode.h"
#include "babUtils.h"

#include <list>
#include <memory>
#include <utility>
#include <vector>
#include <random>


namespace maingo {


// Forward declarations to avoid excessive includes
namespace bab {
class BranchAndBound;
}    // end namespace bab
namespace lbp {
class LowerBoundingSolver;
}    // end namespace lbp
namespace ubp {
class UpperBoundingSolver;
}    // end namespace ubp


/**
* @class MAiNGO
* @brief This class is the MAiNGO solver holding the B&B tree, upper bounding solver, lower bounding solver and settings
*
* This class is used to instantiate a MAiNGO object. It is used to solve a given MAiNGOmodel by doing pre-processing, holding the B&B tree, upper bounding solvers, a lower bounding solver and settings
*/
class MAiNGO {

  public:
    /**
        *  @brief Constructor that does not require a model
        */
    MAiNGO();

    /**
        *  @brief Constructor that requires a model
        */
    MAiNGO(std::shared_ptr<MAiNGOmodel> myModel);

    MAiNGO(const MAiNGO &) = delete;
    MAiNGO(MAiNGO &&) = delete;
    MAiNGO &operator=(const MAiNGO &) = delete;
    MAiNGO &operator=(MAiNGO &&) = delete;
    ~MAiNGO() = default;

    /**
        *  @brief Initializes model
        */
    void set_model(std::shared_ptr<MAiNGOmodel> myModel);

    /**
        *  @brief Solves the problem
        */
    RETCODE solve();

    /**
        *  @brief Solve a multi-objective problem using the epsilon-constraint method
        */
    RETCODE solve_epsilon_constraint();

    /**
        *  @brief Sets an option with a double value. This function is used for all options.
        *
        *  @param[in] option is the option name
        *  @param[in] value is the option value (as double)
        */
    bool set_option(const std::string &option, const double value);

    /**
        *  @brief Sets an option with a boolean value.
        *
        *   Just forwards to version with double value. This is needed for compatibility with the Python interface.
        *
        *  @param[in] option is the option name
        *  @param[in] value is the option value
        */
    bool set_option(const std::string &option, const bool value) { return set_option(option, (double)value); }

    /**
        *  @brief Sets an option with an integer value - just forwards to version with double value
        *
        *   Just forwards to version with double value. This is needed for compatibility with the Python interface.
        *
        *  @param[in] option is the option name
        *  @param[in] value is the option value
        */
    bool set_option(const std::string &option, const int value) { return set_option(option, (double)value); }

    /**
        *  @brief Reads settings from text file.
        *
        *  @param[in] settingsFileName is the file name.
        */
    void read_settings(const std::string &settingsFileName = "MAiNGOSettings.txt");

    /**
        *  @brief Sets input stream from which user input may be read during solution.
        *
        *  @param[in] input is the address of the new input stream to be used by MAiNGO.
        */
    void set_input_stream(std::istream *const inputStream) { _inputStream = inputStream; }

    /**
        *  @brief Sets output stream onto which logging information may be printed.
        *
        *  @param[in] outputStream is the address of the new output stream to be used by MAiNGO.
        */
    void set_output_stream(std::ostream *const outputStream) { _logger->set_output_stream(outputStream); }

    /**
        *  @brief Sets name of the log file into which logging information may be written.
        *
        *  @param[in] logFileName is the file name.
        */
    void set_log_file_name(const std::string &logFileName) { _logger->logFileName = logFileName; }

    /**
        *  @brief Sets name of the text file into which information on the solution may be written.
        *
        *  @param[in] resultFileName is the file name.
        */
    void set_result_file_name(const std::string &resultFileName) { _resultFileName = resultFileName; }

    /**
        *  @brief Sets names of the csv file into which the solution and statistics may be written.
        *
        *  @param[in] csvSolutionStatisticsName is the file name.
        */
    void set_solution_and_statistics_csv_file_name(const std::string &csvSolutionStatisticsName) { _csvSolutionStatisticsName = csvSolutionStatisticsName; }

    /**
        *  @brief Sets names of the csv file into which information on the individual B&B iterations may be written.
        *
        *  @param[in] csvIterationsName is the file name, where B&B iterations are written.
        */
    void set_iterations_csv_file_name(const std::string &csvIterationsName) { _logger->csvIterationsName = csvIterationsName; }

    /**
        *  @brief Sets name of the json file into which information on the problem and solution may be written.
        *
        *  @param[in] jsonFileName is the file name.
        */
    void set_json_file_name(const std::string &jsonFileName) { _jsonFileName = jsonFileName; }

    /**
     *  @brief Sets name of the dot file that contains the structure of the branch and bound tree.
     *
     *  @param[in] babFileName is the file name.
     */
    void set_bab_file_name(const std::string &babFileName) { _babFileName = babFileName; }

    /**
        *  @brief Writes MAiNGO model to a a file in a different modeling language.
        *
        *  @param[in] writingLanguage is the modeling language in which the MAiNGO model is to be written.
        *  @param[in] fileName is the file name. If it is empty, the default name "MAiNGO_written_model" will be used instead with a filename extensions depending on the modeling language.
        *  @param[in] solverName is the solver name. If it is empty, the default solver SCIP will be used in the gams file.
        *  @param[in] useMinMax if true then min/max is used when writing output, otherwise the equivalent abs forms are used.
        *  @param[in] useTrig if true then sinh, cosh, tanh is used when writing output, otherwise the equivalent exp forms are used.
        *  @param[in] ignoreBoundingFuncs if true then squash_node, pos, neg, bounding_func, lb_func and ub_func are ignored otherwise they will be simply written into the file.
        *  @param[in] writeRelaxationOnly if true then relaxation-only equalities and inequalities will be written into the file as well.
        */
    void write_model_to_file_in_other_language(const WRITING_LANGUAGE writingLanguage, std::string fileName = "", const std::string solverName = "SCIP",
                                               const bool useMinMax = true, const bool useTrig = true, const bool ignoreBoundingFuncs = false, const bool writeRelaxationOnly = true);

    /**
        * @name MAiNGO getter functions
        */
    /**@{*/
    /**
        *  @brief Function returning objective value
        */
    double get_objective_value() const;

    /**
        *  @brief Function returning solution point
        */
    std::vector<double> get_solution_point() const;

    /**
        *  @brief Function returning CPU solution time
        */
    double get_cpu_solution_time() const;

    /**
        *  @brief Function returning wallclock solution time
        */
    double get_wallclock_solution_time() const;

    /**
        *  @brief Function returning the number of iterations
        */
    double get_iterations() const;

    /**
        *  @brief Function returning the maximum number of nodes in memory
        */
    double get_max_nodes_in_memory() const;

    /**
        *  @brief Function returning number of UBD problems solved
        */
    double get_UBP_count() const;

    /**
        *  @brief Function returning number of LBD problems solved
        */
    double get_LBP_count() const;

    /**
        *  @brief Function returning the final LBD
        */
    double get_final_LBD() const;

    /**
        *  @brief Function returning the final absolute gap
        */
    double get_final_abs_gap() const;

    /**
        *  @brief Function returning the final relative gap
        */
    double get_final_rel_gap() const;

    /**
        *  @brief Function returning a desired setting value
        *
        *  @param[in] option is the option name
        */
    double get_option(const std::string &option) const;

    /**
        *  @brief Funcition returning whether MAiNGO solved the problem or not
        */
    RETCODE get_status() const;

    /**
        *  @brief Function returning all model function values at solution point.
        *         The ordering of the returned vector is:
        *         vector[0]: objective
        *         vector[1 to (1+ineq)]: inequalities ( + constant inequalities )
        *         vector[(1+ineq) to (1+ineq+eq)]: equalities ( + constant equalities )
        *         vector[(1+ineq+eq) to (1+ineq+eq+ineqRelOnly)]: relaxation only inequalities ( + constant rel only inequalities )
        *         vector[(1+ineq+eq+ineqRelOnly) to (1+ineq+eq+ineqRelOnly+eqRelOnly)]: relaxation only equalities ( + constant rel only equalities )
        *         vector[(1+ineq+eq+ineqRelOnly+eqRelOnly) to (1+ineq+eq+ineqRelOnly+eqRelOnly+ineqSquash)]: squash inequalities ( + constant squash inequalities )
        */
    std::vector<double> evaluate_model_at_solution_point();

    /**
        *  @brief Function returning the additional model outputs at the solution point
        */
    std::vector<std::pair<std::string, double>> evaluate_additional_outputs_at_solution_point();

    /**
        *  @brief Function telling whether a point is feasible or not and returning values of the set model of the objective and all constraints at a point.
        *         The ordering of the vector containing the values of the objective and constraints is:
        *         vector[0]: objective
        *         vector[1 to (1+ineq)]: inequalities ( + constant inequalities )
        *         vector[(1+ineq) to (1+ineq+eq)]: equalities ( + constant equalities )
        *         vector[(1+ineq+eq) to (1+ineq+eq+ineqRelOnly)]: relaxation only inequalities ( + constant rel only inequalities )
        *         vector[(1+ineq+eq+ineqRelOnly) to (1+ineq+eq+ineqRelOnly+eqRelOnly)]: relaxation only equalities ( + constant rel only equalities )
        *         vector[(1+ineq+eq+ineqRelOnly+eqRelOnly) to (1+ineq+eq+ineqRelOnly+eqRelOnly+ineqSquash)]: squash inequalities ( + constant squash inequalities )
        *
        *  @param[in] point is the point to be evaluated
        *  @return returns a tuple consisting of a vector containing the objective value and all constraint residuas, as well as a bool indicating whether the point is feasible or not
        */
    std::pair<std::vector<double>, bool> evaluate_model_at_point(const std::vector<double> &point);

    /**
        *  @brief Function returning values of the additional outputs of the set model at a point
        *
        *  @param[in] point is the point to be evaluated
        */
    std::vector<std::pair<std::string, double>> evaluate_additional_outputs_at_point(const std::vector<double> &point);
    /**@}*/

    /**
        *  @brief Function printing an ASCII MAiNGO with copyright
        */
    void print_MAiNGO(std::ostream &outstream = std::cout);

  private:

    /**
        *  @brief Internal function conducts structure recognition, sets constraint properties, and invokes the correct solution routine
        */
    RETCODE _analyze_and_solve_problem();

    /**
        *  @brief Solves an LP, MIP, QP or MIQP
        */
    RETCODE _solve_MIQP();

    /**
        *  @brief Solves an NLP or MINLP
        */
    RETCODE _solve_MINLP();

    /**
        *  @brief Construct DAG
        */
    void _construct_DAG();

    /**
        *  @brief Print information about the major pieces of third-party software used when solving an (MI)NLP
        */
    void _print_third_party_software_minlp();

    /**
        *  @brief Print information about the major pieces of third-party software used when solving an (MI)QP/(MI)LP
        */
    void _print_third_party_software_miqp();

    /**
        *  @brief Evaluate model at initial point and print the values of the variables, objective, constraint residuals and outputs
        */
    void _print_info_about_initial_point();

    /**
        *  @brief Fills the constraints vectors (original, constant, non-constant) and outputs and writes non-constant functions and outputs to the provided vectors
        *         This function DOES NOT classify auxiliary relaxation only equalities as this is done in _add_auxiliary_variables_to_lbd_dag
        *
        *  @param[out] tmpFunctions holds all non-constant constraints (and objective(s))
        *  @param[in] tmpDAGVars holds all DAG variables
        */
    void _classify_objective_and_constraints(std::vector<mc::FFVar> &tmpFunctions, const std::vector<mc::FFVar> &tmpDAGVars);

    /**
        *  @brief Ensures that the objective function stored in the _modelOutput is valid.
        *         In particular, if _modelOutput is an empty vector, a constant will be used as objective function.
        *         If the objective function is a constant, this functions makes sure it is still correctly associated with the DAG.
        *
        *  @param[in] dummyVariable is a valid optimization variable that is used to ensure that a potential constant objective is associated to the correct DAG
        */
    void _ensure_valid_objective_function_using_dummy_variable(const mc::FFVar &dummyVariable);

#ifdef HAVE_GROWING_DATASETS
    /**
		*  @brief Ensures that constant objective_per_data is not removed
		*
		*  @param[in] dummyVariable is a valid optimization variable that is used to ensure that a potential constant objective is associated to the correct DAG
		*/
    void _ensure_valid_objective_per_data_function_using_dummy_variable(const mc::FFVar &dummyVariable);
#endif    // HAVE_GROWING_DATASETS

    /**
        *  @brief Checks if the constraints are non-zero (constant) after the DAG has been constructed (this may happen if some FFVars are equal).
        *         Fills tmpDAGFunctions and tmpDAGoutputFunctions.
        *
        *  @param[in] tmpDAGVars holds all DAG variables
        *  @param[in,out] tmpDAGFunctions holds all DAG functions (no additional outputs!)
        *  @param[in,out] tmpDAGoutputFunctions holds all DAG additional outputs
        */
    bool _check_for_hidden_zero_constraints(const std::vector<mc::FFVar> &tmpDAGVars, std::vector<mc::FFVar> &tmpDAGFunctions, std::vector<mc::FFVar> &tmpDAGoutputFunctions);

#ifdef HAVE_GROWING_DATASETS
    /**
        *  @brief Initializes objective from objective_per_data and saves the DAG function of each entry of objective_per_data
        */
    void _initialize_objective_from_objective_per_data();

    /**
        *  @brief Initializes full dataset (= largest set) and initial reduced dataset (= smallest set)
        */
    void _initialize_dataset();

    /**
        *  @brief Auxiliary function for getting random initial dataset
        *
        *  @param[in] ndataInit is the size of the dataset to be sampled
        *  @param[in,out] dataset holds the generated dataset
        */
    void _sample_initial_dataset(const int ndataInit, std::set<unsigned int> &dataset);

    /**
        * @brief Function for reading user-given absolute sizing of datasets into _datasets vector
        */
    void read_sizing_of_datasets_from_file();
#endif

    /**
        *  @brief Modifies the lower bound DAG _DAGlbd by adding auxiliary optimization variables for intermediate factors occuring multiple times.
        */
    void _add_auxiliary_variables_to_lbd_dag();

    /**
        *  @brief Initializes subsolvers and internal solution variables for the solution of an LP, MIP, QP or MIQP
        */
    void _initialize_solve();

    /**
        *  @brief Conducts feasibility-based bound tightening at the root node
        */
    void _root_obbt_feasibility();

    /**
        *  @brief Conducts feasibility- and optimality-based bound tightening at the root node
        */
    void _root_obbt_feasibility_optimality();

    /**
        *  @brief Conducts feasibility- and optimality-based bound tightening at the root node
        */
    void _root_constraint_propagation();

    /**
        *  @brief Conducts multistart local search at the root node
        */
    void _root_multistart();

    /**
        *  @brief Uses mc::FFDep properties and the DAG to obtain information on the structure of the underlying problem
        */
    void _recognize_structure();

    /**
        *  @brief Uses mc::FFDep properties and the DAG to obtain information on the properties of constraints and variables
        */
    void _set_constraint_and_variable_properties();

    /**
        * @name MAiNGO printing functions
        */
    /**@{*/
    /**
        *  @brief Prints problem & solution statistics on screen
        */
    void _print_statistics();

    /**
        *  @brief Prints solution on screen
        */
    void _print_solution();

    /**
        *  @brief Prints solution time on screen
        */
    void _print_time();

    /**
        *  @brief Prints additional model output on screen
        */
    void _print_additional_output();

#ifdef HAVE_GROWING_DATASETS
    /**
        *  @brief Prints statistics of post-processing for heuristic B&B algorithm with growing datasets on screen
        */
    void _print_statistics_postprocessing();
#endif    // HAVE_GROWING_DATASETS
    /**@}*/

    /**
        * @name MAiNGO file writing functions
        */
    /**@{*/
    /**
        *  @brief Writes logging and csv information to disk
        */
    void _write_files();

    /**
        *  @brief Writes logging and csv information to disk when an error occurs
        *  @param[in] errorMessage is an error message to be appended
        */
    void _write_files_error(const std::string &errorMessage);

    /**
        *  @brief Write csv summaries to disk
        */
    void _write_solution_and_statistics_csv();

    /**
        *  @brief Write json summaries to disk
        */
    void _write_json_file();

    /**
        *  @brief Write res file to disk containing non-standard model information such as, e.g., residuals
        *         It will be only written if the problem has been solved successfully
        */
    void _write_result_file();
    /**@}*/

    /**
        *  @brief Checks whether the current incumbent satisfies relaxation only constraints and gives a warning if not
        *
        *  @param[in] solutionPoint is the current incumbent which is to be checked
        *  @param[in,out] str is a string which is used to write the warning into, it will be modified such that you can add whitespace to it before passing it to this function
        *  @param[in] whitespaces should be a string holding only whitespaces. This is used for a nicer output
        *
        *  @return returns true if the point is feasible w.r.t. relaxation only constraints and false otherwise
        */
    bool _check_feasibility_of_relaxation_only_constraints(const std::vector<double> &solutionPoint, std::string &str, const std::string &whitespaces);

    /**
        * @name MAiNGO to other language functions
        */
    /**@{*/
    /**
        *  @brief Writes MAiNGO problem to GAMS file.
        *
        *  @param[in] gamsFileName is the file name. If it is empty, the default name "MAiNGO_GAMS_file.gms" will be used instead.
        *  @param[in] solverName is the solver name. If it is empty, the default solver SCIP will be called in the gams file.
        *  @param[in] writeRelaxationOnly if true then relaxation-only equalities and inequalities will be written into the GAMS file as well
        */
    void _write_gams_file(const std::string gamsFileName, const std::string solverName = "SCIP", const bool writeRelaxationOnly = false);

    /**
        * @brief Function writing variables, variable bounds and a initial point in the gams file
        *
        * @param[in] gamsFile is an open gams file
        */
    void _write_gams_variables(std::ofstream &gamsFile);

    /**
        * @brief Function writing functions into the gams file
        *
        * @param[in] gamsFile is an open gams file
        * @param[in] writeRelaxationOnly if true then relaxation-only equalities and inequalities will be written into the gams file as well.
        */
    void _write_gams_functions(std::ofstream &gamsFile, bool writeRelaxationOnly);

    /**
        * @brief Function writing options and model information into gams file
        *
        * @param[in] gamsFile is an open gams file
        * @param[in] solverName is the name of the solver called in the gams file. Default is SCIP
        */
    void _write_gams_options(std::ofstream &gamsFile, std::string solverName = "SCIP");

    /**
        * @brief Function for adding linebreaks in gams string. Older GAMS versions allow only for 40000 characters in one line.
        *
        * @param[in] str is the string where linebreaks shall be added
        */
    void _add_linebreaks_to_gams_string(std::string &str);

    /**
        *  @brief Writes MAiNGO problem to ALE file.
        *
        *  @param[in] aleFileName is the file name. If it is empty, the default name "MAiNGO_ALE_file.txt" will be used instead.
        *  @param[in] solverName is the solver name. If it is empty, the default solver SCIP will be called in the gams file.
        *  @param[in] writeRelaxationOnly if true then relaxation-only equalities and inequalities will be written into the ALE file as well
        */
    void _write_ale_file(const std::string aleFileName, const std::string solverName = "SCIP", const bool writeRelaxationOnly = false);

    /**
        * @brief Function writing variables, variable bounds and a initial point in the ale file
        *
        * @param[in] aleFile is an open ale file
        */
    void _write_ale_variables(std::ofstream &aleFile);

    /**
        * @brief Function writing functions into the ale file
        *
        * @param[in] aleFile is an open ale file
        * @param[in] writeRelaxationOnly if true then relaxation-only equalities and inequalities will be written into the ALE file as well.
        */
    void _write_ale_functions(std::ofstream &aleFile, bool writeRelaxationOnly);

    /**
        * @brief Function writing options and model information into ale file
        *
        * @param[in] aleFile is an open ale file
        * @param[in] solverName is the name of the solver called in the gams file. Default is SCIP
        */
    void _write_ale_options(std::ofstream &aleFile, std::string solverName = "SCIP");

    /**
        * @brief Write MAiNGO header for a different modeling language
        *
        * @param[in] writingLanguage is the desired modeling language
        * @param[in,out] file is the file to be written to
        */
    void _print_MAiNGO_header_for_other_modeling_language(const WRITING_LANGUAGE writingLanguage, std::ofstream &file);
    /**@}*/

    /**
        * @brief Write MAiNGO header
        */
    void _print_MAiNGO_header();

    /**
        * @brief Prints message with beautiful '*' box
        *
        * @param[in] message to be printed
        */
    void _print_message(const std::string &message);

    /**
        * @brief Function for writing the pareto front to MAiNGO_epsilon_constraint_objective_values.csv and the corresponding solution points to MAiNGO_epsilon_constraint_solution_points.csv
        *
        * @param[in] objectiveValues holds the objective value vectors
        * @param[in] solutionPoints holds the corresponding solution points
        */
    void _write_epsilon_constraint_result(const std::vector<std::vector<double>> &objectiveValues, const std::vector<std::vector<double>> &solutionPoints);

    /**
        *  @brief Function telling whether a point is feasible or not and returning values of the set model of the objective and all constraints at a point.
        *         The ordering of the vector containing the values of the objective and constraints is:
        *         vector[0]: objective
        *         vector[1 to (1+ineq)]: inequalities ( + constant inequalities )
        *         vector[(1+ineq) to (1+ineq+eq)]: equalities ( + constant equalities )
        *         vector[(1+ineq+eq) to (1+ineq+eq+ineqRelOnly)]: relaxation only inequalities ( + constant rel only inequalities )
        *         vector[(1+ineq+eq+ineqRelOnly) to (1+ineq+eq+ineqRelOnly+eqRelOnly)]: relaxation only equalities ( + constant rel only equalities )
        *         vector[(1+ineq+eq+ineqRelOnly+eqRelOnly) to (1+ineq+eq+ineqRelOnly+eqRelOnly+ineqSquash)]: squash inequalities ( + constant squash inequalities )
        *
        *  @param[in] point is the point to be evaluated
        *  @return returns a tuple consisting of a vector containing the objective value and all constraint residuas, as well as a bool indicating whether the point is feasible or not
        */
    std::pair<std::vector<double>, bool> _evaluate_model_at_point(const std::vector<double> &point);

    /**
        *  @brief Function returning values of the additional outputs of the set model at a point
        *
        *  @param[in] point is the point to be evaluated
        */
    std::vector<std::pair<std::string, double>> _evaluate_additional_outputs_at_point(const std::vector<double> &point);

    /**
        * @name Internal variables for storing information on the problem
        */
    /**@{*/
    mc::FFGraph _DAG;                                                    /*!< the actual DAG */
    std::vector<mc::FFVar> _DAGvars;                                     /*!< DAG variables */
    std::vector<mc::FFVar> _DAGfunctions;                                /*!< list of all non-constant functions in the DAG except for additional output */
    std::vector<mc::FFVar> _DAGoutputFunctions;                          /*!< list of all constant functions needed for additional output computation */
    std::vector<mc::FFVar> _resultVars;                                  /*!< vector holding evaluated FFVar Objects to not lose pointers */
    std::vector<OptimizationVariable> _originalVariables;                /*!< vector holding the original user-defined optimization variables (initial bounds, variable type, name, branching priority) */
    std::vector<OptimizationVariable *> _infeasibleVariables;            /*!< vector containing pointers to variables in _originalVariables with empty host set */
    std::vector<OptimizationVariable> _variables;                        /*!< vector holding the optimization variables participating in the problem (initial bounds, variable type, name, branching priority) */
    std::vector<bool> _variableIsLinear;                                 /*!< vector storing which variables occur only linearly in the problem */
    std::vector<bool> _removedVariables;                                 /*!< vector holding the information on which variable has been removed from the problem */
    std::vector<std::string> _uniqueNamesOriginal;                       /*!< auxiliary needed for parsing MAiNGO to a different modeling language since in most cases unique variable names are required */
    std::vector<std::string> _uniqueNames;                               /*!< auxiliary needed for parsing MAiNGO to a different modeling language since in most cases unique variable names are required. It is holding the not removed variables */
    std::vector<double> _initialPointOriginal;                           /*!< vector holding the original initial point */
    std::vector<double> _initialPoint;                                   /*!< vector holding the initial point */
    unsigned _nvarOriginal;                                              /*!< number of original user-defined optimization variables */
    unsigned _nvarOriginalContinuous;                                    /*!< number of original user-defined continuous optimization variables */
    unsigned _nvarOriginalBinary;                                        /*!< number of original user-defined binary optimization variables */
    unsigned _nvarOriginalInteger;                                       /*!< number of original user-defined integer optimization variables */
    unsigned _nvar;                                                      /*!< number of not-removed optimization variables participating in the problem */
    unsigned _nobj;                                                      /*!< number of objective functions */
    unsigned _nineq;                                                     /*!< number of non-constant inequalities */
    unsigned _neq;                                                       /*!< number of non-constant equalities */
    unsigned _nineqRelaxationOnly;                                       /*!< number of non-constant relaxation only inequalities */
    unsigned _neqRelaxationOnly;                                         /*!< number of non-constant relaxation only equalities */
    unsigned _nineqSquash;                                               /*!< number of non-constant inequalities used when the squash_node function is applied in the model */
    unsigned _noutputVariables;                                          /*!< number of non-constant output variables */
    unsigned _nconstantIneq;                                             /*!< number of constant inequalities */
    unsigned _nconstantEq;                                               /*!< number of constant equalities */
    unsigned _nconstantIneqRelOnly;                                      /*!< number of constant relaxation only inequalities */
    unsigned _nconstantEqRelOnly;                                        /*!< number of constant relaxation only equalities */
    unsigned _nconstantIneqSquash;                                       /*!< number of constant inequalities used when the squash_node function is applied in the model */
    unsigned _ndata;                                                     /*!< number of data points defined by objective_per_data (only larger 0 when using growing datasets) */
    unsigned _nconstantOutputVariables;                                  /*!< number of constant output variables */
    std::vector<std::string> _outputNames;                               /*!< strings for output variables */
    std::shared_ptr<MAiNGOmodel> _myFFVARmodel;                          /*!< pointer to a MAiNGOmodel object which will be evaluated with mc::FFVar variables */
    std::shared_ptr<maingo::TwoStageModel> _myTwoStageFFVARmodel;        /*!< pointer to a TwoStageModel object which will be evaluated with mc::FFVar variables */
    EvaluationContainer _modelOutput;                                    /*!< object holding the actual modelOutput in mc::FFVar, it is needed to not lose information on pointers */
    bool _modelSpecified;                                                /*!< flag storing whether a model has been successfully specified */
    bool _DAGconstructed;                                                /*!< flag storing whether the DAG has already been constructed */
    bool _variablesFeasible;                                             /*!< flag indicating whether the variable bounds define a non-empty set */
    bool _constantConstraintsFeasible;                                   /*!< flag indicating whether the constant constraints are feasible */
    bool _feasibilityProblem;                                            /*!< flag indicating whether the current problem is a feasibility problem, i.e., no objective has been specified */
    std::shared_ptr<std::vector<Constraint>> _originalConstraints;       /*!< vector holding all constraint (constant and non-constant) as they were read in by the MAiNGOModel evaluate() function. This is used when printing to other language */
    std::shared_ptr<std::vector<Constraint>> _constantConstraints;       /*!< vector holding all constant constraints. This is used for convenient printing and writing of output */
    std::shared_ptr<std::vector<Constraint>> _nonconstantConstraints;    /*!< vector holding all non-constant constraints. The pointer to this vector is provided to the underlying LBD wrapper to ease work with constraints. */
    std::shared_ptr<std::vector<Constraint>> _nonconstantConstraintsUBP; /*!< vector holding all non-constant constraints for the UBS solver. This vector has only obj, ineq, squash ineq and eq (in this order) and is passed to the UBD wrappers. */
    std::shared_ptr<std::vector<Constraint>> _constantOutputs;           /*!< vector holding all constant outputs */
    std::shared_ptr<std::vector<Constraint>> _nonconstantOutputs;        /*!< vector holding all non-constant outputs */
#ifdef HAVE_GROWING_DATASETS
    std::shared_ptr<std::vector<unsigned int>> _datasets;                /*!< pointer to a vector containing the size of all available datasets */
    std::shared_ptr<std::set<unsigned int>> _datasetResampled;           /*!< pointer to resampled initial dataset which contains indices of data points. Note: first data point has index 0 */
#endif    // HAVE_GROWING_MAiNGO
    /**@}*/

    /**
        * @name Internal variables for storing information when auxiliary variables shall be added to the DAG
        */
    /**@{*/
    mc::FFGraph _DAGlbd;                             /*!< DAG used for the lower bounding problem when auxiliary variables have been added */
    std::vector<mc::FFVar> _DAGvarsLbd;              /*!< DAG variables for the lower bounding problem when auxiliary variables have been added */
    std::vector<mc::FFVar> _DAGfunctionsLbd;         /*!< list of all functions in the DAG except for additional output for the lower bounding problem when auxiliary variables have been added */
    std::vector<mc::FFVar> _DAGoutputFunctionsLbd;   /*!< list of all functions needed for additional output computation for the lower bounding problem when auxiliary variables have been added */
    std::vector<OptimizationVariable> _variablesLbd; /*!< vector holding the optimization variables participating in the problem and auxiliary variables (initial bounds, variable type, name, branching priority) */
    unsigned _nvarLbd;                               /*!< number of not-removed optimization variables participating in the problem + number of auxiliary variables added */
    unsigned _nauxiliaryRelOnlyEqs;                  /*!< number of relaxation only equalities introduced for auxiliary variables */
                                                     /**@}*/

    /**
        * @name Auxiliaries variables for storing information on the optimization
        */
    /**@{*/
    std::vector<double> _solutionPoint;      /*!< vector holding the solution point */
    double _solutionValue;                   /*!< double holding the solution value */
    double _preprocessTime;                  /*!< double holding the solution time in CPU s for pre-processing only */
    double _preprocessTimeWallClock;         /*!< double holding the solution time in wall clock s for pre-processing only */
    double _solutionTime;                    /*!< double holding the solution time in CPU s */
    double _solutionTimeWallClock;           /*!< double holding the solution time in wall clock s */
    double _babTime;                         /*!< double holding the solution time in CPU s for B&B only */
    double _babTimeWallClock;                /*!< double holding the solution time in wall clock s for B&B only */
    double _outputTime;                      /*!< double holding the time in CPU s for final output only */
    double _outputTimeWallClock;             /*!< double holding the time in wall clock s for final output only */
    RETCODE _maingoStatus;                   /*!< flag storing the return status of MAiNGO */
    PROBLEM_STRUCTURE _problemStructure;     /*!< flag storing the problem structure */
    TIGHTENING_RETCODE _rootObbtStatus;      /*!< flag indicating whether optimization-based bound tightening at the root node found problem to be infeasible */
    TIGHTENING_RETCODE _rootConPropStatus;   /*!< flag indicating whether constrained propagation at the root node found problem to be infeasible */
    SUBSOLVER_RETCODE _rootMultistartStatus; /*!< flag indicating whether a feasible point was found during multistart at root node */
    SUBSOLVER_RETCODE _miqpStatus;           /*!< flag indicating whether CPLEX found a problem classified as LP, QP, MIP, or MIQP as infeasible or feasible */
    babBase::BabNode _rootNode;              /*!< root node of the branch-and-bound problem. Can be modified during pre-processing */
    babBase::enums::BAB_RETCODE _babStatus;  /*!< flag indicating the return status of the branch-and-bound problem  */
    /**@}*/

    /**
        * @name LowerBoundingSolver, UpperBoundingSolver and the B&B solver
        */
    /**@{*/
    std::shared_ptr<lbp::LowerBoundingSolver> _myLBS; /*!< pointer to lower bounding solver */
#if defined(MAiNGO_DEBUG_MODE) && defined(HAVE_GROWING_DATASETS)
    std::shared_ptr<lbp::LowerBoundingSolver> _myLBSFull; /*!< pointer to lower bounding solver using full dataset only */
#endif
    std::shared_ptr<ubp::UpperBoundingSolver> _myUBSPre; /*!< pointer to upper bounding solver to be used during pre-processing */
    std::shared_ptr<ubp::UpperBoundingSolver> _myUBSBab; /*!< pointer to upper bounding solver to be used in B&B*/
    std::shared_ptr<bab::BranchAndBound> _myBaB;         /*!< pointer to B&B solver */
    /**@}*/

    /**
        * @name Settings
        */
    /**@{*/
    std::shared_ptr<Settings> _maingoSettings = std::make_shared<Settings>(); /*!< object storing settings, may change during solution */
    Settings _maingoOriginalSettings;                                         /*!< object storing original settings */

    /**
        * @name Communication
        */
    /**@{*/
    std::istream* _inputStream             = &std::cin;                                 /*!< stream from which user input may be read during solution */
    std::shared_ptr<Logger> _logger        = std::make_shared<Logger>(_maingoSettings); /*!< object taking care of printing and saving information to logs */
    std::string _jsonFileName              = "statisticsAndSolution.json"; /*!< name of the json file into which information about the problem and solution may be written */
    std::string _babFileName               = "";                           /*!< name of the dot file that contains the structure of the branch and bound tree. An empty sting (default) disables writing this file. */
    std::string _resultFileName            = "MAiNGOresult.txt";           /*!< name of the text file into which the results (solution point, constraints residuals etc.) may be written */
    std::string _csvSolutionStatisticsName = "statisticsAndSolution.csv";  /*!< name of the csv file into which the solution as well as statistics may be written */
    /**@}*/

    /**
        * @name Auxiliaries variables for storing output and logging information
        */
    /**@{*/
    std::vector<double> _objectivesAtRoot;          /*!< contains the objective values of the new incumbents found at the root node */
    std::vector<SUBSOLVER_RETCODE> _feasibleAtRoot; /*!< contains information about which local optimization at the root node yielded a feasible point */
    bool _initialPointFeasible;                     /*!< whether or not the user-specified initial point was found to be feasible */
    bool _inMAiNGOsolve = false;                    /*!< flag used in MAiNGO to other language writing denoting whether the function is called from a MAiNGO solve or not */
                                                    /**@}*/

#ifdef HAVE_MAiNGO_MPI
    /**
        * @name Auxiliary variables for MPI communication
        */
    /**@{*/
    int _rank;   /*!< mpi rank of current process */
    int _nProcs; /*!< number of processes used in current mpi run */
    /**@}*/
#endif

};    // end of class MAiNGO


}    // end of namespace maingo
