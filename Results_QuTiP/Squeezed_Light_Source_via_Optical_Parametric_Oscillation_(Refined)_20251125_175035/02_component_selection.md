# Component Selection Rationale

**Experiment:** Squeezed Light Source via Optical Parametric Oscillation (Refined)

**Timestamp:** 20251125_175035

**Description:** Generates quadrature-squeezed vacuum states using a sub-threshold optical parametric oscillator with impedance-matched cavity, PDH locking, and phase-coherent local oscillator

---

## 1. Seed Laser (1064nm)

Ultra-stable 1064nm laser serving dual purpose: frequency-doubled to create pump AND used directly as LO, ensuring phase coherence and eliminating independent phase noise

## 2. SHG Input Lens

Focuses 1064nm seed into SHG crystal for efficient second-harmonic generation

## 3. SHG Crystal

PPLN crystal for second-harmonic generation (1064nm → 532nm), creating pump that is inherently phase-locked to LO

## 4. SHG Separator

Dichroic mirror separating frequency-doubled 532nm pump from residual 1064nm (which becomes LO)

## 5. Pump Steering Mirror

Directs 532nm pump upward from SHG path to OPO input path

## 6. Pump Turning Mirror

Turns pump beam horizontally toward phase modulator and OPO cavity

## 7. Phase Modulator

EOM at 20MHz provides phase modulation sidebands for Pound-Drever-Hall locking of OPO cavity

## 8. Isolator

Prevents back-reflections from OPO cavity from destabilizing the pump

## 9. HWP1

Rotates pump polarization to match PPLN crystal acceptance for type-0 phase-matching

## 10. Mode-Matching Lens 1

First element of telescope matching pump beam waist to OPO cavity eigenmode

## 11. Mode-Matching Lens 2

Completes mode-matching telescope for optimal pump-cavity coupling

## 12. Pump Injection Mirror

Directs pump upward into OPO cavity through input coupler

## 13. Input Coupler

Piezo-mounted dichroic mirror (R=99.8% @ 1064nm, T=95% @ 532nm) - impedance-matched to cavity losses for optimal squeezing, actuated by PDH servo

## 14. PPLN Crystal

Nonlinear medium for degenerate optical parametric oscillation (532nm → 1064nm + 1064nm), generating squeezed vacuum states

## 15. Curved Mirror M1

High-reflector (R=99.8%) end mirror with 50mm radius of curvature defining stable OPO cavity geometry

## 16. Reflection Monitor

Fast photodiode detecting reflected pump light for PDH error signal generation

## 17. Pump Separator

Dichroic mirror separating residual 532nm pump from 1064nm squeezed output

## 18. Pump Dump

Absorbs waste 532nm light to prevent stray reflections

## 19. Output Mode-Matching Lens 1

First lens matching squeezed beam spatial mode to local oscillator mode at homodyne detector

## 20. Output Mode-Matching Lens 2

Second lens completing mode-matching telescope for optimal homodyne visibility

## 21. Green Filter

Additional dichroic filter (HR@532nm, HT@1064nm) ensuring no residual pump contaminates homodyne detector

## 22. HWP2

Rotates squeezed state quadrature angle relative to LO to select measured quadrature (amplitude or phase)

## 23. Homodyne BS

50:50 beam splitter interfering squeezed vacuum with bright local oscillator for balanced homodyne detection

## 24. LO Steering Mirror 1

Directs residual 1064nm (LO) from SHG separator toward piezo mirror

## 25. LO Piezo Mirror

Piezo-actuated mirror providing fine phase control of LO for homodyne quadrature selection

## 26. LO Steering Mirror 2

Directs LO beam upward to combine with squeezed output at homodyne BS

## 27. Homodyne Detector

Balanced photodetector with 98% quantum efficiency measuring photocurrent difference to extract quadrature noise

## 28. Spectrum Analyzer

RF spectrum analyzer measuring noise power spectral density to verify squeezing below shot-noise level

## 29. PPLN Temperature Controller

Precision controller maintaining PPLN crystal at 50°C ± 0.01°C for stable phase-matching (critical: Δλ ~ 0.1nm/°C)

## 30. PDH Lock Electronics

Servo system generating error signal from reflection monitor and controlling Input Coupler piezo to lock cavity resonance

