#pragma once

#include "MAiNGOException.h"
#include "symbol_table.hpp"

#include "util/evaluator.hpp"

#include "ffunc.hpp"

namespace maingo {


using namespace ale;
using namespace ale::util;
using Var      = mc::FFVar;
using VarType  = std::vector<std::vector<Var>>;
using ParaType = std::vector<std::vector<double>>;

VarType
nrtl_subroutine_tau(Var T, ParaType a, ParaType b, ParaType e, ParaType f)
{
    VarType tau(a.size(), std::vector<Var>(a[0].size(), 0.0));
    int it = a.size();
    int jt = a[0].size();
    for (int i = 0; i < it; i++) {
        for (int j = 0; j < jt; j++) {
            if (i != j) {
                tau[i][j] = mc::nrtl_tau(T, a[i][j], b[i][j], e[i][j], f[i][j]);
            }
        }
    }
    return tau;
}

Var
nrtl_subroutine_tau(Var T, double a, double b, double e, double f)
{
    return mc::nrtl_tau(T, a, b, e, f);
}

Var
nrtl_subroutine_dtau(Var T, double b, double e, double f)
{
    return mc::nrtl_dtau(T, b, e, f);
}

VarType
nrtl_subroutine_G(Var T, VarType tau, ParaType a, ParaType b, ParaType c, ParaType d, ParaType e, ParaType f)
{
    VarType G(tau.size(), std::vector<Var>(tau[0].size(), 1.0));
    int it = tau.size();
    int jt = tau[0].size();
    for (int i = 0; i < it; i++) {
        for (int j = 0; j < jt; j++) {
            if (i != j) {
                double alpha = c[i][j] + d[i][j] * (T.num().val() - 273.15);
                G[i][j]      = mc::nrtl_G(T, a[i][j], b[i][j], e[i][j], f[i][j], alpha);
            }
        }
    }
    return G;
}

Var
nrtl_subroutine_G(Var T, double a, double b, double e, double f, double alpha)
{
    return mc::nrtl_G(T, a, b, e, f, alpha);
}

VarType
nrtl_subroutine_Gtau(Var T, VarType tau, VarType G, ParaType a, ParaType b, ParaType c, ParaType d, ParaType e, ParaType f)
{
    VarType Gtau(tau.size(), std::vector<Var>(tau[0].size(), 0.0));
    int it = tau.size();
    int jt = tau[0].size();
    for (int i = 0; i < it; i++) {
        for (int j = 0; j < jt; j++) {
            if (i != j) {
                double alpha = c[i][j] + d[i][j] * (T.num().val() - 273.15);
                Gtau[i][j]   = mc::nrtl_Gtau(T, a[i][j], b[i][j], e[i][j], f[i][j], alpha);
            }
        }
    }
    return Gtau;
}

Var
nrtl_subroutine_Gtau(Var T, double a, double b, double e, double f, double alpha)
{
    return mc::nrtl_Gtau(T, a, b, e, f, alpha);
}

VarType
nrtl_subroutine_Gdtau(Var T, VarType G, ParaType a, ParaType b, ParaType c, ParaType d, ParaType e, ParaType f)
{
    VarType Gdtau(G.size(), std::vector<Var>(G[0].size(), 0.0));
    int it = G.size();
    int jt = G[0].size();
    for (int i = 0; i < it; i++) {
        for (int j = 0; j < jt; j++) {
            if (i != j) {
                double alpha = c[i][j] + d[i][j] * (T.num().val() - 273.15);
                Gdtau[i][j]  = mc::nrtl_Gdtau(T, a[i][j], b[i][j], e[i][j], f[i][j], alpha);
            }
        }
    }
    return Gdtau;
}

Var
nrtl_subroutine_Gdtau(Var T, double a, double b, double e, double f, double alpha)
{
    return mc::nrtl_Gdtau(T, a, b, e, f, alpha);
}

Var
nrtl_subroutine_dGtau(Var T, double a, double b, double e, double f, double alpha)
{
    return mc::nrtl_dGtau(T, a, b, e, f, alpha);
}

}    // namespace maingo