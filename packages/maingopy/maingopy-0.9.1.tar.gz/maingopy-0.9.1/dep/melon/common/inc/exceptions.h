/**********************************************************************************
 * Copyright (c) 2020 Process Systems Engineering (AVT.SVT), RWTH Aachen University
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0.
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 *  @file exceptions.h
 *
 *  @brief File declaring the MeLOn exception class.
 *
 **********************************************************************************/

#pragma once

#include <exception>
#include <sstream>
#include <string>
#include <typeinfo>

/**
*  @class MelonException
*  @brief This class defines the exceptions thrown by FeedForwardNet
*
* The class contains different constructors. The first parameter is always the error message.
* Additionally, the constructor can take an exception as second argument.
* If done so, the type of the exception object and its what() will be saved in the error message as well.
*
*/
class MelonException : public std::exception {
private:
	std::string _msg{ "" };			/*!< string holding the exception message */;
	MelonException();
public:
	/**
	*  @brief Constructor used for forwarding
	*
	*  @param[in] arg is a string holding an error message
	*/
	explicit MelonException(const std::string& arg) :
		MelonException(arg, nullptr)
	{
	}

	/**
	*  @brief Constructor used for forwarding
	*
	*  @param[in] arg is a string holding an error message
	*  @param[in] e holds the exception
	*/
	MelonException(const std::string& arg, const std::exception& e) :
		MelonException(arg, &e)
	{
	}

	/**
	*  @brief Constructor used printing a FeedForwardNet Exception
	*
	*  @param[in] arg is a string holding an error message
	*  @param[in] e holds the exception
	*/
	MelonException(const std::string& arg, const std::exception* e)
	{
		std::ostringstream message;
		if (e) {
			if (typeid(*e).name() != typeid(*this).name()) {
				message << "  Original std::exception: " << typeid(*e).name() << ": " << std::endl
					<< "   ";
			}
			message << e->what() << std::endl;
		}
		message << arg;
		_msg = message.str();
	}

	/**
	*  @brief Function to return the error message
	*
	*  @return Error message.
	*/
	const char* what() const noexcept
	{
		return _msg.c_str();
	}

};