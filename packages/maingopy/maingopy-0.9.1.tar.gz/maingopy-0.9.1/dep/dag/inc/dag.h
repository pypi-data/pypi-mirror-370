#ifndef DAG_H
#define DAG_H

#pragma once

#include "dagvar.h"
#include "modelvar.h"

#include <vector>

namespace SVT_DAG {

    class BaseOperation;

    struct Dag
    {
        void add_independent_variable(ModelVar& variable);
        template <typename dataType> void add_constant_variable(ModelVar& variable, const dataType& value);
        ModelVar insert_dependent_with_operation_and_operands(BaseOperation* const operation, const ModelVar* const operands, const int numOperands);
        void associate_variable_with_dag(ModelVar& variable);

        void clear();

        void clear_derivatives();

        std::vector< IndependentDagVar > independentVars{};
        std::vector< DependentDagVar > dependentVars{};
        std::vector< ConstantDagVar > constantVars{};

        std::vector<int> dagVarIdObj;
        std::vector<int> dagVarIdIneq{};
        std::vector<int> dagVarIdEq{};
        std::vector<int> dagVarIdIneqRelaxationOnly{};
        std::vector<int> dagVarIdEqRelaxationOnly{};
        std::vector<int> dagVarIdIneqSquash{};

#ifdef CUDA_INSTALLED
        int* d_dagVarIdObj;
        int* d_dagVarIdIneq;
        int* d_dagVarIdEq;
#endif // CUDA_INSTALLED

        int numDagVarIdObj = 0;
        int numDagVarIdIneq = 0;
        int numDagVarIdEq = 0;

        std::size_t get_valid_dagvar_id() const { return independentVars.size() + dependentVars.size() + constantVars.size(); }
        int get_num_vars() { return get_valid_dagvar_id(); }

        // Code for evaluation without vectors
        IndependentDagVar* arrIndependentVars{};
        DependentDagVar* arrDependentVars{};
        ConstantDagVar* arrConstantVars{};

        I_cpu* functionAndDerivativeValues = nullptr;
        bool * isDependentOfIndependentVariable = nullptr;

#ifdef CUDA_INSTALLED
        I_gpu* h_functionAndDerivativeValues = nullptr;
        I_gpu* d_functionAndDerivativeValues = nullptr;
        bool* d_isDependentOfIndependentVariable = nullptr;
#endif // CUDA_INSTALLED

        int numIndependentVars = 0;
        int numDependentVars = 0;
        int numConstantVars = 0;
        int numVars = 0;

        bool synchronized_var_vectors_and_var_arrays = false;

        void synchronize_var_vectors_and_var_arrays();

        // These functions should be called right after a desired dependent variable is added.
        void set_num_obj_functions();
        void set_num_ineq_constraints();
        void set_num_eq_constraints();

#ifdef CUDA_INSTALLED
        // Code for evaluation on GPU
        IndependentDagVar* d_independentVars;
        DependentDagVar* d_dependentVars;
        ConstantDagVar* d_constantVars;

        bool copied_to_gpu = false;

        void copy_to_gpu();
#endif // CUDA_INSTALLED
    };


    template<typename dataType>
    void
        Dag::add_constant_variable(ModelVar& newVar, const dataType& newValue)
    {
        synchronized_var_vectors_and_var_arrays = false;

        const std::size_t dagVarId = get_valid_dagvar_id();
        constantVars.push_back(ConstantDagVar(dagVarId, newValue));

        newVar.dag = this;
        newVar.dagVarId = dagVarId;

        numConstantVars++;
        numVars++;
    }

    DependentDagVar* get_copy_of_DependentDagVar_ptr(DependentDagVar* ptr_original);

} // namespace SVT_DAG


#endif //DAG_H