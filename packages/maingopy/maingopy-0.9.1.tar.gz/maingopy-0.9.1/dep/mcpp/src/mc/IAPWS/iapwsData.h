/**
 * @file iapwsData.h
 *
 * @brief File containing data for the IAPWS-IF97 model.
 *
 * Original model: Wagner, W.; Cooper, J. R.; Dittmann, A.; Kijima, J.; Kretzschmar, H.-J.; Kruse, A.; Mareš, R.; Oguchi, K.; Sato, H.; Stocker, I.; Sifner, O.; Takaishi, Y.; Tanishita, I.; Trubenbach, J. & Willkommen, T.:
 *                 The IAPWS Industrial Formulation 1997 for the Thermodynamic Properties of Water and Steam. Journal of Engineering for Gas Turbines and Power -- Transactions of the ASME, 2000, 122, 150-182.
 *
 * Revised model used for this implementation: Revised Release on the IAPWS Industrial Formulation 1997 for the Thermodynamic Properties of Water and Steam.
 *											   The International Association for the Properties of Water and Steam, Technical Report IAPWS R7-97(2012), 2012. http://www.iapws.org/relguide/IF97-Rev.html.
 *
 * ==============================================================================\n
 * © Aachener Verfahrenstechnik-Systemverfahrenstechnik, RWTH Aachen University  \n
 * ==============================================================================\n
 *
 * @author Dominik Bongartz, Jaromil Najman, David Zanger, Alexander Mitsos
 * @date 15.08.2019
 *
 */

#pragma once

#include <vector>


namespace iapws_if97 {


	/**
	 * @struct DataTriple
	 * @brief Auxiliary struct for storing data of the IAPWS-IF97 model.
	*/
	template <typename U, typename V, typename W>
	struct DataTriple {
		U I;		//!< Exponent for pressure-related expressions
		V J;		//!< Exponent for temperature-related expressions
		W n;		//!< Coefficient for terms
	};


	namespace constants {

		/**
		* @name Constants for water according to the IAPWS-IF97 model.
		*/
		/**@{*/
			constexpr double R = 0.461526;		//!< Specific gas constant of water in kJ/(kg*K)
			constexpr double Tc = 647.096;		//!< Critical temperature of water in K
			constexpr double pc = 22.064;		//!< Critical pressure of water in MPa
			constexpr double vc = 322.;			//!< Critical specific volume of water in kg/(m^3)
			constexpr double Tt = 273.16;		//!< Triple point temperature of water in K
			constexpr double pt = 611.657e-6;	//!< Triple point pressure of water in MPa
		/**@}*/

	}	// end namespace constants


	namespace bounds {

		/**
		* @name Bounds of the IAPWS-IF97 model.
		*/
		/**@{*/
			constexpr double Tmin = 273.15;			//!< Minimum temperature in K for which (a suitable part of this implementation of) the IAPWS-IF97 model is valid
			constexpr double Tmax = 1073.15;		//!< Minimum temperature in K for which (a suitable part of this implementation of) the IAPWS-IF97 model is valid
			constexpr double pmin = 611.2127e-6;	//!< Minimum pressure in MPa for which (a suitable part of this implementation of) the IAPWS-IF97 model is valid
			constexpr double pmax = 100;		//!< Minimum pressure in MPa for which (a suitable part of this implementation of) the IAPWS-IF97 model is valid
		/**@}*/

	}	// end namespace constants


	namespace region1 {


		namespace data {


			/**
			* @name Data used within region 1.
			*/
			/**@{*/
				// Bounds (all valid on the actual domain of region 1 (i.e., host set without the part cut off by the vapor pressure curve))
				constexpr double Tmin = 273.15;									//!< Lower bound on temperature in K (by definition)
				constexpr double Tmax = 623.15;									//!< Upper bound on temperature in K (by definition)
				constexpr double pmin = 611.2127e-6;							//!< Lower bound on pressure in MPa (vapor pressure at 273.15 K)
				constexpr double pmax = 100.;									//!< Upper bound on pressure in MPa (by definition)
				constexpr double hmin = -0.04158782996819355;					//!< Lower bound on enthalpy in kJ/kg (determined through optimization in MAiNGO)
				constexpr double hmax = 1671.023259642434;						//!< Upper bound on enthalpy in kJ/kg (determined through optimization in MAiNGO)
				constexpr double smin = -0.008582287105429742;					//!< Lower bound on entropy in kJ/(kg*K) (determined through optimization in MAiNGO)
				constexpr double smax = 3.778281341700463;						//!< Upper bound on entropy in kJ/(kg*K) (determined through optimization in MAiNGO)

				// Reference values
				constexpr double Tstar = 1386.;									//!< Reference temperature in K
				constexpr double pstar = 16.53;									//!< Reference pressure in MPa
				constexpr double TstarBack = 1.;								//!< Reference temperature for backward equations in K
				constexpr double pstarBack = 1.;								//!< Reference pressure for backward equations in MPa
				constexpr double hstarBack = 2500.;								//!< Reference enthalpy for backward equations in kJ/kg
				constexpr double sstarBack = 1.;								//!< Reference entropy for backward equations in kJ/(kg*K)

				// Parameters for actual equations
				const std::vector< DataTriple<int,int,double> > parBasic = {
					{0,-2,0.14632971213167}
					,{0,-1,-0.84548187169114}
					,{0,0,-0.37563603672040E1}
					,{0,1,0.33855169168385E1}
					,{0,2,-0.95791963387872}
					,{0,3,0.15772038513228}
					,{0,4,-0.16616417199501E-1}
					,{0,5,0.81214629983568E-3}
					,{1,-9,0.28319080123804E-3}
					,{1,-7,-0.60706301565874E-3}
					,{1,-1,-0.18990068218419E-1}
					,{1,0,-0.32529748770505E-1}
					,{1,1,-0.21841717175414E-1}
					,{1,3,-0.52838357969930E-4}
					,{2,-3,-0.47184321073267E-3}
					,{2,0,-0.30001780793026E-3}
					,{2,1,0.47661393906987E-4}
					,{2,3,-0.44141845330846E-5}
					,{2,17,-0.72694996297594E-15}
					,{3,-4,-0.31679644845054E-4}
					,{3,0,-0.28270797985312E-5}
					,{3,6,-0.85205128120103E-9}
					,{4,-5,-0.22425281908000E-5}
					,{4,-2,-0.65171222895601E-6}
					,{4,10,-0.14341729937924E-12}
					,{5,-8,-0.40516996860117E-6}
					,{8,-11,-0.12734301741641E-8}
					,{8,-6,-0.17424871230634E-9}
					,{21,-29,-0.68762131295531E-18}
					,{23,-31,0.14478307828521E-19}
					,{29,-38,0.26335781662795E-22}
					,{30,-39,-0.11947622640071E-22}
					,{31,-40,0.18228094581404E-23}
					,{32,-41,-0.93537087292458E-25}
				};		//!< Vector holding the exponents and coefficients for the basic equation of region 1
				const std::vector< DataTriple<int,int,double> > parBackwardTph = {
					{0,0,-0.23872489924521E3}
					,{0,1,0.40421188637945E3}
					,{0,2,0.11349746881718E3}
					,{0,6,-0.58457616048039E1}
					,{0,22,-0.15285482413140E-3}
					,{0,32,-0.10866707695377E-5}
					,{1,0,-0.13391744872602E2}
					,{1,1,0.43211039183559E2}
					,{1,2,-0.54010067170506E2}
					,{1,3,0.30535892203916E2}
					,{1,4,-0.65964749423638E1}
					,{1,10,0.93965400878363E-2}
					,{1,32,0.11573647505340E-6}
					,{2,10,-0.25858641282073E-4}
					,{2,32,-0.40644363084799E-8}
					,{3,10,0.66456186191635E-7}
					,{3,32,0.80670734103027E-10}
					,{4,32,-0.93477771213947E-12}
					,{5,32,0.58265442020601E-14}
					,{6,32,-0.15020185953503E-16}
				};		//!< Vector holding the exponents and coefficients for the backward equation T(p,h) of region 1
				const std::vector<DataTriple<int,int,double> > parBackwardTps = {
					{0,0,0.17478268058307E3}
					,{0,1,0.34806930892873E2}
					,{0,2,0.65292584978455E1}
					,{0,3,0.33039981775489}
					,{0,11,-0.19281382923196E-6}
					,{0,31,-0.24909197244573E-22}
					,{1,0,-0.26107636489332}
					,{1,1,0.22592965981586}
					,{1,2,-0.64256463395226E-1}
					,{1,3,0.78876289270526E-2}
					,{1,12,0.35672110607366E-9}
					,{1,31,0.17332496994895E-23}
					,{2,0,0.56608900654837E-3}
					,{2,1,-0.32635483139717E-3}
					,{2,2,0.44778286690632E-4}
					,{2,9,-0.51322156908507E-9}
					,{2,31,-0.42522657042207E-25}
					,{3,10,0.26400441360689E-12}
					,{3,32,0.78124600459723E-28}
					,{4,32,-0.30732199903668E-30}
				};		//!< Vector holding the exponents and coefficients for the backward equation T(p,s) of region 1

				// Auxiliary data for the extension and relaxations of h(p,T)
				constexpr double TmaxDhdpGt0 = 510;								//!< Upper bound on temperature in K for which dh/dp (and the derivative of the comp.-conv. alphaBB underestimator of h(p,T)) is guaranteed to be >=0 (determined through optimization in MAiNGO + visual inspection for alphaBB)
				constexpr double TminDhdpLt0 = 613.0136777139426;				//!< Lower bound on temperature in K for which dh/dp is guaranteed to be <=0 (determined through optimization in MAiNGO)
				constexpr double hminAtTmaxDhdpGt0 = 1022.627851896676;			//!< Lower bound on enthalpy in kJ/kg at TmaxDhdpGt0 (determined through optimization in MAiNGO)
				constexpr double hmaxAtTminDhpLt0 = 1652.411806428461;			//!< Upper bound on enthalpy in kJ/kg at TminDhdpLt0 (determined through optimization in MAiNGO)
				constexpr double alphaD2hdT2 = 0.5*0.0035870609;				//!< Alpha parameter used for making h(p,T) componentwise concave w.r.t. T (only needed if T<314K and p<26MPa)
				constexpr double alphaD2hdp2 = 0.5*0.0015608706;				//!< Alpha parameter used for making h(p,T) componentwise concave w.r.t. p (only needed if T<369K and (T<352K or p>16.5292MPa))
				constexpr double TminD2hdp2Gt0 = 369.1178741232919;				//!< Lower bound on temperature in K for which d2h/dp2 is guaranteed to be >= 0 (determined through optimization in MAiNGO)
				constexpr double TminD2hdp2Gt0AtPminB23 = 352.5846514094441; 	//!< Lower bound on temperature in K for which d2h/dp2 is guaranteed to be >= 0 whenever p<=pminB23 (~16.5292MPa) (determined through optimization in MAiNGO)
				constexpr double TminD2hdT2Gt0 = 313.9376246834747;				//!< Lower bound on temperature in K for which d2h/dT2 is guaranteed to be >= 0 (determined through optimization in MAiNGO)
				constexpr double pminD2hdT2Gt0 = 25.95851437648735;				//!< Lower bound on pressure in MPa for which d2h/dT2 is guaranteed to be >= 0 (determined through optimization in MAiNGO)

				// Auxiliary data for the extension and relaxations of s(p,T)
				constexpr double pminDsdpLt0 = 18.93876226118118;				//!< Lower bound on pressure in MPa for which ds/dp is guaranteed to be <= 0 (determined through optimization in MAiNGO)
				constexpr double TminDsdpLt0 = 277.1333780688883;				//!< Lower bound on temperature in K for which ds/dp is guaranteed to be <= 0 (determined through optimization in MAiNGO)
				constexpr double alphaD2sdT2 = 0.5*6.969139275569508e-05;		//!< Alpha parameter used for making s(p,T) componentwise concave w.r.t. T
				constexpr double alphaD2sdp2 = 0.5*3.850687657310027e-06;		//!< Alpha parameter used for making s(p,T) componentwise concave w.r.t. p (only needed if T<~318J)
				constexpr double TminD2sdp2Gt0 = 318.2227203102469;				//!< Lower bound on temperature in K for which d2s/dp2 is guaranteed to be >= 0 (determined through optimization in MAiNGO)

				// Auxiliary data for the extension and relaxations of T(p,h)
				constexpr double hmaxDTdpGt0 = 1056.151838508548;				//!< Upper bound on enthalpy in kJ/kg for which dT/dp is guaranteed to be >=0 (determined through optimization in MAiNGO)
				constexpr double hminDTdpLt0 = 1517.274285941795;				//!< Lower bound on enthalpy in kJ/kg for which dT/dp is guaranteed to be >=0 (determined through optimization in MAiNGO)
				constexpr double TmaxAtHminDTdpLt0 = 615.1465702343805;			//!< Upper bound on temperature in K at hminDTdpLt0
				constexpr double hminD2Tdh2Lt0 = 165.8177568446565;				//!< Lower bound on enthalpy in kJ/kg for which d2T/dh2 is guaranteed to be <= 0 (determined through optimization in MAiNGO)
				constexpr double pminD2Tdh2Lt0 = 16.35167869119773;				//!< Lower bound on pressure in MPa for which d2T/dh2 is guaranteed to be <= 0 (determined through optimization in MAiNGO)
				constexpr double alphaD2Tdh2 = 0.5*8.249651994873545e-06;		//!< Alpha parameter used for making T(p,h) componentwise concave w.r.t. h (only needed if h<165kJ/kg and p<16MPa)
			/**@}*/


		}	// end namespace data


	}	// end namespace region 1


	namespace region2 {


		namespace data {


			/**
			* @name Data used within region 2.
			*/
			/**@{*/
				// Bounds
				constexpr double Tmin = 273.15;								//!< Lower bound on temperature in K (by definition)
				constexpr double Tmax = 1073.15;							//!< Upper bound on temperature in K (by definition)
				constexpr double pmin = 611.2127e-6;						//!< Lower bound on pressure in MPa (by definition)
				constexpr double pmax = 100.;								//!< Upper bound on pressure in MPa (by definition)
				constexpr double hmin = 2500.8250000;						//!< Lower bound on enthalpy in kJ/kg on the physical(!) domain of region 2 (i.e., when considering ps(T) and B23 as constraints)
				constexpr double hmax = 4160.6629478;						//!< Upper bound on enthalpy in kJ/kg on the physical(!) domain of region 2 (i.e., when considering ps(T) and B23 as constraints)
				constexpr double smin = 5.048096823313416;					//!< Lower bound on entropy in kJ/(kg*K) on the physical(!) domain of region 2 (i.e., when considering ps(T) and B23 as constraints)
				constexpr double smax = 11.92105505162985;					//!< Upper bound on entropy in kJ/(kg*K) on the physical(!) domain of region 2 (i.e., when considering ps(T) and B23 as constraints)

				// Reference values
				constexpr double Tstar = 540.;								//!< Reference temperature in K
				constexpr double pstar = 1.;								//!< Reference pressure in MPa
				constexpr double TstarBack = 1.;							//!< Reference temperature in K for backward equations
				constexpr double pstarBack = 1.;							//!< Reference pressure in MPa for backward equations
				constexpr double hstarBack = 2000.;							//!< Reference enthalpy in kJ/kg for backward equations
				constexpr double sstarBackA = 2.;							//!< Reference entropy in kJ/(kg*K) for backward equations in region 2a
				constexpr double sstarBackB = 0.7853;						//!< Reference entropy in kJ/(kg*K) for backward equations in region 2b
				constexpr double sstarBackC = 2.9251;						//!< Reference entropy in kJ/(kg*K) for backward equations in region 2c
				constexpr double hstarBackBC = 1.;							//!< Reference enthalpy in kJ/kg for the equations describing the boundary between regions 2b and 2c
				constexpr double Tstar23 = 1.;								//!< Reference temperature in K for the equations describing the boundary between regions 2 and 3
				constexpr double pstar23 = 1.;								//!< Reference pressure in MPa for the equations describing the boundary between regions 2 and 3c

				// Bounds for boundary equations
				constexpr double TminB23 = 623.15;							//!< Lower bound on temperature in K (intersection with vapor pressure curve)
				constexpr double TmaxB23 = 863.15;							//!< Upper bound on temperature in K (intersection with p=100MPa)
				constexpr double pminB23 = 16.529164253;					//!< Lower bound on pressure in MPa (intersection with vapor pressure curve)
				constexpr double pmaxB23 = 100.;							//!< Upper bound on pressure in MPa (by definition)
				constexpr double hminB2bc = 2.778265762606328e+03;			//!< Lower bound on enthalpy in kJ/kg (intersection with vapor pressure curve)
				constexpr double hmaxB2bc = 3.516004322901269e+03;			//!< Upper bound on enthalpy in kJ/kg (intersection with p=100MPa)
				constexpr double pminB2bc = 6.54670;						//!< Lower bound on pressure in MPa (intersection with vapor pressure curve)
				constexpr double pmaxB2bc = 100.;							//!< Upper bound on pressure in MPa (by definition)

				// Bounds on subregion 2a
				constexpr double TminA = 273.15;							//!< Lower bound on temperature in K in region 2a (by definition)
				constexpr double TmaxA = 1073.15;							//!< Upper bound on temperature in K in region 2a (by definition)
				constexpr double pminA = 611.2127e-6;						//!< Lower bound on pressure in MPa in region 2a (by definition)
				constexpr double pmaxA = 4.;								//!< Upper bound on pressure in MPa in region 2a (by definition)

				// Bounds on subregion 2b
				constexpr double TmaxB = 1073.15;							//!< Upper bound on temperature in K in region 2b (by definition)
				constexpr double pminB = 4.;								//!< Lower bound on pressure in MPa in region 2b (by definition)
				constexpr double pmaxB = 100.;								//!< Upper bound on pressure in MPa in region 2b (by definition)
				constexpr double sminB = 5.85;								//!< Lower bound on entropy in kJ/(kg*K) in region 2b (by definition)

				// Bounds on subregion 2c
				constexpr double pminC = 6.54670;							//!< Lower bound on pressure in MPa in region 2c (intersection of B2bc w/ vapor pressure curve)
				constexpr double pmaxC = 100.;								//!< Upper bound on pressure in MPa in region 2c (by definition)
				constexpr double smaxC = 5.85;								//!< Upper bound on entropy in kJ/(kg*K) in region 2c (by definition)

				// Parameters for actual equations
				const std::vector< DataTriple<int,int,double> > parBasic0 = {
					{0,0,-0.96927686500217E1}
					,{0,1,0.10086655968018E2}
					,{0,-5,-0.56087911283020E-2}
					,{0,-4,0.71452738081455E-1}
					,{0,-3,-0.40710498223928}
					,{0,-2,0.14240819171444E1}
					,{0,-1,-0.43839511319450E1}
					,{0,2,-0.28408632460772}
					,{0,3,0.21268463753307E-1}
				};		//!< Vector holding the exponents and coefficients for the ideal-gas part of the basic equation of region 2
				const std::vector< DataTriple<int,int,double> > parBasicR = {
					{1,0,-0.17731742473213E-2}
					,{1,1,-0.17834862292358E-1}
					,{1,2,-0.45996013696365E-1}
					,{1,3,-0.57581259083432E-1}
					,{1,6,-0.50325278727930E-1}
					,{2,1,-0.33032641670203E-4}
					,{2,2,-0.18948987516315E-3}
					,{2,4,-0.39392777243355E-2}
					,{2,7,-0.43797295650573E-1}
					,{2,36,-0.26674547914087E-4}
					,{3,0,0.20481737692309E-7}
					,{3,1,0.43870667284435E-6}
					,{3,3,-0.32277677238570E-4}
					,{3,6,-0.15033924542148E-2}
					,{3,35,-0.40668253562649E-1}
					,{4,1,-0.78847309559367E-9}
					,{4,2,0.12790717852285E-7}
					,{4,3,0.48225372718507E-6}
					,{5,7,0.22922076337661E-5}
					,{6,3,-0.16714766451061E-10}
					,{6,16,-0.21171472321355E-2}
					,{6,35,-0.23895741934104E2}
					,{7,0,-0.59059564324270E-17}
					,{7,11,-0.12621808899101E-5}
					,{7,25,-0.38946842435739E-1}
					,{8,8,0.11256211360459E-10}
					,{8,36,-0.82311340897998E1}
					,{9,13,0.19809712802088E-7}
					,{10,4,0.10406965210174E-18}
					,{10,10,-0.10234747095929E-12}
					,{10,14,-0.10018179379511E-8}
					,{16,29,-0.80882908646985E-10}
					,{16,50,0.10693031879409}
					,{18,57,-0.33662250574171}
					,{20,20,0.89185845355421E-24}
					,{20,35,0.30629316876232E-12}
					,{20,48,-0.42002467698208E-5}
					,{21,21,-0.59056029685639E-25}
					,{22,53,0.37826947613457E-5}
					,{23,39,-0.12768608934681E-14}
					,{24,26,0.73087610595061E-28}
					,{24,40,0.55414715350778E-16}
					,{24,58,-0.94369707241210E-6}
				};		//!< Vector holding the exponents and coefficients for the residual part of the basic equation of region 2
				const std::vector< DataTriple<int,int,double> > parBackwardTphA = {
					{0,0,0.10898952318288E4}
					,{0,1,0.84951654495535E3}
					,{0,2,-0.10781748091826E3}
					,{0,3,0.33153654801263E2}
					,{0,7,-0.74232016790248E1}
					,{0,20,0.11765048724356E2}
					,{1,0,0.18445749355790E1}
					,{1,1,-0.41792700549624E1}
					,{1,2,0.62478196935812E1}
					,{1,3,-0.17344563108114E2}
					,{1,7,-0.20058176862096E3}
					,{1,9,0.27196065473796E3}
					,{1,11,-0.45511318285818E3}
					,{1,18,0.30919688604755E4}
					,{1,44,0.25226640357872E6}
					,{2,0,-0.61707422868339E-2}
					,{2,2,-0.31078046629583}
					,{2,7,0.11670873077107E2}
					,{2,36,0.12812798404046E9}
					,{2,38,-0.98554909623276E9}
					,{2,40,0.28224546973002E10}
					,{2,42,-0.35948971410703E10}
					,{2,44,0.17227349913197E10}
					,{3,24,-0.13551334240775E5}
					,{3,44,0.12848734664650E8}
					,{4,12,0.13865724283226E1}
					,{4,32,0.23598832556514E6}
					,{4,44,-0.13105236545054E8}
					,{5,32,0.73999835474766E4}
					,{5,36,-0.55196697030060E6}
					,{5,42,0.37154085996233E7}
					,{6,34,0.19127729239660E5}
					,{6,44,-0.41535164835634E6}
					,{7,28,-0.62459855192507E2}
				};		//!< Vector holding the exponents and coefficients for the backward equation T(p,h) of region 2a
				const std::vector< DataTriple<int,int,double> > parBackwardTphB = {
					{0,0,0.14895041079516E4}
					,{0,1,0.74307798314034E3}
					,{0,2,-0.97708318797837E2}
					,{0,12,0.24742464705674E1}
					,{0,18,-0.63281320016026}
					,{0,24,0.11385952129658E1}
					,{0,28,-0.47811863648625}
					,{0,40,0.85208123431544E-2}
					,{1,0,0.93747147377932}
					,{1,2,0.33593118604916E1}
					,{1,6,0.33809355601454E1}
					,{1,12,0.16844539671904}
					,{1,18,0.73875745236695}
					,{1,24,-0.47128737436186}
					,{1,28,0.15020273139707}
					,{1,40,-0.21764114219750E-2}
					,{2,2,-0.21810755324761E-1}
					,{2,8,-0.10829784403677}
					,{2,18,-0.46333324635812E-1}
					,{2,40,0.71280351959551E-4}
					,{3,1,0.11032831789999E-3}
					,{3,2,0.18955248387902E-3}
					,{3,12,0.30891541160537E-2}
					,{3,24,0.13555504554949E-2}
					,{4,2,0.28640237477456E-6}
					,{4,12,-0.10779857357512E-4}
					,{4,18,-0.76462712454814E-4}
					,{4,24,0.14052392818316E-4}
					,{4,28,-0.31083814331434E-4}
					,{4,40,-0.10302738212103E-5}
					,{5,18,0.28217281635040E-6}
					,{5,24,0.12704902271945E-5}
					,{5,40,0.73803353468292E-7}
					,{6,28,-0.11030139238909E-7}
					,{7,2,-0.81456365207833E-13}
					,{7,28,-0.25180545682962E-10}
					,{9,1,-0.17565233969407E-17}
					,{9,40,0.86934156344163E-14}
				};		//!< Vector holding the exponents and coefficients for the backward equation T(p,h) of region 2b
				const std::vector< DataTriple<int,int,double> > parBackwardTphC = {
					{-7,0,-0.32368398555242E13}
					,{-7,4,0.73263350902181E13}
					,{-6,0,0.35825089945447E12}
					,{-6,2,-0.58340131851590E12}
					,{-5,0,-0.10783068217470E11}
					,{-5,2,0.20825544563171E11}
					,{-2,0,0.61074783564516E6}
					,{-2,1,0.85977722535580E6}
					,{-1,0,-0.25745723604170E5}
					,{-1,2,0.31081088422714E5}
					,{0,0,0.12082315865936E4}
					,{0,1,0.48219755109255E3}
					,{1,4,0.37966001272486E1}
					,{1,8,-0.10842984880077E2}
					,{2,4,-0.45364172676660E-1}
					,{6,0,0.14559115658698E-12}
					,{6,1,0.11261597407230E-11}
					,{6,4,-0.17804982240686E-10}
					,{6,10,0.12324579690832E-6}
					,{6,12,-0.11606921130984E-5}
					,{6,16,0.27846367088554E-4}
					,{6,20,-0.59270038474176E-3}
					,{6,22,0.12918582991878E-2}
				};		//!< Vector holding the exponents and coefficients for the backward equation T(p,h) of region 2c
				const std::vector< DataTriple<double,int,double> > parBackwardTpsA = {
					{-1.5,-24,-0.39235983861984E6}
					,{-1.5,-23,0.51526573827270E6}
					,{-1.5,-19,0.40482443161048E5}
					,{-1.5,-13,-0.32193790923902E3}
					,{-1.5,-11,0.96961424218694E2}
					,{-1.5,-10,-0.22867846371773E2}
					,{-1.25,-19,-0.44942914124357E6}
					,{-1.25,-15,-0.50118336020166E4}
					,{-1.25,-6,0.35684463560015}
					,{-1.0,-26,0.44235335848190E5}
					,{-1.0,-21,-0.13673388811708E5}
					,{-1.0,-17,0.42163260207864E6}
					,{-1.0,-16,0.22516925837475E5}
					,{-1.0,-9,0.47442144865646E3}
					,{-1.0,-8,-0.14931130797647E3}
					,{-0.75,-15,-0.19781126320452E6}
					,{-0.75,-14,-0.23554399470760E5}
					,{-0.5,-26,-0.19070616302076E5}
					,{-0.5,-13,0.55375669883164E5}
					,{-0.5,-9,0.38293691437363E4}
					,{-0.5,-7,-0.60391860580567E3}
					,{-0.25,-27,0.19363102620331E4}
					,{-0.25,-25,0.42660643698610E4}
					,{-0.25,-11,-0.59780638872718E4}
					,{-0.25,-6,-0.70401463926862E3}
					,{0.25,1,0.33836784107553E3}
					,{0.25,4,0.20862786635187E2}
					,{0.25,8,0.33834172656196E-1}
					,{0.25,11,-0.43124428414893E-4}
					,{0.5,0,0.16653791356412E3}
					,{0.5,1,-0.13986292055898E3}
					,{0.5,5,-0.78849547999872}
					,{0.5,6,0.72132411753872E-1}
					,{0.5,10,-0.59754839398283E-2}
					,{0.5,14,-0.12141358953904E-4}
					,{0.5,16,0.23227096733871E-6}
					,{0.75,0,-0.10538463566194E2}
					,{0.75,4,0.20718925496502E1}
					,{0.75,9,-0.72193155260427E-1}
					,{0.75,17,0.20749887081120E-6}
					,{1,7,-0.18340657911379E-1}
					,{1,18,0.29036272348696E-6}
					,{1.25,3,0.21037527893619}
					,{1.25,15,0.25681239729999E-3}
					,{1.5,5,-0.12799002933781E-1}
					,{1.5,18,-0.82198102652018E-5}
				};		//!< Vector holding the exponents and coefficients for the backward equation T(p,s) of region 2a
				const std::vector< DataTriple<int,int,double> > parBackwardTpsB = {
					{-6,0,0.31687665083497E6}
					,{-6,11,0.20864175881858E2}
					,{-5,0,-0.39859399803599E6}
					,{-5,11,-0.21816058518877E2}
					,{-4,0,0.22369785194242E6}
					,{-4,1,-0.27841703445817E4}
					,{-4,11,0.99207436071480E1}
					,{-3,0,-0.75197512299157E5}
					,{-3,1,0.29708605951158E4}
					,{-3,11,-0.34406878548526E1}
					,{-3,12,0.38815564249115}
					,{-2,0,0.17511295085750E5}
					,{-2,1,-0.14237112854449E4}
					,{-2,6,0.10943803364167E1}
					,{-2,10,0.89971619308495}
					,{-1,0,-0.33759740098958E4}
					,{-1,1,0.47162885818355E3}
					,{-1,5,-0.19188241993679E1}
					,{-1,8,0.41078580492196}
					,{-1,9,-0.33465378172097}
					,{0,0,0.13870034777505E4}
					,{0,1,-0.40663326195838E3}
					,{0,2,0.41727347159610E2}
					,{0,4,0.21932549434532E1}
					,{0,5,-0.10320050009077E1}
					,{0,6,0.35882943516703}
					,{0,9,0.52511453726066E-2}
					,{1,0,0.12838916450705E2}
					,{1,1,-0.28642437219381E1}
					,{1,2,0.56912683664855}
					,{1,3,-0.99962954584931E-1}
					,{1,7,-0.32632037778459E-2}
					,{1,8,0.23320922576723E-3}
					,{2,0,-0.15334809857450}
					,{2,1,0.29072288239902E-1}
					,{2,5,0.37534702741167E-3}
					,{3,0,0.17296691702411E-2}
					,{3,1,-0.38556050844504E-3}
					,{3,3,-0.35017712292608E-4}
					,{4,0,-0.14566393631492E-4}
					,{4,1,0.56420857267269E-5}
					,{5,0,0.41286150074605E-7}
					,{5,1,-0.20684671118824E-7}
					,{5,2,0.16409393674725E-8}
				};		//!< Vector holding the exponents and coefficients for the backward equation T(p,s) of region 2b
				const std::vector< DataTriple<int,int,double> > parBackwardTpsC = {
					{-2,0,0.90968501005365E3}
					,{-2,1,0.24045667088420E4}
					,{-1,0,-0.59162326387130E3}
					,{0,0,0.54145404128074E3}
					,{0,1,-0.27098308411192E3}
					,{0,2,0.97976525097926E3}
					,{0,3,-0.46966772959435E3}
					,{1,0,0.14399274604723E2}
					,{1,1,-0.19104204230429E2}
					,{1,3,0.53299167111971E1}
					,{1,4,-0.21252975375934E2}
					,{2,0,-0.31147334413760}
					,{2,1,0.60334840894623}
					,{2,2,-0.42764839702509E-1}
					,{3,0,0.58185597255259E-2}
					,{3,1,-0.14597008284753E-1}
					,{3,5,0.56631175631027E-2}
					,{4,0,-0.76155864584577E-4}
					,{4,1,0.22440342919332E-3}
					,{4,4,-0.12561095013413E-4}
					,{5,0,0.63323132660934E-6}
					,{5,1,-0.20541989675375E-5}
					,{5,2,0.36405370390082E-7}
					,{6,0,-0.29759897789215E-8}
					,{6,1,0.10136618529763E-7}
					,{7,0,0.59925719692351E-11}
					,{7,1,-0.20677870105164E-10}
					,{7,3,-0.20874278181886E-10}
					,{7,4,0.10162166825089E-9}
					,{7,5,-0.16429828281347E-9}
				};		//!< Vector holding the exponents and coefficients for the backward equation T(p,s) of region 2c
				const std::vector<double> parB23 = {
					0.34805185628969e3,
					-0.11671859879975e1,
					0.10192970039326e-2,
					0.57254459862746e3,
					0.13918839778870e2
				};		//!< Vector holding the coefficients for the equations describing the boundary between regions 2 and 3
				const std::vector<double> parBackwardB2BC = {
					 0.90584278514723e3,
					-0.67955786399241,
					 0.12809002730136e-3,
					 0.26526571908428e4,
					 0.45257578905948e1
				};		//!< Vector holding the coefficients for the backward equations describing the boundary between regions 2b and 2c

				// Auxiliary data for the extension and relaxations of h(p,T)
				constexpr double Tplim = 350.;								//!< Temperature required for computing the boundary of the relaxed physical domain of region 2 for h(p,T)
				constexpr double aPlim = -25.75767694;						//!< Coefficient for computing the boundary of the relaxed physical domain of region 2 for h(p,T)
				constexpr double bPlim = 0.2283366028;						//!< Coefficient for computing the boundary of the relaxed physical domain of region 2 for h(p,T)
				constexpr double cPlim = -0.0006778819463;					//!< Coefficient for computing the boundary of the relaxed physical domain of region 2 for h(p,T)
				constexpr double dPlim = 0.0000006745676081;				//!< Coefficient for computing the boundary of the relaxed physical domain of region 2 for h(p,T)
				constexpr double pmaxD2hdp2Lt0wAlpha = 80;					//!< Upper bound (non-strict) on pressure in MPa such that d2h/dp2-2*alphaForD2hdp2 (of the un-cut model!) is guaranteed to be <=0 (--> h(p,T) component-wise concave w.r.t. p)
				constexpr double pmaxD2hdp2Lt0 = 28.68;						//!< Upper bound (non-strict) on pressure in MPa such that d2h/dp2 (of the un-cut model!) is guaranteed to be <=0 (--> h(p,T) component-wise concave w.r.t. p)
				constexpr double pmaxD2hdpTgt0 = 60.;						//!< Upper bound (non-strict) on pressure in MPa such that dh/dp is guaranteed to be <=0
				constexpr double alphaD2hdT2 = 0.5*0.0095;					//!< Alpha parameter used for making h(p,T) componentwise concave w.r.t. T
				constexpr double alphaD2hdT2Tlt350orgt375 = 0.5*0.000711;	//!< Alpha parameter used for making h(p,T) componentwise concave w.r.t. T if T>=375 or T<=350
				constexpr double alphaD2hdp2 = 0.5*0.5363876285005711;		//!< Alpha parameter used for making h(p,T) componentwise concave w.r.t. p
				constexpr double kAlphaD2hdp2 = -11.57296832749063;			//!< Coefficient for an additional linear term in p to be used when constructing a component-wise concave overestimator using alphaD2hdp2 in order to maintain monotonicity .w.r.t p

				// Auxiliary data for the extension and relaxations of s(p,T)
				constexpr double aTlim = 531.1061145;										//!< Coefficient for computing the boundary of the relaxed physical domain of region 2 for s(p,T)
				constexpr double bTlim = 6.246965208;										//!< Coefficient for computing the boundary of the relaxed physical domain of region 2 for s(p,T)
				constexpr double cTlim = - 0.04337113851;									//!< Coefficient for computing the boundary of the relaxed physical domain of region 2 for s(p,T)
				constexpr double dTlim = 0.0001409087498;									//!< Coefficient for computing the boundary of the relaxed physical domain of region 2 for s(p,T)
				constexpr double TminD2sdp2Gt0 = 793.4145778879107;							//!< Lower bound on temperature in K above which d2s/dp2 is guaranteed to be >= 0
				constexpr double alphaD2sdp2PgtPminB23 = 0.5*0.193141198507478;				//!< Alpha parameter used for making s(p,T) componentwise concave w.r.t. p if p>=pminB23
				constexpr double alphaD2sdp2PltPminB23 = 0.5*0.1063008916271836;			//!< Alpha parameter used for making s(p,T) componentwise concave w.r.t. p if p<pminB23
				constexpr double alphaD2sdp2PgtPminB23Tgt700 = 0.5*0.02271464655983191;		//!< Alpha parameter used for making s(p,T) componentwise concave w.r.t. p if p>=pminB23 and T>=700K
				constexpr double alphaD2sHatdp2 = 0.5*0.00031;								//!< Alpha parameter used for making the extension of s(p,T) to the non-physical region (T<Tlim(p)) componentwise concave w.r.t. p
				constexpr double alphaD2sdp2PltPminB23Tlt513 = alphaD2sHatdp2;				//!< Alpha parameter used for making s(p,T) componentwise concave w.r.t. p if p>=pminB23 and T<=513K
				constexpr double TmaxD2sdpTGt0 = 793.8402907993708;							//!< Upper bound on temperature in K below which d2s/dpT is guaranteed to be >= 0
				constexpr double TminD2sdpTGt0 = 887.4568880763973;							//!< Lower bound on temperature in K above which d2s/dpT is guaranteed to be >= 0
				constexpr double pmaxD2sdpTGt0 = 61.33609559851094;							//!< Upper bound on pressure in MPa below which d2s/dpT is guaranteed to be >= 0
				constexpr double alphaD2sdpT = 3.774152720309343e-05;						//!< Alpha parameter used for ensuring that d2s/dpT>=0 outside the area delimited by the above values
				constexpr double alphaD2sdT2 = 0.5*0.009444862298557028;					//!< Alpha parameter used for making component-wise convex w.r.t. T (needed for the concave relaxation)

				// Auxiliary data for the extension and relaxations of T(p,h)
				constexpr double aHlim = 2.48996341019e+03;									//!< Coefficient for computing the boundary of the relaxed physical domain of region 2 for T(p,h)
				constexpr double bHlim = 1.893671037353940;									//!< Coefficient for computing the boundary of the relaxed physical domain of region 2 for T(p,h)
				constexpr double cHlim = 0.013;												//!< Coefficient for computing the boundary of the relaxed physical domain of region 2 for T(p,h)
				constexpr double dHlim = 19200.;											//!< Coefficient for computing the boundary of the relaxed physical domain of region 2 for T(p,h)
				constexpr double eHlim = 3.078;												//!< Coefficient for computing the boundary of the relaxed physical domain of region 2 for T(p,h)
				constexpr double fHlim = 5.4;												//!< Coefficient for computing the boundary of the relaxed physical domain of region 2 for T(p,h)
				constexpr double hminD2Tphdp2lt0 = 2619.799618352637;						//!< Lower bound on enthalpy in kJ/kg above which d2T/dp2 is guaranteed to be <= 0
				constexpr double pminD2Tphdp2lt0 = 0.02656664927344643;						//!< Lower bound on pressure in MPa above which d2T/dp2 is guaranteed to be <= 0
				constexpr double hminD2Tdh2Gt0pGt4MPa = 2711.668600204316;					//!< Upper bound on enthalpy in kJ/kg for p>=4MPa below which d2T/dh2 is guaranteed to be >= 0
				constexpr double hmaxD2Tdh2Gt0pGt4MPa = 3505.660030680284;					//!< Upper bound on enthalpy in kJ/kg for p>=4MPa below which d2T/dh2 is guaranteed to be >= 0
				constexpr double pminD2Tdh2Gt0 = 18.68325482025725;							//!< Lower bound on pressure in MPa above which d2T/dh2 is guaranteed to be >= 0
				constexpr double pmaxD2Tdh2Gt0 = 69.65438149938009;							//!< Upper bound on pressure in MPa below which d2T/dh2 is guaranteed to be >= 0
				constexpr double alphaD2Tdh2 = 0.5*7.747118828961489e-05;					//!< Alpha parameter used for ensuring that d2T/dh2>=0; only needed outside the area delimited by the above values
				constexpr double alphaD2Tdph = 0.001520567576851156;						//!< Alpha parameter used for ensuring that d2T/dph<=0
				constexpr double alphaD2TdphPhys = 7.547330836043216e-07;					//!< Alpha parameter used for ensuring that d2T/dph<=0, can be used if we are safely in the (relaxed) physical region
				constexpr double hminalphaPhys = 2815.;										//!< Lower bound on enthalpy in kJ/kg above which it is save to use alphaD2TdphPhys

				// Auxiliary data for the extension and relaxations of T(p,s)
				constexpr double pminD2Tpsdp2lt0 = 4.;						//!< Lower bound on pressure in MPa above which d2Tdp2 is guaranteed to be <= 0
				constexpr double pmaxD2Tpsdp2lt0 = 3.8256;					//!< Upper bound on pressure in MPa below which d2Tdp2 is guaranteed to be <= 0
				constexpr double sminD2Tpsdp2lt0 = 5.51818;					//!< Lower bound on entropy in kJ/(kg*K) above which d2Tdp2 is guaranteed to be <= 0
				constexpr double alphaD2Tpsdp2 =  0.5*6.68425;				//!< Alpha parameter used for ensuring that d2T/dp2<=0; only needed outside the area delimited by the above values
				constexpr double alphaD2Tpsdph = 18.8785;					//!< Alpha parameter used for ensuring that d2T/dph>=0; only needed outside the area delimited by the above values

				// Auxiliary data for the extension of the boundary equations for B23 and B2bc
				constexpr double TB23hat = 594.5405083;						//!< Temperature in K below which p23(T) is extrapolated linearly (such that it hits (pmin,Tmin))
				constexpr double kTB23 = 0.04484072966;						//!< Slope of p23(T) below TB23hat
				constexpr double pB23hat = 14.4119961;						//!< Pressure in MPa below which T23(p) is extrapolated linearly (such that it hits (pmin,Tmin))
				constexpr double khB2bc = 42.382676376860026;				//!< Slope of pb2bc(h) below hminB2bc
			/**@}*/


		}	// end namespace data


	}	// end namespace region 2


	namespace region4 {


		namespace data {


			/**
			* @name Data used within region 4.
			*/
			/**@{*/

				// Bounds
				constexpr double pcrit = 22.064;								//!< Critical temperature in MPa
				constexpr double Tcrit = 647.096;							//!< Critical temperature in K
				constexpr double pmin = 611.2127e-6;						//!< Lower bound on pressure in MPa (by definition)
				constexpr double pmax = pcrit;								//!< Upper bound on pressure in MPa (by definition)
				constexpr double Tmin = 273.15;								//!< Lower bound on temperature in K (by definition)
				constexpr double Tmax = Tcrit;								//!< Upper bound on temperature in K (by definition)
				constexpr double pmax12 = region2::data::pminB23;		//!< Upper bound on pressure in MPa for subregion 4-1/2 (by definition)
				constexpr double Tmax12 = region2::data::TminB23;		//!< Upper bound on temperature in K for subregion 4-1/2 (by definition)
				constexpr double hmin12 = -0.04158782598778999;			//!< Lower bound on enthalpy in kJ/kg for subregion 4-1/2 (determined through optimization in MAiNGO)
				constexpr double hmax12 = 2803.285255890569;				//!< Upper bound on enthalpy in kJ/kg for subregion 4-1/2 (determined through optimization in MAiNGO)
				constexpr double smin12 = -0.0001545495919410556;		//!< Lower bound on entropy in kJ/(kg*K) for subregion 4-1/2 (determined through optimization in MAiNGO)
				constexpr double smax12 = 9.155759395224399;				//!< Upper bound on entropy in kJ/(kg*K) for subregion 4-1/2 (determined through optimization in MAiNGO)

				// Reference values
				constexpr double Tstar = 1.;									//!< Reference temperature in K for region 4
				constexpr double pstar = 1.;									//!< Reference pressure in MPa for region 4

				// Parameters for actual equations
				const std::vector<double> parBasic = {
					0.11670521452767e4,
					-0.72421316703206e6,
					-0.17073846940092e2,
					0.12020824702470e5,
					-0.32325550322333e7,
					0.14915108613530e2,
					-0.48232657361591e4,
					0.40511340542057e6,
					-0.23855557567849,
					0.65017534844798e3,
				};		//!< Vector holding the coefficients for the basic equation of region 4

				// Auxiliary data for extension of ps(T), Ts(p)
				constexpr double psExtrA = 1391.033011;							//!< Parameter of ps(T)=a+b*T+c*T^2 above Tcrit (and its inverse)
				constexpr double psExtrB = -4.499255052;						//!< Parameter of ps(T)=a+b*T+c*T^2 above Tcrit (and its inverse)
				constexpr double psExtrC = 0.003683684059;						//!< Parameter of ps(T)=a+b*T+c*T^2 above Tcrit (and its inverse)

				// Auxiliary data for the  relaxations of hliq(p), hliq(T)
				constexpr double pmaxD2hliq12dp2lt0 = 14.48063980901768; 		//!< Upper bound on pressure in MPa s.t. d2hliq12/dp2<=0
				constexpr double alphaD2hliq12dp2 = 0.5*1.059230085082255;		//!< Alpha parameter used for making hliq12(p) concave (needed only for pU>pmaxD2hliq12dp2lt0)
				constexpr double TminD2hliq12dT2gt0 = 313.269208736924; 		//!< Lower bound on temperature in K s.t. d2hliq12/dT2>=0
				constexpr double alphaD2hliq12dT2 = 0.5*0.003584589592569951;	//!< Alpha parameter used for making hliq12(T) convex (needed only for TL<TminD2hliq12dT2gt0)

				// Auxiliary data for the  relaxations of hvap(p), hvap(T)
				constexpr double pmaxhvap12 = 3.078375697034355; 				//!< Pressure in MPa at which hvap12(p) attains its maximum
				constexpr double Tmaxhvap12 = 508.4429513535588; 				//!< Temperature in K at which hvap12(T) attains its maximum

				// Auxiliary data for the  relaxations of x(p,h)
				constexpr double mindeltahvap12 = 892.7337855842432;	 			//!< Lower bound on hvap-hliq in kJ/kg in region 4-1/2
				constexpr double hmaxDx12hpdpLt0 = 2158.6301581;					//!< Upper bound on enthalpy in kJ/kg for which dx/dp<=0 in region 4-1/2
				constexpr double pmaxDx12hpdpLt0 = 3.07837;							//!< Upper bound on pressure in MPa for which dx/dp<=0 in region 4-1/2
				constexpr double alphaD2x12dp2hGthliq = 0.5*0.0086423;				//!< Alpha parameter used for making x(p,h) componentwise convex w.r.t. p (only needed in certain regions)
				constexpr double alphaD2x12dp2 = 0.5*0.0439148;						//!< Alpha parameter used for making x(p,h) componentwise convex w.r.t. p (only needed in certain regions)
				constexpr double pmaxD2x12phdp2Gt0 = 6.585179;						//!< Upper bound on pressure in MPa for which d2x/dp2>=0 in region 4-1/2
				constexpr double hmaxD2x12phdp2Gt0 = 1245.722;						//!< Upper bound on enthalpy in kJ/kg for which d2x/dp2>=0 in region 4-1/2
				constexpr double hminD2x12phdp2Gt0 = 2080.255;						//!< Lower bound on enthalpy in kJ/kg for which d2x/dp2>=0 in region 4-1/2

				// Auxiliary data for the  relaxations of sliq(p), sliq(T)
				constexpr double pmaxD2sliq12dp2lt0 = 15.26705;					//!< Upper bound on pressure in MPa s.t. d2sliq12/dp2<=0
				constexpr double alphaD2sliq12dp2 = 0.5*0.001115488677665959;	//!< Alpha parameter used for making sliq12(p) concave (needed only for pU>pmaxD2sliq12dp2lt0)
				constexpr double TmaxD2sliq12dT2lt0 = 528.1660519636621;		//!< Upper bound on temperature in K s.t. d2sliq12/dT2<=0
				constexpr double TminD2sliq12dT2gt0 = 528.1739559430038;		//!< Lower bound on temperature in K s.t. d2sliq12/dT2>=0
				constexpr double alphaD2sliq12dT2 = 0.5*6.983393604911197e-05;	//!< Alpha parameter used for making sliq12(T) convex (needed only for TU>TmaxD2sliq12dT2lt0 or TL<TminD2sliq12dT2gt0)

				// Auxiliary data for the  relaxations of svap(p), svap(T)
				constexpr double pmaxD2svap12dp2gt0 = 12.23513758722595;		//!< Upper bound on pressure in MPa s.t. d2svap12/dp2>=0
				constexpr double alphaD2svap12dp2 = 0.5*0.003711065590762716;	//!< Alpha parameter used for making svap12(p) convex (needed only for pU>pmaxD2svap12dp2gt0)
				constexpr double TzeroD2svap12dT2 = 5.182198169984522e+02;		//!< Temperature in K at which svap12(T) has its inflection point, i.e., d2svap12/dT2=0

				// Auxiliary data for the  relaxations of s(p,x)
				constexpr double mindeltasvap12 = 1.432606485313751;	 			//!< Lower bound on svap-sliq in kJ/(kg*K) in region 4-1/2
			/**@}*/


		}	// end namespace data


	}	// end namespace region 4


}	// end namespace iapws_if97