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

#pragma once

#include "usingAdditionalIntrinsicFunctions.h"

#include <iostream>

#define NRTL_ENV    // use this to set whether to use envelopes for nrtl functions (tau,G,Gtau,dGtau,Gdtau) or not -- TO USE THIS IT HAS TO HOLD THAT d = 0


//////////////////////////////////////////////////////////////////////////
// Auxiliary struct for storing the binary interaction parameters
struct NRTLpars {
    std::vector<std::vector<double>> a, b, c, d, e, f;
};


//////////////////////////////////////////////////////////////////////////
// Class for NRTL model
class NRTL {
  private:
    NRTLpars _pars;
    size_t _ncomp;
    const double maxLnGamma, minLnGamma;

    template <typename U>
    std::vector<std::vector<U>> _getTau_env(const U &T);
    template <typename U>
    std::vector<std::vector<U>> _getG_env(const U &T, const std::vector<std::vector<U>> &tau);
    template <typename U>
    std::vector<std::vector<U>> _getTau(const U &T);
    template <typename U>
    std::vector<std::vector<U>> _getG(const U &T, const std::vector<std::vector<U>> &tau);
    template <typename U>
    std::vector<std::vector<U>> _getdTaudT(const U &T);
    template <typename U>
    std::vector<std::vector<U>> _getdGdT(const U &T, const std::vector<std::vector<U>> &tau, const std::vector<std::vector<U>> &dTaudT);

  public:
    NRTL():
        maxLnGamma(std::log(100000000000000000.)), minLnGamma(std::log(1 / 1000000000000000.)) {}

    template <typename U>
    void setPars(NRTLpars parsIN);
    template <typename U>
    std::vector<U> calculateGamma(const U &T, const std::vector<U> &x);
    template <typename U>
    std::vector<U> calculateGammaLog(const U &T, const std::vector<U> &x);
    template <typename U>
    U calculateInifiniteDilutionGammaLog(const U &T, const unsigned iSolute, const unsigned iSolvent);
    template <typename U>
    U calculateHE(const U &T, const std::vector<U> &x);
};


//////////////////////////////////////////////////////////////////////////
// Member function for specifying binary interaction parameters
template <typename U>
void
NRTL::setPars(NRTLpars parsIn)
{
    if ((parsIn.a.size() != parsIn.b.size()) || (parsIn.a.size() != parsIn.c.size())) {
        std::cerr << "Inconsistent dimensions in specification of NRTL binary interaction parameters." << std::endl;
        throw(-1);
    }
    _pars  = parsIn;
    _ncomp = parsIn.a.size();
}


//////////////////////////////////////////////////////////////////////////
// Member function for computing the activity coefficient
template <typename U>
std::vector<U>
NRTL::calculateGamma(const U &T, const std::vector<U> &x)
{
    if (_ncomp != _pars.a.size()) {
        std::cerr << "Dimension of composition std::vector inconsistent with size of NRTL binary interaction parameter matrix when querying activity coefficient." << std::endl;
        throw(-1);
    }
    std::vector<std::vector<U>> tau(_getTau<U>(T));
    std::vector<std::vector<U>> G(_getG<U>(T, tau));
    std::vector<U> gamma(_ncomp);
    U sumC1, sumC2, sumC3;
    std::vector<double> coeff(x.size() + 1, 1.0);
    for (unsigned k = 0; k < _ncomp; k++) {
        U sumA = 0.0, sumB = 0.0, sumC = 0.0;
        std::vector<U> denomA, denomB;
        for (unsigned i = 0; i < _ncomp; i++) {
#ifndef NRTL_ENV
            sumA += tau[i][k] * G[i][k] * x[i];
#else
            // sumA += tau[i][k]*G[i][k]*x[i];
            sumA += nrtl_Gtau(T, _pars.a[i][k], _pars.b[i][k], _pars.e[i][k], _pars.f[i][k], _pars.c[i][k]) * x[i];
            // sumA += xexpax(nrtl_tau(T,_pars.a[i][k],_pars.b[i][k],_pars.e[i][k],_pars.f[i][k]),-_pars.c[i][k])*x[i];
#endif

            sumB += G[i][k] * x[i];
            sumC1 = 0.0;
            sumC2 = 0.0;
            sumC3 = 0.0;
            denomA.clear();
            denomA.push_back(x[i]);    // actually, G[i][i]*x[i], but G[i][i]=1
            for (unsigned j = 0; j < _ncomp; j++) {
                sumC1 += G[j][i] * x[j];
                if (i != j) {
                    denomA.push_back(G[j][i] * x[j]);
                }
#ifndef NRTL_ENV
                sumC2 += tau[j][i] * G[j][i] * x[j];
#else
                // sumC2 += tau[j][i]*G[j][i]*x[j];
                sumC2 += nrtl_Gtau(T, _pars.a[j][i], _pars.b[j][i], _pars.e[j][i], _pars.f[j][i], _pars.c[j][i]) * x[j];
                // sumC2 += xexpax(nrtl_tau(T,_pars.a[j][i],_pars.b[j][i],_pars.e[j][i],_pars.f[j][i]),-_pars.c[j][i])*x[j];

                denomB.clear();
                denomB.push_back(G[j][i] * x[j]);
                for (unsigned l = 0; l < _ncomp; l++) {
                    if (l != j) {
                        denomB.push_back(G[l][i] * x[l]);
                    }
                }
                if (k == j) {
                    sumC3 += nrtl_Gtau(T, _pars.a[k][i], _pars.b[k][i], _pars.e[k][i], _pars.f[k][i], _pars.c[k][i]) * sum_div(denomB, coeff);
                }
                else {
                    sumC3 += G[k][i] * tau[j][i] * sum_div(denomB, coeff);
                }
#endif
            }
#ifndef NRTL_ENV
            // sumC += x[i]*G[k][i]*(tau[k][i]/pos(sumC1) - sumC2/pos(pow(sumC1,2)));
            sumC += x[i] * G[k][i] * (tau[k][i] - sumC2 / pos(sumC1)) / pos(sumC1);
#else
            // sumC += x[i]*G[k][i]*(tau[k][i] - sumC2/pos(sumC1))/pos(sumC1);
            // sumC += x[i]/pos(sumC1) *(nrtl_Gtau(T,_pars.a[k][i],_pars.b[k][i],_pars.e[k][i],_pars.f[k][i],_pars.c[k][i]) - G[k][i]*sumC2/pos(sumC1));
            // sumC += x[i]/pos(sumC1) *(xexpax(nrtl_tau(T,_pars.a[k][i],_pars.b[k][i],_pars.e[k][i],_pars.f[k][i]),-_pars.c[k][i]) - G[k][i]*sumC2/pos(sumC1));
            // sumC += x[i]/pos(sumC1) *nrtl_Gtau(T,_pars.a[k][i],_pars.b[k][i],_pars.e[k][i],_pars.f[k][i],_pars.c[k][i]) - x[i]*G[k][i]*sumC2/pos(sqr(sumC1));
            // sumC += sum_div(denomA,coeff)* (nrtl_Gtau(T,_pars.a[k][i],_pars.b[k][i],_pars.e[k][i],_pars.f[k][i],_pars.c[k][i]) - G[k][i]*sumC2/pos(sumC1));
            sumC += sum_div(denomA, coeff) * (nrtl_Gtau(T, _pars.a[k][i], _pars.b[k][i], _pars.e[k][i], _pars.f[k][i], _pars.c[k][i]) - sumC3);
            // sumC += sum_div(denomA,coeff)* G[k][i]*(tau[k][i] - sumC3);
#endif
        }
        // gamma[k] = exp( bounding_func(sumA/sumB + sumC,minLnGamma,maxLnGamma) );
        // gamma[k] = exp( sumA/pos(sumB) + sumC );
        gamma[k] = exp(bounding_func(sumA / pos(sumB) + sumC, minLnGamma, maxLnGamma));
        // gamma[k] = exp( ub_func(sumA/pos(sumB) + sumC,maxLnGamma) );
        // gamma[k] = (xexpax(nrtl_tau(T,_pars.a[k][1],_pars.b[k][1],_pars.e[k][1],_pars.f[k][1]),-_pars.c[k][1]) - G[k][1]*sumC2/pos(sumC1));
        // gamma[k] = sumC;
    }

    return gamma;
}


//////////////////////////////////////////////////////////////////////////
// Member function for computing the activity coefficient
template <typename U>
std::vector<U>
NRTL::calculateGammaLog(const U &T, const std::vector<U> &x)
{
    if (_ncomp != _pars.a.size()) {
        std::cerr << "Dimension of composition std::vector inconsistent with size of NRTL binary interaction parameter matrix when querying activity coefficient." << std::endl;
        throw(-1);
    }
    std::vector<std::vector<U>> tau(_getTau<U>(T));
    std::vector<std::vector<U>> G(_getG<U>(T, tau));
    std::vector<U> gammaLog(_ncomp);
    for (unsigned k = 0; k < _ncomp; k++) {
        U sumA = 0.0, sumB = 0.0, sumC = 0.0;
        for (unsigned i = 0; i < _ncomp; i++) {
            sumA += tau[i][k] * G[i][k] * x[i];
            sumB += G[i][k] * x[i];
            U sumC1 = 0.0, sumC2 = 0.0;
            for (unsigned j = 0; j < _ncomp; j++) {
                sumC1 += G[j][i] * x[j];
                sumC2 += tau[j][i] * G[j][i] * x[j];
            }
            sumC += x[i] * G[k][i] * (tau[k][i] / sumC1 - sumC2 / pow(sumC1, 2));
        }
        gammaLog[k] = bounding_func(sumA / sumB + sumC, minLnGamma, maxLnGamma);
    }

    return gammaLog;
}


//////////////////////////////////////////////////////////////////////////
// Member function for computing the infinite dilution activity coefficient
template <typename U>
U
NRTL::calculateInifiniteDilutionGammaLog(const U &T, const unsigned iSolute, const unsigned iSolvent)
{

    if (iSolute == iSolvent) {
        std::cerr << "Error evaluating activity coefficient at infinite dilution using NRTL model: Specified solvent and solute are identical." << std::endl;
        throw(-1);
    }

    U tauAi(_pars.a[iSolvent][iSolute] + _pars.b[iSolvent][iSolute] / T);
    U tauiA(_pars.a[iSolute][iSolvent] + _pars.b[iSolute][iSolvent] / T);
    U GiA = exp(-_pars.c[iSolute][iSolvent] * tauiA);
    return tauAi + tauiA * GiA;
}


//////////////////////////////////////////////////////////////////////////
// Member function for computing the excess enthalpy
template <typename U>
U
NRTL::calculateHE(const U &T, const std::vector<U> &x)
{
    if (x.size() != _pars.a.size()) {
        std::cerr << "Dimension of composition std::vector inconsistent with size of NRTL binary interaction parameter matrix when querying excess enthalpy." << std::endl;
        throw(-1);
    }
    std::vector<std::vector<U>> tau    = _getTau<U>(T);
    std::vector<std::vector<U>> G      = _getG<U>(T, tau);
    std::vector<std::vector<U>> dTaudT = _getdTaudT<U>(T);
    std::vector<std::vector<U>> dGdT   = _getdGdT<U>(T, tau, dTaudT);
    U HE                               = 0;
    U leftFactor, rightFactor;
    U div;
    for (unsigned i = 0; i < x.size(); i++) {


        // left factor
        std::vector<U> denomA;
        std::vector<double> coeff(x.size() + 1, 1.);
        denomA.push_back(G[i][i] * x[i]);
        rightFactor = 0.;
        for (unsigned j = 0; j < x.size(); j++) {
            if (j != i) {
                denomA.push_back(G[j][i] * x[j]);
            }
        }
        leftFactor = sum_div(denomA, coeff);


        // right factor
        div = 0.0;
        for (unsigned l = 0; l < x.size(); l++) {
            std::vector<U> denom;
            denom.push_back(G[l][i] * x[l]);
            for (unsigned int k = 0; k < x.size(); k++) {
                if (k != l) {
                    denom.push_back(G[k][i] * x[k]);
                }
            }
            div += tau[l][i] * sum_div(denom, coeff);
        }
        for (unsigned j = 0; j < x.size(); j++) {
            if (j != i) {
                rightFactor += nrtl_Gdtau(T, _pars.a[j][i], _pars.b[j][i], _pars.e[j][i], _pars.f[j][i], _pars.c[j][i]) * x[j] * (1 - _pars.c[j][i] * tau[j][i] + _pars.c[j][i] * div);
                // rightFactor += G[j][i]*dTaudT[j][i]*x[j]*(1 - _pars.c[j][i]*tau[j][i] + _pars.c[j][i]*div);
            }
        }


        HE += leftFactor * rightFactor;
    }
    const double R = 8.3144598;
    HE             = HE * (-R * sqr(T));
    // return HE;
    return HE;
}


//////////////////////////////////////////////////////////////////////////
// Member function for computing tau
template <typename U>
std::vector<std::vector<U>>
NRTL::_getTau(const U &T)
{
    std::vector<std::vector<U>> tau(_ncomp, std::vector<U>(_ncomp, 0.0));
    for (unsigned i = 0; i < _ncomp; i++) {
        for (unsigned j = 0; j < _ncomp; j++) {
            if (i != j) {
#ifndef NRTL_ENV
                tau[i][j] = _pars.a[i][j] + _pars.b[i][j] / T + (_pars.e[i][j] * log(T)) + _pars.f[i][j] * T;
#else
                tau[i][j] = nrtl_tau(T, _pars.a[i][j], _pars.b[i][j], _pars.e[i][j], _pars.f[i][j]);
#endif
            }
        }
    }
    return tau;
}


//////////////////////////////////////////////////////////////////////////
// Member function for computing G
template <typename U>
std::vector<std::vector<U>>
NRTL::_getG(const U &T, const std::vector<std::vector<U>> &tau)
{
    std::vector<std::vector<U>> G(_ncomp, std::vector<U>(_ncomp, 1.0));
    for (unsigned i = 0; i < _ncomp; i++) {
        for (unsigned j = 0; j < _ncomp; j++) {
            if (i != j) {
#ifndef NRTL_ENV
                U alpha = _pars.c[i][j] + _pars.d[i][j] * (T - 273.15);
                G[i][j] = exp(-alpha * tau[i][j]);
#else
                if (_pars.d[i][j] != 0) {
                    std::cerr << "d <> 0 not allowed when using NRTL envelopes." << std::endl;
                    throw(-1);
                }
                G[i][j]      = nrtl_G(T, _pars.a[i][j], _pars.b[i][j], _pars.e[i][j], _pars.f[i][j], _pars.c[i][j]);
#endif
            }
        }
    }
    return G;
}


//////////////////////////////////////////////////////////////////////////
// Member function for computing the partial derivative of tau with respect to T
template <typename U>
std::vector<std::vector<U>>
NRTL::_getdTaudT(const U &T)
{
    std::vector<std::vector<U>> dTaudT(_ncomp, std::vector<U>(_ncomp, 0.0));
    for (unsigned i = 0; i < _ncomp; i++) {
        for (unsigned j = 0; j < _ncomp; j++) {
            if (i != j) {
#ifdef NRTL_ENV
                dTaudT[i][j] = nrtl_dtau(T, _pars.b[i][j], _pars.e[i][j], _pars.f[i][j]);
#else
                dTaudT[i][j] = -_pars.b[i][j] / pow(T, 2) + _pars.e[i][j] / T + _pars.f[i][j];
#endif
            }
        }
    }
    return dTaudT;
}


//////////////////////////////////////////////////////////////////////////
// Member function for computing the partial derivative of G with respect to T
template <typename U>
std::vector<std::vector<U>>
NRTL::_getdGdT(const U &T, const std::vector<std::vector<U>> &tau, const std::vector<std::vector<U>> &dTaudT)
{
    std::vector<std::vector<U>> dGdT(_ncomp, std::vector<U>(_ncomp, 0.0));
    for (unsigned i = 0; i < _ncomp; i++) {
        for (unsigned j = 0; j < _ncomp; j++) {
            if (i != j) {
#ifdef NRTL_ENV
                dGdT[i][j] = -_pars.c[i][j] * nrtl_Gdtau(T, _pars.a[i][j], _pars.b[i][j], _pars.e[i][j], _pars.f[i][j], _pars.c[i][j]);
#else
                U alpha      = _pars.c[i][j] + _pars.d[i][j] * (T - 273.15);
                dGdT[i][j]   = -alpha * dTaudT[i][j] * exp(-alpha * tau[i][j]);
#endif
            }
        }
    }
    return dGdT;
}
