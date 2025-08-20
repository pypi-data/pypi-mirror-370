#pragma once

// torch
#include <torch/torch.h>

namespace kintera {

//! Compute species rate of change
/*!
 * \param stoich stoichiometry matrix, shape (nreaction, nspecies)
 * \param kinetic_rate kinetics rate of reactions [kmol/m^3/s],
 *        shape (ncol, nlyr, nreaction)
 */
torch::Tensor species_rate(torch::Tensor kinetic_rate, torch::Tensor stoich) {
  int nreaction = stoich.size(0);
  int nspecies = stoich.size(1);
  return kinetic_rate.matmul(stoich.view({1, 1, nreaction, nspecies}));
}

}  // namespace kintera
