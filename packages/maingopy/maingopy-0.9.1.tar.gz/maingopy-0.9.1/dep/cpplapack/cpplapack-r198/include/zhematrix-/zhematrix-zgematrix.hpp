//=============================================================================
/*! zhematrix+zgematrix operator */
inline _zgematrix operator+(const zhematrix& matA, const zgematrix& matB)
{CPPL_VERBOSE_REPORT;
#ifdef  CPPL_DEBUG
  if(matA.n!=matB.n || matA.n!=matB.m){
    ERROR_REPORT;
    std::cerr << "These two matrises can not make a summation." << std::endl
              << "Your input was (" << matA.n << "x" << matA.n << ") + (" << matB.m << "x" << matB.n << ")." << std::endl;
    exit(1);
  }
#endif//CPPL_DEBUG
  
  zgematrix newmat =matB;
  
  for(CPPL_INT i=0; i<matA.n; i++){
    for(CPPL_INT j=0; j<matA.n; j++){
      newmat(i,j) += matA(i,j);
    }
  }
  
  return _(newmat);
}

//=============================================================================
/*! zhematrix-zgematrix operator */
inline _zgematrix operator-(const zhematrix& matA, const zgematrix& matB)
{CPPL_VERBOSE_REPORT;
#ifdef  CPPL_DEBUG
  if(matA.n!=matB.n || matA.n!=matB.m){
    ERROR_REPORT;
    std::cerr << "These two matrises can not make a summation." << std::endl
              << "Your input was (" << matA.n << "x" << matA.n << ") + (" << matB.m << "x" << matB.n << ")." << std::endl;
    exit(1);
  }
#endif//CPPL_DEBUG
  
  zgematrix newmat =-matB;
  
  for(CPPL_INT i=0; i<matA.n; i++){
    for(CPPL_INT j=0; j<matA.n; j++){
      newmat(i,j) += matA(i,j);
    }
  }
  
  return _(newmat);
}

//=============================================================================
/*! zhematrix*zgematrix operator */
inline _zgematrix operator*(const zhematrix& matA, const zgematrix& matB)
{CPPL_VERBOSE_REPORT;
#ifdef  CPPL_DEBUG
  if(matA.n!=matB.m){
    ERROR_REPORT;
    std::cerr << "These two matrises can not make a product." << std::endl
              << "Your input was (" << matA.n << "x" << matA.n << ") * (" << matB.m << "x" << matB.n << ")." << std::endl;
    exit(1);
  }
#endif//CPPL_DEBUG
  
  zgematrix newmat( matA.n, matB.n );
  char side ='l';
  char uplo ='l';
  comple alpha =comple(1.,0.);
  comple beta =comple(0.,0.);
  
  zhemm_( &side, &uplo, &matA.n, &matB.n, &alpha, matA.array, &matA.n, matB.array, &matB.m, &beta, newmat.array, &newmat.m );
  
  return _(newmat);
}
