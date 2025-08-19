#include "dagprinting.h"
#include <iostream>

namespace SVT_DAG {

    void
        print(const IndependentDagVar& var)
    {
        std::cout << "IndependentDagVar w/ dagVarId #" << var.dagVarId << std::endl;
    }

    void
        print(const DependentDagVar& var)
    {
        std::cout << "  DependentDagVar w/ dagVarId #" << var.dagVarId << std::endl;
        std::cout << "     -> corresponding operation: ";
        var.operation->print(); std::cout << std::endl;
        std::cout << "     -> operands: " << std::endl;
        for (int i = 0; i < var.numOperands; i++)
        {
            std::cout << "        Dag variable #" << var.operandIds[i] << std::endl;
        }
    }

    void
        print(const ConstantDagVar& var)
    {
        std::cout << "   ConstantDagVar w/ dagVarId #" << var.dagVarId << std::endl;
    }

    void
        print(const Dag& dag)
    {
        for (const IndependentDagVar& var : dag.independentVars)
        {
            print(var);
        }
        for (const ConstantDagVar& var : dag.constantVars)
        {
            print(var);
        }
        for (const DependentDagVar& var : dag.dependentVars)
        {
            print(var);
        }
    }

} // namespace SVT_DAG