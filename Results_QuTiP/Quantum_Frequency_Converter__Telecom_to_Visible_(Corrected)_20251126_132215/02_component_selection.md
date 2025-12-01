# Component Selection Rationale

**Experiment:** Quantum Frequency Converter: Telecom to Visible (Corrected)

**Timestamp:** 20251126_132215

**Description:** Converts single photons from telecom wavelength (1550nm) to visible wavelength (600.4nm) via sum-frequency generation while preserving quantum properties

---

## 1. Telecom Photon Source

Generates heralded single photons at 1550nm, the standard telecom wavelength for quantum communication applications

## 2. Fiber Input Coupler

Couples single photons from fiber into free-space optics with high efficiency (85%) while maintaining single-mode operation

## 3. Telecom Collimator

Collimates the telecom beam to 2mm diameter for optimal mode-matching in the nonlinear crystal

## 4. Signal Focusing Lens

Focuses the 1550nm signal beam into the PPLN crystal to maximize nonlinear interaction strength

## 5. Pump Laser

Provides strong 980nm classical pump field (500mW) required for efficient sum-frequency generation without adding excessive noise

## 6. Pump Focusing Lens

Focuses pump beam to match the signal beam waist in the crystal for optimal spatial mode overlap

## 7. Dichroic Combiner

Combines the 1550nm signal and 980nm pump beams collinearly by reflecting 980nm and transmitting 1550nm

## 8. PPLN Crystal

Periodically-poled lithium niobate crystal with 19.2μm poling period provides quasi-phase-matched SFG for 1550nm+980nm→600.4nm conversion (corrected to satisfy energy conservation)

## 9. Output Collimation Lens

Recollimates the output beams after the crystal for efficient separation and filtering

## 10. Dichroic Separator

Separates the converted 600.4nm photons from residual pump and unconverted signal by reflecting visible light upward

## 11. Pump Beam Dump

Safely absorbs the high-power residual pump and any unconverted telecom photons to prevent detector saturation

## 12. Bandpass Filter

Narrow 10nm bandpass filter centered at 600nm with OD6 rejection eliminates any remaining pump or signal photons

## 13. Coupling Lens

Focuses the converted 600.4nm photons into single-mode fiber for delivery to detector

## 14. Visible Fiber Coupler

Couples visible photons into single-mode fiber with 75% efficiency while providing spatial filtering

## 15. Silicon APD

Silicon avalanche photodiode provides 75% detection efficiency at 600nm with low dark counts and 350ps timing resolution for single-photon detection

