# Component Selection Rationale

**Experiment:** Bell State Generator using SPDC

**Timestamp:** 20251123_132334

**Description:** Generates polarization-entangled photon pairs in Bell states through type-II spontaneous parametric down-conversion with proper pump blocking and phase control.

---

## 1. Pump Laser

405nm CW laser provides pump photons with sufficient energy to generate 810nm photon pairs through SPDC while maintaining good beam quality

## 2. Focusing Lens

Focuses pump beam into BBO crystal to increase conversion efficiency and optimize spatial mode matching for SPDC process

## 3. BBO Crystal

Type-II Beta Barium Borate crystal generates polarization-entangled photon pairs where signal and idler have orthogonal polarizations

## 4. Pump Beam Dump

Absorbs residual 405nm pump light to prevent interference with down-converted photon detection and reduce background

## 5. 810nm Filter

Bandpass filter blocks any remaining pump light and selects only the 810nm down-converted photons for clean detection

## 6. Collection Lens

Collects and collimates the down-converted photon pairs emerging from crystal with proper numerical aperture matching

## 7. Phase Control HWP

Half-wave plate at 22.5° rotation controls the relative phase between |HV⟩ and |VH⟩ components, enabling Bell state selection

## 8. Polarizing PBS

Separates the orthogonally polarized entangled photons into two distinct spatial paths for independent polarization analysis

## 9. Mirror A

Redirects H-polarized photons from PBS reflection port to upper detector arm with proper 45° angle for beam steering

## 10. Mirror B

Redirects V-polarized photons from PBS transmission port to lower detector arm maintaining beam alignment

## 11. Polarizer A

Enables polarization analysis of photons in upper arm - rotation allows measurement in different polarization bases

## 12. Polarizer B

Enables polarization analysis of photons in lower arm - rotation enables Bell inequality tests and state tomography

## 13. SPAD A

Single-photon avalanche photodiode with timing resolution for coincidence measurements and high quantum efficiency

## 14. SPAD B

Second SPAD detector enables coincidence counting necessary for Bell state verification and entanglement characterization

