#include "dag.h"
#include "baseoperation.h"

namespace SVT_DAG {

    void Dag::clear()
    {
        if (synchronized_var_vectors_and_var_arrays)
        {
            free(arrIndependentVars);
            free(arrDependentVars);
            free(arrConstantVars);
        }

#ifdef CUDA_INSTALLED
        if (copied_to_gpu)
        {
            // Deallocate the memory allocated for variables.
            cudaFree(d_independentVars);
            cudaFree(d_dependentVars);
            cudaFree(d_constantVars);

            // Deallocate the memory allocated for functions.
            cudaFree(d_dagVarIdObj);
            cudaFree(d_dagVarIdIneq);
            cudaFree(d_dagVarIdEq);

        }
#endif // CUDA_INSTALLED
    }

    // Deallocate resources for derivatives, only called when CF is used.
    void Dag::clear_derivatives()
    {
        //printf("Derivative clear function is called!\n");
        free(functionAndDerivativeValues);
        free(isDependentOfIndependentVariable);
        
#ifdef CUDA_INSTALLED
        free(h_functionAndDerivativeValues);

        cudaFree(d_functionAndDerivativeValues);
        cudaFree(d_isDependentOfIndependentVariable);
#endif // CUDA_INSTALLED
    }

    void
        Dag::add_independent_variable(ModelVar& newVar)
    {
        synchronized_var_vectors_and_var_arrays = false;

        const std::size_t dagVarId = get_valid_dagvar_id();
        independentVars.push_back(IndependentDagVar(dagVarId));

        newVar.dag = this;
        newVar.dagVarId = dagVarId;

        numIndependentVars++;
        numVars++;
    }

    ModelVar
        Dag::insert_dependent_with_operation_and_operands(BaseOperation* const operation, const ModelVar* const operands, const int numOperands)
    {
        synchronized_var_vectors_and_var_arrays = false;

        auto get_dag_var_id_numbers_from_model_vars = [](const ModelVar* const modelVars, const int numModelVars)
        {
            int* dagVarIds = (int*)malloc(numModelVars * sizeof(int));
            for (std::size_t i = 0; i < numModelVars; ++i)
            {
                dagVarIds[i] = modelVars[i].dagVarId;
            }
            return dagVarIds;
        };


        const std::size_t dagVarId = get_valid_dagvar_id();
        dependentVars.push_back(DependentDagVar(dagVarId, operation, get_dag_var_id_numbers_from_model_vars(operands, numOperands), numOperands));

        ModelVar resultVar;
        resultVar.dag = this;
        resultVar.dagVarId = dagVarId;

        numDependentVars++;
        numVars++;

        return resultVar;
    }

    void
        Dag::associate_variable_with_dag(ModelVar& newVar)
    {
        synchronized_var_vectors_and_var_arrays = false;

        const std::size_t dagVarId = get_valid_dagvar_id();

        newVar.dag = this;
        newVar.dagVarId = dagVarId;
    }

    void
        Dag::synchronize_var_vectors_and_var_arrays()
    {
        if (!synchronized_var_vectors_and_var_arrays) {
            numIndependentVars = independentVars.size();
            numDependentVars = dependentVars.size();
            numConstantVars = constantVars.size();
            numVars = numIndependentVars + numDependentVars + numConstantVars;

            arrIndependentVars = (IndependentDagVar*)malloc(numIndependentVars * sizeof(IndependentDagVar));
            arrDependentVars = (DependentDagVar*)malloc(numDependentVars * sizeof(DependentDagVar));
            arrConstantVars = (ConstantDagVar*)malloc(numConstantVars * sizeof(ConstantDagVar));

            for (int i = 0; i < numIndependentVars; i++)
                arrIndependentVars[i] = independentVars[i];

            for (int i = 0; i < numDependentVars; i++)
                arrDependentVars[i] = dependentVars[i];

            for (int i = 0; i < numConstantVars; i++)
                arrConstantVars[i] = constantVars[i];

            synchronized_var_vectors_and_var_arrays = true;
        }
    }

    // Add the current dependent variable to dag objective function id list
    void 
        Dag::set_num_obj_functions()
    {
        int dagVarId = Dag::get_num_vars() - 1;
        dagVarIdObj.push_back(dagVarId);
        numDagVarIdObj += 1;
    }

    // Add the current dependent variable to dag inequality constraint id list
    void 
        Dag::set_num_ineq_constraints()
    {
        int dagVarId = Dag::get_num_vars() - 1;
        dagVarIdIneq.push_back(dagVarId);
        numDagVarIdIneq += 1;
    }

    // Add the current dependent variable to dag equality constraint id list
    void 
        Dag::set_num_eq_constraints()
    {
        int dagVarId = Dag::get_num_vars() - 1;
        dagVarIdEq.push_back(dagVarId);
        numDagVarIdEq += 1;
    }

#ifdef CUDA_INSTALLED
    void
        Dag::copy_to_gpu()
    {
        // Synchronize dag arrays if they are not up to date
        if (!synchronized_var_vectors_and_var_arrays)
            synchronize_var_vectors_and_var_arrays();

        size_t bytesIndependentVars = numIndependentVars * sizeof(IndependentDagVar);
        size_t bytesDependentVars = numDependentVars * sizeof(DependentDagVar);
        size_t bytesConstantVars = numConstantVars * sizeof(ConstantDagVar);

        // Construtct temporary dependent variable array with pointers to GPU
        DependentDagVar* h_dependentVars;
        h_dependentVars = (DependentDagVar*)malloc(numDependentVars * sizeof(DependentDagVar));
        for (int i = 0; i < numDependentVars; i++)
        {
            BaseOperation* operation = copy_ptr_to_gpu(arrDependentVars[i].operation, 1);
            const int* operandIds = copy_ptr_to_gpu(arrDependentVars[i].operandIds, arrDependentVars[i].numOperands);
            h_dependentVars[i] = DependentDagVar(arrDependentVars[i].dagVarId, operation, operandIds, arrDependentVars[i].numOperands);
        }

        // Allocate memory on GPU for dag variables
        cudaMalloc(&d_independentVars, bytesIndependentVars);
        cudaMalloc(&d_dependentVars, bytesDependentVars);
        cudaMalloc(&d_constantVars, bytesConstantVars);

        // Copy dag variables to GPU
        cudaMemcpy(d_independentVars, arrIndependentVars, bytesIndependentVars, cudaMemcpyHostToDevice);
        cudaMemcpy(d_dependentVars, h_dependentVars, bytesDependentVars, cudaMemcpyHostToDevice);
        cudaMemcpy(d_constantVars, arrConstantVars, bytesConstantVars, cudaMemcpyHostToDevice);

        copied_to_gpu = true;

        free(h_dependentVars);
    }

    DependentDagVar* get_copy_of_DependentDagVar_ptr(DependentDagVar* ptr_original)
    {
        // To be writen
        throw ("Error in dag.cpp in get_copy_of_DependenDagVar_ptr. Function not implemented!\n");
        return ptr_original;
    }

#endif // CUDA_INSTALLED

} // namespace SVT_DAG