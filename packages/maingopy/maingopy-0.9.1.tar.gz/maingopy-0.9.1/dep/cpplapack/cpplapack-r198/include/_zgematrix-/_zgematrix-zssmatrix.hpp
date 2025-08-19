//=============================================================================
/*! _zgematrix+zhematrix operator */
inline _zgematrix operator+(const _zgematrix& matA, const zhematrix& matB)
{CPPL_VERBOSE_REPORT;
#ifdef  CPPL_DEBUG
  if(matA.m!=matB.m || matA.n!=matB.n){
    ERROR_REPORT;
    std::cerr << "These two matrises can not make a summation." << std::endl
              << "Your input was (" << matA.m << "x" << matA.n << ") + (" << matB.m << "x" << matB.n << ")." << std::endl;
    exit(1);
  }
#endif//CPPL_DEBUG
  
  for(CPPL_INT c=0; c<matB.vol; c++){
    matA(matB.indx[c],matB.jndx[c]) += matB.array[c];
  }
  
  return matA;
}

//=============================================================================
/*! _zgematrix-zhematrix operator */
inline _zgematrix operator-(const _zgematrix& matA, const zhematrix& matB)
{CPPL_VERBOSE_REPORT;
#ifdef  CPPL_DEBUG
  if(matA.m!=matB.m || matA.n!=matB.n){
    ERROR_REPORT;
    std::cerr << "These two matrises can not make a subtraction." << std::endl
              << "Your input was (" << matA.m << "x" << matA.n << ") - (" << matB.n << "x" << matB.n << ")." << std::endl;
    exit(1);
  }
#endif//CPPL_DEBUG
  
  //// change sign ////
  for(CPPL_INT i=0; i<matA.m*matA.n; i++){
    matA.array[i]=-matA.array[i];
  }
  
  //// add ////
  for(CPPL_INT c=0; c<matB.vol; c++){
    matA(matB.indx[c],matB.jndx[c]) += matB.array[c];
  }
  
  return matA;
}

//=============================================================================
/*! _zgematrix*zhematrix operator */
inline _zgematrix operator*(const _zgematrix& matA, const zhematrix& matB)
{CPPL_VERBOSE_REPORT;
#ifdef  CPPL_DEBUG
  if(matA.n!=matB.m){
    ERROR_REPORT;
    std::cerr << "These two matrises can not make a product." << std::endl
              << "Your input was (" << matA.m << "x" << matA.n << ") * (" << matB.n << "x" << matB.n << ")." << std::endl;
    exit(1);
  }
#endif//CPPL_DEBUG
  
  zgematrix newmat(matA.m, matB.n);
  newmat.zero();
  
  for(CPPL_INT c=0; c<matB.vol; c++){
    for(CPPL_INT i=0; i<matA.m; i++){
      newmat(i,matB.jndx[c]) += matA(i,matB.indx[c])*matB.array[c];
    }
  }
  
  matA.destroy();
  return _(newmat);
}
