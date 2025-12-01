# Component Selection Rationale

**Experiment:** 4-Photon Boson Sampling Experiment

**Timestamp:** 20251125_185800

**Description:** Demonstrates quantum computational advantage by interfering 4 indistinguishable photons through a 4-mode linear optical network and measuring output statistics

---

## 1. Pump Laser 1

405nm CW laser pumps first SPDC source to generate photon pairs at 810nm through frequency down-conversion

## 2. Pump Laser 2

Second independent 405nm pump laser for second SPDC source to generate additional photon pairs

## 3. SPDC Crystal 1

PPLN crystal with type-0 phase matching generates spectrally pure heralded single photons via spontaneous parametric down-conversion

## 4. SPDC Crystal 2

Second PPLN crystal produces additional photon pairs, enabling 4-photon input state when heralded

## 5. Filter 1

Narrowband interference filter at 810nm blocks pump light and selects desired SPDC wavelength with 3nm bandwidth

## 6. Filter 2

Second narrowband filter ensures spectral indistinguishability between photons from different sources

## 7. Fiber Coupler 1

Single-mode fiber coupling ensures spatial mode matching and temporal indistinguishability of photons

## 8. Fiber Coupler 2

Second fiber coupler for photons from second source, maintaining mode quality

## 9. Input BS 1

Splits first photon pair into modes 1 and 2 to populate upper two input modes of the 4-mode network

## 10. Input BS 2

Splits second photon pair into modes 3 and 4 to populate lower two input modes of the 4-mode network

## 11. Phase 1

First layer phase shifter for mode 1 provides 0-2π phase control for implementing arbitrary unitary

## 12. Phase 2

First layer phase shifter for mode 2 enables independent phase control

## 13. Phase 3

First layer phase shifter for mode 3 provides phase tuning capability

## 14. Phase 4

First layer phase shifter for mode 4 completes first layer phase control across all modes

## 15. Network BS 1-2

Couples modes 1 and 2 with 33% transmittance to create interference between upper modes

## 16. Network BS 2-3

Couples modes 2 and 3 with 67% transmittance for central mode interference

## 17. Network BS 3-4

Couples modes 3 and 4 with 50:50 splitting for lower mode interference

## 18. Phase 5

Second layer phase shifter for mode 1 after first beam splitter layer

## 19. Phase 6

Second layer phase shifter for mode 2 provides additional phase control

## 20. Phase 7

Second layer phase shifter for mode 3 enables complex unitary transformations

## 21. Phase 8

Second layer phase shifter for mode 4 completes two-layer phase control

## 22. Output BS 1-2

Final layer 50:50 beam splitter couples modes 1 and 2 for output interference

## 23. Output BS 2-3

Final layer 50:50 beam splitter couples modes 2 and 3 for output interference

## 24. Output BS 3-4

Final layer 50:50 beam splitter couples modes 3 and 4 for output interference

## 25. SNSPD 1

Superconducting nanowire single-photon detector for mode 1 with 85% efficiency and 50ps timing resolution

## 26. SNSPD 2

High-efficiency SNSPD for mode 2 enables low-loss photon detection

## 27. SNSPD 3

SNSPD for mode 3 with minimal dark counts for high-fidelity measurements

## 28. SNSPD 4

SNSPD for mode 4 with excellent timing resolution for coincidence detection

## 29. 4-Channel Coincidence Logic

Time-tagging electronics process all detector signals to identify 4-fold coincidence events within 2ns window and construct output probability distribution for comparison with permanent calculation

