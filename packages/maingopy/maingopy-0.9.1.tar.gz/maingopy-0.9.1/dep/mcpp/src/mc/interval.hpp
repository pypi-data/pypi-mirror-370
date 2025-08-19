// Copyright (C) 2009-2017 Benoit Chachuat, Imperial College London.
// All Rights Reserved.
// This code is published under the Eclipse Public License.

/*!
\page page_INTERVAL Non-Verified Interval Arithmetic for Factorable Functions
\author Beno&icirc;t Chachuat

Computational methods for enclosing the range of functions find their origins in interval analysis back in the early 1960s [Moore, 1966; Moore <I>et al.</I>, 2009]. For functions whose expressions can be broken down into a finite number of elementary unary and binary operations, namely factorable functions, interval bounding can be readily automated. The class mc::Interval provides a basic implementation of interval arithmetic, which is <B>not a verified implementation</B> in the sense that rounding errors are not accounted for. For verified interval computations, it is strongly recommended to use third-party libraries such as <A href="http://www.ti3.tu-harburg.de/Software/PROFILEnglisch.html">PROFIL</A> or <A href="http://www.math.uni-wuppertal.de/~xsc/software/filib.html">FILIB++</A>.

The implementation of mc::Interval relies on the operator/function overloading mechanism of C++. This makes the computation of bounds both simple and intuitive, similar to computing function values in real arithmetics. Moreover, mc::Interval can be used as the underlying interval type in other classes of MC++ via templates; e.g., mc::McCormick<mc::Interval>, mc::TModel<mc::Interval>, mc::TVar<mc::Interval>.


\section sec_INTERVAL_use How do I compute interval bounds on the range of a factorable function?

Suppose we want to calculate bounds on the range of the real-valued function \f$f(x,y)=x(\exp(x)-y)^2\f$ for \f$(x,y)\in [-2,1]^2\f$.

First, we shall define the variables \f$x\f$ and \f$y\f$. This is done as follows:

\code
      #include "interval.hpp"
      typedef mc::Interval I;

      I X( -2., 1. );
      I Y( -2., 1. );
\endcode

Essentially, the last two lines mean that <tt>X</tt> and <tt>Y</tt> are variable of type mc::Interval, both defined as \f$[-2,1]\f$.

Having defined the variables, bounds on the range of \f$f\f$ on \f$[-2,1]^2\f$ are simply calculated as

\code
      I F = X*pow(exp(X)-Y,2);
\endcode

These bounds can be displayed to the standard output as:

\code
      std::cout << "F bounds: " << F << std::endl;
\endcode

which produces the following output:

\verbatim
F bounds: [ -4.45244e+01 :  2.22622e+01 ]
\endverbatim

Moreover, the upper and lower bounds in the interval bound <a>F</a> can be retrieved as:

\code
      double Fl = IF.l();
      double Fu = IF.u();
\endcode <tt>exp</tt>,


\section sec_INTERVAL_fct Which functions are overloaded in mc::Interval?

mc::Interval overloads the usual functions <tt>exp</tt>, <tt>log</tt>, <tt>sqr</tt>, <tt>sqrt</tt>, <tt>pow</tt>, <tt>inv</tt>, <tt>cos</tt>, <tt>sin</tt>, <tt>tan</tt>, <tt>acos</tt>, <tt>asin</tt>, <tt>atan</tt>, <tt>erf</tt>, <tt>erfc</tt>, <tt>min</tt>, <tt>max</tt>, <tt>fabs</tt>. mc::Interval also defines the following functions:
- <tt>inter(Z,X,Y)</tt>, computing the intersection \f$Z = X\cap Y\f$ and returning true/false if the intersection is nonempty/empty
- <tt>hull(X,Y)</tt>, returning the interval hull of \f$X\cup Y\f$
- <tt>diam(X)</tt>, returning the diameter of \f$X\f$
- <tt>mid(X)</tt>, returning the mid-point of \f$X\f$
- <tt>abs(X)</tt>, returning the absolute value of \f$X\f$
.


\section sec_INTERVAL_opt What are the options in mc::Interval and how are they set?

The class mc::Interval has a public static member called mc::Interval::options that can be used to set/modify the options; e.g.,

\code
      mc::Interval::options.DISPLAY_DIGITS = 7;
\endcode

The available options are as follows:

<TABLE border="1">
<CAPTION><EM>Options in mc::Interval::Options: name, type and description</EM></CAPTION>
     <TR><TH><b>Name</b>  <TD><b>Type</b><TD><b>Default</b>
         <TD><b>Description</b>
     <TR><TH><tt>DISPLAY_DIGITS</tt> <TD><tt>unsigned int</tt> <TD>5
         <TD>Number of digits in output stream
</TABLE>


\section sec_INTERVAL_err What errors can be encountered in using mc::Interval?

Errors are managed based on the exception handling mechanism of the C++ language. Each time an error is encountered, a class object of type Interval::Exceptions is thrown, which contains the type of error.

Possible errors encountered in using mc::Interval are:

<TABLE border="1">
<CAPTION><EM>Exceptions in mc::Interval</EM></CAPTION>
     <TR><TH><b>Number</b> <TD><b>Description</b>
     <TR><TH><tt>1</tt> <TD>Division by zero
     <TR><TH><tt>2</tt> <TD>Inverse with zero in range
     <TR><TH><tt>3</tt> <TD>Log with negative values in range
     <TR><TH><tt>4</tt> <TD>Square-root with nonpositive values in range
     <TR><TH><tt>5</tt> <TD>Inverse cosine with values outside of [-1,1] range
     <TR><TH><tt>6</tt> <TD>Inverse sine with values outside of [-1,1] range
     <TR><TH><tt>7</tt> <TD>Tangent with values \f$\frac{\pi}{2}+k\,\pi\f$, with \f$k\in\mathbb{Z}\f$, in range
</TABLE>

\section sec_INTERVAL_refs References

- Moore, R.E., <I><A href="http://books.google.co.uk/books/about/Interval_analysis.html?id=csQ-AAAAIAAJ&redir_esc=y2">"Interval Analysis"</A></I>, Prentice-Hall, 1966
- Moore, R.E., M.J. Cloud, R.B. Kearfott, <I><A href="http://books.google.co.uk/books/about/Introduction_to_interval_analysis.html?id=tT7ykKbqfEwC&redir_esc=y">"Introduction to Interval Analysis"</A></I>, SIAM, 2009
.

*/

#ifndef MC__INTERVAL_HPP
#define MC__INTERVAL_HPP

#include <iostream>
#include <iomanip>
#include <stdarg.h>

#include "mcfunc.hpp"
#include "library_of_functions.hpp"
#include "library_of_inverse_functions.hpp"

namespace mc
{
//! @brief C++ class for (non-verified) interval bounding of factorable function
////////////////////////////////////////////////////////////////////////
//! mc::Interval is a C++ class for interval bounding of factorable
//! functions on a box based on natural interval extensions. Round-off
//! errors are not accounted for in the computations (non-verified
//! implementation).
////////////////////////////////////////////////////////////////////////
class Interval
////////////////////////////////////////////////////////////////////////
{
  // friends of class Interval for operator overloading
  friend Interval operator+
    ( const Interval& );
  friend Interval operator+
    ( const Interval&, const Interval& );
  friend Interval operator+
    ( const double, const Interval& );
  friend Interval operator+
    ( const Interval&, const double );
  friend Interval operator-
    ( const Interval& );
  friend Interval operator-
    ( const Interval&, const Interval& );
  friend Interval operator-
    ( const double, const Interval& );
  friend Interval operator-
    ( const Interval&, const double );
  friend Interval operator*
    ( const Interval&, const Interval& );
  friend Interval operator*
    ( const Interval&, const double );
  friend Interval operator*
    ( const double, const Interval& );
  friend Interval operator/
    ( const Interval&, const Interval& );
  friend Interval operator/
    ( const Interval&, const double );
  friend Interval operator/
    ( const double, const Interval& );
  friend std::ostream& operator<<
    ( std::ostream&, const Interval& );
  friend bool operator==
    ( const Interval&, const Interval& );
  friend bool operator!=
    ( const Interval&, const Interval& );
  friend bool operator<=
    ( const Interval&, const Interval& );
  friend bool operator>=
    ( const Interval&, const Interval& );
  friend bool operator<
    ( const Interval&, const Interval& );
  friend bool operator>
    ( const Interval&, const Interval& );

  // friends of class Interval for function overloading
  friend double diam
    ( const Interval& );
  friend double abs
    ( const Interval& );
  friend double mid
    ( const Interval& );
  friend Interval inv
    ( const Interval& );
  friend Interval sqr
    ( const Interval& );
  friend Interval exp
    ( const Interval& );
  friend Interval log
    ( const Interval& );
  friend Interval cos
    ( const Interval& );
  friend Interval sin
    ( const Interval& );
  friend Interval tan
    ( const Interval& );
  friend Interval acos
    ( const Interval& );
  friend Interval asin
    ( const Interval& );
  friend Interval atan
    ( const Interval& );
  friend Interval cosh
    ( const Interval& );
  friend Interval sinh
    ( const Interval& );
  friend Interval tanh
    ( const Interval& );
  friend Interval coth
    ( const Interval& );
  friend Interval acosh
    ( const Interval& );
  friend Interval asinh
    ( const Interval& );
  friend Interval atanh
    ( const Interval& );
  friend Interval acoth
    ( const Interval& );
  friend Interval fabs
    ( const Interval& );
  friend Interval sqrt
    ( const Interval& );
  friend Interval root
    ( const Interval&, const int );
  friend Interval xlog
    ( const Interval& );
  friend Interval fabsx_times_x
    ( const Interval& );
  friend Interval xexpax
    ( const Interval&, const double );
  friend Interval centerline_deficit
    ( const Interval&, const double, const double );
  friend Interval wake_profile
    ( const Interval&, const double );
  friend Interval wake_deficit
    ( const Interval&, const Interval&, const double, const double, const double, const double, const double );
  friend Interval power_curve
    ( const Interval&, const double );
  friend Interval lmtd
    ( const Interval&, const Interval& );
  friend Interval rlmtd
    ( const Interval&, const Interval& );
  friend Interval mid
    (const Interval&, const Interval&, const double);
  friend Interval mid
    (const Interval&, const Interval&, const Interval);
  friend Interval pinch
    (const Interval&, const Interval&, const Interval&); 
  friend Interval euclidean_norm_2d
    ( const Interval&, const Interval& );
  friend Interval expx_times_y
    ( const Interval&, const Interval& );
 friend Interval vapor_pressure
    ( const Interval&, const double, const double, const double, const double, const double,
	  const double, const double, const double, const double, const double, const double );
  friend Interval ideal_gas_enthalpy
    ( const Interval&, const double, const double, const double, const double, const double, const double,
	  const double, const double, const double);
  friend Interval saturation_temperature
    ( const Interval&, const double, const double, const double, const double, const double,
	  const double, const double, const double, const double, const double, const double);
  friend Interval enthalpy_of_vaporization
    ( const Interval&, const double, const double, const double, const double, const double,
	  const double, const double);
  friend Interval cost_function
    ( const Interval&, const double, const double, const double, const double);
  friend Interval nrtl_tau
    ( const Interval&, const double, const double, const double, const double);
  friend Interval nrtl_dtau
    ( const Interval&, const double, const double, const double);
  friend Interval nrtl_G
    ( const Interval&, const double, const double, const double, const double, const double);
  friend Interval nrtl_Gtau
    ( const Interval&, const double, const double, const double, const double, const double);
  friend Interval nrtl_Gdtau
    ( const Interval&, const double, const double, const double, const double, const double);
  friend Interval nrtl_dGtau
    ( const Interval&, const double, const double, const double, const double, const double);
  friend Interval iapws
    ( const Interval&, const double);
  friend Interval iapws
    ( const Interval&, const Interval&, const double);
  friend Interval p_sat_ethanol_schroeder
    ( const Interval& );
  friend Interval rho_vap_sat_ethanol_schroeder
    ( const Interval& );
  friend Interval rho_liq_sat_ethanol_schroeder
    ( const Interval& );
  friend Interval covariance_function
    ( const Interval&, const double);
  friend Interval acquisition_function
    ( const Interval&, const Interval&, const double, const double);
  friend Interval gaussian_probability_density_function
    ( const Interval&);
  friend Interval regnormal
    ( const Interval&, const double, const double);
  friend Interval erf
    ( const Interval& );
  friend Interval erfc
    ( const Interval& );
  friend Interval fstep
    ( const Interval& );
  friend Interval bstep
    ( const Interval& );
  friend Interval arh
    ( const Interval&, const double );
  friend Interval pow
    ( const Interval&, const int );
  friend Interval pow
    ( const Interval&, const double );
  friend Interval pow
    ( const Interval&, const Interval& );
  friend Interval prod
    ( const unsigned int, const Interval* );
  friend Interval monom
    ( const unsigned int, const Interval*, const unsigned* );
  friend Interval cheb
    ( const Interval&, const unsigned );
  friend Interval hull
    ( const Interval&, const Interval& );
  friend Interval min
    ( const Interval&, const Interval& );
  friend Interval max
    ( const Interval&, const Interval& );
  friend Interval min
    ( const unsigned int, const Interval* );
  friend Interval max
    ( const unsigned int, const Interval* );
  friend Interval pos
    ( const Interval& );
  friend Interval neg
    ( const Interval& );
  friend Interval lb_func
    ( const Interval&, const double );
  friend Interval ub_func
    ( const Interval&, const double );
  friend Interval bounding_func
    ( const Interval&, const double, const double );
  friend Interval squash_node
    ( const Interval&, const double, const double );
  friend Interval single_neuron
    ( const std::vector<Interval>&, const std::vector<double>& , const double , const int);
  friend Interval sum_div
    ( const std::vector<Interval>&, const std::vector<double>& );
  friend Interval xlog_sum
    ( const std::vector<Interval>&, const std::vector<double>& );
  friend Interval mc_print
    ( const Interval&, const int );
  friend bool inter
    ( Interval&, const Interval&, const Interval& );

public:

  // other operator overloadings (inline)
  Interval& operator=
    ( const double c )
    {
      _l = c;
      _u = c;
      return *this;
    }
  Interval& operator=
    ( const Interval&I )
    {
      _l = I._l;
      _u = I._u;
      return *this;
    }
  Interval& operator+=
    ( const double c )
    {
      _l += c;
      _u += c;
      return *this;
    }
  Interval& operator+=
    ( const Interval&I )
    {
      _l += I._l;
      _u += I._u;
      return *this;
    }
  Interval& operator-=
    ( const double c )
    {
      _l -= c;
      _u -= c;
      return *this;
    }
  Interval& operator-=
    ( const Interval&I )
    {
      Interval I2( _l, _u );
      _l = I2._l - I._u;
      _u = I2._u - I._l;
      return *this;
    }
  Interval& operator*=
    ( const double c )
    {
      Interval I2( _l, _u );
      *this = I2 * c;
      return *this;

      double t = _l;
      c>=0 ? _l*=c, _u*=c : _l=_u*c, _u=t*c;
      return *this;
    }
  Interval& operator*=
    ( const Interval&I )
    {
      Interval I2( _l, _u );
      *this = I2 * I;
      return *this;
    }
  Interval& operator/=
    ( const double c )
    {
      Interval I2( _l, _u );
      *this = I2 / c;
      return *this;
    }
  Interval& operator/=
    ( const Interval&I )
    {
      Interval I2( _l, _u );
      *this = I2 / I;
      return *this;
    }

  /** @defgroup INTERVAL Non-Validated Interval Arithmetic for Factorable Functions
   *  @{
   */
  //! @brief Options of mc::Interval
  static struct Options
  {
    //! @brief Constructor
    Options():
      DISPLAY_DIGITS(5)
      {}
    //! @brief Number of digits displayed with << operator (default=5)
    unsigned int DISPLAY_DIGITS;
  } options;

  //! @brief Exceptions of mc::Interval
  class Exceptions
  {
  public:
    //! @brief Enumeration type for mc::Interval exceptions
    enum TYPE{
      DIV=1,	//!< Division by zero
	  SUM_DIV,  //!< either coefficients or interval <=0
	  XLOG_SUM, //!< either coefficients or interval <=0
	  COVARIANCE, //!< Covariance function with nonpositive values in range
	  ACQUISITION, //!< Acquisition function with negative values in range
      INV,	//!< Inverse with zero in range
      LMTD,  //!< LMTD with non-positive values in range
      RLMTD,  //!< RLMTD with non-positive values in range
      LOG,	//!< Log with negative values in range
      SQRT,	//!< Square-root with nonpositive values in range
      ACOS,	//!< Inverse cosine with values outside of [-1,1] range
      ASIN,	//!< Inverse sine with values outside of [-1,1] range
      TAN,	//!< Tangent with values \f$\frac{\pi}{2}+k\,\pi\f$, with \f$k\in\mathbb{Z}\f$, in range
      ACOSH,//!< Inverse area cosine hyperbolicus with values outside of [-1,1] range
      ATANH,//!< Inverse arcus tangens hyperbolicus with values inside the [-1,1] range
      CHEB	//!< Chebyshev basis function outside of [-1,1] range
    };
    //! @brief Constructor for error flag <a>ierr</a>
    Exceptions( TYPE ierr ) : _ierr( ierr ){}
    //! @brief Return error flag
    int ierr() const { return _ierr; }
    //! @brief Return error description
    std::string what() const {
      switch( _ierr ){
      case DIV:
        return "mc::Interval\t Division by zero";
      case INV:
        return "mc::Interval\t Inverse with zero in range";
      case LOG:
        return "mc::Interval\t Log with negative values in range";
	  case SUM_DIV:
        return "mc::Interval\t  Sum_div coefficients or Interval with values <=0";
	  case XLOG_SUM:
        return "mc::Interval\t  Xlog_sum coefficients or Interval with values <=0";
      case COVARIANCE:
        return "mc::Interval\t Covariance function with nonpositive values in range";
      case ACQUISITION:
        return "mc::Interval\t Acquisition function with nonpositive values in range";
      case SQRT:
        return "mc::Interval\t Square-root with nonpositive values in range";
      case ACOS:
        return "mc::Interval\t Inverse cosine with values outside of [-1,1] range";
      case ASIN:
        return "mc::Interval\t Inverse sine with values outside of [-1,1] range";
      case TAN:
        return "mc::Interval\t Tangent with values pi/2+k*pi in range";
      case ACOSH:
        return "mc::Interval\t Inverse area cosine hyperbolicus with values outside of [-1,1] range";
      case ATANH:
        return "mc::Interval\t Inverse arcus tangens hyperbolicus with values inside the [-1,1] range";
      case CHEB:
        return "mc::Interval\t Chebyshev basis outside of [-1,1] range";
      case LMTD:
        return "mc::Interval\t LMTD with nonpositive values in range";
      case RLMTD:
        return "mc::Interval\t RLMTD with nonpositive values in range";
      }
      return "mc::Interval\t Undocumented error";
    }

  private:
    TYPE _ierr;
  };
  //! @brief Default constructor (needed for arrays of mc::Interval elements)
  Interval()
    {}
  //! @brief Constructor for a constant value <a>c</a>
  Interval
    ( const double c ):
    _l(c), _u(c)
    {}
  //! @brief Constructor for a variable that belongs to the interval [<a>l</a>,<a>u</a>]
  Interval
    ( const double l, const double u ):
    _l(l<u?l:u), _u(l<u?u:l)
    {}
  //! @brief Copy constructor for the interval <a>I</a>
  Interval
    ( const Interval&I ):
    _l(I._l), _u(I._u)
    {}

  //! @brief Destructor
  ~Interval()
    {}

  //! @brief Return lower bound
  const double& l() const
    {
      return _l;
    }
  //! @brief Return upper bound
  const double& u() const
    {
      return _u;
    }

  //! @brief Set lower bound to <a>lb</a>
  void l ( const double lb )
    {
      _l = lb;
    }
  //! @brief Set upper bound to <a>ub</a>
  void u ( const double ub )
    {
      _u = ub;
    }
  /** @} */

private:

  //! @brief Lower bound
  double _l;
  //! @brief Upper bound
  double _u;
};

////////////////////////////////////////////////////////////////////////

// Interval::Options Interval::options; // commented to make use possible in multiple compilation units

inline Interval
operator+
( const Interval&I )
{
  return I;
}

inline Interval
operator-
( const Interval&I )
{
  Interval I2( -I._u, -I._l );
  return I2;
}

inline Interval
operator+
( const double c, const Interval&I )
{
  Interval I2( c + I._l, c + I._u );
  return I2;
}

inline Interval
operator+
( const Interval&I, const double c )
{
  Interval I2( c + I._l, c + I._u );
  return I2;
}

inline Interval
operator+
( const Interval&I1, const Interval&I2 )
{
  Interval I3( I1._l+I2._l, I1._u+I2._u );
  return I3;
}

inline Interval
operator-
( const double c, const Interval&I )
{
  Interval I2( c - I._u, c - I._l );
  return I2;
}

inline Interval
operator-
( const Interval&I, const double c )
{
  Interval I2( I._l-c, I._u-c );
  return I2;
}

inline Interval
operator-
( const Interval&I1, const Interval&I2 )
{
  Interval I3( I1._l-I2._u, I1._u-I2._l );
  return I3;
}

inline Interval
operator*
( const double c, const Interval&I )
{
  Interval I2( c>=0? c*I._l: c*I._u, c>=0? c*I._u: c*I._l );
  return I2;
}

inline Interval
operator*
( const Interval&I, const double c )
{
  Interval I2( c>=0? c*I._l: c*I._u, c>=0? c*I._u: c*I._l );
  return I2;
}

inline Interval
operator*
( const Interval&I1, const Interval&I2 )
{
  Interval I3( std::min(std::min(I1._l*I2._l,I1._l*I2._u),
                        std::min(I1._u*I2._l,I1._u*I2._u)),
               std::max(std::max(I1._l*I2._l,I1._l*I2._u),
                        std::max(I1._u*I2._l,I1._u*I2._u)) );
  return I3;
}

inline Interval
operator/
( const Interval &I, const double c )
{
  if( isequal(c,0.) ) throw Interval::Exceptions( Interval::Exceptions::DIV );
  return (1./c)*I;
}

inline Interval
operator/
( const double c, const Interval&I )
{
  return c*inv(I);
}

inline Interval
operator/
( const Interval&I1, const Interval&I2 )
{
  return I1*inv(I2);
}

inline double
diam
( const Interval &I )
{
  return I._u-I._l;
}

inline double
mid
( const Interval &I )
{
  return 0.5*(I._u+I._l);
}

inline double
abs
( const Interval &I )
{
  return std::max(std::fabs(I._l),std::fabs(I._u));
}

inline Interval
inv
( const Interval &I )
{
  if ( I._l <= 0. && I._u >= 0. ) throw Interval::Exceptions( Interval::Exceptions::INV );
  Interval I2( 1./I._u, 1./I._l );
  return I2;
}

inline Interval
sqr
( const Interval&I )
{
  int imid = -1;
  return Interval( mc::sqr( mid(I._l,I._u,0.,imid) ),
                   std::max(mc::sqr(I._l),mc::sqr(I._u)) );
}

inline Interval
exp
( const Interval &I )
{
  return Interval( std::exp(I._l), std::exp(I._u) );
}

inline Interval
arh
( const Interval &I, const double a )
{
  return exp(-a/I);
}

inline Interval
log
( const Interval &I )
{
  if ( I._l <= 0. ) throw Interval::Exceptions( Interval::Exceptions::LOG );
  return Interval( std::log(I._l), std::log(I._u) );
}

inline Interval
xlog
( const Interval&I )
{
  if ( I._l < 0. ) throw Interval::Exceptions( Interval::Exceptions::LOG );
  int imid = -1;
  return Interval( mc::xlog(mid(I._l,I._u,std::exp(-1.),imid)),
                   std::max(mc::xlog(I._l), mc::xlog(I._u)) );
}

inline Interval
fabsx_times_x
( const Interval&I )
{
  return Interval( mc::fabsx_times_x(I._l), mc::fabsx_times_x(I._u));
}

//added AVT.SVT 08.01.2019
inline Interval
xexpax
( const Interval&I, const double a )
{
  if(a==0){ return I; } // = x*exp(0*x) = x
  else if(a>0){ return Interval(mc::xexpax(mc::mid(I._l, I._u,-1./a),a),std::max(mc::xexpax(I._l,a), mc::xexpax(I._u,a))); } // the extreme point -1/a is a minimum
  else{ return Interval(std::min(mc::xexpax(I._l,a), mc::xexpax(I._u,a)),mc::xexpax(mc::mid(I._l,I._u,-1./a),a)); } // the extreme point -1/a is a maximum
}

//added AVT.SVT 26.03.2020
inline Interval
centerline_deficit
( const Interval&I, const double xLim, const double type )
{
  switch((int)type) {
    case 1:
    case 2:
      if (I._l>=1.) { // decreasing
        return Interval( mc::centerline_deficit(I._u,xLim,type), mc::centerline_deficit(I._l,xLim,type) );
      } else if (I._u<=1.) {    // increasing
        return Interval( mc::centerline_deficit(I._l,xLim,type), mc::centerline_deficit(I._u,xLim,type) );
      } else  {            // maximum at f(1)=1 and minimum at either end
        return Interval( std::min(mc::centerline_deficit(I._l,xLim,type), mc::centerline_deficit(I._u,xLim,type)), 1.);
      }
    case 3:
    { 
      const double tmp = std::sqrt((9.*std::pow(xLim,3) - 69.*mc::sqr(xLim) + 175.*xLim - 175.)/std::pow(xLim - 1.,7));
      const double xmax = ( tmp*( 5.*xLim - 1. - 10.*mc::sqr(xLim) + 10.*std::pow(xLim,3) - 5.*std::pow(xLim,4) + std::pow(xLim,5) ) - 47*xLim + 4*std::pow(xLim,2) + 3*std::pow(xLim,3) + 70)
                / (15.*(mc::sqr(xLim) - 4.*xLim + 5.));
      if (I._l>=xmax) {      // decreasing
        return Interval( mc::centerline_deficit(I._u,xLim,type), mc::centerline_deficit(I._l,xLim,type) );
      } else if (I._u<=xmax) { // increasing
        return Interval( mc::centerline_deficit(I._l,xLim,type), mc::centerline_deficit(I._u,xLim,type) );
      } else {              // maximum at xmax and minimum at either end
        return Interval( std::min(mc::centerline_deficit(I._l,xLim,type),mc::centerline_deficit(I._u,xLim,type)), mc::centerline_deficit(xmax,xLim,type) );
      }
    }
    default:
        throw std::runtime_error("mc::Interval\t centerline_deficit called with unkonw type.\n");
  }
}

//added AVT.SVT 27.03.2020
inline Interval
wake_profile
( const Interval&I, const double type )
{
  if ( I._l >= 0. ){    // above 0, the function is decreasing
    return Interval( mc::wake_profile(I._u,type), mc::wake_profile(I._l,type) );
  } else if ( I._u <= 0. ) {    // below zero, the function is increasing
    return Interval( mc::wake_profile(I._l,type), mc::wake_profile(I._u,type) );
  } else {    // if zero is in the interval, the maximum is f(0)=1 and the minimum at either end of the interval
    return Interval( std::min(mc::wake_profile(I._l,type), mc::wake_profile(I._u,type)),
                      1.);
  }
}

//added AVT.SVT 08.04.2020
inline Interval
wake_deficit
( const Interval& I1, const Interval& I2, const double a, const double alpha, const double rr, const double type1, const double type2) {

  const double r0 = rr*std::sqrt((1.-a)/(1.-2.*a));
  const Interval Rwake = r0 + alpha*I1;
  return Interval(2.)*Interval(a)*centerline_deficit(Rwake/r0,1.-alpha*rr/r0,type1)*wake_profile(I2/Rwake,type2);

}

//added AVT.SVT 27.03.2020
inline Interval
power_curve
( const Interval&I, const double type )
{
    return Interval( mc::power_curve(I._l,type), mc::power_curve(I._u,type) );
}

//added AVT.SVT 06.06.2017
inline Interval
lmtd
( const Interval&I1, const Interval&I2 )
{
  if ( I1._l <= 0. || I2._l <= 0. ) throw Interval::Exceptions( Interval::Exceptions::LMTD );

  return Interval( mc::lmtd(I1._l,I2._l), mc::lmtd(I1._u,I2._u) );
}

inline Interval
euclidean_norm_2d
( const Interval&I1, const Interval&I2 )
{
  double minPointX = mc::mid(I1._l,I1._u,0.);
  double minPointY = mc::mid(I2._l,I2._u,0.);
  // max is one of the 4 corners
  std::vector<double> corners = { mc::euclidean_norm_2d(I1._l,I2._l), mc::euclidean_norm_2d(I1._l,I2._u),
  								  mc::euclidean_norm_2d(I1._u,I2._l), mc::euclidean_norm_2d(I1._u,I2._u) };
  unsigned cornerIndex = mc::argmax(4,corners.data());
  return Interval(mc::euclidean_norm_2d(minPointX,minPointY),corners[cornerIndex]);
}

//added AVT.SVT 01.03.2018
inline Interval
expx_times_y
( const Interval&I1, const Interval&I2 )
{
  return Interval( mc::expx_times_y(I1._l,I2._l), mc::expx_times_y(I1._u,I2._u) );
}

//added AVT.SVT 06.06.2017
inline Interval
rlmtd
( const Interval&I1, const Interval&I2 )
{
  if ( I1._l <= 0. || I2._l <= 0. ) throw Interval::Exceptions( Interval::Exceptions::RLMTD );

  return Interval( mc::rlmtd(I1._l,I2._l), mc::rlmtd(I1._u,I2._u) );
}

//added AVT.SVT 09/2021 
inline Interval
mid
(const Interval& I1, const Interval& I2, const double k)
{
    return Interval(mc::mid(I1._l, I2._l, k), mc::mid(I1._u, I2._u, k));
}

//added AVT.SVT 09/2021 
inline Interval
pinch
(const Interval& I_Th, const Interval& I_Tc, const Interval& I_Tp)
{
    const double l = std::min(mc::pinch(I_Th._l, I_Tc._u, I_Tp._u), mc::pinch(I_Th._l, I_Tc._u, I_Tp._l));
    const double u = std::max(mc::pinch(I_Th._u, I_Tc._l, I_Tp._u), mc::pinch(I_Th._u, I_Tc._l, I_Tp._l));
    return Interval(l, u);
}

//added AVT.SVT 22.08.2017
inline Interval
vapor_pressure
( const Interval& I, const double type, const double p1, const double p2, const double p3, const double p4 = 0,
  const double p5 = 0, const double p6 = 0, const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0)
{
    return Interval( mc::vapor_pressure(I._l, type, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10), mc::vapor_pressure(I._u, type, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10));
}

//added AVT.SVT 01.09.2017
inline Interval
ideal_gas_enthalpy
( const Interval& I, const double x0, const double type, const double p1, const double p2, const double p3, const double p4,
  const double p5, const double p6 = 0, const double p7 = 0)
{
    return Interval( mc::ideal_gas_enthalpy(I._l, x0, type, p1, p2, p3, p4, p5, p6, p7), mc::ideal_gas_enthalpy(I._u, x0, type, p1, p2, p3, p4, p5, p6, p7));
}

//added AVT.SVT 01.09.2017
inline Interval
saturation_temperature
( const Interval& I, const double type, const double p1, const double p2, const double p3, const double p4 = 0,
  const double p5 = 0, const double p6 = 0, const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0)
{
    return Interval( mc::saturation_temperature(I._l, type, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10), mc::saturation_temperature(I._u, type, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10));
}

//added AVT.SVT 01.09.2017
inline Interval
enthalpy_of_vaporization
( const Interval& I, const double type, const double p1, const double p2, const double p3, const double p4,
  const double p5, const double p6 = 0)
{
    return Interval( mc::enthalpy_of_vaporization(I._u, type, p1, p2, p3, p4, p5, p6), mc::enthalpy_of_vaporization(I._l, type, p1, p2, p3, p4, p5, p6));
}

//added AVT.SVT 06.11.2017
inline Interval
cost_function
( const Interval& I, const double type, const double p1, const double p2, const double p3)
{
	// currently only Guthrie implemented
	double min,max;
    MONOTONICITY monotonicity = get_monotonicity_cost_function(type, p1, p2, p3, I._l, I._u, min, max, true );
    switch(monotonicity){
		case MON_INCR:
			return Interval(mc::cost_function(I._l,type,p1,p2,p3),mc::cost_function(I._u,type,p1,p2,p3));
			break;
		case MON_DECR:
			return Interval(mc::cost_function(I._u,type,p1,p2,p3),mc::cost_function(I._l,type,p1,p2,p3));
			break;
		case MON_NONE:
			return Interval(min,max);
			break;
		default:
			return exp((p1 + log(I)/std::log(10.) * (p2 + p3*log(I)/std::log(10.)))*std::log(10.) );
			break;
	}

}

//added AVT.SVT 23.11.2017
inline Interval
nrtl_tau
( const Interval& I, const double a, const double b, const double e, const double f)
{
	double min,max;
    MONOTONICITY monotonicity = get_monotonicity_nrtl_tau(a,b,e,f, I._l, I._u, min, max, true );
    switch(monotonicity){
		case MON_INCR:
			return Interval(mc::nrtl_tau(I._l,a,b,e,f),mc::nrtl_tau(I._u,a,b,e,f));
			break;
		case MON_DECR:
			return Interval(mc::nrtl_tau(I._u,a,b,e,f),mc::nrtl_tau(I._l,a,b,e,f));
			break;
		case MON_NONE:
			return Interval(min,max);
			break;
		default:
			return a + b/I + e * log(I) + f*I;
			break;
	}
}

//added AVT.SVT 10.01.2019
inline Interval
nrtl_dtau
( const Interval& I, const double b, const double e, const double f)
{
    double min,max;
    MONOTONICITY monotonicity = get_monotonicity_nrtl_dtau(b,e,f, I._l, I._u, min, max, true );
    switch(monotonicity){
		case MON_INCR:
			return Interval(mc::nrtl_dtau(I._l,b,e,f),mc::nrtl_dtau(I._u,b,e,f));
			break;
		case MON_DECR:
			return Interval(mc::nrtl_dtau(I._u,b,e,f),mc::nrtl_dtau(I._l,b,e,f));
			break;
		case MON_NONE:
			return Interval(min,max);
			break;
		default:
			return -b/sqr(I) + e/I + f;
			break;
	}

}

//added AVT.SVT 23.11.2017
inline Interval
nrtl_G
( const Interval& I, const double a, const double b, const double e, const double f, const double alpha)
{
    return exp(-alpha*nrtl_tau(I,a,b,e,f));
}

//added AVT.SVT 01.03.2018
inline Interval
nrtl_Gtau
( const Interval& I, const double a, const double b, const double e, const double f, const double alpha)
{
    return xexpax(nrtl_tau(I,a,b,e,f),-alpha);
}

//added AVT.SVT 22.03.2018
inline Interval
nrtl_Gdtau
( const Interval& I, const double a, const double b, const double e, const double f, const double alpha)
{
    return nrtl_G(I,a,b,e,f,alpha)*nrtl_dtau(I,b,e,f);
}

//added AVT.SVT 22.03.2018
inline Interval
nrtl_dGtau
( const Interval& I, const double a, const double b, const double e, const double f, const double alpha)
{
    return -alpha*nrtl_Gtau(I,a,b,e,f,alpha)*nrtl_dtau(I,b,e,f);
}

inline Interval
p_sat_ethanol_schroeder
( const Interval &I )
{
  return Interval( mc::p_sat_ethanol_schroeder(I._l), mc::p_sat_ethanol_schroeder(I._u));
}

inline Interval
rho_vap_sat_ethanol_schroeder
( const Interval &I )
{
  return Interval( mc::rho_vap_sat_ethanol_schroeder(I._l), mc::rho_vap_sat_ethanol_schroeder(I._u) );
}

inline Interval
rho_liq_sat_ethanol_schroeder
( const Interval &I )
{
  return Interval( mc::rho_liq_sat_ethanol_schroeder(I._u), mc::rho_liq_sat_ethanol_schroeder(I._l) );
}

// all covariance functions are monotonically decreasing
inline Interval
covariance_function
( const Interval &I, const double type)
{
	if(I._l < 0) throw Interval::Exceptions( Interval::Exceptions::COVARIANCE );

	return Interval( mc::covariance_function(I._u, type), mc::covariance_function(I._l, type));
}

inline Interval
acquisition_function
( const Interval &I1, const Interval &I2, const double type, const double fmin)
{
	if(I2._l < 0) throw Interval::Exceptions( Interval::Exceptions::ACQUISITION );

    switch((int)type){
		case 1: // lower confidence bound
		{
		    return Interval( I1._l - fmin*I2._u, I1._u - fmin*I2._l );
		}
		case 2: // expected improvement
		{	// monotonically decreasing in x, monotonically increasing in y
			return Interval( mc::acquisition_function(I1._u, I2._l, type, fmin), mc::acquisition_function(I1._l, I2._u, type, fmin) );
		}
		case 3: // probability of improvement
		{
		  throw std::runtime_error("mc::McCormick\t Probability of improvement acquisition function currently not implemented.\n");
		}
		default:
		  throw std::runtime_error("mc::McCormick\t Acquisition function called with an unknown type.\n");
    }
}

// this function is monotonically increasing
inline Interval
gaussian_probability_density_function
( const Interval &I)
{
	double lowerBound = std::min(mc::gaussian_probability_density_function(I._l),mc::gaussian_probability_density_function(I._u));
	double upperBound;
	if(I._l <= 0 && 0 <= I._u){
		upperBound = mc::gaussian_probability_density_function(0.);
	}
	else{
		upperBound = std::max(mc::gaussian_probability_density_function(I._l),mc::gaussian_probability_density_function(I._u));
	}
	return Interval( lowerBound, upperBound);
}

// this function is monotonically increasing
inline Interval
regnormal
( const Interval &I, const double a, const double b)
{
	return Interval( mc::regnormal(I._l, a, b), mc::regnormal(I._u, a, b));
}

inline Interval
erf
( const Interval &I )
{
  return Interval( std::erf(I._l), std::erf(I._u) );
}

inline Interval
erfc
( const Interval &I )
{
  return Interval( std::erfc(I._u), std::erfc(I._l) );
}

inline Interval
sqrt
( const Interval&I )
{
  if ( I._l < 0. ) throw Interval::Exceptions( Interval::Exceptions::SQRT );
  return Interval( std::sqrt(I._l), std::sqrt(I._u) );
}

inline Interval
root
( const Interval&I, const int n )
{
  if ( I._l < 0. ) throw Interval::Exceptions( Interval::Exceptions::SQRT );

  if(I._l==0.){
   Interval I2( 0., std::exp(std::log(I._u)/n));
   return I2;
  }

  Interval I2( std::exp(std::log(I._l)/n), std::exp(std::log(I._u)/n));
  return I2;
}

inline Interval
fabs
( const Interval&I )
{
  int imid = -1;
  return Interval( std::fabs(mid(I._l,I._u,0.,imid)),
                   std::max(std::fabs(I._l),std::fabs(I._u)) );
}

inline Interval
pow
( const Interval&I, const int n )
{
  if( n == 0 ){
    return 1.;
  }
  if( n == 1 ){
    return I;
  }
  if( n >= 2 && n%2 == 0 ){
    int imid = -1;
    return Interval( std::pow(mid(I._l,I._u,0.,imid),n),
                     std::max(std::pow(I._l,n),std::pow(I._u,n)) );
  }
  if ( n >= 3 ){
    return Interval( std::pow(I._l,n), std::pow(I._u,n) );
  }
  return inv( pow( I, -n ) );
}

inline Interval
prod
(const unsigned int n, const Interval*I)
{
  switch( n ){
   case 0:  return 1.;
   case 1:  return I[0];
   default: return I[0] * prod( n-1, I+1 );
  }
}

inline Interval
monom
(const unsigned int n, const Interval*I, const unsigned*k)
{
  switch( n ){
   case 0:  return 1.;
   case 1:  return pow( I[0], (int)k[0] );
   default: return pow( I[0], (int)k[0] ) * monom( n-1, I+1, k+1 );
  }
}

inline Interval
cheb
( const Interval&I0, const unsigned n )
{
  Interval I(-1.,1.);
  if( !inter( I, I0, I ) ){
  //if ( I._l < -1.-1e1*machprec() || I._u > 1.+1e1*machprec() ){
    throw typename Interval::Exceptions( Interval::Exceptions::CHEB );
  }
  switch( n ){
    case 0:  return 1.;
    case 1:  return I;
    case 2:  return 2.*sqr(I)-1.;
    default:{
      int kL = n - std::ceil(n*std::acos(I._l)/mc::PI);  if( kL <= 0 ) kL = 0;
      int kU = n - std::floor(n*std::acos(I._u)/mc::PI); if( kU >= (int)n ) kU = n;
#ifdef MC__INTERVAL_CHEB_DEBUG
      std::cout << "  kL: " << kL << "  kU: " << kU;
#endif
      if( kU-kL <= 1 ){ // monotonic part
        double TL = std::cos(n*std::acos(I._l));
        double TU = std::cos(n*std::acos(I._u));
        return( TL<=TU? Interval(TL,TU): Interval(TU,TL) );
      }
      else if( kU-kL == 2 ){ // single extremum in range
        double TL = std::cos(n*std::acos(I._l));
        double TU = std::cos(n*std::acos(I._u));
        if( (n-kL)%2 ) return( TL<=TU? Interval(TL, 1.): Interval(TU, 1.) );  // minimum
        else           return( TL<=TU? Interval(-1.,TU): Interval(-1.,TL) );  // maximum
      }
      break;
    }
  }
  //Interval Icheb = 2.*I*cheb(I,n-1)-cheb(I,n-2);
  //return( inter( Icheb, Icheb, Interval(-1.,1.) )? Icheb: Interval(-1.,1.) );
  return Interval(-1.,1.);
}

inline Interval
pow
( const Interval&I, const double a )
{
  if( a == 0. ){
    return 1.;
  }
  if( a == 1. ){
    return I;
  }

  return  Interval( std::pow(I._l,a),std::pow(I._u,a) );
 // return exp( a * log( I ) );
}

inline Interval
pow
( const Interval&I1, const Interval&I2 )
{
  return exp( I2 * log( I1 ) );
}

inline Interval
hull
( const Interval&I1, const Interval&I2 )
{
  return Interval( std::min( I1._l, I2._l ), std::max( I1._u, I2._u ) );
}

inline Interval
min
( const Interval&I1, const Interval&I2 )
{
  return Interval( std::min( I1._l, I2._l ), std::min( I1._u, I2._u ) );
}

inline Interval
max
( const Interval&I1, const Interval&I2 )
{
  return Interval( std::max( I1._l, I2._l ), std::max( I1._u, I2._u ) );
}

inline Interval
min
( const unsigned int n, const Interval*I )
{
  Interval I2( n==0 || !I ? 0.: I[0] );
  for( unsigned int i=1; i<n; i++ ) I2 = min( I2, I[i] );
  return I2;
}

inline Interval
max
( const unsigned int n, const Interval*I )
{
  Interval I2( n==0 || !I ? 0.: I[0] );
  for( unsigned int i=1; i<n; i++ ) I2 = max( I2, I[i] );
  return I2;
}

inline Interval
pos
( const Interval&I )
{
  return Interval(std::max(I._l,mc::machprec()),std::max(I._u,mc::machprec()));
}

inline Interval
neg
( const Interval&I )
{
  return Interval(std::min(I._l,-mc::machprec()),std::min(I._u,-mc::machprec()));
}

inline Interval
lb_func
( const Interval&I, const double lb)
{
  return Interval(std::max(I._l,lb),std::max(I._u,lb));
}

inline Interval
ub_func
( const Interval&I, const double ub)
{
  return Interval(std::min(I._l,ub),std::min(I._u,ub));
}

inline Interval
bounding_func
( const Interval&I, const double lb, const double ub)
{
  return Interval(std::min(std::max(I._l,lb),ub),std::min(std::max(I._u,lb),ub));
}

inline Interval
squash_node
( const Interval&I, const double lb, const double ub)
{
  return Interval(std::max(I._l,lb),std::min(I._u,ub));
}

inline Interval
single_neuron
( const std::vector< Interval > &I, const std::vector<double> &w, const double b , const int type)
{
	double lower=b;
	double upper=b;
	for(unsigned int i=1; i<I.size(); i++){
    if(w[i]>0){
		  lower += w[i]*I[i]._l;
		  upper += w[i]*I[i]._u;
    }
    else{
      lower += w[i]*I[i]._u;
		  upper += w[i]*I[i]._l;
    }
	}
  return Interval( std::tanh(lower), std::tanh(upper) );
}

inline Interval
sum_div
( const std::vector< Interval > &I, const std::vector<double> &coeff)
{
	for (unsigned int i=0; i<I.size(); i++ ){
		if ( I[i]._l <= 0.) throw Interval::Exceptions( Interval::Exceptions::SUM_DIV );
	}
	double lower=0;
	double upper=0;
	for(unsigned int i=1; i<I.size(); i++){
		lower += coeff[i+1]*I[i]._u;
		upper += coeff[i+1]*I[i]._l;
	}
  return Interval((I[0]._l*coeff[0]/(coeff[1]*I[0]._l+lower)), (I[0]._u*coeff[0]/(coeff[1]*I[0]._u+upper)));
}

inline Interval
xlog_sum
( const std::vector< Interval > &I, const std::vector<double> &coeff)
{


	for (unsigned int i=0; i<I.size(); i++ ){
		if ( I[i]._l <= 0.) throw Interval::Exceptions( Interval::Exceptions::XLOG_SUM );
	}
	// Special case
	if(I.size() == 1){
	  double valL = I[0]._l * std::log(coeff[0]*I[0]._l);
	  double valU = I[0]._u * std::log(coeff[0]*I[0]._u);
	  double m = mc::mid(I[0]._l,I[0]._u,std::exp(-1.)/coeff[0]);
	  return Interval( m*std::log(coeff[0]*m), std::max(valL,valU) );
	}
	std::vector<double> corner1 = {I[0]._l}; corner1.reserve(I.size());
	std::vector<double> corner2 = {I[0]._u}; corner2.reserve(I.size());
	std::vector<double> rusr = {coeff[0]}; rusr.reserve(I.size()+coeff.size());// used for root finding
	std::vector<double> minPoint(I.size());
	for(size_t i = 1; i<I.size();i++){
		corner1.push_back(I[i]._u);
		corner2.push_back(I[i]._u);
		rusr.push_back(coeff[i]);
		rusr.push_back(I[i]._l);
		minPoint[i] = I[i]._l;
	}
	double upper = std::max(mc::xlog_sum(corner1,coeff), mc::xlog_sum(corner2,coeff));

	rusr.push_back(0.); // root
	int size = coeff.size();
	double zmin = _compute_root(I[0]._l, I[0]._l, I[0]._u, xlog_sum_dfunc, xlog_sum_ddfunc, rusr.data(), &size);
	minPoint[0] = mc::mid(I[0]._l, I[0]._u, zmin);
	double lower = mc::xlog_sum(minPoint, coeff);

    return Interval(lower, upper);
}

inline Interval
mc_print
( const Interval&I, const int number )
{
  return Interval(I._l,I._u);
}

inline Interval
cos
( const Interval&I )
{
  const int k = std::ceil(-(1.+I._l/PI)/2.); // -pi <= xL+2*k*pi < pi
  const double l = I._l+2.*PI*k, u = I._u+2.*PI*k;
  if( l <= 0 ){
    if( u <= 0 )   return Interval( std::cos(l), std::cos(u) );
    if( u >= PI )  return Interval( -1., 1. );
    return Interval( std::min(std::cos(l), std::cos(u)), 1. );
  }
  if( u <= PI )    return Interval( std::cos(u), std::cos(l) );
  if( u >= 2.*PI ) return Interval( -1., 1. );
  return Interval( -1., std::max(std::cos(l), std::cos(u)));
}

inline Interval
sin
( const Interval &I )
{
  return cos( I - PI/2. );
}

inline Interval
tan
( const Interval&I )
{
  const int k = std::ceil(-0.5-I._l/PI); // -pi/2 <= xL+k*pi < pi/2
  const double l = I._l+PI*k, u = I._u+PI*k;
  if( u >= 0.5*PI ) throw Interval::Exceptions( Interval::Exceptions::TAN );
  return Interval( std::tan(l), std::tan(u) );
}

inline Interval
acos
( const Interval &I )
{
  if ( I._l < -1. || I._u > 1. ) throw Interval::Exceptions( Interval::Exceptions::ACOS );
  return Interval( std::acos(I._u), std::acos(I._l) );
}

inline Interval
asin
( const Interval &I )
{
  if ( I._l < -1. || I._u > 1. ) throw Interval::Exceptions( Interval::Exceptions::ASIN );
  return Interval( std::asin(I._l), std::asin(I._u) );
}

inline Interval
atan
( const Interval &I )
{
  return Interval( std::atan(I._l), std::atan(I._u) );
}

inline Interval
cosh
( const Interval &I )
{
  int imid = -1;
  return Interval( std::cosh( mid(I._l,I._u,0.,imid) ),
                   std::max(std::cosh(I._l),std::cosh(I._u)) );
}

inline Interval
sinh
( const Interval &I )
{
  return Interval( std::sinh(I._l), std::sinh(I._u) );
}

inline Interval
tanh
( const Interval &I )
{
  return Interval( std::tanh(I._l), std::tanh(I._u) );
}

inline Interval
acosh
( const Interval &I )
{
  if(I._l<1) throw Interval::Exceptions( Interval::Exceptions::ACOSH );

  return Interval(std::acosh(I._l), std::acosh(I._u));
}

inline Interval
asinh
( const Interval &I )
{
  return Interval( std::asinh(I._l), std::asinh(I._u) );
}

inline Interval
atanh
( const Interval &I )
{
  if ( I._l < -1. || I._u > 1. ) throw Interval::Exceptions( Interval::Exceptions::ATANH );
  return Interval( std::tanh(I._l), std::tanh(I._u) );
}

inline Interval
coth
( const Interval &I )
{
  return Interval( 1./std::tanh(I._l), 1./std::tanh(I._u) );
}

inline Interval
acoth
( const Interval &I )
{
  if ( (I._l > -1. && I._l < 1.) || (I._u > -1. && I._u < 1.)) throw Interval::Exceptions( Interval::Exceptions::ATANH );
  return Interval( mc::acoth(I._u), mc::acoth(I._l) );
}

inline Interval
fstep
( const Interval &I )
{
  if( I._l >= 0 )     return Interval(1.);
  else if( I._u < 0 ) return Interval(0.);
  return Interval(0.,1.);
}

inline Interval
bstep
( const Interval &I )
{
  return fstep( -I );
}

inline std::ostream&
operator<<
( std::ostream&out, const Interval&I)
{
  out << std::right << std::scientific << std::setprecision(Interval::options.DISPLAY_DIGITS);
  out << "[ "  << std::setw(Interval::options.DISPLAY_DIGITS+7) << I.l()
      << " : " << std::setw(Interval::options.DISPLAY_DIGITS+7) << I.u() << " ]";
  return out;
}

inline bool
inter
( Interval &XIY, const Interval &X, const Interval &Y )
{
  if( X._l > Y._u || Y._l > X._u ) return false;
  XIY._l = std::max( X._l, Y._l );
  XIY._u = std::min( X._u, Y._u );
  return true;
}

inline bool
operator==
( const Interval&I1, const Interval&I2 )
{
  return( I1._l == I2._l && I1._u == I2._u );
}

inline bool
operator!=
( const Interval&I1, const Interval&I2 )
{
  return( I1._l != I2._l || I1._u != I2._u );
}

inline bool
operator<=
( const Interval&I1, const Interval&I2 )
{
  return( I1._l >= I2._l && I1._u <= I2._u );
}

inline bool
operator>=
( const Interval&I1, const Interval&I2 )
{
  return( I1._l <= I2._l && I1._u >= I2._u );
}

inline bool
operator<
( const Interval&I1, const Interval&I2 )
{
  return( I1._l > I2._l && I1._u < I2._u );
}

inline bool
operator>
( const Interval&I1, const Interval&I2 )
{
  return( I1._l < I2._l && I1._u > I2._u );
}

} // namespace mc

#include "mcfadbad.hpp"
//#include "fadbad.h"

namespace fadbad
{

//! @brief Specialization of the structure fadbad::Op for use of the type mc::Interval of MC++ as a template parameter of the classes fadbad::F, fadbad::B and fadbad::T of FADBAD++
template <> struct Op<mc::Interval>
{
  typedef double Base;
  typedef mc::Interval T;
  static Base myInteger( const int i ) { return Base(i); }
  static Base myZero() { return myInteger(0); }
  static Base myOne() { return myInteger(1);}
  static Base myTwo() { return myInteger(2); }
  static double myPI() { return mc::PI; }
  static T myPos( const T& x ) { return  x; }
  static T myNeg( const T& x ) { return -x; }
  template <typename U> static T& myCadd( T& x, const U& y ) { return x+=y; }
  template <typename U> static T& myCsub( T& x, const U& y ) { return x-=y; }
  template <typename U> static T& myCmul( T& x, const U& y ) { return x*=y; }
  template <typename U> static T& myCdiv( T& x, const U& y ) { return x/=y; }
  static T myInv( const T& x ) { return mc::inv( x ); }
  static T mySqr( const T& x ) { return mc::pow( x, 2 ); }
  template <typename X, typename Y> static T myPow( const X& x, const Y& y ) { return mc::pow( x, y ); }
  //static T myCheb( const T& x, const unsigned n ) { return mc::cheb( x, n ); }
  static T mySqrt( const T& x ) { return mc::sqrt( x ); }
  static T myLog( const T& x ) { return mc::log( x ); }
  static T myExp( const T& x ) { return mc::exp( x ); }
  static T mySin( const T& x ) { return mc::sin( x ); }
  static T myCos( const T& x ) { return mc::cos( x ); }
  static T myTan( const T& x ) { return mc::tan( x ); }
  static T myAsin( const T& x ) { return mc::asin( x ); }
  static T myAcos( const T& x ) { return mc::acos( x ); }
  static T myAtan( const T& x ) { return mc::atan( x ); }
  static T mySinh( const T& x ) { return mc::sinh( x ); }
  static T myCosh( const T& x ) { return mc::cosh( x ); }
  static T myTanh( const T& x ) { return mc::tanh( x ); }
  static bool myEq( const T& x, const T& y ) { return x==y; }
  static bool myNe( const T& x, const T& y ) { return x!=y; }
  static bool myLt( const T& x, const T& y ) { return x<y; }
  static bool myLe( const T& x, const T& y ) { return x<=y; }
  static bool myGt( const T& x, const T& y ) { return x>y; }
  static bool myGe( const T& x, const T& y ) { return x>=y; }
};

} // end namespace fadbad

//#include "mcop.hpp"

namespace mc
{

//! @brief Specialization of the structure mc::Op to allow usage of the type mc::Interval for DAG evaluation or as a template parameter in other MC++ classes
template <> struct Op<mc::Interval>
{
  typedef mc::Interval T;
  static T point( const double c ) { return T(c); }
  static T zeroone() { return T(0.,1.); }
  static void I(T& x, const T&y) { x = y; }
  static double l(const T& x) { return x.l(); }
  static double u(const T& x) { return x.u(); }
  static double abs (const T& x) { return mc::abs(x);  }
  static double mid (const T& x) { return mc::mid(x);  }
  static double diam(const T& x) { return mc::diam(x); }
  static T inv (const T& x) { return mc::inv(x);  }
  static T sqr (const T& x) { return mc::sqr(x);  }
  static T sqrt(const T& x) { return mc::sqrt(x); }
  static T exp (const T& x) { return mc::exp(x);  }
  static T root(const T& x, const int n) { return mc::root(x,n); }
  static T log (const T& x) { return mc::log(x);  }
  static T xlog(const T& x) { return mc::xlog(x); }
  static T fabsx_times_x(const T& x) { return mc::fabsx_times_x(x); }
  static T xexpax(const T& x, const double a) { return mc::xexpax(x,a); }
  static T centerline_deficit(const T& x, const double xLim, const double type) { return mc::centerline_deficit(x,xLim,type); }
  static T wake_profile(const T& x, const double type) { return mc::wake_profile(x,type); }
  static T wake_deficit(const T& x, const T& r, const double a, const double alpha, const double rr, const double type1, const double type2) { return mc::wake_deficit(x,r,a,alpha,rr,type1,type2); }
  static T power_curve(const T& x, const double type) { return mc::power_curve(x,type); }
  static T lmtd(const T& x, const T& y) { return mc::lmtd(x,y); }
  static T rlmtd(const T& x, const T& y) { return mc::rlmtd(x,y); }
  static T mid(const T& x, const T& y, const double k) { return mc::mid(x, y, k); } 
  static T pinch(const T& Th, const T& Tc, const T& Tp) { return mc::pinch(Th, Tc, Tp); } 
  static T euclidean_norm_2d(const T& x, const T& y) { return mc::euclidean_norm_2d(x,y); }
  static T expx_times_y(const T& x, const T& y) { return mc::expx_times_y(x,y); }
  static T vapor_pressure(const T& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
							const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return mc::vapor_pressure(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10);}
  static T ideal_gas_enthalpy(const T& x, const double x0, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0,
							  const double p7 = 0) { return mc::ideal_gas_enthalpy(x, x0,type,p1,p2,p3,p4,p5,p6,p7);}
  static T saturation_temperature(const T& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
									const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return mc::saturation_temperature(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10);}
  static T enthalpy_of_vaporization(const T& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0) { return mc::enthalpy_of_vaporization(x, type, p1,p2,p3,p4,p5,p6);}
  static T cost_function(const T& x, const double type, const double p1, const double p2, const double p3) { return mc::cost_function(x, type, p1, p2, p3);}
  static T nrtl_tau(const T& x, const double a, const double b, const double e, const double f) { return mc::nrtl_tau(x, a, b, e, f);}
  static T nrtl_dtau(const T& x, const double b, const double e, const double f) { return mc::nrtl_dtau(x, b, e, f);}
  static T nrtl_G(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return mc::nrtl_G(x, a, b, e, f, alpha);}
  static T nrtl_Gtau(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return mc::nrtl_Gtau(x, a, b, e, f, alpha);}
  static T nrtl_Gdtau(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return mc::nrtl_Gdtau(x, a, b, e, f, alpha);}
  static T nrtl_dGtau(const T& x, const double a, const double b, const double e, const double f, const double alpha) { return mc::nrtl_dGtau(x, a, b, e, f, alpha);}
  static T iapws(const T& x, const double type) { throw std::runtime_error("Error: IAPWS-IF97 envelopes are not implemented for mc::Interval."); }
  static T iapws(const T& x, const T& y, const double type) { throw std::runtime_error("Error: IAPWS-IF97 envelopes are not implemented for mc::Interval."); }
  static T p_sat_ethanol_schroeder(const T& x) { return mc::p_sat_ethanol_schroeder(x); }
  static T rho_vap_sat_ethanol_schroeder(const T& x) { return mc::rho_vap_sat_ethanol_schroeder(x); }
  static T rho_liq_sat_ethanol_schroeder(const T& x) { return mc::rho_liq_sat_ethanol_schroeder(x); }
  static T covariance_function(const T& x, const double type) { return mc::covariance_function(x,type); }
  static T acquisition_function(const T& x, const T& y, const double type, const double fmin) { return mc::acquisition_function(x,y,type,fmin); }
  static T gaussian_probability_density_function(const T& x) { return mc::gaussian_probability_density_function(x); }
  static T regnormal(const T& x, const double a, const double b) { return mc::regnormal(x,a,b); }
  static T fabs(const T& x) { return mc::fabs(x); }
  static T sin (const T& x) { return mc::sin(x);  }
  static T cos (const T& x) { return mc::cos(x);  }
  static T tan (const T& x) { return mc::tan(x);  }
  static T asin(const T& x) { return mc::asin(x); }
  static T acos(const T& x) { return mc::acos(x); }
  static T atan(const T& x) { return mc::atan(x); }
  static T sinh(const T& x) { return mc::sinh(x); }
  static T cosh(const T& x) { return mc::cosh(x); }
  static T tanh(const T& x) { return mc::tanh(x); }
  static T coth(const T& x) { return mc::coth(x); }
  static T asinh(const T& x) { return mc::asinh(x); }
  static T acosh(const T& x) { return mc::acosh(x); }
  static T atanh(const T& x) { return mc::atanh(x); }
  static T acoth(const T& x) { return mc::acoth(x); }
  static T erf (const T& x) { return mc::erf(x);  }
  static T erfc(const T& x) { return mc::erfc(x); }
  static T fstep(const T& x) { return mc::fstep(x); }
  static T bstep(const T& x) { return mc::bstep(x); }
  static T min (const T& x, const T& y) { return mc::min(x,y);  }
  static T max (const T& x, const T& y) { return mc::max(x,y);  }
  static T pos (const T& x) { return mc::pos(x);  }
  static T neg (const T& x) { return mc::neg(x);  }
  static T lb_func (const T& x, const double lb) { return mc::lb_func(x,lb);  }
  static T ub_func (const T& x, const double ub) { return mc::ub_func(x,ub);  }
  static T bounding_func (const T& x, const double lb, const double ub) { return mc::bounding_func(x,lb,ub);  }
  static T squash_node (const T& x, const double lb, const double ub) { return mc::squash_node(x,lb,ub);  }
  static T single_neuron(const std::vector<T> &x, const std::vector<double> &w, const double b, const int type) { return mc::single_neuron(x,w,b,type); }
  static T sum_div(const std::vector<T> &x, const std::vector<double> &coeff){ return mc::sum_div(x,coeff); }
  static T xlog_sum(const std::vector<T> &x, const std::vector<double> &coeff){ return mc::xlog_sum(x,coeff); }
  static T mc_print (const T& x, const int number) { return mc::mc_print(x,number);  }
  static T arh (const T& x, const double k) { return mc::arh(x,k); }
  template <typename X, typename Y> static T pow(const X& x, const Y& y) { return mc::pow(x,y); }
  static T cheb (const T& x, const unsigned n) { return mc::cheb(x,n); }
  static T prod (const unsigned int n, const T* x) { return mc::prod(n,x); }
  static T monom (const unsigned int n, const T* x, const unsigned* k) { return mc::monom(n,x,k); }
  static T hull(const T& x, const T& y) { return mc::hull(x,y); }
  static bool inter(T& xIy, const T& x, const T& y) { return mc::inter(xIy,x,y); }
  static bool eq(const T& x, const T& y) { return x==y; }
  static bool ne(const T& x, const T& y) { return x!=y; }
  static bool lt(const T& x, const T& y) { return x<y;  }
  static bool le(const T& x, const T& y) { return x<=y; }
  static bool gt(const T& x, const T& y) { return x>y;  }
  static bool ge(const T& x, const T& y) { return x>=y; }
};

} // namespace mc

#endif
