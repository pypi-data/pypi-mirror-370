//=============================================================================
/*! drovector_small constructor */
template<CPPL_INT l>
inline drovector_small<l>::drovector_small()
{CPPL_VERBOSE_REPORT;
  ;
}

//=============================================================================
/*! drovector_small constructor */
template<CPPL_INT l>
inline drovector_small<l>::drovector_small(const drovector& vec)
{CPPL_VERBOSE_REPORT;
#ifdef  CPPL_DEBUG
  if( l!=vec.l ){
    ERROR_REPORT;
    std::cerr << "Vector sizes must be the same." << std::endl
              << "Your input was " << l << " and " << vec.l << "." << std::endl;
    exit(1);
  }
#endif//CPPL_DEBUG
  
  for(CPPL_INT k=0; k<l; k++){
    array[k] =vec.array[k];
  }
}

//=============================================================================
/*! drovector_small constructor */
template<CPPL_INT l>
inline drovector_small<l>::drovector_small(const double& x, const double& y)
{CPPL_VERBOSE_REPORT;
#ifdef  CPPL_DEBUG
  if( l!=2 ){
    ERROR_REPORT;
    std::cerr << "The vector size must be 2." << std::endl
              << "The vector size you set was " << l << "." << std::endl;
    exit(1);
  }
#endif//CPPL_DEBUG]
  
  array[0] =x;
  array[1] =y;
}

//=============================================================================
/*! drovector_small constructor */
template<CPPL_INT l>
inline drovector_small<l>::drovector_small(const double& x, const double& y, const double& z)
{CPPL_VERBOSE_REPORT;
#ifdef  CPPL_DEBUG
  if( l!=3 ){
    ERROR_REPORT;
    std::cerr << "The vector size must be 3." << std::endl
              << "The vector size you set was " << l << "." << std::endl;
    exit(1);
  }
#endif//CPPL_DEBUG
  
  array[0] =x;
  array[1] =y;
  array[2] =z;
}

//=============================================================================
/*! drovector_small constructor */
template<CPPL_INT l>
inline drovector_small<l>::drovector_small(const double& x, const double& y, const double& z, const double& r)
{CPPL_VERBOSE_REPORT;
#ifdef  CPPL_DEBUG
  if( l!=4 ){
    ERROR_REPORT;
    std::cerr << "The vector size must be 4." << std::endl
              << "The vector size you set was " << l << "." << std::endl;
    exit(1);
  }
#endif//CPPL_DEBUG
  
  array[0] =x;
  array[1] =y;
  array[2] =z;
  array[3] =r;
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

//=============================================================================
/*! drovector_small destructor */
template<CPPL_INT l>
inline drovector_small<l>::~drovector_small()
{CPPL_VERBOSE_REPORT;
  ;
}
