from maingopy import *
import unittest

class TestInstrinsicFunctions(unittest.TestCase):


    def test_FFVar_initialization(self):
        try:
            x = FFVar()
            x = FFVar(1)
            x = FFVar(1.5)
        except:
            self.fail("Initialization of FFVar raised exception unexpectedly")


    def test_basic_operations(self):
        x = FFVar(3.)
        y = FFVar(1.)
        try:
            z = x +y
            z = x + 2.
            z = 2.+y
            z =   +y
            z = x -y
            z = x - 2.
            z = 2.-y
            z =   -y
            z = x *y
            z = x *2.
            z = 2.*y
            z = x /y
            z = x /2.
            z = 2./y
            z = x**2.
            z = x**2
            z = x**y
            z = 2.**x
            x == y
            x != y
            x += y
            x -= y
            x *= y
            x /= y
        except:
            self.fail("Basic operation with FFVar raised exception unexpectedly")


    def test_intrinsic_functions(self):
        x = FFVar(1.)
        y = FFVar(1.)
        try:
            z = inv(x)
            z = sqr(x)
            z = exp(x)
            z = log(x)
            z = xlog(x)
            z = fabsx_times_x(x)
            z = xexpax(x,2.)
            z = arh(x,2.)
            z = vapor_pressure(x,1.,1.,1.,1.,1.,1.,1.,1.)
            z = vapor_pressure(x,2.,1.,1.,1.)
            z = vapor_pressure(x,3.,1.,1.,1.,1.,1.,1.)
            z = vapor_pressure(x,4.,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.)
            z = saturation_temperature(x,2.,1.,1.,1.)
            z = ideal_gas_enthalpy(x,1.,1.,1.,1.,1.,1.,1.)
            z = ideal_gas_enthalpy(x,2.,1.,1.,1.,1.,1.,1.,1.)
            z = ideal_gas_enthalpy(x,3.,1.,1.,1.,1.,1.,1.)
            z = ideal_gas_enthalpy(x,4.,1.,1.,1.,1.,1.,1.,1.)
            z = enthalpy_of_vaporization(x,1.,1.,1.,1.,1.,1.)
            z = enthalpy_of_vaporization(x,2.,1.,1.,1.,1.,1.,1.)
            z = cost_function(x,1.,1.,1.,1.)
            z = sum_div([x,y],[1.,1.,1.])
            z = xlog_sum([x,y],[1.,1.])
            z = nrtl_tau(x,1.,1.,1.,1.)
            z = nrtl_dtau(x,1.,1.,1.)
            z = nrtl_G(x,1.,1.,1.,1.,1.)
            z = nrtl_Gtau(x,1.,1.,1.,1.,1.)
            z = nrtl_Gdtau(x,1.,1.,1.,1.,1.)
            z = nrtl_dGtau(x,1.,1.,1.,1.,1.)
            z = iapws(x,42)
            z = iapws(x,y,11)
            z = p_sat_ethanol_schroeder(x)
            z = rho_vap_sat_ethanol_schroeder(x)
            z = rho_liq_sat_ethanol_schroeder(x)
            z = covariance_function(x,1.)
            z = acquisition_function(x,y,1.,1.)
            z = gaussian_probability_density_function(x)
            z = regnormal(x,1.,1.)
            z = pos(x)
            z = neg(x)
            z = lb_func(x,1.)
            z = ub_func(x,1.)
            z = squash_node(x,0.,1.)
            z = bounding_func(x,0.,1.)
            z = sqrt(x)
            z = fabs(x)
            z = cos(x)
            z = sin(x)
            z = tan(x)
            z = acos(x)
            z = asin(x)
            z = atan(x)
            z = cosh(x)
            z = sinh(x)
            z = tanh(x)
            z = coth(x)
            z = erf(x)
            z = erfc(x)
            z = fstep(x)
            z = bstep(x)
            z = pow(x,2)
            z = pow(x,2.5)
            z = pow(x,y)
            z = pow(2.5,x)
            z = cheb(x,2)
            z = xlogx(x)
            z = xexpy(x,y)
            z = norm2(x,y)
            z = squash(x,0.,1.)
            z = ext_antoine_psat(x,1.,1.,1.,1.,1.,1.,1.)
            z = ext_antoine_psat(x,[1.,1.,1.,1.,1.,1.,1.])
            z = antoine_psat(x,1.,1.,1.)
            z = antoine_psat(x,[1.,1.,1.])
            z = wagner_psat(x,1.,1.,1.,1.,1.,1.)
            z = wagner_psat(x,[1.,1.,1.,1.,1.,1.])
            z = ik_cape_psat(x,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.)
            z = ik_cape_psat(x,[1.,1.,1.,1.,1.,1.,1.,1.,1.,1.])
            z = antoine_tsat(x,1.,1.,1.)
            z = antoine_tsat(x,[1.,1.,1.])
            z = aspen_hig(x,1.,1.,1.,1.,1.,1.,1.)
            z = aspen_hig(x,1.,[1.,1.,1.,1.,1.,1.])
            z = nasa9_hig(x,1.,1.,1.,1.,1.,1.,1.,1.)
            z = nasa9_hig(x,1.,[1.,1.,1.,1.,1.,1.,1.])
            z = dippr107_hig(x,1.,1.,1.,1.,1.,1.)
            z = dippr107_hig(x,1.,[1.,1.,1.,1.,1.])
            z = dippr127_hig(x,1.,1.,1.,1.,1.,1.,1.,1.)
            z = dippr127_hig(x,1.,[1.,1.,1.,1.,1.,1.,1.])
            z = watson_dhvap(x,1.,1.,1.,1.,1.)
            z = watson_dhvap(x,[1.,1.,1.,1.,1.])
            z = dippr106_dhvap(x,1.,1.,1.,1.,1.,1.)
            z = dippr106_dhvap(x,[1.,1.,1.,1.,1.,1.])
            z = nrtl_tau(x,[1.,1.,1.,1.])
            z = nrtl_dtau(x,[1.,1.,1.])
            z = nrtl_g(x,1.,1.,1.,1.,1.)
            z = nrtl_g(x,[1.,1.,1.,1.,1.])
            z = nrtl_gtau(x,1.,1.,1.,1.,1.)
            z = nrtl_gtau(x,[1.,1.,1.,1.,1.])
            z = nrtl_gdtau(x,1.,1.,1.,1.,1.)
            z = nrtl_gdtau(x,[1.,1.,1.,1.,1.])
            z = nrtl_dgtau(x,1.,1.,1.,1.,1.)
            z = nrtl_dgtau(x,[1.,1.,1.,1.,1.])
            z = schroeder_ethanol_p(x)
            z = schroeder_ethanol_rhovap(x)
            z = schroeder_ethanol_rholiq(x)
            z = cost_turton(x,1.,1.,1.)
            z = cost_turton(x,[1.,1.,1.])
            z = covar_matern_1(x)
            z = covar_matern_3(x)
            z = covar_matern_5(x)
            z = covar_sqrexp(x)
            z = af_lcb(x,y,1.)
            z = af_ei(x,y,1.)
            z = af_pi(x,y,1.)
            z = gpdf(x)

            # Test implicit convertion of int and double to FFVar
            z = pos(1)
            z = pos(1.5)
        except:
            self.fail("Intrinsic function with FFVar raised exception unexpectedly")


if __name__ == '__main__':
    unittest.main()