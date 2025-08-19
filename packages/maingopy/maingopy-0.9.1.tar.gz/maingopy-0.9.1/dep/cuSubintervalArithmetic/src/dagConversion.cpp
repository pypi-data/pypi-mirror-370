#include "dagConversion.h"
#include "../../../inc/lbpDagObj.h"
#include <vector>

namespace SIA{

    int DagConversionInformation::get_num_vars(){
        return independentVars.size() + dependentVars.size() + constantVars.size();
    }

    void init_var_vectors(DagConversionInformation& dagConversionInformation){
        for (int index = 0; index < dagConversionInformation.numDagVars; index++) {
            MCvar currentMcVar = dagConversionInformation.mcVars[index];
            if (mcVar_is_independentDagVar(currentMcVar))
                dagConversionInformation.independentVars.push_back(currentMcVar);
            if (mcVar_is_dependentDagVar(currentMcVar))
                dagConversionInformation.dependentVars.push_back(currentMcVar);
            if (mcVar_is_constantDagVar(currentMcVar))
                dagConversionInformation.constantVars.push_back(currentMcVar);
        }        
    }

    int get_index_of_MCvar_in_MCvarVector(MCvar mcVar, std::vector<MCvar>& mcVars)
    {
        for (int index = 0; index < mcVars.size(); index++)			
            if (mcVar->id() == mcVars[index]->id() && mcVar->dag() == mcVars[index]->dag())
                return index;
        throw std::runtime_error("Error: did not find index of MCvar in MCvarVector during dag conversion!\n");
    }

    double get_value_of_MCvar(MCvar mcVar)
    {
        if (mcVar->num().t == mc::FFNum::TYPE::INT)
            return mcVar->num().n;
        else
            return mcVar->num().x;
    }

    int get_number_of_operands_of_MCvar(MCvar mcVar)
    {
        return mcVar->ops().first->pops.size();
    }

    std::vector<MCvar> get_mcVarOperands_of_MCvar(MCvar mcVar)
    {
        int numOperands = get_number_of_operands_of_MCvar(mcVar);
        std::vector<MCvar> mcVarOperands;

        for (int i = 0; i < numOperands; i++)
            mcVarOperands.push_back(mcVar->ops().first->pops[i]);

        return mcVarOperands;
    }

    MCoperation get_operation_of_MCvar(MCvar mcVar)
    {
        return mcVar->ops().first->type;
    }

    void init_function_ids_for_dag(DagConversionInformation& dagConversionInformation)
    {
        std::shared_ptr<DagObj> dagObj = dagConversionInformation.dagObj; 

        init_function_ids_for_dag(dagConversionInformation.mcVars, dagObj->functionsObj, dagConversionInformation.functionIdObj);
        init_function_ids_for_dag(dagConversionInformation.mcVars, dagObj->functionsIneq, dagConversionInformation.functionIdIneq);
        init_function_ids_for_dag(dagConversionInformation.mcVars, dagObj->functionsEq, dagConversionInformation.functionIdEq);

        dagConversionInformation.numFunctionIdObj = dagConversionInformation.functionIdObj.size();
        dagConversionInformation.numFunctionIdIneq = dagConversionInformation.functionIdIneq.size();
        dagConversionInformation.numFunctionIdEq = dagConversionInformation.functionIdEq.size();
    }

    void init_function_ids_for_dag(std::vector<MCvar> &mcVars, std::vector<std::vector<mc::FFVar>> &mcDagFunctions, std::vector<int> &dagFunctionIds)
    {
        // Clear old ids
        dagFunctionIds.clear();

        // Init new ids
        for (auto& function : mcDagFunctions)
        {
            int id = get_index_of_MCvar_in_MCvarVector(&function[0], mcVars);
            dagFunctionIds.push_back(id);
        }
    }
}
