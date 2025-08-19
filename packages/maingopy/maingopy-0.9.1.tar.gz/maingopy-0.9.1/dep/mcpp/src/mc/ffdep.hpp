// Copyright (C) 2017 Benoit Chachuat, Imperial College London.
// All Rights Reserved.
// This code is published under the Eclipse Public License.

/*!
\page page_FFDEP Structure and Dependency Detection for Factorable Functions
\author Benoit C. Chachuat
\version 1.0
\date 2017
\bug No known bugs.

mc::FFDep is a C++ class that determines the structure of mathematical expressions, namely their sparsity pattern and linearity, for a given set of participating variables. It relies on the operator overloading and function overloading mechanisms of C++. The overloaded operators are: `+', `-', `*', and `/'; the overloaded functions include: `exp', `log', `sqr', `pow', `cheb', `sqrt', `fabs', `xlog', `min', `max', `cos', `sin', `tan', `acos', `asin', `atan', `cosh', `sinh', `tanh', `coth'.


\section sec_FFDepEval How Do I Determine the Structure of a Factorable Function?

Suppose you are given 4 variables \f$x_1,\ldots,x_4\f$ and want to determine the sparsity pattern and linearity of the vector following function
\f{eqnarray*}
  {\bf f}({\bf x}) = \left(\begin{array}{c} f_1({\bf x})\\ f_2({\bf x})\end{array}\right) = \left(\begin{array}{c} \displaystyle x_3 x_4+\frac{x_1}{x_3}\\x_1(\exp(x_3-x_4))^2+x_2 \end{array}\right)
\f}

First, define the variables \f$x_1,\ldots,x_4\f$ as

\code
      const int NX = 4;
      mc::FFDep X[NX];
      for( int i=0; i<NX; i++ ) X[i].indep(i);
\endcode

Essentially, the first line means that <tt>X</tt> is an array of mc::FFDep class objects, and the second line defines X[0],...X[NX-1] as independent variables with indices 0,...,NX-1, respectively.

Once the independent variables \f${\bf x}\f$ have been defined, determine the structure of \f${\bf f}({\bf x})\f$ simply as

\code
      const int NF = 2;
      mc::FFDep F[NF] = { X[2]*X[3]+X[0]/X[2],
                          X[0]*pow(exp(X[2]-X[3]),2)+X[1] };
\endcode

Retrieve the structure - both the sparsity pattern and the dependence type - of \f$f_1\f$ and \f$f_2\f$ as

\code
      std::map<int,int> F0_dep = F[0].dep();
      std::map<int,int> F1_dep = F[1].dep();
\endcode

You can also display the structure as

\code
      std::cout << "Variable dependence of F[0]: " << F[0] << std::endl;
      std::cout << "Variable dependence of F[1]: " << F[1] << std::endl;
\endcode

The corresponding output is

\verbatim
      Variable dependence of F[0]: { 0P 2R 3P }
      Variable dependence of F[1]: { 0P 1L 2N 3N }
\endverbatim

which indicates that X[0], X[2] and X[3] participate in F[0], but not X[1], where X[0] and X[3] have polynomial 'P' dependence, whereas X[2] has rational 'R' dependence. Likewise, all four variables X[0], X[1], X[2] and X[3] participate in F[1], where X[0] has polynomial dependence, X[1] has linear 'L' dependence, and both X[2] and X[3] have nonlinear 'N' dependence.

\section sec_FFDepErr Errors Encountered in Determining the Structure of a Factorable Function?

Errors are managed based on the exception handling mechanism of the C++ language. Each time an error is encountered, a class object of type FFDep::Exceptions is thrown, which contains the type of error. It is the user's responsibility to test whether an exception was thrown during a calculation, and then make the appropriate changes. Should an exception be thrown and not caught by the calling program, the execution will stop.

Possible errors encountered in determining the structure of a factorable function are:

<TABLE border="1">
<CAPTION><EM>Errors during Structure Determination</EM></CAPTION>
     <TR><TH><b>Number</b> <TD><b>Description</b>
     <TR><TH><tt>-1</tt> <TD>Internal error
     <TR><TH><tt>-33</tt> <TD>Call to unavailable feature
</TABLE>
*/

#ifndef MC__FFDEP_HPP
#define MC__FFDEP_HPP

#include <iostream>
#include <map>

namespace mc
{

//! @brief C++ class for evaluation of the sparsity pattern of a factorable function
////////////////////////////////////////////////////////////////////////
//! mc::FFDep is a C++ class for evaluating the sparsity pattern of a
//! factorable function
////////////////////////////////////////////////////////////////////////
class FFDep
////////////////////////////////////////////////////////////////////////
{
  // friends of class FFDep for operator and function overloading
  friend FFDep operator+  ( const FFDep& );
  friend FFDep operator+  ( const FFDep&, const FFDep& );
  friend FFDep operator+  ( const double, const FFDep& );
  friend FFDep operator+  ( const FFDep&, const double );
  friend FFDep operator-  ( const FFDep& );
  friend FFDep operator-  ( const FFDep&, const FFDep& );
  friend FFDep operator-  ( const double, const FFDep& );
  friend FFDep operator-  ( const FFDep&, const double );
  friend FFDep operator*  ( const FFDep&, const FFDep& );
  friend FFDep operator*  ( const FFDep&, const double );
  friend FFDep operator*  ( const double, const FFDep& );
  friend FFDep operator/  ( const FFDep&, const FFDep& );
  friend FFDep operator/  ( const FFDep&, const double );
  friend FFDep operator/  ( const double, const FFDep& );
  friend std::ostream& operator<< ( std::ostream&, const FFDep& );
  friend bool operator==  ( const FFDep&, const FFDep& );
  friend bool operator!=  ( const FFDep&, const FFDep& );
  friend bool operator<=  ( const FFDep&, const FFDep& );
  friend bool operator>=  ( const FFDep&, const FFDep& );
  friend bool operator<   ( const FFDep&, const FFDep& );
  friend bool operator>   ( const FFDep&, const FFDep& );
  friend FFDep inv   ( const FFDep& );
  friend FFDep sqr   ( const FFDep& );
  friend FFDep exp   ( const FFDep& );
  friend FFDep log   ( const FFDep& );
  friend FFDep xlog  ( const FFDep& );
  friend FFDep fabsx_times_x  ( const FFDep& );
  friend FFDep xexpax  ( const FFDep&, const double );
  friend FFDep centerline_deficit  ( const FFDep&, const double, const double );
  friend FFDep wake_profile  ( const FFDep&, const double );
  friend FFDep wake_deficit  ( const FFDep&, const FFDep&, const double, const double, const double, const double, const double );
  friend FFDep power_curve  ( const FFDep&, const double );
  friend FFDep lmtd  ( const FFDep&, const FFDep& );
  friend FFDep rlmtd ( const FFDep&, const FFDep& );
  friend FFDep mid(const FFDep&, const FFDep&, const double); 
  friend FFDep pinch(const FFDep&, const FFDep&, const FFDep&); 
  friend FFDep pinch(const FFDep&, const FFDep&); 
  friend FFDep pinch(const FFDep&);
  friend FFDep euclidean_norm_2d  ( const FFDep&, const FFDep& );
  friend FFDep expx_times_y  ( const FFDep&, const FFDep& );
  friend FFDep vapor_pressure ( const FFDep&, const double, const double, const double, const double, const double,
								const double, const double, const double, const double, const double, const double );
  friend FFDep ideal_gas_enthalpy ( const FFDep&, const double, const double, const double, const double, const double, const double,
									const double, const double, const double );
  friend FFDep saturation_temperature  ( const FFDep&, const double, const double, const double, const double, const double,
										 const double, const double, const double, const double, const double, const double );
  friend FFDep enthalpy_of_vaporization ( const FFDep&, const double, const double, const double, const double, const double,
										  const double, const double );
  friend FFDep cost_function ( const FFDep&, const double, const double, const double, const double );
  friend FFDep sum_div ( const std::vector<FFDep>&, const std::vector<double>& );
  friend FFDep xlog_sum ( const std::vector<FFDep>&, const std::vector<double>& );
  friend FFDep nrtl_tau ( const FFDep&, const double, const double, const double, const double );
  friend FFDep nrtl_dtau ( const FFDep&, const double, const double, const double );
  friend FFDep nrtl_G ( const FFDep&, const double, const double, const double, const double, const double );
  friend FFDep nrtl_Gtau ( const FFDep&, const double, const double, const double, const double, const double );
  friend FFDep nrtl_Gdtau ( const FFDep&, const double, const double, const double, const double, const double );
  friend FFDep nrtl_dGtau ( const FFDep&, const double, const double, const double, const double, const double );
  friend FFDep iapws ( const FFDep&, const double);
  friend FFDep iapws ( const FFDep&, const FFDep&, const double);
  friend FFDep p_sat_ethanol_schroeder ( const FFDep& );
  friend FFDep rho_vap_sat_ethanol_schroeder ( const FFDep& );
  friend FFDep rho_liq_sat_ethanol_schroeder ( const FFDep& );
  friend FFDep covariance_function (const FFDep&, const double);
  friend FFDep acquisition_function (const FFDep&, const FFDep&, const double, const double);
  friend FFDep gaussian_probability_density_function(const FFDep&);
  friend FFDep regnormal (const FFDep&, const double, const double);
  friend FFDep cos   ( const FFDep& );
  friend FFDep sin   ( const FFDep& );
  friend FFDep tan   ( const FFDep& );
  friend FFDep acos  ( const FFDep& );
  friend FFDep asin  ( const FFDep& );
  friend FFDep atan  ( const FFDep& );
  friend FFDep cosh  ( const FFDep& );
  friend FFDep sinh  ( const FFDep& );
  friend FFDep tanh  ( const FFDep& );
  friend FFDep coth  ( const FFDep& );
  friend FFDep fabs  ( const FFDep& );
  friend FFDep sqrt  ( const FFDep& );
  friend FFDep erf   ( const FFDep& );
  friend FFDep erfc  ( const FFDep& );
  friend FFDep fstep ( const FFDep& );
  friend FFDep bstep ( const FFDep& );
  friend FFDep cheb  ( const FFDep&, const unsigned );
  friend FFDep pow   ( const FFDep&, const int );
  friend FFDep pow   ( const FFDep&, const double );
  friend FFDep pow   ( const FFDep&, const FFDep& );
  friend FFDep min   ( const FFDep&, const FFDep& );
  friend FFDep max   ( const FFDep&, const FFDep& );
  friend FFDep pos   ( const FFDep& );
  friend FFDep neg   ( const FFDep& );
  friend FFDep lb_func  ( const FFDep&, const double );
  friend FFDep ub_func  ( const FFDep&, const double );
  friend FFDep bounding_func  ( const FFDep&, const double, const double );
  friend FFDep squash_node  ( const FFDep&, const double, const double );
  friend FFDep single_neuron  ( const std::vector<FFDep>&, const std::vector<double>&, const double, const int );
  friend FFDep mc_print ( const FFDep&, const int  );
  friend FFDep inter ( const FFDep&, const FFDep& );
  friend FFDep min   ( const unsigned int, const FFDep* );
  friend FFDep max   ( const unsigned int, const FFDep* );
  friend FFDep sum   ( const unsigned int, const FFDep* );
  friend FFDep prod  ( const unsigned int, const FFDep* );
  friend FFDep monom ( const unsigned int, const FFDep*, const unsigned* );

public:

  //! @brief Exceptions of mc::FFDep
  class Exceptions
  {
  public:
    //! @brief Enumeration type for FFDep exception handling
    enum TYPE{
      INTERN=-1, //!< Internal error
      UNDEF=-33	  //!< Error due to calling an unavailable feature
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
      case UNDEF:
        return "mc::FFDep\t Unavailable feature";
      case INTERN:
        return "mc::FFDep\t Internal error";
      default:
        return "mc::FFDep\t Undocumented error";
      }
    }
  };

  /** @defgroup FFDep Structure and Dependency Detection for Factorable Functions
   *  @{
   */
  //! @brief Dependence type
  enum TYPE{
    L=0, //!< Linear
	B,   //!< Bilinear
	Q,   //!< Quadratic
    P,   //!< Polynomial
    R,   //!< Rational
    N,   //!< General nonlinear
	D	 //!< General nonlinear non-smooth, e.g., using abs, min, max, fstep, bstep
  };

  //! @brief Typedef for dependency map
  typedef std::map<int,int> t_FFDep; // variable i (first int) has type j (second int)

  //! @brief Default constructor (needed to declare arrays of FFDep class)
  FFDep
    ( const double c=0. ) :
	nontrivialOperationDepth(0)
    {}
  //! @brief Copy constructor
  FFDep
    ( const FFDep&S ):
    _dep(S._dep), nontrivialOperationDepth(S.nontrivialOperationDepth)
    {}
  //! @brief Destructor
  ~FFDep()
    {}

  //! @brief Set independent variable with index <a>ind</a>
  FFDep& indep
    ( const int ind )
    { _dep.clear();
      _dep.insert( std::make_pair(ind,FFDep::L) ); // changed from TYPE::L to FFDep::L to avoid Warnings and be compatible with standards
	  nontrivialOperationDepth = 0; // independent variables have depth 0
      return *this; }

  //! @brief Determine if current object is dependent on the variable of index <a>ind</a>
  std::pair<bool,int> dep
    ( const int ind )
    { auto it = _dep.find(ind);
      return( it==_dep.end()? std::make_pair(false,FFDep::L):
                              std::make_pair(true,static_cast<TYPE>(it->second)) ); } // have to cast to TYPE since VS2010 can't cast int to enum


  //! @brief Combines with the dependency sets of another variable
  FFDep& combine
    ( const FFDep&S, const TYPE&dep );
  //! @brief Combines the dependency sets of two variables
  static FFDep combine
    ( const FFDep&S1, const FFDep&S2, const TYPE&dep );

  //! @brief Update type of dependent variables
  FFDep& update
    ( const TYPE&dep );
  //! @brief Copy dependent variables and update type
  static FFDep copy
    ( const FFDep&S, const TYPE&dep );

  //AVT.SVT 22.05.2018
  //! @brief Combines the dependency sets of two variables for the multiplication operator
  static FFDep combineMult
    ( const FFDep&S1, const FFDep&S2, const TYPE&dep );

  //! @brief Copy dependent variables and update type in the cases of quadratic functions
  static FFDep copyQuad
    ( const FFDep&S, const TYPE&dep );

  //! @brief Return dependency map
  const t_FFDep& dep() const
    { return _dep; }
  t_FFDep& dep()
    { return _dep; }
  /** @} */

  unsigned nontrivialOperationDepth;

private:
  //! @brief Dependency set
  t_FFDep _dep;

public:
  // other operator overloadings (inlined)
  FFDep& operator=
    ( const double c )
    { _dep.clear(); nontrivialOperationDepth=0; return *this; }
  FFDep& operator=
    ( const FFDep&S )
    { if( this != &S ) _dep = S._dep; nontrivialOperationDepth = S.nontrivialOperationDepth; return *this; }
  FFDep& operator+=
    ( const double c )
    { return *this; }
  FFDep& operator+=
    ( const FFDep&S )
    { return combine( S, FFDep::L ); }
  FFDep& operator-=
    ( const double c )
    { return *this; }
  FFDep& operator-=
    ( const FFDep&S )
    { return combine( S, FFDep::L ); }
  FFDep& operator*=
    ( const double c )
    { return *this; }
  FFDep& operator*=
    ( const FFDep&S )
    { return combine( S, FFDep::P ); }
  FFDep& operator/=
    ( const double c )
    { return *this; }
  FFDep& operator/=
    ( const FFDep&S )
    { return combine( S, FFDep::R ); }

};

////////////////////////////////////////////////////////////////////////

inline FFDep&
FFDep::update
( const TYPE&dep )
{
  auto it = _dep.begin();
  for( ; it != _dep.end(); ++it )
    if( it->second < dep ) it->second = dep;

  if(dep>FFDep::L){
      nontrivialOperationDepth++; // increase depth by 1
  }
  return *this;
}

inline FFDep
FFDep::copy
( const FFDep&S, const TYPE&dep )
{
  FFDep S2( S );
  if(dep > FFDep::L ){
      S2.nontrivialOperationDepth = S.nontrivialOperationDepth+1; // increase depth by 1
  }
  return S2.update( dep );
}

inline FFDep&
FFDep::combine
( const FFDep&S, const TYPE&dep )
{
  auto cit = S._dep.begin();
  FFDep::TYPE t = FFDep::L;
  for( ; cit != S._dep.end(); ++cit ){
    auto ins = _dep.insert( *cit );
    if( !ins.second && ins.first->second < cit->second ){
		ins.first->second = cit->second;
	}
    //if( !ins.second ) ins.first->second = ( ins.first->second && cit->second );
  }
  nontrivialOperationDepth = std::max(nontrivialOperationDepth,S.nontrivialOperationDepth);
  return( dep? update( dep ): *this );
}

inline FFDep
FFDep::combine
( const FFDep&S1, const FFDep&S2, const TYPE&dep )
{
  FFDep S3( S1 );
  return S3.combine( S2, dep );
}

//AVT.SVT 22.05.2018
inline FFDep
FFDep::combineMult
( const FFDep&S1, const FFDep&S2, const TYPE&dep )
{
  // dep equals FFDep::P
  FFDep S3( S1 );
  // check whether both factors are linear, if not, the operation is polynomial, else it is quadratic
  // also check if the multiplication results in a multilinear or bilinear
  bool independent = true;
  FFDep::TYPE S1type = FFDep::L;
  FFDep::TYPE S2type = FFDep::L;
  auto cit = S1._dep.begin();
  for( ; cit != S1._dep.end(); ++cit ){
	 if(cit->second > FFDep::B) { return S3.combine( S2, dep ); }
	 if(cit->second > S1type) { S1type = (FFDep::TYPE)cit->second; }
  }
  cit = S2._dep.begin();
  t_FFDep depS1 = S1._dep;
  for( ; cit != S2._dep.end(); ++cit ){
	 if(cit->second > FFDep::B) { return S3.combine( S2, dep ); }
	 if(cit->second > S2type) { S2type = (FFDep::TYPE)cit->second; }
	 auto ins = depS1.insert( *cit);
	 if(!ins.second){ independent = false; }	//check whether any variable of S2 is already in S1
  }

  if(independent){ // case where the operands have no common variable
	  if(S1type >= FFDep::B || S2type >= FFDep::B) { return S3.combine(S2, dep); }
	  return S3.combine(S2, FFDep::B); // case x1*x2
  }else // case where the operands have at least one common variable
  {
	  if(S1type > FFDep::L || S2type > FFDep::L) { return S3.combine( S2, dep ); }
	  return S3.combine(S2, FFDep::Q);
  }
  return S3.combine( S2, dep );
}

//AVT.SVT 22.05.2018
inline FFDep
FFDep::copyQuad
( const FFDep&S, const TYPE&dep )
{
  // dep equals FFDep::P
  FFDep S2( S );
   // check whether the univariate factor is linear, if not, the operation is polynomial, else it is quadratic
  auto cit = S._dep.begin();
  for( ; cit != S._dep.end(); ++cit ){
	if(cit->second > FFDep::L){ return S2.update( dep); }
  }
  S2.nontrivialOperationDepth = S.nontrivialOperationDepth+1; // increase depth by 1
  return S2.update( FFDep::Q );
}

inline std::ostream&
operator<<
( std::ostream&out, const FFDep&S)
{
  out << "{ ";
  auto iS = S._dep.begin();
  for( ; iS != S._dep.end(); ++iS ){
    out << iS->first;
    switch( iS->second ){
     case FFDep::L: out << "L "; break;
     case FFDep::B: out << "B "; break;
     case FFDep::Q: out << "Q "; break;
     case FFDep::P: out << "P "; break;
     case FFDep::R: out << "R "; break;
     case FFDep::N: out << "N "; break;
	 case FFDep::D: out << "D "; break;
     default: throw FFDep::Exceptions( FFDep::Exceptions::INTERN );
    }
  }
  out << "}";
  return out;
}

inline FFDep
operator+
( const FFDep&S )
{
  return S;
}

inline FFDep
operator-
( const FFDep&S )
{
  return S;
}

inline FFDep
operator+
( const double c, const FFDep&S )
{
  return S;
}

inline FFDep
operator+
( const FFDep&S, const double c )
{
  return S;
}

inline FFDep
operator+
( const FFDep&S1, const FFDep&S2 )
{
  if( S1._dep.empty() ) return S2;
  if( S2._dep.empty() ) return S1;
  return FFDep::combine( S1, S2, FFDep::L );
}

inline FFDep
sum
( const unsigned int n, const FFDep*S )
{
  switch( n ){
   case 0:  return 0.;
   case 1:  return S[0];
   case 2:  return S[0] + S[1];
   default: return S[0] + sum( n-1, S+1 );
  }
}

inline FFDep
operator-
( const double c, const FFDep&S )
{
  return S;
}

inline FFDep
operator-
( const FFDep&S, const double c )
{
  return S;
}

inline FFDep
operator-
( const FFDep&S1, const FFDep&S2 )
{
  if( S1._dep.empty() ) return S2;
  if( S2._dep.empty() ) return S1;
  return FFDep::combine( S1, S2, FFDep::L );
}

inline FFDep
operator*
( const double c, const FFDep&S )
{
  return S;
}

inline FFDep
operator*
( const FFDep&S, const double c )
{
  return S;
}

inline FFDep
operator*
( const FFDep&S1, const FFDep&S2 )
{
  if( S1._dep.empty() ) return S2;
  if( S2._dep.empty() ) return S1;
  return FFDep::combineMult( S1, S2, FFDep::P );
}

inline FFDep
prod
( const unsigned int n, const FFDep*S )
{
  switch( n ){
   case 0:  return 0.;
   case 1:  return S[0];
   case 2:  return S[0] * S[1];
   default: return S[0] * prod( n-1, S+1 );
  }
}

inline FFDep
monom
( const unsigned int n, const FFDep*S, const unsigned*k )
{
  switch( n ){
   case 0:  return 0.;
   case 1:  return pow( S[0], (int)k[0] );
   default: return pow( S[0], (int)k[0] ) * monom( n-1, S+1, k+1 );
  }
}

inline FFDep
operator/
( const FFDep&S, const double c )
{
  return S;
}

inline FFDep
operator/
( const double c, const FFDep&S )
{
  return inv( S );
}

inline FFDep
operator/
( const FFDep&S1, const FFDep&S2 )
{
  if( S1._dep.empty() ) return inv( S2 );
  if( S2._dep.empty() ) return S1;
  return FFDep::combine( S1, inv( S2 ), FFDep::P );
}

inline FFDep
inv
( const FFDep &S )
{
  return FFDep::copy( S, FFDep::R );
}

inline FFDep
sqr
( const FFDep&S )
{
  return FFDep::copyQuad( S, FFDep::P );
}

inline FFDep
sqrt
( const FFDep&S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
exp
( const FFDep &S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
arh
( const FFDep &S, const double a )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
log
( const FFDep &S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
xlog
( const FFDep&S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
xexpax
( const FFDep&S, const double a )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
centerline_deficit
( const FFDep&S, const double xLim, const double type )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
wake_profile
( const FFDep&S, const double type )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
wake_deficit
( const FFDep&S1, const FFDep&S2, const double a, const double alpha, const double rr, const double type1, const double type2 )
{
  return FFDep::combine( S1, S2, FFDep::N );
}

inline FFDep
power_curve
( const FFDep&S, const double type )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
lmtd
( const FFDep&S1, const FFDep&S2 )
{

  return FFDep::combine( S1, S2, FFDep::N );
}

inline FFDep
rlmtd
( const FFDep&S1, const FFDep&S2 )
{
  return FFDep::combine( S1, S2, FFDep::N );
}

inline FFDep
mid
(const FFDep& S1, const FFDep& S2, const double k)
{
    return FFDep::combine(S1, S2, FFDep::N);
}

inline FFDep
pinch 
(const FFDep& Th, const FFDep& Tc, const FFDep& Tp)
{
    FFDep S4 = FFDep::combine(Th, Tc, FFDep::N);
    return FFDep::combine(S4, Tp, FFDep::N);
}
inline FFDep
pinch
(const FFDep& S1, const FFDep& S2)
{
    return FFDep::combine(S1, S2, FFDep::N);
}
inline FFDep
pinch
(const FFDep& S1)
{
    return FFDep::copy(S1, FFDep::N);
}


inline FFDep
euclidean_norm_2d
( const FFDep&S1, const FFDep&S2 )
{
  return FFDep::combine( S1, S2, FFDep::N );
}

inline FFDep
expx_times_y
( const FFDep&S1, const FFDep&S2 )
{
  return FFDep::combine( S1, S2, FFDep::N );
}

inline FFDep
vapor_pressure
( const FFDep&S, const double type, const double p1, const double p2, const double p3, const double p4 = 0,
  const double p5 = 0, const double p6 = 0, const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0)
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
ideal_gas_enthalpy
( const FFDep&S, const double x0, const double type, const double p1, const double p2, const double p3, const double p4,
  const double p5, const double p6 = 0, const double p7 = 0)
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
saturation_temperature
( const FFDep&S, const double type, const double p1, const double p2, const double p3, const double p4 = 0,
  const double p5 = 0, const double p6 = 0, const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0)
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
enthalpy_of_vaporization
( const FFDep&S, const double type, const double p1, const double p2, const double p3, const double p4,
  const double p5, const double p6 = 0 )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
cost_function
( const FFDep&S, const double type, const double p1, const double p2, const double p3 )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
sum_div
( const std::vector<FFDep>& S, const std::vector<double>& coeff)
{
	FFDep S2(coeff[1]*S[0]);
	for(size_t i = 1; i<S.size(); i++){
		S2 += coeff[i+1]*S[i];
	}
	for(unsigned int i = S.size()+1; i <coeff.size();i+=2 ){ // constants
		S2 += coeff[i]*coeff[i+1];
	}
	return coeff[0]*S[0]/S2;
}

inline FFDep
xlog_sum
( const std::vector<FFDep>& S, const std::vector<double>& coeff)
{
	FFDep S2(coeff[0]*S[0]);
	for(size_t i = 1; i<S.size(); i++){
		S2 += coeff[i]*S[i];
	}
	for(size_t i = S.size(); i <coeff.size();i+=2 ){
		S2 += coeff[i]*coeff[i+1];
	}
	return S[0]*log(S2);
}

inline FFDep
nrtl_tau
( const FFDep&S, const double a, const double b, const double e, const double f )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
nrtl_dtau
( const FFDep&S, const double b, const double e, const double f )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
nrtl_G
( const FFDep&S, const double a, const double b, const double e, const double f, const double alpha)
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
nrtl_Gtau
( const FFDep&S, const double a, const double b, const double e, const double f, const double alpha)
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
nrtl_Gdtau
( const FFDep&S, const double a, const double b, const double e, const double f, const double alpha)
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
nrtl_dGtau
( const FFDep&S, const double a, const double b, const double e, const double f, const double alpha)
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
iapws
( const FFDep&S, const double type )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
iapws
( const FFDep&S1, const FFDep&S2, const double type )
{
  return FFDep::combine( S1, S2, FFDep::N );
}

inline FFDep
p_sat_ethanol_schroeder
( const FFDep&S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
rho_vap_sat_ethanol_schroeder
( const FFDep&S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
rho_liq_sat_ethanol_schroeder
( const FFDep&S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
covariance_function
( const FFDep&S, const double type )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
acquisition_function
( const FFDep&S1, const FFDep&S2, const double type, const double fmin )
{
    switch((int)type){
		case 1: // lower confidence bound
		{
		    return FFDep::combine(S1, S2, FFDep::L);
		}
		case 2: // expected improvement
		{
		    return FFDep::combine(S1, S2, FFDep::N);
		}
		case 3: // probability of improvement
		{
		    return FFDep::combine(S1, S2, FFDep::N);
		}
		default:
		  throw std::runtime_error("mc::FFDep\t Acquisition function called with an unknown type.\n");
    }
}

inline FFDep
gaussian_probability_density_function
( const FFDep&S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
regnormal
( const FFDep&S, const double a, const double b )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
erf
( const FFDep &S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
erfc
( const FFDep &S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
fstep
( const FFDep &S )
{
  return FFDep::copy( S, FFDep::D );
}

inline FFDep
bstep
( const FFDep &S )
{
  return FFDep::copy( S, FFDep::D );
}

inline FFDep
fabs
( const FFDep&S )
{
  return FFDep::copy( S, FFDep::D );
}

inline FFDep
fabsx_times_x
( const FFDep&S )
{
  return FFDep::copy( S, FFDep::D );
}

inline FFDep
cheb
( const FFDep&S, const unsigned n )
{
  if( n == 0 ){ FFDep C; return C; }
  if( n == 1 ) return S;
  return FFDep::copy( S, FFDep::P );
}

inline FFDep
pow
( const FFDep&S, const int n )
{
  if( n == 0 ){ FFDep C; return C; }
  if( n == 1 ) return S;
  if( n == 2 ) return FFDep::copyQuad( S, FFDep::P );
  if( n < 0  ) return FFDep::copy( S, FFDep::R );
  return FFDep::copy( S, FFDep::P );
}

inline FFDep
pow
( const FFDep&S, const double a )
{
  if(a == 0.){FFDep S2; return S2;}
  if(a == 1.) return S;
  if( a == 2.) return FFDep::copyQuad( S, FFDep::P );
  if( a > 1. && a == std::ceil(a) ) return FFDep::copy( S, FFDep::P ); //std::rint(double x) not known in VS2010
  if( a < 0. && a == std::ceil(a) ) return FFDep::copy( S, FFDep::R );
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
pow
( const FFDep&S1, const FFDep&S2 )
{
  return FFDep::combine( S1, S2, FFDep::N );
}

inline FFDep
min
( const FFDep&S1, const FFDep&S2 )
{
  return FFDep::combine( S1, S2, FFDep::D );
}

inline FFDep
max
( const FFDep&S1, const FFDep&S2 )
{
  return FFDep::combine( S1, S2, FFDep::D );
}

inline FFDep
min
( const unsigned int n, const FFDep*S )
{
  switch( n ){
   case 0:  return 0.;
   case 1:  return S[0];
   case 2:  return min( S[0], S[1] );
   default: return min( S[0], min( n-1, S+1 ) );
  }
}

inline FFDep
max
( const unsigned int n, const FFDep*S )
{
  switch( n ){
   case 0:  return 0.;
   case 1:  return S[0];
   case 2:  return max( S[0], S[1] );
   default: return max( S[0], max( n-1, S+1 ) );
  }
}

inline FFDep
pos
( const FFDep&S )
{
  return S;
}

inline FFDep
neg
( const FFDep&S )
{
  return S;
}

inline FFDep
lb_func
( const FFDep&S, const double lb )
{
  return S;
}

inline FFDep
ub_func
( const FFDep&S, const double ub )
{
  return S;
}

inline FFDep
bounding_func
( const FFDep&S, const double lb, const double ub )
{
  return S;
}

inline FFDep
squash_node
( const FFDep&S, const double lb, const double ub )
{
  return S;
}

inline FFDep
single_neuron
( const std::vector<FFDep>& S, const std::vector<double>& w, const double b, const int type)
{
  FFDep S2(b);
	for(size_t i = 0; i<S.size(); i++){
		S2 += w[i]*S[i];
	}
  return FFDep::copy( S2, FFDep::N );
}

inline FFDep
mc_print
( const FFDep&S, const int number )
{
  return S;
}

inline FFDep
cos
( const FFDep&S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
sin
( const FFDep &S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
tan
( const FFDep&S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
acos
( const FFDep &S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
asin
( const FFDep &S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
atan
( const FFDep &S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
cosh
( const FFDep &S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
sinh
( const FFDep &S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
tanh
( const FFDep &S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
coth
( const FFDep &S )
{
  return FFDep::copy( S, FFDep::N );
}

inline FFDep
inter
( const FFDep&S1, const FFDep&S2 )
{
  return FFDep::combine( S1, S2, FFDep::N );
}

inline bool
operator==
( const FFDep&S1, const FFDep&S2 )
{
  return( S1._dep == S2._dep );
}

inline bool
operator!=
( const FFDep&S1, const FFDep&S2 )
{
  return( S1._dep != S2._dep );
}

inline bool
operator<=
( const FFDep&S1, const FFDep&S2 )
{
  return( S1._dep <= S2._dep );
}

inline bool
operator>=
( const FFDep&S1, const FFDep&S2 )
{
  return( S1._dep >= S2._dep );
}

inline bool
operator<
( const FFDep&S1, const FFDep&S2 )
{
  return( S1._dep < S2._dep );
}

inline bool
operator>
( const FFDep&S1, const FFDep&S2 )
{
  return( S1._dep > S2._dep );
}

} // namespace mc

namespace mc
{

//! @brief Specialization of the structure mc::Op to allow usage of the type mc::Interval for DAG evaluation or as a template parameter in other MC++ classes
template <> struct Op< mc::FFDep >
{
  typedef mc::FFDep FV;
  static FV point( const double c ) { return FV(c); }
  static FV zeroone() { throw typename FFDep::Exceptions( FFDep::Exceptions::UNDEF ); }
  static void I(FV& x, const FV&y) { x = y; }
  static double l(const FV& x) { throw typename FFDep::Exceptions( FFDep::Exceptions::UNDEF ); }
  static double u(const FV& x) { throw typename FFDep::Exceptions( FFDep::Exceptions::UNDEF ); }
  static double abs (const FV& x) { throw typename FFDep::Exceptions( FFDep::Exceptions::UNDEF );  }
  static double mid (const FV& x) { throw typename FFDep::Exceptions( FFDep::Exceptions::UNDEF );  }
  static double diam(const FV& x) { throw typename FFDep::Exceptions( FFDep::Exceptions::UNDEF ); }
  static FV inv (const FV& x) { return mc::inv(x);  }
  static FV sqr (const FV& x) { return mc::sqr(x);  }
  static FV sqrt(const FV& x) { return mc::sqrt(x); }
  static FV exp (const FV& x) { return mc::exp(x);  }
  static FV log (const FV& x) { return mc::log(x);  }
  static FV xlog(const FV& x) { return mc::xlog(x); }
  static FV fabsx_times_x(const FV& x) { return mc::fabsx_times_x(x); }
  static FV xexpax(const FV& x, const double a) { return mc::xexpax(x,a); }
  static FV centerline_deficit(const FV& x, const double xLim, const double type) { return mc::centerline_deficit(x,xLim,type); }
  static FV wake_profile(const FV& x, const double type) { return mc::wake_profile(x,type); }
  static FV wake_deficit(const FV& x, const FV& r, const double a, const double alpha, const double rr, const double type1, const double type2) { return mc::wake_deficit(x,r,a,alpha,rr,type1,type2); }
  static FV power_curve(const FV& x, const double type) { return mc::power_curve(x,type); }
  static FV lmtd(const FV& x, const FV& y) { return mc::lmtd(x,y); }
  static FV rlmtd(const FV& x, const FV& y) { return mc::rlmtd(x,y); }
  static FV mid(const FV& x, const FV& y, const double k) { return mc::mid(x, y, k); } 
  static FV pinch(const FV& Th, const FV& Tc, const FV& Tp) { return mc::pinch(Th, Tc, Tp); }
  static FV euclidean_norm_2d(const FV& x, const FV& y) { return mc::euclidean_norm_2d(x,y); }
  static FV expx_times_y(const FV& x, const FV& y) { return mc::expx_times_y(x,y); }
  static FV vapor_pressure(const FV& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
						   const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return mc::vapor_pressure(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10); }
  static FV ideal_gas_enthalpy(const FV& x, const double x0, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0,
							   const double p7 = 0) { return mc::ideal_gas_enthalpy(x,x0,type,p1,p2,p3,p4,p5,p6,p7); }
  static FV saturation_temperature(const FV& x, const double type, const double p1, const double p2, const double p3, const double p4 = 0, const double p5 = 0, const double p6 = 0,
								   const double p7 = 0, const double p8 = 0, const double p9 = 0, const double p10 = 0) { return mc::saturation_temperature(x,type,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10);}
  static FV enthalpy_of_vaporization(const FV& x, const double type, const double p1, const double p2, const double p3, const double p4, const double p5, const double p6 = 0) { return mc::enthalpy_of_vaporization(x,type,p1,p2,p3,p4,p5,p6); }
  static FV nrtl_tau(const FV& x, const double a, const double b, const double e, const double f) { return mc::nrtl_tau(x,a,b,e,f); }
  static FV nrtl_dtau(const FV& x, const double b, const double e, const double f) { return mc::nrtl_dtau(x,b,e,f); }
  static FV nrtl_G(const FV& x, const double a, const double b, const double e, const double f, const double alpha) { return mc::nrtl_G(x,a,b,e,f,alpha); }
  static FV nrtl_Gtau(const FV& x, const double a, const double b, const double e, const double f, const double alpha) { return mc::nrtl_Gtau(x,a,b,e,f,alpha); }
  static FV nrtl_Gdtau(const FV& x, const double a, const double b, const double e, const double f, const double alpha) { return mc::nrtl_Gdtau(x,a,b,e,f,alpha); }
  static FV nrtl_dGtau(const FV& x, const double a, const double b, const double e, const double f, const double alpha) { return mc::nrtl_dGtau(x,a,b,e,f,alpha); }
  static FV p_sat_ethanol_schroeder(const FV& x) { return mc::p_sat_ethanol_schroeder(x); }
  static FV rho_vap_sat_ethanol_schroeder(const FV& x) { return mc::rho_vap_sat_ethanol_schroeder(x); }
  static FV rho_liq_sat_ethanol_schroeder(const FV& x) { return mc::rho_liq_sat_ethanol_schroeder(x); }
  static FV covariance_function(const FV& x, const double type) { return mc::covariance_function(x,type); }
  static FV acquisition_function(const FV& x, const FV& y, const double type, const double fmin) { return mc::acquisition_function(x,y,type,fmin); }
  static FV gaussian_probability_density_function(const FV& x) { return mc::gaussian_probability_density_function(x); }
  static FV regnormal(const FV& x, const double a, const double b) { return mc::regnormal(x,a,b); }
  static FV fabs(const FV& x) { return mc::fabs(x); }
  static FV sin (const FV& x) { return mc::sin(x);  }
  static FV cos (const FV& x) { return mc::cos(x);  }
  static FV tan (const FV& x) { return mc::tan(x);  }
  static FV asin(const FV& x) { return mc::asin(x); }
  static FV acos(const FV& x) { return mc::acos(x); }
  static FV atan(const FV& x) { return mc::atan(x); }
  static FV sinh(const FV& x) { return mc::sinh(x); }
  static FV cosh(const FV& x) { return mc::cosh(x); }
  static FV tanh(const FV& x) { return mc::tanh(x); }
  static FV coth(const FV& x) { return mc::coth(x); }
  static FV erf (const FV& x) { return mc::erf(x);  }
  static FV erfc(const FV& x) { return mc::erfc(x); }
  static FV fstep(const FV& x) { return mc::fstep(x); }
  static FV bstep(const FV& x) { return mc::bstep(x); }
  static FV hull(const FV& x, const FV& y) { throw typename FFDep::Exceptions( FFDep::Exceptions::UNDEF ); }
  static FV min (const FV& x, const FV& y) { return mc::min(x,y);  }
  static FV max (const FV& x, const FV& y) { return mc::max(x,y);  }
  static FV pos (const FV& x) { return mc::pos(x);  }
  static FV neg (const FV& x) { return mc::neg(x);  }
  static FV lb_func(const FV& x, const double lb) { return mc::lb_func(x,lb); }
  static FV ub_func(const FV& x, const double ub) { return mc::ub_func(x,ub); }
  static FV bounding_func(const FV& x, const double lb, const double ub) { return mc::bounding_func(x,lb,ub); }
  static FV squash_node(const FV& x, const double lb, const double ub) { return mc::squash_node(x,lb,ub); }
  static FV mc_print(const FV& x, const int number) { return mc::mc_print(x,number); }
  static FV arh (const FV& x, const double k) { return mc::arh(x,k); }
  template <typename X, typename Y> static FV pow(const X& x, const Y& y) { return mc::pow(x,y); }
  static FV cheb(const FV& x, const unsigned n) { return mc::cheb(x,n); }
  static FV prod(const unsigned int n, const FV* x) { return mc::prod(n,x); }
  static FV monom(const unsigned int n, const FV* x, const unsigned* k) { return mc::monom(n,x,k); }
  static bool inter(FV& xIy, const FV& x, const FV& y) { xIy = mc::inter(x,y); return true; }
  static bool eq(const FV& x, const FV& y) { throw typename FFDep::Exceptions( FFDep::Exceptions::UNDEF ); }
  static bool ne(const FV& x, const FV& y) { throw typename FFDep::Exceptions( FFDep::Exceptions::UNDEF ); }
  static bool lt(const FV& x, const FV& y) { throw typename FFDep::Exceptions( FFDep::Exceptions::UNDEF ); }
  static bool le(const FV& x, const FV& y) { throw typename FFDep::Exceptions( FFDep::Exceptions::UNDEF ); }
  static bool gt(const FV& x, const FV& y) { throw typename FFDep::Exceptions( FFDep::Exceptions::UNDEF ); }
  static bool ge(const FV& x, const FV& y) { throw typename FFDep::Exceptions( FFDep::Exceptions::UNDEF ); }
};

} // namespace mc

#endif
