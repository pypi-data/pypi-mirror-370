/*!
\page page_FFTOSTRING Generation of strings for different output formats.
\author Jaromil Najman, Felix Rauh
\version 1.0
\date May 2019
\bug No known bugs.

It is often desired to write factorable function to different standard modeling formats. The class mc::FFToString provides an implementation for the construction of strings and ostringstreams describing the factorable function symbolically.

The implementation of mc::FFToString relies on the operator/function overloading mechanism of C++. This makes the construction of the final output string simple and intuitive but possibly very memory consuming.

\section sec_FFTOSTRING_use How do I construct a string of a factorable function in a particular modeling language?

Suppose one wants to write a factorable function to a string in the GAMS modeling language format.

First, we set the option for the language to write the factorable function in:

\code
	mc::FFToString::options.WRITING_LANGUAGE = mc::FFToString::LANGUAGE::GAMS;
\endcode

Second, we define the optimization variables with its names:

\code
	mc::FFToString x = mc::FFToString("x", mc::FFToString::PRIO);
	mc::FFToString y = mc::FFToString("y", mc::FFToString::PRIO);
\endcode

Essentialy, the first line means that <tt>x<tt> is a variable of type mc::FFToString with name "x" and no parantheses have to be taken care of, i.e., the expression x is fully paranthesized.

Having defined the variables, a string of \f$f(x,y)=x*y^3\f$ is simply computed as:

\code
	mc::FFToString F = x*pow(y,3);
\endcode

The string can be accessed or displayed in standard output as:

\code
	std::string str = F.get_function_string();
	std::cout << str << std::endl;
	std::cout << "or" << std::endl;
	std::cout << F << std::endl;
\endcode

which produces the following output:

\verbatim
x*power(y,3)
or
x*power(y,3)
\endverbatim

what matches the GAMS modeling language expression of \f$f(x,y)=x*y^3\f$.

\section sec_FFTOSTRING_opt What are the options in mc::FFToString and how are they set?

The class mc::FFToString has a public static member called mc::FFToString::options that can be used to set/modify the options; e.g.,

\code
      mc::FFToString::options.PRECISION = 16;
      mc::FFToString::options.USE_MIN_MAX = true;
      mc::FFToString::options.USE_TRIG = true;
      mc::FFToString::options.IGNORE_BOUNDING_FUNCS = true;
      mc::FFToString::options.WRITING_LANGUAGE = GAMS;
      mc::FFToString::options.USED_ENTHALPY_OF_VAPORIZATION = false;
\endcode

The available options are the following:

<TABLE border="1">
<CAPTION><EM>Options in mc::FFToString::Options: name, type and description</EM></CAPTION>
     <TR><TH><b>Name</b>  <TD><b>Type</b><TD><b>Default</b>
         <TD><b>Description</b>
     <TR><TH><tt>PRECISION</tt> <TD><tt>unsigned int</tt> <TD>16
         <TD>Maximum number digits written to string.
     <TR><TH><tt>USE_MIN_MAX</tt> <TD><tt>bool</tt> <TD>true
         <TD>Whether to write min/max as it is or to write it as an abs() formulation.
     <TR><TH><tt>USE_TRIG</tt> <TD><tt>bool</tt> <TD>true
         <TD>Whether to use trigonometric functions or use exp reformulations (if possible).
     <TR><TH><tt>IGNORE_BOUNDING_FUNCS</tt> <TD><tt>bool</tt> <TD>true
         <TD>Whether to use or ignore bounding functions.
     <TR><TH><tt>WRITING_LANGUAGE</tt> <TD><tt>LANGUAGE</tt> <TD>GAMS
         <TD>Modeling language to be written to.
     <TR><TH><tt>USED_ENTHALPY_OF_VAPORIZATION</tt> <TD><tt>bool</tt> <TD>false
         <TD>This function is only used to know whether ENTHALPY_OF_VAPORIZATION has been used, since it is a piecewise defined function. It is not meant to be used as a real option.
</TABLE>

\section sec_FFToString_err What Errors Can Be Encountered during the construction of function strings?

Errors are managed based on the exception handling mechanism of the C++ language. Each time an error is encountered, a class object of type mc::FFToString::Exceptions is thrown, which contains the type of error. It is the user's responsibility to test whether an exception was thrown during a FFToString construction, and then make the appropriate changes. Should an exception be thrown and not caught by the calling program, the execution will stop.

Possible errors encountered during the construction of a FFToString are:

<TABLE border="1">
<CAPTION><EM>Errors during construction of a FFToString are</EM></CAPTION>
     <TR><TH><b>Number</b> <TD><b>Description</b>
     <TR><TH><tt>-1</tt> <TD>Internal error
     <TR><TH><tt>3</tt> <TD>Function SUM_DIV is called with invalid inputs
     <TR><TH><tt>3</tt> <TD>Function XLOG_SUM is called with invalid inputs
     <TR><TH><tt>4</tt> <TD>Function VAPOR_PRESSURE is called with an unknown type
     <TR><TH><tt>5</tt> <TD>Function IDEAL_GAS_ENTHALPY is called with an unknown type
     <TR><TH><tt>6</tt> <TD>Function SATURATION_TEMPERATURE is called with an unknown type
     <TR><TH><tt>7</tt> <TD>Function ENTHALPY_OF_VAPORIZATION is called with an unknown type
     <TR><TH><tt>8</tt> <TD>Function COST_FUNCTION is called with an unknown type
	 <TR><TH><tt>9</tt> <TD>Function SINGLE_NEURON is called with invalid inputs
     <TR><TH><tt>10</tt> <TD>Inconsistent size of subgradient between two mc::McCormick variables
     <TR><TH><tt>11</tt> <TD>A function is called although it is not supported by FFToString
     <TR><TH><tt>12</tt> <TD>Unknown writing language
</TABLE>
*/

#ifndef MC__FFTOSTRING_HPP
#define MC__FFTOSTRING_HPP

#include <iostream>
#include <sstream>
#include <iomanip>
#include <string>
#include <vector>

#include "mcop.hpp"

namespace mc
{


class FFToString
////////////////////////////////////////////////////////////////////////
{

 // friends of class FFToString for operator and function overloading
 friend FFToString operator+  (const FFToString&);
 friend FFToString operator+  (const FFToString&, const FFToString&);
 friend FFToString operator+  (const double, const FFToString&);
 friend FFToString operator+  (const FFToString&, const double);
 friend FFToString operator-  (const FFToString&);
 friend FFToString operator-  (const FFToString&, const FFToString&);
 friend FFToString operator-  (const double, const FFToString&);
 friend FFToString operator-  (const FFToString&, const double);
 friend FFToString operator*  (const FFToString&, const FFToString&);
 friend FFToString operator*  (const FFToString&, const double);
 friend FFToString operator*  (const double, const FFToString&);
 friend FFToString operator/  (const FFToString&, const FFToString&);
 friend FFToString operator/  (const FFToString&, const double);
 friend FFToString operator/  (const double, const FFToString&);
 friend std::ostream& operator<< (std::ostream&, const FFToString&);
 friend bool operator==  (const FFToString&, const FFToString&);
 friend bool operator!=  (const FFToString&, const FFToString&);
 friend bool operator<=  (const FFToString&, const FFToString&);
 friend bool operator>=  (const FFToString&, const FFToString&);
 friend bool operator<   (const FFToString&, const FFToString&);
 friend bool operator>   (const FFToString&, const FFToString&);
 friend FFToString inv(const FFToString&);
 friend FFToString sqr(const FFToString&);
 friend FFToString exp(const FFToString&);
 friend FFToString log(const FFToString&);
 friend FFToString xlog(const FFToString&);
 friend FFToString fabsx_times_x(const FFToString&);
 friend FFToString xexpax(const FFToString&, const double);
 friend FFToString centerline_deficit(const FFToString&, const double, const double);
 friend FFToString wake_profile(const FFToString&, const double);
 friend FFToString wake_deficit(const FFToString&, const FFToString&, const double, const double, const double, const double, const double);
 friend FFToString power_curve(const FFToString&, const double);
 friend FFToString lmtd(const FFToString&, const FFToString&);
 friend FFToString rlmtd(const FFToString&, const FFToString&);
 friend FFToString mid(const FFToString&, const FFToString&, const double);
 friend FFToString pinch(const FFToString&, const FFToString&, const FFToString&);
 friend FFToString euclidean_norm_2d(const FFToString&, const FFToString&);
 friend FFToString expx_times_y(const FFToString&, const FFToString&);
 friend FFToString vapor_pressure(const FFToString&, const double, const double, const double, const double, const double,
	 const double, const double, const double, const double, const double, const double);
 friend FFToString ideal_gas_enthalpy(const FFToString&, const double, const double, const double, const double, const double, const double,
	 const double, const double, const double);
 friend FFToString saturation_temperature(const FFToString&, const double, const double, const double, const double, const double,
	 const double, const double, const double, const double, const double, const double);
 friend FFToString enthalpy_of_vaporization(const FFToString&, const double, const double, const double, const double, const double,
	 const double, const double);
 friend FFToString cost_function(const FFToString&, const double, const double, const double, const double);
 friend FFToString sum_div(const std::vector< FFToString >&, const std::vector<double>&);
 friend FFToString xlog_sum(const std::vector< FFToString >&, const std::vector<double>&);
 friend FFToString nrtl_tau(const FFToString&, const double, const double, const double, const double);
 static FFToString nrtl_dtau(const FFToString&, const double, const double, const double);
 friend FFToString nrtl_G(const FFToString&, const double, const double, const double, const double, const double);
 friend FFToString nrtl_Gtau(const FFToString&, const double, const double, const double, const double, const double);
 friend FFToString nrtl_Gdtau(const FFToString&, const double, const double, const double, const double, const double);
 friend FFToString nrtl_dGtau(const FFToString&, const double, const double, const double, const double, const double);
 friend FFToString p_sat_ethanol_schroeder(const FFToString&);
 friend FFToString rho_vap_sat_ethanol_schroeder(const FFToString&);
 friend FFToString rho_liq_sat_ethanol_schroeder(const FFToString&);
 friend FFToString covariance_function(const FFToString&, const double);
 friend FFToString acquisition_function(const FFToString&, const FFToString&, const double, const double);
 friend FFToString gaussian_probability_density_function(const FFToString&);
 friend FFToString regnormal(const FFToString&, const double, const double);
 friend FFToString arh(const FFToString&, const double);
 friend FFToString cos(const FFToString&);
 friend FFToString sin(const FFToString&);
 friend FFToString tan(const FFToString&);
 friend FFToString acos(const FFToString&);
 friend FFToString asin(const FFToString&);
 friend FFToString atan(const FFToString&);
 friend FFToString cosh(const FFToString&);
 friend FFToString sinh(const FFToString&);
 friend FFToString tanh(const FFToString&);
 friend FFToString coth(const FFToString&);
 friend FFToString fabs(const FFToString&);
 friend FFToString sqrt(const FFToString&);
 friend FFToString erf(const FFToString&);
 friend FFToString erfc(const FFToString&);
 friend FFToString fstep(const FFToString&);
 friend FFToString bstep(const FFToString&);
 friend FFToString cheb(const FFToString&, const unsigned);
 friend FFToString pow(const FFToString&, const int);
 friend FFToString pow(const FFToString&, const double);
 friend FFToString pow(const FFToString&, const FFToString&);
 friend FFToString min(const FFToString&, const FFToString&);
 friend FFToString max(const FFToString&, const FFToString&);
 friend FFToString pos(const FFToString&);
 friend FFToString neg(const FFToString&);
 friend FFToString lb_func(const FFToString&, const double);
 friend FFToString ub_func(const FFToString&, const double);
 friend FFToString bounding_func(const FFToString&, const double, const double);
 friend FFToString squash_node(const FFToString&, const double, const double);
 friend FFToString single_neuron(const std::vector< FFToString >&, const std::vector<double>&, const double, const int);
 friend FFToString mc_print(const FFToString&, const int);
 friend FFToString inter(const FFToString&, const FFToString&);
 friend FFToString min(const unsigned int, const FFToString*);
 friend FFToString max(const unsigned int, const FFToString*);
 friend FFToString sum(const unsigned int, const FFToString*);
 friend FFToString prod(const unsigned int, const FFToString*);
 friend FFToString monom(const unsigned int, const FFToString*, const unsigned*);

public:

  /** @defgroup FFToString Arithmetic for String writing
   *  @{
   */

  //! @brieg Enum for different languages to write the function in
	enum LANGUAGE {
		AMPL = 0, //!< AMPL
		ALE,      //!< ALE
		BARON,    //!< BARON
		GAMS,	  //!< GAMS
		PYOMO,    //!< PYOMO
		NLP,      //!< NLP
	};
  //! @brieg Enum for different types of expressions saved in _name (depends on outermost operator)
	enum OPTYPE {
		PRIO = 0,   //!< Fully parenthesized expession which can be combined with any other operator
		MINUS_PRIO, //!< Fully parenthesized expession with a minus in front
		PROD,       //!< Product which can be combined with any other operator without parenthesizing except for division
		MINUS_PROD, //!< Product with a minus in front
		SUM,        //!< Expession which consists of a sum, may have to be parenthesized
		MINUS_SUM,  //!< Expession which consists of a sum and a negative sign, may have to be parenthesized
	};

  //! @brief Options of mc::FFToString
  static struct Options
  {
    //! @brief Constructor
    Options():
      PRECISION(16), USE_MIN_MAX(true), USE_TRIG(true), IGNORE_BOUNDING_FUNCS(true), WRITING_LANGUAGE(GAMS), USED_ENTHALPY_OF_VAPORIZATION(false)
      {}
    //! @brief Maximum number digits written to string.
    unsigned int PRECISION;
    //! @brief Whether to write min/max as it is or to write it as an abs() formulation.
    bool USE_MIN_MAX;
    //! @brief Whether to use trigonometric functions or use exp reformulations (if possible).
	bool USE_TRIG;
    //! @brief Whether to use or ignore bounding functions.
	bool IGNORE_BOUNDING_FUNCS;
    //! @brief Language to be written to.
	LANGUAGE WRITING_LANGUAGE;
	//! @brief This function is only used to know whether ENTHALPY_OF_VAPORIZATION has been used, since it is a piecewise defined function. It is not meant to be used as a real option.
	bool USED_ENTHALPY_OF_VAPORIZATION;
  } options;

  //! @brief Exceptions of mc::FFToString
  class Exceptions
  {
  public:
    //! @brief Enumeration type for FFToString exception handling

    enum TYPE{
	  INTERN=-1, 						//!< Internal error
	  SUM_DIV,					        //!< Function SUM_DIV is called with invalid inputs
	  XLOG_SUM,						    //!< Function XLOG_SUM is called with invalid inputs
	  VAPOR_PRESSURE,					//!< Function VAPOR_PRESSURE is called with an unknown type
	  IDEAL_GAS_ENTHALPY,				//!< Function IDEAL_GAS_ENTHALPY is called with an unknown type
	  SATURATION_TEMPERATURE,			//!< Function SATURATION_TEMPERATURE is called with an unknown type
	  ENTHALPY_OF_VAPORIZATION,			//!< Function ENTHALPY_OF_VAPORIZATION is called with an unknown type
	  COST_FUNCTION,					//!< Function COST_FUNCTION is called with an unknown type
	  COVARIANCE_FUNCTION,				//!< Function COVARIANCE_FUNCTION is called with an unknown type
	  ACQUISITION_FUNCTION,				//!< Function ACQUISITION_FUNCTION is called with an unknown type
	  SINGLE_NEURON,					//!< Function SINGLE_NEURON is called with invalid inputs
	  UNSUPPORTED_FUNCTION,				//!< A function is called although it is not supported by FFToString
	  UNKNOWN_LANGUAGE, 				//!< Unknown writing language
    };
    //! @brief Constructor for error <a>ierr</a>
    Exceptions( TYPE ierr ) : _ierr( ierr ){}

    //! @brief Inline function returning the error flag
    int ierr(){ return _ierr; }
  private:
    TYPE _ierr;
    //! @brief Error description
    std::string what(){
      switch( _ierr ){
      case INTERN:
        return "mc::FFToString    Internal error.";
	  case SUM_DIV:
		return "mc::FFToString    Function SUM_DIV is called with invalid dimensions of input vectors.";
	  case XLOG_SUM:
		return "mc::FFToString    Function XLOG_SUM is called with invalid dimensions of input vectors.";
	  case VAPOR_PRESSURE:
		return "mc::FFToString    Function VAPOR_PRESSURE is called with an unknown type.";
	  case IDEAL_GAS_ENTHALPY:
		return "mc::FFToString    Function IDEAL_GAS_ENTHALPY is called with an unknown type.";
	  case SATURATION_TEMPERATURE:
		return "mc::FFToString    Function SATURATION_TEMPERATURE is called with an unknown type.";
	  case ENTHALPY_OF_VAPORIZATION:
		return "mc::FFToString    Function ENTHALPY_OF_VAPORIZATION is called with an unknown type.";
	  case COST_FUNCTION:
		return "mc::FFToString    Function COST_FUNCTION is called with an unknown type.";
	  case COVARIANCE_FUNCTION:
		return "mc::FFToString    Function COVARIANCE_FUNCTION is called with an unknown type.";
	  case ACQUISITION_FUNCTION:
		return "mc::FFToString    Function ACQUISITION_FUNCTION is called with an unknown type.";
	  case SINGLE_NEURON:
		return "mc::FFToString    Function SINGLE_NEURON is called with invalid dimensions of input vectors.";
	  case UNSUPPORTED_FUNCTION:
		return "mc::FFToString    A Function is called which is not supported in FFToString.";
	  case UNKNOWN_LANGUAGE:
		return "mc::FFToString    Unknown modeling language.";
      default:
        return "mc::FFToString    Undocumented error";
      }
    }
  };

  //! @brief Default constructor (needed to declare arrays of FFToString class)
  FFToString()
    {
		_name << "";
		_optype = PRIO;
	}

  //! @brief Constructor for a string value <a>str</a> (without information about operator type)
  FFToString
    ( const std::string str )
    {
		_name << "(" << str << ")";
		_optype = PRIO;
	}

  //! @brief Constructor for a string value <a>str</a> and operator type <a>optype</a>
  FFToString
  (const std::string str, const OPTYPE optype)
  {
	  _name << str;
	  _optype = optype;
  }

  //! @brief Constructor for a ostringstream value <a>str</a> (without information about operator type)
  FFToString
    ( const std::ostringstream str )
    {
		_name << "(" << str.str() << ")" ;
		_optype = PRIO;
	}

  //! @brief Constructor for a ostringstream value <a>str</a> and operator type <a>optype</a>
  FFToString
  (const std::ostringstream str, const OPTYPE optype)
  {
	  _name << str.str();
	  _optype = optype;
  }

  //! @brief Constructor for a double
  FFToString
    ( const double c )
    {
		if(c<0.){
			_name << std::setprecision(mc::FFToString::options.PRECISION) << -c;
			_optype = MINUS_PRIO;
		}
		else{
			_name << std::setprecision(mc::FFToString::options.PRECISION) << c;
			_optype = PRIO;
		}
    }

  //! @brief Constructor for a unary <a>function</a> on <a>S</a>
  FFToString
  (const FFToString& S, const std::string& function)
	{
		_name << function << "(";
		if(S.get_optype() == MINUS_PRIO || S.get_optype() == MINUS_PROD){
			_name << "-";
		} else if(S.get_optype() == MINUS_SUM){
			_name << "-(";
		}
		_name << S.get_name_string() << ")";
		if (S.get_optype() == MINUS_SUM){
			_name << ")";
		}
		_optype = PRIO;
	}

  //! @brief Copy constructor
  FFToString
    ( const FFToString& S)
    {
		_name << S.get_name_string();
		_optype = S._optype;
    }


  //! @brief Destructor
  ~FFToString()
    {}

  //! @brief Name
  std::ostringstream& name()
  {
	  return _name;
  }

  const std::ostringstream& name() const
  {
	  return _name;
  }


  //! @brief Set interval bounds
  void set_name
  (const std::string& str)
  {
	  _name.clear(); _name.str("");
	  _name << str;
  }

  void set_optype
  (const OPTYPE optype)
  {
	  _optype = optype;
  }


private:

  //! @brief Name of the variable, basically the resulting string
  std::ostringstream _name;
  OPTYPE _optype;

public:

  std::string get_name_string() {
		return _name.str();
	}

  std::string get_name_string() const {
		return _name.str();
	}

  /*std::ostringstream get_name_ostringstream() const {
	  return _name;
  }*/

  std::string get_function_string() const {
		std::ostringstream out;
		if(_optype == mc::FFToString::MINUS_PRIO || _optype == mc::FFToString::MINUS_PROD){
			out << "-";
		} else if (_optype == mc::FFToString::MINUS_SUM){
			out << "-(";
		}
		out << _name.str();
		if (_optype == mc::FFToString::MINUS_SUM){
			out << ")";
		}
		return out.str();
	}

  OPTYPE get_optype() const {
		return _optype;
	}

  // other operator overloadings (inlined)
  FFToString& operator=
    ( const double c )
    {
       _name.clear(); _name.str("");
	   if(c<0.){
			_name << std::setprecision(mc::FFToString::options.PRECISION) << -c;
			_optype = MINUS_PRIO;
		}
		else{
			_name << std::setprecision(mc::FFToString::options.PRECISION) << c;
			_optype = PRIO;
		}
		return *this;
    }

  FFToString& operator=
    ( const std::string& str )
    {
       _name.clear(); _name.str("");
	   _name << "(" << str << ")";
	   _optype = PRIO;
	   return *this;
    }

  FFToString& operator=
    ( const FFToString&S )
    {
		_name.clear(); _name.str("");
		_name << S.get_name_string();
		_optype = S.get_optype();
		return *this;
    }

  FFToString& operator+=
    ( const double c )
    {
		std::ostringstream ostr;

		switch (this->_optype) {
			case PRIO: case SUM: case PROD:
				ostr << get_name_string();
				if (c<0) {
					ostr << "-" << std::setprecision(mc::FFToString::options.PRECISION) << -c;
				}
				else {
					ostr << "+" << std::setprecision(mc::FFToString::options.PRECISION) << c;
				}
				this->_optype = SUM;
				break;

			case MINUS_PRIO: case MINUS_SUM: case MINUS_PROD:
				if (c<0) {
					ostr << get_name_string();
					ostr << "+" << std::setprecision(mc::FFToString::options.PRECISION) << -c;
				}
				else {
					ostr << get_name_string();
					ostr << "-" << std::setprecision(mc::FFToString::options.PRECISION) << c;
				}
				this->_optype = MINUS_SUM;
				break;
		}

		_name.clear(); _name.str("");
		_name << ostr.str();

		return *this;
    }

  FFToString& operator+=
    ( const FFToString&S )
    {
	  std::ostringstream ostr;

	  switch (this->_optype) {
		case PRIO: case SUM: case PROD:
		{
		  switch (S._optype) {
			  case PRIO: case SUM: case PROD:
				  ostr << get_name_string() << "+" << S.get_name_string();
				  break;
			  case MINUS_PRIO: case MINUS_PROD:
				  ostr << get_name_string() << "-" << S.get_name_string();
				  break;
			  case MINUS_SUM:
				  ostr << get_name_string() << "-(" << S.get_name_string() << ")";
				  break;
		  }
		  this->_optype = SUM;
		  break;
		}

		case MINUS_SUM: case MINUS_PRIO: case MINUS_PROD:
		{
		  switch (S._optype) {
			  case PRIO: case PROD: case SUM:
				  ostr << get_name_string() << "-(" << S.get_name_string() << ")";
				  break;
			  case MINUS_PRIO: case MINUS_PROD: case MINUS_SUM:
				  ostr << get_name_string() << "+" << S.get_name_string();
				  break;
		  }
		  this->_optype = MINUS_SUM;
		  break;
		}

	  }

	  _name.clear(); _name.str("");
	  _name << ostr.str();

	  return *this;
  }

 FFToString& operator-=
    ( const double c )
    {
		*this += -c;
		return *this;
    }

  FFToString& operator-=
    ( const FFToString&S )
    {
	  switch (S._optype) {
		  case PRIO:
			  *this += FFToString(S.get_name_string(), MINUS_PRIO);
			  break;
		  case MINUS_PRIO:
			  *this += FFToString(S.get_name_string(), PRIO);
			  break;
		  case PROD:
			  *this += FFToString(S.get_name_string(), MINUS_PROD);
			  break;
		  case MINUS_PROD:
			  *this += FFToString(S.get_name_string(), PROD);
			  break;
		  case SUM:
			  *this += FFToString(S.get_name_string(), MINUS_SUM);
			  break;
		  case MINUS_SUM:
			  *this += FFToString(S.get_name_string(), SUM);
			  break;
	  }
	  return *this;
    }

  FFToString& operator*=
    ( const double c )
    {

	  std::ostringstream ostr;

	  switch (this->_optype) {
	  case PRIO: case PROD:
		  ostr << get_name_string();
		  if (c<0) {
			  ostr << "*" << std::setprecision(mc::FFToString::options.PRECISION) << -c;
			  this->_optype = MINUS_PROD;
		  }
		  else {
			  ostr << "*" << std::setprecision(mc::FFToString::options.PRECISION) << c;
			  this->_optype = PROD;
		  }
		  break;
	  case SUM:
		  ostr << "(" << get_name_string() << ")";
		  if (c<0) {
			  ostr << "*" << std::setprecision(mc::FFToString::options.PRECISION) << -c;
			  this->_optype = MINUS_PROD;
		  }
		  else {
			  ostr << "*" << std::setprecision(mc::FFToString::options.PRECISION) << c;
			  this->_optype = PROD;
		  }
		  break;
	  case MINUS_PRIO: case MINUS_PROD:
		  ostr << get_name_string();
		  if (c<0) {
			  ostr << "*" << std::setprecision(mc::FFToString::options.PRECISION) << -c;
			  this->_optype = PROD;
		  }
		  else {
			  ostr << "*" << std::setprecision(mc::FFToString::options.PRECISION) << c;
			  this->_optype = MINUS_PROD;
		  }
		  break;
	  case MINUS_SUM:
		  ostr << "(" << get_name_string() << ")";
		  if (c<0) {
			  ostr << "*" << std::setprecision(mc::FFToString::options.PRECISION) << -c;
			  this->_optype = PROD;
		  }
		  else {
			  ostr << "*" << std::setprecision(mc::FFToString::options.PRECISION) << c;
			  this->_optype = MINUS_PROD;
		  }
		  break;
	  }

	  _name.clear(); _name.str("");
	  _name << ostr.str();

	  return *this;
    }

  FFToString& operator*=
    ( const FFToString&S )
    {
	  std::ostringstream ostr;

	  switch (this->_optype) {
	  case PRIO: case PROD:
		  ostr << get_name_string();
		  switch (S._optype) {
		  case PRIO: case PROD:
			  ostr << "*" << S.get_name_string();
			  this->_optype = PROD;
			  break;
		  case SUM:
			  ostr << "*(" << S.get_name_string() << ")";
			  this->_optype = PROD;
			  break;
		  case MINUS_PRIO: case MINUS_PROD:
			  ostr << "*" << S.get_name_string();
			  this->_optype = MINUS_PROD;
			  break;
		  case MINUS_SUM:
			  ostr << "*(" << S.get_name_string() << ")";
			  this->_optype = MINUS_PROD;
			  break;
		  }
		  break;
	  case SUM:
		  ostr << "(" << get_name_string()<< ")";
		  switch (S._optype) {
		  case PRIO: case PROD:
			  ostr << "*" << S.get_name_string();
			  this->_optype = PROD;
			  break;
		  case SUM:
			  ostr << "*(" << S.get_name_string() << ")";
			  this->_optype = PROD;
			  break;
		  case MINUS_PRIO: case MINUS_PROD:
			  ostr << "*" << S.get_name_string();
			  this->_optype = MINUS_PROD;
			  break;
		  case MINUS_SUM:
			  ostr << "*(" << S.get_name_string() << ")";
			  this->_optype = MINUS_PROD;
			  break;
		  }
		  break;
	  case MINUS_PRIO: case MINUS_PROD:
		  ostr << get_name_string();
		  switch (S._optype) {
		  case PRIO: case PROD:
			  ostr << "*" << S.get_name_string();
			  this->_optype = MINUS_PROD;
			  break;
		  case SUM:
			  ostr << "*(" << S.get_name_string() << ")";
			  this->_optype = MINUS_PROD;
			  break;
		  case MINUS_PRIO: case MINUS_PROD:
			  ostr << "*" << S.get_name_string();
			  this->_optype = PROD;
			  break;
		  case MINUS_SUM:
			  ostr << "*(" << S.get_name_string() << ")";
			  this->_optype = PROD;
			  break;
		  }
		  break;
	  case MINUS_SUM:
		  ostr << "(" << get_name_string()<< ")";
		  switch (S._optype) {
		  case PRIO: case PROD:
			  ostr << "*" << S.get_name_string();
			  this->_optype = MINUS_PROD;
			  break;
		  case SUM:
			  ostr << "*(" << S.get_name_string() << ")";
			  this->_optype = MINUS_PROD;
			  break;
		  case MINUS_PRIO: case MINUS_PROD:
			  ostr << "*" << S.get_name_string();
			  this->_optype = PROD;
			  break;
		  case MINUS_SUM:
			  ostr << "*(" << S.get_name_string() << ")";
			  this->_optype = PROD;
			  break;
		  }
		  break;
	  }

	  _name.clear(); _name.str("");
	  _name << ostr.str();

	  return *this;
    }

  FFToString& operator/=
    ( const double c )
    {
	  std::ostringstream ostr;

	  switch (this->_optype) {
	  case PRIO: case PROD:
		  ostr << get_name_string();
		  if (c<0) {
			  ostr << "/" << std::setprecision(mc::FFToString::options.PRECISION) << -c;
			  this->_optype = MINUS_PROD;
		  }
		  else {
			  ostr << "/" << std::setprecision(mc::FFToString::options.PRECISION) << c;
			  this->_optype = PROD;
		  }
		  break;
	  case SUM:
		  ostr << "(" << get_name_string() << ")";
		  if (c<0) {
			  ostr << "/" << std::setprecision(mc::FFToString::options.PRECISION) << -c;
			  this->_optype = MINUS_PROD;
		  }
		  else {
			  ostr << "/" << std::setprecision(mc::FFToString::options.PRECISION) << c;
			  this->_optype = PROD;
		  }
		  break;
	  case MINUS_PRIO: case MINUS_PROD:
		  ostr << get_name_string();
		  if (c<0) {
			  ostr << "/" << std::setprecision(mc::FFToString::options.PRECISION) << -c;
			  this->_optype = PROD;
		  }
		  else {
			  ostr << "/" << std::setprecision(mc::FFToString::options.PRECISION) << c;
			  this->_optype = MINUS_PROD;
		  }
		  break;
	  case MINUS_SUM:
		  ostr << "(" << get_name_string() << ")";
		  if (c<0) {
			  ostr << "/" << std::setprecision(mc::FFToString::options.PRECISION) << -c;
			  this->_optype = PROD;
		  }
		  else {
			  ostr << "/" << std::setprecision(mc::FFToString::options.PRECISION) << c;
			  this->_optype = MINUS_PROD;
		  }
		  break;
	  }

	  _name.clear(); _name.str("");
	  _name << ostr.str();

	  return *this;
    }

  FFToString& operator/=
    ( const FFToString&S )
    {
	  std::ostringstream ostr;

	  switch (this->_optype) {
	  case PRIO: case PROD:
		  ostr << get_name_string();
		  switch (S._optype) {
		  case PRIO:
			  ostr << "/" << S.get_name_string();
			  this->_optype = PROD;
			  break;
		  case SUM: case PROD:
			  ostr << "/(" << S.get_name_string() << ")";
			  this->_optype = PROD;
			  break;
		  case MINUS_PRIO:
			  ostr << "/" << S.get_name_string();
			  this->_optype = MINUS_PROD;
			  break;
		  case MINUS_SUM: case MINUS_PROD:
			  ostr << "/(" << S.get_name_string() << ")";
			  this->_optype = MINUS_PROD;
			  break;
		  }
		  break;
	  case SUM:
		  ostr << "(" << get_name_string()<< ")";
		  switch (S._optype) {
		  case PRIO:
			  ostr << "/" << S.get_name_string();
			  this->_optype = PROD;
			  break;
		  case SUM: case PROD:
			  ostr << "/(" << S.get_name_string() << ")";
			  this->_optype = PROD;
			  break;
		  case MINUS_PRIO:
			  ostr << "/" << S.get_name_string();
			  this->_optype = MINUS_PROD;
			  break;
		  case MINUS_SUM: case MINUS_PROD:
			  ostr << "/(" << S.get_name_string() << ")";
			  this->_optype = MINUS_PROD;
			  break;
		  }
		  break;
	  case MINUS_PRIO: case MINUS_PROD:
		  ostr << get_name_string();
		  switch (S._optype) {
		  case PRIO:
			  ostr << "/" << S.get_name_string();
			  this->_optype = MINUS_PROD;
			  break;
		  case SUM: case PROD:
			  ostr << "/(" << S.get_name_string() << ")";
			  this->_optype = MINUS_PROD;
			  break;
		  case MINUS_PRIO:
			  ostr << "/" << S.get_name_string();
			  this->_optype = PROD;
			  break;
		  case MINUS_SUM: case MINUS_PROD:
			  ostr << "/(" << S.get_name_string() << ")";
			  this->_optype = PROD;
			  break;
		  }
		  break;
	  case MINUS_SUM:
		  ostr << "(" << get_name_string()<< ")";
		  switch (S._optype) {
		  case PRIO:
			  ostr << "/" << S.get_name_string();
			  this->_optype = MINUS_PROD;
			  break;
		  case SUM: case PROD:
			  ostr << "/(" << S.get_name_string() << ")";
			  this->_optype = MINUS_PROD;
			  break;
		  case MINUS_PRIO:
			  ostr << "/" << S.get_name_string();
			  this->_optype = PROD;
			  break;
		  case MINUS_SUM: case MINUS_PROD:
			  ostr << "/(" << S.get_name_string() << ")";
			  this->_optype = PROD;
			  break;
		  }
		  break;
	  }

	  _name.clear(); _name.str("");
	  _name << ostr.str();

	  return *this;
    }

};

////////////////////////////////////////////////////////////////////////////////
//Non-member operators
////////////////////////////////
inline std::ostream&
operator<<
( std::ostream&out, const FFToString&S)
{
	out << S.get_function_string();
	return out;
}

inline FFToString
operator+
( const FFToString&S )
{
  return S;
}

inline FFToString
operator-
( const FFToString&S )
{
  switch (S.get_optype()) {
	  case mc::FFToString::PRIO:
		  return FFToString(S.get_name_string(), mc::FFToString::MINUS_PRIO);
		  break;
	  case mc::FFToString::MINUS_PRIO:
		  return FFToString(S.get_name_string(), mc::FFToString::PRIO);
		  break;
	  case mc::FFToString::PROD:
		  return FFToString(S.get_name_string(), mc::FFToString::MINUS_PROD);
		  break;
	  case mc::FFToString::MINUS_PROD:
		  return FFToString(S.get_name_string(), mc::FFToString::PROD);
		  break;
	  case mc::FFToString::SUM:
		  return FFToString(S.get_name_string(), mc::FFToString::MINUS_SUM);
		  break;
	  case mc::FFToString::MINUS_SUM:
		  return FFToString(S.get_name_string(), mc::FFToString::SUM);
		  break;
	  default:
		  return 0 - S;
  }
}

inline FFToString
operator+
( const double c, const FFToString&S )
{
	FFToString C(c);
	C += S;
	return C;
}

inline FFToString
operator+
( const FFToString&S, const double c )
{
	FFToString S2(S);
	S2 += c;
	return S2;
}

inline FFToString
operator+
( const FFToString&S1, const FFToString&S2 )
{
	FFToString S(S1);
	S += S2;
	return S;
}

inline FFToString
sum
( const unsigned int n, const FFToString*S )
{
	switch(n)
	{
		case 0:
			return FFToString(0);
			break;
		case 1:
			return FFToString(S[0]);
			break;
		default:
			FFToString res(S[0]);
			for(unsigned int i = 1; i < n; i++){
				res += S[i];
			}
			return res;
	}
}

inline FFToString
operator-
( const double c, const FFToString&S )
{
	FFToString C(c);
	C -= S;
	return C;
}

inline FFToString
operator-
( const FFToString&S, const double c )
{
	FFToString S2(S);
	S2 -= c;
	return S2;
}

inline FFToString
operator-
( const FFToString&S1, const FFToString&S2 )
{
	FFToString S(S1);
	S -= S2;
	return S;
}

inline FFToString
operator*
( const double c, const FFToString&S )
{
	FFToString C(c);
	C *= S;
	return C;
}

inline FFToString
operator*
( const FFToString&S, const double c )
{
	FFToString S2(S);
	S2 *= c;
	return S2;
}

inline FFToString
operator*
( const FFToString&S1, const FFToString&S2 )
{
	FFToString S(S1);
	S *= S2;
	return S;
}

inline FFToString
prod
( const unsigned int n, const FFToString*S )
{
	FFToString res;
	switch(n)
	{
		case 0:
			return FFToString(1);
			break;
		case 1:
			return FFToString(S[0]);
			break;
		default:
			for(unsigned int i = 0; i < n; i++){
				res *= S[i];
			}
	}
	return res;
}

inline FFToString
monom
( const unsigned int n, const FFToString*S, const unsigned*k )
{
	switch(n)
	{
		case 0:
			return FFToString(1);
			break;
		case 1:
			return pow(FFToString(S[0]),(int)k[0]);
			break;
		default:
			FFToString res = pow(FFToString(S[0]), (int)k[0]);
			for (unsigned int i = 1; i < n; i++) {
				res *= pow(FFToString(S[i]), (int)k[i]);
			}
			return res;
	}
}

inline FFToString
operator/
( const FFToString&S, const double c )
{
	FFToString S2(S);
	S2 /= c;
	return S2;
}

inline FFToString
operator/
( const double c, const FFToString&S )
{
	FFToString C(c);
	C /= S;
	return C;
}

inline FFToString
operator/
( const FFToString&S1, const FFToString&S2 )
{
	FFToString S(S1);
	S /= S2;
	return S;
}

inline FFToString
inv
( const FFToString&S )
{
  return 1./S;
}

inline FFToString
sqr
( const FFToString&S )
{
  return FFToString(S,"sqr");
}

inline FFToString
sqrt
( const FFToString&S )
{
  return FFToString(S,"sqrt");
}

inline FFToString
exp
( const FFToString&S )
{
  return FFToString(S,"exp");
}

inline FFToString
arh
( const FFToString&S, const double a )
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
			{
			std::ostringstream ostr;
			ostr << "arh(" << S << "," << std::setprecision(mc::FFToString::options.PRECISION) << a << ")";
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
			}
		default:
			return exp( -a / S );
	}
}

inline FFToString
log
( const FFToString&S )
{
  return FFToString(S,"log");
}

inline FFToString
xlog
( const FFToString&S )
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
			return FFToString(S,"xlogx");
		default:
	        return S * log(S);
	}
}

inline FFToString
fabsx_times_x
( const FFToString&S )
{
    switch (mc::FFToString::options.WRITING_LANGUAGE) {
        case mc::FFToString::ALE:
            return FFToString(S, "xabsx");
        default:
            return fabs(S)*S;
    }
}

inline FFToString
xexpax
(const FFToString& S, const double a)
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
			{
			std::ostringstream ostr;
			ostr << "xexpax(" << S << "," << std::setprecision(mc::FFToString::options.PRECISION) << a << ")";
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
			}
		default:
	        return S * exp(a * S);
	}
}

inline FFToString
centerline_deficit
(const FFToString& S, const double xLim, const double type)
{
  throw std::runtime_error("   mc::FFToString:\t centerline_deficit not implemented yet.");
  return S;
}

inline FFToString
wake_profile
(const FFToString& S, const double type)
{
  throw std::runtime_error("   mc::FFToString:\t wake_profile not implemented yet.");
  return S;
}

inline FFToString
wake_deficit
(const FFToString& S1, const FFToString& S2, const double a, const double alpha, const double rr, const double type1, const double type2)
{
  throw std::runtime_error("   mc::FFToString:\t wake_deficit not implemented yet.");
  return S1;
}

inline FFToString
power_curve
(const FFToString& S, const double type)
{
  throw std::runtime_error("   mc::FFToString:\t power_curve not implemented yet.");
  return S;
}

inline FFToString
lmtd
( const FFToString&S1, const FFToString&S2 )
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
			{
			std::ostringstream ostr;
			ostr << "lmtd(" << S1 << "," << S2 << ")";
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
			}
		default:
			return (S1-S2) / (log(S1)-log(S2));
	}
}

inline FFToString
rlmtd
( const FFToString&S1, const FFToString&S2 )
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
			{
			std::ostringstream ostr;
			ostr << "rlmtd(" << S1 << "," << S2 << ")";
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
			}
		default:
			return (S1-S2) / (log(S1)-log(S2));
	}
}

inline FFToString
mid
(const FFToString& S1, const FFToString& S2, const double k)
{
	return max(min(S1, S2), max(min(S1, k), min(S2, k)));
}

inline FFToString
pinch
(const FFToString& S1, const FFToString& S2, const FFToString& S3)
{
	return max(S1, S3) - max(S2, S3);
}


inline FFToString
euclidean_norm_2d
( const FFToString&S1, const FFToString&S2 )
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
			{
			std::ostringstream ostr;
			ostr << "norm2(" << S1 << "," << S2 << ")";
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
			}
		default:
	        return sqrt(sqr(S1)+sqr(S2));
	}
}

inline FFToString
expx_times_y
( const FFToString&S1, const FFToString&S2 )
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
			{
			std::ostringstream ostr;
			ostr << "xexpy(" << S2 << "," << S1 << ")";    // Note that variables are swapped in ALE
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
			}
		default:
	        return exp(S1)*S2;
	}
}

inline FFToString
vapor_pressure
( const FFToString&S, const double type, const double p1, const double p2, const double p3, const double p4 = 0,
  const double p5 = 0, const double p6 = 0, const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0)
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
		{
			std::ostringstream ostr;
			switch ((int)type) {
				case 1:
					ostr << "ext_antoine_psat(" << S << "," << std::setprecision(mc::FFToString::options.PRECISION) << p1 << ","
						<< std::setprecision(mc::FFToString::options.PRECISION) << p2 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p3 << ","
						<< std::setprecision(mc::FFToString::options.PRECISION) << p4 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p5 << ","
						<< std::setprecision(mc::FFToString::options.PRECISION) << p6 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p7 << ")";
						break;
				case 2:
					ostr << "antoine_psat(" << S << "," << std::setprecision(mc::FFToString::options.PRECISION) << p1 << ","
						<< std::setprecision(mc::FFToString::options.PRECISION) << p2 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p3 << ")";
					break;
				case 3:
					ostr << "wagner_psat(" << S << "," << std::setprecision(mc::FFToString::options.PRECISION) << p1 << ","
						<< std::setprecision(mc::FFToString::options.PRECISION) << p2 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p3 << ","
						<< std::setprecision(mc::FFToString::options.PRECISION) << p4 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p5 << ","
						<< std::setprecision(mc::FFToString::options.PRECISION) << p6 << ")";
					break;
				case 4:
					ostr << "ik_cape_psat(" << S << "," << std::setprecision(mc::FFToString::options.PRECISION) << p1 << ","
						<< std::setprecision(mc::FFToString::options.PRECISION) << p2 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p3 << ","
						<< std::setprecision(mc::FFToString::options.PRECISION) << p4 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p5 << ","
						<< std::setprecision(mc::FFToString::options.PRECISION) << p6 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p7 << ","
            << std::setprecision(mc::FFToString::options.PRECISION) << p8 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p9 << ","
            << std::setprecision(mc::FFToString::options.PRECISION) << p10 << ")";
					break;
				default:
					throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::VAPOR_PRESSURE);
			}
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
		}
		default:
	        switch((int)type){
				case 1: //Extended Antoine
				  return exp(p1+p2/(S+p3)+S*p4+p5*log(S)+p6*pow(S,p7));
				  break;

				case 2: //Antoine
				  return pow(10.,p1-p2/(p3+S));
				  break;

				case 3: //Wagner
				  {
				  FFToString Tr = S/p5;
				  return p6*exp((p1*(1-Tr)+p2*pow(1-Tr,1.5)+p3*pow(1-Tr,2.5)+p4*pow(1-Tr,5))/Tr);
				  break;
				  }
				case 4: // IK-CAPE
				  return exp(p1+p2*S+p3*pow(S,2)+p4*pow(S,3)+p5*pow(S,4)+p6*pow(S,5)+p7*pow(S,6)+p8*pow(S,7)+p9*pow(S,8)+p10*pow(S,9));
				  break;

				default:
				  throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::VAPOR_PRESSURE);
			  }
	}

}

inline FFToString
ideal_gas_enthalpy
( const FFToString&S, const double x0, const double type, const double p1, const double p2, const double p3, const double p4,
  const double p5, const double p6 = 0, const double p7 = 0)
{
	std::ostringstream ostr;
	if (x0<0) {
		ostr << "(" << std::setprecision(mc::FFToString::options.PRECISION) << x0 << ")";
	}
	else {
		ostr << std::setprecision(mc::FFToString::options.PRECISION) << x0;
	}
	FFToString x0str(ostr.str());
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
		{
			std::ostringstream ostr;
			switch ((int)type) {
			case 1:
				ostr << "aspen_hig("
					<< S << "," << x0str << "," << std::setprecision(mc::FFToString::options.PRECISION) << p1 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p2 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p3 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p4 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p5 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p6 << ")";
				break;
			case 2:
				ostr << "nasa9_hig("
					<< S << "," << x0str << "," << std::setprecision(mc::FFToString::options.PRECISION) << p1 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p2 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p3 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p4 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p5 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p6 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p7 << ")";
				break;
			case 3:
				ostr << "dippr107_hig("
					<< S << "," << x0str << "," << std::setprecision(mc::FFToString::options.PRECISION) << p1 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p2 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p3 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p4 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p5 << ")";
				break;
			case 4:
				ostr << "dippr127_hig("
					<< S << "," << x0str << "," << std::setprecision(mc::FFToString::options.PRECISION) << p1 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p2 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p3 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p4 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p5 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p6 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p7 << ")";
				break;
			default:
				throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::IDEAL_GAS_ENTHALPY);
			}
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
		}
		default:
	        switch ((int)type) {
				case 1: // Aspen polynomial (implementing only the high-temperature version); the NASA 7-coefficient polynomial is equivalent with the last parameter equal to 0
					return p1 * (S - x0str) + p2 / 2 * (pow(S, 2) - pow(x0str, 2)) + p3 / 3 * (pow(S, 3) - pow(x0str, 3)) + p4 / 4 * (pow(S, 4) - pow(x0str, 4)) + p5 / 5 * (pow(S, 5) - pow(x0str, 5)) + p6 / 6 * (pow(S, 6) - pow(x0str, 6));
					break;
				case 2: // NASA 9-coefficient polynomial
					return -p1 * (1 / S - 1 / x0str) + p2 * log(S / x0str) + p3 * (S - x0str) + p4 / 2 * (pow(S, 2) - pow(x0str, 2)) + p5 / 3 * (pow(S, 3) - pow(x0str, 3)) + p6 / 4 * (pow(S, 4) - pow(x0str, 4)) + p7 / 5 * (pow(S, 5) - pow(x0str, 5));
					break;
				case 3: // DIPPR 107 equation
					return p1 * (S - x0str) + p2 * p3*(1 / tanh(p3 / S) - 1 / tanh(p3 / x0str)) - p4 * p5*(tanh(p5 / S) - tanh(p5 / x0str));
					break;
				case 4: // DIPPR 127 equation
					return p1 * (S - x0str) + p2 * p3*(1 / (exp(p3 / S) - 1) - 1 / (exp(p3 / x0str) - 1)) + p4 * p5*(1 / (exp(p5 / S) - 1) - 1 / (exp(p5 / x0str) - 1)) + p6 * p7*(1 / (exp(p7 / S) - 1) - 1 / (exp(p7 / x0str) - 1));
					break;
				default:
					throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::IDEAL_GAS_ENTHALPY);
			}
	}
}

inline FFToString
saturation_temperature
( const FFToString&S, const double type, const double p1, const double p2, const double p3, const double p4 = 0,
  const double p5 = 0, const double p6 = 0, const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0)
{

	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
		{
			std::ostringstream ostr;
			switch ((int)type) {
			case 1:
				ostr << "ext_antoine_tsat(" << S << ", " << std::setprecision(mc::FFToString::options.PRECISION) << p1 << ", "
					<< std::setprecision(mc::FFToString::options.PRECISION) << p2 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p3 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p4 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p5 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p6 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p7 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p8 << ")";
					break;
			case 2:
				ostr << "antoine_tsat(" << S << ", " << std::setprecision(mc::FFToString::options.PRECISION) << p1 << ", "
					<< std::setprecision(mc::FFToString::options.PRECISION) << p2 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p3 << ")";
				break;
			case 3:
				ostr << "wagner_tsat(" << S << ", " << std::setprecision(mc::FFToString::options.PRECISION) << p1 << ", "
					<< std::setprecision(mc::FFToString::options.PRECISION) << p2 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p3 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p4 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p5 << ")";
				break;
			case 4:
				ostr << "ik_cape_tsat(" << S << ", " << std::setprecision(mc::FFToString::options.PRECISION) << p1 << ", "
					<< std::setprecision(mc::FFToString::options.PRECISION) << p2 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p3 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p4 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p5 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p6 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p7 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p8 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p9 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p10 << ")";
				break;

			default:
				throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::SATURATION_TEMPERATURE);
			}
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
		}
		default:
	        switch ((int)type) {
				case 1:
				case 3:
				case 4:
				{
					throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::SATURATION_TEMPERATURE);
					break;
				}
				case 2:
					return p2 / (p1 - log(S) / FFToString("log(10)",mc::FFToString::PRIO)) - p3;
					break;
				default:
					throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::SATURATION_TEMPERATURE);
			}
	}

}

inline FFToString
enthalpy_of_vaporization
( const FFToString&S, const double type, const double p1, const double p2, const double p3, const double p4,
  const double p5, const double p6 = 0 )
{
  FFToString::options.USED_ENTHALPY_OF_VAPORIZATION = true;
  switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
		{
			std::ostringstream ostr;
			switch ((int)type) {
			case 1:
				ostr << "watson_dhvap(" << S << "," << std::setprecision(mc::FFToString::options.PRECISION) << p1 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p2 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p3 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p4 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p5 << ")";
				break;
			case 2:
				ostr << "dippr106_dhvap(" << S << "," << std::setprecision(mc::FFToString::options.PRECISION) << p1 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p2 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p3 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p4 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p5 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p6 << ")";
				break;
			default:
				throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::ENTHALPY_OF_VAPORIZATION);

			}
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
		}
		default:
	        switch ((int)type) {
				case 1: // Watson equation
				{
					FFToString tmp1 = 1 - S / p1;	// this is 1-Tr
					return p5 * pow(tmp1 / (1 - p4 / p1), p2 + p3 * tmp1);
					break;
				}
				case 2: // DIPPR 106
				{
					FFToString Tr = S / p1;
					return p2 * pow(1 - Tr, p3 + p4 * Tr + p5 * pow(Tr, 2) + p6 * pow(Tr, 3));
					break;
				}
				default:
					throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::ENTHALPY_OF_VAPORIZATION);
			  }
	}

}

inline FFToString
cost_function
(const FFToString&S, const double type, const double p1, const double p2, const double p3)
{

	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
		{
			std::ostringstream ostr;
			ostr << "cost_";
			switch ((int)type) {
			case 1:
				ostr << "turton(" << S << "," << std::setprecision(mc::FFToString::options.PRECISION) << p1 << ","
					<< std::setprecision(mc::FFToString::options.PRECISION) << p2 << "," << std::setprecision(mc::FFToString::options.PRECISION) << p3 << ")";
				break;
			default:
				throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::COST_FUNCTION);
			}
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
		}
		default:
	        switch ((int)type) {
				case 1: // Guthrie cost function
				{
					return pow(10., p1 + p2 * log(S) / FFToString("log(10)",mc::FFToString::PRIO) + p3 * pow(log(S) / FFToString("log(10)",mc::FFToString::PRIO), 2));
					break;
				}
				default:
					throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::COST_FUNCTION);
			  }
	}

}

inline FFToString
covariance_function
( const FFToString&S, const double type )
{
  switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
		{
			std::ostringstream ostr;
			switch ((int)type) {
			case 1:
				ostr << "covar_matern_1(" << S << ")";
				break;
			case 2:
				ostr << "covar_matern_3(" << S << ")";
				break;
			case 3:
				ostr << "covar_matern_5(" << S << ")";
                break;
            case 4:
				ostr << "covar_sqrexp("   << S << ")";
			    break;
			default:
				throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::COVARIANCE_FUNCTION);

			}
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
		}
		default:
	        switch ((int)type) {
				case 1: // matern 1/2
				{
					return exp(-sqrt(S));
					break;
				}
				case 2: // matern 3/2
				{
					FFToString sqrt3 = FFToString("sqrt(3)",mc::FFToString::PRIO);
					return (1+sqrt3*sqrt(S))*exp(-sqrt3*sqrt(S));
					break;
				}
				case 3: // matern 5/2
				{
					FFToString sqrt5 = FFToString("sqrt(5)",mc::FFToString::PRIO);
					return (1+sqrt5*sqrt(S) + 5./3.*S)*exp(-sqrt5*sqrt(S));
					break;
				}
				case 4: // squared exponential
				{
					return exp(-0.5*S);
					break;
				}
				default:
					throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::COVARIANCE_FUNCTION);
			  }
	}
}

inline FFToString
acquisition_function
( const FFToString&S1, const FFToString&S2, const double type, const double fmin )
{
  switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
		{
			std::ostringstream ostr;
			switch ((int)type) {
			case 1:
				ostr << "af_lcb(" << S1 << "," << S2 << "," << fmin << ")";
				break;
			case 2:
				ostr << "af_ei(" << S1 << "," << S2 << "," << fmin << ")";
				break;
			case 3:
				ostr << "af_pi(" << S1 << "," << S2 << "," << fmin << ")";
                break;
			default:
				throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::ACQUISITION_FUNCTION);

			}
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
		}
		default:
	        switch ((int)type) {
				case 1: // lower confidence bound
				{
					return S1 - fmin*S2;
					break;
				}
				case 2: // expected improvement
				{
					FFToString sqrt2 = FFToString("1./sqrt(2)",mc::FFToString::PRIO);
					return (fmin-S1)*(erf(sqrt2*((fmin-S1)/S2))/2.+0.5) + S2*gaussian_probability_density_function((fmin-S1)/S2);
					break;
				}
				case 3: // probability of improvement
				{
					FFToString sqrt2 = FFToString("1./sqrt(2)",mc::FFToString::PRIO);
					return (erf(sqrt2*((fmin-S1)/S2))/2.+0.5);
					break;
				}
				default:
					throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::COVARIANCE_FUNCTION);
			  }
	}
}

inline FFToString
gaussian_probability_density_function
( const FFToString&S )
{
  switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
		{
			std::ostringstream ostr;
			ostr << "gpdf(" << S << ")";
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
		}
		default:
	        return 1./std::sqrt(2*mc::PI)*exp(-sqr(S)/2.);
	}
}


inline FFToString
regnormal
( const FFToString&S, const double a, const double b )
{
  switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
		{
			std::ostringstream ostr;
			ostr << "regnormal(" << S << "," << std::setprecision(mc::FFToString::options.PRECISION) << a << std::setprecision(mc::FFToString::options.PRECISION) << b << ")";
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
		}
		default:
	        return S / sqrt(a + b*sqr(S));
	}
}

inline FFToString
sum_div
(const std::vector< FFToString >& x, const std::vector<double>& coeff)
{
switch (mc::FFToString::options.WRITING_LANGUAGE) {
	case mc::FFToString::ALE:
	{
	std::ostringstream ostr;
	ostr << "sum_div(";
	for(int i=0; i<x.size(); i++){
	  ostr << x[i] << ",";
	}
	for(int i=0; i<coeff.size()-1; i++){
	  ostr << std::setprecision(mc::FFToString::options.PRECISION) << coeff[i] << ",";
	}
	ostr << std::setprecision(mc::FFToString::options.PRECISION) << coeff[coeff.size()-1] << ")";
	FFToString S3(ostr.str(), mc::FFToString::PRIO);
	return S3;
	}
	default:
	if(x.size()!=coeff.size()-1){
		throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::SUM_DIV);
	}

	FFToString dummy(coeff[1]*x[0]);
	for(unsigned int i=1; i<x.size(); i++){
		dummy += coeff[i+1]*x[i];
	}
	return (coeff[0]*x[0]/dummy);
}
}

inline FFToString
xlog_sum
(const std::vector< FFToString >& x, const std::vector<double>& coeff)
{
	if(x.size()!=coeff.size()){
		throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::XLOG_SUM);
	}
	switch (mc::FFToString::options.WRITING_LANGUAGE) {
		case mc::FFToString::ALE:
		{
			std::ostringstream ostr;
			ostr << "xlog_sum(";
			for (int i = 0; i < x.size(); i++) {
				ostr << x[i] << ",";
			}
			for (int i = 0; i < coeff.size() - 1; i++) {
				ostr << coeff[i] << ",";
			}
			ostr << coeff[coeff.size() - 1] << ")";
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
		}
		default:
			FFToString dummy(coeff[0] * x[0]);
			for (unsigned int i = 1; i < x.size(); i++) {
				dummy += coeff[i] * x[i];
			}
			return x[0] * log(dummy);
	}

}

inline FFToString
nrtl_tau
(const FFToString&S, const double a, const double b, const double e, const double f)
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
		{
			std::ostringstream ostr;
			ostr << "nrtl_tau(" << S << "," << std::setprecision(mc::FFToString::options.PRECISION) << a << ","
                 << std::setprecision(mc::FFToString::options.PRECISION) << b << "," << std::setprecision(mc::FFToString::options.PRECISION) << e << ","
				 << std::setprecision(mc::FFToString::options.PRECISION) << f << ")";
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
		}
		default:
			return a + b/S + e*log(S) + f*S;
	}
}

inline FFToString
nrtl_dtau
(const FFToString&S, const double b, const double e, const double f)
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
		{
			std::ostringstream ostr;
			ostr << "nrtl_dtau(" << S << "," << std::setprecision(mc::FFToString::options.PRECISION) << b << ","
                 << std::setprecision(mc::FFToString::options.PRECISION) << e << "," << std::setprecision(mc::FFToString::options.PRECISION) << f << ")";
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
		}
		default:
			return f - b/pow(S,2) + e/S;
	}
}

inline FFToString
nrtl_G
(const FFToString&S, const double a, const double b, const double e, const double f, const double alpha)
{
  switch(mc::FFToString::options.WRITING_LANGUAGE){
    case mc::FFToString::ALE:
      {
      std::ostringstream ostr;
      ostr << "nrtl_g(" << S << "," << std::setprecision(mc::FFToString::options.PRECISION) << a << ","
        << std::setprecision(mc::FFToString::options.PRECISION) << b << "," << std::setprecision(mc::FFToString::options.PRECISION) << e << ","
        << std::setprecision(mc::FFToString::options.PRECISION) << f << "," << std::setprecision(mc::FFToString::options.PRECISION) << alpha << ")";
      FFToString S3(ostr.str(), mc::FFToString::PRIO);
      return S3;
      }
    default:
      return exp( -alpha*nrtl_tau(S, a, b, e, f) );
  }
}

inline FFToString
nrtl_Gtau
(const FFToString&S, const double a, const double b, const double e, const double f, const double alpha)
{
  switch(mc::FFToString::options.WRITING_LANGUAGE){
    case mc::FFToString::ALE:
      {
      std::ostringstream ostr;
      ostr << "nrtl_gtau(" << S << "," << std::setprecision(mc::FFToString::options.PRECISION) << a << ","
        << std::setprecision(mc::FFToString::options.PRECISION) << b << "," << std::setprecision(mc::FFToString::options.PRECISION) << e << ","
        << std::setprecision(mc::FFToString::options.PRECISION) << f << "," << std::setprecision(mc::FFToString::options.PRECISION) << alpha << ")";
      FFToString S3(ostr.str(), mc::FFToString::PRIO);
      return S3;
      }
    default:
      return xexpax(nrtl_tau(S,a,b,e,f),-alpha);
  }
}

inline FFToString
nrtl_Gdtau
(const FFToString&S, const double a, const double b, const double e, const double f, const double alpha)
{
  switch(mc::FFToString::options.WRITING_LANGUAGE){
    case mc::FFToString::ALE:
      {
      std::ostringstream ostr;
      ostr << "nrtl_gdtau(" << S << "," << std::setprecision(mc::FFToString::options.PRECISION) << a << ","
        << std::setprecision(mc::FFToString::options.PRECISION) << b << "," << std::setprecision(mc::FFToString::options.PRECISION) << e << ","
        << std::setprecision(mc::FFToString::options.PRECISION) << f << "," << std::setprecision(mc::FFToString::options.PRECISION) << alpha << ")";
      FFToString S3(ostr.str(), mc::FFToString::PRIO);
      return S3;
      }
    default:
      return nrtl_G(S,a,b,e,f,alpha)*nrtl_dtau(S,b,e,f);
  }
}

inline FFToString
nrtl_dGtau
(const FFToString&S, const double a, const double b, const double e, const double f, const double alpha)
{
  switch(mc::FFToString::options.WRITING_LANGUAGE){
    case mc::FFToString::ALE:
      {
      std::ostringstream ostr;
      ostr << "nrtl_dgtau(" << S << "," << std::setprecision(mc::FFToString::options.PRECISION) << a << ","
        << std::setprecision(mc::FFToString::options.PRECISION) << b << "," << std::setprecision(mc::FFToString::options.PRECISION) << e << ","
        << std::setprecision(mc::FFToString::options.PRECISION) << f << "," << std::setprecision(mc::FFToString::options.PRECISION) << alpha << ")";
      FFToString S3(ostr.str(), mc::FFToString::PRIO);
      return S3;
      }
    default:
      return -alpha*nrtl_Gtau(S,a,b,e,f,alpha)*nrtl_dtau(S,b,e,f);
  }
}

inline FFToString
p_sat_ethanol_schroeder
( const FFToString&S )
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
			return FFToString(S,"schroeder_ethanol_p");
		default:
			{
				const double _T_c_K = 514.71;
				const double _N_Tsat_1 = -8.94161;
				const double _N_Tsat_2 = 1.61761;
				const double _N_Tsat_3 = -51.1428;
				const double _N_Tsat_4 = 53.1360;
				const double _k_Tsat_1 = 1.0;
				const double _k_Tsat_2 = 1.5;
				const double _k_Tsat_3 = 3.4;
				const double _k_Tsat_4 = 3.7;
				const double _p_c = 62.68;

				return _p_c*(exp(_T_c_K/S*(_N_Tsat_1*pow((1-S/_T_c_K),_k_Tsat_1) + _N_Tsat_2*pow((1-S/_T_c_K),_k_Tsat_2) + _N_Tsat_3*pow((1-S/_T_c_K),_k_Tsat_3) + _N_Tsat_4*pow((1-S/_T_c_K),_k_Tsat_4))));
			}
	}
}

inline FFToString
rho_vap_sat_ethanol_schroeder
( const FFToString&S )
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
			return FFToString(S,"schroeder_ethanol_rhovap");
		default:
			{
				const double _T_c_K = 514.71;
				const double _N_vap_1 = -1.75362;
				const double _N_vap_2 = -10.5323;
				const double _N_vap_3 = -37.6407;
				const double _N_vap_4 = -129.762;
				const double _k_vap_1 = 0.21;
				const double _k_vap_2 = 1.1;
				const double _k_vap_3 = 3.4;
				const double _k_vap_4 = 10;
				const double _rho_c = 273.195;

				return _rho_c*(exp(_N_vap_1*pow((1 - S/_T_c_K),_k_vap_1) + _N_vap_2*pow((1 - S/_T_c_K),_k_vap_2) + _N_vap_3*pow((1 - S/_T_c_K),_k_vap_3) + _N_vap_4*pow((1 - S/_T_c_K),_k_vap_4)));
			}
	}
}

inline FFToString
rho_liq_sat_ethanol_schroeder
( const FFToString&S )
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
			return FFToString(S,"schroeder_ethanol_rholiq");
		default:
			{
				const double _T_c_K = 514.71;
				const double _N_liq_1=9.00921;
				const double _N_liq_2=-23.1668;
				const double _N_liq_3=30.9092;
				const double _N_liq_4=-16.5459;
				const double _N_liq_5=3.64294;
				const double _k_liq_1=0.5;
				const double _k_liq_2=0.8;
				const double _k_liq_3=1.1;
				const double _k_liq_4=1.5;
				const double _k_liq_5=3.3;
				const double _rho_c = 273.195;

				return _rho_c*(1 + _N_liq_1*pow((1 - S/_T_c_K),_k_liq_1) + _N_liq_2*pow((1 - S/_T_c_K),_k_liq_2) + _N_liq_3*pow((1 - S/_T_c_K),_k_liq_3) + _N_liq_4*pow((1 - S/_T_c_K),_k_liq_4) + _N_liq_5*pow((1 - S/_T_c_K),_k_liq_5));
			}
	}
}

inline FFToString
erf
( const FFToString &S )
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
			return FFToString(S,"erf");
		default:
			return FFToString(S,"errorf");
	}
}

inline FFToString
erfc
( const FFToString &S )
{
  switch(mc::FFToString::options.WRITING_LANGUAGE){
    case mc::FFToString::ALE:
      return FFToString(S,"erfc");
    default:
      return 1-erf(S);
  }
}

inline FFToString
fstep
( const FFToString &S )
{
  throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::UNSUPPORTED_FUNCTION);
  return S;
}

inline FFToString
bstep
( const FFToString &S )
{
  throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::UNSUPPORTED_FUNCTION);
  return S;
}

inline FFToString
fabs
( const FFToString&S )
{
	return FFToString(S,"abs");
}

inline FFToString
cheb
( const FFToString&S, const unsigned n )
{
	std::ostringstream ostr;
	switch( n ){
    case 0:  return FFToString(1.);
    case 1:  return S;
    case 2:  return 2.*S*S-1.;
    default: return 2.*S*cheb(S,n-1)-cheb(S,n-2);
	}
}

inline FFToString
pow
( const FFToString&S, const int n )
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
			switch (n){
			case 0:
				return FFToString(1.);
			case 1:
				return S;
			default:
				{
				std::ostringstream ostr;
				ostr << "(" << S << ")^(" << n << ")";
				FFToString S2(ostr.str(), mc::FFToString::PRIO);
				return S2;
				}
			}
		case mc::FFToString::GAMS:
		default:
			switch (n){
			case 0:
				return FFToString(1.);
			case 1:
				return S;
			default:
				{
				std::ostringstream ostr;
				ostr << "power(" << S << "," << n << ")";
				FFToString S2(ostr.str(), mc::FFToString::PRIO);
				return S2;
				}
			}
	}
}

inline FFToString
pow
( const FFToString&S, const double a )
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
			{
			if(a==0){return FFToString(1.);}
			if(a==1){return S;}
			std::ostringstream ostr;
			ostr << "(" << S << ")^(" << a << ")";
			FFToString S2(ostr.str(), mc::FFToString::PRIO);
			return S2;
			}
		default:
			return exp(a * log(S));
	}
}

inline FFToString
pow
( const FFToString&S1, const FFToString&S2 )
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
			{
			std::ostringstream ostr;
			ostr << "(" << S1 << ")^(" << S2 << ")";
			FFToString S3(ostr.str(), mc::FFToString::PRIO);
			return S3;
			}
		default:
			return exp( S2 * log( S1 ) );
	}
}

inline FFToString
pow
( const double a, const FFToString &S )
{
	switch(mc::FFToString::options.WRITING_LANGUAGE){
		case mc::FFToString::ALE:
			{
			std::ostringstream ostr;
			ostr << "(" << a << ")^(" << S << ")";
			FFToString S2(ostr.str(), mc::FFToString::PRIO);
			return S2;
			}
		default:
			return exp(S * log(FFToString(a)));
	}
}

inline FFToString
min
( const FFToString&S1, const FFToString&S2 )
{
	std::ostringstream ostr;
	FFToString S3;
	if(mc::FFToString::options.USE_MIN_MAX){
		ostr << "min(" << S1 << "," << S2 << ")";
		S3 = ostr.str();
		S3.set_optype(mc::FFToString::PRIO);
	} else {
		S3 = (0.5 * (S1 + S2 - fabs(S1-S2)));
	}
	return S3;
}

inline FFToString
max
( const FFToString&S1, const FFToString&S2 )
{
	std::ostringstream ostr;
	FFToString S3;
	if(mc::FFToString::options.USE_MIN_MAX){
		ostr << "max(" << S1 << "," << S2 << ")";
		S3 = ostr.str();
		S3.set_optype(mc::FFToString::PRIO);
	} else {
		S3 = (0.5 * (S1 + S2 + fabs(S1-S2)));
	}
	return S3;
}

inline FFToString
min
( const unsigned int n, const FFToString*S )
{
  if(n == 0){
    return FFToString();
  } else if (n == 1){
    return S[0];
  } else {
    return min(min(n-1,S),S[n-1]);
  }

}

inline FFToString
max
( const unsigned int n, const FFToString*S )
{
  if(n == 0){
    return FFToString();
  } else if (n == 1){
    return S[0];
  }
  else {
	  return max(max(n - 1, S), S[n - 1]);
  }
}

inline FFToString
pos
( const FFToString&S )
{
	if(mc::FFToString::options.IGNORE_BOUNDING_FUNCS){
		return S;
	} else {
		return FFToString(S,"pos");
	}
}

inline FFToString
neg
(const FFToString&S)
{
	if(mc::FFToString::options.IGNORE_BOUNDING_FUNCS){
		return S;
	} else {
		return FFToString(S,"neg");
	}
}

inline FFToString
lb_func
(const FFToString&S, const double lb)
{
  if(mc::FFToString::options.IGNORE_BOUNDING_FUNCS){
    return S;
  }else {
    std::ostringstream ostr;
    ostr << "lb_func(" << S << ",";
    ostr << std::setprecision(mc::FFToString::options.PRECISION) << lb << ")";
    FFToString S3(ostr.str(),mc::FFToString::PRIO);
    return S3;
  }
}


inline FFToString
ub_func
(const FFToString&S, const double ub)
{
  if(mc::FFToString::options.IGNORE_BOUNDING_FUNCS){
    return S;
  } else {
    std::ostringstream ostr;
    ostr << "ub_func(" << S << ",";
    ostr << std::setprecision(mc::FFToString::options.PRECISION) << ub << ")";
    FFToString S3(ostr.str(),mc::FFToString::PRIO);
    return S3;
  }
}

inline FFToString
bounding_func
(const FFToString&S, const double lb, const double ub)
{
  if(mc::FFToString::options.IGNORE_BOUNDING_FUNCS){
    return S;
  } else {
    switch(mc::FFToString::options.WRITING_LANGUAGE){
      case mc::FFToString::ALE:
      {
        std::ostringstream ostr;
        ostr << "bounding_func(" << S << ",";
        ostr << std::setprecision(mc::FFToString::options.PRECISION) << lb << ","
          << std::setprecision(mc::FFToString::options.PRECISION) << ub << ")";
        FFToString S3(ostr.str(),mc::FFToString::PRIO);
        return S3;
      }
      default:
        return mc::ub_func(mc::lb_func(S,lb),ub);
    }
  }
}

inline FFToString
squash_node
(const FFToString&S, const double lb, const double ub)
{
  if(mc::FFToString::options.IGNORE_BOUNDING_FUNCS){
    return S;
  } else {
    std::ostringstream ostr;
    switch (mc::FFToString::options.WRITING_LANGUAGE) {
    case mc::FFToString::ALE:
        ostr << "squash(";
        break;
    default:
        ostr << "squash_node(";
    }
    ostr << S << ",";
    ostr << std::setprecision(mc::FFToString::options.PRECISION) << lb << ",";
    ostr << std::setprecision(mc::FFToString::options.PRECISION) << ub << ")";
    FFToString S3(ostr.str(), mc::FFToString::PRIO);
    return S3;
  }
}

inline FFToString
single_neuron
( const std::vector< FFToString >& x, const std::vector<double>& w, const double b, const int type)
{
  switch (mc::FFToString::options.WRITING_LANGUAGE) {
    case mc::FFToString::ALE:
	{
	  std::ostringstream ostr;
	  ostr << "single_neuron(";
	  for(int i=0; i<x.size(); i++){
	    ostr << x[i] << ",";
	  }
	  for(int i=0; i<w.size(); i++){
		ostr << std::setprecision(mc::FFToString::options.PRECISION) << w[i] << ",";
	  }
	  ostr << std::setprecision(mc::FFToString::options.PRECISION) << b << "," << type << ")";
	  FFToString S3(ostr.str(), mc::FFToString::PRIO);
	  return S3;
	}
	default:
	  if(x.size()!=w.size()){
		throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::SINGLE_NEURON);
	  }
	  FFToString dummy(b);
	  for(unsigned int i=0; i<x.size(); i++){
		dummy += w[i]*x[i];
	  }
	  return 1 - 2/(exp(2*dummy)+1);
  }
}

inline FFToString
mc_print
(const FFToString&S, const int number)
{
  throw typename mc::FFToString::Exceptions(mc::FFToString::Exceptions::UNSUPPORTED_FUNCTION);
  return S;
}

inline FFToString
cos
( const FFToString&S )
{
  return FFToString(S,"cos");
}

inline FFToString
sin
( const FFToString &S )
{
  return FFToString(S,"sin");
}

inline FFToString
tan
( const FFToString&S )
{
  return FFToString(S,"tan");
}

inline FFToString
acos
( const FFToString &S )
{
	switch (mc::FFToString::options.WRITING_LANGUAGE) {
		case mc::FFToString::ALE:
			return FFToString(S,"acos");
		default:
			return FFToString(S,"arccos");
	}
}

inline FFToString
asin
( const FFToString &S )
{
	switch (mc::FFToString::options.WRITING_LANGUAGE) {
		case mc::FFToString::ALE:
			return FFToString(S,"asin");
		default:
			return FFToString(S,"arcsin");
	}
}

inline FFToString
atan
( const FFToString &S )
{
	switch (mc::FFToString::options.WRITING_LANGUAGE) {
		case mc::FFToString::ALE:
			return FFToString(S,"atan");
		default:
			return FFToString(S,"arctan");
	}
}

inline FFToString
cosh
( const FFToString &S )
{
  if(mc::FFToString::options.USE_TRIG){
    return FFToString(S,"cosh");
  } else {
    return (exp(S)+exp(-S))/2;
  }
}

inline FFToString
sinh
( const FFToString &S )
{
  if(mc::FFToString::options.USE_TRIG){
    return FFToString(S,"sinh");
  } else {
    return (exp(S)-exp(-S))/2;
  }
}

inline FFToString
tanh
( const FFToString &S )
{
  if(mc::FFToString::options.USE_TRIG){
    return FFToString(S,"tanh");
  } else {
    return 1 - 2/(exp(2*S)+1);
  }
}

inline FFToString
coth
( const FFToString &S )
{
  if(mc::FFToString::options.USE_TRIG){
      switch (mc::FFToString::options.WRITING_LANGUAGE) {
      case mc::FFToString::ALE:
          return FFToString(S, "coth");
      default:
          return 1+2/(exp(2*S)-1);
      }
  } else {
    return 1+2/(exp(2*S)-1);
  }
}

inline bool
operator==
( const FFToString&S1, const FFToString&S2 )
{
	return S1.name().str().compare(S2.name().str())==0;
}

inline bool
operator!=
( const FFToString&S1, const FFToString&S2 )
{
	return !(S1==S2);
}

inline bool
operator<=
( const FFToString&S1, const FFToString&S2 )
{
	return S1.get_function_string().length() <= S2.get_function_string().length();
}

inline bool
operator>=
( const FFToString&S1, const FFToString&S2 )
{
	return S1.get_function_string().length() >= S2.get_function_string().length();
}

inline bool
operator<
( const FFToString&S1, const FFToString&S2 )
{
	return S1.get_function_string().length() < S2.get_function_string().length();
}

inline bool
operator>
( const FFToString&S1, const FFToString&S2 )
{
	return S1.get_function_string().length() > S2.get_function_string().length();
}

typename FFToString::Options FFToString::options;

} // namespace mc

namespace mc
{

//! @brief Specialization of the structure mc::Op to allow usage of the type mc::Interval for DAG evaluation or as a template parameter in other MC++ classes
template <> struct Op< mc::FFToString >
{
  typedef mc::FFToString FS;
  static FS point( const double c ) { return FS(c); }
  static FS zeroone() { throw  FFToString::Exceptions( FFToString::Exceptions::UNSUPPORTED_FUNCTION ); }
  static void I(FS& x, const FS&y) { x = y; }
  static double l(const FS& x) { throw FFToString::Exceptions( FFToString::Exceptions::UNSUPPORTED_FUNCTION ); }
  static double u(const FS& x) { throw FFToString::Exceptions( FFToString::Exceptions::UNSUPPORTED_FUNCTION ); }
  static double abs (const FS& x) { throw FFToString::Exceptions( FFToString::Exceptions::UNSUPPORTED_FUNCTION );  }
  static double mid (const FS& x) { throw FFToString::Exceptions( FFToString::Exceptions::UNSUPPORTED_FUNCTION );  }
  static double diam(const FS& x) { throw FFToString::Exceptions( FFToString::Exceptions::UNSUPPORTED_FUNCTION ); }
  static FS inv (const FS& x) { return mc::inv(x);  }
  static FS sqr (const FS& x) { return mc::sqr(x);  }
  static FS sqrt(const FS& x) { return mc::sqrt(x); }
  static FS exp (const FS& x) { return mc::exp(x);  }
  static FS log (const FS& x) { return mc::log(x);  }
  static FS xlog(const FS& x) { return mc::xlog(x); }
  static FS fabsx_times_x(const FS& x) { return mc::fabsx_times_x(x); }
  static FS xexpax(const FS& x, const double a) { return mc::xexpax(x,a); }
  static FS centerline_deficit(const FS& x, const double xLim, const double type) { return mc::centerline_deficit(x,xLim,type); }
  static FS wake_profile(const FS& x, const double type) { return mc::wake_profile(x,type); }
  static FS wake_deficit(const FS& x, const FS& r, const double a, const double alpha, const double rr, const double type1, const double type2) { return mc::wake_deficit(x,r,a,alpha,rr,type1,type2); }
  static FS power_curve(const FS& x, const double type) { return mc::power_curve(x,type); }
  static FS lmtd(const FS& x, const FS& y) { return mc::lmtd(x,y); }
  static FS rlmtd(const FS& x, const FS& y) { return mc::rlmtd(x,y); }
  static FS mid(const FS& x, const FS& y, const double k) { return mc::mid(x, y, k); } 
  static FS pinch(const FS& Th, const FS& Tc, const FS& Tp) { return mc::pinch(Th, Tc, Tp); }
  static FS euclidean_norm_2d(const FS& x, const FS& y) { return mc::euclidean_norm_2d(x,y); }
  static FS expx_times_y(const FS& x, const FS& y) { return mc::expx_times_y(x,y); }
  static FS vapor_pressure(const FS& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
                 const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return mc::vapor_pressure(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10); }
  static FS ideal_gas_enthalpy(const FS& x, const double x0, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0,
                 const double p7 = 0) { return mc::ideal_gas_enthalpy(x,x0,type,p1,p2,p3,p4,p5,p6,p7); }
  static FS saturation_temperature(const FS& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
                 const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return mc::saturation_temperature(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10);}
  static FS enthalpy_of_vaporization(const FS& x, const double type, const double p1, const double p2, const double p3,
                                     const double p4, const double p5, const double p6 = 0) { return mc::enthalpy_of_vaporization(x,type,p1,p2,p3,p4,p5,p6); }
  static FS cost_function(const FS&x, const double type, const double p1, const double p2, const double p3) { return mc::cost_function(x, type, p1, p2, p3); }
  static FS sum_div(const std::vector< FS >& x, const std::vector<double>& coeff) { return mc::sum_div(x,coeff); }
  static FS xlog_sum(const std::vector< FS >& x, const std::vector<double>& coeff) { return mc::xlog_sum(x,coeff); }
  static FS nrtl_tau(const FS& x, const double a, const double b, const double e, const double f) { return mc::nrtl_tau(x,a,b,e,f); }
  static FS nrtl_dtau(const FS& x, const double b, const double e, const double f) { return mc::nrtl_dtau(x,b,e,f); }
  static FS nrtl_G(const FS& x, const double a, const double b, const double e, const double f, const double alpha) { return mc::nrtl_G(x,a,b,e,f,alpha); }
  static FS nrtl_Gtau(const FS& x, const double a, const double b, const double e, const double f, const double alpha) { return mc::nrtl_Gtau(x,a,b,e,f,alpha); }
  static FS nrtl_Gdtau(const FS& x, const double a, const double b, const double e, const double f, const double alpha) { return mc::nrtl_Gdtau(x,a,b,e,f,alpha); }
  static FS nrtl_dGtau(const FS& x, const double a, const double b, const double e, const double f, const double alpha) { return mc::nrtl_dGtau(x,a,b,e,f,alpha); }
  static FS iapws(const FS& x, const double type) { throw std::runtime_error("FFToString::iawps -- operation not implemented"); }
  static FS iapws(const FS& x, const FS& y, const double type) { throw std::runtime_error("FFToString::iawps -- operation not implemented"); }
  static FS p_sat_ethanol_schroeder(const FS& x) { return mc::p_sat_ethanol_schroeder(x); }
  static FS rho_vap_sat_ethanol_schroeder(const FS& x) { return mc::rho_vap_sat_ethanol_schroeder(x); }
  static FS rho_liq_sat_ethanol_schroeder(const FS& x) { return mc::rho_liq_sat_ethanol_schroeder(x); }
  static FS covariance_function(const FS& x, const double type) { return mc::covariance_function(x,type); }
  static FS acquisition_function(const FS& x, const FS& y, const double type, const double fmin) { return mc::acquisition_function(x,y,type,fmin); }
  static FS gaussian_probability_density_function(const FS& x) { return mc::gaussian_probability_density_function(x); }
  static FS regnormal(const FS& x, const double a, const double b) { return mc::regnormal(x,a,b); }
  static FS fabs(const FS& x) { return mc::fabs(x); }
  static FS sin (const FS& x) { return mc::sin(x);  }
  static FS cos (const FS& x) { return mc::cos(x);  }
  static FS tan (const FS& x) { return mc::tan(x);  }
  static FS asin(const FS& x) { return mc::asin(x); }
  static FS acos(const FS& x) { return mc::acos(x); }
  static FS atan(const FS& x) { return mc::atan(x); }
  static FS sinh(const FS& x) { return mc::sinh(x); }
  static FS cosh(const FS& x) { return mc::cosh(x); }
  static FS tanh(const FS& x) { return mc::tanh(x); }
  static FS coth(const FS& x) { return mc::coth(x); }
  static FS asinh(const FS& x) { throw std::runtime_error("FFToString::asinh -- operation not implemented"); }
  static FS acosh(const FS& x) { throw std::runtime_error("FFToString::acosh -- operation not implemented"); }
  static FS atanh(const FS& x) { throw std::runtime_error("FFToString::atanh -- operation not implemented"); }
  static FS acoth(const FS& x) { throw std::runtime_error("FFToString::acoth -- operation not implemented"); }
  static FS erf (const FS& x) { return mc::erf(x);  }
  static FS erfc(const FS& x) { return mc::erfc(x); }
  static FS fstep(const FS& x) { return mc::fstep(x); }
  static FS bstep(const FS& x) { return mc::bstep(x); }
  static FS hull(const FS& x, const FS& y) { throw std::runtime_error("FFToString::hull -- operation not implemented"); }
  static FS min (const FS& x, const FS& y) { return mc::min(x,y);  }
  static FS max (const FS& x, const FS& y) { return mc::max(x,y);  }
  static FS pos (const FS& x) { return mc::pos(x);  }
  static FS neg (const FS& x) { return mc::neg(x);  }
  static FS lb_func(const FS& x, const double lb) { return mc::lb_func(x,lb); }
  static FS ub_func(const FS& x, const double ub) { return mc::ub_func(x,ub); }
  static FS bounding_func (const FS& x, const double lb, const double ub) { return mc::bounding_func(x, lb, ub); }
  static FS squash_node (const FS& x, const double lb, const double ub) { return mc::squash_node(x,lb,ub);  }
  static FS single_neuron (const std::vector< FS >& x, const std::vector<double>& w, const double b, const int type) { return mc::single_neuron(x,w,b,type);  }
  static FS mc_print(const FS& x, const int number) { return mc::mc_print(x,number); }
  static FS arh (const FS& x, const double k) { return mc::arh(x,k); }
  template <typename X, typename Y> static FS pow(const X& x, const Y& y) { return mc::pow(x,y); }
  static FS cheb(const FS& x, const unsigned n) { return mc::cheb(x,n); }
  static FS prod(const unsigned int n, const FS* x) { return mc::prod(n,x); }
  static FS monom(const unsigned int n, const FS* x, const unsigned* k) { return mc::monom(n,x,k); }
  static bool inter(FS& xIy, const FS& x, const FS& y) { throw std::runtime_error("FFToString::inter -- operation not implemented"); }
  static bool eq(const FS& x, const FS& y) { throw  FFToString::Exceptions( FFToString::Exceptions::UNSUPPORTED_FUNCTION ); }
  static bool ne(const FS& x, const FS& y) { throw  FFToString::Exceptions( FFToString::Exceptions::UNSUPPORTED_FUNCTION ); }
  static bool lt(const FS& x, const FS& y) { throw  FFToString::Exceptions( FFToString::Exceptions::UNSUPPORTED_FUNCTION ); }
  static bool le(const FS& x, const FS& y) { throw  FFToString::Exceptions( FFToString::Exceptions::UNSUPPORTED_FUNCTION ); }
  static bool gt(const FS& x, const FS& y) { throw  FFToString::Exceptions( FFToString::Exceptions::UNSUPPORTED_FUNCTION ); }
  static bool ge(const FS& x, const FS& y) { throw  FFToString::Exceptions( FFToString::Exceptions::UNSUPPORTED_FUNCTION ); }
};

} // namespace mc


#endif
