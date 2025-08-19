
#include "dagconversion.h"
#include "dagconversionintrinsicfunctions.h"
#include "lbpDagObj.h"
#include <vector>


namespace SVT_DAG {

	using namespace DagConversionHelpFunctions;

	void construct_dag_from_MCdag(Dag &dag, MCdag& mcDag, std::shared_ptr<DagObj> dagObj)
	{
		DagConversionInformation dagConversionInformation(mcDag, dag, dagObj);

		init_dagVars(dagConversionInformation);

		init_function_ids(dagConversionInformation);

		//if (dag.numVars != mcDag.Vars().size()) throw std::runtime_error("Error: Unequal number of dag variables after dag conversion!\n");
	}

	namespace DagConversionHelpFunctions {

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

		void init_dagVars(DagConversionInformation& dagConversionInformation)
		{
			for (int index = 0; index < dagConversionInformation.numDagVars; index++) {
				MCvar currentMcVar = dagConversionInformation.mcVars[index];
				if (!dagConversionInformation.is_dagVar_initialized[index])
					insert_mcVar_into_dag(currentMcVar, index, dagConversionInformation);
			}
		}
		void insert_mcVar_into_dag(MCvar mcVar, int mcVarIndex, DagConversionInformation& dagConversionInformation)
		{
			if (dagConversionInformation.is_dagVar_initialized[mcVarIndex]) return;

			if (mcVar_is_independentDagVar(mcVar))
				insert_independent_mcVar_into_dag(mcVar, mcVarIndex, dagConversionInformation);

			if (mcVar_is_dependentDagVar(mcVar))
				insert_dependent_mcVar_into_dag(mcVar, mcVarIndex, dagConversionInformation);

			if (mcVar_is_constantDagVar(mcVar))
				insert_constant_mcVar_into_dag(mcVar, mcVarIndex, dagConversionInformation);
		}
		void insert_independent_mcVar_into_dag(MCvar mcVar, int mcVarIndex, DagConversionInformation& dagConversionInformation)
		{
			ModelVar* dagVar = &dagConversionInformation.dagVars[mcVarIndex];
			dagConversionInformation.ptr_dag->add_independent_variable(*dagVar);

			dagConversionInformation.is_dagVar_initialized[mcVarIndex] = true;
		}
		void insert_dependent_mcVar_into_dag(MCvar mcVar, int mcVarIndex, DagConversionInformation& dagConversionInformation)
		{
			ModelVar* dagVar = &dagConversionInformation.dagVars[mcVarIndex];
			int numOperands = get_number_of_operands_of_MCvar(mcVar);
			std::vector<MCvar> mcVarOperands = get_mcVarOperands_of_MCvar(mcVar);
			std::vector<int> operandIndices;

			for (int i = 0; i < numOperands; i++)
				operandIndices.push_back(get_index_of_MCvar_in_MCvarVector(mcVarOperands[i], dagConversionInformation.mcVars));

			insert_not_initialize_mcVars_into_dag(operandIndices, dagConversionInformation);

			MCoperation currentOperation = get_operation_of_MCvar(mcVar);
			insert_operation_into_dag(currentOperation, *dagVar, operandIndices, dagConversionInformation);

			dagConversionInformation.is_dagVar_initialized[mcVarIndex] = true;
		}
		void insert_constant_mcVar_into_dag(MCvar mcVar, int mcVarIndex, DagConversionInformation& dagConversionInformation)
		{
			ModelVar* dagVar = &dagConversionInformation.dagVars[mcVarIndex];
			double varValue = get_value_of_MCvar(mcVar);
			dagConversionInformation.ptr_dag->add_constant_variable(*dagVar, varValue);

			dagConversionInformation.is_dagVar_initialized[mcVarIndex] = true;
		}
		void insert_not_initialize_mcVars_into_dag(std::vector<int> mcVarIndices, DagConversionInformation& dagConversionInformation)
		{
			for (int& mcVarIndex : mcVarIndices) {
				MCvar currentMcVar = dagConversionInformation.mcVars[mcVarIndex];
				if (!dagConversionInformation.is_dagVar_initialized[mcVarIndex])
					insert_mcVar_into_dag(currentMcVar, mcVarIndex, dagConversionInformation);
			}
		}
		void insert_operation_into_dag(MCoperation mcOperation, ModelVar &operationDagVar, std::vector<int> &operandIndices, DagConversionInformation& dagConversionInformation)
		{
			Dag* dag = dagConversionInformation.ptr_dag;
			std::vector<ModelVar>* dagVars = &dagConversionInformation.dagVars;
			switch (mcOperation)
			{
			case MCoperation::PLUS:
				operationDagVar = (*dagVars)[operandIndices[0]] + (*dagVars)[operandIndices[1]];
				break;

			case MCoperation::SHIFT:
				operationDagVar = (*dagVars)[operandIndices[0]] + (*dagVars)[operandIndices[1]];
				break;

			case MCoperation::TIMES:
				operationDagVar = (*dagVars)[operandIndices[0]] * (*dagVars)[operandIndices[1]];
				break;

			case MCoperation::SQRT:
				operationDagVar = sqrt((*dagVars)[operandIndices[0]]);
				break;

			case MCoperation::SQR:
				operationDagVar = sqr((*dagVars)[operandIndices[0]]);
				break;

			case MCoperation::SCALE:
				operationDagVar = (*dagVars)[operandIndices[0]] * (*dagVars)[operandIndices[1]];
				break;

			case MCoperation::MINUS:
				operationDagVar = (*dagVars)[operandIndices[0]] - (*dagVars)[operandIndices[1]];
				break;

			case MCoperation::NEG:
				operationDagVar = -(*dagVars)[operandIndices[0]]; 
				break;

			case MCoperation::TANH:
				operationDagVar = tanh((*dagVars)[operandIndices[0]]);
				break;

			case MCoperation::COS:
				operationDagVar = cos((*dagVars)[operandIndices[0]]);
				break;

			case MCoperation::SIN:
				operationDagVar = sin((*dagVars)[operandIndices[0]]);
				break;

			case MCoperation::EXP:
				operationDagVar = exp((*dagVars)[operandIndices[0]]);
				break;

			case MCoperation::LOG:
				operationDagVar = log((*dagVars)[operandIndices[0]]);
				break;

			case MCoperation::IPOW:		// Power function with integer value as exponent
				operationDagVar = pow((*dagVars)[operandIndices[0]], (*dagVars)[operandIndices[1]]);
				break;	

			case MCoperation::DIV:
				operationDagVar = (*dagVars)[operandIndices[0]] / (*dagVars)[operandIndices[1]];
				break;

			case MCoperation::INV:		// Could also be implemented as intrisic function
				operationDagVar = inv((*dagVars)[operandIndices[0]]);
				break;

			case MCoperation::FABS:
				operationDagVar = abs((*dagVars)[operandIndices[0]]);
				break;

			case MCoperation::DPOW:		// Power function with double value as exponent
				operationDagVar = pow((*dagVars)[operandIndices[0]], (*dagVars)[operandIndices[1]]);
				break;

			case MCoperation::MAXF:
				operationDagVar = max((*dagVars)[operandIndices[0]], (*dagVars)[operandIndices[1]]);
				break;


			case MCoperation::COST_FUNCTION:
				operationDagVar = cost_function(dagVars, operandIndices);
				break;

			case MCoperation::SATURATION_TEMPERATURE:
				operationDagVar = saturation_temperature(dagVars, operandIndices);
				break;

			case MCoperation::RLMTD:
				operationDagVar = rlmtd(dagVars, operandIndices);
				break;

			case MCoperation::LMTD:
				operationDagVar = lmtd(dagVars, operandIndices);
				break;

			default:
				throw std::runtime_error("Error: Unkown mcOperation during dag conversion\n");
			}
		}

		void init_function_ids(DagConversionInformation& dagConversionInformation)
		{
			Dag* dag = dagConversionInformation.ptr_dag;
			std::shared_ptr<DagObj> dagObj = dagConversionInformation.dagObj; 

			init_function_ids(dagConversionInformation, dagObj->functionsObj, dag->dagVarIdObj);
			init_function_ids(dagConversionInformation, dagObj->functionsIneq, dag->dagVarIdIneq);
			init_function_ids(dagConversionInformation, dagObj->functionsEq, dag->dagVarIdEq);
			
			dag->numDagVarIdObj = dag->dagVarIdObj.size();
			dag->numDagVarIdIneq = dag->dagVarIdIneq.size();
			dag->numDagVarIdEq = dag->dagVarIdEq.size();
		}
		void init_function_ids(DagConversionInformation& dagConversionInformation, std::vector<std::vector<mc::FFVar>> &mcDagFunctions, std::vector<int> &dagFunctionIds)
		{
			std::vector<MCvar> mcVars = dagConversionInformation.mcVars;
			std::vector<ModelVar> dagVars = dagConversionInformation.dagVars;

			// Clear old ids
			dagFunctionIds.clear();

			// Init new ids
			for (auto& function : mcDagFunctions)
			{
				int id = get_index_of_MCvar_in_MCvarVector(&function[0], mcVars);
				dagFunctionIds.push_back(dagVars[id].dagVarId);
			}
		}
	}
} // namespace SVT_DAG