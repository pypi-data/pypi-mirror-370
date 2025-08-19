
#pragma once

#include "dag.h"
#include "modeloperations.h"
#include "ffunc.hpp"

namespace maingo {
	namespace lbp {
		struct DagObj;
	}
}

namespace SVT_DAG {

	typedef mc::FFGraph MCdag;
	typedef mc::FFVar* MCvar;
	typedef mc::FFOp::TYPE MCoperation;
	using maingo::lbp::DagObj;


	void construct_dag_from_MCdag(Dag &dag, MCdag& mcDag, std::shared_ptr<DagObj> dagObj);

	namespace DagConversionHelpFunctions {
		struct DagConversionInformation {
			MCdag* ptr_mcDag;
			Dag* ptr_dag;
			std::shared_ptr<DagObj> dagObj;

			int numDagVars;
			std::vector<bool> is_dagVar_initialized;
			std::vector<MCvar> mcVars;
			std::vector<ModelVar> dagVars;

			DagConversionInformation(MCdag& mcDag, Dag& dag, std::shared_ptr<DagObj> dagObj)
			{
				ptr_mcDag = &mcDag;
				ptr_dag = &dag;
				this->dagObj = dagObj;

				init_numDagVars();
				init_is_dagVar_initialized();
				init_mcVars();
				init_dagVars();
			}

		private:
			void init_numDagVars()
			{
				numDagVars = ptr_mcDag->Vars().size();
			}
			void init_is_dagVar_initialized()
			{
				is_dagVar_initialized = std::vector<bool>(numDagVars, false);
			}
			void init_mcVars()
			{
				std::set< MCvar, mc::lt_FFVar > mcDagVars = ptr_mcDag->Vars();
				std::set<MCvar, mc::lt_FFVar>::iterator it;

				//std::vector<MCvar> mcVarVector;
				for (it = mcDagVars.begin(); it != mcDagVars.end(); it++)
					mcVars.push_back(*it);
			}
			void init_dagVars()
			{
				dagVars = std::vector<ModelVar>(numDagVars);
			}
		};

		int get_index_of_MCvar_in_MCvarVector(MCvar mcVar, std::vector<MCvar>& mcVars);
		double get_value_of_MCvar(MCvar mcVar);
		int get_number_of_operands_of_MCvar(MCvar mcVar);
		std::vector<MCvar> get_mcVarOperands_of_MCvar(MCvar mcVar);
		MCoperation get_operation_of_MCvar(MCvar mcVar);

		void init_dagVars(DagConversionInformation& dagConversionInformation);
		void init_function_ids(DagConversionInformation& dagConversionInformation);
		void init_function_ids(DagConversionInformation& dagConversionInformation, std::vector<std::vector<mc::FFVar>> &mcDagFunctions, std::vector<int> &dagFunctionIds);

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

		void insert_mcVar_into_dag(MCvar mcVar, int mcVarIndex, DagConversionInformation& dagConversionInformation);
		void insert_independent_mcVar_into_dag(MCvar mcVar, int mcVarIndex, DagConversionInformation& dagConversionInformation);
		void insert_dependent_mcVar_into_dag(MCvar mcVar, int mcVarIndex, DagConversionInformation& dagConversionInformation);
		void insert_constant_mcVar_into_dag(MCvar mcVar, int mcVarIndex, DagConversionInformation& dagConversionInformation);

		void insert_not_initialize_mcVars_into_dag(std::vector<int> mcVarIndices, DagConversionInformation& dagConversionInformation);
		void insert_operation_into_dag(MCoperation mcOperation, ModelVar& operationDagVar, std::vector<int> &operandIndices, DagConversionInformation& dagConversionInformation);		
	}

} // namespace SVT_DAG