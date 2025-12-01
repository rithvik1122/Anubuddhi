# Component Selection Rationale

**Experiment:** Hong-Ou-Mandel Interference Setup

**Timestamp:** 20251124_182846

**Description:** Demonstrates quantum interference of indistinguishable photons at a beam splitter, showing the quantum bunching effect.

---

## 1. Pump Laser

405nm continuous-wave laser provides pump photons for the SPDC process, with sufficient power and narrow linewidth for stable photon pair generation

## 2. PPLN Crystal

Periodically-poled lithium niobate crystal efficiently generates correlated photon pairs at 810nm through type-II SPDC with precise phase matching

## 3. Pump Filter

Dichroic mirror reflects 405nm pump light while transmitting 810nm SPDC photons, eliminating pump contamination from the interference measurement

## 4. PBS

Polarizing beam splitter separates the orthogonally polarized SPDC photon pairs into distinct spatial modes for the two interferometer arms

## 5. Upper Mirror

Directs one photon from the SPDC pair along the upper interferometer arm toward the delay stage

## 6. Lower Mirror

Directs the second photon from the SPDC pair along the lower interferometer arm toward the delay stage

## 7. Upper Delay Stage

Motorized delay stage provides precise optical path length control for the upper arm to achieve temporal overlap

## 8. Lower Delay Stage

Motorized delay stage provides precise optical path length control for the lower arm to achieve temporal overlap

## 9. HWP Upper

Half-wave plate rotates the polarization of the upper arm photon to ensure indistinguishability with the lower arm photon

## 10. HWP Lower

Half-wave plate rotates the polarization of the lower arm photon to ensure indistinguishability with the upper arm photon

## 11. Upper Steering Mirror

Redirects the upper arm photon toward the 50:50 beam splitter for Hong-Ou-Mandel interference

## 12. Lower Steering Mirror

Redirects the lower arm photon toward the 50:50 beam splitter for Hong-Ou-Mandel interference

## 13. 50:50 BS

Non-polarizing 50:50 beam splitter where quantum interference occurs - indistinguishable photons exhibit bunching due to bosonic statistics

## 14. SPAD Detector 1

Single-photon avalanche photodiode detects photons from transmission port of beam splitter with high timing resolution for coincidence measurements

## 15. SPAD Detector 2

Second SPAD detector at reflection port of beam splitter enables coincidence counting to measure the HOM interference visibility

