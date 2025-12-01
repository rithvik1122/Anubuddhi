# Component Selection Rationale

**Experiment:** Hyperentangled Photon Source with Polarization and Time-Bin Entanglement

**Timestamp:** 20251126_112153

**Description:** Generates photon pairs entangled in both polarization and time-bin degrees of freedom using Type-II SPDC with independent Mach-Zehnder interferometers for each photon

---

## 1. 405nm Pump Laser

Provides 405nm pump photons to drive Type-II SPDC in the BBO crystal, with sufficient power (200mW) for measurable pair generation rates

## 2. Pump Focusing Lens

Focuses pump beam into the BBO crystal to increase intensity and enhance SPDC efficiency while maintaining phase-matching conditions

## 3. Type-II BBO Crystal

Generates polarization-entangled photon pairs via Type-II SPDC where signal and idler have orthogonal polarizations (H and V), creating the initial polarization entanglement |HV⟩ + |VH⟩

## 4. Collection Lens

Collects down-converted photon pairs from the crystal cone overlap region and collimates them for subsequent optics

## 5. 810nm Bandpass Filter

Blocks residual 405nm pump light while transmitting 810nm down-converted photons with high optical depth (OD=6) for clean signal

## 6. PBS Separator

Spatially separates H-polarized and V-polarized photons into two distinct paths, enabling independent time-bin encoding for each photon

## 7. H-Photon Steering Mirror

Redirects H-polarized photons from PBS output upward into the H-photon Mach-Zehnder interferometer

## 8. H-Path BS1

First beam splitter of H-photon MZ interferometer, creating superposition of short (direct) and long (upper loop) paths for time-bin encoding

## 9. H-Upper Mirror 1

First mirror in long path of H-photon MZ, directing light upward to create path length difference

## 10. H-Upper Mirror 2

Second mirror in long path, extending the optical delay for time-bin separation

## 11. H-Upper Mirror 3

Third mirror completing the long path and directing light back to recombination beam splitter

## 12. H-Lower Mirror 1

Single mirror defining the short (reference) path in H-photon MZ interferometer

## 13. H-Path BS2

Recombination beam splitter for H-photon MZ, creating coherent superposition of early and late time bins

## 14. PBS Output A

Analyzes polarization state of H-path photon after time-bin encoding, separating H and V components for detection

## 15. Detector A-H

SPAD with 50ps timing resolution to measure H-polarized photons and resolve time-bin arrival statistics

## 16. Detector A-V

SPAD measuring V-polarized component from H-path, enabling polarization analysis with high temporal resolution

## 17. V-Photon Steering Mirror 1

First steering mirror redirecting V-polarized photons from PBS toward V-photon interferometer

## 18. V-Photon Steering Mirror 2

Second steering mirror directing V-photons downward into their dedicated MZ interferometer

## 19. V-Path BS1

First beam splitter of V-photon MZ interferometer, creating time-bin superposition independently from H-photon

## 20. V-Upper Mirror 1

Mirror defining short path in V-photon MZ interferometer

## 21. V-Lower Mirror 1

First mirror in long path of V-photon MZ, creating path length difference for time-bin encoding

## 22. V-Lower Mirror 2

Second mirror extending the long path to match time-bin separation with H-photon interferometer

## 23. V-Lower Mirror 3

Third mirror completing long path and directing light to recombination beam splitter

## 24. V-Path BS2

Recombination beam splitter for V-photon MZ, creating coherent time-bin superposition

## 25. PBS Output B

Analyzes polarization of V-path photon after time-bin encoding, enabling polarization correlation measurements

## 26. Detector B-H

SPAD measuring H-polarized component from V-path with 50ps timing resolution for time-bin analysis

## 27. Detector B-V

SPAD measuring V-polarized photons from V-path, completing the four-detector configuration for hyperentanglement verification

## 28. 4-Fold Coincidence Counter

Electronic unit processing all four SPAD outputs to identify coincidence events, measuring correlations in both polarization (H/V analysis via PBS) and time-bin (arrival time statistics) degrees of freedom to verify hyperentanglement

