/**********************************************************************************
 * Copyright (c) 2023 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 **********************************************************************************/

#pragma once

#include "util/visitor_utils.hpp"
#include <string>
#include <map>

namespace ale {

	namespace helper {

		/*
		structure used to rename parameters in an expression
		*/

		struct rename_parameters_visitor {

			rename_parameters_visitor(std::map<std::string, std::string> names) : names(names) {}
			std::map<std::string, std::string> names;

			template <typename TType>
			void operator()(value_node<TType>* node) {
				traverse_children(*this, node);
			}

			template <typename TType>
			void operator()(parameter_node<TType>* node) {
				if (names.count(node->name)) {
					node->name = names[node->name];
				}
			}

		};

	}

	/*
	subs keys (old names) with values (new names) in expression
	*/
	template <typename TType>
	void rename_parameters(expression<TType>& expr, std::map<std::string, std::string> names) {
		call_visitor(helper::rename_parameters_visitor(names), expr);
	}

	/*
	subs keys (old names) with values (new names) of arguments of function_symbol
	*/
	template <typename TType>
	void rename_arguments(function_symbol<TType>* sym, std::map<std::string, std::string> names) {
		for (auto it = sym->arg_names.begin(); it != sym->arg_names.end(); ++it) {
			if (names.count(*it)) {
				*it = names[*it];
			}
		}
	}

}
