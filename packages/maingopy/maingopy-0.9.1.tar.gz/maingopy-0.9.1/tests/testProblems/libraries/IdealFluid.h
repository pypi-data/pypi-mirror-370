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

#ifndef IDEALFLUID_H_
#define IDEALFLUID_H_

#include "math.h"

// This struct stores all constants needed to solve functions of an ideal stream
struct IdealFluid {
    double cpig;      //heat capacity ideal gas		[kJ/kg*K]
    double cif;       //heat capacity ideal fluid		[kJ/kg*K]
    double Rm;        //specific gas constant 			[kJ/kg*K]
    double vif;       //specific volume ideal fluid 	[m^3/kg]
    double A;         //for Antoine equation (in bar,K)	[-]
    double B;         //for Antoine equation (in bar,K)	[-]
    double C;         //for Antoine equation (in bar,K)	[-]
    double deltaH;    //evaporation enthalpy			[kJ/kg]
    double deltaS;    //evaporation entropy			[kJ/kg*K]

    IdealFluid():
        cpig(), cif(), Rm(), vif(), A(), B(), C(), deltaH(), deltaS() {}

    IdealFluid(const double cpigIn, const double cifIn, const double RmIn, const double vifIn, const double AIn, const double BIn, const double CIn, const double deltaHIn, const double deltaSIn):
        cpig(cpigIn), cif(cifIn), Rm(RmIn), vif(vifIn), A(AIn), B(BIn), C(CIn), deltaH(deltaHIn), deltaS(deltaSIn)
    {
    }

    IdealFluid(const IdealFluid &theFluid)
    {
        *this = theFluid;
    }

    IdealFluid &operator=(const IdealFluid &theFluid)
    {
        if (this != &theFluid) {
            cpig   = theFluid.cpig;
            cif    = theFluid.cif;
            Rm     = theFluid.Rm;
            vif    = theFluid.vif;
            A      = theFluid.A;
            B      = theFluid.B;
            C      = theFluid.C;
            deltaH = theFluid.deltaH;
            deltaS = theFluid.deltaS;
        }
        return *this;
    }
};


enum ST {    //enables the function to distinguish which variables are set
    ST_pT,
    ST_ph,
    ST_ps,
    ST_px,
    ST_undefined
};

struct DefinedStateVars {    // stores the information on which variables have already been computed
    bool p;
    bool t;
    bool h;
    bool s;
    bool ts;
    bool x;
    bool hsatvap;
    bool hsatliq;
    bool ssatvap;
    bool ssatliq;


    void setAllFalse()
    {
        p       = false;
        t       = false;
        h       = false;
        s       = false;
        ts      = false;
        x       = false;
        hsatvap = false;
        hsatliq = false;
        ssatvap = false;
        ssatliq = false;
    }
};

#endif /* IDEALFLUID_H_ */
