// kintera
#include "check_resize.hpp"

namespace kintera {

bool if_options_match(const torch::TensorOptions& a,
                      const torch::TensorOptions& b) {
  return a.dtype() == b.dtype() && a.device() == b.device() &&
         a.layout() == b.layout() && a.requires_grad() == b.requires_grad() &&
         a.pinned_memory() == b.pinned_memory();
}

torch::Tensor check_resize(torch::Tensor tensor, at::IntArrayRef desired_shape,
                           const torch::TensorOptions& desired_options) {
  // Check shape and options
  bool shape_matches = tensor.sizes().equals(desired_shape);
  bool options_match = if_options_match(tensor.options(), desired_options);

  if (shape_matches && options_match) {
    return tensor;  // No-op
  }

  // Resize (create new tensor with correct shape and options)
  return torch::empty(desired_shape, desired_options);
}

}  // namespace kintera
