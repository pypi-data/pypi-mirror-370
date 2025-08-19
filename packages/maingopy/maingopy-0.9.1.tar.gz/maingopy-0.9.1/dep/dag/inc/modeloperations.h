#ifndef MODELOPERATION_H
#define MODELOPERATION_H

#pragma once
#include "modelvar.h"
#include "operations.h"
#include "externbaseoperationdec.h"
#include "dag.h"

namespace SVT_DAG {

    ModelVar operator+(const ModelVar& x, const ModelVar& y);
    ModelVar operator-(const ModelVar& x, const ModelVar& y);
    ModelVar operator-(const ModelVar& x);
    ModelVar operator*(const ModelVar& x, const ModelVar& y);
    ModelVar operator/(const ModelVar& x, const ModelVar& y);
    ModelVar exp(const ModelVar& x);
    ModelVar pow(const ModelVar& x, const ModelVar& y);    
    ModelVar sqrt(const ModelVar& x);
    ModelVar sqr(const ModelVar& x);
    ModelVar tanh(const ModelVar& x);
    ModelVar log(const ModelVar& x);
    ModelVar abs(const ModelVar& x);
    ModelVar cos(const ModelVar& x);
    ModelVar sin(const ModelVar& x);
    ModelVar inv(const ModelVar& x);    
    ModelVar max(const ModelVar& x, const ModelVar& y);

    template <typename T> ModelVar operator+(const ModelVar& x, const T& y)
    {

        if (!x.dag)
        {
            throw std::runtime_error("Error: operator+ with variable not associated with a Dag.");
        }

        ModelVar yModelVar;
        x.dag->add_constant_variable(yModelVar, y);

        //return x.dag->insert_dependent_with_operation_and_operands(&opAddition, std::vector< ModelVar >{ x, yModelVar });
        ModelVar operands[2] = { x, yModelVar };
        return x.dag->insert_dependent_with_operation_and_operands(&opAddition, operands, 2);
    }
    template <typename T> ModelVar operator+(const T& x, const ModelVar& y)
    {
        return y + x;
    }
    template <typename T> ModelVar operator-(const ModelVar& x, const T& y)
    {

        if (!x.dag)
        {
            throw std::runtime_error("Error: operator- with variable not associated with a Dag.");
        }

        ModelVar yModelVar;
        x.dag->add_constant_variable(yModelVar, dataType(y));

        ModelVar operands[2] = { x, yModelVar };
        return x.dag->insert_dependent_with_operation_and_operands(&opSubtraction, operands, 2);

    }
    template <typename T> ModelVar operator-(const T& x, const ModelVar& y)
    {
        if (!y.dag)
        {
            throw std::runtime_error("Error: operator- with variable not associated with a Dag.");
        }

        ModelVar xModelVar;
        y.dag->add_constant_variable(xModelVar, x);

        ModelVar operands[2] = { xModelVar, y };
        return y.dag->insert_dependent_with_operation_and_operands(&opSubtraction, operands, 2);
    }
    template <typename T> ModelVar operator*(const ModelVar& x, const T& y)
    {

        if (!x.dag)
        {
            throw std::runtime_error("Error: operator* with variable not associated with a Dag.");
        }

        ModelVar yModelVar;
        x.dag->add_constant_variable(yModelVar, y);

        ModelVar operands[2] = { x, yModelVar };
        return x.dag->insert_dependent_with_operation_and_operands(&opMultiplication, operands, 2);

    }
    template <typename T> ModelVar operator*(const T& x, const ModelVar& y)
    {
        return y * x;
    }
    template <typename T> ModelVar operator/(const ModelVar& x, const T& y)
    {
        if (!x.dag)
        {
            throw std::runtime_error("Error: operator/ with variable not associated with a Dag.");
        }

        ModelVar yModelVar;
        x.dag->add_constant_variable(yModelVar, y);

        ModelVar operands[2] = { x, yModelVar };
        return x.dag->insert_dependent_with_operation_and_operands(&opDivision, operands, 2);
    }
    template <typename T> ModelVar operator/(const T& x, const ModelVar& y)
    {
        if (!y.dag)
        {
            throw std::runtime_error("Error: operator/ with variable not associated with a Dag.");
        }

        ModelVar xModelVar;
        y.dag->add_constant_variable(xModelVar, x);

        ModelVar operands[2] = { xModelVar, y };
        return y.dag->insert_dependent_with_operation_and_operands(&opDivision, operands, 2);
    }
    template <typename T> ModelVar pow(const ModelVar& x, const T& y)
    {
        if (!x.dag)
        {
            throw std::runtime_error("Error: pow with variable not associated with a Dag.");
        }

        ModelVar yModelVar;
        x.dag->add_constant_variable(yModelVar, y);

        ModelVar operands[2] = { x, yModelVar };
        return x.dag->insert_dependent_with_operation_and_operands(&opPower, operands, 2);
    }   
    template <typename T> ModelVar pow(const T& x, const ModelVar& y)
    {
        if (!y.dag)
        {
            throw std::runtime_error("Error: pow with variable not associated with a Dag.");
        }

        ModelVar xModelVar;
        y.dag->add_constant_variable(xModelVar, x);

        ModelVar operands[2] = { y, xModelVar };
        return y.dag->insert_dependent_with_operation_and_operands(&opPower, operands, 2);
    } 
    template <typename T> ModelVar max(const ModelVar& x, const T& y)
    {
        if (!x.dag)
        {
            throw std::runtime_error("Error: max with variable not associated with a Dag.");
        }

        ModelVar yModelVar;
        x.dag->add_constant_variable(yModelVar, y);

        ModelVar operands[2] = { x, yModelVar };
        return x.dag->insert_dependent_with_operation_and_operands(&opMaximum, operands, 2);
    }
    template <typename T> ModelVar max(const T& x, const ModelVar& y)
    {
        if (!y.dag)
        {
            throw std::runtime_error("Error: max with variable not associated with a Dag.");
        }

        ModelVar xModelVar;
        y.dag->add_constant_variable(xModelVar, x);

        ModelVar operands[2] = { y, xModelVar };
        return y.dag->insert_dependent_with_operation_and_operands(&opMaximum, operands, 2);
    }

} // namespace SVT_DAG

#endif // MODELOPERATION_H