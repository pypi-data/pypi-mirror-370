#ifndef DAGEVALUATION_H
#define DAGEVALUATION_H

#pragma once

#include "dag.h"
#include "derivativeinformation.h"

namespace SVT_DAG {

    // template <typename dataType>
    // std::vector<dataType>
    // evaluate(Dag& dag, const std::vector<dataType>& valuesOfIndependentVariables);

    // template <typename dataType>
    // dataType*
    // evaluate(Dag& dag, dataType* valuesOfIndependentVariables);


    template <typename dataType>
    std::vector<dataType>
    evaluate(Dag& dag, const std::vector<dataType>& valuesOfIndependentVariables)
    {
        if (valuesOfIndependentVariables.size() != dag.independentVars.size())
        {
            throw std::runtime_error("Error in evaluation of Dag: Number of given values does not match number of independent variables.");
        }

        std::vector<dataType> dagVarValues(dag.independentVars.size() + dag.dependentVars.size() + dag.constantVars.size());

        for (std::size_t i = 0; i < dag.independentVars.size(); ++i)
        {
            dagVarValues[dag.independentVars[i].dagVarId] = valuesOfIndependentVariables[i];
        }
        
        for (std::size_t i = 0; i < dag.constantVars.size(); ++i)
        {       
            dagVarValues[dag.constantVars[i].dagVarId] = dag.constantVars[i].value;
        }    

        for (std::size_t i = 0; i < dag.dependentVars.size(); ++i)
        {
            dagVarValues[dag.dependentVars[i].dagVarId] = dag.dependentVars[i].operation->evaluate(dagVarValues, dag.dependentVars[i].operandIds);
        }    

        return dagVarValues;
    }

    template <typename dataType>
    dataType*
    evaluate(Dag& dag, const dataType* valuesOfIndependentVariables)
    {
        if (!dag.synchronized_var_vectors_and_var_arrays)
        {
            dag.synchronize_var_vectors_and_var_arrays();
            //throw std::runtime_error("Error in evaluation of Dag: Number of given values does not match number of independent variables.");
        }

        dataType* dagVarValues = new dataType[dag.numVars];

        for (std::size_t i = 0; i < dag.numIndependentVars; ++i)
        {
            dagVarValues[dag.arrIndependentVars[i].dagVarId] = valuesOfIndependentVariables[i];
        }

        for (std::size_t i = 0; i < dag.numConstantVars; ++i)
        {
            dagVarValues[dag.arrConstantVars[i].dagVarId] = dag.arrConstantVars[i].value;
        }

        for (std::size_t i = 0; i < dag.numDependentVars; ++i)
        {
            dagVarValues[dag.arrDependentVars[i].dagVarId] = dag.arrDependentVars[i].operation->evaluate(dagVarValues, dag.arrDependentVars[i].operandIds);
        }

        return dagVarValues;
    }

    template <typename dataType>
    void
    evaluate(Dag& dag, const dataType* valuesOfIndependentVariables, dataType* dagVarValues)
    {
        if (!dag.synchronized_var_vectors_and_var_arrays)
        {
            dag.synchronize_var_vectors_and_var_arrays();
            //throw std::runtime_error("Error in evaluation of Dag: Number of given values does not match number of independent variables.");
        }

        for (std::size_t i = 0; i < dag.numIndependentVars; ++i)
        {
            dagVarValues[dag.arrIndependentVars[i].dagVarId] = valuesOfIndependentVariables[i];
        }

        for (std::size_t i = 0; i < dag.numConstantVars; ++i)
        {
            dagVarValues[dag.arrConstantVars[i].dagVarId] = dag.arrConstantVars[i].value;
        }

        for (std::size_t i = 0; i < dag.numDependentVars; ++i)
        {
            dagVarValues[dag.arrDependentVars[i].dagVarId] = dag.arrDependentVars[i].operation->evaluate(dagVarValues, dag.arrDependentVars[i].operandIds);
        }
    }

    template <typename dataType>
    void
    evaluate_derivative(Dag& dag, dataType* valuesOfIndependentVariables, DerivativeInformation* dagVarValues)
    {		
        for (int i = 0; i < dag.numIndependentVars; ++i)
        {
            dagVarValues[dag.independentVars[i].dagVarId].functionValue_I_cpu[0] = valuesOfIndependentVariables[i];
        }		
        for (int i = 0; i < dag.numConstantVars; i++)
        {
            dagVarValues[dag.constantVars[i].dagVarId].functionValue_I_cpu[0] = dag.constantVars[i].value;
        }
        for (int i = 0; i < dag.numDependentVars; ++i)
        {
            dag.dependentVars[i].operation->evaluate_derivative(dagVarValues, dag.dependentVars[i].operandIds, dagVarValues[dag.dependentVars[i].dagVarId]);
        }
    }

} // namespace SVT_DAG
#endif // DAGEVALUATION_H