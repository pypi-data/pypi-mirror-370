#include "ffunc.hpp"
#include <memory>

namespace maingo {
	namespace lbp {
		struct DagObj;
	}
}

namespace SIA{
    typedef mc::FFGraph MCdag;
    typedef mc::FFVar* MCvar;
    typedef mc::FFOp::TYPE MCoperation;
    using maingo::lbp::DagObj;

    bool inline mcVar_is_independentDagVar(MCvar mcVar)
    {
        if (mcVar->id().first == mc::FFVar::TYPE::VAR) return true;
        else return false;
    }
    bool inline mcVar_is_dependentDagVar(MCvar mcVar)
    {
        if (mcVar->id().first == mc::FFVar::TYPE::AUX) return true;
        else return false;
    }
    bool inline mcVar_is_constantDagVar(MCvar mcVar)
    {
        if (mcVar->id().first == mc::FFVar::TYPE::CREAL || mcVar->id().first == mc::FFVar::TYPE::CINT) return true;
        else return false;
    }

    struct DagConversionInformation {
        MCdag* ptr_mcDag = nullptr;
        std::shared_ptr<DagObj> dagObj;

        int numDagVars;
        std::vector<MCvar> mcVars;

        std::vector<MCvar> independentVars;
        std::vector<MCvar> dependentVars;
        std::vector<MCvar> constantVars;

        std::vector<int> functionIdObj;
        std::vector<int> functionIdIneq;
        std::vector<int> functionIdEq;

        int numFunctionIdObj = 0;
        int numFunctionIdIneq = 0;
        int numFunctionIdEq = 0;

        DagConversionInformation() {}

        DagConversionInformation(MCdag& mcDag, std::shared_ptr<DagObj> dagObj)
        {
            ptr_mcDag = &mcDag;
            this->dagObj = dagObj;

            init_numDagVars();
            init_mcVars();
            init_var_vectors();
        }

        int get_num_vars();

    private:
        // Get # of dag variables
        void init_numDagVars()
        {
            numDagVars = ptr_mcDag->Vars().size();
        }
        void init_mcVars()
        {
            std::set<MCvar, mc::lt_FFVar> mcDagVars = ptr_mcDag->Vars();
            std::set<MCvar, mc::lt_FFVar>::iterator it;

            for (it = mcDagVars.begin(); it != mcDagVars.end(); it++)
                mcVars.push_back(*it);
        }
        void init_var_vectors(){
            for (int index = 0; index < numDagVars; index++) 
            {
                MCvar currentMcVar = mcVars[index];
                if (mcVar_is_independentDagVar(currentMcVar))
                    independentVars.push_back(currentMcVar);
                if (mcVar_is_dependentDagVar(currentMcVar))
                    dependentVars.push_back(currentMcVar);
                if (mcVar_is_constantDagVar(currentMcVar))
                    constantVars.push_back(currentMcVar);
            }        
        }
    };

    int get_index_of_MCvar_in_MCvarVector(MCvar mcVar, std::vector<MCvar>& mcVars);
    double get_value_of_MCvar(MCvar mcVar);
    int get_number_of_operands_of_MCvar(MCvar mcVar);
    std::vector<MCvar> get_mcVarOperands_of_MCvar(MCvar mcVar);
    MCoperation get_operation_of_MCvar(MCvar mcVar);

    void init_var_vectors(DagConversionInformation& dagConversionInformation);
    void init_function_ids_for_dag(DagConversionInformation& dagConversionInformation);
    void init_function_ids_for_dag(std::vector<MCvar> &mcVars, std::vector<std::vector<mc::FFVar>> &mcDagFunctions, std::vector<int> &dagFunctionIds);
}