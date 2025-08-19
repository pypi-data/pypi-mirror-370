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
#include "logger.h"
#include "mpiUtilities.h"
#ifdef HAVE_MAiNGO_MPI
#include "MAiNGOMpiException.h"
#endif

#include "babBrancher.h"
#include "siblingResults.h"

#include <cmath>
#include <map>
#include <memory>
#include <string>
#include <vector>
#include <array>


namespace maingo {


namespace lbp {
  class LowerBoundingSolver;
  struct LbpDualInfo;
}    // namespace lbp
namespace ubp {
  class UpperBoundingSolver;
}    // namespace ubp


/**
 *   @namespace maingo::bab
 *   @brief namespace holding everything related to the actual branch-and-bound algorithm
 */
namespace bab {


/**
 * @class BranchAndBound
 * @brief This class contains the main algorithm, including handling of pre-processing routines and managing the B&B tree as well as the respective sub-solvers
 *
 * The class BranchAndBound implements a basic branch-and-bound (BaB) solver with some simple features for range reduction.
 * These include optimization-based range reduction (OBBT; cf., e.g., Gleixner et al., J. Glob. Optim. 67 (2017) 731), which can be conducted multiple times at the root node, and also once at every
 * node of the BAB tree, as well as duality-based bounds tightening (DBBT) and probing (cf. Ryoo&Sahinidis, Comput. Chem. Eng. 19 (1995) 551).
 * It also contains a multi-start local search from randomly generated initial points at the root node. Lower and upper bounding are conducted by the respective lower and upper bounding solvers (LBS / UBS).
*/
class BranchAndBound : public babBase::FathomObserver {

  public:
    /**
     * @brief Constructor, stores information on problem and settings
     *
     * @param[in] variables is a vector containing the initial optimization variables defined in problem.h
     * @param[in] LBSIn is a pointer to the LowerBoundingSolver object
     * @param[in] UBSIn is a pointer to the UpperBoundingSolver object
     * @param[in] settingsIn is a pointer to an object containing the settings for the Branch-and-Bound solvers
     * @param[in] loggerIn is a pointer to the MAiNGO logger object
     * @param[in] nvarWOaux is the number of optimization variables without the additional auxiliary variables added by the LBP_addAuxiliaryVars option
     * @param[in] inputStream is the address of the input stream from which user input may be read during solution
     * @param[in] babFileName is the name of the file to which the B&B tree is written in dot format
     */
    BranchAndBound(const std::vector<babBase::OptimizationVariable> &variables, std::shared_ptr<lbp::LowerBoundingSolver> LBSIn, std::shared_ptr<ubp::UpperBoundingSolver> UBSIn,
                   std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, const unsigned nvarWOaux, std::istream *const inputStream = &std::cin, const std::string & babFileName = "");

    /**
     * @brief Main function to solve the optimization problem
     * @param[in] rootNodeIn Root node to start Branch&Bound on.
     * @param[in,out] solutionValue Objective value of best feasible point found (empty if no feasible point was found); Also used for communicating objective value of initial feasible point.
     * @param[in,out] solutionPoint Solution point, i.e., (one of) the point(s) at which the best objective value was found (empty if no feasible point was found); Also used for communicating initial feasible point.
     * @param[in] preprocessTime Is the CPU time spent in pre-processing before invoking this solve routine (needed for correct output of total CPU time during B&B)
     * @param[in] preprocessWallTime Is the wall time spent in pre-processing before invoking this solve routine (needed for correct output of total wall time during B&B)
     * @param[out] timePassed Is the CPU time spent in B&B (especially useful if time is >24h)
     * @param[out] wallTimePassed Is the wall time spent in B&B (especially useful if time is >24h)
     * @return Return code summarizing the solution status.
     */
    babBase::enums::BAB_RETCODE solve(babBase::BabNode &rootNodeIn, double &solutionValue, std::vector<double> &solutionPoint, const double preprocessTime, const double preprocessWallTime, double &timePassed, double &wallTimePassed);

#ifdef HAVE_GROWING_DATASETS
    /**
        * @brief Function for post-processing nodes in heuristic approach with growing datasets
        *
        * @param[in] finalUBD Is the objective value of the best feasible point found by the B&B algorithm
        */
    void postprocess(const double &finalUBD);
#endif    // HAVE_GROWING_DATASETS

    /**
     *  @brief Function returning the number of iterations
     */
    double get_iterations() { return _iterations; }

    /**
     *  @brief Function returning the maximum number of nodes in memory
     */
    double get_max_nodes_in_memory() { return _nNodesMaxInMemory; }

    /**
     *  @brief Function returning number of UBD problems solved
     */
    double get_UBP_count() { return _ubdcnt; }

    /**
     *  @brief Function returning number of LBD problems solved
     */
    double get_LBP_count() { return _lbdcnt; }

    /**
     *  @brief Function returning the final LBD
     */
    double get_final_LBD() { return _lbd; }

    /**
     *  @brief Function returning the final absolute gap
     */
    double get_final_abs_gap() { return _ubd - _lbd; }

    /**
     *  @brief Function returning the final relative gap
     */
    double get_final_rel_gap() { return ((_ubd == 0) ? (get_final_abs_gap()) : ((_ubd - _lbd) / std::fabs(_ubd))); }

    /**
     *  @brief Function returning the ID of the node where the incumbent was first found
     */
    double get_first_found() { return _firstFound; }

    /**
     *  @brief Function returning the number of nodes left after termination of B&B
     */
    double get_nodes_left() { return _nNodesLeft; }

#ifdef HAVE_GROWING_DATASETS
    /**
        *  @brief Function returning the number of nodes tracked for postprocessing the heuristic B&B algorithm with growing datasets
        */
    double get_nodes_tracked_for_postprocessing() { return _nNodesTrackedPost; }

    /**
        *  @brief Function returning the number of nodes processed in postprocessing of the heuristic B&B algorithm with growing datasets
        */
    double get_nodes_processed_in_postprocessing() { return _nNodesProcessedPost; }

    /**
        *  @brief Function returning the final lower bound after postprocessing the heuristic B&B algorithm with growing datasets
        */
    double get_lower_bound_after_postprocessing() { return _lbdPostpro; }

    /**
        *  @brief Function returning the CPU time spent for postprocessing the heuristic B&B algorithm with growing datasets
        */
    double get_time_for_postprocessing() { return _timePostpro; }

    /**
     * @brief Function for passing pointer of vector containing datasets to B&B
     *
     * @param[in] datasetsIn is a pointer to a vector containing the size of all available datasets
     */
    void pass_datasets_to_bab(const std::shared_ptr<std::vector<unsigned int>> datasetsIn)
    {
        _datasets = datasetsIn;
    }
  #ifdef MAiNGO_DEBUG_MODE
    /**
	 * @brief Function for passing pointer of LBS with full dataset to B&B
	 *
	 * @param[in] LBSFullIn is a pointer to an LBS object using the full dataset only
	 */
    void pass_LBSFull_to_bab(const std::shared_ptr<lbp::LowerBoundingSolver> LBSFullIn)
    {
        _LBSFull = LBSFullIn;
    }
  #endif
#endif    // HAVE_GROWING_DATASETS

    /**
     * @brief Setup the use of _two_stage_branching.
     * 
     * @param[in] Nx Number of first-stage variables.
     * @param[in] Ny Number of second-stage variables.
     * @param[in] w Vector of weights for the scenarios.
     * @param[in] solve_sibling_subproblems Callable for solving LBP subproblems of sibling nodes.
     * @param[in] alpha Strong branching score threshold.
     * @param[in] k_max Base 2 log of the maximum number of nodes generated during multi section branching.
     */
    void setup_two_stage_branching(
        unsigned Nx, unsigned Ny, const std::vector<double> &w,
        std::vector<double> &subproblemBounds,
        std::function<
            void(
                lbp::SiblingResults & siblingResults,
                double ubd,
                int obbtType
            )
        > solve_sibling_subproblems,
        double alpha,
        unsigned int k_max
    );

  private:
    /**
     * @enum _TERMINATION_TYPE
     * @brief Enum for representing different termination types in B&B
     */
    enum _TERMINATION_TYPE {
        _TERMINATED = 0,            /*!< termination condition has been reached and no worker is processing any nodes */
        _TERMINATED_WORKERS_ACTIVE, /*!< termination condition has been reached, but there are still nodes being processed by workers */
        _NOT_TERMINATED             /*!< termination condition has not been reached yet*/
    };

    /**
     * @brief Function processing the current node
     *
     * @param[in,out] currentNodeInOut  The node to be processed
     */
    std::tuple<bool, bool, int, int, double, std::vector<double>, bool, double, std::vector<double>> _process_node(babBase::BabNode &currentNodeInOut);

    /**
     * @brief Function to process sibling nodes obtained from second-stage branching.
     * 
     * @param[in] siblingResults The struct storing the results of the sibling iteration.
     */
    void _process_siblings(lbp::SiblingResults &siblingResults);

    /**
     * @brief Function for pre-processing the current node. Includes bound tightening and OBBT.
     *
     * @param[in,out] currentNodeInOut  The node to be processed
     * @return Flag indicating whether the node was proven to be infeasible
     */
    bool _preprocess_node(babBase::BabNode &currentNodeInOut);

    /**
     * @brief Function invoking the LBS to solve the lower bounding problem
     *
     * @param[in] currentNode  The node to be processed
     * @return Tuple consisting of flags for whether the node is infeasible and whether it is converged, the lower bound, the lower bounding solution point, and dual information for DBBT
     */
    std::tuple<bool, bool, double, std::vector<double>, lbp::LbpDualInfo> _solve_LBP(const babBase::BabNode &currentNode);

    /**
     * @brief Function invoking the UBS to solve the upper bounding problem
     *
     * @param[in] currentNode  The node to be processed
     * @param[in,out] ubpSolutionPoint  On input: initial point for local search. On output: solution point.
     * @param[in] currentLBD Lower bound of current Node. Needed for sanity check.
     * @return Tuple consisting of flags indicating whether a new feasible point has been found and whether the node converged, and the optimal objective value of the new point
     */
    std::tuple<bool, bool, double> _solve_UBP(const babBase::BabNode &currentNode, std::vector<double> &ubpSolutionPoint, const double currentLBD);

    /**
     * @brief Function for post-processing the current node. Includes bound DBBT and probing
     *
     * @param[in,out] currentNodeInOut  The node to be processed
     * @param[in] lbpSolutionPoint  Solution point of the lower bounding problem
     * @param[in] dualInfo is a struct containing information from the LP solved during LBP
     * @return Flag indicating whether the node has converged
     */
    bool _postprocess_node(babBase::BabNode &currentNodeInOut, const std::vector<double> &lbpSolutionPoint, const lbp::LbpDualInfo &dualInfo);

    /**
     * @brief Function for updating the incumbent and fathoming accordingly
     *
     * @param[in] solval is the value of the processed solution
     * @param[in] sol is the solution point
     * @param[in] currentNodeID is the ID of the new node holding the incumbent (it is used instead of directly giving the node to match the parallel implementation)
     */
    void _update_incumbent_and_fathom(const double solval, const std::vector<double> sol, const unsigned int currentNodeID);

    /**
     * @brief Function for updating the global lower bound
     */
    void _update_lowest_lbd();

#ifdef HAVE_GROWING_DATASETS
    /**
    * @brief Auxiliary function for calling augmentation rule CONST
    *
    * @param[in] depth is the depth of the node calling the augmentation rule
    * @param[out] boolean indicating whether to augment (true) or branch (false)
    */
    bool _call_augmentation_rule_const(const int depth);

    /**
    * @brief Auxiliary function for calling augmentation rule SCALING
    *
    * @param[in] indexDataset is the index of the the dataset of the node calling the augmentation rule
    * @param[in] redLBD is the reduced lower bound calculated when lower bounding the current node with the (potentially) reduced dataset
    * @param[out] boolean indicating whether to augment (true) or branch (false)
    */
    bool _call_augmentation_rule_scaling(const int indexDataset, const double redLBD);

    /**
    * @brief Function for evaluating solution point of lower bounding problem with validation set, i.e., out-of-sample evaluation
    *
    * @param[in] currentNode is the node to be processed
    * @param[in] lbpSolutionPoint is the solution point of the LBP of the current node
    * @param[in] currentLBD is the objective value of the LBP of the current node
    */
    double _evaluate_lower_bound_for_validation_set(const babBase::BabNode& currentNode, const std::vector<double>& lbpSolutionPoint, const double currentLBD);

    /**
    * @brief Function for calculating approximated lower bound as combination of reduced and out-of-sample lower bound
    *
    * @param[in] currentLBD is the objective value of the LBP of the current node
    * @param[in] oosLBD is the out-of-sample evaluation of the LBP with the validation dataset at the optimal lower bounding point
    * @param[in] indexDataset is the index of the dataset of the current node
    */
    double _calculate_combined_lower_bound(const double currentLBD, const double oosLBD, const unsigned int indexDataset);

    /**
    * @brief Auxiliary function for calling augmentation rule OOS
    *
    * @param[in] oosLBD is the out-of-sample evaluation of the LBP with the validation dataset at the optimal lower bounding point
    * @param[out] boolean indicating whether to augment (true) or branch (false)
    */
    bool _call_augmentation_rule_oos(const double oosLBD);

    /**
    * @brief Auxiliary function for calling augmentation rule COMBI
    *
    * @param[in] combiLBD is the combined lower bound given by a convex/linear combination of the reduced lower bound and the out-of-sample lower bound
    */
    bool _call_augmentation_rule_combi(const double combiLBD);

    /**
    * @brief Auxiliary function for calling augmentation rule TOL
    *
    * @param[in] redLBD is the reduced lower bound calculated when lower bounding the current node with the (potentially) reduced dataset
    * @param[in] combiLBD is the combined lower bound given by a convex/linear combination of the reduced lower bound and the out-of-sample lower bound
    */
    bool _call_augmentation_rule_tol(const double redLBD, const double combiLBD);

    /**
    * @brief Function which checks whether to augment the dataset
    *
    * @param[in] currentNode is the node to be processed
    * @param[in] lbpSolutionPoint is the solution point of the LBP of the current node
    * @param[in] redLBD is the reduced lower bound calculated when lower bounding the current node with the (potentially) reduced dataset
    * @param[in] oosLBD is the out-of-sample evaluation of the LBP with the validation dataset at the optimal lower bounding point
    * @param[in] combiLBD is the combined lower bound given by a convex/linear combination of the reduced lower bound and the out-of-sample lower bound
    */
    bool _check_whether_to_augment(const babBase::BabNode &currentNode, const std::vector<double> &lbpSolutionPoint, const double redLBD, const double oosLBD, const double combiLBD);

    /**
     * @brief Function for augmenting dataset of node
     *
     * @param[in] current index of dataset
     * @param[out] new index of dataset after augmentation
     */
    unsigned int _augment_dataset(babBase::BabNode &currentNode);
#endif    // HAVE_GROWING_DATASETS

    /**
     * @brief Function which checks whether it is necessary to activate scaling within the LBD solver. This is a heuristic approach, which does not affect any deterministic optimization assumptions
     */
    void _check_if_more_scaling_needed();

    /**
     * @brief Function for checking if the B&B algorithm terminated
     */
    _TERMINATION_TYPE _check_termination();

#ifdef HAVE_GROWING_DATASETS
    /**
        * @brief Function for checking if post-processing of heuristic approach terminated
        */
    _TERMINATION_TYPE _check_termination_postprocessing();
#endif     // HAVE_GROWING_DATASETS

    /**
     * @brief Function for printing the current progress on the screen and appending it to the internal log to be written to file later
     *
     * @param[in] currentNodeLBD is the lower bound for the current node
     * @param[in] currentNode is the current node
     */
    void _display_and_log_progress(const double currentNodeLBD, const babBase::BabNode &currentNode);

#if defined(MAiNGO_DEBUG_MODE) && defined(HAVE_GROWING_DATASETS)
    /**
	 * @brief Function for printing the current node to a separate log file
	 *
	 * @param[in] currentNode is the current node
	 * @param[in] currentNodeLbd is the lower bound calculated in the current node
	 * @param[in] currentNodeUbd is the upper bound calculated in the current node
	 * @param[in] lbpSolutionPoint is the solution point of the lower bound calculated und used in the current node
	 */
    void _log_nodes(const babBase::BabNode &currentNode, const double currentNodeLbd, const double currentNodeUbd, const std::vector<double> lbpSolutionPoint);
#endif

#ifdef HAVE_GROWING_DATASETS
    /**
        * @brief Function for printing post-processing information of one node
        *
        * @param[in] ID is the id of the node
        * @param[in] oldLBD is the lower bound of the node before post-processing
        * @param[in] newLBD is the lower bound of the node after post-processing
        */
    void _print_postprocessed_node(const int ID, const double oldLBD, const double newLBD);
#endif // HAVE_GROWING_DATASETS

    /**
     * @brief Function printing a termination message
     *
     * @param[in] message is a string holding the message to print
     */
    void _print_termination(std::string message);

    /**
        * @brief Function printing one node
        *
        * @param[in] theLBD is the lower bound of the node
        * @param[in] theNode is the node to be printed
        */
    void _print_one_node(const double theLBD, const babBase::BabNode &theNode);

#ifdef HAVE_MAiNGO_MPI
    /**
     * @name MPI management and communication functions of manager
     */
    /**@{*/
    /**
     * @brief Function for dealing with exceptions (informing workers etc.)
     *
     * @param[in] e is the exception to be handled
     */
    void _communicate_exception_and_throw(const maingo::MAiNGOMpiException &e);

    /**
     * @brief Auxiliary function for receiving solved problems from workers
     *
     * @param[out] node is the node corresponding to the solved problem
     * @param[out] sibling is the sibling node of the solved node
     * @param[out] siblingResults is the results from solving the sibling nodes
     * @param[out] lbd is the new lowerbound for the node
     * @param[out] lbdSolutionPoint is the solution point of the node
     * @param[out] lbdcnt is the number of lower bounding problems that were solved during solving the node
     * @param[out] ubdcnt is the number of upper bounding problems that were solved during solving the node
     * @param[in] status is the status of the node after solving it (NORMAL, CONVERGED, INFEASIBLE)
     * @param[in] src is the worker who solved the problem
     */
    void _recv_solved_problem(babBase::BabNode &node, 
                              babBase::BabNode &sibling, lbp::SiblingResults &siblingResults,
                              double &lbd, std::vector<double> &lbdSolutionPoint, unsigned &lbdcnt,
                              unsigned &ubdcnt, const COMMUNICATION_TAG status, const int src);

    /**
     * @brief Auxiliary function for sending a new problem to a worker
     *
     * @param[in] node is the node that is sent to the worker for solving
     * @param[in] dest is the worker to whom the problem is sent
     */
    void _send_new_problem(const babBase::BabNode &node, const int dest);

    /**
     * @brief Auxiliary function for sending a new problem corresponding to a sibling iteration to a worker
     *
     * @param[in] lower_sibling is the lower sibling node
     * @param[in] upper_sibling is the upper sibling node
     * @param[in] siblingResults is a pointer to the siblingResults object
     */
    void _send_new_sibling_problem(const babBase::BabNode &lower_sibling, const babBase::BabNode &upper_sibling, const int dest);

    /**
     * @brief Auxiliary function for sending the incumbent to a worker   
     * 
     * @param[in] dest is the worker to whom the incumbent is sent  
     */
    inline void send_incumbent(const int dest);

    /**
     * @brief Auxillary function for informing workers about occuring events
     *
     * @param[in] eventTag is the tag corresponding to the event the workers should be informed of
     * @param[in] blocking is a flag indicating if the communication should be performed in a blocking or non-blocking manner
     */
    void _inform_worker_about_event(const BCAST_TAG eventTag, const bool blocking);
    /**@}*/

    /**
      * @name MPI management and communication functions of worker
      */
    /**@{*/
    /**
     * @brief Auxiliary function for receiving a new problem from the manager
     *
     * @param[out] node is the node that is received from the manager for solving
     * @param[out] sibling is the (upper) sibling node if the two nodes are siblings
     */
    babBase::enums::ITERATION_TYPE _recv_new_problem(babBase::BabNode &node, babBase::BabNode &sibling);

    /**
     * @brief Auxiliary function for sending a new incumbent to the manager
     *
     * @param[in] ubd is the objective value of the found incumbent
     * @param[in] incumbent is the found incumbent point
     * @param[in] incumbentID is the ID of the node which holds the found incumbent
     */
    void _send_incumbent(const double ubd, const std::vector<double> incumbent, const unsigned incumbentID);

    /**
     * @brief Auxiliary function for sending a solved problem to the manager
     *
     * @param[in] node is the solved node which is sent to the manager
     * @param[in] lbd is the new lbd found for the node
     * @param[in] lbdSolutionPoint is the solution point of the node
     * @param[in] lbdcnt is the number of lower bounding problems that were solved during solving the node
     * @param[in] ubdcnt is the number of upper bounding problems that were solved during solving the node
     * @param[in] status is the status of the node after solving it (NORMAL, CONVERGED, INFEASIBLE)
     */
    void _send_solved_problem(const babBase::BabNode node, const double lbd, const std::vector<double> lbdSolutionPoint,
                              const unsigned lbdcnt, const unsigned ubdcnt, const COMMUNICATION_TAG status);

    /**
     * @brief Auxiliary function for sending a solved problem to the manager
     *
     * @param[in] siblingResults is the object containing results from solving the sibling nodes
     * @param[in] lbdcnt is the number of lower bounding problems that were solved during solving the node
     * @param[in] ubdcnt is the number of upper bounding problems that were solved during solving the node
     * @param[in] status is the status of the node after solving it (NORMAL, CONVERGED, INFEASIBLE)
     */
    void _send_solved_sibling_problem(const lbp::SiblingResults &siblingResults,
                                      const unsigned lbdcnt, const unsigned ubdcnt, const COMMUNICATION_TAG status);

    /**
     * @brief Auxiliary function for synchronizing with the master (e.g., to manage termination, exceptions etc.)
     *
     * @param[in] req is the pending request for which the worker awaits an answer
     */
    void _sync_with_master(MPI_Request &req);

    /**
     * @brief Auxiliary function for synchronizing with the master (e.g., to manage termination, exceptions etc.)
     *
     * @param[in] req is the pending request for which the worker awaits an answer
     * @param[out] terminate is a flag that indicates if the worker should terminate the B&B loop
     */
    void _sync_with_master(MPI_Request &req, bool &terminate);
    /**@}*/
#endif    // HAVE_MAiNGO_MPI

    std::unique_ptr<babBase::Brancher> _brancher;   /*!< pointer to brancher object that holds and manages the branch-and-bound tree */
    std::shared_ptr<ubp::UpperBoundingSolver> _UBS; /*!< pointer to upper bounding solver */
    std::shared_ptr<lbp::LowerBoundingSolver> _LBS; /*!< pointer to lower bounding solver */
#if defined(MAiNGO_DEBUG_MODE) && defined(HAVE_GROWING_DATASETS)
    std::shared_ptr<lbp::LowerBoundingSolver> _LBSFull; /*!< pointer to lower bounding solver using the full dataset only */
    double _currentLBDFull;                         /*!< lower bound of the current node when using the full dataset */
    std::vector<double> _lbpSolutionPointFull;      /*!< solution point of the LBP in the current node when using the full dataset */
    double _currentLBDValid;                        /*!< lower bound of the current node when using the evaluation called for augmentation rule OOS */
#endif

    std::shared_ptr<Settings> _maingoSettings; /*!< pointer to object storing settings */

    /**
     * @name Internal variables for storing problem parameters
     */
    /**@{*/
    std::vector<babBase::OptimizationVariable> _originalVariables; /*!< vector holding the optimization variables */
    const unsigned _nvar;                                          /*!< stores number of optimization parameters */
    const unsigned _nvarWOaux;                                     /*!< stores number of optimization variables without additional auxiliary variables */
    std::vector<double> _lowerVarBoundsOrig;                       /*!< vector storing original lower bounds */
    std::vector<double> _upperVarBoundsOrig;                       /*!< vector storing upper bounds */
#ifdef HAVE_GROWING_DATASETS
    std::shared_ptr<std::vector<unsigned int>> _datasets;          /*!< pointer to a vector containing the size of all available datasets */
#endif    // HAVE_GROWING_DATASETS
    /**@}*/

    /**
     * @name Internal variables for storing solution information
     */
    /**@{*/
    std::vector<double> _incumbent;      /*!< vector storing solution (p^*) */
    std::vector<double> _initialPoint;   /*!< vector storing initial point */
    double _ubd;                         /*!< incumbent upper bound */
    double _lbd;                         /*!< lowest lower bound */
#ifdef HAVE_GROWING_DATASETS
    double _lbdPostpro;                  /*!< final lower bound after post-processing the heuristic B&B algorithm with growing datasets */
#endif // HAVE_GROWING_DATASETS
    double _bestLbdFathomed;             /*!< this is the lowest lower bound of a node that has been fathomed by value dominance so far (needed to compute the final optimality gap correctly) */
    bool _foundFeas;                     /*!< if a feasible point has been found */
    unsigned _firstFound;                /*!< first node to find incumbent */
    babBase::enums::BAB_RETCODE _status; /*!< status of the B&B */
    /**@}*/

    /**
     * @name Internal variables for heuristic approaches
     */
    /**@{*/
    double _lbdOld;             /*!< lowest lower bound before update in _update_lowest_lbd() */
    unsigned _lbdNotChanged;    /*!< counter on iterations where the lowest lbd did not change */
    bool _moreScalingActivated; /*!< bool telling whether more scaling has already been activated in the LBS */
    /**@}*/

    /**
     * @name Internal variables for two stage problems
     */
    /**@{*/
    std::vector<double> _w = {};                                                               /*!< vector storing the weights for the scenarios of two-stage problems */
    unsigned _Ns = 0;                                                                          /*!< number of scenarios for two-stage problems */
    unsigned _Nx = 0;                                                                          /*!< number of first-stage variables for two-stage problems */
    unsigned _Ny = 0;                                                                          /*!< number of second-stage variables for two-stage problems */
    std::shared_ptr<std::vector<double>> _subproblemBounds = nullptr;                          /*!< storage for subproblem objective bounds */
    std::map<int, std::pair<std::vector<std::vector<double>>, bool>> _parentSubproblemBounds;  /*!< dictionary storing the bounds obtained using subsolvers for each node and a bool indicating whether to keep the entry after lookup */

    /**
     * @brief Function for updating an entry in _parentSubproblemBounds
     * 
     * @param[in] it is a valid iterator to the entry in _parentSubproblemBounds that should be updated
     * 
     * @return bool indicating whether the entry was removed
     */
    inline bool _update_psb_entry(std::map<int, std::pair<std::vector<std::vector<double>>, bool>>::iterator &it);

    /**
     * @brief Function for setting _subproblemBounds based on the entry in _parentSubproblemBounds
     * 
     * @param[in] n is the node for which the bounds should be set
     * @param[in] sibling_iteration is a flag indicating whether the current iteration is a sibling iteration
     */
    void _retreive_parent_subproblem_bounds(const babBase::BabNode &n, const bool sibling_iteration = false);

    /**
     * @brief Function for updating an entry in _parentSubproblemBounds after observing the fathoming of a node 
     * 
     * @param[in] id is the ID of the node for which the bounds should be updated
     */
    void observe_fathoming(const babBase::BabNode &n) override;

    std::function<
        void(
            lbp::SiblingResults &siblingResults,
            double ubd,
            int obbtType
        )
    > _solve_sibling_subproblems; /*!< function that solves the lower bounding subproblems for sibling nodes */
    std::function<
        int(
            babBase::BabNode &orthantNode,
            const std::vector<unsigned int> &bits,
            const std::array<std::vector<double>, 2> &subproblemBounds,
            const std::array<std::vector<lbp::LbpDualInfo>, 2> &subproblemDualInfo,
            const std::array<std::vector<std::vector<double>>, 2> &subproblemSolutions,
            const std::vector<double> &parentSubproblemBounds,
            double _ubd,
            bool newUbd
        )
    > _postprocess_orthant;       /*!< function that sets the data for orthant nodes */
    /**@}*/

    /**
     * @name Internal variables to store statistics
     */
    /**@{*/
    unsigned _nNodesTotal;       /*!< total nodes created in Iset */
    unsigned _nNodesLeft;        /*!< nodes left in Iset */
    unsigned _nNodesMaxInMemory; /*!< maximum number of nodes held in memory so far */
    unsigned _nNodesDeleted;     /*!< nodes deleted in Iset */
    unsigned _nNodesFathomed;    /*!< nodes fathomed in Iset */
#ifdef HAVE_GROWING_DATASETS
    unsigned _nNodesTrackedPost;   /*!< nodes tracked for post-processing heuristic approach */
    unsigned _nNodesProcessedPost; /*!< nodes actually processed in post-processing before hitting CPU time limit */
#endif    // HAVE_GROWING_DATASETS
    /**@}*/

    /**
     * @name Counters
     */
    /**@{*/
    unsigned _lbdcnt;                   /*!< total number of LBPs solved */
    unsigned _ubdcnt;                   /*!< total number of UBPs solved */
    double _timePassed;                 /*!< total CPU time in seconds */
    double _wtimePassed;                /*!< total wall time in seconds */
    double _timePreprocess;             /*!< CPU time in seconds used for preprocessing */
    double _wtimePreprocess;            /*!< wall time in seconds used for preprocessing */
    unsigned _daysPassed, _wdaysPassed; /*!< number of full days */
#ifdef HAVE_GROWING_DATASETS
    double _timePostpro;                /*!< CPU time for post-processing the heuristic B&B algorithm with growing datasets */
#endif    // HAVE_GROWING_DATASETS
    /**@}*/

    /**
     * @name Internal variables used for printing
     */
    /**@{*/
    unsigned _linesprinted;          /*!< number of lines printed */
    unsigned _iterations;            /*!< number of iterations */
    unsigned _iterationsgap;         /*!< number defining the gap between two outputs*/
    bool _printNewIncumbent;         /*!< auxiliary variable to make sure a line is printed whenever a new incumbent, which is better than the old one for more than the tolerances, is found */
    unsigned _writeToLogEverySec;    /*!< auxiliary variable to make sure we print to log every writeToLogSec seconds */
    std::shared_ptr<Logger> _logger; /*!< pointer to MAiNGO logger */
    std::istream* _inputStream = &std::cin; /*!< stream from which user input may be read during solution */
                                     /**@}*/

#ifdef HAVE_MAiNGO_MPI
    /**
     * @name Internal variables used for MPI communication
     */
    /**@{*/
    int _rank;             /*!< rank of process*/
    int _nProcs;           /*!< number of processes*/
    BCAST_TAG _bcastTag;   /*!< MPI tag representig information which is spread among all processes*/
    MPI_Request _bcastReq; /*!< MPI request handle containing information about incoming/outgoing broadcasts*/
    /**@}*/

    /**
     * @name Internal variables used for MPI management
     */
    /**@{*/
    std::vector<bool> _informedWorkerAboutIncumbent;           /*!< stores information about which worker already knows about the current incumbent */
    bool _checkForNodeWithIncumbent;                           /*!< used to properly track the incumbent when a new one is found within the B&B tree */
    bool _confirmedTermination;                                /*!< stores whether termination was already confirmed by the user */
    unsigned _workCount;                                       /*!< number of  active workers */
    std::vector<std::pair<bool, double>> _nodesGivenToWorkers; /*!< vector holding whether worker i currently has a node and the double value of the lbd of this node */
    /**@}*/

    /**
     * @name Internal variables used by worker processes
     */
    /**@{*/
    bool _pendingIncumbentUpdate; /*!< flag determining whether the workers should be informed about new incumbent */
    MPI_Request _incumbentReq;    /*!< MPI request handle for new incumbent */
    /**@}*/

#endif    // HAVE_MAiNGO_MPI
    };


}    // end namespace bab


}    // end namespace maingo
