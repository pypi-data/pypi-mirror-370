#include "modeloperations.h"
#include <memory>
#include <stdexcept>
#include <vector>

namespace SVT_DAG {

    ModelVar operator+(const ModelVar& x, const ModelVar& y)
    {

        if ((!x.dag) || (!y.dag))
        {
            throw std::runtime_error("Error: operator+ with variables not associated with a Dag.");
        }
        if (x.dag != y.dag)
        {
            throw std::runtime_error("Error: operator+ with variables from different Dags. ");
        }

        //return x.dag->insert_dependent_with_operation_and_operands(&opAddition, std::vector< ModelVar >{ x, y });
        ModelVar operands[2] = { x,y };
        return x.dag->insert_dependent_with_operation_and_operands(&opAddition, operands, 2);
    }
    ModelVar operator-(const ModelVar& x, const ModelVar& y)
    {

        if ((!x.dag) || (!y.dag))
        {
            throw std::runtime_error("Error: operator- with variables not associated with a Dag.");
        }
        if (x.dag != y.dag)
        {
            throw std::runtime_error("Error: operator- with variables from different Dags. ");
        }

        ModelVar operands[2] = { x,y };
        return x.dag->insert_dependent_with_operation_and_operands(&opSubtraction, operands, 2);
    }
    ModelVar operator-(const ModelVar& x)
    {
        if (!x.dag)
        {
            throw std::runtime_error("Error: exp with variables not associated with a Dag.");
        }

        ModelVar operands[1] = { x };
        return x.dag->insert_dependent_with_operation_and_operands(&opNegative, operands, 1);
    }
    ModelVar operator*(const ModelVar& x, const ModelVar& y)
    {

        if ((!x.dag) || (!y.dag))
        {
            throw std::runtime_error("Error: operator* with variables not associated with a Dag.");
        }
        if (x.dag != y.dag)
        {
            throw std::runtime_error("Error: operator* with variables from different Dags. ");
        }

        ModelVar operands[2] = { x,y };
        return x.dag->insert_dependent_with_operation_and_operands(&opMultiplication, operands, 2);
    }
    ModelVar operator/(const ModelVar& x, const ModelVar& y)
    {

        if ((!x.dag) || (!y.dag))
        {
            throw std::runtime_error("Error: operator/ with variables not associated with a Dag.");
        }
        if (x.dag != y.dag)
        {
            throw std::runtime_error("Error: operator/ with variables from different Dags. ");
        }

        ModelVar operands[2] = { x,y };
        return x.dag->insert_dependent_with_operation_and_operands(&opDivision, operands, 2);
    }

    ModelVar exp(const ModelVar& x)
    {
        if (!x.dag)
        {
            throw std::runtime_error("Error: exp with variables not associated with a Dag.");
        }

        ModelVar operands[1] = { x };
        return x.dag->insert_dependent_with_operation_and_operands(&opExponential, operands, 1);
    }
    ModelVar pow(const ModelVar& x, const ModelVar& y)
    {
        if ((!x.dag) || (!y.dag))
        {
            throw std::runtime_error("Error: pow with variables not associated with a Dag.");
        }
        if (x.dag != y.dag)
        {
            throw std::runtime_error("Error: pow with variables from different Dags. ");
        }

        ModelVar operands[2] = { x,y };
        return x.dag->insert_dependent_with_operation_and_operands(&opPower, operands, 2);
    }
    ModelVar sqrt(const ModelVar& x)
    {
        if (!x.dag)
        {
            throw std::runtime_error("Error: square root with variable not associated with a Dag.");
        }

        ModelVar operands[1] = { x };
        return x.dag->insert_dependent_with_operation_and_operands(&opSquareRoot, operands, 1);
    }
    ModelVar sqr(const ModelVar& x)
    {
        if (!x.dag)
        {
            throw std::runtime_error("Error: square with variable not associated with a Dag.");
        }

        ModelVar operands[1] = { x };
        return x.dag->insert_dependent_with_operation_and_operands(&opSquare, operands, 1);
    }
    ModelVar tanh(const ModelVar& x) {
        if (!x.dag)
        {
            throw std::runtime_error("Error: tanh with variable not associated with a Dag.");
        }

        ModelVar operands[1] = { x };
        return x.dag->insert_dependent_with_operation_and_operands(&opTangensHyperbolicus, operands, 1);
    }
    ModelVar log(const ModelVar& x) {
        if (!x.dag)
        {
            throw std::runtime_error("Error: log with variable not associated with a Dag.");
        }

        ModelVar operands[1] = { x };
        return x.dag->insert_dependent_with_operation_and_operands(&opLogarithmus, operands, 1);
    }
    ModelVar abs(const ModelVar& x) {
        if (!x.dag)
        {
            throw std::runtime_error("Error: log with variable not associated with a Dag.");
        }

        ModelVar operands[1] = { x };
        return x.dag->insert_dependent_with_operation_and_operands(&opAbsoluteValue, operands, 1);
    }
    ModelVar cos(const ModelVar& x) {
        if (!x.dag)
        {
            throw std::runtime_error("Error: cos with variable not associated with a Dag.");
        }

        ModelVar operands[1] = { x };
        return x.dag->insert_dependent_with_operation_and_operands(&opCosinus, operands, 1);
    }
    ModelVar sin(const ModelVar& x) {
        if (!x.dag)
        {
            throw std::runtime_error("Error: sin with variable not associated with a Dag.");
        }

        ModelVar operands[1] = { x };
        return x.dag->insert_dependent_with_operation_and_operands(&opSinus, operands, 1);
    }
    ModelVar inv(const ModelVar& x) {
        if (!x.dag)
        {
            throw std::runtime_error("Error: inv with variable not associated with a Dag.");
        }

        ModelVar operands[1] = { x };
        return x.dag->insert_dependent_with_operation_and_operands(&opInverse, operands, 1);
    }
    ModelVar max(const ModelVar& x, const ModelVar& y)
    {
        if ((!x.dag) || (!y.dag))
        {
            throw std::runtime_error("Error: max with variables not associated with a Dag.");
        }
        if (x.dag != y.dag)
        {
            throw std::runtime_error("Error: max with variables from different Dags. ");
        }

        ModelVar operands[2] = { x,y };
        return x.dag->insert_dependent_with_operation_and_operands(&opMaximum, operands, 2);
    }

} // namespace SVT_DAG