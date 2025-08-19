#ifndef MC__NUMERICS_HPP
#define MC__NUMERICS_HPP

#include <vector>

namespace numerics {
	
	
 typedef double (puniv)
    ( const double x, const double*rusr, const int*iusr );
  //! @brief Newton method for root finding 
  double newton
    ( const double x0, const double xL, const double xU, puniv f,
      puniv df, const double*rusr, const int*iusr=0 );
  //! @brief Secant method for root finding 
  double secant
    ( const double x0, const double x1, const double xL, const double xU,
      puniv f, const double*rusr, const int*iusr=0 );
  //! @brief Golden section search method for root finding 
  double goldsect
    ( const double xL, const double xU, puniv f, const double*rusr,
      const int*iusr=0 );
  //! @brief Golden section search iterations 
  double goldsect_iter
    ( const bool init, const double a, const double fa, const double b,
      const double fb, const double c, const double fc, puniv f,
      const double*rusr, const int*iusr=0 );
	  
	
inline double
machprec()
{
  return 1e4*std::numeric_limits<double>::epsilon();
}
	
	  
inline bool
isequal
( const double real1, const double real2, const double atol=machprec(),
  const double rtol=machprec() )
{
  // Test if two real values are within the same absolute and relative
  // tolerances
  double gap = std::fabs(real1-real2);
  double ave = 0.5*std::fabs(real1+real2);
  return( gap>atol+ave*rtol? false: true );
}


// x0 is starting point, xL is left bound, xU is right bound, f is the function to be solved for f=0, df is the derivative of f,
// *rusr is a user defined double, *iusr is a user defined integer, vusr is a user defined vector	   
inline double
newton
( const double x0, const double xL, const double xU, puniv f,
  puniv df, const double*rusr, const int*iusr )
{

  double xk = std::max(xL,std::min(xU,x0));
  double fk = f(xk,rusr,iusr);
  
  for( unsigned int it=0; it<100; it++ ){
    if( std::fabs(fk) < machprec()) return xk;
     double dfk = df(xk,rusr,iusr);
    if( dfk == 0 ) throw(-1);
    if( isequal(xk,xL) && fk/dfk>0 ) return xk;
    if( isequal(xk,xU) && fk/dfk<0 ) return xk;
    xk = std::max(xL,std::min(xU,xk-fk/dfk));
    fk = f(xk,rusr,iusr);
  }

  throw(-1);
}


inline double
secant
( const double x0, const double x1, const double xL, const double xU,
  puniv f, const double*rusr, const int*iusr )
{
  double xkm = std::max(xL,std::min(xU,x0));
  double fkm = f(xkm,rusr,iusr);
  double xk = std::max(xL,std::min(xU,x1));
  
  for( unsigned int it=0; it<100; it++ ){
    double fk = f(xk,rusr,iusr);
    if( std::fabs(fk) < machprec() ) return xk;
    double Bk = (fk-fkm)/(xk-xkm);
    if( Bk == 0 ) throw(-1);
    if( isequal(xk,xL) && fk/Bk>0 ) return xk;
    if( isequal(xk,xU) && fk/Bk<0 ) return xk;
    xkm = xk;
    fkm = fk;
    xk = std::max(xL,std::min(xU,xk-fk/Bk));
  }

  throw(-1);
}

inline double
goldsect
( const double xL, const double xU, puniv f, const double*rusr,
  const int*iusr )
{
  const double phi = 2.-(1.+std::sqrt(5.))/2.;
  const double fL = f(xL,rusr,iusr), fU = f(xU,rusr,iusr);
  if( fL*fU > 0 ) throw(-1);
  const double xm = xU-phi*(xU-xL), fm = f(xm,rusr,iusr);
  return goldsect_iter( true, xL, fL, xm, fm, xU, fU, f, rusr, iusr );
}

inline double
goldsect_iter
( const bool init, const double a, const double fa, const double b,
  const double fb, const double c, const double fc, puniv f,
  const double*rusr, const int*iusr )
// a and c are the current bounds; the minimum is between them.
// b is a center point
{
  static thread_local unsigned int iter;
  iter = ( init? 1: iter+1 );
  const double phi = 2.-(1.+std::sqrt(5.))/2.;
  bool b_then_x = ( c-b > b-a );
  double x = ( b_then_x? b+phi*(c-b): b-phi*(b-a) );
  if( std::fabs(c-a) < 1e-12*(std::fabs(b)+std::fabs(x)) 
   || iter > 100 ) return (c+a)/2.;
  double fx = f(x,rusr,iusr);
  if( b_then_x )
    return( fa*fx<0? goldsect_iter( false, a, fa, b, fb, x, fx, f, rusr, iusr ):
                      goldsect_iter( false, b, fb, x, fx, c, fc, f, rusr, iusr ) );
  return( fa*fb<0? goldsect_iter( false, a, fa, x, fx, b, fb, f, rusr, iusr ):
                    goldsect_iter( false, x, fx, b, fb, c, fc, f, rusr, iusr ) );
}


} // end namespace numerics

#endif