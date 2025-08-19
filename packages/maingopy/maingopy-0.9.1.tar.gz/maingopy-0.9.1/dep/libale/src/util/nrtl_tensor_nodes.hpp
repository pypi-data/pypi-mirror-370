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

#pragma once

double operator()(nrtl_gamma_tensor2_node* node) {
    int _ncomp = (int)dispatch(node->get_child<0>()).shape()[1];

    if (_ncomp != (int)dispatch(node->get_child<5>()).shape()[1]) {
        throw std::invalid_argument("Dimension of composition std::vector inconsistent with size of NRTL binary interaction parameter matrix.");
    }

    std::vector<double> x(_ncomp, 0.0);
    double t{ 0.0 };
    double p{ 0.0 };
    int k{ 0 };
    std::vector<std::vector<double>> a(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> b(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> c(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> d(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> e(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> f(_ncomp, std::vector<double>(_ncomp, 0.0));

    int phase{ 0 };
    phase = dispatch(node->get_child<3>()) - 1;
    for (int i = 0; i < _ncomp; i++) {
        x[i] = dispatch(node->get_child<0>())[(size_t)phase][(size_t)i];
    }
    t = dispatch(node->get_child<1>());
    p = dispatch(node->get_child<2>());
    k = dispatch(node->get_child<4>()) - 1;
    for (int i = 0; i < _ncomp; i++) {
        for (int j = 0; j < _ncomp; j++) {
            a[i][j] = dispatch(node->get_child<5>())[(size_t)0][(size_t)i][(size_t)j];
            b[i][j] = dispatch(node->get_child<5>())[(size_t)1][(size_t)i][(size_t)j];
            c[i][j] = dispatch(node->get_child<5>())[(size_t)2][(size_t)i][(size_t)j];
            d[i][j] = dispatch(node->get_child<5>())[(size_t)3][(size_t)i][(size_t)j];
            e[i][j] = dispatch(node->get_child<5>())[(size_t)4][(size_t)i][(size_t)j];
            f[i][j] = dispatch(node->get_child<5>())[(size_t)5][(size_t)i][(size_t)j];
        }
    }

    //Tau
    std::vector<std::vector<double>>tau(_ncomp, std::vector<double>(_ncomp, 0.0));
    tau = nrtl_subroutine_tau(t, a, b, e, f);

    //G
    std::vector<std::vector<double>>G(_ncomp, std::vector<double>(_ncomp, 1.0));
    G = nrtl_subroutine_G(t, tau, c, d);

    //Gtau
    std::vector<std::vector<double>>Gtau(_ncomp, std::vector<double>(_ncomp, 0.0));
    Gtau = nrtl_subroutine_Gtau(G, tau);

    //Gamma
    double gamma = nrtl_subroutine_gamma(x, tau, G, Gtau, k);
    return gamma;

}

double operator()(nrtl_gamma_tensor3_node* node) {
    int _ncomp = (int)dispatch(node->get_child<0>()).shape()[2];

    if (_ncomp != (int)dispatch(node->get_child<6>()).shape()[1]) {
        throw std::invalid_argument("Dimension of composition std::vector inconsistent with size of NRTL binary interaction parameter matrix.");
    }

    std::vector<double> x(_ncomp, 0.0);
    double t{ 0.0 };
    double p{ 0.0 };
    int k{ 0 };
    std::vector<std::vector<double>> a(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> b(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> c(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> d(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> e(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> f(_ncomp, std::vector<double>(_ncomp, 0.0));

    int phase{ 0 };
    int stage{ 0 };
    stage = dispatch(node->get_child<3>()) - 1;
    phase = dispatch(node->get_child<4>()) - 1;
    for (int i = 0; i < _ncomp; i++) {
        x[i] = dispatch(node->get_child<0>())[(size_t)stage][(size_t)phase][(size_t)i];
    }
    t = dispatch(node->get_child<1>());
    p = dispatch(node->get_child<2>());
    k = dispatch(node->get_child<5>()) - 1;
    for (int i = 0; i < _ncomp; i++) {
        for (int j = 0; j < _ncomp; j++) {
            a[i][j] = dispatch(node->get_child<6>())[(size_t)0][(size_t)i][(size_t)j];
            b[i][j] = dispatch(node->get_child<6>())[(size_t)1][(size_t)i][(size_t)j];
            c[i][j] = dispatch(node->get_child<6>())[(size_t)2][(size_t)i][(size_t)j];
            d[i][j] = dispatch(node->get_child<6>())[(size_t)3][(size_t)i][(size_t)j];
            e[i][j] = dispatch(node->get_child<6>())[(size_t)4][(size_t)i][(size_t)j];
            f[i][j] = dispatch(node->get_child<6>())[(size_t)5][(size_t)i][(size_t)j];
        }
    }

    //Tau
    std::vector<std::vector<double>>tau(_ncomp, std::vector<double>(_ncomp, 0.0));
    tau = nrtl_subroutine_tau(t, a, b, e, f);

    //G
    std::vector<std::vector<double>>G(_ncomp, std::vector<double>(_ncomp, 1.0));
    G = nrtl_subroutine_G(t, tau, c, d);

    //Gtau
    std::vector<std::vector<double>>Gtau(_ncomp, std::vector<double>(_ncomp, 0.0));
    Gtau = nrtl_subroutine_Gtau(G, tau);

    //Gamma
    double gamma = nrtl_subroutine_gamma(x, tau, G, Gtau, k);
    return gamma;

}

double operator()(nrtl_lngamma_tensor2_node* node) {
    int _ncomp = (int)dispatch(node->get_child<0>()).shape()[1];

    if (_ncomp != (int)dispatch(node->get_child<5>()).shape()[1]) {
        throw std::invalid_argument("Dimension of composition std::vector inconsistent with size of NRTL binary interaction parameter matrix.");
    }

    std::vector<double> x(_ncomp, 0.0);
    double t{ 0.0 };
    double p{ 0.0 };
    int k{ 0 };
    std::vector<std::vector<double>> a(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> b(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> c(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> d(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> e(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> f(_ncomp, std::vector<double>(_ncomp, 0.0));

    int phase{ 0 };
    phase = dispatch(node->get_child<3>()) - 1;
    for (int i = 0; i < _ncomp; i++) {
        x[i] = dispatch(node->get_child<0>())[(size_t)phase][(size_t)i];
    }
    t = dispatch(node->get_child<1>());
    p = dispatch(node->get_child<2>());
    k = dispatch(node->get_child<4>()) - 1;
    for (int i = 0; i < _ncomp; i++) {
        for (int j = 0; j < _ncomp; j++) {
            a[i][j] = dispatch(node->get_child<5>())[(size_t)0][(size_t)i][(size_t)j];
            b[i][j] = dispatch(node->get_child<5>())[(size_t)1][(size_t)i][(size_t)j];
            c[i][j] = dispatch(node->get_child<5>())[(size_t)2][(size_t)i][(size_t)j];
            d[i][j] = dispatch(node->get_child<5>())[(size_t)3][(size_t)i][(size_t)j];
            e[i][j] = dispatch(node->get_child<5>())[(size_t)4][(size_t)i][(size_t)j];
            f[i][j] = dispatch(node->get_child<5>())[(size_t)5][(size_t)i][(size_t)j];
        }
    }

    //Tau
    std::vector<std::vector<double>>tau(_ncomp, std::vector<double>(_ncomp, 0.0));
    tau = nrtl_subroutine_tau(t, a, b, e, f);

    //G
    std::vector<std::vector<double>>G(_ncomp, std::vector<double>(_ncomp, 1.0));
    G = nrtl_subroutine_G(t, tau, c, d);

    //Gtau
    std::vector<std::vector<double>>Gtau(_ncomp, std::vector<double>(_ncomp, 0.0));
    Gtau = nrtl_subroutine_Gtau(G, tau);

    //Gamma
    double gamma = nrtl_subroutine_gamma(x, tau, G, Gtau, k);
    return std::log(gamma);

}

double operator()(nrtl_lngamma_tensor3_node* node) {
    int _ncomp = (int)dispatch(node->get_child<0>()).shape()[2];

    if (_ncomp != (int)dispatch(node->get_child<6>()).shape()[1]) {
        throw std::invalid_argument("Dimension of composition std::vector inconsistent with size of NRTL binary interaction parameter matrix.");
    }

    std::vector<double> x(_ncomp, 0.0);
    double t{ 0.0 };
    double p{ 0.0 };
    int k{ 0 };
    std::vector<std::vector<double>> a(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> b(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> c(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> d(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> e(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> f(_ncomp, std::vector<double>(_ncomp, 0.0));

    int phase{ 0 };
    int stage{ 0 };
    stage = dispatch(node->get_child<3>()) - 1;
    phase = dispatch(node->get_child<4>()) - 1;
    for (int i = 0; i < _ncomp; i++) {
        x[i] = dispatch(node->get_child<0>())[(size_t)stage][(size_t)phase][(size_t)i];
    }
    t = dispatch(node->get_child<1>());
    p = dispatch(node->get_child<2>());
    k = dispatch(node->get_child<5>()) - 1;
    for (int i = 0; i < _ncomp; i++) {
        for (int j = 0; j < _ncomp; j++) {
            a[i][j] = dispatch(node->get_child<6>())[(size_t)0][(size_t)i][(size_t)j];
            b[i][j] = dispatch(node->get_child<6>())[(size_t)1][(size_t)i][(size_t)j];
            c[i][j] = dispatch(node->get_child<6>())[(size_t)2][(size_t)i][(size_t)j];
            d[i][j] = dispatch(node->get_child<6>())[(size_t)3][(size_t)i][(size_t)j];
            e[i][j] = dispatch(node->get_child<6>())[(size_t)4][(size_t)i][(size_t)j];
            f[i][j] = dispatch(node->get_child<6>())[(size_t)5][(size_t)i][(size_t)j];
        }
    }

    //Tau
    std::vector<std::vector<double>>tau(_ncomp, std::vector<double>(_ncomp, 0.0));
    tau = nrtl_subroutine_tau(t, a, b, e, f);

    //G
    std::vector<std::vector<double>>G(_ncomp, std::vector<double>(_ncomp, 1.0));
    G = nrtl_subroutine_G(t, tau, c, d);

    //Gtau
    std::vector<std::vector<double>>Gtau(_ncomp, std::vector<double>(_ncomp, 0.0));
    Gtau = nrtl_subroutine_Gtau(G, tau);

    //Gamma
    double gamma = nrtl_subroutine_gamma(x, tau, G, Gtau, k);
    return std::log(gamma);

}

double operator()(nrtl_gamma_rs_node* node) {
    int _ncomp = 3;
    std::vector<double> x(_ncomp, 0.0);
    double t{ 0.0 };
    double p{ 0.0 };
    int k{ 0 };
    std::vector<std::vector<double>> a(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> b(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> c(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> d(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> e(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> f(_ncomp, std::vector<double>(_ncomp, 0.0));

    x[0] = dispatch(node->get_child<0>());
    x[1] = dispatch(node->get_child<1>());
    x[2] = dispatch(node->get_child<2>());

    t = dispatch(node->get_child<3>());
    p = dispatch(node->get_child<4>());
    k = dispatch(node->get_child<5>()) - 1;
    for (int i = 0; i < _ncomp; i++) {
        for (int j = 0; j < _ncomp; j++) {
            a[i][j] = dispatch(node->get_child<6>())[(size_t)0][(size_t)i][(size_t)j];
            b[i][j] = dispatch(node->get_child<6>())[(size_t)1][(size_t)i][(size_t)j];
            c[i][j] = dispatch(node->get_child<6>())[(size_t)2][(size_t)i][(size_t)j];
            d[i][j] = dispatch(node->get_child<6>())[(size_t)3][(size_t)i][(size_t)j];
            e[i][j] = dispatch(node->get_child<6>())[(size_t)4][(size_t)i][(size_t)j];
            f[i][j] = dispatch(node->get_child<6>())[(size_t)5][(size_t)i][(size_t)j];
        }
    }
    //Tau
    std::vector<std::vector<double>>tau(_ncomp, std::vector<double>(_ncomp, 0.0));
    tau = nrtl_subroutine_tau(t, a, b, e, f);

    //G
    std::vector<std::vector<double>>G(_ncomp, std::vector<double>(_ncomp, 1.0));
    G = nrtl_subroutine_G(t, tau, c, d);

    //Gtau
    std::vector<std::vector<double>>Gtau(_ncomp, std::vector<double>(_ncomp, 0.0));
    Gtau = nrtl_subroutine_Gtau(G, tau);

    //Gamma
    double gamma = nrtl_subroutine_gamma(x, tau, G, Gtau, k);
    return gamma;

}

double operator()(nrtl_ge_rs_node* node) {
    int _ncomp = 3;


    std::vector<double> x(_ncomp, 0.0);
    double t{ 0.0 };
    double p{ 0.0 };
    std::vector<std::vector<double>> a(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> b(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> c(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> d(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> e(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> f(_ncomp, std::vector<double>(_ncomp, 0.0));
    int phase{ 0 };

    x[0] = dispatch(node->get_child<0>());
    x[1] = dispatch(node->get_child<1>());
    x[2] = dispatch(node->get_child<2>());
    t = dispatch(node->get_child<3>());
    p = dispatch(node->get_child<4>());
    for (int i = 0; i < _ncomp; i++) {
        for (int j = 0; j < _ncomp; j++) {
            a[i][j] = dispatch(node->get_child<5>())[(size_t)0][(size_t)i][(size_t)j];
            b[i][j] = dispatch(node->get_child<5>())[(size_t)1][(size_t)i][(size_t)j];
            c[i][j] = dispatch(node->get_child<5>())[(size_t)2][(size_t)i][(size_t)j];
            d[i][j] = dispatch(node->get_child<5>())[(size_t)3][(size_t)i][(size_t)j];
            e[i][j] = dispatch(node->get_child<5>())[(size_t)4][(size_t)i][(size_t)j];
            f[i][j] = dispatch(node->get_child<5>())[(size_t)5][(size_t)i][(size_t)j];
        }
    }

    //Tau
    std::vector<std::vector<double>>tau(_ncomp, std::vector<double>(_ncomp, 0.0));
    tau = nrtl_subroutine_tau(t, a, b, e, f);

    //G
    std::vector<std::vector<double>>G(_ncomp, std::vector<double>(_ncomp, 1.0));
    G = nrtl_subroutine_G(t, tau, c, d);

    //Gtau
    std::vector<std::vector<double>>Gtau(_ncomp, std::vector<double>(_ncomp, 0.0));
    Gtau = nrtl_subroutine_Gtau(G, tau);

    //GE
    double gE = nrtl_subroutine_gE(x, G, Gtau);
    return gE;
}

double operator()(nrtl_ge_tensor2_node* node) {
    int _ncomp = (int)dispatch(node->get_child<0>()).shape()[1];
    if (_ncomp != (int)dispatch(node->get_child<4>()).shape()[1]) {
        throw std::invalid_argument("Dimension of composition vector inconsistent with size of NRTL binary interaction parameter matrix.");
    }

    std::vector<double> x(_ncomp, 0.0);
    double t{ 0.0 };
    double p{ 0.0 };
    std::vector<std::vector<double>> a(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> b(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> c(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> d(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> e(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> f(_ncomp, std::vector<double>(_ncomp, 0.0));
    int phase{ 0 };
    phase = dispatch(node->get_child<3>()) - 1;
    for (int i = 0; i < _ncomp; i++) {
        x[i] = dispatch(node->get_child<0>())[(size_t)phase][(size_t)i];
    }
    t = dispatch(node->get_child<1>());
    p = dispatch(node->get_child<2>());
    for (int i = 0; i < _ncomp; i++) {
        for (int j = 0; j < _ncomp; j++) {
            a[i][j] = dispatch(node->get_child<4>())[(size_t)0][(size_t)i][(size_t)j];
            b[i][j] = dispatch(node->get_child<4>())[(size_t)1][(size_t)i][(size_t)j];
            c[i][j] = dispatch(node->get_child<4>())[(size_t)2][(size_t)i][(size_t)j];
            d[i][j] = dispatch(node->get_child<4>())[(size_t)3][(size_t)i][(size_t)j];
            e[i][j] = dispatch(node->get_child<4>())[(size_t)4][(size_t)i][(size_t)j];
            f[i][j] = dispatch(node->get_child<4>())[(size_t)5][(size_t)i][(size_t)j];
        }
    }


    //Tau
    std::vector<std::vector<double>>tau(_ncomp, std::vector<double>(_ncomp, 0.0));
    tau = nrtl_subroutine_tau(t, a, b, e, f);

    //G
    std::vector<std::vector<double>>G(_ncomp, std::vector<double>(_ncomp, 1.0));
    G = nrtl_subroutine_G(t, tau, c, d);

    //Gtau
    std::vector<std::vector<double>>Gtau(_ncomp, std::vector<double>(_ncomp, 0.0));
    Gtau = nrtl_subroutine_Gtau(G, tau);

    //GE
    double gE = nrtl_subroutine_gE(x, G, Gtau);
    return gE;
}

double operator()(nrtl_he_rs_node* node) {
    int _ncomp = 3;


    std::vector<double> x(_ncomp, 0.0);
    double t{ 0.0 };
    double p{ 0.0 };
    std::vector<std::vector<double>> a(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> b(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> c(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> d(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> e(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> f(_ncomp, std::vector<double>(_ncomp, 0.0));
    int phase{ 0 };

    x[0] = dispatch(node->get_child<0>());
    x[1] = dispatch(node->get_child<1>());
    x[2] = dispatch(node->get_child<2>());
    t = dispatch(node->get_child<3>());
    p = dispatch(node->get_child<4>());
    for (int i = 0; i < _ncomp; i++) {
        for (int j = 0; j < _ncomp; j++) {
            a[i][j] = dispatch(node->get_child<5>())[(size_t)0][(size_t)i][(size_t)j];
            b[i][j] = dispatch(node->get_child<5>())[(size_t)1][(size_t)i][(size_t)j];
            c[i][j] = dispatch(node->get_child<5>())[(size_t)2][(size_t)i][(size_t)j];
            d[i][j] = dispatch(node->get_child<5>())[(size_t)3][(size_t)i][(size_t)j];
            e[i][j] = dispatch(node->get_child<5>())[(size_t)4][(size_t)i][(size_t)j];
            f[i][j] = dispatch(node->get_child<5>())[(size_t)5][(size_t)i][(size_t)j];
        }
    }


    //Tau
    std::vector<std::vector<double>>tau(_ncomp, std::vector<double>(_ncomp, 0.0));
    tau = nrtl_subroutine_tau(t, a, b, e, f);

    //G
    std::vector<std::vector<double>>G(_ncomp, std::vector<double>(_ncomp, 1.0));
    G = nrtl_subroutine_G(t, tau, c, d);

    //Gtau
    std::vector<std::vector<double>>Gtau(_ncomp, std::vector<double>(_ncomp, 0.0));
    Gtau = nrtl_subroutine_Gtau(G, tau);

    //HE
    double HE = nrtl_subroutine_HE(t, x, tau, G, Gtau, c);
    return HE;
}

double operator()(nrtl_he_tensor2_node* node) {
    int _ncomp = (int)dispatch(node->get_child<0>()).shape()[1];
    if (_ncomp != (int)dispatch(node->get_child<4>()).shape()[1]) {
        throw std::invalid_argument("Dimension of composition vector inconsistent with size of NRTL binary interaction parameter matrix.");
    }

    std::vector<double> x(_ncomp, 0.0);
    double t{ 0.0 };
    double p{ 0.0 };
    std::vector<std::vector<double>> a(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> b(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> c(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> d(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> e(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> f(_ncomp, std::vector<double>(_ncomp, 0.0));
    int phase{ 0 };
    phase = dispatch(node->get_child<3>()) - 1;
    for (int i = 0; i < _ncomp; i++) {
        x[i] = dispatch(node->get_child<0>())[(size_t)phase][(size_t)i];
    }
    t = dispatch(node->get_child<1>());
    p = dispatch(node->get_child<2>());
    for (int i = 0; i < _ncomp; i++) {
        for (int j = 0; j < _ncomp; j++) {
            a[i][j] = dispatch(node->get_child<4>())[(size_t)0][(size_t)i][(size_t)j];
            b[i][j] = dispatch(node->get_child<4>())[(size_t)1][(size_t)i][(size_t)j];
            c[i][j] = dispatch(node->get_child<4>())[(size_t)2][(size_t)i][(size_t)j];
            d[i][j] = dispatch(node->get_child<4>())[(size_t)3][(size_t)i][(size_t)j];
            e[i][j] = dispatch(node->get_child<4>())[(size_t)4][(size_t)i][(size_t)j];
            f[i][j] = dispatch(node->get_child<4>())[(size_t)5][(size_t)i][(size_t)j];
        }
    }


    //Tau
    std::vector<std::vector<double>>tau(_ncomp, std::vector<double>(_ncomp, 0.0));
    tau = nrtl_subroutine_tau(t, a, b, e, f);

    //G
    std::vector<std::vector<double>>G(_ncomp, std::vector<double>(_ncomp, 1.0));
    G = nrtl_subroutine_G(t, tau, c, d);

    //Gtau
    std::vector<std::vector<double>>Gtau(_ncomp, std::vector<double>(_ncomp, 0.0));
    Gtau = nrtl_subroutine_Gtau(G, tau);

    //HE
    double HE = nrtl_subroutine_HE(t, x, tau, G, Gtau, c);
    return HE;
}

double operator()(nrtl_ge_tensor3_node* node) {
    int _ncomp = (int)dispatch(node->get_child<0>()).shape()[1];
    if (_ncomp != (int)dispatch(node->get_child<5>()).shape()[1]) {
        throw std::invalid_argument("Dimension of composition vector inconsistent with size of NRTL binary interaction parameter matrix.");
    }

    std::vector<double> x(_ncomp, 0.0);
    double t{ 0.0 };
    double p{ 0.0 };
    std::vector<std::vector<double>> a(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> b(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> c(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> d(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> e(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> f(_ncomp, std::vector<double>(_ncomp, 0.0));
    int phase{ 0 };
    int stage{ 0 };
    stage = dispatch(node->get_child<3>()) - 1;
    phase = dispatch(node->get_child<4>()) - 1;
    for (int i = 0; i < _ncomp; i++) {
        x[i] = dispatch(node->get_child<0>())[(size_t)stage][(size_t)phase][(size_t)i];
    }
    t = dispatch(node->get_child<1>());
    p = dispatch(node->get_child<2>());
    for (int i = 0; i < _ncomp; i++) {
        for (int j = 0; j < _ncomp; j++) {
            a[i][j] = dispatch(node->get_child<5>())[(size_t)0][(size_t)i][(size_t)j];
            b[i][j] = dispatch(node->get_child<5>())[(size_t)1][(size_t)i][(size_t)j];
            c[i][j] = dispatch(node->get_child<5>())[(size_t)2][(size_t)i][(size_t)j];
            d[i][j] = dispatch(node->get_child<5>())[(size_t)3][(size_t)i][(size_t)j];
            e[i][j] = dispatch(node->get_child<5>())[(size_t)4][(size_t)i][(size_t)j];
            f[i][j] = dispatch(node->get_child<5>())[(size_t)5][(size_t)i][(size_t)j];
        }
    }

    //Tau
    std::vector<std::vector<double>>tau(_ncomp, std::vector<double>(_ncomp, 0.0));
    tau = nrtl_subroutine_tau(t, a, b, e, f);

    //G
    std::vector<std::vector<double>>G(_ncomp, std::vector<double>(_ncomp, 1.0));
    G = nrtl_subroutine_G(t, tau, c, d);

    //Gtau
    std::vector<std::vector<double>>Gtau(_ncomp, std::vector<double>(_ncomp, 0.0));
    Gtau = nrtl_subroutine_Gtau(G, tau);

    //GE
    double gE = nrtl_subroutine_gE(x, G, Gtau);
    return gE;
}

double operator()(nrtl_he_tensor3_node* node) {
    int _ncomp = (int)dispatch(node->get_child<0>()).shape()[1];
    if (_ncomp != (int)dispatch(node->get_child<5>()).shape()[1]) {
        throw std::invalid_argument("Dimension of composition vector inconsistent with size of NRTL binary interaction parameter matrix.");
    }

    std::vector<double> x(_ncomp, 0.0);
    double t{ 0.0 };
    double p{ 0.0 };
    std::vector<std::vector<double>> a(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> b(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> c(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> d(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> e(_ncomp, std::vector<double>(_ncomp, 0.0));
    std::vector<std::vector<double>> f(_ncomp, std::vector<double>(_ncomp, 0.0));
    int phase{ 0 };
    int stage{ 0 };
    stage = dispatch(node->get_child<3>()) - 1;
    phase = dispatch(node->get_child<4>()) - 1;
    for (int i = 0; i < _ncomp; i++) {
        x[i] = dispatch(node->get_child<0>())[(size_t)stage][(size_t)phase][(size_t)i];
    }
    t = dispatch(node->get_child<1>());
    p = dispatch(node->get_child<2>());
    for (int i = 0; i < _ncomp; i++) {
        for (int j = 0; j < _ncomp; j++) {
            a[i][j] = dispatch(node->get_child<5>())[(size_t)0][(size_t)i][(size_t)j];
            b[i][j] = dispatch(node->get_child<5>())[(size_t)1][(size_t)i][(size_t)j];
            c[i][j] = dispatch(node->get_child<5>())[(size_t)2][(size_t)i][(size_t)j];
            d[i][j] = dispatch(node->get_child<5>())[(size_t)3][(size_t)i][(size_t)j];
            e[i][j] = dispatch(node->get_child<5>())[(size_t)4][(size_t)i][(size_t)j];
            f[i][j] = dispatch(node->get_child<5>())[(size_t)5][(size_t)i][(size_t)j];
        }
    }

    //Tau
    std::vector<std::vector<double>>tau(_ncomp, std::vector<double>(_ncomp, 0.0));
    tau = nrtl_subroutine_tau(t, a, b, e, f);

    //G
    std::vector<std::vector<double>>G(_ncomp, std::vector<double>(_ncomp, 1.0));
    G = nrtl_subroutine_G(t, tau, c, d);

    //Gtau
    std::vector<std::vector<double>>Gtau(_ncomp, std::vector<double>(_ncomp, 0.0));
    Gtau = nrtl_subroutine_Gtau(G, tau);

    //HE
    double HE = nrtl_subroutine_HE(t, x, tau, G, Gtau, c);
    return HE;
}