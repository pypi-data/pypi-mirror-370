#pragma once

// C/C++
#include <string>

namespace kintera {

//! Convert a string to a double
double fp_value(const std::string& val);

//! Convert a string to a double, checking for validity
double fp_value_check(const std::string& val);

}  // namespace kintera
