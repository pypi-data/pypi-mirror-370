#pragma once

// torch
#include <torch/torch.h>

namespace kintera {

//! \brief Resizes a tensor to the desired shape and options if necessary.
/*!
 *
 * This function checks if the input tensor matches the desired shape and
 * options. If it does, it returns the tensor as is. If not, it creates a new
 * tensor with the specified shape and options.
 *
 * \param tensor The input tensor to check and potentially resize.
 * \param desired_shape The desired shape for the tensor.
 * \param desired_options The desired tensor options (dtype, device, etc.).
 * \return A tensor that matches the desired shape and options.
 */
torch::Tensor check_resize(torch::Tensor tensor, at::IntArrayRef desired_shape,
                           const torch::TensorOptions& desired_options);

}  // namespace kintera
