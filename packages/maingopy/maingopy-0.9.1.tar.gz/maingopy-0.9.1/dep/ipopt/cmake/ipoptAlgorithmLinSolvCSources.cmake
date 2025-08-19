SET(IPOPT_ALGORITHM_LINSOLV_C_SOURCES
   #${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpIterativeWsmpSolverInterface.cpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpLinearSolversRegOp.cpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpMa27TSolverInterface.cpp
#   ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpMa28Partition.c  # causes symbol name clash with real MA28
#   ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpMa28TDependencyDetector.cpp
#   ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpMa57TSolverInterface.cpp
#   ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpMa77SolverInterface.cpp
#   ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpMa86SolverInterface.cpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpMc19TSymScalingMethod.cpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpMumpsSolverInterface.cpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpPardisoSolverInterface.cpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpSlackBasedTSymScalingMethod.cpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpTripletToCSRConverter.cpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpTSymDependencyDetector.cpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpTSymLinearSolver.cpp
#   ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpWsmpSolverInterface.cpp
    )
    
Set(IPOPT_ALGORITHM_LINSOLV_C_HEADER
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/hsl_ma86d.h
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/hsl_mc68i.h
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpGenKKTSolverInterface.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpIterativeWsmpSolverInterface.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpLinearSolversRegOp.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpMa27TSolverInterface.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpMa28TDependencyDetector.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpMa57TSolverInterface.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpMa77SolverInterface.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpMa86SolverInterface.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpMc19TSymScalingMethod.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpMumpsSolverInterface.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpPardisoSolverInterface.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpSlackBasedTSymScalingMethod.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpSparseSymLinearSolverInterface.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpSymLinearSolver.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpTDependencyDetector.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpTripletToCSRConverter.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpTSymDependencyDetector.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpTSymLinearSolver.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpTSymScalingMethod.hpp
    ${IPOPT_SRCDIR}/Algorithm/LinearSolvers/IpWsmpSolverInterface.hpp
    )
