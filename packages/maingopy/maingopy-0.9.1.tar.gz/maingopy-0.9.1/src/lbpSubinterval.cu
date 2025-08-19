
#include "lbpSubinterval.h"
#include "version.h"

#include "subinterval_arithmetic_settings.cuh"
#include "dagConversion.cuh"

using namespace maingo;
using namespace lbp;


/////////////////////////////////////////////////////////////////////////
// constructor for the lower bounding solver
LbpSubinterval::LbpSubinterval(mc::FFGraph& DAG, const std::vector<mc::FFVar>& DAGvars, const std::vector<mc::FFVar>& DAGfunctions, const std::vector<babBase::OptimizationVariable>& variables,
    const std::vector<bool>& variableIsLinear, const unsigned nineqIn, const unsigned neqIn, const unsigned nineqRelaxationOnlyIn, const unsigned neqRelaxationOnlyIn, const unsigned nineqSquashIn,
    std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, std::shared_ptr<std::vector<Constraint>> constraintPropertiesIn) :
    LowerBoundingSolver(DAG, DAGvars, DAGfunctions, variables, variableIsLinear, nineqIn, neqIn, nineqRelaxationOnlyIn, neqRelaxationOnlyIn, nineqSquashIn, settingsIn, loggerIn, constraintPropertiesIn)
{
    cudaDeviceProp deviceProp;
    int dev = 0;

    cudaGetDeviceProperties(&deviceProp, dev);

    // We only need the Interval stuff if we want to use natural interval extensions
    if (_maingoSettings->LBP_subgradientIntervals) {
        // All set in LowerBoundingSolver constructor
    }
    _Iarray.clear();
    _Iarray.resize(_DAGobj->subgraph.l_op.size());
    _Intervals.clear();
    _Intervals.resize(_nvar);
    _resultInterval.clear();
    _resultInterval.resize(DAGfunctions.size());

    int inputDim = _DAGobj->DAG.nvar();
    int numSubintervals = _maingoSettings->Num_subdomains;
    int intervalArithmetic = _maingoSettings->Interval_arithmetic;
    int branchingStrategy = _maingoSettings->Subinterval_branch_strategy;
    int numThreadsPerBlock = _maingoSettings->Threads_per_block;
    int centerStrategy = _maingoSettings->Center_strategy;
    int minBranchingPerDim = _maingoSettings->MIN_branching_per_dim;
    
    // Creating objects for managing the settings and the memory of the GPU lower bounding
    _subintervalArithmeticSettings = std::make_shared<SIA::subinterval_arithmetic_settings>(inputDim, numSubintervals, intervalArithmetic, branchingStrategy, numThreadsPerBlock, centerStrategy, minBranchingPerDim);
    numSubintervals = _subintervalArithmeticSettings->get_num_subintervals();
    int numBranchMoreDims = _subintervalArithmeticSettings->get_num_branch_more_dims();
    bool adaptiveBranching = _subintervalArithmeticSettings->get_adaptive_branching_flag();  
    _subintervalArithmeticMemory = std::make_shared <SIA::subinterval_arithmetic_memory<I_gpu>>(inputDim, numSubintervals, intervalArithmetic, _DAGobj, numBranchMoreDims, adaptiveBranching);

    _dagVarValues.clear(); 
    _dagVarValues.resize(_subintervalArithmeticMemory->dagInfo.numDagVars);

    cudaGraphNode_t errorNode;
    // If use CENTERED FORM, create the graph for handling center values.
    if (intervalArithmetic == SIA::_CENTERED_FORM)
        construct_cuda_graph_for_centers(*_subintervalArithmeticMemory, *_subintervalArithmeticSettings);
    construct_cuda_graph(*_subintervalArithmeticMemory, *_subintervalArithmeticSettings); 
    CUDA_CHECK(cudaGraphInstantiate(&_subintervalArithmeticMemory->cuDagExec, _subintervalArithmeticMemory->cuDag, &errorNode, nullptr, 0));
    CUDA_CHECK(cudaDeviceSynchronize());

#ifdef LP__OPTIMALITY_CHECK
    // Not needed in this solver
#endif
}

/////////////////////////////////////////////////////////////////////////////////////////////
// function called by the B&B in preprocessing in order to check the need for specific options, currently for subgradient intervals & CPLEX no large values
void
LbpSubinterval::activate_more_scaling()
{

    // Not needed in the interval solver
}


/////////////////////////////////////////////////////////////////////////
// function for setting the bounds of variables
void
LbpSubinterval::_set_variable_bounds(const std::vector<double>& lowerVarBounds, const std::vector<double>& upperVarBounds)
{

    _lowerVarBounds = lowerVarBounds;
    _upperVarBounds = upperVarBounds;

    for (unsigned int i = 0; i < _nvar; i++) {
        _Intervals[i] = I(lowerVarBounds[i], upperVarBounds[i]);
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////
// constructs the desired linearization point and calls the function for updating linearizations and modifying the coefficients of the optimization problem
LINEARIZATION_RETCODE
LbpSubinterval::_update_LP(const babBase::BabNode& currentNode)
{


    // Set bounds for current node
    _set_variable_bounds(currentNode.get_lower_bounds(), currentNode.get_upper_bounds());

    // Copy input domain of current node to GPU
    _subintervalArithmeticMemory->copy_inputDomain_to_GPU(_Intervals.data());

    if (_subintervalArithmeticSettings->get_adaptive_branching_flag())
        _subintervalArithmeticMemory->get_largest_dims_for_adaptive_branching();
    
    // Start calcuation of lower bounds for subintervals with parallel GPU implementation
    SIA::perform_subinterval_arithmetic(*_subintervalArithmeticMemory, *_subintervalArithmeticSettings);    

    // Wait for the GPU to finish the GPU lower bounding & copy results of GPU lower bounding back to CPU
    _subintervalArithmeticMemory->copy_results_to_CPU();

    return LINEARIZATION_UNKNOWN;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an objective of the linear program
void
LbpSubinterval::_update_LP_obj(const MC& resultRelaxation, const std::vector<double>& linearizationPoint, const std::vector<double>& lowerVarBounds, const std::vector<double>& upperVarBounds, unsigned const& iLin, unsigned const& iObj)
{

    // Not needed in the interval solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an inequality of the linear program
void
LbpSubinterval::_update_LP_ineq(const MC& resultRelaxation, const std::vector<double>& linearizationPoint, const std::vector<double>& lowerVarBounds, const std::vector<double>& upperVarBounds, unsigned const& iLin, unsigned const& iIneq)
{

    // Not needed in the interval solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an equality of the linear program
void
LbpSubinterval::_update_LP_eq(const MC& resultRelaxationCv, const MC& resultRelaxationCc, const std::vector<double>& linearizationPoint, const std::vector<double>& lowerVarBounds, const std::vector<double>& upperVarBounds, unsigned const& iLin, unsigned const& iEq)
{

    // Not needed in the interval solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates a relaxation only inequality of the linear program
void
LbpSubinterval::_update_LP_ineqRelaxationOnly(const MC& resultRelaxation, const std::vector<double>& linearizationPoint, const std::vector<double>& lowerVarBounds, const std::vector<double>& upperVarBounds, unsigned const& iLin, unsigned const& iIneqRelaxationOnly)
{

    // Not needed in the interval solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates an equality of the linear program
void
LbpSubinterval::_update_LP_eqRelaxationOnly(const MC& resultRelaxationCv, const MC& resultRelaxationCc, const std::vector<double>& linearizationPoint, const std::vector<double>& lowerVarBounds, const std::vector<double>& upperVarBounds, unsigned const& iLin, unsigned const& iEqRelaxationOnly)
{

    // Not needed in the interval solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// updates a squash inequality of the linear program
void
LbpSubinterval::_update_LP_ineq_squash(const MC& resultRelaxation, const std::vector<double>& linearizationPoint, const std::vector<double>& lowerVarBounds, const std::vector<double>& upperVarBounds, unsigned const& iLin, unsigned const& iIneqSquash)
{

    // Not needed in the interval solver
}


/////////////////////////////////////////////////////////////////////////////////////////////
// solves the current linear program
LP_RETCODE
LbpSubinterval::_solve_LP(const babBase::BabNode& currentNode)
{

    _solutionPoint.resize(_nvar);
    // In an interval solver, we don't have multipliers
    _multipliers.clear();

    for (unsigned i = 0; i < _nvar; i++) {
        // In an interval solver, we don't care about the solution point so just set it as the middle point
        _solutionPoint[i] = (_lowerVarBounds[i] + _upperVarBounds[i]) / 2.;
    }

    double constraintValueL, constraintValueU;
    // We need to use the correct bounds
    _objectiveValue = mc::Op<I>::l(_subintervalArithmeticMemory->result->get_bounds_of_obj(0));

    // Next, check feasibility
    for (size_t i = 0; i < (*_constraintProperties).size(); i++) {
        // We have to use the correct bounds            
        constraintValueL = mc::Op<I>::l(_subintervalArithmeticMemory->result->get_bounds(i));    // Interval lower bound
        constraintValueU = mc::Op<I>::u(_subintervalArithmeticMemory->result->get_bounds(i));    // Interval upper bound
        
        switch ((*_constraintProperties)[i].type) {
        case INEQ:
        case INEQ_REL_ONLY:
            if (constraintValueL > _maingoSettings->deltaIneq) {
                _LPstatus = LP_INFEASIBLE;
                return _LPstatus;
            }
            break;
        case EQ:
        case EQ_REL_ONLY:
        case AUX_EQ_REL_ONLY:
            if (constraintValueL > _maingoSettings->deltaEq || constraintValueU < -_maingoSettings->deltaEq) {
                _LPstatus = LP_INFEASIBLE;
                return _LPstatus;
            }
            break;
        case INEQ_SQUASH:
            if (constraintValueL > 0) {
                _LPstatus = LP_INFEASIBLE;
                return _LPstatus;
            }
            break;
        case OBJ:
        default:
            break;
        }
    }
    _LPstatus = LP_OPTIMAL;
    return _LPstatus;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// check need for options in preprocessing
void
LbpSubinterval::_turn_off_specific_options()
{

    if (_maingoSettings->LBP_solver != LBP_SOLVER_SUBDOMAIN) {
        _logger->print_message("        Warning: Function for turning off specific options not implemented. Not changing any settings. Procedding...\n", VERB_NORMAL, LBP_VERBOSITY);
    }
    else {
        if (_maingoSettings->LBP_linPoints != LINP_MID) {
            _logger->print_message("        The option LBP_linPoints has to be 0 when using the interval-based solver (LBP_solver = 1). Setting it to 0.\n", VERB_NORMAL, LBP_VERBOSITY);
            _maingoSettings->LBP_linPoints = LINP_MID;    // Note that this already has been used in the constructor!
        }
        if (_maingoSettings->PRE_obbtMaxRounds > 0) {
            _logger->print_message("        The option PRE_obbtMaxRounds has to be 0 when using the interval-based solver (LBP_solver = 1). Setting it to 0.\n", VERB_NORMAL, LBP_VERBOSITY);
            _maingoSettings->PRE_obbtMaxRounds = 0;
        }
        if (_maingoSettings->BAB_alwaysSolveObbt) {
            _logger->print_message("        The option BAB_alwaysSolveObbt has to be 0 when using the interval-based solver (LBP_solver = 1). Setting it to 0.\n", VERB_NORMAL, LBP_VERBOSITY);
            _maingoSettings->BAB_alwaysSolveObbt = false;
        }
        if (_maingoSettings->BAB_probing) {
            _logger->print_message("        The option BAB_probing has to be 0 when using the interval-based solver (LBP_solver = 1). Setting it to 0.\n", VERB_NORMAL, LBP_VERBOSITY);
            _maingoSettings->BAB_probing = false;
        }
        if (_maingoSettings->BAB_dbbt) {
            _logger->print_message("        The option BAB_dbbt has to be 0 when using the interval-based solver (LBP_solver = 1). Setting it to 0.\n", VERB_NORMAL, LBP_VERBOSITY);
            _maingoSettings->BAB_dbbt = false;
        }
    }
}


#ifdef LP__OPTIMALITY_CHECK
/////////////////////////////////////////////////////////////////////////////////////////////
// infeasibility check
SUBSOLVER_RETCODE
LbpSubinterval::_check_infeasibility(const babBase::BabNode& currentNode)
{
    // We don't have a check in the interval solver
    return SUBSOLVER_INFEASIBLE;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// feasibility check
SUBSOLVER_RETCODE
LbpSubinterval::_check_feasibility(const std::vector<double>& solution)
{
    // We don't have a check in the interval solver
    return SUBSOLVER_FEASIBLE;
}


/////////////////////////////////////////////////////////////////////////////////////////////
// optimality check
SUBSOLVER_RETCODE
LbpSubinterval::_check_optimality(const babBase::BabNode& currentNode, const double newLBD, const std::vector<double>& solution, const double etaVal, const std::vector<double>& multipliers)
{
    // We don't have a check in the interval solver
    return SUBSOLVER_FEASIBLE;
}
#endif


#ifdef LP__WRITE_CHECK_FILES
/////////////////////////////////////////////////////////////////////////////////////////////
// write current LP to file
void
LbpInterval::_write_LP_to_file(std::string& fileName)
{

    std::string str;
    if (fileName.empty()) {
        str = "MAiNGO_LP_WRITE_CHECK_FILES.lp";
    }
    else {
        str = fileName + ".lp";
    }

    std::ofstream lpFile(str);

    lpFile << "\\ This file was generated by MAiNGO " << get_version() << "\n\n";

    lpFile << "Minimize\n";
    // Print objective
    lpFile << _DAGobj->resultRelaxation[0].l();
    lpFile << "\n Subject To \n";

    for (size_t i = 0; i < _constraintProperties->size(); i++) {
        unsigned index = (*_constraintProperties)[i].indexTypeNonconstant;
        switch ((*_constraintProperties)[i].type) {
        case OBJ:
            break;
        case INEQ:
            lpFile << "ineq" << index << ": " << _DAGobj->resultRelaxation[i].l() << " <= " << _maingoSettings->deltaIneq << "\n";
            break;
        case EQ:
            lpFile << "eqcv" << index << ": " << _DAGobj->resultRelaxation[i].l() << " <= " << _maingoSettings->deltaIneq << "\n";
            lpFile << "eqcc" << index << ": " << -_DAGobj->resultRelaxation[i].u() << " <= " << _maingoSettings->deltaIneq << "\n";
            break;
        case INEQ_REL_ONLY:
            lpFile << "ineqRelOnly" << index << ": " << _DAGobj->resultRelaxation[i].l() << " <= " << _maingoSettings->deltaIneq << "\n";
            break;
        case EQ_REL_ONLY:
        case AUX_EQ_REL_ONLY:
            lpFile << "eqcvRelOnly" << index << ": " << _DAGobj->resultRelaxation[i].l() << " <= " << _maingoSettings->deltaIneq << "\n";
            lpFile << "eqccRelOnly" << index << ": " << -_DAGobj->resultRelaxation[i].u() << " <= " << _maingoSettings->deltaIneq << "\n";
            break;
        case INEQ_SQUASH:
            lpFile << "ineqSquash" << index << ": " << _DAGobj->resultRelaxation[i].l() << " <= " << 0 << "\n";
            break;
        }
    }
    lpFile << "Bounds\n";
    // Write bounds
    for (unsigned i = 0; i < _nvar; i++) {
        lpFile << _lowerVarBounds[i] << " <= x" << i + 1 << " <= " << _upperVarBounds[i] << "\n";
    }
    lpFile << "End\n";
    lpFile.close();
}
#endif