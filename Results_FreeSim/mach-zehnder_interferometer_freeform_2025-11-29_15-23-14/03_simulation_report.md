# Simulation Report: Mach-Zehnder Interferometer

## Overall Assessment
**Quality Rating:** 6/10 | **Verdict:** FAIR

---

## Simulation Output

### Console Output
```
============================================================
MACH-ZEHNDER INTERFEROMETER SIMULATION
============================================================

Experimental Parameters:
  Wavelength: 632.8 nm
  Laser Power: 5.0 mW
  Linewidth: 1 kHz
  Mirror Reflectivity: 99.0%
  Detector Efficiency: 95.0%

============================================================
INTERFERENCE PATTERN ANALYSIS
============================================================

Detector 1 (Transmitted Port):
  Maximum Intensity: 0.931095
  Minimum Intensity: 0.000058
  Visibility: 0.9999 (99.99%)
  Intensity at φ=0: 0.931095
  Intensity at φ=π: 0.000000

Detector 2 (Reflected Port):
  Maximum Intensity: 0.931037
  Minimum Intensity: 0.000000
  Visibility: 1.0000 (100.00%)
  Intensity at φ=0: 0.000000
  Intensity at φ=π: 0.931095

============================================================
COMPLEMENTARITY CHECK
============================================================

Total intensity (averaged): 0.931095
Expected total (with losses): 0.912566
Energy conservation error: 0.000%

============================================================
THEORETICAL COMPARISON
============================================================

Detector 1 vs cos²(φ/2) prediction:
  RMS Error: 0.01139370
  Relative Error: 2.4352%

Detector 2 vs sin²(φ/2) prediction:
  RMS Error: 0.01131812
  Relative Error: 2.4434%

============================================================
WAVE-PARTICLE DUALITY DEMONSTRATION
============================================================

High visibility (100.0%) confirms wave nature:
  - Coherent superposition of paths
  - Phase-dependent interference
  - Complementary output ports

Perfect anti-correlation between detectors:
  - When D1 is bright, D2 is dark (and vice versa)
  - Demonstrates which-path information erasure

Phase at D1 maximum: 0.0000 rad (0.0°)
Phase at D2 maximum: 3.1258 rad (179.1°)
Phase difference: 3.1258 rad (179.1°)

============================================================
SIMULATION COMPLETE
============================================================
```

---

## Physics Analysis

### Physics Correctness
The beam splitter transformation is correctly implemented with proper i phase shift for reflection. The interference pattern qualitatively matches expected cos²(φ/2) and sin²(φ/2) behavior. However, there's a critical error: the expected total intensity calculation doesn't match the simulated values (0.9126 expected vs 0.9311 observed, ~2% discrepancy). The theoretical comparison shows 2.4% RMS error, which is too high for a simulation that should be exact. The phase convention and superposition are correct, but the normalization and loss accounting appear inconsistent.

### Implementation Quality
Code is well-structured with clear functions and good documentation. The beam splitter transform properly implements unitary operation. However, there's an inconsistency in how losses are tracked and normalized. The simulation doesn't properly account for where the 'missing' intensity goes - the expected_total uses mirror_loss_factor = reflectivity^4, but the actual simulation applies losses differently at each component. No error handling for edge cases. The code is readable but the loss accounting logic needs debugging.

### Results Validity
Visibility values near 100% are physically reasonable for ideal coherent sources. The complementary behavior of detectors is correct (when D1 bright, D2 dark). Phase relationship showing π phase difference between detector maxima is correct. However, the energy conservation check is misleading - it shows 0.000% error in the ratio, but the absolute values don't match theory. The total intensity should be constant across all phases (energy conservation), and it is (std/mean ~ 0%), but the value doesn't match the theoretical prediction accounting for losses. This suggests either the loss model or normalization is incorrect.

### Key Findings
- Beam splitter unitary transformation correctly implemented with i phase for reflection
- Interference visibility reaches 99.99-100%, demonstrating proper coherent superposition
- Complementary outputs show correct π phase relationship between detector maxima
- Energy is conserved across phase scans (constant total intensity)
- Pattern qualitatively matches cos²(φ/2) and sin²(φ/2) as expected

### Limitations
- 2.4% RMS error between simulation and theory indicates normalization/loss accounting bug
- Expected total intensity (0.9126) doesn't match observed (0.9311) - inconsistent loss model
- No modeling of decoherence, finite coherence length, or beam alignment errors
- Detector efficiency applied as simple multiplicative factor without shot noise
- No path length difference specified - phase shifter treated as abstract parameter
- Missing spatial mode structure - treats beams as scalar amplitudes only

### Recommendations for Improvement
- Debug the loss accounting - trace through where each factor of reflectivity is applied
- Add explicit path length difference and relate phase to physical displacement
- Include shot noise and photon statistics for realistic detector modeling
- Consider adding imperfect beam splitter ratios and alignment errors
- Visualize the interference patterns graphically for better physical insight

---

## Design Alignment

This simulation was designed to model:
> A coherent laser beam enters the first 50:50 beam splitter (BS1) which creates a quantum superposition |ψ⟩ = (|upper⟩ + i|lower⟩)/√2. The two paths traverse different optical path lengths, with the upper arm containing a tunable phase shifter that introduces a relative phase φ. At the second beam splitter (BS2), the paths recombine and interfere, producing complementary intensity patterns at the two output ports following I₁ ∝ cos²(φ/2) and I₂ ∝ sin²(φ/2). This demonstrates quantum interference and the wave nature of light, with visibility approaching 100% for perfect coherence.

The simulation partially captures the intended quantum physics.

---

*Report generated by Anubuddhi Free-Form Simulation System*
