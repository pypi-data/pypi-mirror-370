#pragma once

// C/C++
#include <string>
#include <vector>

// torch
#include <torch/torch.h>

// kintera
#include <kintera/reaction.hpp>

namespace kintera {

// The matrix has dimensions (number of reactions × number of species).
torch::Tensor generate_stoichiometry_matrix(
    const std::vector<Reaction>& reactions,
    const std::vector<std::string>& species);

}  // namespace kintera
