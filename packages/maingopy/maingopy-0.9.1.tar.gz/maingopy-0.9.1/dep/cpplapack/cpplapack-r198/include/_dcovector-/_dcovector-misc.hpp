//=============================================================================
/*! nullify all the vector data */
inline void _dcovector::nullify() const
{CPPL_VERBOSE_REPORT;
  l=0;
  cap=0;
  array=NULL;
}

//=============================================================================
/*!  destroy all the vector data */
inline void _dcovector::destroy() const
{CPPL_VERBOSE_REPORT;
  delete [] array;
  array=NULL;
}
