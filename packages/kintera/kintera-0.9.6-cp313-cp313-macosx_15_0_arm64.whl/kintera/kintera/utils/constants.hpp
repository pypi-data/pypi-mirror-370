#pragma once

#include <cmath>

// STL includes
#include <algorithm>
#include <cstdlib>
#include <functional>
#include <map>
#include <memory>
#include <set>
#include <string>
#include <vector>

namespace kintera {

// Constant indices, to be aligned with canoe
const int IDN = 0;
const int IPR = 1;
const int IEN = 2;

namespace constants {

const double Pi = 3.14159265358979323846;
const double Sqrt2 = 1.41421356237309504880;

//! Avogadro's Number @f$ N_{\mathrm{A}} @f$ [number/kmol]
const double Avogadro = 6.02214076e26;
//! Boltzmann constant @f$ k @f$ [J/K]
const double Boltzmann = 1.380649e-23;
//! Planck constant @f$ h @f$ [J-s]
const double Planck = 6.62607015e-34;
//! Elementary charge @f$ e @f$ [C]
const double ElectronCharge = 1.602176634e-19;
//! Speed of Light in a vacuum @f$ c @f$ [m/s]
const double lightSpeed = 299792458.0;
//! One atmosphere [Pa]
const double OneAtm = 1.01325e5;
//! One bar [Pa]
const double OneBar = 1.0E5;
//! Electron Mass @f$ m_e @f$ [kg]
const double ElectronMass = 9.1093837015e-31;

//! Fine structure constant @f$ \alpha @f$ []
const double fineStructureConstant = 7.2973525693e-3;

//! Universal Gas Constant @f$ R_u @f$ [J/kmol/K]
const double GasConstant = Avogadro * Boltzmann;
const double logGasConstant = std::log(GasConstant);
//! Universal gas constant in cal/mol/K
const double GasConst_cal_mol_K = GasConstant / 4184.0;
//! Stefan-Boltzmann constant @f$ \sigma @f$ [W/m2/K4]
const double StefanBoltz =
    2.0 * std::pow(Pi, 5) * std::pow(Boltzmann, 4) /
    (15.0 * std::pow(Planck, 3) * lightSpeed * lightSpeed);  // 5.670374419e-8
//! Faraday constant @f$ F @f$ [C/kmol]
const double Faraday = ElectronCharge * Avogadro;
//! Permeability of free space @f$ \mu_0 @f$ [N/A2]
const double permeability_0 = 2 * fineStructureConstant * Planck /
                              (ElectronCharge * ElectronCharge * lightSpeed);
//! Permittivity of free space @f$ \varepsilon_0 @f$ [F/m]
const double epsilon_0 = 1.0 / (lightSpeed * lightSpeed * permeability_0);

//! smallest number to compare to zero.
const double SmallNumber = 1.e-300;
//! largest number to compare to inf.
const double BigNumber = 1.e300;

//! Fairly random number to be used to initialize variables against
//! to see if they are subsequently defined.
const double Undef = -999.1234;

//! Small number to compare differences of mole fractions against.
/*!
 * This number is used for the interconversion of mole fraction and mass
 * fraction quantities when the molecular weight of a species is zero. It's also
 * used for the matrix inversion of transport properties when mole fractions
 * must be positive.
 */
const double Tiny = 1.e-20;

}  // namespace constants

//! Map from string names to doubles. Used for defining species mole/mass
//! fractions, elemental compositions, and reaction stoichiometries.
typedef std::map<std::string, double> Composition;

//! index returned by functions to indicate "no position"
const size_t npos = static_cast<size_t>(-1);

}  // namespace kintera
