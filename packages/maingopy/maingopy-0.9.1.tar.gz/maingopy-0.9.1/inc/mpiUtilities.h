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

#ifdef HAVE_MAiNGO_MPI
#include "babNode.h"
#include "mpi.h"

#define MAiNGO_IF_BAB_MANAGER if (_rank == 0) {
#define MAiNGO_IF_BAB_WORKER if (_rank != 0) {
#define MAiNGO_ELSE \
    }               \
    else            \
    {
#define MAiNGO_END_IF }

#define MAiNGO_MPI_BARRIER MPI_Barrier(MPI_COMM_WORLD);
#define MAiNGO_MPI_FINALIZE MPI_Finalize();
#else
#define MAiNGO_IF_BAB_MANAGER
#define MAiNGO_IF_BAB_WORKER
#define MAiNGO_ELSE
#define MAiNGO_END_IF

#define MAiNGO_MPI_BARRIER
#define MAiNGO_MPI_FINALIZE

#endif

#ifdef HAVE_MAiNGO_MPI

namespace maingo {


/**
* @enum BCAST_TAG
* @brief Enum for representing broadcasting tags
*/
enum BCAST_TAG {
    BCAST_NOTHING_PENDING = 0,    /*!< No pending broadcast (initial/empty state for _bcastTag) */
    BCAST_EXCEPTION,              /*!< An exception occured */
    BCAST_EVERYTHING_FINE,        /*!< Everything is fine */
    BCAST_TIGHTENING_INFEASIBLE,  /*!< OBBT is infeasible */
    BCAST_CONSTR_PROP_INFEASIBLE, /*!< Constraint Propagation was infeasible, but multistart was feasible*/
    BCAST_INFEASIBLE,             /*!< Problem is infeasible */
    BCAST_FEASIBLE,               /*!< Problem might be feasible */
    BCAST_TERMINATE,              /*!< Terminate BaB loop */
    BCAST_FOUND_FEAS,             /*!< A feasible point was found */
    BCAST_SCALING_NEEDED          /*!< More scaling is needed */
};

/**
* @enum COMMUNICATION_TAG
* @brief Enum for representing communication tags
*/
enum COMMUNICATION_TAG {
    TAG_EXCEPTION = 0,                /*!< An exception occured */
    TAG_FOUND_INCUMBENT,              /*!< Worker found an incumbent */
    TAG_NEW_INCUMBENT,                /*!< Value of found incumbent */
    TAG_NEW_INCUMBENT_ID,             /*!< Node ID of found incumbent */
    TAG_NODE_REQUEST,                 /*!< Worker requests a new node */
    TAG_NEW_NODE_NO_INCUMBENT,        /*!< Manager will send new node, but no new incumbent */
    TAG_NEW_NODE_NEW_INCUMBENT,       /*!< Manager will send new node and a new incumbent */
    TAG_NEW_NODE_NO_DATASET,          /*!< Manager will send new node, but no new dataset */
    TAG_NEW_NODE_NEW_DATASET,         /*!< Manager will send new node and a new dataset */
    TAG_NEW_SIBLINGS_NO_INCUMBENT,    /*!< Manager will send new siblings, but no new incumbent */
    TAG_NEW_SIBLINGS_NEW_INCUMBENT,   /*!< Manager will send new siblings and a new incumbent */
    TAG_NEW_NODE_UBD,                 /*!< New global UBD value*/
    TAG_NEW_SUBPROBLEM_BOUNDS,        /*!< New subproblem bounds */
    TAG_SOLVED_NODE_STATUS_NORMAL,    /*!< The solved node is normal */
    TAG_SOLVED_SIBLING_STATUS_NORMAL, /*!< The siblings were solved normally */
    TAG_SOLVED_NODE_STATUS_CONVERGED, /*!< The solved node converged */
    TAG_SOLVED_SIBLING_STATUS_CONVERGED, /*!< The solved siblings converged */
    TAG_SOLVED_NODE_STATUS_INFEAS, /*!< The solved node is infeasible */
    TAG_SOLVED_SIBLING_STATUS_INFEAS, /*!< The solved siblings are infeasible */
    TAG_SOLVED_NODE_LBD,               /*!< LBD of solved node */
    TAG_SOLVED_SUBPROBLEM_LBD,         /*!< LBD of subproblem */
    TAG_SERIALIZED_SIBLING_RESULTS,    /*!< Serialized results of siblings */
    TAG_FATHOMED_SUBPROBLEMS,          /*!< Fathomed subproblems */
    TAG_SOLVED_NODE_SOLUTION_POINT,    /*!< Solution point of solved node */
    TAG_SOLVED_NODE_STATISTICS,        /*!< Statistic from solving node (lbd and ubd counts) */
    TAG_NODE_ID,                       /*!< ID of the node being sent */
    TAG_PARENT_ID,                     /*!< ID of the parent of the node being sent */
    TAG_NODE_PRUNING_SCORE,            /*!< Pruning score of the node being sent */
    TAG_NODE_LOWER_BOUNDS,             /*!< Variable lower bounds of the node being sent */
    TAG_NODE_UPPER_BOUNDS,             /*!< Variable upper bounds of the node being sent */
    TAG_NODE_HAS_INCUMBENT,            /*!< Whether the node being sent holds the incumbent */
    TAG_NODE_DEPTH,                    /*!< Depth of the node being sent */
    TAG_NODE_IDXDATA,                  /*!< Index of dataset used in node being sent */
    TAG_NODE_AUGMENT_DATA,             /*!< Whether dataset has been augmented to get the dataset of the node being sent */
    TAG_NODE_DATAPOINT,                /*!< Data point of a new dataset being sent */
    TAG_WORKER_FINISHED,               /*!< Worker finished BAB-loop */
    TAG_MS_STOP_SOLVING,               /*!< Multistart: worker should stop searching for local solutions */
    TAG_MS_NEW_POINT,                  /*!< Multistart: new initial point for local search */
    TAG_MS_SOLUTION,                   /*!< Multistart: local solution */
    TAG_MS_FEAS,                       /*!< Multistart: found feasible solution */
    TAG_MS_INFEAS,                     /*!< Multistart: initial point was infeasible */
};

/**
* @brief Communication function for sending a bab node
*
* @param[in] node is the node to be send
* @param[in] dest is the number of the process to recieve the node
*/
inline void
send_babnode(const babBase::BabNode &node, const int dest)
{

    int id                 = node.get_ID();
    int parent_id          = node.get_parent_ID();
    std::vector<double> lb = node.get_lower_bounds();
    std::vector<double> ub = node.get_upper_bounds();
    double pruningScore    = node.get_pruning_score();
    int depth              = node.get_depth();
    int idData             = node.get_index_dataset();
    int aD                 = node.get_augment_data() ? 1 : 0;
    // Send all information
    MPI_Ssend(&id, 1, MPI_INT, dest, TAG_NODE_ID, MPI_COMM_WORLD);
    MPI_Ssend(&parent_id, 1, MPI_INT, dest, TAG_PARENT_ID, MPI_COMM_WORLD);
    MPI_Ssend(&pruningScore, 1, MPI_DOUBLE, dest, TAG_NODE_PRUNING_SCORE, MPI_COMM_WORLD);
    MPI_Ssend(lb.data(), lb.size(), MPI_DOUBLE, dest, TAG_NODE_LOWER_BOUNDS, MPI_COMM_WORLD);
    MPI_Ssend(ub.data(), lb.size(), MPI_DOUBLE, dest, TAG_NODE_UPPER_BOUNDS, MPI_COMM_WORLD);
    MPI_Ssend(&depth, 1, MPI_INT, dest, TAG_NODE_DEPTH, MPI_COMM_WORLD);
    MPI_Ssend(&idData, 1, MPI_INT, dest, TAG_NODE_IDXDATA, MPI_COMM_WORLD);
    MPI_Ssend(&aD, 1, MPI_INT, dest, TAG_NODE_AUGMENT_DATA, MPI_COMM_WORLD);
}

/**
* @brief Communication function for recieving a bab node
*
* @param[in] node is the node to be send
* @param[in] source is the number of process from which the node came
* @param[in] nvar is the number variables
*/
inline void
recv_babnode(babBase::BabNode &node, const int source, const unsigned nvar)
{

    int id, parent_id;
    std::vector<double> lb(nvar, 0);
    std::vector<double> ub(nvar, 0);
    double pruningScore;
    int depth;
    int idData;
    int aD;

    MPI_Recv(&id, 1, MPI_INT, source, TAG_NODE_ID, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    MPI_Recv(&parent_id, 1, MPI_INT, source, TAG_PARENT_ID, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    MPI_Recv(&pruningScore, 1, MPI_DOUBLE, source, TAG_NODE_PRUNING_SCORE, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    MPI_Recv(lb.data(), nvar, MPI_DOUBLE, source, TAG_NODE_LOWER_BOUNDS, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    MPI_Recv(ub.data(), nvar, MPI_DOUBLE, source, TAG_NODE_UPPER_BOUNDS, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    MPI_Recv(&depth, 1, MPI_INT, source, TAG_NODE_DEPTH, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    MPI_Recv(&idData, 1, MPI_INT, source, TAG_NODE_IDXDATA, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    MPI_Recv(&aD, 1, MPI_INT, source, TAG_NODE_AUGMENT_DATA, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

    node = babBase::BabNode(pruningScore, lb, ub, idData, parent_id, id, depth, aD == 1);
}

/**
* @brief Communication function for receiving a double vector
*
* @param[in] vec is the double vector to be received
* @param[in] source is the number of the process from which the vector was sent
* @param[in] tag is the MPI tag attached to the "send double vector" communication
* @param[in] comm is the MPI communication namespace
* @param[in] status is the MPI status connected to this communication
*/
inline void
recv_vector_double(std::vector<double> &vec, int source, int tag, MPI_Comm comm, MPI_Status *status)
{

    MPI_Status probeStatus;
    int messageSize;

    MPI_Probe(source, tag, MPI_COMM_WORLD, &probeStatus);
    MPI_Get_count(&probeStatus, MPI_DOUBLE, &messageSize);
    vec.resize(messageSize);

    MPI_Recv(vec.data(), messageSize, MPI_DOUBLE, source, tag, comm, status);
}

/**
* @brief Communication function for receiving an integer vector
*
* @param[in] vec is the integer vector to be sent
* @param[in] source is the number of process from which the node came
* @param[in] tag is the MPI tag attached to the "send integer vector" communication
* @param[in] comm is the MPI communication namespace
* @param[in] status is the MPI status connected to this communication
*/
inline void
recv_vector_int(std::vector<int> &vec, int source, int tag, MPI_Comm comm, MPI_Status *status)
{

    MPI_Status probeStatus;
    int messageSize;

    MPI_Probe(source, tag, MPI_COMM_WORLD, &probeStatus);
    MPI_Get_count(&probeStatus, MPI_INT, &messageSize);
    vec.resize(messageSize);

    MPI_Recv(vec.data(), messageSize, MPI_INT, source, tag, comm, status);
}

/**
    * @struct WorkerNodeComparator
    * @brief Functor for comparing node lower bounds of nodes that were given to workers.
    *
    * If the boolean of the pair is true, then the node has been given to a worker and shall be
    * taken into account when setting the output lower bound.
    */
struct WorkerNodeComparator {
    /**
        * @brief () operator for comparing
        *
        * @param[in] a is the left object
        * @param[in] b is the right object
        * @return true if a is lesser than b
        */
    bool operator()(const std::pair<bool, double> &a, const std::pair<bool, double> &b) const
    {
        if (a.first) {
            if (b.first) {
                return a.second < b.second;
            }
            else {
                return true;
            }
        }
        else {
            return false;
        }
    };
};


}    // end namespace maingo

#endif
