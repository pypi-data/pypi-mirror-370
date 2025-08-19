set(MAiNGO_SOURCE_DIR ${PROJECT_SOURCE_DIR}/src)
set(MAiNGO_SRC
    ${MAiNGO_SOURCE_DIR}/bab.cpp
    ${MAiNGO_SOURCE_DIR}/constraint.cpp
    ${MAiNGO_SOURCE_DIR}/decayingProbability.cpp
    ${MAiNGO_SOURCE_DIR}/getTime.cpp
    ${MAiNGO_SOURCE_DIR}/ipoptProblem.cpp
    ${MAiNGO_SOURCE_DIR}/knitroProblem.cpp
    ${MAiNGO_SOURCE_DIR}/lbp.cpp
    ${MAiNGO_SOURCE_DIR}/lbpFactory.cpp
    ${MAiNGO_SOURCE_DIR}/lbpCplex.cpp
    ${MAiNGO_SOURCE_DIR}/lbpGurobi.cpp
    ${MAiNGO_SOURCE_DIR}/lbpClp.cpp
    ${MAiNGO_SOURCE_DIR}/lbpDagObj.cpp
    ${MAiNGO_SOURCE_DIR}/lbpInterval.cpp
    ${MAiNGO_SOURCE_DIR}/lbpLinearizationStrats.cpp
    ${MAiNGO_SOURCE_DIR}/logger.cpp
    ${MAiNGO_SOURCE_DIR}/MAiNGO.cpp
    ${MAiNGO_SOURCE_DIR}/MAiNGOevaluationFunctions.cpp
    ${MAiNGO_SOURCE_DIR}/MAiNGOException.cpp
    ${MAiNGO_SOURCE_DIR}/MAiNGOgetOption.cpp
    ${MAiNGO_SOURCE_DIR}/MAiNGOgetterFunctions.cpp
    ${MAiNGO_SOURCE_DIR}/MAiNGOmodelEpsCon.cpp
    ${MAiNGO_SOURCE_DIR}/MAiNGOprintingFunctions.cpp
    ${MAiNGO_SOURCE_DIR}/MAiNGOreadSettings.cpp
    ${MAiNGO_SOURCE_DIR}/MAiNGOsetOption.cpp
    ${MAiNGO_SOURCE_DIR}/MAiNGOtoOtherLanguage.cpp
    ${MAiNGO_SOURCE_DIR}/MAiNGOwritingFunctions.cpp
    ${MAiNGO_SOURCE_DIR}/pointIsWithinNodeBounds.cpp
    ${MAiNGO_SOURCE_DIR}/outputVariable.cpp
    ${MAiNGO_SOURCE_DIR}/ubp.cpp
    ${MAiNGO_SOURCE_DIR}/ubpClp.cpp
    ${MAiNGO_SOURCE_DIR}/ubpCplex.cpp
    ${MAiNGO_SOURCE_DIR}/ubpGurobi.cpp
    ${MAiNGO_SOURCE_DIR}/ubpFactory.cpp
    ${MAiNGO_SOURCE_DIR}/ubpIpopt.cpp
    ${MAiNGO_SOURCE_DIR}/ubpKnitro.cpp
    ${MAiNGO_SOURCE_DIR}/ubpNLopt.cpp
)

if(MAiNGO_build_parser OR MAiNGO_build_shared_c_api)
    set(PARSER_SRC
        ${MAiNGO_SOURCE_DIR}/aleModel.cpp
        ${MAiNGO_SOURCE_DIR}/programParser.cpp
    )
endif()

if(MAiNGO_use_mpi)
    set(MAiNGO_SRC ${MAiNGO_SRC}
        ${MAiNGO_SOURCE_DIR}/babMpi.cpp
    )
endif()
# Add subindomain lower bound solver
if(HAVE_CUDA_TOOLKIT)
    # If use CUDA, compile the .cu source file (GPU-parallel version)
	set(MAiNGO_SRC ${MAiNGO_SRC}
		${MAiNGO_SOURCE_DIR}/lbpSubinterval.cu
	)
else()
	# Otherwise, compile the .cpp source file (CPU-serial version)
    set(MAiNGO_SRC ${MAiNGO_SRC}
		${MAiNGO_SOURCE_DIR}/lbpSubinterval.cpp
	)
endif()

if(MAiNGO_build_test)
    set(MAiNGO_UNIT_TEST_SRC
        ${PROJECT_SOURCE_DIR}/tests/unitTests/testBab.cpp
        ${PROJECT_SOURCE_DIR}/tests/unitTests/testConstraint.cpp
        ${PROJECT_SOURCE_DIR}/tests/unitTests/testDecayingProbability.cpp
        ${PROJECT_SOURCE_DIR}/tests/unitTests/testLogger.cpp
        ${PROJECT_SOURCE_DIR}/tests/unitTests/testMAiNGO.cpp
        ${PROJECT_SOURCE_DIR}/tests/unitTests/testMAiNGOException.cpp
        ${PROJECT_SOURCE_DIR}/tests/unitTests/testMAiNGOevaluationFunctions.cpp
        ${PROJECT_SOURCE_DIR}/tests/unitTests/testMAiNGOgetterFunctions.cpp
        ${PROJECT_SOURCE_DIR}/tests/unitTests/testMAiNGOmodelEpsCon.cpp
        ${PROJECT_SOURCE_DIR}/tests/unitTests/testMAiNGOprintingFunctions.cpp
        ${PROJECT_SOURCE_DIR}/tests/unitTests/testMAiNGOreadSettings.cpp
        ${PROJECT_SOURCE_DIR}/tests/unitTests/testMAiNGOsetAndGetOption.cpp
        ${PROJECT_SOURCE_DIR}/tests/unitTests/testMAiNGOtoOtherLanguage.cpp
        ${PROJECT_SOURCE_DIR}/tests/unitTests/testMAiNGOwritingFunctions.cpp
        ${PROJECT_SOURCE_DIR}/tests/unitTests/testOutputVariable.cpp
        ${PROJECT_SOURCE_DIR}/tests/unitTests/testPointIsWithinNodeBounds.cpp
    )
endif()