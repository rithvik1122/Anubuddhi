# Simulation Report: Electromagnetically Induced Transparency (EIT) in Warm Rb-87 Vapor

## Overall Assessment
**Quality Rating:** 3/10 | **Verdict:** POOR

---

## Simulation Output

### Console Output
```
=== EIT Simulation for Rb-87 Vapor ===

Laser Parameters:
Probe power: 0.50 mW
Coupling power: 50.00 mW
Probe Rabi frequency: 31.36 MHz
Coupling Rabi frequency: 313.57 MHz
Natural linewidth: 6.00 MHz

Doppler broadening:
Thermal velocity: 252.34 m/s
Doppler width (FWHM): 323.52 MHz

Vapor Cell Parameters:
Temperature: 60.0 °C
Cell length: 75.0 mm
Atomic density: 2.00e+16 atoms/m^3
Effective cross-section: 2.90e-14 m^2
Resonant optical depth: 43.57

=== Scanning Probe Detuning ===

=== EIT Window Characteristics ===
Maximum transmission with EIT: 1.0000
Minimum transmission without coupling: 1.0000
Transparency enhancement: 1.00x
EIT contrast: 0.00%
EIT window width (FWHM): 200.00 MHz
Expected width (~ Omega_c): 313.57 MHz

=== Group Velocity Effects ===
Maximum group delay derivative: 0.00e+00 s
Group velocity: 3.00e+08 m/s
Group velocity reduction factor: 1.00e+00

=== Dark State Composition ===
Dark state |D⟩ = 0.9950|F=2⟩ - 0.0995|F=1⟩
Population in |F=2⟩: 0.9901
Population in |F=1⟩: 0.0099

=== Physical Validation ===
Transmission range: [0.9846, 1.0000]
All transmissions in [0,1]: True
EIT enhancement reasonable (<100x): True
Coupling Rabi > Probe Rabi (required for EIT): True
Doppler width > Natural linewidth: True

=== Quantum Interference Summary ===
EIT demonstrates quantum interference between two excitation pathways:
  Path 1: |F=1⟩ --probe--> |5P_3/2⟩
  Path 2: |F=2⟩ --coupling--> |5P_3/2⟩

At two-photon resonance, destructive interference creates:
  - Dark state that cannot absorb probe photons
  - Transparency window of width 200.00 MHz
  - 1.0x enhancement in transmission
  - Group velocity reduction to 3.00e+08 m/s (1x slower than c)

When coupling laser is blocked (Omega_c = 0):
  - No quantum interference
  - Normal absorption restored (transmission = 1.0000)

Plot saved as 'eit_simulation.png'

=== Simulation Complete ===
```

### Generated Figures

This simulation produced 1 figure(s). See the `figures/` folder:

- **Figure 1:** `figures/figure_01.png`

---

## Physics Analysis

### Physics Correctness
The physics intent is correct - EIT in a Lambda system with quantum interference creating a dark state. However, the implementation has critical flaws: (1) The steady-state density matrix solution is incomplete and incorrectly normalized. The formula used doesn't properly account for atomic populations and uses an ad-hoc normalization factor (Omega_p/Gamma) without justification. (2) The susceptibility calculation for dispersion is incorrect - it uses the coherence directly rather than the proper relationship chi = -N*d^2*rho_13/(epsilon_0*hbar*E). (3) The optical depth scaling factor of 0.01 is arbitrary and destroys the physical meaning - it makes the medium essentially transparent regardless of EIT. (4) The two-photon resonance condition is mentioned but the coupling laser detuning is fixed at zero, which doesn't properly demonstrate the resonance condition.

### Implementation Quality
Code is well-structured with good documentation and parameter definitions. Uses appropriate libraries (scipy, numpy). However, critical implementation errors: (1) The lambda_system_steady_state function doesn't solve the full density matrix equations - it only computes one coherence element without proper population dynamics. (2) The normalization scheme (multiplying by OD_resonant * 0.01) is physically incorrect and arbitrary. (3) No validation that the steady-state solution converges or is physically meaningful. (4) The group velocity calculation uses gradient of phase shift but doesn't properly compute the refractive index from susceptibility. (5) Missing proper treatment of the two-photon detuning scan - should vary delta_coupling relative to delta_probe.

### Results Validity
The results are unphysical and demonstrate the implementation is broken: (1) Transmission is 1.0 (100%) both WITH and WITHOUT the coupling laser - this means no absorption at all, which contradicts the stated optical depth of 43.57. (2) Zero EIT contrast (0.00%) means the simulation shows no EIT effect whatsoever. (3) Zero group velocity reduction (factor = 1.00) means no slow light effect. (4) The transparency enhancement is 1.0x, meaning no enhancement. (5) The transmission range [0.9846, 1.0000] indicates essentially no absorption even though OD_resonant = 43.57 should give transmission ~ exp(-43.57) ≈ 10^-19 without EIT. The 0.01 scaling factor made the medium artificially transparent. These results show the simulation completely failed to demonstrate EIT.

### Key Findings
- Simulation shows 100% transmission both with and without coupling laser - no EIT effect demonstrated
- Zero EIT contrast and zero group velocity reduction indicate complete simulation failure
- Arbitrary 0.01 scaling factor destroys physical optical depth, making medium transparent regardless of quantum interference
- Dark state composition is correctly calculated (99% in |F=2⟩) but has no effect on transmission due to broken absorption calculation
- Doppler broadening (323 MHz) properly dominates natural linewidth (6 MHz) for warm vapor

### Limitations
- Density matrix solution is incomplete - doesn't solve full Lindblad master equation for populations and coherences
- No proper treatment of saturation effects or power broadening
- Fixed coupling detuning prevents demonstration of two-photon resonance condition
- Arbitrary normalization destroys quantitative accuracy
- No time-dependent dynamics - only steady state
- Doesn't account for transit-time broadening in warm vapor
- Missing proper susceptibility-to-refractive-index conversion for group velocity

### Recommendations for Improvement
- Study proper density matrix formalism for three-level systems (e.g., Scully & Zubairy Chapter 7)
- Implement full optical Bloch equations with populations rho_11, rho_22, rho_33 and all coherences
- Remove arbitrary scaling factors - let optical depth determine transmission naturally
- Validate against experimental EIT papers (e.g., Harris et al. Phys. Rev. Lett. 1990) for realistic parameter ranges

---

## Design Alignment

This simulation was designed to model:
> The experiment creates a three-level Λ-system in Rb-87 atoms where both the probe and coupling lasers (780nm D2 line) couple different ground state hyperfine levels 5S_1/2(F=1) and 5S_1/2(F=2) to the same excited state 5P_3/2. Quantum interference between the two excitation pathways creates a coherent dark state |D⟩ = (Ωc|F=1⟩ - Ωp|F=2⟩)/√(|Ωc|² + |Ωp|²) that cannot absorb probe photons. When both lasers satisfy the two-photon resonance condition (δ_probe + δ_coupling = 0), destructive interference eliminates absorption and the medium becomes transparent to the probe (EIT window), accompanied by steep dispersion causing dramatic group velocity reduction. The transparency width is determined by the coupling Rabi frequency Ωc, and the effect vanishes when the coupling laser is blocked, restoring normal absorption.

The simulation does not adequately capture the intended quantum physics.

---

*Report generated by AgenticQuantum Free-Form Simulation System*
