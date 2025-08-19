//=============================================================================
/*! operator() for const object */
inline double& _dcovector::operator()(const CPPL_INT& i) const
{CPPL_VERBOSE_REPORT;
#ifdef  CPPL_DEBUG
  if( i<0 || l<=i ){
    ERROR_REPORT;
    std::cerr << "The required component is out of the vector size." << std::endl
              << "Your input is (" << i << "), whereas the vector size is " << l << "." << std::endl;
    exit(1);
  }
#endif//CPPL_DEBUG
  
  return array[i];
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

//=============================================================================
inline std::ostream& operator<<(std::ostream& s, const _dcovector& vec)
{CPPL_VERBOSE_REPORT;
  for(CPPL_INT i=0; i<vec.l; i++){
    s << " " << vec.array[i] << std::endl;
  }
  
  vec.destroy();
  return s;
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

//=============================================================================
inline void _dcovector::write(const char *filename) const
{CPPL_VERBOSE_REPORT;
  std::ofstream ofs(filename, std::ios::trunc);
  ofs.setf(std::cout.flags());
  ofs.precision(std::cout.precision());
  ofs.width(std::cout.width());
  ofs.fill(std::cout.fill());
  
  ofs << "#dcovector" << " " << l << std::endl;
  for(CPPL_INT i=0; i<l; i++){
    ofs << operator()(i) << std::endl;
  }
  
  ofs.close();
  destroy();
}
