#pragma once

namespace kintera {

/**
 * \brief Read the cross-section data from VULCAN format files
 *
 * \param branches Composition of the photodissociation products (no
 * photoabsorption branch).
 *
 * \param files filenames.
 * There are two files for each photolysis reaction. The first one is for
 * cross-section data and the second one for the branch ratios.
 *
 * \return a pair of vectors containing the wavelength (m) and cross section
 * data (m^2)
 */
std::pair<torch::Tensor, torch::Tensor> load_xsection_vulcan(
    std::vector<std::string> const& files,
    std::vector<Composition> const& branches);

/**
 * Read the cross-section data from KINETICS7 format files
 */

std::pair<torch::Tensor, torch::Tensor> load_xsection_kinetics7(
    std::vector<std::string> const& files,
    std::vector<Composition> const& branches);

}  // namespace kintera
