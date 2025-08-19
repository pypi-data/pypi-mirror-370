/**
*
*  This is work in progress and is currently not used in MAiNGO!
*
*/


#ifndef MC__VMCCORMICK_LIN_H
#define MC__VMCCORMICK_LIN_H

#include <iostream>
#include <iomanip>
#include <stdarg.h>
#include <cassert>
#include <string>
#include <limits>
#include <functional>
#include <unordered_set>

#include "mcfunc.hpp"
#include "mcop.hpp"

// preprocessor variable for easier debugging
#undef  MC__VMCCORMICK_LIN_DEBUG

namespace mc
{
//! @brief C++ class for vector McCormick relaxation arithmetic for factorable function
////////////////////////////////////////////////////////////////////////
//! mc::vMcCormick is a C++ class computing possibly multiple McCormick
//! convex/concave relaxations of factorable functions on a box at once,
//! as well as doing subgradient propagation. The template parameter
//! corresponds to the type used in the underlying interval arithmetic
//! computations.
////////////////////////////////////////////////////////////////////////
class vMcCormick_Linearizations
////////////////////////////////////////////////////////////////////////
{

public:

    /**
    * @enum OPERATION
    * @brief Enum for representing different intrinsic operation
    */
    enum OPERATION{
		MINUS = 0, PLUS, TIMES,	LMTD, RLMTD, EUCLIDEAN_NORM_2D, EXPX_TIMES_Y, MIN, MAX, SUM_DIV, XLOG_SUM, SINGLE_NEURON
        EXP, INV, SQR, LOG, COS, SIN, TAN, COSH, SINH, TANH, COTH, FABS, SQRT, XLOG, XEXPAX, 
		VAPOR_PRESSURE, IDEAL_GAS_ENTHALPY, SATURATION_TEMPERATURE, ENTHALPY_OF_VAPORIZATION,
		COST_FUNCTION, NRTL_TAU, NRTL_DTAU, P_SAT_ETHANOL_SCHROEDER, RHO_VAP_SAT_ETHANOL_SCHROEDER, RHO_LIQ_SAT_ETHANOL_SCHROEDER,
		ARH, ERF, NPOW, DPOW
    };

    /**
    * @enum STRATEGY_UNIVARIATE
    * @brief Enum for representing different strategies for obtaining additional affine relaxations for bivariate operations
    */
    enum STRATEGY_UNIVARIATE{
        AFFINE_RELAXATION_ALL = 0,
        COMPOSITION_ALL,
        AFFINE_RELAXATION_ALL_TO_MID,
        AFFINE_RELAXATION_MID_TO_ALL,
        COMPOSITION_ALL_TO_MID,
        COMPOSITION_MID_TO_ALL,
		COMPOSITION_BEST_POINT
    };

    /**
    * @enum STRATEGY_BIVARIATE
    * @brief Enum for representing different strategies for obtaining additional affine relaxations for bivariate operations
    */
    enum STRATEGY_BIVARIATE{
        BIVARIATE_ALL = 0,
        BIVARIATE_COBINE_WITH_MID
    };

    /**
    * @enum FUNCTION_TYPE
    * @brief Enum for representing different function types (if any known)
    */
    enum FUNCTION_TYPE{
        CONVEX_INCREASING = 0,
        CONVEX_DECREASING,
        CONVEX,
        CONCAVE_INCREASING,
        CONCAVE_DECREASING,
        CONCAVE,
        FUNC_TYPE_NONE
    };

    enum VALUE_CHOICE{		
		CUT = 0,
		CV,
		CC
	};

    /**
    * @brief Initialization function
    *
    * @param[in] npts is the number of input linearization points
    * @param[in] nvar is the number of participating variables
    */
    void initialize(const unsigned npts, const unsigned nvar, const unsigned midIndex = 0, const unsigned numberOperations = 100,
                   	const STRATEGY_UNIVARIATE strat_univ = COMPOSITION_BEST_POINT, const STRATEGY_BIVARIATE strat_biv = BIVARIATE_COBINE_WITH_MID)
    {
        _npts = npts;
        _nvar = nvar;
		_midIndex = midIndex;
		_runningIndexUniv = 0;
		_strategy_univ = strat_univ;
		_strategy_biv = strat_biv;
		_nadditionalLins = 0;
		_lowerBoundCandidate = -std::numeric_limits<double>::max();
		_upperBoundCandidate =  std::numeric_limits<double>::max();
        set_strategy_univariate(strat_univ);
        set_strategy_bivariate(strat_biv);
        _cv.clear(); _cv.resize(_nadditionalLins);
        _cc.clear(); _cc.resize(_nadditionalLins);
        _cvsub.clear(); _cvsub = std::vector<std::vector<double>>(_nadditionalLins, std::vector<double>(nvar));
        _ccsub.clear(); _ccsub = std::vector<std::vector<double>>(_nadditionalLins, std::vector<double>(nvar));
        _linPoints.clear(); _linPoints = std::vector<std::vector<double>>(_nvar, std::vector<double>(_nadditionalLins));
		_minValues.clear(); _minValues.resize(_nadditionalLins);
		_maxValues.clear(); _maxValues.resize(_nadditionalLins);
    }

    /**
    * @brief Function for setting of pointers to essential information
    *
    * @param[in] originalPoints holds the linearization points in the original variable space, first dimension is the variable dimension, second dimension is the linearization point number
    * @param[in] originalLowerBounds holds the original lower bounds
    * @param[in] originalUpperBounds holds the original upper bounds
    */
    void set_points(const std::vector<std::vector<double>>* originalPoints, const std::vector<double>* originalLowerBounds, const std::vector<double>* originalUpperBounds)
    {
        _originalPoints = originalPoints;
        _originalLowerBounds = originalLowerBounds;
        _originalUpperBounds = originalUpperBounds;
    }

    /**
    * @brief Function for setting strategy
    *
    * @param[in] strategy is the requested strategy
    */
    void set_strategy_bivariate(const STRATEGY_BIVARIATE strategy)
	{
		_index1.clear();
		_index2.clear();
		_originalIndexForBiv.clear();
		_useLeftFactorLinPoint.clear();
        _strategy_biv = strategy;
        switch(_strategy_biv){
            case BIVARIATE_ALL:
			{
                _nadditionalLins = std::max(_nadditionalLins,(_npts*(_npts-1)));
				_nadditionalLinsBiv = _npts*(_npts-1);
				_index1.resize((_npts*(_npts-1)));
				_index2.resize((_npts*(_npts-1)));
				_originalIndexForBiv.resize((_npts*(_npts-1)));
				_useLeftFactorLinPoint.resize((_npts*(_npts-1)));
				unsigned index = 0;
				bool takeFirst = false;
				for(unsigned int i = 0; i<_npts;i++){
					for(unsigned int j = 0; j < _npts; j++){
						if(i!=j){
							_index1[index] = i;
							_index2[index] = j;
							if(takeFirst){
								if(i==_midIndex){ 
									_originalIndexForBiv[index] = j;
									takeFirst = true;
								}
								else{
									_originalIndexForBiv[index] = i;
									takeFirst = false;
								}
							}else{
								if(j==_midIndex){ 
									_originalIndexForBiv[index] = i; 
									takeFirst = false;
								}
								else{
									_originalIndexForBiv[index] = j;
									takeFirst = true;
								}
							}
							index++;
						}
					}
				}
				for(unsigned int i = 0; i<_nadditionalLins;i++){
					_useLeftFactorLinPoint[i] = _originalIndexForBiv[i]==_index1[i];
				}
                break;
			}
            case BIVARIATE_COBINE_WITH_MID:
			{
                _nadditionalLins = std::max(_nadditionalLins,2*(_npts-1));
				_nadditionalLinsBiv = 2*(_npts-1);
                _midIndex = 0;
				_index1.resize(2*(_npts-1));
				_index2.resize(2*(_npts-1));
				_originalIndexForBiv.resize(2*(_npts-1));
				_useLeftFactorLinPoint.resize(2*(_npts-1));
				for(unsigned int i = 0; i < _npts-1;i++){
					_index1[i] = _midIndex;
					_index2[i+_npts-1] = _midIndex;
					_useLeftFactorLinPoint[i] = false;
					_useLeftFactorLinPoint[i+_npts-1] = true;
				}
				unsigned index = 0;
				for(unsigned int i = 0; i < _npts;i++){
					if(i!=_midIndex){
						_index1[index+_npts-1] = i;
						_index2[index] = i;
						_originalIndexForBiv[index+_npts-1] = i;
						_originalIndexForBiv[index] = i;
						index++;
					}
				}
                break;
			}
            default:
                throw std::runtime_error("    mc::vMcCormick_Linearizations\t Error in set_strategy_bivariate, unknown strategy "+std::to_string((unsigned)_strategy_biv)+".");
        }
        _linPoints.clear(); _linPoints = std::vector<std::vector<double>>(_nvar, std::vector<double>(_nadditionalLins));
        _cv.clear(); _cv.resize(_nadditionalLins);
        _cc.clear(); _cc.resize(_nadditionalLins);
        _cvsub.clear(); _cvsub = std::vector<std::vector<double>>(_nadditionalLins, std::vector<double>(_nvar));
        _ccsub.clear(); _ccsub = std::vector<std::vector<double>>(_nadditionalLins, std::vector<double>(_nvar));
		_minValues.clear(); _minValues.resize(_nadditionalLins);
		_maxValues.clear(); _maxValues.resize(_nadditionalLins);
    }

     /**
    * @brief Function for setting strategy for univariate operations
    *
    * @param[in] strategy is the requested strategy
    */
    void set_strategy_univariate(const STRATEGY_UNIVARIATE strategy)
	{
        _strategy_univ = strategy;
		_originalIndexForUniv.clear();
		_computeConvexUniv = true;
		_computeConcaveUniv = true;
        switch(_strategy_univ){
            case AFFINE_RELAXATION_ALL:
            case COMPOSITION_ALL:
			{
                _nadditionalLins = std::max(_nadditionalLins,(_npts*(_npts-1))/2);
				_nadditionalLinsUniv = (_npts*(_npts-1))/2;
				_originalIndexForUniv.resize((_npts*(_npts-1))/2);
				unsigned counter = 0;
				for(unsigned int i = 0; i<_npts; i++){
                    for(unsigned int j = 0; j<_npts; j++){
                        if(i!=j){
							_originalIndexForUniv[counter] = i;
							counter++;
						}
					}
				}
                break;
			}
            case AFFINE_RELAXATION_ALL_TO_MID: case AFFINE_RELAXATION_MID_TO_ALL:
            case COMPOSITION_ALL_TO_MID: case COMPOSITION_MID_TO_ALL:
			{
                _nadditionalLins = std::max(_nadditionalLins,_npts-1);
				_nadditionalLinsUniv = _npts-1;
				_originalIndexForUniv.resize(_npts-1);
				unsigned counter = 0;
				for(unsigned int i = 0; i<_npts; i++){
					if(i!=_midIndex){
						_originalIndexForUniv[counter] = i;
						counter++;			
					}
				}
                break;
			}
			case COMPOSITION_BEST_POINT:
			{
				_nadditionalLins = std::max(_nadditionalLins,_npts);
				_nadditionalLinsUniv = _npts;
				_originalIndexForUniv.resize(_npts);
				unsigned counter = 0;
				for(unsigned int i = 0; i<_npts; i++){
					_originalIndexForUniv[counter] = i;
					counter++;						
				}
				break;
			}
            default:
                throw std::runtime_error("    mc::vMcCormick_Linearizations\t Error in set_strategy_univariate, unknown strategy "+std::to_string((unsigned)_strategy_univ)+".");
        }
        _linPoints.clear(); _linPoints = std::vector<std::vector<double>>(_nvar, std::vector<double>(_nadditionalLins));
        _cv.clear(); _cv.resize(_nadditionalLins);
        _cc.clear(); _cc.resize(_nadditionalLins);
        _cvsub.clear(); _cvsub = std::vector<std::vector<double>>(_nadditionalLins, std::vector<double>(_nvar));
        _ccsub.clear(); _ccsub = std::vector<std::vector<double>>(_nadditionalLins, std::vector<double>(_nvar));
		_minValues.clear(); _minValues.resize(_nadditionalLins);
		_maxValues.clear(); _maxValues.resize(_nadditionalLins);
    }

    /**
    * @brief Function for setting the index of the mid point for strategies reliant on mid point (can be any other point)
    *
    * @param[in] pt is the additional affine relaxation point index
    */
    void set_mid_index(const unsigned pt)
	{
#ifdef MC__VMCCORMICK_LIN_DEBUG
       std::string str = "set_mid_index";
       _check_consistency(str, pt);
#endif
        _midIndex = pt;
    }
 
    /**
    * @brief Function for setting additional values needed for the evaluation of a function, e.g., parameters
    *
    * @param[in] doubleValues is a pointer to additional double values
	* @param[in] intValues is a pointer to additional int values
    */
    void set_additional_values(const double* doubleValues, const int* intValues){
		_additionalValuesDouble = doubleValues;
		_additionalValuesInt = intValues;
	}

    /**
    * @brief Function for resetting the values of the subgradient heuristic candidates
    */
    void reset_candidates(){		
		_lowerBoundCandidate = -std::numeric_limits<double>::max();
		_upperBoundCandidate =  std::numeric_limits<double>::max();
	}

    /**
    * @brief Function for properly computing and propagating additional affine relaxations for univariate compositions
    *
    * @param[in] cv holds convex relaxation values at npts points
    * @param[in] cc holds concave relaxation values at npts points
    * @param[in] cvsub holds convex subgradient values at npts points of nvar variables ([npts][nvar])
    * @param[in] ccsub holds concave subgradient values at npts points of nvar variables ([npts][nvar])
    * @param[in] npts is the number of given linearization points
    * @param[in] op is the given operation
    * @param[in] xL is the lower range bound of input function
    * @param[in] xU is the upper range bound of input function
    */
    void compute_additional_linearizations_univariate_operation
    (double* cv, double* cc, double** cvsub, double** ccsub,
     const unsigned npts, const double xL, const double xU, const OPERATION op)
    {
#ifdef MC__VMCCORMICK_LIN_DEBUG
        if(npts != _npts){
            throw std::runtime_error("mc::vMcCormick_Linearizations\t Error in compute_additional_linearizations_univariate_operation number of points does not match, "+std::to_string(_npts)+"<>"+std::to_string(npts)+".");
        }
#endif

		_lowerBoundCandidate = -std::numeric_limits<double>::max();
		_upperBoundCandidate =  std::numeric_limits<double>::max();
		_set_functions_for_univariate_operation(xL,xU,op);
		
        switch(_strategy_univ){
            case AFFINE_RELAXATION_ALL: case AFFINE_RELAXATION_ALL_TO_MID: case AFFINE_RELAXATION_MID_TO_ALL:
                _compute_additional_lins_by_using_affine_relaxation_for_univariate_function(cv, cc, cvsub, ccsub);
                break;
            case COMPOSITION_ALL: case COMPOSITION_ALL_TO_MID: case COMPOSITION_MID_TO_ALL:
                _compute_additional_lins_by_affine_composition_for_univariate_function(cv, cc, cvsub, ccsub);
                break;
			case COMPOSITION_BEST_POINT:
                 _compute_additional_lins_by_affine_composition_for_univariate_function_with_fixed_points(cv, cc, cvsub, ccsub, xL, xU, op);
                break;				
            default:
                throw std::runtime_error("mc::vMcCormick_Linearizations\t Error in compute_additional_linearizations_univariate_operation, unknown strategy"+std::to_string((unsigned)_strategy_univ)+".");
        }
    }
     
	/**
    * @brief Function for properly computing and propagating additional affine relaxations for bivariate operations
    *
    * @param[in] cvx holds convex relaxation values of first operand at npts points
    * @param[in] ccx holds concave relaxation values of first operand at npts points
    * @param[in] cvsubx holds convex subgradient values of first operand at npts points of nvar variables ([npts][nvar])
    * @param[in] ccsubx holds concave subgradient values of first operand at npts points of nvar variables ([npts][nvar])
    * @param[in] xL is the lower range bound of first operand 
    * @param[in] xU is the upper range bound of first operand 
    * @param[in] cvy holds convex relaxation values of second operand at npts points
    * @param[in] ccy holds concave relaxation values of second operand at npts points
    * @param[in] cvsuby holds convex subgradient values of second operand at npts points of nvar variables ([npts][nvar])
    * @param[in] ccsuby holds concave subgradient values of second operand at npts points of nvar variables ([npts][nvar])
    * @param[in] yL is the lower range bound of second operand
    * @param[in] yU is the upper range bound of second operand
    * @param[in] npts is the number of given linearization points
    * @param[in] op is the given operation
    */
    void compute_additional_linearizations_bivariate_operation
    (double* cvx, double* ccx, double** cvsubx, double** ccsubx, const double xL, const double xU,
     double* cvy, double* ccy, double** cvsuby, double** ccsuby, const double yL, const double yU, const unsigned npts, const OPERATION op)
    {
#ifdef MC__VMCCORMICK_LIN_DEBUG
        if(npts != _npts){
            throw std::runtime_error("mc::vMcCormick_Linearizations\t Error in compute_additional_linearizations_bivariate_operation number of points does not match, "+std::to_string(_npts)+"<>"+std::to_string(npts)+".");
        }
#endif
		_lowerBoundCandidate = -std::numeric_limits<double>::max();
		_upperBoundCandidate =  std::numeric_limits<double>::max();
		unsigned additionalLinsCounter = 0;
		for(unsigned int i = 0; i < _nadditionalLinsBiv; i++){
			_compute_additional_lins_for_bivariate_function(op,cvx,ccx,cvsubx,ccsubx,xL,xU,cvy,ccy,cvsuby,ccsuby,yL,yU,additionalLinsCounter);
		}       
    }
	 
    /**
    * @brief Function returning the convex subgradient at point pt of variable var
    *
    * @param[in] pt is the additional affine relaxation point index
    * @param[in] var is the variable index
    */
    double get_subgradient_cv(unsigned int pt, unsigned int var)
	{
#ifdef MC__VMCCORMICK_LIN_DEBUG
       std::string str = "get_subgradient_cv";
       _check_consistency(str, pt, var);
#endif
        return _cvsub[pt][var];
    }

    /**
    * @brief Function returning the concave subgradient at point pt of variable var
    *
    * @param[in] pt is the additional affine relaxation point index
    * @param[in] var is the variable index
    */
    double get_subgradient_cc(unsigned int pt, unsigned int var)
	{
#ifdef MC__VMCCORMICK_LIN_DEBUG
       std::string str = "get_subgradient_cc";
       _check_consistency(str, pt, var);
#endif
        return _ccsub[pt][var];
    }

    /**
    * @brief Function returning the convex relaxation value at point pt
    *
    * @param[in] pt is the additional affine relaxation point index
    */
    double get_cv(unsigned int pt)
	{
#ifdef MC__VMCCORMICK_LIN_DEBUG
       std::string str = "get_cv";
       _check_consistency(str, pt);
#endif
        return _cv[pt];
    }

    /**
    * @brief Function returning the appropriate linearization point
    *
    * @param[in] pt is the additional affine relaxation point index
    */
    double get_cc(unsigned int pt)
	{
#ifdef MC__VMCCORMICK_LIN_DEBUG
       std::string str = "get_cc";
       _check_consistency(str, pt);
#endif
        return _cc[pt];
    }

    /**
    * @brief Function returning the concave relaxation value at point pt
    *
    * @param[in] pt is the additional affine relaxation point index
    * @param[in] var is the variable index
    */
    double get_lin_point(unsigned int pt, unsigned int var)
	{
#ifdef MC__VMCCORMICK_LIN_DEBUG
       std::string str = "get_lin_point";
       _check_consistency(str, pt, var);
#endif
        return _linPoints[var][pt];
    }

    /**
    * @brief Function returning the number of additional affine relaxations
    */
    double get_nadditionalLins()
	{
        return _nadditionalLins;
    }

    /**
    * @brief Function returning lower bound candidate value (used for subgradient heuristic)
    */
    double get_lower_bound_candidate()
	{
		return _lowerBoundCandidate;
	}
	
    /**
    * @brief Function returning upper bound candidate value (used for subgradient heuristic)
    */	
	double get_upper_bound_candidate()
	{
		return _upperBoundCandidate;
	}

    /**
    * @brief Function for choosing good affine relaxations
    *
    * @param[in,out] cv holds convex relaxation values at npts points
    * @param[in,out] cc holds concave relaxation values at npts points
    * @param[in,out] cvsub holds convex subgradient values at npts points of nvar variables ([npts][nvar])
    * @param[in,out] ccsub holds concave subgradient values at npts points of nvar variables ([npts][nvar])
    */
    void choose_good_linearizations_bivariate(double* cv, double* cc, double** cvsub, double** ccsub,
                                 	std::vector<double>& lowerBoundValues, std::vector<double>& upperBoundValues,
									double &bestLowerValue, double &bestUpperValue, const bool valuesPrecomputed)
    {
		
		if(!valuesPrecomputed){
			//TODO
		}

		
		bestLowerValue = std::max(bestLowerValue, _lowerBoundCandidate);
		bestUpperValue = std::min(bestUpperValue, _upperBoundCandidate);
		reset_candidates();			
		std::unordered_set<double, std::hash<double>, my_double_eq_compare> minValueSet(lowerBoundValues.begin(),lowerBoundValues.end());
		std::unordered_set<double, std::hash<double>, my_double_eq_compare> maxValueSet(upperBoundValues.begin(),upperBoundValues.end());		
#ifdef MC__VMCCORMICK_LIN_DEBUG		
		std::cout << "size of min set: " << minValueSet.size() << " containing:" << std::endl;
		for(auto it = minValueSet.begin(); it != minValueSet.end(); it++){
			std::cout << " " << std::setprecision(16) << *it;
		}
		std::cout << std::endl;		
		std::cout << "size of max set: " << maxValueSet.size() << " containing:" << std::endl;
		for(auto it = maxValueSet.begin(); it != maxValueSet.end(); it++){
			std::cout << " " << std::setprecision(16) << *it;
		}
		std::cout << std::endl;
#endif		
        for(unsigned int i = 0; i<_nadditionalLinsBiv;i++){
			bool cvBetter = _minValues[i] > lowerBoundValues[_originalIndexForBiv[i]];
			bool ccBetter = _maxValues[i] < upperBoundValues[_originalIndexForBiv[i]];
			if(cvBetter){
				if( minValueSet.find(_minValues[i]) != minValueSet.end() ){
#ifdef MC__VMCCORMICK_LIN_DEBUG					
                    std::cout << "inserting affine relaxation with min value " << std::setprecision(16) << _minValues[i] << std::endl;		
#endif					
					minValueSet.insert(_minValues[i]);
					lowerBoundValues[_originalIndexForBiv[i]] = _minValues[i];
					cv[_originalIndexForBiv[i]]= _cv[i];			
					for(unsigned int j = 0; j<_nvar; j++){
						cvsub[_originalIndexForBiv[i]][j] = _cvsub[i][j];
					}
				}
									
			}
			if(ccBetter){
				if( maxValueSet.find(_maxValues[i]) != maxValueSet.end()){ 
#ifdef MC__VMCCORMICK_LIN_DEBUG				
                    std::cout << "inserting affine relaxation with max value " << std::setprecision(16) << _maxValues[i] << std::endl;
#endif					
					upperBoundValues[_originalIndexForBiv[i]] = _maxValues[i];
					cc[_originalIndexForBiv[i]]= _cc[i];
					for(unsigned int j = 0; j<_nvar; j++){
						ccsub[_originalIndexForBiv[i]][j] = _ccsub[i][j];
					}
				}
			}
		}
        
	}
	
	/**
    * @brief Function for choosing good affine relaxations
    *
    * @param[in,out] cv holds convex relaxation values at npts points
    * @param[in,out] cc holds concave relaxation values at npts points
    * @param[in,out] cvsub holds convex subgradient values at npts points of nvar variables ([npts][nvar])
    * @param[in,out] ccsub holds concave subgradient values at npts points of nvar variables ([npts][nvar])
    */
    void choose_good_linearizations_univariate(double* cv, double* cc, double** cvsub, double** ccsub,
                                 	           std::vector<double>& lowerBoundValues, std::vector<double>& upperBoundValues,
									           double &bestLowerValue, double &bestUpperValue, const bool valuesPrecomputed)
    {
		
		if(!valuesPrecomputed){
			//TODO
		}

		// We can safely set it here, since we know that we will improve
		bestLowerValue = -std::numeric_limits<double>::max();
		bestUpperValue =  std::numeric_limits<double>::max();
		_iterate_running_index();
		if(_computeConvexUniv){
		    bestLowerValue = _lowerBoundCandidate;		
			// switch(_strategy_univ){
				 // case AFFINE_RELAXATION_MID_TO_ALL:  case COMPOSITION_MID_TO_ALL: 			    
					// cv[_runningIndexUniv]= _compute_value_of_affine_function(_originalPoints, _cvsub[_bestPointIndexCv].data(), _cv[_bestPointIndexCv], _originalPoints, _midIndex, _runningIndexUniv); 	
					// break;
				 // case COMPOSITION_ALL_TO_MID:  case AFFINE_RELAXATION_ALL_TO_MID:	
					// cv[_runningIndexUniv]= _compute_value_of_affine_function(_originalPoints, _cvsub[_bestPointIndexCv].data(), _cv[_bestPointIndexCv], _originalPoints, _originalIndexForUniv[_bestPointIndexCv], _runningIndexUniv); 
					// break;
				 // case AFFINE_RELAXATION_ALL: case COMPOSITION_ALL:
				 // case COMPOSITION_BEST_POINT:
					// if(_runningIndexUniv != _bestPointIndexCv){
						// cv[_runningIndexUniv]= _compute_value_of_affine_function(_originalPoints, _cvsub[_bestPointIndexCv].data(), _cv[_bestPointIndexCv], _originalPoints, _originalIndexForUniv[_bestPointIndexCv], _runningIndexUniv); 				
					// }
					// else{
						// cv[_runningIndexUniv]= _cv[_bestPointIndexCv];
					// }						
					// break;
			// }			
			// lowerBoundValues[_runningIndexUniv] = _minValues[_bestPointIndexCv];		
			// for(unsigned int j = 0; j<_nvar; j++){
				// cvsub[_runningIndexUniv][j] = _cvsub[_bestPointIndexCv][j];
			// }		
	    }
		
		if(_computeConcaveUniv){
			bestUpperValue = _upperBoundCandidate;
			// switch(_strategy_univ){	 
				 // case AFFINE_RELAXATION_MID_TO_ALL:  case COMPOSITION_MID_TO_ALL: 				    
					// cc[_runningIndexUniv]= _compute_value_of_affine_function(_originalPoints, _ccsub[_bestPointIndexCc].data(), _cc[_bestPointIndexCc], _originalPoints, _midIndex, _runningIndexUniv); 	
					// break;
				 // case COMPOSITION_ALL_TO_MID:  case AFFINE_RELAXATION_ALL_TO_MID:
					// cc[_runningIndexUniv]= _compute_value_of_affine_function(_originalPoints, _ccsub[_bestPointIndexCc].data(), _cc[_bestPointIndexCc], _originalPoints, _originalIndexForUniv[_bestPointIndexCc], _runningIndexUniv);
					// break;
				 // case AFFINE_RELAXATION_ALL: case COMPOSITION_ALL:
				 // case COMPOSITION_BEST_POINT:
					// if(_runningIndexUniv != _bestPointIndexCc){
						// cc[_runningIndexUniv]= _compute_value_of_affine_function(_originalPoints, _ccsub[_bestPointIndexCc].data(), _cc[_bestPointIndexCc], _originalPoints, _originalIndexForUniv[_bestPointIndexCc], _runningIndexUniv);	
					// }
					// else{
						// cc[_runningIndexUniv]= _cc[_bestPointIndexCc];
					// }						
					// break;
			// }
			// upperBoundValues[_runningIndexUniv] = _maxValues[_bestPointIndexCc];
			// for(unsigned int j = 0; j<_nvar; j++){
				// ccsub[_runningIndexUniv][j] = _ccsub[_bestPointIndexCc][j];
			// } 
			
		}
		reset_candidates();
	}
	
private:

    /**
    * @brief Function for the proper computation of additional affine relaxations by using affine relaxations as convex/concave estimators. It sets the indices properly.
    *
    * @param[in] cv holds convex relaxation values at npts points
    * @param[in] cc holds concave relaxation values at npts points
    * @param[in] cvsub holds convex subgradient values at npts points of nvar variables ([npts][nvar])
    * @param[in] ccsub holds concave subgradient values at npts points of nvar variables ([npts][nvar])
    * @param[in] _fcv is the function to compute the convex relaxation value
    * @param[in] _dfcv is the function to compute the convex relaxation derivative value
    * @param[in] _fcc is the function to compute the concave relaxation value
    * @param[in] _dfcc is the function to compute the concave relaxation derivative value
    */
    void _compute_additional_lins_by_using_affine_relaxation_for_univariate_function
    (double* cv, double* cc, double** cvsub, double** ccsub)
    {
        unsigned additionalLinsCounter = 0;
        switch(_strategy_univ){
            case AFFINE_RELAXATION_ALL:
            {
                for(unsigned int i = 0; i<_npts; i++){
                    for(unsigned int j = 0; j<_npts; j++){
                        if(i!=j){
                            _compute_values_affine_relaxation_univariate(cv,cc,cvsub,ccsub,additionalLinsCounter,i,j);
                        }
                    }
                }
                break;
            }// End of AFFINE_RELAXATION_ALL
            case AFFINE_RELAXATION_ALL_TO_MID:
            {
                for(unsigned int i = 0; i<_npts; i++){
                    if(i!=_midIndex){
                        _compute_values_affine_relaxation_univariate(cv,cc,cvsub,ccsub,additionalLinsCounter,i,_midIndex);
                    }
                }
                break;
            }// End of AFFINE_RELAXATION_ALL_TO_MID
            case AFFINE_RELAXATION_MID_TO_ALL:
            {
                for(unsigned int i = 0; i<_npts; i++){
                    if(i!=_midIndex){
                        _compute_values_affine_relaxation_univariate(cv,cc,cvsub,ccsub,additionalLinsCounter,_midIndex,i);
                    }
                }
                break;
            }// End of AFFINE_RELAXATION_ALL_TO_MID
        }
    }

    /**
    * @brief Function for the proper computation of additional affine relaxations by using affine relaxations as convex/concave estimators. It sets the indices properly.
    *
    * @param[in] cv holds convex relaxation values at npts points
    * @param[in] cc holds concave relaxation values at npts points
    * @param[in] cvsub holds convex subgradient values at npts points of nvar variables ([npts][nvar])
    * @param[in] ccsub holds concave subgradient values at npts points of nvar variables ([npts][nvar])
    * @param[in] _fcv is the function to compute the convex relaxation value
    * @param[in] _dfcv is the function to compute the convex relaxation derivative value
    * @param[in] _fcc is the function to compute the concave relaxation value
    * @param[in] _dfcc is the function to compute the concave relaxation derivative value
    * @param[in] xL is the lower range bound of input function
    * @param[in] xU is the upper range bound of input function
    * @param[in] op is the given operation
    */
    void _compute_additional_lins_by_affine_composition_for_univariate_function_with_fixed_points
     (double* cv, double* cc, double** cvsub, double** ccsub,
      const double xL, const double xU, const OPERATION op)
	 {
		 
		double cvLinPoint, ccLinPoint, cvInputValue, ccInputValue;
		VALUE_CHOICE idCv, idCc;
		for(unsigned int i = 0; i<_npts;i++){
			
			_set_evaluation_points_for_univariate_operation(cvLinPoint, ccLinPoint, cvInputValue, ccInputValue, cv, cc, xL, xU, i, idCv, idCc, op);

			_cv[i] = _computeConvexUniv  ? _fcv(cvLinPoint) + _dfcv(cvLinPoint)*(cvInputValue - cvLinPoint) : 0;
			_cc[i] = _computeConcaveUniv ? _fcc(ccLinPoint) + _dfcc(ccLinPoint)*(ccInputValue - ccLinPoint) : 0;
			_set_min_max_values(_cv[i], _cc[i], i);
			for(unsigned int k = 0; k<_nvar; k++){
				double cvSubValue, ccSubValue;
				switch(idCv){
					case CV: cvSubValue = cvsub[i][k]; break;
                    case CC: cvSubValue = ccsub[i][k]; break;
                    case CUT: cvSubValue = cvLinPoint; break;				
				}				
				switch(idCc){
					case CV: ccSubValue = cvsub[i][k]; break;
                    case CC: ccSubValue = ccsub[i][k]; break;
                    case CUT: ccSubValue = ccLinPoint; break;					
				}
				_cvsub[i][k] = _computeConvexUniv  ? _dfcv(cvLinPoint)* cvSubValue : 0;
				_ccsub[i][k] = _computeConcaveUniv ? _dfcc(ccLinPoint)* ccSubValue : 0;
				_linPoints[k][i] = (*_originalPoints)[k][i];
				_add_to_min_max_values(_cvsub[i][k],_ccsub[i][k],i,k);
			}
			_update_candidates(i);
		}
	 }
	 
    /**
    * @brief Function for the proper computation of additional affine relaxations by using affine relaxations as convex/concave estimators. It sets the private variables appriopriately.
    *
    * @param[in] cv holds convex relaxation values at npts points
    * @param[in] cc holds concave relaxation values at npts points
    * @param[in] cvsub holds convex subgradient values at npts points of nvar variables ([npts][nvar])
    * @param[in] ccsub holds concave subgradient values at npts points of nvar variables ([npts][nvar])
    * @param[in] _fcv is the function to compute the convex relaxation value
    * @param[in] _dfcv is the function to compute the convex relaxation derivative value
    * @param[in] _fcc is the function to compute the concave relaxation value
    * @param[in] _dfcc is the function to compute the concave relaxation derivative value
    * @param[in] additionalLinsCounter is the index of additional affine relaxation
    * @param[in] i is the index of reference point at which the affine function has been constructed
    * @param[in] j is the index of reference point at which the affine function shall be evaluated
    */
    void _compute_values_affine_relaxation_univariate(double* cv, double* cc, double** cvsub, double** ccsub,
                                                      unsigned& additionalLinsCounter, const unsigned i, const unsigned j)
    {
        double cvTmp = _computeConvexUniv ? _compute_value_of_affine_function(_originalPoints,cvsub[i],cv[i],_originalPoints, i, j) : 0; // Value of affine relaxation constructed at point [i] evaluated at point [j]
        _cv[additionalLinsCounter] = _computeConvexUniv ? _fcv(cvTmp) : 0;
        double ccTmp = _computeConcaveUniv ? _compute_value_of_affine_function(_originalPoints,ccsub[i],cc[i],_originalPoints, i, j) : 0;
        _cc[additionalLinsCounter] = _computeConcaveUniv ? _fcc(ccTmp) : 0;
		_set_min_max_values(_cv[additionalLinsCounter], _cc[additionalLinsCounter], additionalLinsCounter);
        for(unsigned int k = 0; k<_nvar; k++){
            _cvsub[additionalLinsCounter][k] = _computeConvexUniv  ? _dfcv(cvTmp)*cvsub[i][k] : 0;
            _ccsub[additionalLinsCounter][k] = _computeConcaveUniv ? _dfcc(ccTmp)*ccsub[i][k] : 0;
            _linPoints[k][additionalLinsCounter] = (*_originalPoints)[k][j];
			_add_to_min_max_values(_cvsub[additionalLinsCounter][k],_ccsub[additionalLinsCounter][k],additionalLinsCounter,k);
        }
		_update_candidates(additionalLinsCounter);
        additionalLinsCounter++;
    }

    /**
    * @brief Function for the computation of the value at point x of an affine function with a given slope, constant t and linearization point p
    *
    * @param[in] x is a pointer to a point matrix (nvar x npts) which we want to evaluate at
    * @param[in] slope is an array holding the slopes of each dimension
    * @param[in] t is the affine function constant
    * @param[in] p is a pointer to a point matrix (nvar x npts) which holds the reference points
    * @param[in] indexLinPoint is the index of the reference point at which the given affine function was build at
    * @param[in] indexEvaluateAt is the index of the point at which we want to evaluate the affine function
    */
    double _compute_value_of_affine_function(const std::vector<std::vector<double>>* x, double* slope, const double t,
                                             const std::vector<std::vector<double>>* p, const unsigned indexLinPoint, const unsigned indexEvaluateAt)
    {
        double val = t;
        for(unsigned int i=0;i<_nvar;i++){
            val += slope[i]*((*x)[i][indexEvaluateAt]-(*p)[i][indexLinPoint]);
        }

        return val;
    }

    /**
    * @brief Function for the proper computation of additional affine relaxations by composition of affine functions (AVM style). It sets the indices properly.
    *
    * @param[in] cv holds convex relaxation values at npts points
    * @param[in] cc holds concave relaxation values at npts points
    * @param[in] cvsub holds convex subgradient values at npts points of nvar variables ([npts][nvar])
    * @param[in] ccsub holds concave subgradient values at npts points of nvar variables ([npts][nvar])
    * @param[in] _fcv is the function to compute the convex relaxation value
    * @param[in] _dfcv is the function to compute the convex relaxation derivative value
    * @param[in] _fcc is the function to compute the concave relaxation value
    * @param[in] _dfcc is the function to compute the concave relaxation derivative value
    */
    void _compute_additional_lins_by_affine_composition_for_univariate_function
    (double* cv, double* cc, double** cvsub, double** ccsub)
    {
        unsigned additionalLinsCounter = 0;
        switch(_strategy_univ){
            case COMPOSITION_ALL:
            {
                for(unsigned int i = 0; i < _npts; i++){
                    for(unsigned int j = 0; j < _npts; j++){
                        if(i!=j){
                            _compute_values_composition(cv,cc,cvsub,ccsub,additionalLinsCounter,i,j);
                        }
                    }
                }
                break;
            }// End of AFFINE_RELAXATION_ALL
            case COMPOSITION_ALL_TO_MID:
            {
                for(unsigned int i = 0; i < _npts; i++){
                    if(i!=_midIndex){
                        _compute_values_composition(cv,cc,cvsub,ccsub,additionalLinsCounter,i,_midIndex);
                    }
                }
                break;
            }// End of AFFINE_RELAXATION_ALL_TO_MID
            case COMPOSITION_MID_TO_ALL:
            {				
                for(unsigned int i = 0; i < _npts; i++){
                    if(i!=_midIndex){
                        _compute_values_composition(cv,cc,cvsub,ccsub,additionalLinsCounter,_midIndex,i);
                    }
                }
                break;
            }// End of AFFINE_RELAXATION_ALL_TO_MID
        }
    }

    /**
    * @brief Function for the proper computation of additional affine relaxations by using by composition of affine functions (AVM style). It sets the private variables appriopriately.
    *
    * @param[in] cv holds convex relaxation values at npts points
    * @param[in] cc holds concave relaxation values at npts points
    * @param[in] cvsub holds convex subgradient values at npts points of nvar variables ([npts][nvar])
    * @param[in] ccsub holds concave subgradient values at npts points of nvar variables ([npts][nvar])
    * @param[in] _fcv is the function to compute the convex relaxation value
    * @param[in] _dfcv is the function to compute the convex relaxation derivative value
    * @param[in] _fcc is the function to compute the concave relaxation value
    * @param[in] _dfcc is the function to compute the concave relaxation derivative value
    * @param[in] additionalLinsCounter is the index of additional affine relaxation
    * @param[in] i is the index of reference point at which the affine function has been constructed
    * @param[in] j is the index of reference point at which the affine function shall be evaluated
    */
    void _compute_values_composition(double* cv, double* cc, double** cvsub, double** ccsub,
                                     unsigned& additionalLinsCounter, const unsigned i, const unsigned j)
    {
		
        _cv[additionalLinsCounter] = _computeConvexUniv  ? _compute_fixed_value_of_affine_composition(cv, _fcv, _dfcv, i, j) : 0;
        _cc[additionalLinsCounter] = _computeConcaveUniv ? _compute_fixed_value_of_affine_composition(cc, _fcc, _dfcc, i, j) : 0;
		_set_min_max_values(_cv[additionalLinsCounter], _cc[additionalLinsCounter], additionalLinsCounter);
        for(unsigned int k=0; k<_nvar; k++){
            _cvsub[additionalLinsCounter][k] = _computeConvexUniv  ? _dfcv(cv[j])*cvsub[i][k] : 0;
            _ccsub[additionalLinsCounter][k] = _computeConcaveUniv ? _dfcc(cc[j])*ccsub[i][k] : 0;
            _linPoints[k][additionalLinsCounter] = (*_originalPoints)[k][i];
			_add_to_min_max_values(_cvsub[additionalLinsCounter][k],_ccsub[additionalLinsCounter][k],additionalLinsCounter,k);
        }
		_update_candidates(additionalLinsCounter);
        additionalLinsCounter++;
    }

    /**
    * @brief Function for the computation of the value at point x of an affine function with a given slope, constant t and linearization point p
    *
    * @param[in] f are the values of the inner convex/concave function f
    * @param[in] G is the outer convex/concave composition function
    * @param[in] dG is the derivative of G
    * @param[in] pointThis is the index of the reference point at which the given affine function was build at
    * @param[in] pointOther is the index of the point at which we want to compose
    */
    double _compute_fixed_value_of_affine_composition(double* f, const std::function<double(double)> G, const std::function<double(double)> dG,
                                                      const unsigned pointThis, const unsigned pointOther)
    {
        return G(f[pointOther]) - f[pointOther]*dG(f[pointOther]) + dG(f[pointOther])*f[pointThis];
    }

    /**
    * @brief Function for properly computing and propagating additional affine relaxations for bivariate operations
    *
    * @param[in] cvx holds convex relaxation values of first operand at npts points
    * @param[in] ccx holds concave relaxation values of first operand at npts points
    * @param[in] cvsubx holds convex subgradient values of first operand at npts points of nvar variables ([npts][nvar])
    * @param[in] ccsubx holds concave subgradient values of first operand at npts points of nvar variables ([npts][nvar])
    * @param[in] xL is the lower range bound of first operand 
    * @param[in] xU is the upper range bound of first operand 
    * @param[in] cvy holds convex relaxation values of second operand at npts points
    * @param[in] ccy holds concave relaxation values of second operand at npts points
    * @param[in] cvsuby holds convex subgradient values of second operand at npts points of nvar variables ([npts][nvar])
    * @param[in] ccsuby holds concave subgradient values of second operand at npts points of nvar variables ([npts][nvar])
    * @param[in] yL is the lower range bound of second operand
    * @param[in] yU is the upper range bound of second operand
    */
    void _compute_additional_lins_for_bivariate_function
    (const OPERATION op, double* cvx, double* ccx, double** cvsubx, double** ccsubx, const double xL, const double xU,
                         double* cvy, double* ccy, double** cvsuby, double** ccsuby, const double yL, const double yU,
                         unsigned& additionalLinsCounter)
	 {	
        switch(op){
           case MINUS: 
				_compute_values_affine_relaxation_subtraction(cvx,ccx,cvsubx,ccsubx,cvy,ccy,cvsuby,ccsuby,additionalLinsCounter);
				break;
			case PLUS: 
				_compute_values_affine_relaxation_addition(cvx,ccx,cvsubx,ccsubx,cvy,ccy,cvsuby,ccsuby,additionalLinsCounter);
				break;	
            default:
                break;
        }
	 }

    /**
    * @brief Function for the proper computation of additional affine relaxations for subtraction.
    *
    * @param[in] cvx holds convex relaxation values of first operand at npts points
    * @param[in] ccx holds concave relaxation values of first operand at npts points
    * @param[in] cvsubx holds convex subgradient values of first operand at npts points of nvar variables ([npts][nvar])
    * @param[in] ccsubx holds concave subgradient values of first operand at npts points of nvar variables ([npts][nvar])
    * @param[in] xL is the lower range bound of first operand 
    * @param[in] xU is the upper range bound of first operand 
    * @param[in] cvy holds convex relaxation values of second operand at npts points
    * @param[in] ccy holds concave relaxation values of second operand at npts points
    * @param[in] cvsuby holds convex subgradient values of second operand at npts points of nvar variables ([npts][nvar])
    * @param[in] ccsuby holds concave subgradient values of second operand at npts points of nvar variables ([npts][nvar])
    * @param[in] yL is the lower range bound of second operand
    * @param[in] yU is the upper range bound of second operand
    * @param[in] additionalLinsCounter is the index of additional affine relaxation
    * @param[in] i is the index of reference point at which the affine function has been constructed
    * @param[in] j is the index of reference point at which the affine function shall be evaluated
    */
    void _compute_values_affine_relaxation_subtraction(double* cvx, double* ccx, double** cvsubx, double** ccsubx,
                                                       double* cvy, double* ccy, double** cvsuby, double** ccsuby,
                                                       unsigned& additionalLinsCounter)
    {
		double cvTmpx, cvTmpy, ccTmpx, ccTmpy;
		if(_useLeftFactorLinPoint[additionalLinsCounter]){
			cvTmpx = cvx[_index1[additionalLinsCounter]];
			ccTmpx = ccx[_index1[additionalLinsCounter]];
			// Value of affine relaxation constructed at point _index2 and evaluated at _index1
			cvTmpy = _compute_value_of_affine_function(_originalPoints,cvsuby[_index2[additionalLinsCounter]],cvy[_index2[additionalLinsCounter]],
			                                           _originalPoints, _index2[additionalLinsCounter], _index1[additionalLinsCounter]);
			ccTmpy = _compute_value_of_affine_function(_originalPoints,ccsuby[_index2[additionalLinsCounter]],ccy[_index2[additionalLinsCounter]],
			                                           _originalPoints, _index2[additionalLinsCounter], _index1[additionalLinsCounter]);
		}
		else{
			cvTmpx = _compute_value_of_affine_function(_originalPoints,cvsubx[_index1[additionalLinsCounter]],cvx[_index1[additionalLinsCounter]],
			                                           _originalPoints, _index1[additionalLinsCounter], _index2[additionalLinsCounter]);
			ccTmpx = _compute_value_of_affine_function(_originalPoints,ccsubx[_index1[additionalLinsCounter]],ccx[_index1[additionalLinsCounter]],
			                                           _originalPoints, _index1[additionalLinsCounter], _index2[additionalLinsCounter]);
			// Value of affine relaxation constructed at point _index2 and evaluated at _index1
			cvTmpy = cvy[_index2[additionalLinsCounter]];
			ccTmpy = ccy[_index2[additionalLinsCounter]];
		}
		
		_cv[additionalLinsCounter] = cvTmpx-ccTmpy;
        _cc[additionalLinsCounter] = ccTmpx-cvTmpy;
		_set_min_max_values(_cv[additionalLinsCounter], _cc[additionalLinsCounter], additionalLinsCounter);
        for(unsigned int k = 0; k<_nvar; k++){
            _cvsub[additionalLinsCounter][k] = cvsubx[_index1[additionalLinsCounter]][k] - ccsuby[_index2[additionalLinsCounter]][k];
            _ccsub[additionalLinsCounter][k] = ccsubx[_index1[additionalLinsCounter]][k] - cvsuby[_index2[additionalLinsCounter]][k];
            _linPoints[k][additionalLinsCounter] = (*_originalPoints)[k][_originalIndexForBiv[additionalLinsCounter]];
			_add_to_min_max_values(_cvsub[additionalLinsCounter][k],_ccsub[additionalLinsCounter][k],additionalLinsCounter,k);
        }
		_update_candidates(additionalLinsCounter);
        additionalLinsCounter++;
    }
	
	/**
    * @brief Function for the proper computation of additional affine relaxations for addition.
    *
    * @param[in] cvx holds convex relaxation values of first operand at npts points
    * @param[in] ccx holds concave relaxation values of first operand at npts points
    * @param[in] cvsubx holds convex subgradient values of first operand at npts points of nvar variables ([npts][nvar])
    * @param[in] ccsubx holds concave subgradient values of first operand at npts points of nvar variables ([npts][nvar])
    * @param[in] xL is the lower range bound of first operand 
    * @param[in] xU is the upper range bound of first operand 
    * @param[in] cvy holds convex relaxation values of second operand at npts points
    * @param[in] ccy holds concave relaxation values of second operand at npts points
    * @param[in] cvsuby holds convex subgradient values of second operand at npts points of nvar variables ([npts][nvar])
    * @param[in] ccsuby holds concave subgradient values of second operand at npts points of nvar variables ([npts][nvar])
    * @param[in] yL is the lower range bound of second operand
    * @param[in] yU is the upper range bound of second operand
    * @param[in] additionalLinsCounter is the index of additional affine relaxation
    */
    void _compute_values_affine_relaxation_addition(double* cvx, double* ccx, double** cvsubx, double** ccsubx,
                                                    double* cvy, double* ccy, double** cvsuby, double** ccsuby,
                                                    unsigned& additionalLinsCounter)
    {
		double cvTmpx, cvTmpy, ccTmpx, ccTmpy;
		if(_useLeftFactorLinPoint[additionalLinsCounter]){
			cvTmpx = cvx[_index1[additionalLinsCounter]];
			ccTmpx = ccx[_index1[additionalLinsCounter]];
			// Value of affine relaxation constructed at point _index2 and evaluated at _index1
			cvTmpy = _compute_value_of_affine_function(_originalPoints,cvsuby[_index2[additionalLinsCounter]],cvy[_index2[additionalLinsCounter]],
			                                           _originalPoints, _index2[additionalLinsCounter], _index1[additionalLinsCounter]);
			ccTmpy = _compute_value_of_affine_function(_originalPoints,ccsuby[_index2[additionalLinsCounter]],ccy[_index2[additionalLinsCounter]],
			                                           _originalPoints, _index2[additionalLinsCounter], _index1[additionalLinsCounter]);
		}
		else{
			cvTmpx = _compute_value_of_affine_function(_originalPoints,cvsubx[_index1[additionalLinsCounter]],cvx[_index1[additionalLinsCounter]],
			                                           _originalPoints, _index1[additionalLinsCounter], _index2[additionalLinsCounter]);
			ccTmpx = _compute_value_of_affine_function(_originalPoints,ccsubx[_index1[additionalLinsCounter]],ccx[_index1[additionalLinsCounter]],
			                                           _originalPoints, _index1[additionalLinsCounter], _index2[additionalLinsCounter]);
			// Value of affine relaxation constructed at point _index2 and evaluated at _index1
			cvTmpy = cvy[_index2[additionalLinsCounter]];
			ccTmpy = ccy[_index2[additionalLinsCounter]];
		}
		
		_cv[additionalLinsCounter] = cvTmpx+cvTmpy;
        _cc[additionalLinsCounter] = ccTmpx+ccTmpy;
		_set_min_max_values(_cv[additionalLinsCounter], _cc[additionalLinsCounter], additionalLinsCounter);
        for(unsigned int k = 0; k<_nvar; k++){
            _cvsub[additionalLinsCounter][k] = cvsubx[_index1[additionalLinsCounter]][k] + cvsuby[_index2[additionalLinsCounter]][k];
            _ccsub[additionalLinsCounter][k] = ccsubx[_index1[additionalLinsCounter]][k] + ccsuby[_index2[additionalLinsCounter]][k];
            _linPoints[k][additionalLinsCounter] = (*_originalPoints)[k][_originalIndexForBiv[additionalLinsCounter]];
			_add_to_min_max_values(_cvsub[additionalLinsCounter][k],_ccsub[additionalLinsCounter][k],additionalLinsCounter,k);
        }
		_update_candidates(additionalLinsCounter);
        additionalLinsCounter++;
    }

	/**
    * @brief Function for setting min and max values
    *
    * @param[in] cv holds convex relaxation value
    * @param[in] cc holds concave relaxation value
    * @param[in] additionalLinsCounter is the index of additional affine relaxation
    */
    void _set_min_max_values(const double cv, const double cc, unsigned int additionalLinsCounter){
		_minValues[additionalLinsCounter] = cv;
		_maxValues[additionalLinsCounter] = cc;
	}

	/**
    * @brief Function adding to min and max values
    *
    * @param[in] cvsub holds convex relaxation subgradient value
    * @param[in] ccsub holds concave relaxation subgradient value
    * @param[in] additionalLinsCounter is the index of additional affine relaxation
    * @param[in] var is the variable index
    */	
	void _add_to_min_max_values(const double cvsub, const double ccsub, unsigned int additionalLinsCounter, unsigned int var){
		double p = cvsub>0 ? (*_originalLowerBounds)[var] : (*_originalUpperBounds)[var];
		_minValues[additionalLinsCounter] += cvsub*(p-_linPoints[var][additionalLinsCounter] ) ;
		p = ccsub>0 ? (*_originalUpperBounds)[var] : (*_originalLowerBounds)[var];
		_maxValues[additionalLinsCounter] += ccsub*(p-_linPoints[var][additionalLinsCounter] );
	}
	
	/**
    * @brief Function for the updating of candidates
    *
    * @param[in] additionalLinsCounter is the index of additional affine relaxation
    */		
	void _update_candidates(unsigned int additionalLinsCounter){
		if(_lowerBoundCandidate <= _minValues[additionalLinsCounter]){
			_lowerBoundCandidate = _minValues[additionalLinsCounter];
			_bestPointIndexCv = additionalLinsCounter;
		}
		if(_upperBoundCandidate >= _maxValues[additionalLinsCounter]){
			_upperBoundCandidate = _maxValues[additionalLinsCounter];
			_bestPointIndexCc = additionalLinsCounter;
		}		
	}

    void _set_functions_for_univariate_operation(const double xL, const double xU, const OPERATION op)
	 {
		 switch(op){
            case EXP:
            { // convex increasing
                _fcv = static_cast<double(*)(double)>(std::exp);
                _dfcv = static_cast<double(*)(double)>(std::exp);
                // double r = 0.;
                // if( !mc::isequal( xL, xU )){
                  // r = ( std::exp( xU ) - std::exp( xL ) ) / ( xU - xL );
                // }
                // _fcc = [r, xU](double x){ return std::exp(xU) + r*(x-xU);};
                // _dfcc = [r](double x){return r;};
				_computeConvexUniv = true; _computeConcaveUniv = false;
                break;
            }
			case LOG:
			{ // concave increasing
				// double r = 0.;
                // if( !mc::isequal( xL, xU )){
                  // r = ( std::log( xU ) - std::log( xL ) ) / ( xU - xL );
                // }
				// _fcv =  [r,xL](double x){ return std::log(xL)+r*(x-xL);};
				// _dfcv = [r](double x){ return r;};
				_fcc =  static_cast<double(*)(double)>(std::log);
				_dfcc = [](double x){ return 1./x;};
				_computeConvexUniv = false; _computeConcaveUniv = true;
				break;
			}
			case INV:
			{
				if(xL>0){ // convex
					_fcv =  [](double x){ return 1./x;};
					_dfcv = [](double x){ return -1./std::pow(x,2);};
					// _fcc =  [xL,xU](double x){ return 1./xL + 1./xU -x/(xL*xU);};
					// _dfcc = [xL,xU](double x){ return -1./(xL*xU);};
				    _computeConvexUniv = true; _computeConcaveUniv = false;	
				}
				else{ // concave				
					// _fcv =  [xL,xU](double x){ return 1./xL + 1./xU -x/(xL*xU);};
					// _dfcv = [xL,xU](double x){ return -1./(xL*xU);};
					_fcc =  [](double x){ return 1./x;};
					_dfcc = [](double x){ return -1./std::pow(x,2);};
				    _computeConvexUniv = false; _computeConcaveUniv = true;	
				}
				break;
			}
			case SQR:
			{ // convex
				_fcv =  [](double x){ return std::pow(x,2);};
				_dfcv = [](double x){ return 2*x;};
				// double r = 0.;
				// double pt = xL;
                // if( !mc::isequal( xL, xU )){
                  // r = ( std::pow(xU,2) - std::pow(xL,2) ) / ( xU - xL );
				  // pt = std::pow(xL,2) > std::pow(xU,2) ? xL : xU;
                // }
				// _fcc =  [r,pt](double x){ return std::pow(pt,2) + r*(x-pt);};
				// _dfcc = [r](double x){ return r;};
				_computeConvexUniv = true; _computeConcaveUniv = false;	
				break;
			}
			case ARH:
			{
				double k = (*_additionalValuesDouble);
				// double r = 0.;
				// if( !mc::isequal( xL, xU )){
				  // r = ( mc::arh(xU,k) - mc::arh(xL,k) ) / ( xU - xL );
				// }
				if(xU<= 0.5* k){ // convex, increasing
					_fcv =  [k](double x){ return std::exp( -k / x);};
					_dfcv = [k](double x){ return k/std::pow(x,2) * std::exp( -k / x);};				
					// _fcc =  [r,xU,k](double x){ return mc::arh(xU,k) + r*(x-xU);};
					// _dfcc = [r](double x){ return r;};
					_computeConvexUniv = true; _computeConcaveUniv = false;
				}
				else if(xL >= 0.5* k){ // concave increasing			
					// _fcv =  [r,xL,k](double x){ return mc::arh(xL,k) + r*(x-xL);};
					// _dfcv = [r](double x){ return r;};			
					_fcc =  [k](double x){ return std::exp( -k / x);};
					_dfcc = [k](double x){ return k/std::pow(x,2) * std::exp( -k / x);};
					_computeConvexUniv = false; _computeConcaveUniv = true;
				}
				break;
			}
            case XLOG:		
			{ // convex
				_fcv =  [](double x){ return x*std::log(x);};
				_dfcv = [](double x){ return std::log(x)+1;};
				// double r = 0.;
				// double pt = xL*std::log(xL) > xU*std::log(xU) ? xL : xU;
                // if( !mc::isequal( xL, xU )){
					// r = ( xU*std::log(xU) - xL*std::log(xL) ) / ( xU - xL);
					// pt = xL;
                // }
				// _fcc =  [r,pt](double x){ return pt*std::log(pt) + r*(x-pt);};
				// _dfcc = [r](double x){ return r;};
				_computeConvexUniv = true; _computeConcaveUniv = false;	
				break;
			}
			case XEXPAX:
			{
				double a = (*_additionalValuesDouble);
				int currentCase = (*_additionalValuesInt);
				if(a>0){
					switch(currentCase){
						case 0: // convex (not necessarily monotonic						
						    _fcv = [a](double x){ return x*std::exp(a*x);};
							_dfcv = [a](double x){ return std::exp(a*x)*(1+a*x);};
							// _fcc = [a,r,pt](double x){ return pt*std::exp(a*pt) + r*(x-pt);};
							// _dfcc = [r](double x){ return r;};
							_computeConvexUniv = true; _computeConcaveUniv = false;	
							break;
						case 1: // concave decreasing
						    // _fcv = [a,xU,r](double x){ return xU*std::exp(xU*a) + r*(x-xU);};
							// _dfcv = [r](double x){ return r;};
							_fcc = [a](double x){ return x*std::exp(x*a);};
							_dfcc = [a](double x){ return std::exp(a*x)*(1+a*x);};
							_computeConvexUniv = false; _computeConcaveUniv = true;	
						    break;
						default: // convex-concave	
						    if(_strategy_univ != COMPOSITION_BEST_POINT){							
				                _computeConvexUniv = false; _computeConcaveUniv = false;
								break;
							}
							else{
								_computeConvexUniv = currentCase == 4 || currentCase == 5;
								_computeConcaveUniv = currentCase == 4 || currentCase == 6;
							}
                            _fcv = [a](double x){ return x*std::exp(a*x);};
							_dfcv = [a](double x){ return std::exp(a*x)*(1+a*x);};
							_fcc = [a](double x){ return x*std::exp(a*x);};
							_dfcc = [a](double x){ return std::exp(a*x)*(1+a*x);};
                            break;													
				            // throw std::runtime_error("mc::vMcCormick_Linearizations\t Error in _set_functions_for_univariate_operation, unknown case in xexpax "+std::to_string(currentCase)+".");					   
					}
				}
				else{
					switch(currentCase){
						case 0: // concave (not necessarily monotonic)
						    // _fcv = [a,pt,r](double x){ return pt*std::exp(pt*a) + r*(x-pt);};
							// _dfcv = [r](double x){ return r;};
							_fcc = [a](double x){ return x*std::exp(x*a);};
							_dfcc = [a](double x){ return std::exp(a*x)*(1+a*x);};
							_computeConvexUniv = false; _computeConcaveUniv = true;	
							break;
						case 1: // convex and monotonically decreasing
						    _fcv = [a](double x){ return x*std::exp(a*x);};
							_dfcv = [a](double x){ return std::exp(a*x)*(1+a*x);};
							// _fcc = [a,r,xL](double x){ return xL*std::exp(a*xL) + r*(x-xL);};
							// _dfcc = [r](double x){ return r;};
							_computeConvexUniv = true; _computeConcaveUniv = false;	
						    break;
						default: // convex-concave 
				            if(_strategy_univ != COMPOSITION_BEST_POINT){							
				                _computeConvexUniv = false; _computeConcaveUniv = false;
								break;
							}
							else{
								_computeConvexUniv = currentCase == 4 || currentCase == 5;
								_computeConcaveUniv = currentCase == 4 || currentCase == 6;
							}
                            _fcv = [a](double x){ return x*std::exp(a*x);};
							_dfcv = [a](double x){ return std::exp(a*x)*(1+a*x);};
							_fcc = [a](double x){ return x*std::exp(a*x);};
							_dfcc = [a](double x){ return std::exp(a*x)*(1+a*x);};
                            break;								
				            // throw std::runtime_error("mc::vMcCormick_Linearizations\t Error in _set_functions_for_univariate_operation, unknown case in xexpax "+std::to_string(currentCase)+".");					   
					}					
				}
				break;
			}
			case VAPOR_PRESSURE:
			{ // convex increasing
				double type = _additionalValuesDouble[0]; double p1 = _additionalValuesDouble[1];  double p2  = _additionalValuesDouble[2];  double p3 = _additionalValuesDouble[3]; 
				double p4 = _additionalValuesDouble[4];   double p5 = _additionalValuesDouble[5];  double p6  = _additionalValuesDouble[6];  double p7 = _additionalValuesDouble[7]; 
				double p8 = _additionalValuesDouble[8];   double p9 = _additionalValuesDouble[9];  double p10 = _additionalValuesDouble[10]; 
				_fcv = [type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10](double x){ return mc::vapor_pressure(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10);}; 
				_dfcv = [type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10](double x){ return mc::der_vapor_pressure(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10);}; 		
				_computeConvexUniv = true; _computeConcaveUniv = false;
				break;
			}
			case IDEAL_GAS_ENTHALPY:
			{ // convex increasing
				double type = _additionalValuesDouble[0]; double p1 = _additionalValuesDouble[1];  double p2  = _additionalValuesDouble[2];  double p3 = _additionalValuesDouble[3]; 
				double p4 = _additionalValuesDouble[4];   double p5 = _additionalValuesDouble[5];  double p6  = _additionalValuesDouble[6];  double p7 = _additionalValuesDouble[7]; 
				_fcv = [type,p1,p2,p3,p4,p5,p6,p7](double x){ return mc::ideal_gas_enthalpy(x,type,p1,p2,p3,p4,p5,p6,p7);}; 
				_dfcv = [type,p1,p2,p3,p4,p5,p6,p7](double x){ return mc::der_ideal_gas_enthalpy(x,type,p1,p2,p3,p4,p5,p6,p7);}; 		
				_computeConvexUniv = true; _computeConcaveUniv = false;
				break;
			}
			case SATURATION_TEMPERATURE:
			{ // concave increasing		
				double type = _additionalValuesDouble[0]; double p1 = _additionalValuesDouble[1];  double p2  = _additionalValuesDouble[2];  double p3 = _additionalValuesDouble[3]; 
				double p4 = _additionalValuesDouble[4];   double p5 = _additionalValuesDouble[5];  double p6  = _additionalValuesDouble[6];  double p7 = _additionalValuesDouble[7]; 
				double p8 = _additionalValuesDouble[8];   double p9 = _additionalValuesDouble[9];  double p10 = _additionalValuesDouble[10]; 
				_fcc = [type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10](double x){ return mc::saturation_temperature(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10);}; 
				_dfcc = [type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10](double x){ return mc::der_saturation_temperature(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10);}; 		
				_computeConvexUniv = false; _computeConcaveUniv = true;
				break;
			}
			case ENTHALPY_OF_VAPORIZATION:
			{ // concave decreasing				
				double type = _additionalValuesDouble[0]; double p1 = _additionalValuesDouble[1];  double p2  = _additionalValuesDouble[2];  double p3 = _additionalValuesDouble[3]; 
				double p4 = _additionalValuesDouble[4];   double p5 = _additionalValuesDouble[5];  double p6  = _additionalValuesDouble[6];
				_fcc = [type,p1,p2,p3,p4,p5,p6](double x){ return mc::enthalpy_of_vaporization(x,type,p1,p2,p3,p4,p5,p6);}; 
				_dfcc = [type,p1,p2,p3,p4,p5,p6](double x){ return mc::der_enthalpy_of_vaporization(x,type,p1,p2,p3,p4,p5,p6);}; 		
				_computeConvexUniv = false; _computeConcaveUniv = true;
				break;
			}
			case COST_FUNCTION:
			{
				int givenCase = (*_additionalValuesInt);
				double type = _additionalValuesDouble[0]; double p1 = _additionalValuesDouble[1];  double p2  = _additionalValuesDouble[2];  double p3 = _additionalValuesDouble[3]; 
				switch(givenCase){
					case 0: case 2: case 4: // convex 
					{
						_fcv = [type,p1,p2,p3](double x){ return mc::cost_function(x,type,p1,p2,p3);}; 
						_dfcv = [type,p1,p2,p3](double x){ return mc::der_cost_function(x,type,p1,p2,p3);}; 		
						_computeConvexUniv = true; _computeConcaveUniv = false;
						break;
					}
					case 1: case 3: case 5: // concave				
					{
						_fcc = [type,p1,p2,p3](double x){ return mc::cost_function(x,type,p1,p2,p3);}; 
						_dfcc = [type,p1,p2,p3](double x){ return mc::der_cost_function(x,type,p1,p2,p3);}; 		
						_computeConvexUniv = false; _computeConcaveUniv = true;
						break;
					}
					default:				        
						throw std::runtime_error("mc::vMcCormick_Linearizations\t Error in _set_functions_for_univariate_operation, unknown case of cost_function "+std::to_string(givenCase)+".");
				}
				break;
			}
			case NRTL_TAU:
			{
				int givenCase = (*_additionalValuesInt);
				double a = _additionalValuesDouble[0]; double b = _additionalValuesDouble[1];  double e  = _additionalValuesDouble[2];  double f = _additionalValuesDouble[3]; 
				switch(givenCase){
					case 0: case 2: case 4: // convex 
					{
						_fcv = [a,b,e,f](double x){ return mc::nrtl_tau(x,a,b,e,f);}; 
						_dfcv = [b,e,f](double x){ return mc::nrtl_dtau(x,b,e,f);}; 		
						_computeConvexUniv = true; _computeConcaveUniv = false;
						break;
					}
					case 1: case 3: case 5: // concave				
					{
						_fcc = [a,b,e,f](double x){ return mc::nrtl_tau(x,a,b,e,f);}; 
						_dfcc = [b,e,f](double x){ return mc::nrtl_dtau(x,b,e,f);}; 		
						_computeConvexUniv = false; _computeConcaveUniv = true;
						break;
					}
					default:				        
						throw std::runtime_error("mc::vMcCormick_Linearizations\t Error in _set_functions_for_univariate_operation, unknown case of nrtl_tau "+std::to_string(givenCase)+".");
				}
				break;
			}			
			case NRTL_DTAU:
			{
				int givenCase = (*_additionalValuesInt);
				double b = _additionalValuesDouble[0]; double e = _additionalValuesDouble[1];  double f  = _additionalValuesDouble[2];
				switch(givenCase){
					case 0: case 2: case 4: // convex 
					{
						_fcv = [b,e,f](double x){ return mc::nrtl_dtau(x,b,e,f);}; 
						_dfcv = [b,e](double x){ return mc::der2_nrtl_tau(x,b,e);}; 		
						_computeConvexUniv = true; _computeConcaveUniv = false;
						break;
					}
					case 1: case 3: case 5: // concave				
					{
						_fcc = [b,e,f](double x){ return mc::nrtl_dtau(x,b,e,f);}; 
						_dfcc = [b,e](double x){ return mc::der2_nrtl_tau(x,b,e);}; 		
						_computeConvexUniv = false; _computeConcaveUniv = true;
						break;
					}
					default:				        
						throw std::runtime_error("mc::vMcCormick_Linearizations\t Error in _set_functions_for_univariate_operation, unknown case of nrtl_dtau "+std::to_string(givenCase)+".");
				}
				break;
			}
			case P_SAT_ETHANOL_SCHROEDER:
			{ // convex increasing
				_fcv = [](double x){ return mc::p_sat_ethanol_schroeder(x);}; 
				_dfcv = [](double x){ return mc::der_p_sat_ethanol_schroeder(x);}; 		
				_computeConvexUniv = true; _computeConcaveUniv = false;
				break;
			}
			case RHO_VAP_SAT_ETHANOL_SCHROEDER:
			{ // convex increasing
				_fcv = [](double x){ return mc::rho_vap_sat_ethanol_schroeder(x);}; 
				_dfcv = [](double x){ return mc::der_rho_vap_sat_ethanol_schroeder(x);}; 		
				_computeConvexUniv = true; _computeConcaveUniv = false;
				break;
			}
			case RHO_LIQ_SAT_ETHANOL_SCHROEDER:
			{ // concave decreasing
				_fcv = [](double x){ return mc::rho_liq_sat_ethanol_schroeder(x);}; 
				_dfcv = [](double x){ return mc::der_rho_liq_sat_ethanol_schroeder(x);}; 		
				_computeConvexUniv = false; _computeConcaveUniv = true;
				break;
			}
			case SQRT:
			{ // concave increasing			
				_fcc =  static_cast<double(*)(double)>(std::sqrt);
				_dfcc = [](double x){ return 1./(2*std::sqrt(x));};
				_computeConvexUniv = false; _computeConcaveUniv = true;
				break;
			}
			case NPOW:
			{
				int n = (*_additionalValuesInt);
				if(!(n%2)){ // even exponent
					_fcv = [n](double x){ return std::pow(x,n);}; 
					_dfcv = [n](double x){ return n*std::pow(x,n-1);}; 		
					_computeConvexUniv = true; _computeConcaveUniv = false;	
				}
				else{ // odd exponent
					_computeConvexUniv = false; _computeConcaveUniv = false;					  
					if(xL >= 0){ // convex
						_fcv = [n](double x){ return std::pow(x,n);}; 
						_dfcv = [n](double x){ return n*std::pow(x,n-1);}; 		
						_computeConvexUniv = true;					
					}
					if(xU <= 0){ // concave
						_fcc = [n](double x){ return std::pow(x,n);}; 
						_dfcc = [n](double x){ return n*std::pow(x,n-1);}; 		
						_computeConcaveUniv = true;	
					}
				}
			    break;
			}
			case DPOW:
			{
				double a = (*_additionalValuesDouble);
				_computeConvexUniv = false; _computeConcaveUniv = false;
				if(a > 1){ // convex
					_fcv = [a](double x){ return std::pow(x,a);}; 
					_dfcv = [a](double x){ return a*std::pow(x,a-1);};	
					_computeConvexUniv = true;	
				}
				if(a<1){ // concave
					_fcc = [a](double x){ return std::pow(x,a);}; 
					_dfcc = [a](double x){ return a*std::pow(x,a-1);}; 		
					_computeConcaveUniv = true;		
				}	
                break;					
			}
			case FABS:
			{ // convex
				_fcv = static_cast<double(*)(double)>(std::fabs);
				_dfcv = [](double x){ if(x>0){ return 1;} else if (x<0) {return -1;} else{ return 0;}};	
				_computeConvexUniv = true; _computeConcaveUniv = false;	
				break;
			}
			case TANH:
			{				
				_computeConvexUniv = false; _computeConcaveUniv = false;
				if(xL>=0){ // concave increasing
					_computeConcaveUniv = true;
					_fcc = static_cast<double(*)(double)>(std::tanh);
					_dfcc = [](double x){ return 1-std::pow(std::tanh(x),2);};
					break;
				}
				if(xU<=0){ // convex increasing
					_computeConvexUniv = true;
					_fcv = static_cast<double(*)(double)>(std::tanh);
					_dfcv = [](double x){ return 1-std::pow(std::tanh(x),2);};
					break;
				}
				// We check if the solution point of the equation (1-tanh(x)^2) = (tanh(x)-tanh(xU))/(x-xU) is within the given interval 
				// We do it by a simple sign check at lower(upper) bound and 0
				if(mc::sign((1-std::pow(std::tanh(xL),2)) - (std::tanh(xL)-std::tanh(xU))/(xL-xU)) != mc::sign(1 - (std::tanh(xU))/(xU))){
					// Connection point for the convex relaxation is in the interval
					_computeConvexUniv = true;
					_fcv = static_cast<double(*)(double)>(std::tanh);
					_dfcv = [](double x){ return 1-std::pow(std::tanh(x),2);};
				}			
				if(mc::sign((1-std::pow(std::tanh(xU),2)) - (std::tanh(xU)-std::tanh(xL))/(xU-xL)) != mc::sign(1 - (std::tanh(xL))/(xL))){
					// Connection point for the concave relaxation is in the interval
					_computeConcaveUniv = true;
					_fcc = static_cast<double(*)(double)>(std::tanh);
					_dfcc = [](double x){ return 1-std::pow(std::tanh(x),2);};
				}
				break;
			}
			case COSH:
			{ // convex
                _fcv =  static_cast<double(*)(double)>(std::cosh);
				_dfcv = [](double x){ return std::sinh(x);};
				// double r = 0.;
				// double pt = xL;
                // if( !mc::isequal( xL, xU )){
                  // r = ( std::pow(xU,2) - std::pow(xL,2) ) / ( xU - xL );
				  // pt = std::pow(xL,2) > std::pow(xU,2) ? xL : xU;
                // }
				// _fcc =  [r,pt](double x){ return std::pow(pt,2) + r*(x-pt);};
				// _dfcc = [r](double x){ return r;};
				_computeConvexUniv = true; _computeConcaveUniv = false;	
				break;
			}
			case ERF:
			{
				_computeConvexUniv = false; _computeConcaveUniv = false;
				if(xL>=0){ // concave increasing
					_computeConcaveUniv = true;
					_fcc = static_cast<double(*)(double)>(std::erf);
					_dfcc = [](double x){ return 2./std::sqrt(mc::PI)*std::exp(-std::pow(x,2));};
					break;
				}
				if(xU<=0){ // convex increasing
					_computeConvexUniv = true;
					_fcv = static_cast<double(*)(double)>(std::erf);
					_dfcv = [](double x){ return 2./std::sqrt(mc::PI)*std::exp(-std::pow(x,2));};
					break;
				}
				// We check if the solution point of the equation 2./std::sqrt(mc::PI)*std::exp(-std::pow(x,2)) = (erf(x)-erf(xU))/(x-xU) is within the given interval 
				// We do it by a simple sign check at lower(upper) bound and 0
				if(mc::sign((2./std::sqrt(mc::PI)*std::exp(-std::pow(xL,2))) - (std::erf(xL)-std::erf(xU))/(xL-xU)) != mc::sign(2./std::sqrt(mc::PI) - (std::erf(xU))/(xU))){
					// Connection point for the convex relaxation is in the interval
					_computeConvexUniv = true;
					_fcv = static_cast<double(*)(double)>(std::erf);
					_dfcv = [](double x){ return 2./std::sqrt(mc::PI)*std::exp(-std::pow(x,2));};
				}			
				if(mc::sign((2./std::sqrt(mc::PI)*std::exp(-std::pow(xU,2))) - (std::erf(xU)-std::erf(xL))/(xU-xL)) != mc::sign(2./std::sqrt(mc::PI) - (std::erf(xL))/(xL))){
					// Connection point for the concave relaxation is in the interval
					_computeConcaveUniv = true;
					_fcc = static_cast<double(*)(double)>(std::erf);
					_dfcc = [](double x){ return 2./std::sqrt(mc::PI)*std::exp(-std::pow(x,2));};
				}
				break;
			}
			default:
                throw std::runtime_error("mc::vMcCormick_Linearizations\t Error in _set_functions_for_univariate_operation, unknown operation "+std::to_string((unsigned)op)+".");
                break;
        }
	 }
   
    
	void _set_evaluation_points_for_univariate_operation
	(double &cvLinPoint, double &ccLinPoint, double &cvInputValue, double &ccInputValue,
     double* cv, double* cc, const double xL, const double xU, const unsigned i, VALUE_CHOICE &choiceCv, VALUE_CHOICE &choiceCc , const OPERATION op)
	{
		switch(op){			
			case EXP: case VAPOR_PRESSURE: case IDEAL_GAS_ENTHALPY: case P_SAT_ETHANOL_SCHROEDER: case RHO_VAP_SAT_ETHANOL_SCHROEDER:
			case LOG: case SATURATION_TEMPERATURE: case SQRT: case DPOW: case TANH: case ERF:
			//    convex and monotonically increasing
			// or concave and monotonically increasing
			{
				cvLinPoint = xL; ccLinPoint = xU;
				cvInputValue = cv[i]; ccInputValue = cc[i];
				choiceCv = CV; choiceCc = CC;
				break;
			}		
			case INV:
			{				
				cvLinPoint = xU; ccLinPoint = xL;
				cvInputValue = cc[i]; ccInputValue = cv[i];
				choiceCv = CC; choiceCc = CV;
				break;
			}
			case SQR: case FABS:
			{   // convex
                int imid = -1;
				cvLinPoint = mc::mid(xL, xU ,0, imid); ccLinPoint = xL;
				cvInputValue = mc::mid(cv[i], cc[i], cvLinPoint, imid); ccInputValue = cc[i];
				choiceCv = imid == 0 ? CUT : (imid == 1 ? CV : CC); choiceCc = CC;
				break;
			}	
            case ARH:
			{
				if(xU<= 0.5* (*_additionalValuesDouble)){ // convex, increasing
					cvLinPoint = xL; ccLinPoint = xU;
					cvInputValue = cv[i]; ccInputValue = cc[i];
					choiceCv = CV; choiceCc = CC;
				}
				else if(xL >= 0.5* (*_additionalValuesDouble)){ // concave increasing			
					cvLinPoint = xL; ccLinPoint = xU;
					cvInputValue = cv[i]; ccInputValue = cc[i];
					choiceCv = CV; choiceCc = CC;
				}
				break;
			}
			case XLOG:
			{   // convex
                int imid = -1;
				cvLinPoint = mc::mid(xL, xU ,std::exp(-1.), imid); ccLinPoint = xL;
				cvInputValue = mc::mid(cv[i], cc[i], cvLinPoint, imid); ccInputValue = cc[i];
				choiceCv = imid == 0 ? CUT : (imid == 1 ? CV : CC); choiceCc = CC;
				break;
			}
			case XEXPAX:
			{
				double a = (*_additionalValuesDouble);
				int currentCase = (*_additionalValuesInt);
				if(a>0){
					switch(currentCase){
						case 0: // convex (not necessarily monotonic)
						{    
							int imid = -1;
							cvLinPoint = mc::mid(xL, xU ,-1/a, imid); ccLinPoint = xL;
							cvInputValue = mc::mid(cv[i], cc[i], cvLinPoint, imid); ccInputValue = cc[i];
							choiceCv = imid == 0 ? CUT : (imid == 1 ? CV : CC); choiceCc = CC;
							break;
						}
						case 1: // concave decreasing
							cvLinPoint = xU; ccLinPoint = xL;
							cvInputValue = cc[i]; ccInputValue = cv[i];
							choiceCv = CC; choiceCc = CV;
						    break;
						default: // convex-concave
						    if(-1/a < xU){
								cvLinPoint = -1/a;
								choiceCv = CUT;
							}
							else{
								cvLinPoint = xU;
								choiceCv = CV;
							}
                            ccLinPoint = xL;
							cvInputValue = cv[i]; ccInputValue = cv[i];
							choiceCc = CV;	
							break;
				            // throw std::runtime_error("mc::vMcCormick_Linearizations\t Error in _set_functions_for_univariate_operation, unknown case in xexpax "+std::to_string(currentCase)+".");					   
					}
				}
				else{
					switch(currentCase){
						case 0: // concave (not necessarily monotonic)
						{    
							int imid = -1;
							cvLinPoint = xL; ccLinPoint = mc::mid(xL, xU ,-1/a, imid);
							cvInputValue = cv[i]; ccInputValue = mc::mid(cv[i], cc[i], cvLinPoint, imid);
							choiceCv = imid == 0 ? CUT : (imid == 1 ? CV : CC); choiceCc = CC;
							break;
						}
						case 1: // convex and monotonically decreasing				    
							cvLinPoint = xU; ccLinPoint = xL;
							cvInputValue = cc[i]; ccInputValue = cv[i];
							choiceCv = CC; choiceCc = CV;
						    break;
						default: // convex-concave
				            if(-1/a < xU){
								ccLinPoint = -1/a;
								choiceCc = CUT;
							}
							else{
								ccLinPoint = xU;
								choiceCc = CC;
							}
                            cvLinPoint = xU;
							cvInputValue = cc[i]; ccInputValue = cc[i];
							choiceCv = CC;	
							break;						
				            // throw std::runtime_error("mc::vMcCormick_Linearizations\t Error in _set_functions_for_univariate_operation, unknown case in xexpax "+std::to_string(currentCase)+".");					   
					}					
				}
                break;				
			}
			case ENTHALPY_OF_VAPORIZATION: case RHO_LIQ_SAT_ETHANOL_SCHROEDER:
			{   // concave decreasing				
				cvLinPoint = xU; ccLinPoint = xL;
				cvInputValue = cc[i]; ccInputValue = cv[i];
				choiceCv = CC; choiceCc = CV;
				break;
			}
			case COST_FUNCTION: case NRTL_TAU: case NRTL_DTAU:
			{
				int givenCase = (*_additionalValuesInt);
				switch(givenCase){
					case 0: // convex not monotonic
					{
						int imid = -1;
						cvLinPoint = mc::mid(xL, xU , _additionalValuesDouble[4], imid); ccLinPoint = xL;
						cvInputValue = mc::mid(cv[i], cc[i], cvLinPoint, imid); ccInputValue = cc[i];
						choiceCv = imid == 0 ? CUT : (imid == 1 ? CV : CC); choiceCc = CC;
						break;
					}
					case 2: // convex increasing
					{
						cvLinPoint = xL; ccLinPoint = xU;
						cvInputValue = cv[i]; ccInputValue = cc[i];
						choiceCv = CV; choiceCc = CC;
						break;
					}
					case 4: // convex decreasing
					{
						cvLinPoint = xU; ccLinPoint = xL;
						cvInputValue = cc[i]; ccInputValue = cv[i];
						choiceCv = CC; choiceCc = CV;
						break;
					}
					case 1: // concave not monotonic
					{
						int imid = -1;
						cvLinPoint = xL; ccLinPoint = mc::mid(xL, xU , _additionalValuesDouble[4], imid);
						cvInputValue = cv[i]; ccInputValue = mc::mid(cv[i], cc[i], cvLinPoint, imid);;
						choiceCv = CV; choiceCc = imid == 0 ? CUT : (imid == 1 ? CV : CC);
						break;						
					}
					case 3: // concave increasing
					{
						cvLinPoint = xL; ccLinPoint = xU;
						cvInputValue = cv[i]; ccInputValue = cc[i];
						choiceCv = CV; choiceCc = CC;
						break;						
					}
					case 5: // concave decreasing				
					{
						cvLinPoint = xU; ccLinPoint = xL;
						cvInputValue = cc[i]; ccInputValue = cv[i];
						choiceCv = CC; choiceCc = CV;
						break;	
					}
				}
				break;
			}
			case NPOW:
			{
				int n = (*_additionalValuesInt);
				if(!(n%2)){ // even exponent		
				    int imid = -1;
					cvLinPoint = mc::mid(xL, xU ,0, imid); ccLinPoint = xL;
					cvInputValue = mc::mid(cv[i], cc[i], cvLinPoint, imid); ccInputValue = cc[i];
					choiceCv = imid == 0 ? CUT : (imid == 1 ? CV : CC); choiceCc = CC;
				}
				else{ // odd exponent
					cvLinPoint = xL; ccLinPoint = xU;
					cvInputValue = cv[i]; ccInputValue = cc[i];
					choiceCv = CV; choiceCc = CC;
				}
			    break;
			}
			case COSH:
			{   // convex
                int imid = -1;
				cvLinPoint = mc::mid(xL, xU ,1, imid); ccLinPoint = xL;
				cvInputValue = mc::mid(cv[i], cc[i], cvLinPoint, imid); ccInputValue = cc[i];
				choiceCv = imid == 0 ? CUT : (imid == 1 ? CV : CC); choiceCc = CC;
				break;
			}
			default:
				throw std::runtime_error("mc::vMcCormick_Linearizations\t Error in _set_evaluation_points_for_univariate_operation, unknown operation "+std::to_string((unsigned)op)+".");
				break;
		}
	}

    void _iterate_running_index(){
		_runningIndexUniv++;		
		switch(_midIndex){
			case 0:
				if(_runningIndexUniv >= _npts){
				  _runningIndexUniv = 1;
				}
				break;
			default:
				if(_runningIndexUniv == _midIndex){
					_runningIndexUniv++;
					if(_runningIndexUniv >= _npts){
					  _runningIndexUniv = _runningIndexUniv-2;
					  return;
					}
				}
				if(_runningIndexUniv >= _npts){
				  _runningIndexUniv = 0;
				  if(_runningIndexUniv == _midIndex){
					  _runningIndexUniv++;
				  }
				  return;
				}
				break;
		}
		
	}

    struct my_double_eq_compare{
        bool operator()(const double &lhs, const double &rhs) const{
			return mc::isequal(lhs,rhs,1e-6,1e-6);
		}	   
   };

#ifdef MC__VMCCORMICK_LIN_DEBUG
    /**
    * @brief Function checking for index consistency in debug mode
    *
    * @param[in] str is the function name
    * @param[in] pt is the additional affine relaxation point index
    * @param[in] var is the variable index
    */
    void _check_consistency(const std::string& function, unsigned int pt, unsigned int var=0)
    {
        if(pt< 0 || pt >= _nadditionalLins)
            throw std::runtime_error("mc::vMcCormick_Linearizations\t Error in "+function+", inconsistent pt = "+std::to_string(pt)+", _nadditionalLins= "+std::to_string(_nadditionalLins)+".");
        if(var< 0 || var >= _nvar)
            throw std::runtime_error("mc::vMcCormick_Linearizations\t Error in "+function+", inconsistent var = "+std::to_string(var)+", _nvar= "+std::to_string(_nvar)+".");
    }
#endif

    const std::vector<std::vector<double>>* _originalPoints; /*!< reference points in the original variable space */
    const std::vector<double>* _originalLowerBounds;         /*!< lower variable bounds in the original variable space  */
    const std::vector<double>* _originalUpperBounds;         /*!< upper variable bounds in the original variable space  */
    std::vector<std::vector<double>> _linPoints;             /*!< reference linearization points to be used when plotting/evaluating the addtional affine relaxations. In  a+b*(x-r), this holds the r*/
    std::vector<double> _cv;                                 /*!< constant value of the convex affine relaxations. In a+b*(x-r) this holds a */
    std::vector<double> _cc;                                 /*!< constant value of the concave affine relaxations. In a+b*(x-r) this holds a */
    std::vector< std::vector<double> > _cvsub;               /*!< slopes of the convex affine relaxations. In a+b*(x-r) this holds b */
    std::vector< std::vector<double> > _ccsub;               /*!< slopes of the concave affine relaxations. In a+b*(x-r) this holds b */
    double _lowerBoundCandidate;                             /*!< best lower bound value as candidate for subgradient heuristic */
    double _upperBoundCandidate;                             /*!< best upper bound value as candidate for subgradient heuristic */
    unsigned int _npts;                                      /*!< number of linearization points of the underlying vmccormick */
    unsigned int _nvar;                                      /*!< number of variables */
    unsigned int _nadditionalLins;                           /*!< maximal number of additional affine relaxations */
	unsigned int _nadditionalLinsUniv;                       /*!< number of additional affine relaxations for univariate operations */
	unsigned int _nadditionalLinsBiv;                        /*!< number of additional affine relaxations for bivariate operations */
    unsigned int _midIndex;                                  /*!< index of mid point (can also be any other point) */
	unsigned int _bestPointIndexCv;                          /*!< index of point with highest minimum of convex affine relaxation */
	unsigned int _bestPointIndexCc;                          /*!< index of point with lower maximum of concave affine relaxation */
	unsigned int _runningIndexUniv;
	bool _computeConvexUniv;                                 /*!< whether to work with additional convex affine relaxations */
	bool _computeConcaveUniv;                                /*!< whether to work with additional concave affine relaxations */ 
    STRATEGY_UNIVARIATE _strategy_univ;                      /*!< strategy used for univariate operations */
    STRATEGY_BIVARIATE _strategy_biv;                        /*!< strategy used for bivariate operations */
	const double* _additionalValuesDouble;                   /*!< pointer holding additional double values for several opeartions */
    const int* _additionalValuesInt;                         /*!< pointer holding additional int values for several operations */
	std::function<double(double)> _fcv;                      /*!< function for evaluation of convex affine relaxation */
	std::function<double(double)> _dfcv;                     /*!< function for evaluation of the derivative of the convex affine relaxation */
	std::function<double(double)> _fcc;                      /*!< function for evaluation of concave affine relaxation */
	std::function<double(double)> _dfcc;                     /*!< function for evaluation of the derivative of the concave affine relaxation */	
	std::vector<unsigned> _index1;                           /*!< indices of first(left) factor to be combined */
	std::vector<unsigned> _index2;	                         /*!< indices of second(right) factor to be combined */
	std::vector<unsigned> _originalIndexForBiv;	             /*!< indices telling with which original point the additional affine relaxation shall be compared */
	std::vector<unsigned> _originalIndexForUniv;             /*!< indices telling with which original point the additional affine relaxation shall be compared */
	std::vector<bool> _useLeftFactorLinPoint;                /*!< whether to use the linearization point of left factor when evaluating affine functions*/
    std::vector<double> _minValues;                          /*!< min values for convex affine relaxation of each addtional linearization point */
    std::vector<double> _maxValues;                          /*!< max values for concave affine relaxation of each addtional linearization point */
    //! @brief  array containing precomputed roots of Q^k(x) up to power 2*k+1 for k=1,...,10 [Liberti & Pantelides (2002), "Convex envelopes of Monomial of Odd Degree]  
    double _Qroots[10]= { -0.5000000000, -0.6058295862, -0.6703320476, -0.7145377272, -0.7470540749, -0.7721416355, -0.7921778546, -0.8086048979, -0.8223534102, -0.8340533676 };  
};

}// namespace mc
#endif
