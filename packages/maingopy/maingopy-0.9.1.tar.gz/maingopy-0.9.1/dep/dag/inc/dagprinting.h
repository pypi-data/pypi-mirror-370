#ifndef DAGPRINTING_H
#define DAGPRINTING_H

#pragma once

#include "dag.h"
#include "baseoperation.h"

namespace SVT_DAG {

	void print(const IndependentDagVar& var);
	void print(const DependentDagVar& var);
	void print(const ConstantDagVar& var);

	void print(const Dag& dag);

}

#endif // DAGPRINTING_H