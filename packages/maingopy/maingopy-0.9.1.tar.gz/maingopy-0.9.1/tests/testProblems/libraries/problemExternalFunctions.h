/**********************************************************************************
 * Copyright (c) 2019 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#ifndef EXTERNALFUNCTIONS_H_
#define EXTERNALFUNCTIONS_H_

#define MY_PI 3.14159265358979323846 /* pi */


using Var = mc::FFVar;    // this allows us to write Var instead of mc::FFVar


/**
* @class SomeExternalClass
* @brief Exemplary class needed in problem.h 
*
* This class provides some exemplary functions called in problem.h
*/
class SomeExternalClass {

  public:
    /**
		* @brief Constructor setting parameter _p1 to p1 and _p2 to p2
		*
		* @param[in] p1 is the parameter value	
		* @param[in] p2 is the parameter value	
		*/
    SomeExternalClass(Var p1, Var p2):
        _p1(p1), _p2(p2)
    {
    }

    /**
		* @brief Constructor setting parameter _p1 to p1 and _p2 to 5
		*
		* @param[in] p1 is the parameter value	
		*/
    SomeExternalClass(Var p1):
        _p1(p1)
    {
        _p2 = 5;
    }

    /**
		* @brief Default constructor setting parameter _p1 to 3 and _p2 to 5
		*/
    SomeExternalClass()
    {
        _p1 = 3;
        _p2 = 5;
    }

    /**
		* @brief Copy constructor 
		*
		* @param[in] mySomeExternalClass is some other object of class SomeExternalClass
		*/
    SomeExternalClass(const SomeExternalClass &mySomeExternalClass)
    {
        *this = mySomeExternalClass;
    }

    /**
		* @brief Copy constructor via = operator
		*
		* @param[in] mySomeExternalClass is some other object of class SomeExternalClass
		*/
    SomeExternalClass &operator=(const SomeExternalClass &mySomeExternalClass)
    {
        if (this != &mySomeExternalClass) {
            _p1 = mySomeExternalClass._p1;
            _p2 = mySomeExternalClass._p2;
        }

        return *this;
    }

    /**
		* @brief Function for setting _p1 to p1 
		*
		* @param[in] p1 is the parameter value	
		*/
    void set_p1(Var p1)
    {
        _p1 = p1;
    }

    /**
		* @brief Function for setting _p2 to p2 
		*
		* @param[in] p2 is the parameter value	
		*/
    void set_p2(Var p2)
    {
        _p2 = p2;
    }

    /**
		* @brief Function for setting parameter _p1 to p1 and _p2 to p2
		*
		* @param[in] p1 is the parameter value	
		* @param[in] p2 is the parameter value	
		*/
    void set_p1_p2(Var p1, Var p2)
    {
        _p1 = p1;
        _p2 = p2;
    }

    /**
		* @brief Exemplary function 
		*
		* @param[in] x is the first variable
		* @param[in] y is the second variable
		
		*/
    Var functionOne(Var x, Var y)
    {
        Var result = -_p1 * sqrt((sqr(x) + sqr(y)) / 2.);
        return result;
    }

    /**
		* @brief Exemplary function 
		*
		* @param[in] x is the first variable
		* @param[in] y is the second variable
		
		*/
    Var functionTwo(Var x, Var y)
    {
        Var result = (cos(_p2 * x) + cos(_p2 * y)) / 2.;
        return result;
    }

  private:
    // parameters
    Var _p1;
    Var _p2;
};

#endif
