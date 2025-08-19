/**********************************************************************************
 * Copyright (c) 2023 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#include "nrtl_subroutines.hpp"

#include <cstddef>            // for size_t
#include <cmath>               // for exp, log, pow
#include <memory>              // for allocator_traits<>::value_type
#include <stdexcept>           // for invalid_argument

namespace ale {
 
    //the parameters are a, b, c, d, e, f and alpha, for further info, see ASPEN help

    VarType nrtl_subroutine_tau(double t, VarType a, VarType b, VarType e, VarType f) {
        VarType tau(a.size(), std::vector<double>(a[0].size(), 0.0));
        size_t it = a.size();
        size_t jt = a[0].size();
        for (int i = 0; i < it; i++) {
            for (int j = 0; j < jt; j++) {
                if (i != j) {
                    tau[i][j] = a[i][j] + b[i][j] / t + e[i][j] * std::log(t) + f[i][j] * t;
                }
            }
        }
        return tau;
    }

    double nrtl_subroutine_tau(double t, double a, double b, double e, double f) {
        return a + b / t + e * std::log(t) + f * t;
    }

    VarType nrtl_subroutine_G(double t, VarType tau, VarType c, VarType d) {
        VarType G(tau.size(), std::vector<double>(tau[0].size(), 1.0));
        size_t it = tau.size();
        size_t jt = tau[0].size();
        for (int i = 0; i < it; i++) {
            for (int j = 0; j < jt; j++) {
                if (i != j) {
                    double alpha = c[i][j] + d[i][j] * (t - 273.15);
                    G[i][j] = std::exp(-alpha*tau[i][j]);
                }
            }
        }
        return G;
    }

    double nrtl_subroutine_G(double t, double a, double b, double e, double f, double alpha) {
        if (alpha < 0) {
            throw std::invalid_argument("Parameter alpha used in computation of g is negative!");
        }
        return std::exp(-alpha * (a + b / t + e * std::log(t) + f * t));
    }

    VarType nrtl_subroutine_Gtau(VarType G, VarType tau) {
        VarType Gtau(tau.size(), std::vector<double>(tau[0].size(), 0.0));
        size_t it = tau.size();
        size_t jt = tau[0].size();
        for (int i = 0; i < it; i++) {
            for (int j = 0; j < jt; j++) {
                if (i != j) {
                    Gtau[i][j] = G[i][j] * tau[i][j];
                }
            }
        }
        return Gtau;
    }

    double nrtl_subroutine_Gtau(double t, double a, double b, double e, double f, double alpha) {
        if (alpha < 0) {
            throw std::invalid_argument("Parameter alpha used in computation of gtau is negative!");
        }
        return nrtl_subroutine_G(t, a, b, e, f, alpha) * nrtl_subroutine_tau(t, a, b, e, f);
    }

    double nrtl_subroutine_dtau(double t, double b, double e, double f) {
        return f - b / std::pow(t, 2) + e / t;
    }

    VarType nrtl_subroutine_Gdtau(double t, VarType G, VarType b, VarType e, VarType f) {
        VarType Gdtau(G.size(), std::vector<double>(G[0].size(), 0.0));
        size_t it = G.size();
        size_t jt = G[0].size();
        for (int i = 0; i < it; i++) {
            for (int j = 0; j < jt; j++) {
                if (i != j) {
                    Gdtau[i][j] = G[i][j] * (f[i][j] - b[i][j] / std::pow(t, 2) + e[i][j] / t);
                }
            }
        }
        return Gdtau;
    }

    double nrtl_subroutine_Gdtau(double t, double a, double b, double e, double f, double alpha) {
        if (alpha < 0) {
            throw std::invalid_argument("Parameter alpha used in computation of gdtau is negative!");
        }
        return nrtl_subroutine_G(t, a, b, e, f, alpha) * nrtl_subroutine_dtau(t, b, e, f);
    }

    double nrtl_subroutine_dGtau(double t, double a, double b, double e, double f, double alpha) {
        if (alpha < 0) {
            throw std::invalid_argument("Parameter alpha used in computation of dgtau is negative!");
        }
        return -alpha * nrtl_subroutine_Gtau(t, a, b, e, f, alpha)*nrtl_subroutine_dtau(t, b, e, f);
    }

}
