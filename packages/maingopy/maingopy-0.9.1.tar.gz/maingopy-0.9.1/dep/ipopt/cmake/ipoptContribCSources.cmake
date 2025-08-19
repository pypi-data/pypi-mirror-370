SET(IPOPT_CONTRIB_C_SOURCES
    ${IPOPT_SRCDIR}/contrib/CGPenalty/IpCGPenaltyCq.cpp
    ${IPOPT_SRCDIR}/contrib/CGPenalty/IpCGPenaltyData.cpp
    ${IPOPT_SRCDIR}/contrib/CGPenalty/IpCGPenaltyLSAcceptor.cpp
    ${IPOPT_SRCDIR}/contrib/CGPenalty/IpCGPenaltyRegOp.cpp
    ${IPOPT_SRCDIR}/contrib/CGPenalty/IpCGPerturbationHandler.cpp
    ${IPOPT_SRCDIR}/contrib/CGPenalty/IpCGSearchDirCalc.cpp
    ${IPOPT_SRCDIR}/contrib/CGPenalty/IpPiecewisePenalty.cpp
    ${IPOPT_SRCDIR}/contrib/LinearSolverLoader/HSLLoader.c
    ${IPOPT_SRCDIR}/contrib/LinearSolverLoader/LibraryHandler.c
    ${IPOPT_SRCDIR}/contrib/LinearSolverLoader/PardisoLoader.c
    
    )
    
SET(IPOPT_CONTRIB_C_HEADER
    ${IPOPT_SRCDIR}/contrib/CGPenalty/IpCGPenaltyCq.hpp
    ${IPOPT_SRCDIR}/contrib/CGPenalty/IpCGPenaltyData.hpp
    ${IPOPT_SRCDIR}/contrib/CGPenalty/IpCGPenaltyLSAcceptor.hpp
    ${IPOPT_SRCDIR}/contrib/CGPenalty/IpCGPenaltyRegOp.hpp
    ${IPOPT_SRCDIR}/contrib/CGPenalty/IpCGPerturbationHandler.hpp
    ${IPOPT_SRCDIR}/contrib/CGPenalty/IpCGSearchDirCalc.hpp
    ${IPOPT_SRCDIR}/contrib/CGPenalty/IpPiecewisePenalty.hpp
    ${IPOPT_SRCDIR}/contrib/LinearSolverLoader/HSLLoader.h
    ${IPOPT_SRCDIR}/contrib/LinearSolverLoader/LibraryHandler.h
    ${IPOPT_SRCDIR}/contrib/LinearSolverLoader/PardisoLoader.h
    )
