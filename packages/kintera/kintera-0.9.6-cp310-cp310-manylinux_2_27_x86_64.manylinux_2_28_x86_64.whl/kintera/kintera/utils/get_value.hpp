#pragma once

// C/C++
#include <map>

namespace kintera {

//! Const accessor for a value in a map.
/*
 * Similar to map.at(key), but returns *default_val* if the key is not
 * found instead of throwing an exception.
 */
template <class T, class U>
const U& get_value(const std::map<T, U>& m, const T& key,
                   const U& default_val) {
  typename std::map<T, U>::const_iterator iter = m.find(key);
  return (iter == m.end()) ? default_val : iter->second;
}

}  // namespace kintera
