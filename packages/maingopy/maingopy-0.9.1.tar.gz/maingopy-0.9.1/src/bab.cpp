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

#include "bab.h"
#include "MAiNGOException.h"
#include "decayingProbability.h"
#include "getTime.h"
#include "lbp.h"
#include "siblingResults.h"
#include "instrumentor.h"
#include "MAiNGOException.h"
#include "mpiUtilities.h"
#include "ubp.h"

#include <iterator>
#include <limits>

using namespace maingo;
using namespace bab;


////////////////////////////////////////////////////////////////////////////////////////
// constructor for the branch and bound object
BranchAndBound::BranchAndBound(const std::vector<babBase::OptimizationVariable> &variables, std::shared_ptr<lbp::LowerBoundingSolver> LBSIn, std::shared_ptr<ubp::UpperBoundingSolver> UBSIn,
                               std::shared_ptr<Settings> settingsIn, std::shared_ptr<Logger> loggerIn, const unsigned nvarWOauxIn, std::istream *const inputStream, const std::string &babFileName):
    babBase::FathomObserver(), _parentSubproblemBounds(),
    _originalVariables(variables),
    _LBS(LBSIn), _UBS(UBSIn), _nvar(variables.size()), _maingoSettings(settingsIn), _logger(loggerIn), _nvarWOaux(nvarWOauxIn), _inputStream(inputStream)
{

#ifdef HAVE_MAiNGO_MPI
    // Initialize common MPI variables
    MPI_Comm_rank(MPI_COMM_WORLD, &_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &_nProcs);
    _bcastTag = BCAST_NOTHING_PENDING;

    // Initialize manager related variables
    _checkForNodeWithIncumbent = false;
    _confirmedTermination      = false;
    _workCount                 = 0;

    // Initialize worker related variables
    _pendingIncumbentUpdate = false;
    _moreScalingActivated   = false;

    MAiNGO_IF_BAB_MANAGER
        _informedWorkerAboutIncumbent = std::vector<bool>(_nProcs - 1, false);
        _nodesGivenToWorkers = std::vector<std::pair<bool, double>>(_nProcs - 1, std::make_pair(false, _maingoSettings->infinity));
    MAiNGO_ELSE
            _brancher = nullptr;
    MAiNGO_END_IF

#endif

    MAiNGO_IF_BAB_MANAGER
            //Create brancher
            _brancher = std::unique_ptr<babBase::Brancher>(new babBase::Brancher(variables, babFileName));
            // Store settings:
            _brancher->set_branching_dimension_selection_strategy(_maingoSettings->BAB_branchVariable);
            _brancher->set_node_selection_strategy(_maingoSettings->BAB_nodeSelection);
            _brancher->decrease_pruning_score_threshold_to(_maingoSettings->infinity);
            _brancher->enable_pruning_with_rel_and_abs_tolerance(_maingoSettings->epsilonR, _maingoSettings->epsilonA);
    MAiNGO_END_IF

        // Initialize internals
        _foundFeas       = false;
        _firstFound      = 0;
        _lbd             = -_maingoSettings->infinity;
#ifdef HAVE_GROWING_DATASETS
        _lbdPostpro      = -_maingoSettings->infinity;
#endif   // HAVE_GROWING_DATASETS
        _lbdOld          = -_maingoSettings->infinity;
        _bestLbdFathomed = _maingoSettings->infinity;
        _ubd             = _maingoSettings->infinity;

        // Set counters to 0
        _nNodesTotal          = 0;
        _nNodesLeft           = 0;
        _nNodesDeleted        = 0;
        _nNodesFathomed       = 0;
        _nNodesMaxInMemory    = 0;
#ifdef HAVE_GROWING_DATASETS
        _nNodesTrackedPost    = 0;
        _nNodesProcessedPost  = 0;
#endif    // HAVE_GROWING_DATASETS
        _lbdcnt               = 0;
        _ubdcnt               = 0;
        _timePassed           = 0.0;
        _wtimePassed          = 0.0;
        _timePreprocess       = 0.0;
        _wtimePreprocess      = 0.0;
        _daysPassed           = 0;
        _wdaysPassed          = 0;
#ifdef HAVE_GROWING_DATASETS
        _timePostpro          = 0.0;
#endif    // HAVE_GROWING_DATASETS
        _iterations           = 0;
        _linesprinted         = 0;
        _printNewIncumbent    = false;
        _writeToLogEverySec   = 1;                                      // First write to log is after Settings->writeToLogSec CPU seconds
        _iterationsgap        = 20 * _maingoSettings->BAB_printFreq;    // Print after every 20 outputs
        _lbdNotChanged        = 0;
        _moreScalingActivated = false;

        // Save original bounds
        _lowerVarBoundsOrig.resize(_originalVariables.size());
        _upperVarBoundsOrig.resize(_originalVariables.size());
        for (unsigned int i = 0; i < _originalVariables.size(); i++) {
            _lowerVarBoundsOrig[i] = _originalVariables[i].get_lower_bound();
            _upperVarBoundsOrig[i] = _originalVariables[i].get_upper_bound();
        }
}


////////////////////////////////////////////////////////////////////////////////////////
// main branch and bound algorithm
babBase::enums::BAB_RETCODE
BranchAndBound::solve(babBase::BabNode &rootNodeIn, double &solutionValue, std::vector<double> &solutionPoint, const double preprocessTime, const double preprocessWallTime, double &timePassed, double &wallTimePassed)
{
    try {
        // ---------------------------------------------------------------------------------
        // 0: Process Inputs
        // ---------------------------------------------------------------------------------
#ifdef HAVE_GROWING_DATASETS
        // Warn user when skipping bound tightening
        MAiNGO_IF_BAB_MANAGER
        if ((_maingoSettings->growing_approach > GROW_APPR_DETERMINISTIC) && (!_maingoSettings->PRE_pureMultistart)) {
            if ((_maingoSettings->BAB_alwaysSolveObbt) || (_maingoSettings->BAB_dbbt)
                || (_maingoSettings->BAB_probing) || (_maingoSettings->BAB_constraintPropagation)) {
                _logger->print_message("\n  Warning: No bound tightening performed in B&B nodes with a reduced dataset since it may be erroneous for heuristic approaches.\n", VERB_NORMAL, BAB_VERBOSITY);
            }
        }
        MAiNGO_END_IF
#endif    // HAVE_GROWING_DATASETS

        // Auxiliary variables for timing (have to be declared outside of MAiNGO_IF_BAB_MANAGER scope to be available in whole loop)
        double startTime, startwTime, currentTime, currentwTime, lastTime, lastwTime;
        double currentLBD;    // This is declared here to be available for the Manager and Workers in the parallel version

#ifdef HAVE_GROWING_DATASETS
        std::shared_ptr<babBase::BabNode> nodeFinalLB;    // Auxiliary variable for storing node providing overall lower bound
#endif    // HAVE_GROWING_DATASETS

    MAiNGO_IF_BAB_MANAGER
        // Store initial feasible point if given
        if (!solutionPoint.empty()) {
            _update_incumbent_and_fathom(solutionValue, solutionPoint, 0);
            // Since _update_incumbent_and_fathom triggers an asterisk in the output whenever a new incumbent was found,
            // we need to suppress this here (otherwise it would look like this incumbent was found during B&B in the root node, although it comes from pre-processing)
            _printNewIncumbent = false;
        }

        // Hand root node to _brancher
        // Change id from 0 to 1 since we start B&B
        rootNodeIn = babBase::BabNode(rootNodeIn.get_pruning_score(), rootNodeIn.get_lower_bounds(), rootNodeIn.get_upper_bounds(), rootNodeIn.get_index_dataset(), 0 /*parent ID*/, 1 /*ID*/, 0 /*depth*/, rootNodeIn.get_augment_data());
        _brancher->insert_root_node(rootNodeIn);
        _nNodesLeft = _brancher->get_nodes_in_tree();

#ifdef HAVE_GROWING_DATASETS
        // Initialize node containing solution with root node
        nodeFinalLB = std::make_shared<babBase::BabNode>(rootNodeIn);
#endif    // HAVE_GROWING_DATASETS

        // Initialize stuff for timing and logging
        _timePreprocess  = preprocessTime;
        _wtimePreprocess = preprocessWallTime;
        _timePassed      = preprocessTime;
        _wtimePassed     = preprocessWallTime;
        startTime        = get_cpu_time();
        startwTime       = get_wall_time();
        lastTime         = -1e10;    // This is needed since the time is reset after 24h --> if we detect this, we can store it as days passed
        lastwTime        = -1e10;    // This is needed since the time is reset after 24h --> if we detect this, we can store it as days passed
#ifdef HAVE_MAiNGO_MPI
    MAiNGO_ELSE // WORKER
        startTime = get_cpu_time();
        // Opening for broadcasts from master
        MPI_Ibcast(&_bcastTag, 1, MPI_INT, 0, MPI_COMM_WORLD, &_bcastReq);
#endif  // HAVE_MAiNGO_MPI
    MAiNGO_END_IF

        // ------------------------- End 0: Process Inputs ---------------------------------


    // ---------------------------------------------------------------------------------
    // 1-10: Main Branch-and-Bound loop
    // ---------------------------------------------------------------------------------
    MAiNGO_IF_BAB_MANAGER
        _logger->print_message("\n  Entering branch-and-bound loop:\n", VERB_NORMAL, BAB_VERBOSITY);
    MAiNGO_END_IF

        // Check termination criteria: when terminating regularly, no nodes should be left; otherwise, termination occurs when hitting CPU time or node limit
        _TERMINATION_TYPE termination = _check_termination();    // _workers == 0
        while (termination != _TERMINATED) {

            babBase::BabNode currentNode;
            babBase::BabNode sibling;
            lbp::SiblingResults siblingResults(_w, _Nx, _Ny);

#ifdef HAVE_MAiNGO_MPI
            MPI_Status status;
    MAiNGO_IF_BAB_MANAGER
            // -----------------------------------
            // Check incoming messages from workers
            // -----------------------------------
            // Don't accept node requests if babTree is empty or terminated
            if (_nNodesLeft == 0 || termination == _TERMINATED_WORKERS_ACTIVE) {
                const int tagCount = 8;
                // Allowed are exceptions and solved nodes
                COMMUNICATION_TAG allowedTags[tagCount] = {TAG_EXCEPTION, TAG_FOUND_INCUMBENT, TAG_SOLVED_NODE_STATUS_NORMAL,
                                                           TAG_SOLVED_NODE_STATUS_CONVERGED, TAG_SOLVED_NODE_STATUS_INFEAS,
                                                           TAG_SOLVED_SIBLING_STATUS_NORMAL, TAG_SOLVED_SIBLING_STATUS_CONVERGED,
                                                           TAG_SOLVED_SIBLING_STATUS_INFEAS};
                int flag                                = 0;
                // Probe for messages with allowed tags
                while (!flag) {
                    for (int i = 0; i < tagCount; i++) {
                        MPI_Iprobe(MPI_ANY_SOURCE, allowedTags[i], MPI_COMM_WORLD, &flag, &status);
                        if (flag)
                            break;
                    }
                }
            }
            else {
                // Otherwise just check for any incoming tags
                MPI_Probe(MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, &status);
            }

            if (status.MPI_TAG == TAG_EXCEPTION) {
                // -----------------------------------
                // Worker ran into an exception
                // -----------------------------------
                MPI_Recv(NULL, 0, MPI_INT, status.MPI_SOURCE, status.MPI_TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                std::string str = "  Worker ran into exception!";
                throw MAiNGOMpiException(str, MAiNGOMpiException::ORIGIN_OTHER);
            }
            else if (status.MPI_TAG == TAG_FOUND_INCUMBENT) {
                // -----------------------------------
                // Worker has found new incumbent
                // -----------------------------------
                std::vector<double> incumbentBuf(_nvarWOaux + 2);
                MPI_Recv(incumbentBuf.data(), _nvarWOaux + 2, MPI_DOUBLE, status.MPI_SOURCE, status.MPI_TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

                // Store incumbent
                std::vector<double> newIncumbent(incumbentBuf.begin(), incumbentBuf.begin() + _nvarWOaux);
                double newUBD        = incumbentBuf[_nvarWOaux];
                unsigned incumbentID = incumbentBuf[_nvarWOaux + 1];

                _update_incumbent_and_fathom(newUBD, newIncumbent, incumbentID);

                continue;
            }
            else if (status.MPI_TAG == TAG_NODE_REQUEST) {

                // -----------------------------------
                // Worker requests a new node
                // -----------------------------------
                MPI_Recv(NULL, 0, MPI_INT, status.MPI_SOURCE, status.MPI_TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                _workCount++;
#endif   // HAVE_MAiNGO_MPI (MANAGER IS ACTIVE)

                // -----------------------------------
                // 1. Node selection: Determine which node to treat next
                // -----------------------------------
                currentNode = _brancher->get_next_node();
                if (_maingoSettings->BAB_verbosity > VERB_NORMAL) {
                    _print_one_node(currentNode.get_pruning_score(), currentNode);
                }
                bool sibling_iteration = false;
                if (_maingoSettings->TS_useLowerBoundingSubsolvers && _subproblemBounds != nullptr) {
                    // See if this node has a sibling
                    sibling_iteration = _brancher->find_sibling(currentNode, sibling);
                    _retreive_parent_subproblem_bounds(currentNode, sibling_iteration);
                }

#ifdef HAVE_MAiNGO_MPI  // (MANAGER IS ACTIVE)
                if (sibling_iteration) {    // Can only be true for extension two-stage stochastic programming
                    // -----------------------------------
                    // Send siblings to worker
                    // -----------------------------------
                    _send_new_sibling_problem(currentNode, sibling, status.MPI_SOURCE);
                }
                else {
                    // -----------------------------------
                    // Send node to worker
                    // -----------------------------------
                    _send_new_problem(currentNode, status.MPI_SOURCE);
                }   
                _nNodesLeft                                        = _brancher->get_nodes_in_tree();
                _nodesGivenToWorkers[status.MPI_SOURCE - 1].first  = true;
                _nodesGivenToWorkers[status.MPI_SOURCE - 1].second = currentNode.get_pruning_score();

                continue;

            } // end else if (status.MPI_TAG == TAG_NODE_REQUEST)
    MAiNGO_ELSE // switch from MANAGER TO WORKER
#endif // HAVE_MAiNGO_MPI (WORKER ACTIVE)

            //-------------------------------------
            // Process Node:
            // 2. Node pre-processing:
            //      a) Constraint propagation
            //      b) Optimization-based bound tightening (OBBT)
            // 3. Lower bounding: solve lower bounding problem (LBP) to derive a better lower bound
            // 4. Upper bounding: try to find a good feasible point within the current node
            // 5. Node post-processing:
            //      a) Duality-based bounds tightening (DBBT)
            //      b) Probing
            //-------------------------------------
            bool nodeProvenInfeasible = false;
            bool nodeConverged        = false;
            unsigned nAddedLBSolves   = 0;
            unsigned nAddedUBSolves   = 0;
            std::vector<double> lbpSolutionPoint;
            bool foundNewFeasiblePoint = false;
            double ubpObjectiveValue   = _maingoSettings->infinity;
            std::vector<double> ubpSolutionPoint;

#ifdef HAVE_MAiNGO_MPI  // (WORKER ACTIVE)
            // -----------------------------------
            // Receive new node from Manager
            // -----------------------------------

            // Send node request to manager
            MPI_Request node_request;
            MPI_Issend(NULL, 0, MPI_INT, 0, TAG_NODE_REQUEST, MPI_COMM_WORLD, &node_request);

            bool terminate;
            _sync_with_master(node_request, terminate);
            if (terminate)
                break;

            // Receive new problem and update _incumbent if necessary
            bool sibling_iteration = (_recv_new_problem(currentNode, sibling) == babBase::enums::SIBLING_ITERATION);
#endif // HAVE_MAiNGO_MPI (WORKER ACTIVE)

            if (sibling_iteration) {    // Can only be true for extension two-stage stochastic programming
                siblingResults.reset(std::move(currentNode), std::move(sibling), *_subproblemBounds);
                _process_siblings(siblingResults);
                nodeConverged        = siblingResults.converged;
                nodeProvenInfeasible = !siblingResults.feasible;
                nAddedLBSolves       = siblingResults.nAddedLBSolves;
                nAddedUBSolves       = siblingResults.feasible; // If feasible we did one 
                currentLBD           = siblingResults.parentPruningScore;
                lbpSolutionPoint     = {};
                foundNewFeasiblePoint = siblingResults.foundNewFeasiblePoint;
                ubpObjectiveValue     = siblingResults.ubpObjectiveValue;
                ubpSolutionPoint      = siblingResults.ubpSolutionPoint;

#ifdef HAVE_MAiNGO_MPI // (WORKER ACTIVE)
                // -----------------------------------
                // Send sibling results to Manager
                // -----------------------------------

                // Wait until manager accepted pending incumbent updates
                if (_pendingIncumbentUpdate) {
                _sync_with_master(_incumbentReq, terminate);
                _pendingIncumbentUpdate = false;
                if (terminate)
                    break;
                }

                MPI_Request solutionRequest;
                // Choose communication tag according to node status
                COMMUNICATION_TAG nodeStatus = TAG_SOLVED_SIBLING_STATUS_NORMAL;
                if (nodeConverged)
                    nodeStatus = TAG_SOLVED_SIBLING_STATUS_CONVERGED;  // or just TAG_SOLVED_NODE_STATUS_CONVERGED?
                if (nodeProvenInfeasible)
                    nodeStatus = TAG_SOLVED_SIBLING_STATUS_INFEAS; // or just TAG_SOLVED_NODE_STATUS_INFEAS?

                // Send communication request to manager
                MPI_Issend(NULL, 0, MPI_INT, 0, nodeStatus, MPI_COMM_WORLD, &solutionRequest);
                _sync_with_master(solutionRequest, terminate);
                if (terminate) {
                    break;
                }

                _send_solved_sibling_problem(siblingResults, nAddedLBSolves, nAddedUBSolves, nodeStatus);
#else // SERIAL
                if (nodeConverged || nodeProvenInfeasible) {
                    // set current node to dummy parent to register fathoming
                    currentNode = babBase::BabNode(siblingResults.parentPruningScore, {}, {}, 0, 0, siblingResults.siblings[0].get_parent_ID(), 0, false);
                }
#endif // end HAVE_MAiNGO_MPI (WORKER ACTIVE)

            } else { // end sibling iteration, begin normal iteration
                std::tie(nodeProvenInfeasible, nodeConverged, nAddedLBSolves, nAddedUBSolves, currentLBD, lbpSolutionPoint, foundNewFeasiblePoint, ubpObjectiveValue, ubpSolutionPoint) = _process_node(currentNode);

#if defined(MAiNGO_DEBUG_MODE) && defined(HAVE_GROWING_DATASETS) && ! defined(HAVE_MAiNGO_MPI)
                    if (currentNode.get_index_dataset() > 0) {
                        _currentLBDValid = _evaluate_lower_bound_for_validation_set(currentNode, lbpSolutionPoint, currentLBD);
                    }
                    else {
                        _currentLBDValid = -_maingoSettings->infinity; // Not defined for full dataset
                    }
#endif    // HAVE_GROWING_DATASETS && ...

#ifdef HAVE_MAiNGO_MPI // (WORKER ACTIVE)
                // -----------------------------------
                // Send solved node to Manager
                // -----------------------------------

                // Wait until manager accepted pending incumbent updates
                if (_pendingIncumbentUpdate) {
                    _sync_with_master(_incumbentReq, terminate);
                    _pendingIncumbentUpdate = false;
                    if (terminate)
                        break;
                }

                MPI_Request solutionRequest;
                // Choose communication tag according to node status
                COMMUNICATION_TAG nodeStatus = TAG_SOLVED_NODE_STATUS_NORMAL;
                if (nodeConverged)
                    nodeStatus = TAG_SOLVED_NODE_STATUS_CONVERGED;
                if (nodeProvenInfeasible)
                    nodeStatus = TAG_SOLVED_NODE_STATUS_INFEAS;

                // Send communication request to manager
                MPI_Issend(NULL, 0, MPI_INT, 0, nodeStatus, MPI_COMM_WORLD, &solutionRequest);
                _sync_with_master(solutionRequest, terminate);
                if (terminate) {
                    break;
                }
                _send_solved_problem(currentNode, currentLBD, lbpSolutionPoint, nAddedLBSolves, nAddedUBSolves, nodeStatus);
    MAiNGO_END_IF // end of MAiNGO_IF_BAB_WORKER
#endif // HAVE_MAiNGO_MPI (WORKER ACTIVE)

            } // end normal iteration

#ifdef HAVE_MAiNGO_MPI
    MAiNGO_IF_BAB_MANAGER
            // -----------------------------------
            // Receive solved node from Worker
            // -----------------------------------

            MPI_Recv(NULL, 0, MPI_INT, status.MPI_SOURCE, status.MPI_TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            _workCount--;
            _nodesGivenToWorkers[status.MPI_SOURCE - 1].first  = false;
            _nodesGivenToWorkers[status.MPI_SOURCE - 1].second = _maingoSettings->infinity;

            // Receive problem
            COMMUNICATION_TAG nodeStatus = (COMMUNICATION_TAG)status.MPI_TAG;
            std::vector<double> lbpSolutionPoint;
            unsigned nAddedLBSolves;
            unsigned nAddedUBSolves;
            bool nodeConverged        = false;
            bool nodeProvenInfeasible = false;
            bool sibling_iteration    = false;
            // Get node status
            switch (nodeStatus) {
                case TAG_SOLVED_SIBLING_STATUS_NORMAL:
                    sibling_iteration = true;
                    break;
                case TAG_SOLVED_SIBLING_STATUS_CONVERGED:
                    nodeConverged = true;
                    sibling_iteration = true;
                    break;
                case TAG_SOLVED_SIBLING_STATUS_INFEAS:
                    nodeProvenInfeasible = true;
                    sibling_iteration = true;
                    break;
                case TAG_SOLVED_NODE_STATUS_CONVERGED:
                    nodeConverged = true;
                    break;
                case TAG_SOLVED_NODE_STATUS_INFEAS:
                    nodeProvenInfeasible = true;
                    break;
                default:
                    break;
            }

            _recv_solved_problem(currentNode, sibling, siblingResults, currentLBD, lbpSolutionPoint, nAddedLBSolves, nAddedUBSolves, nodeStatus, status.MPI_SOURCE);
#else // (SERIAL) In the parallel version the worker already told the manager about the incumbent

            //-------------------------------------
            // 6. Process the incumbent status of the processed node
            //-------------------------------------
            if (foundNewFeasiblePoint) {
                // Check if this feasible point is better than the incumbent & fathom by value dominance (first remaining tree and then current node):
                _update_incumbent_and_fathom(ubpObjectiveValue, ubpSolutionPoint, currentNode.get_ID());
            }
#endif // end SERIAL (MANAGER ACTIVE)

            // -----------------------------------
            // 7. Branching
            //    (Optional) Extension B&B with growing datasets: Either augment or branch
            // -----------------------------------
            bool nodeReachedMinRelNodeSize = false;    // nodeReachedMinRelNodeSize indicates whether the brancher chose not to branch on the node because it is too small

#ifdef HAVE_GROWING_DATASETS
            auto nNodesLeftBeforeAugmentingOrBranching = _brancher->get_nodes_in_tree();

            // Catch all approximations of full lower bound
            // After getting the currentLBD from workers, before augmenting and pruning
            double redLBD = currentLBD;
            double oosLBD = -_maingoSettings->infinity;
            double combiLBD = -_maingoSettings->infinity;

            // Evaluating validation set if applicable
            if ((_maingoSettings->growing_approach > GROW_APPR_DETERMINISTIC) && (currentNode.get_index_dataset() > 0)) {
                // Validation set is only defined for reduced dataset
                oosLBD = _evaluate_lower_bound_for_validation_set(currentNode, lbpSolutionPoint, currentLBD);
                combiLBD = _calculate_combined_lower_bound(currentLBD, oosLBD, currentNode.get_index_dataset());

                // Pruning based on combined lower bound
                currentLBD = combiLBD;

                // Check whether node converged with combined lower bound & fathom
                if (nodeConverged == false) {
                    if (babBase::larger_or_equal_within_rel_and_abs_tolerance(currentLBD, _ubd, _maingoSettings->epsilonR, _maingoSettings->epsilonA)) {
                        std::ostringstream outstr;
                        outstr << "  Node #" << currentNode.get_ID() << " converged with LBD " << currentLBD << " to UBD " << _ubd << std::endl;
                        _logger->print_message(outstr.str(), VERB_ALL, BAB_VERBOSITY);

                        nodeConverged = true;
                        currentNode.set_pruning_score(currentLBD);
                    }
                }
            }

            // Call augmentation rule
            if (nodeProvenInfeasible == false) {
                currentNode.set_augment_data(_check_whether_to_augment(currentNode, lbpSolutionPoint, redLBD, oosLBD, combiLBD));
            }
            else {
                // For logging: infeasible node is never augmented (but discarded)
                currentNode.set_augment_data(false);
            }
#endif    // HAVE_GROWING_DATASETS

            if (currentNode.get_augment_data()) {   // Can only be true for extension B&B with growing datasets
#ifdef HAVE_GROWING_DATASETS
                // Augmenting
                unsigned int newDataIndex = _augment_dataset(currentNode);
                if ((nodeConverged == false) || (currentNode.get_index_dataset() > 0)) {
                    // If not converged with full data
                    _brancher->add_node_with_new_data_index(currentNode, newDataIndex);
                }
#endif    // HAVE_GROWING_DATASETS
            }
            else {    // Branching
                if (sibling_iteration) {    // Can only be true for extension two-stage stochastic programming
                    // If the sibling results indicate convergence or infeasibility, the parent node (whose id is now stored in the dummy currentNode) is fathomed
                    if (nodeConverged) {
                        _brancher->register_node_status(currentNode, babBase::enums::NodeStatus::DOMINATED);
                    }
                    else if (nodeProvenInfeasible) {
                        _brancher->register_node_status(currentNode, babBase::enums::NodeStatus::INFEASIBLE);
                    }
                    else {  // neither converged, nor infeasible, we will multisect
                        // Callback to test for domination of orthant nodes resulting from multisection
                        auto dominance_test = [&](unsigned int id, double pruningScore) {
                            bool dominated = babBase::larger_or_equal_within_rel_and_abs_tolerance(
                                pruningScore, _ubd, _maingoSettings->epsilonR, _maingoSettings->epsilonA);
                            if (dominated) {
                                std::ostringstream outstr;
                                outstr << "  Node #" << id << " converged with LBD "
                                        << pruningScore << " to UBD " << _ubd << std::endl;
                                _logger->print_message(outstr.str(), VERB_ALL, BAB_VERBOSITY);
                            }
                            return dominated;
                        };

                        double previousUbd = _ubd;

                        // Callback for storing orthant subproblem bounds
                        auto postprocess_orthant = [&](
                            babBase::BabNode &orthantNode,
                            const std::vector<unsigned int> &bits,
                            const std::array<std::vector<double>, 2> &subproblemBounds)
                        {
                            /** NOTE: If the second-stage variables corresponding to some scenario are not branched, the assiciated subproblem bounds for a given orthant node are derived from the orthant node's parent.
                             *        Since the subproblem bounds for both siblings are at least as tight as the subproblem bounds of the parent, the former constitute a valid tightening, which we can use to compute better scenario upper bounds and pruning scores.
                             *        However, since this tightening is not based on the orthant node domain, we cannot use it to compute strong branching scores.
                             *        To accurately measure subproblem bound improvement resulting from a possible multisection branching of an orthant node, we therefore additionally store subproblem bounds based on the original parent node. 
                             */
                            // orthant subproblem bounds for scenario upper bounds and pruning [0] and for calculation of strong-branching scores [1]
                            std::vector<std::vector<double>> OSPBs = {std::vector<double>(siblingResults.parentObjectiveBounds.size()), siblingResults.parentObjectiveBounds};
                            #ifdef _OPENMP
                            #pragma omp parallel for
                            #endif
                            for (int s = 0; s < _Ns; s++) {
                              auto bit = bits[s];
                              if (bit <= 1) { // siblings
                                OSPBs[0][s] = subproblemBounds[bit][s];
                                OSPBs[1][s] = subproblemBounds[bit][s];
                              }
                              else { // parent
                                OSPBs[0][s] = std::min(subproblemBounds[0][s], subproblemBounds[1][s]);
                              }
                            }
                            _parentSubproblemBounds[orthantNode.get_ID()] = {OSPBs, true};
                        };

                        _brancher->multisect_parent_node(
                            siblingResults.parentPruningScore,
                            siblingResults.parentObjectiveBounds,
                            siblingResults.siblings,
                            siblingResults.objectiveBounds,
                            siblingResults.solutions,
                            siblingResults.lowerBounds,
                            siblingResults.upperBounds,
                            _nNodesFathomed,
                            _bestLbdFathomed,
                            dominance_test,
                            postprocess_orthant,
                            _maingoSettings->relNodeTol
                        );
                    } // end if feasible
                } else {    // Standard B&B algorithm
                    // Inform brancher about changes in node
                    _brancher->register_node_change(currentNode.get_ID(), currentNode);
                    if (nodeConverged) {
                        _brancher->register_node_status(currentNode, babBase::enums::NodeStatus::DOMINATED);
                    }
                    else if (nodeProvenInfeasible) {
                        _brancher->register_node_status(currentNode, babBase::enums::NodeStatus::INFEASIBLE);
                    }
                    // If node is feasible but it did not converge yet branch it
                    bool nodeReachedMinRelNodeSize = false;    // nodeReachedMinRelNodeSize indicates whether the brancher chose not to branch on the node because it is too small
                    if ((nodeProvenInfeasible == false) && (nodeConverged == false)) {
                        if (_maingoSettings->TS_useLowerBoundingSubsolvers && _subproblemBounds != nullptr) {
                            _parentSubproblemBounds[currentNode.get_ID()] = {{*_subproblemBounds}, true};
                        }
                        currentNode.set_pruning_score(currentLBD);
                        bool dummy;
                        std::tie(dummy, nodeReachedMinRelNodeSize) = _brancher->branch_on_node(currentNode, lbpSolutionPoint, currentLBD, _maingoSettings->relNodeTol);
                    }
                } // end node or sibling handling
            } // end if (currentNode.get_augment_data())

            // -----------------------------------
            // 8. Heuristic checks
            // -----------------------------------
            if (!_moreScalingActivated) {
                _check_if_more_scaling_needed();
            }

            // -----------------------------------
            // 9. Updating statistics
            // -----------------------------------
            // Update best fathomed lower bound properly. This ensures that the final overall lower bound is correct.
            // In particular, nodeReachedMinRelNodeSize is needed to ensure the overall LBD does not get better than that of nodes which were thrown out because they were too small.
            if (nodeConverged || nodeReachedMinRelNodeSize) {
                _bestLbdFathomed = std::min(_bestLbdFathomed, currentLBD);
            }
            // Update overall lbd
            _update_lowest_lbd();
            // Update counters
            _iterations++;
            _ubdcnt += nAddedUBSolves;
            _lbdcnt += nAddedLBSolves;

#ifdef HAVE_GROWING_DATASETS
            bool restartGrowing = false;
            if (currentNode.get_index_dataset() > 0) {
                // Track node with overall lower bound
                if (_lbd != _lbdOld) {
                    nodeFinalLB = std::make_shared<babBase::BabNode>(currentNode);
                }

                // Track nodes pruned based on reduced/combined lower bound for postprocessing (heuristic approaches)
                if ((_maingoSettings->growing_approach > GROW_APPR_DETERMINISTIC)
                    && (nodeProvenInfeasible == false) && (_brancher->get_nodes_in_tree() <= nNodesLeftBeforeAugmentingOrBranching)) {
                    // If tree didn't grow, active node is pruned based on lower bound (= no child/ren) or found to be infeasible
                    _brancher->add_node_for_postprocessing(currentNode);
                }

                // Restart B&B loop if data reduction prevents convergence (augmentation rule not finitely convergent)
                if (_brancher->get_nodes_in_tree() == 0) {
                    restartGrowing = true;
                    currentNode.set_augment_data(true);

                    // Reset LBD of node to circumvent pruning = force the addition of a new node to the BaB tree
                    (*nodeFinalLB).set_pruning_score(-_maingoSettings->infinity);
                    _brancher->add_node_with_new_data_index(*nodeFinalLB, 0);
                }
            }
#endif    // HAVE_GROWING_DATASETS

            if (nodeConverged || nodeProvenInfeasible) {
                _nNodesFathomed++;
            }
            _nNodesLeft        = _brancher->get_nodes_in_tree();
            _nNodesMaxInMemory = std::max(_nNodesMaxInMemory, _nNodesLeft);

#ifdef HAVE_MAiNGO_MPI // (MANAGER IS ACTIVE)
    MAiNGO_END_IF // end of MAiNGO_IF_BAB_MANAGER
#endif // end HAVE_MAiNGO_MPI

            // -----------------------------------
            // 10. Timing & output
            // -----------------------------------
            // Get time
            currentTime = get_cpu_time();
            if ((currentTime - startTime) < lastTime) { // GCOVR_EXCL_START
                _daysPassed += 1; // NOTE: Assumes each iteration takes at most one day
    MAiNGO_IF_BAB_MANAGER
                std::ostringstream outstr;
                outstr << "    Days spent: " << _daysPassed << std::endl
                        << std::endl;
                _logger->print_message(outstr.str(), VERB_NORMAL, BAB_VERBOSITY);
    MAiNGO_END_IF
            } // GCOVR_EXCL_STOP
            lastTime    = currentTime - startTime;
            _timePassed = _timePreprocess + _daysPassed * 86400 + lastTime;

            currentwTime = get_wall_time();
            if ((currentwTime - startwTime) < lastwTime) { // GCOVR_EXCL_START
                _wdaysPassed += 1; // NOTE: Assumes each iteration takes at most one day
            } // GCOVR_EXCL_STOP
            lastwTime    = currentwTime - startwTime;
            _wtimePassed = _wtimePreprocess + _wdaysPassed * 86400 + lastwTime;
    MAiNGO_IF_BAB_MANAGER
            // Print output
            _display_and_log_progress(currentLBD, currentNode);

#ifdef HAVE_GROWING_DATASETS
            // Print warning if applicable
            if (restartGrowing) {
                std::ostringstream outstr;
                outstr << "  Warning: The B&B algorithm with growing datasets was about to terminate with a reduced dataset. Restarting with the full dataset ..." << std::endl;
                _logger->print_message(outstr.str(), VERB_NORMAL, BAB_VERBOSITY);
            }
#if defined(MAiNGO_DEBUG_MODE) && !defined(HAVE_MAiNGO_MPI)
            _log_nodes(currentNode, currentLBD, ubpObjectiveValue, lbpSolutionPoint);
#endif    // HAVE_GROWING_DATASETS && !defined(HAVE_MAiNGO_MPI)
#endif // HAVE_GROWING_DATASETS

            // -----------------------------------
            // 11. Check termination
            // -----------------------------------
            termination = _check_termination();
    MAiNGO_END_IF

        }    // main while loop

        // ----------------- End 1-10: Main branch and bound loop ----------------------------

#ifdef HAVE_MAiNGO_MPI
    MAiNGO_IF_BAB_MANAGER
        // ---------------------------------------------------------------------------------
        // Inform workers about termination
        // ---------------------------------------------------------------------------------

        _inform_worker_about_event(BCAST_TERMINATE, /* blocking broadcast */ true);
        // Wait for all workers to get out of the while(true) loop
        MAiNGO_MPI_BARRIER

        // Clean up all pending requests -- it is not the best way, but MPI_Cancel seems to have problems on different operating systems so we do this just to make sure everything is fine
        bool pendingRequests = true;
        while (pendingRequests) {
            int flag = 0;
            MPI_Status status;
            MPI_Iprobe(MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, &flag, &status);
            if (flag) {
                MPI_Recv(NULL, 0, MPI_INT, status.MPI_SOURCE, status.MPI_TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            }
            else {
                pendingRequests = false;
            }
        }
        MAiNGO_MPI_BARRIER

        // Get CPU times of workers
        std::vector<double> processTimes(_nProcs);
        MPI_Gather(&_timePassed, 1, MPI_DOUBLE, processTimes.data(), 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);

        // Calculate sum of compute times
        _timePassed = 0;
        for (int i = 0; i < _nProcs; i++) {
            _timePassed += processTimes[i];
        }
    MAiNGO_ELSE
        // ---------------------------------------------------------------------------------
        // Inform manager about required solution time
        // ---------------------------------------------------------------------------------
        MAiNGO_MPI_BARRIER // Wait for all workers to get out of the while(true) loop
        MAiNGO_MPI_BARRIER // Wait for manager to clean up all pending requests
        // Send needed CPU time to master
        MPI_Gather(&_timePassed, 1, MPI_DOUBLE, NULL, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);
    MAiNGO_END_IF
#endif

        // ---------------------------------------------------------------------------------
        // 11: Prepare output
        // ---------------------------------------------------------------------------------
    MAiNGO_IF_BAB_MANAGER
        // Store solution for returning to MAiNGO
        if (_foundFeas == true) {
            solutionPoint = _incumbent;
            solutionValue = _ubd;
        }

        // Save time passed (this is especially needed when the passed CPU time is >24h)
        timePassed = _timePassed;
        wallTimePassed = _wtimePassed;
    MAiNGO_END_IF
        // --------------------- End: Prepare output -------------------------------
    }
#ifdef HAVE_MAiNGO_MPI
    catch (std::exception &e) {
        MAiNGOMpiException e_mpi("  Error during branch-and-bound.", e, MAiNGOMpiException::ORIGIN_ME);
        _communicate_exception_and_throw(e_mpi);
    }
    catch (...) {
        std::string str;
    MAiNGO_IF_BAB_MANAGER
            str = "  Unknown error during branch-and-bound (Manager).";
    MAiNGO_ELSE
            str = "  Unknown error during branch-and-bound (Worker).";
    MAiNGO_END_IF
        MAiNGOMpiException e(str, MAiNGOMpiException::ORIGIN_ME);
        _communicate_exception_and_throw(e);
    }
#else
    catch (std::exception &e) // GCOVR_EXCL_START
    {
        throw MAiNGOException("  Error during branch-and-bound.", e);
    }
    catch (...)
    {
        throw MAiNGOException("  Unknown error during branch-and-bound.");
    }
// GCOVR_EXCL_STOP
#endif
    return _status;    // Return code is determined in _check_termination()
}

void
BranchAndBound::setup_two_stage_branching(
    unsigned Nx, unsigned Ny, const std::vector<double> &w,
    std::vector<double>& subproblemBounds,
    std::function<
        void(
            lbp::SiblingResults &siblingResults,
            double ubd,
            int obbtType
        )
    > solve_sibling_subproblems,
    double alpha,
    unsigned int k_max) {
        _w  = w;
        _Ns = w.size();
        _Nx = Nx;
        _Ny = Ny;
#ifdef HAVE_MAINGO_MPI
    MAiNGO_IF_BAB_MANAGER
        // The passed subproblemBounds are from the MANAGER's LBS which is not used
        // We create a new vector and communicate with the workers to get the correct subproblem bounds
        _subproblemBounds = std::make_shared<std::vector<double>>(2 * _Ns, _maingoSettings->infinity);
#endif
    if (_brancher != nullptr)
        _brancher->setup_two_stage_branching(
            Nx, Ny, w,
            std::shared_ptr<babBase::FathomObserver>(this, [](babBase::FathomObserver *) {}),
            alpha,
            k_max);
#ifdef HAVE_MAINGO_MPI
    MAiNGO_ELSE // switch to WORKER
#endif
        // using a noop deleter to prevent deletion of the original vector
        _subproblemBounds = std::shared_ptr<std::vector<double>>(&subproblemBounds, [](std::vector<double> *) {});
        _solve_sibling_subproblems = solve_sibling_subproblems;
#ifdef HAVE_MAINGO_MPI
    MAiNGO_END_IF
#endif
}

#ifdef HAVE_GROWING_DATASETS
////////////////////////////////////////////////////////////////////////////////////////
// Function for post-processing nodes in heuristic approach with growing datasets
void
BranchAndBound::postprocess(const double& finalUBD)
{
    try {
        // -----------------------------------
        // 0. Initialization
        // -----------------------------------

        // Initialize variables and timing for both Manager and Workers
        double fullLBD;
        SUBSOLVER_RETCODE lbpStatus;

        double startTime, currentTime;
        _timePostpro = 0;

        MAiNGO_IF_BAB_MANAGER
            startTime = get_cpu_time();
#ifdef HAVE_MAiNGO_MPI
        MAiNGO_ELSE    // Worker
            startTime = get_cpu_time();
            // Opening for broadcasts from master
            MPI_Ibcast(&_bcastTag, 1, MPI_INT, 0, MPI_COMM_WORLD, &_bcastReq);
#endif
        MAiNGO_END_IF

        // Change to full dataset (for both Manager and Workers)
        _LBS->change_growing_objective(0);

        MAiNGO_IF_BAB_MANAGER
            // Initialize variables for statistics
            _nNodesProcessedPost = 0;
            _lbdPostpro          = _lbd;
            _nNodesTrackedPost   = _brancher->get_nodes_tracked_for_postprocessing();

            // Sort nodes w.r.t. LBD such that nodes with tightest decisions are processed first if hitting CPU time limit
            _brancher->sort_nodes_for_postprocessing();

            // Inform user about start of post-processing
			_logger->print_message("\n  Entering post-processing with \n", VERB_NORMAL, BAB_VERBOSITY);
            std::ostringstream outstream;
            outstream << "  Best upper bound  = " << std::setprecision(6) << finalUBD << std::endl
                      << "  Final lower bound = " << std::setprecision(6) << _lbd << std::endl
                      << std::endl;
            _logger->print_message(outstream.str(), VERB_NORMAL, BAB_VERBOSITY);
        MAiNGO_END_IF

        // ------------------------- End 0: Initialization ---------------------------------


        // ---------------------------------------------------------------------------------
        // 1-4: Main post-processing loop
        // ---------------------------------------------------------------------------------
        _TERMINATION_TYPE termination = _check_termination_postprocessing(); // For workers always false
        while (termination != _TERMINATED) {

            babBase::BabNode currentNode;

#ifdef HAVE_MAiNGO_MPI
            MPI_Status status;
            MAiNGO_IF_BAB_MANAGER
                // -----------------------------------
                // Check incoming messages from workers
                // -----------------------------------
                // Don't accept node requests if terminated
                if (termination == _TERMINATED_WORKERS_ACTIVE) {
                    const int tagCount = 3;
                    // Allowed are exceptions and solved nodes
                    COMMUNICATION_TAG allowedTags[tagCount] = { TAG_EXCEPTION, TAG_SOLVED_NODE_STATUS_NORMAL, TAG_SOLVED_NODE_STATUS_INFEAS };
                    int flag = 0;
                    // Probe for messages with allowed tags
                    while (!flag) {
                        for (int i = 0; i < tagCount; i++) {
                            MPI_Iprobe(MPI_ANY_SOURCE, allowedTags[i], MPI_COMM_WORLD, &flag, &status);
                            if (flag)
                                break;
                        }
                    }
                }
                else {
                    // Otherwise just check for any incoming tags
                    MPI_Probe(MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, &status);
                }

                if (status.MPI_TAG == TAG_EXCEPTION) {
                    // -----------------------------------
                    // Worker ran into an exception
                    // -----------------------------------
                    MPI_Recv(NULL, 0, MPI_INT, status.MPI_SOURCE, status.MPI_TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                    std::string str = "  Worker ran into exception!";
                    throw MAiNGOMpiException(str, MAiNGOMpiException::ORIGIN_OTHER);
                }
                else if (status.MPI_TAG == TAG_NODE_REQUEST) {
                    // -----------------------------------
                    // Worker requests a new node
                    // -----------------------------------
                    MPI_Recv(NULL, 0, MPI_INT, status.MPI_SOURCE, status.MPI_TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                    _workCount++;
#endif

                // -----------------------------------
                // 1. Node selection:Next entry of vector _nodesPostprocessing
                // -----------------------------------
                currentNode = _brancher->get_next_node_for_postprocessing(_nNodesProcessedPost);
                _nNodesProcessedPost++;

#ifdef HAVE_MAiNGO_MPI
                    // -----------------------------------
                    // Send node to worker
                    // -----------------------------------
                    // Send Request Answer
                    MPI_Ssend(NULL, 0, MPI_INT, status.MPI_SOURCE, TAG_NEW_NODE_NO_INCUMBENT, MPI_COMM_WORLD);
                    // Send new node
                    send_babnode(currentNode, status.MPI_SOURCE);

                    _nodesGivenToWorkers[status.MPI_SOURCE - 1].first = true;
                    _nodesGivenToWorkers[status.MPI_SOURCE - 1].second = currentNode.get_pruning_score();

                    continue;
                }
            MAiNGO_END_IF    // End of MAiNGO_IF_BAB_MANAGER
#endif

#ifdef HAVE_MAiNGO_MPI
            MAiNGO_IF_BAB_WORKER
                // -----------------------------------
                // Receive new node from Manager
                // -----------------------------------

                // Send node request to manager
                MPI_Request node_request;
                MPI_Issend(NULL, 0, MPI_INT, 0, TAG_NODE_REQUEST, MPI_COMM_WORLD, &node_request);

                bool terminate;
                _sync_with_master(node_request, terminate);
                if (terminate)
                    break;

                // Receive request answer
                MPI_Status status;
                MPI_Recv(NULL, 0, MPI_INT, 0, MPI_ANY_TAG, MPI_COMM_WORLD, &status);
                // Receive new node
                recv_babnode(currentNode, 0, _nvar);
#endif
            // -----------------------------------
            // 2. Lower bounding: solve lower bounding problem (LBP) with full dataset to derive a valid lower bound
            // -----------------------------------
            std::vector<double> lbpSolutionPoint;
            lbp::LbpDualInfo dualInfo;

            lbpStatus = _LBS->solve_LBP(currentNode, fullLBD, lbpSolutionPoint, dualInfo);

#ifdef HAVE_MAiNGO_MPI
                // -----------------------------------
                // Send solved node to Manager
                // -----------------------------------

                MPI_Request solutionRequest;
                // Choose communication tag according to node status
                COMMUNICATION_TAG nodeStatus = TAG_SOLVED_NODE_STATUS_NORMAL;
                if (lbpStatus == SUBSOLVER_INFEASIBLE) {
                    nodeStatus = TAG_SOLVED_NODE_STATUS_INFEAS;
                }

                // Send communication request to manager
                MPI_Issend(NULL, 0, MPI_INT, 0, nodeStatus, MPI_COMM_WORLD, &solutionRequest);
                _sync_with_master(solutionRequest, terminate);
                if (terminate) {
                    break;
                }
                if (nodeStatus == TAG_SOLVED_NODE_STATUS_NORMAL) {
                    // Send fullLBD and corresponding node
                    MPI_Ssend(&fullLBD, 1, MPI_DOUBLE, 0, TAG_SOLVED_NODE_LBD, MPI_COMM_WORLD);
                    send_babnode(currentNode, 0);
                }
            MAiNGO_END_IF    // End of MAiNGO_IF_BAB_WORKER
#endif

#ifdef HAVE_MAiNGO_MPI
            MAiNGO_IF_BAB_MANAGER
                // -----------------------------------
                // Receive solved node from Worker
                // -----------------------------------
                // Receive communication request from worker
                MPI_Recv(NULL, 0, MPI_INT, status.MPI_SOURCE, status.MPI_TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                _workCount--;
                _nodesGivenToWorkers[status.MPI_SOURCE - 1].first = false;
                _nodesGivenToWorkers[status.MPI_SOURCE - 1].second = _maingoSettings->infinity;

                // Catch lbpStatus
                COMMUNICATION_TAG nodeStatus = (COMMUNICATION_TAG)status.MPI_TAG;
                if (nodeStatus == TAG_SOLVED_NODE_STATUS_NORMAL) {
                    lbpStatus = SUBSOLVER_FEASIBLE;
                    // Receive fullLBD and corresponding node
                    MPI_Recv(&fullLBD, 1, MPI_DOUBLE, status.MPI_SOURCE, TAG_SOLVED_NODE_LBD, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                    recv_babnode(currentNode, status.MPI_SOURCE, _nvar);
                }
                else if (nodeStatus == TAG_SOLVED_NODE_STATUS_INFEAS) {
                    lbpStatus = SUBSOLVER_INFEASIBLE;
                }
#endif

            // -----------------------------------
            // 3. Update best lower bound
            // -----------------------------------
            // Infeasible nodes and nodes with fullLBD > finalUBD were pruned correctly
            // Update final LBD for all other nodes and print information about change
            if (lbpStatus == SUBSOLVER_FEASIBLE
                && !(babBase::larger_or_equal_within_rel_and_abs_tolerance(fullLBD, finalUBD, _maingoSettings->epsilonR, _maingoSettings->epsilonA)))
            {
                _print_postprocessed_node(currentNode.get_ID(), currentNode.get_pruning_score(), fullLBD);
                _lbdPostpro = std::min(_lbdPostpro, fullLBD);
            }

            // -----------------------------------
            // 4. Check termination
            // -----------------------------------
            currentTime  = get_cpu_time();
            _timePostpro = currentTime - startTime;

            termination  = _check_termination_postprocessing();

            MAiNGO_END_IF    // End of MAiNGO_IF_BAB_MANAGER

        }    // main while loop

        // ----------------- End 1-4: Main post-processing loop ----------------------------

#ifdef HAVE_MAiNGO_MPI
            // ---------------------------------------------------------------------------------
            // Inform workers about termination
            // ---------------------------------------------------------------------------------
        MAiNGO_IF_BAB_MANAGER

            _inform_worker_about_event(BCAST_TERMINATE, /* blocking broadcast */ true);
            // Wait for all workers to get out of the while(true) loop
            MAiNGO_MPI_BARRIER
            // Clean up all pending requests -- it is not the best way, but MPI_Cancel seems to have problems on different operating systems so we do this just to make sure everything is fine
            bool pendingRequests = true;
            while (pendingRequests) {
                int flag = 0;
                MPI_Status status;
                MPI_Iprobe(MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, &flag, &status);
                if (flag) {
                    MPI_Recv(NULL, 0, MPI_INT, status.MPI_SOURCE, status.MPI_TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                }
                else {
                    pendingRequests = false;
                }
            }
            MAiNGO_MPI_BARRIER

        MAiNGO_ELSE

            MAiNGO_MPI_BARRIER    // Wait for all workers to get out of the while(true) loop
            MAiNGO_MPI_BARRIER    // Wait for manager to clean up all pending requests

        MAiNGO_END_IF
#endif
    }
#ifdef HAVE_MAiNGO_MPI
    catch (std::exception& e) {
        MAiNGOMpiException e_mpi("  Error during post-processing.", e, MAiNGOMpiException::ORIGIN_ME);
        _communicate_exception_and_throw(e_mpi);
    }
    catch (...) {
        std::string str;
        MAiNGO_IF_BAB_MANAGER
            str = "  Unknown error during post-processing (Manager).";
        MAiNGO_ELSE
            str = "  Unknown error during post-processing (Worker).";
        MAiNGO_END_IF
            MAiNGOMpiException e(str, MAiNGOMpiException::ORIGIN_ME);
        _communicate_exception_and_throw(e);
    }
#else
    catch (std::exception& e)
    {
        throw MAiNGOException("  Error during post-processing.", e);
    }
    catch (...)
    {
        throw MAiNGOException("  Unknown error during post-processing.");
    }
#endif
}
#endif    // HAVE_GROWING_DATASETS

///////////////////////////////////////////////////////////////////////////////////////
// function processing the current node (pre-processing, LBP, UBP, post-processing)
std::tuple<bool, bool, int, int, double, std::vector<double>, bool, double, std::vector<double>>
BranchAndBound::_process_node(babBase::BabNode &currentNode)
{
    PROFILE_FUNCTION()

    // Prepare output variables
    bool nodeProvenInfeasible = false;
    bool nodeConverged        = false;
    int lbdcnt                = 0;    // output outside needs to increase _lbdcnt by lbdcnt
    int ubdcnt                = 0;    // see above
    double currentLBD         = currentNode.get_pruning_score();
    std::vector<double> lbpSolutionPoint;
    bool foundNewFeasiblePoint = false;
    double ubpObjectiveValue   = _maingoSettings->infinity;
    std::vector<double> ubpSolutionPoint;

#ifdef HAVE_GROWING_DATASETS
    unsigned int indexDataset = currentNode.get_index_dataset();

    _UBS->change_growing_objective(indexDataset);
    _LBS->change_growing_objective(indexDataset);
#endif    // HAVE_GROWING_DATASETS

    // -----------------------------------
    // 2. Node pre-processing: Constraint propagation and Optimization-based bound tightening (OBBT)
    // -----------------------------------
    if ( (_maingoSettings->growing_approach == GROW_APPR_DETERMINISTIC) || (currentNode.get_index_dataset() == 0) ) {
        // Without growing datasets: growing_approach = GROW_APPR_DETERMINISTIC (default) and index dataset == 0 (no augmentation)
        // With growing datasets: Only in this case bound tightening techniques are guaranteed to be correct
        nodeProvenInfeasible = _preprocess_node(currentNode);    // Tightens bounds and possibly proves infeasibilty
    }

    // Infeasible nodes get infinity as currentLBD
    if (nodeProvenInfeasible == false) {    // Only continue with 3-5 if node has not been proven to be infeasible

        // -----------------------------------
        // 3. Lower bounding: solve lower bounding problem (LBP) to derive a better lower bound
        // -----------------------------------
        lbp::LbpDualInfo dualInfo;
        std::tie(nodeProvenInfeasible, nodeConverged, currentLBD, lbpSolutionPoint, dualInfo) = _solve_LBP(currentNode);
        lbdcnt++;
        if (_maingoSettings->growing_useResampling && (currentNode.get_index_dataset()==1)) {
            lbdcnt++; // Within _solve_LBP a second dataset, namely the resampled initial dataset, has been solved
        }

        if ((nodeProvenInfeasible == false) && (nodeConverged == false)) {

            // -----------------------------------
            // 4. Upper bounding: try to find a good feasible point within the current node
            // -----------------------------------
            ubpSolutionPoint = lbpSolutionPoint;
            if (_maingoSettings->LBP_addAuxiliaryVars && !lbpSolutionPoint.empty()) {
                ubpSolutionPoint.resize(_nvarWOaux);
            }
            std::tie(foundNewFeasiblePoint, nodeConverged, ubpObjectiveValue) = _solve_UBP(currentNode, ubpSolutionPoint, currentLBD);
            ubdcnt++;
            if (nodeConverged == false) {

                // -----------------------------------
                // 5. Node post-processing: Duality-based bounds tightening (DBBT) & probing
                // -----------------------------------
                if ((_maingoSettings->growing_approach == GROW_APPR_DETERMINISTIC) || (currentNode.get_index_dataset() == 0)) {
                    // Without growing datasets: growing_approach = GROW_APPR_DETERMINISTIC (default) and index dataset == 0 (no augmentation)
                    // With growing datasets: Only in this case bound tightening techniques are guaranteed to be correct
                    nodeProvenInfeasible = _postprocess_node(currentNode, lbpSolutionPoint, dualInfo);
                }

            }    // end if(nodeConverged==false)
        }    // end if(((nodeProvenInfeasible==false)&&(nodeConverged==false))
    }    // end if(nodeProvenInfeasible==false)

    // Infeasible nodes get infinity as currentLBD
    if (nodeProvenInfeasible) {
        currentLBD = _maingoSettings->infinity;
    }

#if defined(MAiNGO_DEBUG_MODE) && defined(HAVE_GROWING_DATASETS) && !defined(HAVE_MAiNGO_MPI)
    if (currentNode.get_index_dataset() == 0) {
        _currentLBDFull       = currentLBD;
        _lbpSolutionPointFull = lbpSolutionPoint;
    }
#endif

    if (nodeConverged) {
        currentNode.set_pruning_score(currentLBD);
    }

    return std::make_tuple(nodeProvenInfeasible, nodeConverged, lbdcnt, ubdcnt, currentLBD, lbpSolutionPoint, foundNewFeasiblePoint, ubpObjectiveValue, ubpSolutionPoint);
}

void BranchAndBound::_process_siblings(lbp::SiblingResults & siblingResults) {
    int obbtType = -1;  // don't do OBBT
    if (_maingoSettings->BAB_alwaysSolveObbt) {
        if (_foundFeas == true) {
            obbtType = lbp::OBBT_FEASOPT;
        }
        else {
            obbtType = lbp::OBBT_FEAS;
        }
    }
    _solve_sibling_subproblems(siblingResults, _ubd, obbtType);

    if (!siblingResults.feasible) {
        return;
    }
    /**
     * Generate a consistent starting point for upper bounding from the solutions of both sibling subproblems
     * In contrast to nodes obtained from first-stage branching, where we only need to aggregate the x part of subproblem solutions, here we have split second-stage domains.
     * Thus we need to decide on a consistent way to aggregate the solutions of both the x and the y part of solutions from subproblems of both siblings.
     * 
     * There are several possibilities how to do this:
     * 1: solve a single upper bounding problem using the x part of the scenario that is closest to the mean of all x parts from all feasible subproblems of both siblings.
     *    1.1 Either the scenario for which this is the case determines the sibling from which the y part is used (consistency over scenarios with chosen x part, but somewhat biased towards the orthant corresponding to the selected sibling),
     *    1.2 or the scenario average over y parts over both siblings is used (unbiased starting point in parent domain, but likely inconsistent with the selected x part).
     * 2: solve two upper bounding problems, one for each sibling using the above aggregation separately for each sibling.
     *    This is analogous to nodes obtained from first-stage branching, however, it biases search towards the orthant nodes corresponding to the siblings, and is thus somewhat arbitrary.
     * 3: solve 2 Ns upper bounding problems, one for each scenario of each sibling; use the x-parts withouth aggregation and aggregate the y-parts per scenario over both siblings.
     *    While this is costly, the cost seems reasonable, given that 2^k nodes are produced.
     *    However it is likely that the x parts repeat for large Ns, so we might want to impose a minimum distance to ensure that we don't solve the same problem over and over again.
     *    This could be done via clustering algorithms.
     * 
     * In the following we implement 1.1, as it is straightforward and the bias towards the orthant corresponding to the selected sibling is relativized by the fact that the selected x part is somewhat representative of all x parts.
     */

    // initialize x part of solution with mean of xs
    siblingResults.ubpSolutionPoint = std::vector<double>(siblingResults.Nx + siblingResults.Ns * siblingResults.Ny, 0.0);
    for (unsigned int j = 0; j < 2; ++j) {
      for (unsigned int s = 0; s < siblingResults.Ns; s++) {
        auto & solution_s = siblingResults.solutions[j][s];
        if (solution_s.size() == 0) {
          // If the scenario subproblem for one sibling is infeasible, we use the solution of the other sibling, effectively increasing the weight of the feasible sibling.
          solution_s = siblingResults.solutions[(j + 1) % 2][s];
        }
        // average over first-stage variable values of both siblings
        for (unsigned i = 0; i < siblingResults.Nx; i++) {
          siblingResults.ubpSolutionPoint[i] += 0.5 * siblingResults.w[s] * solution_s[i];
        }
      }
    }

    // Find the s for which xs is closest to the mean over the xs in the l2 norm
    auto & lb = siblingResults.get_parent_lower_bounds();
    auto & ub = siblingResults.get_parent_upper_bounds();
    int s_opt         = -1;
    int j_opt         = -1;
    double minRelDist = _maingoSettings->infinity;
    for (unsigned int j = 0; j < 2; ++j) {
      for (unsigned int s = 0; s < siblingResults.Ns; s++) {
        double sumSquaredRelDists = 0.0, dist = 0.0, initGap=0.0, relDist = 0.0;
        auto & solution_s = siblingResults.solutions[j][s];
        if (solution_s.size() == 0) {
          // An infeasible scenario subproblem cannot be selected
          continue;
        }
        for (unsigned int i = 0; i < siblingResults.Nx; i++) {
          dist                = solution_s[i] - siblingResults.ubpSolutionPoint[i];
          initGap             = _upperVarBoundsOrig[i] - _lowerVarBoundsOrig[i];
          relDist             = (initGap > 0) ? (dist / initGap) : 0.;
          sumSquaredRelDists += std::pow(relDist, 2);
        }
        if (sumSquaredRelDists < minRelDist) {
          minRelDist = sumSquaredRelDists;
          s_opt      = s;
          j_opt      = j;
          if (sumSquaredRelDists == 0) {
            break;
          }
        }
      }
    }
    
    // Update the solution point
    for (unsigned int i = 0; i < siblingResults.Nx; i++) {
      siblingResults.ubpSolutionPoint[i] = siblingResults.solutions[j_opt][s_opt][i];
    }
    for (unsigned int s = 0; s < siblingResults.Ns; s++) {
      for (unsigned int i = 0; i < siblingResults.Ny; i++) {
        siblingResults.ubpSolutionPoint[siblingResults.Nx + s * siblingResults.Ny + i] = siblingResults.solutions[j_opt][s][siblingResults.Nx + i];
      }
    }

    // only used for bounds and id
    auto fakeParent = babBase::BabNode(siblingResults.parentPruningScore, lb, ub, 0, -1, siblingResults.siblings[0].get_parent_ID(), siblingResults.siblings[0].get_depth(), false);
    std::tie(siblingResults.foundNewFeasiblePoint, siblingResults.converged, siblingResults.ubpObjectiveValue) = _solve_UBP(fakeParent, siblingResults.ubpSolutionPoint, siblingResults.parentPruningScore);

    if (siblingResults.foundNewFeasiblePoint) {
        #ifdef HAVE_MAiNGO_MPI
            // Check if this feasible point is better than the incumbent & inform manager about it
            if (siblingResults.ubpObjectiveValue < _ubd) {
                _send_incumbent(siblingResults.ubpObjectiveValue, siblingResults.ubpSolutionPoint, fakeParent.get_ID());
            }
        #else
            // Check if this feasible point is better than the incumbent & fathom by value dominance (first remaining tree and then current node):
            _update_incumbent_and_fathom(siblingResults.ubpObjectiveValue, siblingResults.ubpSolutionPoint, fakeParent.get_ID());
        #endif
    }
}

////////////////////////////////////////////////////////////////////////////////////////
// function for pre-processing the current node (constraint propagation + OBBT)
bool
BranchAndBound::_preprocess_node(babBase::BabNode &currentNode)
{
    PROFILE_FUNCTION()

    bool nodeProvenInfeasible = false;

    // -----------------------------------
    // 2a Constraint propagation
    // -----------------------------------
    TIGHTENING_RETCODE conPropStatus = TIGHTENING_UNCHANGED;
    if (_maingoSettings->BAB_constraintPropagation) {
        if (_foundFeas == true) {    // If we already have a feasible point, consider an upper bound for the objective as well
            conPropStatus = _LBS->do_constraint_propagation(currentNode, _ubd);
        }
        else {    // If we do not have a feasible point, use infinity as upper bound
            conPropStatus = _LBS->do_constraint_propagation(currentNode, _maingoSettings->infinity);
        }
    }
    if (_maingoSettings->BAB_verbosity > VERB_NORMAL) {
        _print_one_node(currentNode.get_pruning_score(), currentNode);
    }

    // Check if constraint propagation proved node to be infeasible
    if (conPropStatus == TIGHTENING_INFEASIBLE) {
        
        nodeProvenInfeasible = true;
    }
    // If constraint propagation did not prove node to be infeasible,
    // proceed with OBBT with a probability dependent on the depth of the current node.
    else if (do_based_on_decaying_probability(_maingoSettings->BAB_obbtDecayCoefficient, currentNode.get_depth())) {

        // -----------------------------------
        // 2b Optimization-based bound tightening (OBBT)
        // -----------------------------------
        TIGHTENING_RETCODE obbtStatus = TIGHTENING_UNCHANGED;
        if (_maingoSettings->BAB_alwaysSolveObbt) {
            if (_foundFeas == true) {    // If we already have a feasible point, consider optimality as well
                obbtStatus = _LBS->solve_OBBT(currentNode, _ubd, lbp::OBBT_FEASOPT);
            }
            else {    // If we do not have a feasible point, use only feasibility
                obbtStatus = _LBS->solve_OBBT(currentNode, _ubd, lbp::OBBT_FEAS);
            }
        }
        // Check if OBBT proved node to be infeasible
        if (obbtStatus == TIGHTENING_INFEASIBLE) {
            nodeProvenInfeasible = true;
        }
        if (_maingoSettings->BAB_verbosity > VERB_NORMAL) {
            _print_one_node(currentNode.get_pruning_score(), currentNode);
        }
    }

    return nodeProvenInfeasible;
}


////////////////////////////////////////////////////////////////////////////////////////
// function invoking the LBS to solve the lower bounding problem
std::tuple<bool /*nodeProvenInfeasible*/, bool /*nodeConverged*/, double /*currentLBD*/, std::vector<double> /*lbpSolutionPoint*/, lbp::LbpDualInfo /*dualInfo*/>
BranchAndBound::_solve_LBP(const babBase::BabNode &currentNode)
{

    bool nodeProvenInfeasible = false;
    bool nodeConverged        = false;
    const double parentLBD    = currentNode.get_pruning_score();
    double currentLBD         = parentLBD;
    std::vector<double> lbpSolutionPoint;
    lbp::LbpDualInfo dualInfo;

    SUBSOLVER_RETCODE lbpStatus = _LBS->solve_LBP(currentNode, currentLBD, lbpSolutionPoint, dualInfo);

#ifdef HAVE_GROWING_DATASETS
    if (_maingoSettings->growing_useResampling && (currentNode.get_index_dataset() == 1)) {
        double resampledLBD = parentLBD;

        // Using input and output dummies to not overwrite information obtained with initial dataset
        lbp::LbpDualInfo dualInfo2;
        std::vector<double> lbpSolutionPoint2;

        _LBS->change_growing_objective_for_resampling();
        SUBSOLVER_RETCODE lbpStatus2 = _LBS->solve_LBP(currentNode, resampledLBD, lbpSolutionPoint2, dualInfo2);
        if ((_maingoSettings->growing_approach > GROW_APPR_DETERMINISTIC) || (resampledLBD > currentLBD) ) {
            // Do not decrease (weaken) currentLBD when using deterministic approach
            // But only correct currentLBD when using heuristic approaches
            currentLBD = (currentLBD + resampledLBD) / 2;
        }

        // Reset to former dataset
        _LBS->change_growing_objective(currentNode.get_index_dataset());
    }
#endif    // HAVE_GROWING_DATASETS

    if (currentLBD < parentLBD) {   // GCOVR_EXCL_START
        std::ostringstream outstr;
        outstr << "  LBD obtained for node " << currentNode.get_ID() << " is lower than LBD of its parent node. Using parent LBD." << std::endl;
        _logger->print_message(outstr.str(), VERB_ALL, BAB_VERBOSITY);

        currentLBD = parentLBD;
    }
    // GCOVR_EXCL_STOP

    // Check if LBP proved node to be infeasible
    if (lbpStatus == SUBSOLVER_INFEASIBLE) {    // Ok, exit DBBT loop and just forget node
        currentLBD           = _maingoSettings->infinity;
        nodeProvenInfeasible = true;
    }

    // Check if LBP proved that node cannot contain a better point
    if (babBase::larger_or_equal_within_rel_and_abs_tolerance(currentLBD, _ubd, _maingoSettings->epsilonR, _maingoSettings->epsilonA)) {    // Ok, fathomed by value dominance

        std::ostringstream outstr;
        outstr << "  Node #" << currentNode.get_ID() << " converged with LBD " << currentLBD << " to UBD " << _ubd << std::endl;
        _logger->print_message(outstr.str(), VERB_ALL, BAB_VERBOSITY);

        nodeConverged = true;
    }

#if defined(MAiNGO_DEBUG_MODE) && defined(HAVE_GROWING_DATASETS) && !defined(HAVE_MAiNGO_MPI)
    //catch information for full dataset (!= reduced dataset) for this node
    lbp::LbpDualInfo dualInfoFull;    //dummy for calling solve_LBP

    if (currentNode.get_index_dataset() > 0) {
        _currentLBDFull                 = parentLBD;
        SUBSOLVER_RETCODE lbpStatusFull = _LBSFull->solve_LBP(currentNode, _currentLBDFull, _lbpSolutionPointFull, dualInfoFull);
    }
#endif
    return std::make_tuple(nodeProvenInfeasible, nodeConverged, currentLBD, lbpSolutionPoint, dualInfo);
}


////////////////////////////////////////////////////////////////////////////////////////
// function invoking the UBS to solve the upper bounding problem
std::tuple<bool /*foundNewFeasiblePoint*/, bool /*nodeConverged*/, double /*ubpObjectiveValue*/>
BranchAndBound::_solve_UBP(const babBase::BabNode &currentNode, std::vector<double> &ubpSolutionPoint, const double currentLBD)
{
    PROFILE_FUNCTION()

    bool foundNewFeasiblePoint  = false;
    bool nodeConverged          = false;
    double ubpObjectiveValue    = _maingoSettings->infinity;
    SUBSOLVER_RETCODE ubpStatus = _UBS->solve(currentNode, ubpObjectiveValue, ubpSolutionPoint);

    // Check if we found a feasible point
    if (ubpStatus == SUBSOLVER_FEASIBLE) {
        foundNewFeasiblePoint = true;
        // Sanity check to detect inconsistent bounding operations
        if ((ubpObjectiveValue < currentLBD - _maingoSettings->epsilonA) && (ubpObjectiveValue < currentLBD - std::fabs(ubpObjectiveValue) * _maingoSettings->epsilonR)) {   // GCOVR_EXCL_START
            if (ubpObjectiveValue > -_maingoSettings->infinity) {
#ifdef HAVE_GROWING_DATASETS
                if ((_maingoSettings->growing_approach > GROW_APPR_DETERMINISTIC)
                    && ((currentNode.get_index_dataset() > 0) || currentNode.get_augment_data()) ) {
                    // May also happen for full dataset if LBD is inherited from parent node with reduced dataset
                    babBase::BabNode newNode = currentNode;
                    newNode.set_pruning_score(-_maingoSettings->infinity);
                    unsigned int newDataIndex = _augment_dataset(newNode);
                    _brancher->add_node_with_new_data_index(newNode, newDataIndex);

                    std::ostringstream outstr;
                    outstr << "  Warning: Upper bound < heuristic lower bound in node " << currentNode.get_ID() << " . Augmenting dataset and resetting lower bound to -infinity..." << std::endl;
                    _logger->print_message(outstr.str(), VERB_NORMAL, BAB_VERBOSITY);
                }
                else {
#endif    // HAVE_GROWING_DATASETS
                    std::ostringstream errmsg;
                    errmsg << std::endl
                           << "  Error while checking objective returned by upper bounding solver: Upper bound < lower bound:" << std::endl;
                    errmsg << "  LBD = " << std::setprecision(16) << currentLBD << std::endl
                           << "UBD = " << ubpObjectiveValue << std::endl;
#ifdef HAVE_MAiNGO_MPI
                    throw MAiNGOMpiException(errmsg.str(), currentNode, MAiNGOMpiException::ORIGIN_ME);
#else
                    throw MAiNGOException(errmsg.str());
#endif
#ifdef HAVE_GROWING_DATASETS
                } // else
#endif // HAVE_GROWING_DATASETS

            }
            else {
                ubpObjectiveValue = _maingoSettings->infinity;
                std::ostringstream outstr;
                outstr << "  Warning: UBD found in node " << currentNode.get_ID() << " is lower than the MAiNGO infinity value " << -_maingoSettings->infinity << ".\n";
                outstr << "           Please consider scaling your objective function.\n";
                _logger->print_message(outstr.str(), VERB_NORMAL, BAB_VERBOSITY);
            }
        }
        // GCOVR_EXCL_STOP

#ifdef HAVE_MAiNGO_MPI
        // Check if this feasible point is better than the incumbent & inform manager about it
        if (ubpObjectiveValue < _ubd) {
            _send_incumbent(ubpObjectiveValue, ubpSolutionPoint, currentNode.get_ID());
        }
#endif

        // Check if this feasible point is better than the incumbent & fathom by value dominance (first remaining tree and then current node):
        if (babBase::larger_or_equal_within_rel_and_abs_tolerance(currentLBD, std::min(_ubd, ubpObjectiveValue), _maingoSettings->epsilonR, _maingoSettings->epsilonA)) {    // Ok, fathomed by value dominance

            std::ostringstream outstr;
            outstr << "  Node #" << currentNode.get_ID() << " converged with LBD " << currentLBD << " to UBD " << _ubd << std::endl;
            _logger->print_message(outstr.str(), VERB_ALL, BAB_VERBOSITY);

            nodeConverged = true;
        }
    }

    return std::make_tuple(foundNewFeasiblePoint, nodeConverged, ubpObjectiveValue);
}


////////////////////////////////////////////////////////////////////////////////////////
// Function for post-processing the current node. Includes bound DBBT and probing
bool
BranchAndBound::_postprocess_node(babBase::BabNode &currentNode, const std::vector<double> &lbpSolutionPoint, const lbp::LbpDualInfo &dualInfo)
{
    PROFILE_FUNCTION()

    bool nodeProvenInfeasible = false;
    if ((dualInfo.multipliers.size() != _nvar) || (lbpSolutionPoint.size() != _nvar)) {    // We can only do DBBT or probing if we have multipliers and a solution point from LBP
        // No multipliers or no valid LBD available --> cannot proceed with post-processing --> node not converged, return
    }
    else {
        TIGHTENING_RETCODE status = _LBS->do_dbbt_and_probing(currentNode, lbpSolutionPoint, dualInfo, _ubd);
        if (_maingoSettings->BAB_verbosity > VERB_NORMAL) {
            _print_one_node(currentNode.get_pruning_score(), currentNode);
        }
        switch (status) {
            case TIGHTENING_INFEASIBLE:
                nodeProvenInfeasible = true;
                break;
            case TIGHTENING_UNCHANGED:
            case TIGHTENING_CHANGED:
                break;
        }
    }

    return nodeProvenInfeasible;
}


////////////////////////////////////////////////////////////////////////////////////////
// function updating the incumbent, sending the information to the LBS and fathoming nodes
void
BranchAndBound::_update_incumbent_and_fathom(const double solval, const std::vector<double> sol, const unsigned int currentNodeID)
{


    // Update incumbent value
    if (solval < _ubd) {
#ifdef HAVE_MAiNGO_MPI
        // Inform workers that a feasible point was found
        if (!_foundFeas) {
            _inform_worker_about_event(BCAST_FOUND_FEAS, /*non-blocking*/ false);
        }
#endif
        _foundFeas  = true;
        _firstFound = _iterations;
        // Only print line if new incumbent is better than the old one by more than the specified tolerance
        if (!babBase::larger_or_equal_within_rel_and_abs_tolerance(solval, _ubd, _maingoSettings->epsilonR, _maingoSettings->epsilonA)) {
            _printNewIncumbent = true;
        }

        _ubd             = solval;
        _incumbent       = sol;
        _LBS->update_incumbent_LBP(_incumbent);

#ifdef HAVE_MAiNGO_MPI
        _informedWorkerAboutIncumbent = std::vector<bool>(_nProcs - 1, false);
#endif

#ifdef HAVE_GROWING_DATASETS
        // Before pruning, update list of nodes for post-processing (if post-processing turned on)
        if ((_maingoSettings->growing_approach > GROW_APPR_DETERMINISTIC) && (_maingoSettings->growing_maxTimePostprocessing > 0))
        {
            _brancher->update_nodes_for_postprocessing(solval);
        }
#endif    // HAVE_GROWING_DATASETS

        // Inform _brancher about new incumbent
        size_t nodesBefore         = _brancher->get_nodes_in_tree();
        double smallestFathomedLBD = _brancher->decrease_pruning_score_threshold_to(_ubd);    // Here, nodes with lbd exceeding the new _ubd are fathomed
        _bestLbdFathomed           = std::min(smallestFathomedLBD, _bestLbdFathomed);
        _nNodesFathomed += nodesBefore - _brancher->get_nodes_in_tree();
        _nNodesDeleted += nodesBefore - _brancher->get_nodes_in_tree();
        _nNodesLeft = _brancher->get_nodes_in_tree();
    }
}


////////////////////////////////////////////////////////////////////////////////////////
// function for updating the lowest lower bound
void
BranchAndBound::_update_lowest_lbd()
{

    _lbdOld = _lbd;
#ifdef HAVE_MAiNGO_MPI
    if (_brancher->get_nodes_in_tree() > 0 || _workCount > 0) {
#endif
        if (_brancher->get_nodes_in_tree() > 0) {
            // This is to make sure that in case we needed to throw a node out because of node size, the proven _lbd does not get better than this node
            _lbd = std::min(_brancher->get_lowest_pruning_score(), _bestLbdFathomed);
#ifdef HAVE_MAiNGO_MPI
            double minValWorkers = std::min_element(_nodesGivenToWorkers.begin(), _nodesGivenToWorkers.end(), maingo::WorkerNodeComparator())->second;
            _lbd                 = std::min(_lbd, minValWorkers);
#endif
        }
#ifdef HAVE_MAiNGO_MPI
        else {    // Case where there are no nodes in the tree but workers are still working
            _lbd                 = std::min(_lbd, _bestLbdFathomed);
            double minValWorkers = std::min_element(_nodesGivenToWorkers.begin(), _nodesGivenToWorkers.end(), maingo::WorkerNodeComparator())->second;
            _lbd                 = std::min(_lbd, minValWorkers);
        }
    }
#endif
    else {
        _lbd = _bestLbdFathomed;
    }
}


#ifdef HAVE_GROWING_DATASETS
////////////////////////////////////////////////////////////////////////////////////////
// auxiliary function calling augmentation rule CONST
bool
BranchAndBound::_call_augmentation_rule_const(const int depth)
{
    // Augment nodes in depth which is a multiple of freq
    return !((int)fmod(depth, (double)_maingoSettings->growing_augmentFreq));
}


////////////////////////////////////////////////////////////////////////////////////////
// auxiliary function calling augmentation rule SCALING
bool
BranchAndBound::_call_augmentation_rule_scaling(const int indexDataset, const double redLBD)
{
    // Augment if linear scaling of reduced LB to full LB suggests pruning
    double scaledLBD = _maingoSettings->growing_augmentWeight * redLBD * (double)(*_datasets)[0] / (double)(*_datasets)[indexDataset];
    return babBase::larger_or_equal_within_rel_and_abs_tolerance(scaledLBD, _ubd, _maingoSettings->epsilonR, _maingoSettings->epsilonA);
}


////////////////////////////////////////////////////////////////////////////////////////
// function for evaluating the lower bounding solution point for the validation set
// i.e., for calculating the out-of-sample lower bound
double
BranchAndBound::_evaluate_lower_bound_for_validation_set(const babBase::BabNode& currentNode, const std::vector<double>& lbpSolutionPoint, const double currentLBD)
{
    // Sanity check
    if (currentNode.get_index_dataset() == 0) {
        std::ostringstream errmsg;
        errmsg << "  Error in BaB - evaluating lower bound for validation set: validation set for full dataset is empty by definition." << std::endl;
        throw MAiNGOException(errmsg.str());
    }

    double oosLBD = _maingoSettings->infinity;

    // Evaluate validation set
    _LBS->change_growing_objective(-currentNode.get_index_dataset());
    _LBS->evaluate_LBP(currentNode, lbpSolutionPoint, oosLBD);

    // Reset current dataset to former training set
    _LBS->change_growing_objective(currentNode.get_index_dataset());

    return oosLBD;
}


////////////////////////////////////////////////////////////////////////////////////////
// function for calculating approximated lower bound as combination of reduced and out-of-sample lower bound
double
BranchAndBound::_calculate_combined_lower_bound(const double currentLBD, const double oosLBD, const unsigned int indexDataset)
{
    double combiLBD;

    // approximate lower bound by convex combination of currentLBD and out-of-sample LBD
    if (_maingoSettings->growing_approach == GROW_APPR_MSEHEURISTIC) {
        // objective of LBP is mean squared error
        // Thus, use dataRatio * reduced LBD + (1-dataRatio) * out-of-sample LBD
        double dataRatio = (double)(*_datasets)[indexDataset] / (double)(*_datasets)[0];
        combiLBD = dataRatio * currentLBD + (1 - dataRatio) * oosLBD;
    }
    else {
        // objective of LBP is summed squared error
        // Thus, use reduced LBD + out-of-sample LBD
        combiLBD = currentLBD + oosLBD;
    }

    return combiLBD;
}


////////////////////////////////////////////////////////////////////////////////////////
// auxiliary function calling augmentation rule OOS
bool
BranchAndBound::_call_augmentation_rule_oos(const double oosLBD)
{
    // Augment if out-of-sample LB suggests pruning
    return babBase::larger_or_equal_within_rel_and_abs_tolerance(oosLBD, _ubd, _maingoSettings->epsilonR, _maingoSettings->epsilonA);
}


////////////////////////////////////////////////////////////////////////////////////////
// auxiliary function calling augmentation rule COMBI
bool
BranchAndBound::_call_augmentation_rule_combi(const double combiLBD)
{
    // Augment if combined LB suggests pruning
    return babBase::larger_or_equal_within_rel_and_abs_tolerance(combiLBD, _ubd, _maingoSettings->epsilonR, _maingoSettings->epsilonA);
}


////////////////////////////////////////////////////////////////////////////////////////
// auxiliary function calling augmentation rule TOL
bool
BranchAndBound::_call_augmentation_rule_tol(const double redLBD, const double combiLBD)
{
    // Augment if upper bound is smaller than the lower bound used for pruning plus an additional absolute or relative tolerance
    if (_maingoSettings->growing_approach > GROW_APPR_DETERMINISTIC) {
        // Combined lower bound used for pruning
        return babBase::larger_or_equal_within_rel_and_abs_tolerance(combiLBD, _ubd, _maingoSettings->growing_augmentTol, _maingoSettings->growing_augmentTol);
    }
    else {
        // Reduced lower bound used for pruning
        return babBase::larger_or_equal_within_rel_and_abs_tolerance(redLBD, _ubd, _maingoSettings->growing_augmentTol, _maingoSettings->growing_augmentTol);
    }
}


////////////////////////////////////////////////////////////////////////////////////////
// function which checks whether to augment the dataset
bool
BranchAndBound::_check_whether_to_augment(const babBase::BabNode &currentNode, const std::vector<double> &lbpSolutionPoint, const double redLBD, const double oosLBD, const double combiLBD)
{
    bool augment = false;

    if (!(currentNode.get_ID() == 1 || currentNode.get_augment_data() == true || currentNode.get_index_dataset() == 0)) {
        // Do not augment in root node, if data already augmented in this node, or if already full dataset considered
        // Otherwise follow augmentation rule
        switch (_maingoSettings->growing_augmentRule) {
            case AUG_RULE_CONST: {
                augment = _call_augmentation_rule_const(currentNode.get_depth());
                break;
            }
            case AUG_RULE_SCALING: {
                augment = _call_augmentation_rule_scaling(currentNode.get_index_dataset(), redLBD);
                break;
            }
            case AUG_RULE_OOS: {
                augment = _call_augmentation_rule_oos(oosLBD);
                break;
            }
            case AUG_RULE_COMBI: {
                augment = _call_augmentation_rule_combi(combiLBD);
                break;
            }
            case AUG_RULE_TOL: {
                augment = _call_augmentation_rule_tol(redLBD, combiLBD);
                break;
            }
            case AUG_RULE_SCALCST: {
                augment = _call_augmentation_rule_const(currentNode.get_depth())
                          || _call_augmentation_rule_scaling(currentNode.get_index_dataset(), redLBD);
                break;
            }
            case AUG_RULE_OOSCST: {// Augment if OOS or CONST is triggered
                augment = _call_augmentation_rule_const(currentNode.get_depth())
                          || _call_augmentation_rule_oos(oosLBD);
                break;
            }
            case AUG_RULE_COMBICST: {
                augment = _call_augmentation_rule_const(currentNode.get_depth())
                    || _call_augmentation_rule_combi(combiLBD);
                break;
            }
            case AUG_RULE_TOLCST: {// Augment if TOL or CONST is triggered
                augment = _call_augmentation_rule_const(oosLBD)
                    || _call_augmentation_rule_tol(redLBD, combiLBD);
                break;
            }
            default: {
                break;
            }
        }
    }

    return augment;
}


////////////////////////////////////////////////////////////////////////////////////////
// function for augmenting dataset of node
unsigned int
BranchAndBound::_augment_dataset(babBase::BabNode &currentNode)
{
    unsigned int newIndex  = currentNode.get_index_dataset();
    newIndex++;

    // Check whether next dataset is already the full dataset
    if(newIndex >= (*_datasets).size()) {
        newIndex = 0;
    }

    return newIndex;
}
#endif    // HAVE_GROWING_DATASETS


////////////////////////////////////////////////////////////////////////////////////////
// function which checks whether it is necessary to activate scaling within the LBD solver. This is a heuristic approach, which does not affect any deterministic optimization assumptions
void
BranchAndBound::_check_if_more_scaling_needed()
{

    if (!_logger->reachedMinNodeSize) {
        if (mc::isequal(_lbd, _lbdOld, mc::machprec(), mc::machprec())) {    // If the lbd did not change enough increase the counter
            _lbdNotChanged++;
        }
        else {
            _lbdNotChanged = 0;
        }
        // If the lbd did not change for at least LBP_activateMoreScaling iterations, scaling was not yet activated (checked before going into this function) and the difference between lowest lbd and current best ubd is small enough, we activate more scaling in the LBS
        if (_lbdNotChanged > _maingoSettings->LBP_activateMoreScaling && (_lbd >= (_ubd - 1E-2) || _lbd >= (_ubd - std::fabs(_ubd) * 1E-1))) {  // GCOVR_EXCL_START
            _LBS->activate_more_scaling();
            _moreScalingActivated = true;
            _lbdNotChanged        = 0;
#ifdef HAVE_MAiNGO_MPI
            _inform_worker_about_event(BCAST_SCALING_NEEDED, true);
#endif
            if (_maingoSettings->LBP_solver > 1) {    // LBP_solver = 0 is MAiNGO default, LBP_solver = 1 is interval-based
                _logger->print_message("  Warning: Additional scaling in the lower bounding solver activated.\n", VERB_NORMAL, BAB_VERBOSITY, LBP_VERBOSITY);
            }
        }
        // GCOVR_EXCL_STOP
    }
}


////////////////////////////////////////////////////////////////////////////////////////
// function for displaying the rows of the B&B output and saving them to logs
void
BranchAndBound::_display_and_log_progress(const double currentNodeLBD, const babBase::BabNode &currentNode)
{

#ifndef HAVE_MAiNGO_MPI
    int _workCount = 0;
#endif
    // Determine whether to print due to a special occasion
    bool solved               = (_nNodesLeft == 0 && _workCount == 0);
    bool maxNodesReached      = (_nNodesLeft >= _maingoSettings->BAB_maxNodes && _workCount == 0);
    bool maxTimeReached       = (_timePassed >= _maingoSettings->maxTime && _workCount == 0);
    bool maxwTimeReached       = (_wtimePassed >= _maingoSettings->maxwTime && _workCount == 0);
    bool maxIterationsReached = (_iterations >= _maingoSettings->BAB_maxIterations && _workCount == 0);
    bool specialOccasion      = _printNewIncumbent || solved || maxNodesReached || maxTimeReached || maxwTimeReached || maxIterationsReached || _iterations == 1;
#if defined(MAiNGO_DEBUG_MODE) && defined(HAVE_GROWING_DATASETS)
    specialOccasion = specialOccasion || currentNode.get_augment_data();
#endif
    bool printToStream = specialOccasion || (!((int)fmod((double)_iterations, (double)_maingoSettings->BAB_printFreq)));
    bool printToLog    = specialOccasion || (!((int)fmod((double)_iterations, (double)_maingoSettings->BAB_logFreq)));

    std::ostringstream strout;
    std::ostringstream stroutCsv;
    if (_maingoSettings->BAB_verbosity >= VERB_NORMAL) {
        if (_linesprinted == 0 || !((int)fmod((double)_linesprinted, (double)_iterationsgap))) {
            strout << "  " << std::setw(9) << "Iteration"
                   << "  "
#ifdef MAiNGO_DEBUG_MODE
                   << std::setw(9) << " NodeId  "
                   << "  "
                   << std::setw(15) << "NodeLBD  "
                   << "  "
#endif
#ifdef HAVE_GROWING_DATASETS
                   << std::setw(6) << "   NoData"
                   << std::setw(1)
                   << "  "
#endif    // HAVE_GROWING_DATASETS
                   << std::setw(15) << "LBD      "
                   << "  "
                   << std::setw(15) << "UBD      "
                   << "  "
                   << std::setw(9) << "NodesLeft"
                   << "  "
                   << std::setw(15) << "AbsGap   "
                   << "  "
                   << std::setw(15) << "RelGap   "
                   << "  "
                   << std::setw(15) << "CPU     "
                   << "  "
                   << std::setw(15) << "Wall     "
                   << "  "
                   << std::endl;
            if (_linesprinted == 0) {
                _linesprinted = 1;    // We start with _iterations = 1
            }
            else {
                _linesprinted = 0;    // Do not count intermediate header lines
            }
        }
        if (printToStream || printToLog) {
            strout.setf(std::ios_base::scientific);
            stroutCsv.setf(std::ios_base::scientific);
            if (_printNewIncumbent && _firstFound != 0) {    // Mark line with * in case a new incumbent was found in this iteration
                strout << "  *";
            }
            else {
                strout << "   ";
            }
            strout << std::setw(8) << _iterations << "  "
#ifdef MAiNGO_DEBUG_MODE
                   << std::setw(9) << currentNode.get_ID() << "  "
                   << std::setw(15) << currentNodeLBD << "  "
#endif
#ifdef HAVE_GROWING_DATASETS
                   << std::setw(6) << (*_datasets)[currentNode.get_index_dataset()]
                   << "  ";
            if (currentNode.get_augment_data()) {
                strout << "A";
            }
            else {
                strout << "B";
            }
            strout << "  "
#endif    // HAVE_GROWING_DATASETS
                   << std::setw(15) << _lbd << "  "
                   << std::setw(15) << _ubd << "  "
                   << std::setw(9) << _nNodesLeft << "  "
                   << std::setw(15) << _ubd - _lbd << "  ";
            if (mc::isequal(_ubd, 0, mc::machprec(), mc::machprec())) {
                strout << std::setw(15) << "N/A"
                       << "  ";
            }
            else {
                strout << std::setw(15) << (_ubd - _lbd) / std::fabs(_ubd) << "  ";
            }
            strout << std::setw(15) << _timePassed << "  " 
                   << std::setw(15) << _wtimePassed << "  " << std::endl;
            strout.unsetf(std::ios_base::scientific);
            if (_maingoSettings->writeCsv) {
                stroutCsv << std::setw(8) << _iterations << ","
#ifdef MAiNGO_DEBUG_MODE
                          << std::setw(9) << currentNode.get_ID() << ","
                          << std::setw(15) << currentNodeLBD << ","
#endif
#ifdef HAVE_GROWING_DATASETS
                          << std::setw(6) << (*_datasets)[currentNode.get_index_dataset()]
                          << "  ";
                if (currentNode.get_augment_data()) {
                    stroutCsv << "A";
                }
                else {
                    stroutCsv << "B";
                }
                stroutCsv << "  "
#endif    // HAVE_GROWING_DATASETS
                          << std::setw(15) << _lbd << ","
                          << std::setw(15) << _ubd << ","
                          << std::setw(9) << _nNodesLeft << ","
                          << std::setw(15) << _ubd - _lbd << ",";
                if (mc::isequal(_ubd, 0, mc::machprec(), mc::machprec())) {
                    stroutCsv << std::setw(15) << "N/A"
                              << ",";
                }
                else {
                    stroutCsv << std::setw(15) << (_ubd - _lbd) / std::fabs(_ubd) << ",";
                }
                stroutCsv << std::setw(15) << _timePassed << ","
                          << std::setw(15) << _wtimePassed << std::endl;
                stroutCsv.unsetf(std::ios_base::scientific);
            }
        }
        _linesprinted++;
        if (printToStream) {
            // This is done instead of print_message, since the logging freq and print freq may differ
            _logger->print_message_to_stream_only(strout.str());
        }
    }

    // Save information if we want a log or csv file
    if (specialOccasion || printToLog) {
        if ((_maingoSettings->loggingDestination == LOGGING_FILE) || (_maingoSettings->loggingDestination == LOGGING_FILE_AND_STREAM)) {
            _logger->babLine.push(strout.str());
        }
        if (_maingoSettings->writeCsv) {
            _logger->babLineCsv.push(stroutCsv.str());
        }
    }
    if ((_maingoSettings->writeToLogSec > 0) && (((double)_timePassed) / ((double)_maingoSettings->writeToLogSec) > _writeToLogEverySec)) {
        if ((_maingoSettings->loggingDestination == LOGGING_FILE) || (_maingoSettings->loggingDestination == LOGGING_FILE_AND_STREAM)) {
            _logger->write_all_lines_to_log();
        }
        if (_maingoSettings->writeCsv) {
            _logger->write_all_iterations_to_csv();
        }
        _writeToLogEverySec++;
    }
    _printNewIncumbent = false;
}


#if defined(MAiNGO_DEBUG_MODE) && defined(HAVE_GROWING_DATASETS)
////////////////////////////////////////////////////////////////////////////////////////
// function for printing the current node to a separate log file
void
BranchAndBound::_log_nodes(const babBase::BabNode &currentNode, const double currentNodeLbd, const double currentNodeUbd, const std::vector<double> lbpSolutionPoint)
{

#ifndef HAVE_MAiNGO_MPI
    int _workCount = 0;
#endif
    // Print whenever B&B progress is logged
    bool solved               = (_nNodesLeft == 0 && _workCount == 0);
    bool maxNodesReached      = (_nNodesLeft >= _maingoSettings->BAB_maxNodes && _workCount == 0);
    bool maxTimeReached       = (_timePassed >= _maingoSettings->maxTime && _workCount == 0);
    bool maxIterationsReached = (_iterations >= _maingoSettings->BAB_maxIterations && _workCount == 0);
    bool specialOccasion      = _printNewIncumbent || solved || maxNodesReached || maxTimeReached || maxIterationsReached || _iterations == 1;
    specialOccasion           = specialOccasion || currentNode.get_augment_data();
    bool printToLog           = specialOccasion || (!((int)fmod((double)_iterations, (double)_maingoSettings->BAB_logFreq)));

    std::ostringstream strout;
    std::ofstream logFile;
    std::string fileName = "maingoNodes.log";

    if (_iterations == 1) {
        // Create new file
        logFile.open(fileName, std::ios::out);
        logFile.close();

        // Print header
        strout << "  " << std::setw(9) << "Iteration"
               << "  "
               << std::setw(9) << " NodeId  "
               << "  "
               << std::setw(6) << "Depth"
               << "  "
               << std::setw(9) << "NoData"
               << "  "
               << std::setw(15) << "NodeLB_red  "
               << "  "
               << std::setw(15) << "NodeLB_full "
               << "  "
               << std::setw(15) << "NodeLB_valid "
               << "  "
               << std::setw(15) << "LB      "
               << "  "
               << std::setw(15) << "NodeUB   "
               << "  "
               << std::setw(15) << "UB      "
               << "  ";
        for (size_t i = 0; i < _incumbent.size(); i++) {
            strout << std::setw(9) << "lb["
                   << i << "]    "
                   << "  ";
        }
        for (size_t i = 0; i < _incumbent.size(); i++) {
            strout << std::setw(9) << "ub["
                   << i << "]    "
                   << "  ";
        }
        for (size_t i = 0; i < _incumbent.size(); i++) {
            strout << std::setw(9) << "pointLb["
                   << i << "]    "
                   << "  ";
        }
        for (size_t i = 0; i < _incumbent.size(); i++) {
            strout << std::setw(12) << "pointLbFull["
                   << i << "]"
                   << "  ";
        }
        strout << std::endl;
    }

    // Information of current node
    std::vector<double> lbdVar = currentNode.get_lower_bounds();
    std::vector<double> ubdVar = currentNode.get_upper_bounds();
    if (printToLog) {
        strout.setf(std::ios_base::scientific);
        strout << std::setw(9) << _iterations << "  "
               << std::setw(9) << currentNode.get_ID() << "  "
               << std::setw(6) << currentNode.get_depth() << "  "
               << std::setw(6) << (*_datasets)[currentNode.get_index_dataset()].size()
               << "  ";
        if (currentNode.get_augment_data()) {
            strout << "A";
        }
        else {
            strout << "B";
        }
        strout << "  "
               << std::setw(15) << currentNodeLbd << "  "
               << std::setw(15) << _currentLBDFull << "  "
               << std::setw(15) << _currentLBDValid << "  "
               << std::setw(15) << _lbd << "  "
               << std::setw(15) << currentNodeUbd << "  "
               << std::setw(15) << _ubd << "  ";
        for (size_t i = 0; i < _incumbent.size(); i++) {
            strout << std::setw(15) << lbdVar[i] << "  ";
        }
        for (size_t i = 0; i < _incumbent.size(); i++) {
            strout << std::setw(15) << ubdVar[i] << "  ";
        }
        if (lbpSolutionPoint.size() > 0) {    // Feasible point found
            for (size_t i = 0; i < _incumbent.size(); i++) {
                strout << std::setw(15) << lbpSolutionPoint[i] << "  ";
            }
        }
        else {    // No feasible point found
            for (size_t i = 0; i < _incumbent.size(); i++) {
                strout << std::setw(15) << "N/A"
                       << "  ";
            }
        }
        if (_lbpSolutionPointFull.size() > 0) {    // Feasible point found
            for (size_t i = 0; i < _incumbent.size(); i++) {
                strout << std::setw(15) << _lbpSolutionPointFull[i] << "  ";
            }
        }
        else {    // No feasible point found
            for (size_t i = 0; i < _incumbent.size(); i++) {
                strout << std::setw(15) << "N/A"
                       << "  ";
            }
        }
        strout << std::endl;
        strout.unsetf(std::ios_base::scientific);

        // Write line to separate log file
        logFile.open(fileName, std::ios::app);
        logFile << strout.str();
        logFile.close();
    }
}
#endif

#ifdef HAVE_GROWING_DATASETS
////////////////////////////////////////////////////////////////////////////////////////
// function for printing post-processing information of one node
void
BranchAndBound::_print_postprocessed_node(const int ID, const double oldLBD, const double newLBD)
{
    std::ostringstream outstr;
    outstr << "  Lower bound of NODE " << std::setw(9) << ID << " changed from " << std::setw(10) << std::setprecision(6) << oldLBD
           << " to " << std::setw(10) << std::setprecision(6) << newLBD << std::endl;
    _logger->print_message(outstr.str(), VERB_NORMAL, BAB_VERBOSITY);
}
#endif // HAVE_GROWING_DATASETS


////////////////////////////////////////////////////////////////////////////////////////
void
BranchAndBound::_print_one_node(const double theLBD, const babBase::BabNode &theNode)
{
    std::ostringstream outstr;
    outstr << "  NODE " << theNode.get_ID() << "  has lbd (inherited from parent) =" << std::setprecision(16) << theLBD << std::endl;
    for (unsigned int i = 0; i < _nvar; i++) {
        outstr << "  " << std::setprecision(16) << "var " << i + 1 << " " << theNode.get_lower_bounds()[i] << "..." << theNode.get_upper_bounds()[i] << std::endl;
    }
    _logger->print_message(outstr.str(), VERB_ALL, BAB_VERBOSITY);
}


////////////////////////////////////////////////////////////////////////////////////////
// function for checking termination
BranchAndBound::_TERMINATION_TYPE
BranchAndBound::_check_termination()
{

#ifdef HAVE_MAiNGO_MPI
    MAiNGO_IF_BAB_WORKER
        // Workers get their termination signal from the manager, which causes the bab-loop to break
        return _NOT_TERMINATED;
    MAiNGO_END_IF
#else
    unsigned _workCount = 0;    // Dummy for convenience
#endif

    _TERMINATION_TYPE terminate = _NOT_TERMINATED;
    bool solved                 = (_nNodesLeft == 0 && _workCount == 0);
    bool maxNodesReached        = (_nNodesLeft >= _maingoSettings->BAB_maxNodes);
    bool maxTimeReached         = (_timePassed >= _maingoSettings->maxTime);
    bool maxwTimeReached         = (_wtimePassed >= _maingoSettings->maxwTime);
    bool maxIterationsReached   = (_iterations >= _maingoSettings->BAB_maxIterations);
    bool reachedTargetUbd       = (_ubd <= _maingoSettings->targetUpperBound);
    bool reachedTargetLbd       = (_lbd >= _maingoSettings->targetLowerBound);
    unsigned *limit;
    std::string criterion;
    std::string message;
    std::string userInput;


    if (solved) {    // Regular termination.
        if (_foundFeas) {
            // If we terminated regularly, we either have a global optimum, we reached min node size or the problem is infeasible
            if (babBase::larger_or_equal_within_rel_and_abs_tolerance(_lbd, _ubd, _maingoSettings->epsilonR, _maingoSettings->epsilonA)) {
                _status = babBase::enums::GLOBALLY_OPTIMAL;
            }
            else {
                _status = babBase::enums::GLOBAL_MIN_NODE_SIZE;
            }
        }
        else {
            _status = babBase::enums::INFEASIBLE;
        }
        terminate = _TERMINATED;

        if (_status == babBase::enums::GLOBALLY_OPTIMAL || _status == babBase::enums::INFEASIBLE) {
            // Print on screen and write to log
            _logger->print_message("  Done.\n", VERB_NORMAL, BAB_VERBOSITY);
            _print_termination("*                                             *** Regular termination. ***                                             *");
        }
        else {
            // Print on screen and write to log
            _logger->print_message("  Done.\n", VERB_NORMAL, BAB_VERBOSITY);
            _print_termination("*                                             *** Regular termination. ***                                             *\n*               *** Reached minimum node size. User-defined optimality tolerance could not be reached ***              *");
        }
    }
    else if (reachedTargetUbd) {    // Reached user-defined upper bound
        if (_workCount > 0) {
            return _TERMINATED_WORKERS_ACTIVE;
        }
        terminate = _TERMINATED;
        _status   = babBase::enums::TARGET_UBD;
        _logger->print_message("  Done.\n", VERB_NORMAL, BAB_VERBOSITY);
        _print_termination("*                                          *** Reached target upper bound. ***                                         *");
    }
    else if (reachedTargetLbd) {    // Reached user-defined lower bound
        if (_workCount > 0) {
            return _TERMINATED_WORKERS_ACTIVE;
        }
        terminate = _TERMINATED;
        _status   = babBase::enums::TARGET_LBD;
        _logger->print_message("  Done.\n", VERB_NORMAL, BAB_VERBOSITY);
        _print_termination("*                                          *** Reached target lower bound. ***                                         *");
    }
    else if (_maingoSettings->terminateOnFeasiblePoint && _foundFeas) {    // Found feasible point and this is enough for the user
        if (_workCount > 0) {
            return _TERMINATED_WORKERS_ACTIVE;
        }
        terminate = _TERMINATED;
        _status   = babBase::enums::FEASIBLE_POINT_ONLY;
        _logger->print_message("  Done.\n", VERB_NORMAL, BAB_VERBOSITY);
        _print_termination("*                                            *** Found feasible point. ***                                             *");
    }
    else if (maxNodesReached || maxTimeReached || maxwTimeReached || maxIterationsReached) {    // Reached some other termination criterion.

        if (_workCount > 0) {
            return _TERMINATED_WORKERS_ACTIVE;
        }
        babBase::enums::BAB_RETCODE potentialStatus;
        if (maxNodesReached) {
            message         = "*                                  *** Reached maximum number of nodes in memory! ***                                  *";
            criterion       = "number of nodes in memory";
            limit           = &_maingoSettings->BAB_maxNodes;
            potentialStatus = babBase::enums::MAX_NODES;
        }
        else if (maxTimeReached) {
            message         = "*                                            *** Reached CPU time limit! ***                                           *";
            criterion       = "CPU time";
            limit           = &_maingoSettings->maxTime;
            potentialStatus = babBase::enums::MAX_TIME;
        }
        else if (maxwTimeReached) {
            message         = "*                                           *** Reached Wall time limit! ***                                           *";
            criterion       = "Wall time";
            limit           = &_maingoSettings->maxwTime;
            potentialStatus = babBase::enums::MAX_TIME;
        }
        else {
            message         = "*                                   *** Reached maximum number of B&B iterations! ***                                  *";
            criterion       = "B&B iterations";
            limit           = &_maingoSettings->BAB_maxIterations;
            potentialStatus = babBase::enums::MAX_ITERATIONS;
        }


        if (!_maingoSettings->confirmTermination) {    // Just terminate.

            terminate = _TERMINATED;
            _print_termination(message);
            _status = potentialStatus;
        }
        else {    // Ask user whether to terminate

            _print_termination(message);

            // Summarize current status
            std::ostringstream outstr;
            outstr << std::endl
                   << "  " << std::setw(16) << std::left << " " << std::setw(10) << std::right << "Current" << std::setw(3) << " " << std::setw(10) << std::left << "Limit" << std::endl
                   << "  " << std::setw(16) << std::left << "Nodes in memory:" << std::setw(10) << std::right << _nNodesLeft << std::setw(3) << " " << std::setw(10) << std::left << _maingoSettings->BAB_maxNodes << std::endl
                   << "  " << std::setw(16) << std::left << "Iterations:" << std::setw(10) << std::right << _iterations << std::setw(3) << " " << std::setw(10) << std::left << _maingoSettings->BAB_maxIterations << std::endl
                   << "  " << std::setw(16) << std::left << "CPU time [s]:" << std::setw(10) << std::right << _timePassed << std::setw(3) << " " << std::setw(10) << std::left << _maingoSettings->maxTime << std::endl
                   << std::endl;
            outstr << "  " << std::setw(16) << std::left << "LBD:" << std::setw(10) << std::right << _lbd << std::endl
                   << "  " << std::setw(16) << std::left << "UBD:" << std::setw(10) << std::right << _ubd << std::endl
                   << "  " << std::setw(16) << std::left << "Absolute gap:" << std::setw(10) << std::right << _ubd - _lbd << std::setw(3) << " " << std::setw(10) << std::left << _maingoSettings->epsilonA << std::endl
                   << "  " << std::setw(16) << std::left << "Relative gap:" << std::setw(10) << std::right << ((_ubd == 0) ? (_lbd) : ((_ubd - _lbd) / std::fabs(_ubd))) << std::setw(3) << " " << std::setw(10) << std::left << _maingoSettings->epsilonR << std::endl
                   << std::endl
                   << "************************************************************************************************************************" << std::endl
                   << std::endl;

            // Query input
            outstr << "  Do you want to continue (y/n)? ";
            _logger->print_message(outstr.str(), VERB_NONE, BAB_VERBOSITY);
            while (getline((*_inputStream), userInput) && userInput != "y" && userInput != "n") {
                _logger->print_message("  Invalid input. Please type 'y' or 'n' and press enter: ", VERB_NONE, BAB_VERBOSITY);
            }

            // Interpret input
            if (userInput == "y") {
                outstr.str("");
                outstr.clear();
                outstr << "  User input: yes\n  Enter new limit for " << criterion << ": ";
                _logger->print_message(outstr.str(), VERB_NONE, BAB_VERBOSITY);
                while (getline((*_inputStream), userInput) && (*limit >= atof(userInput.c_str()))) {
                    outstr.str("");
                    outstr.clear();
                    outstr << "  Invalid input (has to be greater than  " << *limit << "), please revise: ";
                    _logger->print_message(outstr.str(), VERB_NONE, BAB_VERBOSITY);
                }
                if (userInput == "") {
                    throw MAiNGOException("  Error while checking termination: Querying user input while checking termination criteria.");
                }
                else if (atof(userInput.c_str()) > std::numeric_limits<int>::max()) {
                    _logger->print_message("  Value is too high for integer type, set to maximum.\n", VERB_NONE, BAB_VERBOSITY);
                    *limit = std::numeric_limits<int>::max();
                }
                else {
                    *limit = (int)atof(userInput.c_str());
                }
                outstr.str("");
                outstr.clear();
                outstr << "  User input: " << (*limit) << "\n  Okay, Resuming solution..." << std::endl
                       << std::endl;
                _logger->print_message(outstr.str(), VERB_NONE, BAB_VERBOSITY);
                _linesprinted = 0;    // To make sure header line is printed before continuing to print progress
                terminate     = _NOT_TERMINATED;
            }
            else if (userInput == "n") {
                _logger->print_message("  User input: no\n  ", VERB_NONE, BAB_VERBOSITY);
                terminate = _TERMINATED;
                _print_termination(message);
                _status = potentialStatus;
            }
            else {
                throw MAiNGOException("  Error while checking termination: invalid user input '" + userInput + "'");    // GCOVR_EXCL_LINE
            }
        }
    }
    return terminate;
}


#ifdef HAVE_GROWING_DATASETS
////////////////////////////////////////////////////////////////////////////////////////
// function for checking termination of post-processing of heuristic B&B algorithm with growing datasets
BranchAndBound::_TERMINATION_TYPE
BranchAndBound::_check_termination_postprocessing()
{

#ifdef HAVE_MAiNGO_MPI
    MAiNGO_IF_BAB_WORKER
        // Workers get their termination signal from the manager, which causes the post-processingp to break
        return _NOT_TERMINATED;
    MAiNGO_END_IF
#else
    unsigned _workCount = 0;    // Dummy for convenience
#endif

    if (_nNodesProcessedPost == _nNodesTrackedPost) {    // All tracked nodes processed - regular termination.
        // Print on screen and write to log
        _logger->print_message("  Done.\n", VERB_NORMAL, BAB_VERBOSITY);
        _print_termination("*                                             *** Regular termination. ***                                             *");

        return _TERMINATED;
    }
    else if (_timePostpro >= _maingoSettings->growing_maxTimePostprocessing) {
        if (_workCount > 0) {
            return _TERMINATED_WORKERS_ACTIVE;
        }

        _print_termination("*                                           *** Reached CPU time limit! ***                                            *");
        return _TERMINATED;
    }

    return _NOT_TERMINATED;
}
#endif    // HAVE_GROWING_DATASETS


////////////////////////////////////////////////////////////////////////////////////////
// function for printing stars in the termination
void
BranchAndBound::_print_termination(std::string message)
{

    std::ostringstream outstr;
    if ((_maingoSettings->BAB_verbosity > VERB_NONE) || (_maingoSettings->confirmTermination)) {
        outstr << std::endl
               << "************************************************************************************************************************" << std::endl
               << "*                                                                                                                      *" << std::endl
               << message << std::endl
               << "*                                                                                                                      *" << std::endl
               << "************************************************************************************************************************" << std::endl;
    }

    _logger->print_message(outstr.str(), VERB_NORMAL, BAB_VERBOSITY);
}

//////////////////////////////////////////////////////
// Utility functions for solving Two Stage problems //
//////////////////////////////////////////////////////
inline bool 
BranchAndBound::_update_psb_entry(std::map<int, std::pair<std::vector<std::vector<double>>, bool>>::iterator &it) {
    if (it->second.second) {
        // first lookup for child of node with this id, one lookup remaining
        it->second.second = false;
        return false;
    }
    else {
        // second lookup for child of node with this id, removing
        this->_parentSubproblemBounds.erase(it);
        return true;
    }
}

void 
BranchAndBound::_retreive_parent_subproblem_bounds(const babBase::BabNode &n, const bool sibling_iteration) {
    if (n.get_ID() == 1) return; // We don't store bounds for the root node
    auto it = this->_parentSubproblemBounds.find(n.get_parent_ID());
    if (it == this->_parentSubproblemBounds.end()) {
        throw MAiNGOException("  Error: Lookup of parent subproblem bounds"
                                " for child node with id " +
                                std::to_string(n.get_ID()) + " and parent id " +
                                std::to_string(n.get_parent_ID()) + " failed.");
    }
    else {
        /** NOTE: Entries in _parentSubproblemBounds may contain one or two sets of bounds.
         *        The latter case occurs if the parent of the current siblings was
         *        an orthant node, that was itself obtained by second stage branching.
         *        In that case, the two sets of bounds only differ in the scenarios
         *        corresponding to unbranched variables.
         *        For those scenarios, the first set of bounds is based on the original
         *        SPBs of the orthant node's parent (except for tightening by
         *        infeasibility), while the second set of bounds is based on tightened
         *        SPBs (using the minima over the two associated sibling SPBs).
         */
        *_subproblemBounds = it->second.first[0];

        if (sibling_iteration) {    // Can only be true for extension two-stage stochastic programming
            if (it->second.first.size() > 1) {
                _subproblemBounds->insert(_subproblemBounds->end(), it->second.first[1].begin(), it->second.first[1].end());
            }
            _parentSubproblemBounds.erase(it);
        }
        else {
            if (_update_psb_entry(it)) {
            }
        }
    }
}

void
BranchAndBound::observe_fathoming(const babBase::BabNode &n) {
    auto it = _parentSubproblemBounds.find(n.get_parent_ID());
    if (it != _parentSubproblemBounds.end()) {
        if (_update_psb_entry(it)) {
            // possible debug output
        }
    }
    else {
        throw MAiNGOException("  Error: When fathoming child node with id "
                              + std::to_string(n.get_ID())
                              + " no subproblem bounds entry could be found"
                              " for the parent node with id "
                              + std::to_string(n.get_parent_ID()));
    }
}