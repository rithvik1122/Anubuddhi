# Component Selection Rationale

**Experiment:** Franson Interferometer for Time-Bin Entanglement

**Timestamp:** 20251125_161034

**Description:** Demonstrates energy-time entanglement using unbalanced Mach-Zehnder interferometers in both photon paths with time-bin encoded states

---

## 1. Pump Laser

405nm CW pump laser for continuous SPDC generation with moderate linewidth to create energy-time entangled photon pairs

## 2. PPLN Crystal

Periodically-poled lithium niobate crystal for efficient Type-II SPDC, generating orthogonally polarized signal and idler photons at 810nm with energy-time entanglement

## 3. PBS Separator

Polarizing beam splitter separates Type-II SPDC signal (H-polarized) and idler (V-polarized) photons into different spatial modes for independent interferometers

## 4. Mirror to Signal Arm

Redirects H-polarized signal photons upward to the signal interferometer path

## 5. BS1 Signal

First 50:50 beam splitter in signal arm creates superposition of short and long paths (time bins)

## 6. BS1 Idler

First 50:50 beam splitter in idler arm creates superposition of short and long paths (time bins)

## 7. Mirror S-Short

Reflects signal photon in short arm of signal interferometer

## 8. Mirror S-Long-1

First mirror directing signal photon through extended long arm for time delay

## 9. Mirror S-Long-2

Second mirror in long arm returning signal photon to recombination beam splitter

## 10. Mirror I-Short

Reflects idler photon in short arm of idler interferometer

## 11. Mirror I-Long-1

First mirror directing idler photon through extended long arm for time delay

## 12. Mirror I-Long-2

Second mirror in long arm returning idler photon to recombination beam splitter

## 13. BS2 Signal

Second 50:50 beam splitter recombines short and long paths in signal interferometer

## 14. BS2 Idler

Second 50:50 beam splitter recombines short and long paths in idler interferometer

## 15. Phase Shifter Signal

Piezo-mounted mirror or phase modulator to scan relative phase φ_S between signal interferometer arms

## 16. Phase Shifter Idler

Piezo-mounted mirror or phase modulator to scan relative phase φ_I between idler interferometer arms

## 17. Filter Signal

Narrow-band interference filter (3nm bandwidth) increases coherence time to exceed path delay, making early/late emission times indistinguishable

## 18. Filter Idler

Narrow-band interference filter (3nm bandwidth) increases coherence time to exceed path delay, making early/late emission times indistinguishable

## 19. SPAD Signal

Single-photon avalanche photodiode with sub-nanosecond timing resolution for detecting signal photons and providing electrical timing signals

## 20. SPAD Idler

Single-photon avalanche photodiode with sub-nanosecond timing resolution for detecting idler photons and providing electrical timing signals

## 21. Coincidence Counter

Time-tagging electronics receives electrical signals from both SPADs to measure coincidence counts as function of phase settings, revealing two-photon interference pattern characteristic of energy-time entanglement

