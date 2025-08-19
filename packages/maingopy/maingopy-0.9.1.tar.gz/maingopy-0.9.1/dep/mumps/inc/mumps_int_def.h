/**********************************************************************************
 * Copyright (c) 2019 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 * @file mumps_int_def.h
 *
 * @brief File needed by MUMPS to declare int size.
 *
 **********************************************************************************/

#ifdef INTSIZE64
#define MUMPS_INTSIZE64
#else
#undef MUMPS_INTSIZE64
#endif