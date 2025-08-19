/**********************************************************************************
 * Copyright (c) 2019-2024 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#pragma once

#include "ffunc.hpp"

#include <string>
#include <vector>


namespace maingo {


/**
    * @struct ModelFunction
    * @brief Struct for making work with the EvaluationContainer easier for the user and also to ensure backward compatibility
    */
struct ModelFunction {

    ModelFunction()                                 = default;
    ~ModelFunction()                                = default;
    ModelFunction(const ModelFunction &)            = default;
    ModelFunction(ModelFunction &&)                 = default;
    ModelFunction &operator=(const ModelFunction &) = default;
    ModelFunction &operator=(ModelFunction &&)      = default;

    /**
        *  @brief Constructor with FFVar value only
        */
    ModelFunction(const mc::FFVar var)
    {
        value.clear();
        value.push_back(var);
        name.clear();
        name.push_back("");
    }

    /**
        *  @brief Constructor with FFVar value and a name
        */
    ModelFunction(const mc::FFVar var, const std::string &str)
    {
        value.clear();
        value.push_back(var);
        name.clear();
        name.push_back(str);
    }

    /**
        *  @brief Constructor with vector of FFVar
        */
    ModelFunction(const std::vector<mc::FFVar> &vars)
    {
        value = vars;
        name  = std::vector<std::string>(value.size(), "");
    }

    /**
        *  @brief Function deleting everything in the model function
        */
    void clear()
    {
        value.clear();
        name.clear();
    }

    /**
        *  @brief Function for inserting a FFVar value at the end of the value vector
        */
    void push_back(const mc::FFVar var)
    {
        value.push_back(var);
        name.push_back("");
    }

    /**
        *  @brief Function for inserting a FFVar and a name at the end of the vectors
        */
    void push_back(const mc::FFVar var, const std::string &str)
    {
        value.push_back(var);
        name.push_back(str);
    }

    /**
        *  @brief Function for inserting a vector of FFVar at the end of the value vector
        */
    void push_back(const std::vector<mc::FFVar> &vars)
    {
        for (size_t i = 0; i < vars.size(); i++) {
            value.push_back(vars[i]);
            name.push_back("");
        }
    }

    /**
        *  @brief Function for inserting a vector of FFVar at the end of the value vector with names
        */
    void push_back(const std::vector<mc::FFVar> &vars, const std::string &baseName)
    {
        if (vars.size() == 1) {
            value.push_back(vars[0]);
            name.push_back(baseName);
        }
        else if (baseName == "") {
            push_back(vars);
        }
        else {
            for (size_t i = 0; i < vars.size(); i++) {
                value.push_back(vars[i]);
                name.push_back(baseName + '_' + std::to_string(i + 1));
            }
        }
    }

    /**
        *  @brief Function returning the size of the value vector. Note that value and name vectors have the same size at any time
        */
    size_t size() const
    {
        return value.size();
    }

    /**
        *  @brief Function for resizing of the underlying vectors
        */
    void resize(const size_t size)
    {
        value.resize(size);
        name.resize(size);
    }

    /**
        *  @brief Function for seting FFVar value at a given index
        */
    void set_value(const mc::FFVar var, const unsigned i)
    {
        value[i] = var;
    }

    /**
        *  @brief Function for seting name value at a given index
        */
    void set_name(const std::string str, const unsigned i)
    {
        name[i] = str;
    }

    /**
        *  @brief = operator for backward compatibility
        */
    inline ModelFunction &operator=(const mc::FFVar var)
    {
        value.clear();
        value.push_back(var);
        name.clear();
        name.push_back("");
        return *this;
    }

    /**
        *  @brief [] operator for easier access to value vector
        */
    inline mc::FFVar &operator[](const unsigned int i)
    {
        return value[i];
    }

    /**
        *  @brief Function for accessing elements
        */
    inline mc::FFVar &at(const unsigned int i)
    {
        return value.at(i);
    }

    /**
        *  @brief Equality comparison operator
        */
    inline bool operator==(const ModelFunction &other) const
    {
        return ((name == other.name) && (value == other.value));
    }

    std::vector<std::string> name = {}; /*!< vector holding possible function names */
    std::vector<mc::FFVar> value = {};  /*!< vector holding the actual propagated FFVar values */
};

}    // end namespace maingo