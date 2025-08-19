#include "modelvar.h"
#include "dag.h"

namespace SVT_DAG {
    template <typename T>
    ModelVar& ModelVar::operator=(const T& y)
    {
        if (!this->dag)
            throw std::runtime_error("Error: operator= with variable not associated with a Dag.");

        ModelVar yModelVar;
        this->dag->add_constant_variable(yModelVar, convert_to_double(y));
        this->dagVarId = yModelVar.dagVarId;
        return *this;
    }
} // namespace SVT_DAG