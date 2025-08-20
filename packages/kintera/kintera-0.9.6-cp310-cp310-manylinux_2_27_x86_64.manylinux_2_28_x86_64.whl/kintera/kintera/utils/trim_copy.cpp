// C/C++
#include <algorithm>
#include <cctype>
#include <iostream>
#include <string>

namespace kintera {

std::string trim_copy(const std::string& str) {
  // Find first non-whitespace character
  auto start = std::find_if(str.begin(), str.end(),
                            [](unsigned char ch) { return !std::isspace(ch); });

  // Find last non-whitespace character
  auto end = std::find_if(str.rbegin(), str.rend(), [](unsigned char ch) {
               return !std::isspace(ch);
             }).base();

  // Ensure valid range before constructing a new string
  return (start < end) ? std::string(start, end) : std::string();
}

}  // namespace kintera
