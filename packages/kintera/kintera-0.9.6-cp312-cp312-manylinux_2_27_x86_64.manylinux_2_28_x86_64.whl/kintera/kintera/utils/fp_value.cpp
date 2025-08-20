// C/++
#include <sstream>

// torch
#include <torch/torch.h>

// fmt
#include <fmt/format.h>

// kintera
#include "fp_value.hpp"
#include "trim_copy.hpp"

namespace kintera {

double fp_value(const std::string& val) {
  double rval;
  std::stringstream ss(val);
  ss.imbue(std::locale("C"));
  ss >> rval;
  return rval;
}

double fp_value_check(const std::string& s) {
  std::istringstream ss(s);
  double value;
  ss >> value;
  if (ss.fail()) {
    throw std::runtime_error("Error parsing floating point value");
  }
  return value;
}

}  // namespace kintera
