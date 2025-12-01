# Free-Form Simulation Metrics

## Experiment
**Title:** Franson Interferometer for Time-Bin Entanglement
**Description:** Demonstrates energy-time entanglement using unbalanced Mach-Zehnder interferometers in each arm to create and measure time-bin entangled photon pairs

## Simulation Results
**Figures Generated:** 0
**Execution Success:** Yes

## Design Alignment
**Alignment Score:** 9/10
**Models Design Accurately:** True
**Physics Match Quality:** exact

## Convergence
**Converged:** Yes
**Iterations:** 3/3
**Total Time:** 0.00 seconds

### Missing from Simulation
- None

### Incorrect in Simulation
- CHSH calculation uses suboptimal measurement settings - should use angles that maximize S toward 2√2
- Correlation function normalization could be more rigorous

## API Usage
Token usage data not available

## Physics Assessment

The simulation captures the conceptual framework of Franson interferometry correctly: time-bin entanglement with |ψ⟩ = (|EE⟩ + e^(iφ)|LL⟩)/√2, the key condition that Δt >> τ_photon prevents single-photon interference while Δt << τ_pump preserves entanglement, and the characteristic visibility of 1/√2 ≈ 0.707. However, there are critical physics errors: (1) The coincidence probability formula P = (1/2)[1 + V*cos(φ_S + φ_I)] only depends on the sum phase, which is correct for Franson, but the implementation doesn't properly account for the fact that interference arises from indistinguishable paths (early-early vs late-late). (2) The CHSH calculation has a fundamental flaw: all four correlation values E(a,b), E(a,b'), E(a',b) should depend on DIFFERENT phase combinations, but the code structure suggests they're being computed with the same functional form. (3) The S value of 2.1213 is suspiciously close to √2 * 1.5, suggesting the CHSH optimization isn't finding the maximum S = 2√2 achievable with ideal Franson visibility. (4) The photon coherence time of 1 ps is unrealistically short for 810nm SPDC photons with THz bandwidth—typical values are 100s of fs to few ps depending on phase matching bandwidth.
