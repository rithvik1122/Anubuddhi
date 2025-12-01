# Component Selection Rationale

**Experiment:** Hong-Ou-Mandel Interference Experiment

**Timestamp:** 20251122_160227

**Description:** Demonstrates quantum interference between indistinguishable photons at a beam splitter, showing photon bunching.

---

## 1. Pump Laser

405nm continuous-wave laser provides pump photons for the SPDC process to generate correlated photon pairs

## 2. PPLN Crystal

Periodically-poled lithium niobate crystal enables efficient type-I SPDC to create photon pairs at 810nm with identical polarizations for natural indistinguishability

## 3. Mirror 1

Directs one photon from the pair to the upper arm of the interferometer at 315° angle to achieve proper beam steering

## 4. Mirror 2

Directs the other photon from the pair to the lower arm of the interferometer at 45° angle for symmetric path separation

## 5. Delay Stage

Provides variable optical delay to control the relative arrival time of photons at the beam splitter for temporal matching

## 6. Bandpass Filter 1

Narrows spectral bandwidth of photons in upper arm to improve indistinguishability by reducing frequency distinguishability

## 7. Bandpass Filter 2

Matches the spectral filtering in the lower arm to ensure symmetric conditions and equal spectral profiles

## 8. Mirror 3

Redirects upper arm photons toward the beam splitter at 225° angle for proper alignment

## 9. Mirror 4

Steers lower arm photons toward the beam splitter at 315° angle to achieve convergent paths

## 10. 50:50 BS

The central component where Hong-Ou-Mandel interference occurs - indistinguishable photons interfere destructively for coincidence detection

## 11. SPAD 1

Single-photon avalanche photodiode detects photons from the reflection port of the beam splitter for coincidence measurements

## 12. SPAD 2

Second SPAD detector for the transmission port enables coincidence counting to measure the HOM dip

