//=============================================================================
/*! zgbmatrix=zgbmatrix operator\n
  The left side matrix is overwritten thoroughly including band width. */
inline zgbmatrix& zgbmatrix::operator=(const zgbmatrix& mat)
{CPPL_VERBOSE_REPORT;
  if(array!=mat.array){ // if it is NOT self substitution
    copy(mat);
  }
  return *this;
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

//=============================================================================
/*! zgbmatrix+=zgbmatrix operator\n
  If the band width of the left side matrix is narrower than the right side matrix, the band width of the left side matrix become thicker as same as the right side matrix. */
inline zgbmatrix& zgbmatrix::operator+=(const zgbmatrix& mat)
{CPPL_VERBOSE_REPORT;
#ifdef  CPPL_DEBUG
  if(n!=mat.n || m!=mat.m){
    ERROR_REPORT;
    std::cerr << "These two matrises can not make a summation." << std::endl
              << "Your input was" << "(" << m <<"x"<< n <<","<< kl <<":"<< ku << ") "<< "+=" << "("<< mat.m <<"x"<< mat.n <<","<< mat.kl <<":"<< mat.ku <<") " << std::endl;
    exit(1);
  }
#endif//CPPL_DEBUG
  
  if(kl>=mat.kl && ku>=mat.ku){
    for(CPPL_INT i=0; i<m; i++){
      const CPPL_INT jmax =std::min(n,i+mat.ku+1);
      for(CPPL_INT j=std::max(CPPL_INT(0),i-mat.kl); j<jmax; j++){
        operator()(i,j) += mat(i,j);
      }
    }
    
    return *this;
  }
  
  else{
    zgbmatrix newmat(m,n,std::max(kl,mat.kl),std::max(ku,mat.ku));
    newmat.zero();
    for(CPPL_INT i=0; i<m; i++){
      const CPPL_INT jmax1 =std::min(n,i+ku+1);
      for(CPPL_INT j=std::max(CPPL_INT(0),i-kl); j<jmax1; j++){
        newmat(i,j) += operator()(i,j);
      }
      const CPPL_INT jmax2 =std::min(mat.n,i+mat.ku+1);
      for(CPPL_INT j=std::max(CPPL_INT(0),i-mat.kl); j<jmax2; j++){
        newmat(i,j) += mat(i,j);
      }
    }
    
    swap(*this,newmat);
    return *this;
  }
}

//=============================================================================
/*! zgbmatrix-=zgbmatrix operator\n
  If the band width of the left side matrix is narrower than the right side matrix, the band width of the left side matrix become thicker as same as the right side matrix. */
inline zgbmatrix& zgbmatrix::operator-=(const zgbmatrix& mat)
{CPPL_VERBOSE_REPORT;
#ifdef  CPPL_DEBUG
  if(n!=mat.n || m!=mat.m){
    ERROR_REPORT;
    std::cerr << "These two matrises can not make a subtraction." << std::endl
              << "Your input was" << "(" << m <<"x"<< n <<","<< kl <<":"<< ku << ") "<< "-=" << "("<< mat.m <<"x"<< mat.n <<","<< mat.kl <<":"<< mat.ku <<") " << std::endl;
    exit(1);
  }
#endif//CPPL_DEBUG
  
  if(kl>=mat.kl && ku>=mat.ku){
    for(CPPL_INT i=0; i<m; i++){
      const CPPL_INT jmax =std::min(n,i+mat.ku+1);
      for(CPPL_INT j=std::max(CPPL_INT(0),i-mat.kl); j<jmax; j++){
        operator()(i,j) -= mat(i,j);
      }
    }
    
    return *this;
  }
  
  else{
    zgbmatrix newmat(m,n,std::max(kl,mat.kl),std::max(ku,mat.ku));
    newmat.zero();
    for(CPPL_INT i=0; i<m; i++){
      const CPPL_INT jmax1 =std::min(n,i+ku+1);
      for(CPPL_INT j=std::max(CPPL_INT(0),i-kl); j<jmax1; j++){
        newmat(i,j) += operator()(i,j);
      }
      const CPPL_INT jmax2 =std::min(mat.n,i+mat.ku+1);
      for(CPPL_INT j=std::max(CPPL_INT(0),i-mat.kl); j<jmax2; j++){
        newmat(i,j) -= mat(i,j);
      }
    }
    
    swap(*this,newmat);
    return *this;
  }
}

//=============================================================================
/*! zgbmatrix*=zgbmatrix operator */
inline zgbmatrix& zgbmatrix::operator*=(const zgbmatrix& mat)
{CPPL_VERBOSE_REPORT;
#ifdef  CPPL_DEBUG
  if(n!=mat.m){
    ERROR_REPORT;
    std::cerr << "These two matrises can not make a product." << std::endl
              << "Your input was (" << m << "x" << n << ") * (" << mat.m << "x" << mat.n << ")." << std::endl;
    exit(1);
  }
#endif//CPPL_DEBUG
  
  zgbmatrix newmat( m, mat.n, std::min(kl+mat.kl, m-1), std::min(ku+mat.ku, mat.n-1) );
  newmat.zero();
  
  for(CPPL_INT i=0; i<newmat.m; i++){
    const CPPL_INT jmax =std::min(newmat.n,i+newmat.ku+1);
    for(CPPL_INT j=std::max(CPPL_INT(0),i-newmat.kl); j<jmax; j++){
      const CPPL_INT kmax =std::min( std::min(n,i+ku+1), std::min(mat.m,j+mat.kl+1) );
      for(CPPL_INT k=std::max( std::max(CPPL_INT(0),i-kl), std::max(CPPL_INT(0),j-mat.ku) ); k<kmax; k++){
        newmat(i,j)+= operator()(i,k)*mat(k,j);
      }
    }
  }
  
  swap(*this,newmat);
  return *this;
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

//=============================================================================
/*! zgbmatrix+zgbmatrix operator */
inline _zgbmatrix operator+(const zgbmatrix& matA, const zgbmatrix& matB)
{CPPL_VERBOSE_REPORT;
#ifdef  CPPL_DEBUG
  if(matA.n!=matB.n || matA.m!=matB.m){
    ERROR_REPORT;
    std::cerr << "These two matrises can not make a summation." << std::endl
              << "Your input was (" << matA.m << "x" << matA.n << ") + (" << matB.m << "x" << matB.n << ")." << std::endl;
    exit(1);
  }
#endif//CPPL_DEBUG
  
  zgbmatrix newmat(matA.m,matA.n,std::max(matA.kl,matB.kl),std::max(matA.ku,matB.ku));
  newmat.zero();
  
  for(CPPL_INT i=0; i<matA.m; i++){
    const CPPL_INT jmax1 =std::min(matA.n,i+matA.ku+1);
    for(CPPL_INT j=std::max(CPPL_INT(0),i-matA.kl); j<jmax1; j++){
      newmat(i,j) += matA(i,j);
    }
    const CPPL_INT jmax2 =std::min(matB.n,i+matB.ku+1);
    for(CPPL_INT j=std::max(CPPL_INT(0),i-matB.kl); j<jmax2; j++){
      newmat(i,j) += matB(i,j);
    }
  }
  
  return _(newmat);
}

//=============================================================================
/*! zgbmatrix-zgbmatrix operator */
inline _zgbmatrix operator-(const zgbmatrix& matA, const zgbmatrix& matB)
{CPPL_VERBOSE_REPORT;
#ifdef  CPPL_DEBUG
  if(matA.n!=matB.n || matA.m!=matB.m){
    ERROR_REPORT;
    std::cerr << "These two matrises can not make a subtraction." << std::endl
              << "Your input was (" << matA.m << "x" << matA.n << ") - (" << matB.m << "x" << matB.n << ")." << std::endl;
    exit(1);
  }
#endif//CPPL_DEBUG
  
  zgbmatrix newmat(matA.m,matA.n,std::max(matA.kl,matB.kl),std::max(matA.ku,matB.ku));
  newmat.zero();
  
  for(CPPL_INT i=0; i<matA.m; i++){
    const CPPL_INT jmax1 =std::min(matA.n,i+matA.ku+1);
    for(CPPL_INT j=std::max(CPPL_INT(0),i-matA.kl); j<jmax1; j++){
      newmat(i,j) += matA(i,j);
    }
    const CPPL_INT jmax2 =std::min(matB.n,i+matB.ku+1);
    for(CPPL_INT j=std::max(CPPL_INT(0),i-matB.kl); j<jmax2; j++){
      newmat(i,j) -= matB(i,j);
    }
  }
  
  return _(newmat);
}

//=============================================================================
/*! zgbmatrix*zgbmatrix operator */
inline _zgbmatrix operator*(const zgbmatrix& matA, const zgbmatrix& matB)
{CPPL_VERBOSE_REPORT;
#ifdef  CPPL_DEBUG
  if(matA.n!=matB.m){
    ERROR_REPORT;
    std::cerr << "These two matrises can not make a product." << std::endl
              << "Your input was (" << matA.m << "x" << matA.n << ") * (" << matB.m << "x" << matB.n << ")." << std::endl;
    exit(1);
  }
#endif//CPPL_DEBUG
  
  zgbmatrix newmat( matA.m, matB.n, std::min(matA.kl+matB.kl,matA.m-1), std::min(matA.ku+matB.ku,matB.n-1) );
  newmat.zero();
  
  for(CPPL_INT i=0; i<newmat.m; i++){
    const CPPL_INT jmax =std::min(newmat.n,i+newmat.ku+1);
    for(CPPL_INT j=std::max(CPPL_INT(0),i-newmat.kl); j<jmax; j++){
      const CPPL_INT kmax =std::min( std::min(matA.n,i+matA.ku+1), std::min(matB.m,j+matB.kl+1) );
      for(CPPL_INT k=std::max( std::max(CPPL_INT(0),i-matA.kl), std::max(CPPL_INT(0),j-matB.ku) ); k<kmax; k++){
        newmat(i,j) += matA(i,k)*matB(k,j);
      }
    }
  }
  
  return _(newmat);
}
