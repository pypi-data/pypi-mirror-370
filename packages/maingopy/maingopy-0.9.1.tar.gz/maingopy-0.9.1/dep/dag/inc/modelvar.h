#ifndef MODELVAR_H
#define MODELVAR_H

#pragma once
#include "dagdatatypes.h"

#include <cstdlib>

namespace SVT_DAG {

    struct Dag;

    struct ModelVar
    {
        ModelVar() {};
        ModelVar(Dag& dag) { this->dag = &dag; }

        template <typename T>
        ModelVar& operator=(const T& y);

        Dag* dag{};
        std::size_t dagVarId;
    };
} // namespace SVT_DAG

#endif // MODELVAR_H