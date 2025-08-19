/**********************************************************************************
 * Copyright (c) 2019 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/


/**
*	@namespace mc
*	@brief namespace holding forward declaration of McCormick objects. For more info refer to the open-source library MC++
*/
namespace mc {


class FFVar;                                                          /*!< defined in ffunc.hpp of MC++  */
class FFGraph;                                                        /*!< defined in ffunc.hpp of MC++  */
struct FFSubgraph;                                                    /*!< defined in ffunc.hpp of MC++  */
class FFOp;                                                           /*!< defined in mcop.hpp of MC++   */
double machprec();                                                    /*!< defined in mcfunc.hpp of MC++ */
bool isequal(const double, const double, const double, const double); /*!< defined in mcfunc.hpp of MC++ */


}    // end namespace mc
