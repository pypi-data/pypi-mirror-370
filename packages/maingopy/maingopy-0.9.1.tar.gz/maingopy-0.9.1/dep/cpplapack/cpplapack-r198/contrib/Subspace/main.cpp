/*****************************************************************************/
/*                                main.cpp                                   */
/*****************************************************************************/
//=============================================================================
#include <iostream>
#include <cstdlib>
#include <ctime>
#include <vector>
#include "cpplapack.h"

//=============================================================================
/* the simplest block subspace itration */
template <typename MATRIX>
bool block_subspace_simplest
(
 const MATRIX& A,
 CPPL::drovector& lambda,
 CPPL::dgematrix& V, //V.m >= V.n
 const double& eps,
 const int& itmax
 )
{
  //////// initialization ////////
  srand(time(NULL));
  for(int i=0; i<V.m; i++){ for(int j=0;j<V.n; j++){ V(i,j)=rand(); } }
  CPPL::dgematrix V_new;
  double *tau(new double[V.n]), *work(new double[V.n]);
  int info, itc(0);
  
  //////// loop ////////
  while(++itc<itmax){
    //// ortonormalize ////
    CPPL::dgeqrf_(&V.m, &V.n, V.array, &V.m, tau, work, &V.n, &info);
    if(info!=0){ std::cerr << "info = " << info << std::endl; }
    CPPL::dorgqr_(&V.m, &V.n, &V.n, V.array, &V.m, tau, work, &V.n, &info);
    if(info!=0){ std::cerr << "info = " << info << std::endl; }
    
    //// power method ////
    V_new =A*V;
    lambda =V_new%V;
    
    //// convergence check ////
    double rmax(0.);
    for(int k=0; k<V.n; k++){
      CPPL::dcovector rv( V_new.col(k)/lambda(k) -V.col(k) );
      rmax =std::max( rmax, fabs(damax(rv)) );
      if(rmax>eps){ break; }//failed
    }
    if(rmax<eps){ break; }//converged
    
    //// update ////
    swap(V,V_new);
  }
  std::cerr << "itc=" << itc << std::endl;
  
  if(itc<itmax){
    std::cerr << "[NOTE]@block_subspace_simplest: converged!!!!!!\n" << std::endl;
    return 0;
  }
  else{
    std::cerr << "[WARNING]@block_subspace_simplest: not converged......\n" << std::endl;
    return 1;
  }
}

//=============================================================================
/* block subspace itration with projection */
template <typename MATRIX>
bool block_subspace_projection
(
 const MATRIX& A,//a symmetrix matrix
 CPPL::drovector& lambda,
 CPPL::dgematrix& V, //V.m >= V.n
 const double& eps,
 const int& itmax
 )
{
  //////// initialization ////////
  char jobz ='V';
  char uplo ='L';
  double *tau =new double[V.n];
  double *work =new double[V.n];
  double *work2 =new double[3*V.n-1];
  int lwork =3*V.n-1;
  int info;
  //// make initial V ////
  srand(time(NULL));
  for(int i=0; i<V.m; i++){
    for(int j=0;j<V.n; j++){
      V(i,j) =double(rand())/double(RAND_MAX);
    }
  }
  
  //////// loop ////////
  size_t itc =0;
  while(++itc<itmax){
    //// ortonormalize ////
    CPPL::dgeqrf_(&V.m, &V.n, V.array, &V.m, tau, work, &V.n, &info);
    if(info!=0){ std::cerr << "[ERROR]dgeqrf_ info = " << info << std::endl; exit(1); }
    CPPL::dorgqr_(&V.m, &V.n, &V.n, V.array, &V.m, tau, work, &V.n, &info);
    if(info!=0){ std::cerr << "[ERROR]dorgqr_ info = " << info << std::endl; exit(1); }
    std::cerr << "V=\n" << V;
    
    //// make Schur vectors S ////
    CPPL::dgematrix S =(t(V)*A)*V;
    CPPL::dsyev_(&jobz, &uplo, &S.n, S.array, &S.n, lambda.array, work2, &lwork, &info);
    if(info!=0){ std::cerr << "[ERROR]dsyev_ info = " << info << std::endl; exit(1); }
    //std::cerr << "lambda = " << lambda << std::endl;
    
    //// convergence check ////
    CPPL::dgematrix lhs =A*V;
    CPPL::dgematrix tmp =lhs;
    for(int j=0; j<tmp.n; j++){
      for(int i=0; i<tmp.m; i++){
        tmp(i,j) /=lambda(j);
      }
    }
    std::cerr << "tmp=\n" << tmp;
    double rmax =fabs(damax((tmp-V)));
    std::cerr << "rmax=" << rmax << std::endl;
    if(rmax<eps){ break; }//converged
    
    //// update ////
    V =lhs*S;
  }
  std::cerr << "itc=" << itc << std::endl;
  
  if(itc<itmax){
    std::cerr << "[NOTE]@block_subspace_projection: converged!!!!!!\n" << std::endl;
    return 0;
  }
  else{
    std::cerr << "[WARNING]@block_subspace_projection: not converged......\n" << std::endl;
    return 1;
  }
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

//=============================================================================
/* block subspace itration with projection and deflation */
template <typename MATRIX>
bool block_subspace_projection_deflation
(
 const MATRIX& A,//a symmetrix matrix
 CPPL::drovector& lambda,
 CPPL::dgematrix& V, //V.m >= V.n
 const double& eps,
 const int& itmax
 )
{
  //////// initialization ////////
  srand(time(NULL));
  lambda.resize(V.n);
  CPPL::dgematrix V_yet, AV_yet, Y(V.m,V.n), V_new(V.m,V.n);
  CPPL::drovector lambda_yet(V.n);
  double *tau(new double[V.n]), *work(new double[V.n]), *work2(new double[3*V.n-1]);
  int info, itc(0);
  int nconv(0);
  
  //// make initial V ////
  for(int i=0; i<V.m; i++){ for(int j=0;j<V.n; j++){ V(i,j)=rand(); } }
  CPPL::dgeqrf_(&V.m, &V.n, V.array, &V.m, tau, work, &V.n, &info);
  if(info!=0){ std::cerr << "[ERROR]dgeqrf_ info = " << info << std::endl; exit(1); }
  CPPL::dorgqr_(&V.m, &V.n, &V.n, V.array, &V.m, tau, work, &V.n, &info);
  if(info!=0){ std::cerr << "[ERROR]dorgqr_ info = " << info << std::endl; exit(1); }
  
  //////// main loop ////////
  char jobz ='V';
  char uplo ='L';
  int lwork =3*V.n-1;
  while(++itc<itmax){
    //// make V_yet ////
    V_yet.resize(V.m, V.n-nconv);
    for(int j=0; j<V.n-nconv; j++){
      for(int i=0; i<V.m; i++){
        V_yet(i,j) =V(i,j);
      }
    }
h    
    //// power method ////
    AV_yet =A*V_yet;
    
    //// make Y ////
    for(int j=0; j<V.n-nconv; j++){
      for(int i=0; i<V.m; i++){
        Y(i,j) =AV_yet(i,j);
      }
    }
    for(int j=V.n-nconv; j<V.n; j++){
      for(int i=0; i<V.m; i++){
        Y(i,j) =V(i,j);
      }
    }
    
    //// ortonormalize ////
    CPPL::dgeqrf_(&Y.m, &Y.n, Y.array, &Y.m, tau, work, &Y.n, &info);
    if(info!=0){ std::cerr << "[ERROR]dgeqrf_ info = " << info << std::endl; exit(1); }
    CPPL::dorgqr_(&Y.m, &Y.n, &Y.n, Y.array, &Y.m, tau, work, &Y.n, &info);
    if(info!=0){ std::cerr << "[ERROR]dorgqr_ info = " << info << std::endl; exit(1); }
    
    //// remake V_yet ////
    for(int j=0; j<V.n-nconv; j++){
      for(int i=0; i<V.m; i++){
        V_yet(i,j) =Y(i,j);
      }
    }
    
    //// make Schur vectors S ////
    CPPL::dgematrix S( t(V_yet)*(A*V_yet) );
    CPPL::dsyev_(&jobz, &uplo, &S.n, S.array, &S.n, lambda_yet.array, work2, &lwork, &info);
    
    if(info!=0){ std::cerr << "[ERROR]dsyev_ info = " << info << std::endl; exit(1); }
    //std::cerr << "lambda_yet B= " << lambda_yet << std::endl;
    
    //// update lambda ////
    for(int j=0; j<V.n-nconv; j++){
      lambda(j) =lambda_yet(j);
    }
    
    //// make V_new ////
    V_yet =V_yet*S;
    for(int j=0; j<V.n-nconv; j++){
      for(int i=0; i<V.m; i++){
        V_new(i,j) =V_yet(i,j);
      }
    }
    for(int j=V.n-nconv; j<V.n; j++){
      for(int i=0; i<V.m; i++){
        V_new(i,j) =V(i,j);
      }
    }
    
    //// convergence check ////
    int nconv_new(nconv);
    for(int j=V.n-nconv-1; j>=0; j--){
      //if( nconv_new>0 ){
      //std::cerr << "lambda(j)             = " << lambda(j) << std::endl;
      //std::cerr << "lambda(V.n-nconv_new) = " << lambda(V.n-nconv_new) << std::endl;
      //}
      if( nconv_new>0 && lambda(j)>lambda(V.n-nconv_new) ){ break; }//failed
      CPPL::dcovector rv( V_new.col(j) -V.col(j) );
      if(fabs(damax(rv))>eps){ break; }//failed
      nconv_new++;
    }
    if(nconv_new==V.n){ break; }//all converged
    //std::cerr << "nconv_new = " << nconv_new << std::endl;
    
    //// update ////
    V =V_new;
    nconv =nconv_new;
  }
  std::cerr << "itc=" << itc << std::endl;
  
  if(itc<itmax){
    std::cerr << "[NOTE]@block_subspace_projection_deflation: converged!!!!!!\n" << std::endl;
    return 0;
  }
  else{
    std::cerr << "[WARNING]@block_subspace_projection_deflation: not converged......\n" << std::endl;
    return 1;
  }
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

//=============================================================================
int main(int /*argc*/, char** /*argv*/)
{
  std::cout.precision(6);
  std::cout.setf(std::ios::scientific, std::ios::floatfield);
  std::cout.setf(std::ios::showpos);
  std::cerr.precision(6);
  std::cerr.setf(std::ios::scientific, std::ios::floatfield);
  std::cerr.setf(std::ios::showpos);
  
  //////// objects ////////
  CPPL::dssmatrix A("K6.dssmatrix");
  //CPPL::dssmatrix A("K810.dssmatrix");
  std::cout << "A=\n" << A << std::endl;
  
  const int num_of_eigen(3);
  CPPL::drovector lambda(num_of_eigen);
  CPPL::dgematrix V(A.m,num_of_eigen);
  
  //////// subspace ////////
  //block_subspace_simplest(A,lambda,V,1e-3,A.m*A.n);//unstable
  //block_subspace_projection(A,lambda,V,1e-3,A.m*A.n);//better
  block_subspace_projection_deflation(A,lambda,V,1e-3,A.m*A.n);//YET UNSTABLE!!!!!!!
  
  //////// print ////////
  for(int k=V.n-1; k>=0; k--){
    std::cout << "lambda(" << k << ") = " << lambda(k) << std::endl;
    std::cout << "v(" << k << ") = " << t(V.col(k)) << std::flush;
    //std::cout << "residual=" << t( A*V.col(k)/lambda(k)-V.col(k) ) << std::endl;
    //std::cout << "nrm2(residual)=" << nrm2( A*V.col(k)/lambda(k)-V.col(k) ) << std::endl;
    std::cout << std::endl;
  }
  
  std::cout << std::endl << std::endl;
  
  //////// verify ////////
  CPPL::dsymatrix B(A.to_dsymatrix());
  std::vector<double> w;
  std::vector<CPPL::dcovector> v;
  B.dsyev(w,v);
  for(int k=B.n-1; k>=B.n-V.n; k--){
    std::cout << "answer lambda[" << k << "] = " << w[k] << std::endl;
    std::cout << "answer v[" << k << "] = " << t(v[k]) << std::endl;
  }
  
  return 0;
}
