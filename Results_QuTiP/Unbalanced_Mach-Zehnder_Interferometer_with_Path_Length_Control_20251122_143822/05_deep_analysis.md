# Deep Analysis: Design vs Simulation vs Results

**Experiment:** Unbalanced Mach-Zehnder Interferometer with Path Length Control

**Timestamp:** 20251122_143822

**Quality Rating:** 2/10 (POOR)

---

## Overview

The designer wants to demonstrate quantum interference in an unbalanced Mach-Zehnder interferometer, showing how path length differences create phase shifts that modulate interference visibility according to I₁,₂ = I₀(1 ± cos(φ))/2. However, the simulation has a fundamental conceptual flaw: it applies phase shifts using the operator (1j * φ * qt.num(cutoff_dim)).expm(), which is a number operator phase shift that affects photon statistics, not a spatial path length phase shift. Real interferometry phase shifts are geometric phases from optical path differences, implemented as simple multiplicative factors e^(iφ) on field amplitudes. The simulation shows extremely high visibility (>95%) that contradicts the theoretical prediction (16.6%) for coherent states, indicating the wrong physics is being modeled. Additionally, the path length calculation yields an enormous 85mm difference, creating massive phase accumulation (851,789 radians) that would wash out all interference in a real experiment due to laser coherence length limitations. The complementarity factor of 2.0 suggests perfect anti-correlation between detectors, which is suspicious for the weak coherent state used.

## Key Insight

The simulation applies quantum phase shifts to photon number states rather than classical optical path length phases, fundamentally misrepresenting interferometer physics.

## Design Intent

**Components:**
- HeNe laser: 632.8nm coherent source at 5mW power
- Two 50:50 beam splitters: split and recombine light paths
- Asymmetric mirror paths: upper arm shorter than lower arm
- Variable delay stage: 100μm range for phase control
- Two photodiode detectors: measure interference outputs

**Physics Goal:** Demonstrate wave-particle duality through phase-dependent quantum interference with controllable visibility

**Key Parameters:**
- wavelength: 632.8nm
- transmittance: 0.5 (50:50 beam splitters)
- delay_range: 100μm
- detector_efficiency: 0.85

## QuTiP Implementation

### State Init

```python
# Weak coherent state initialization
alpha = np.sqrt(0.1)
initial_state = qt.tensor(qt.coherent(cutoff_dim, alpha), qt.fock(cutoff_dim, 0))
initial_state = initial_state.unit()
```

### Operations

```python
# WRONG: Phase shift via number operator
phase_op = qt.tensor((1j * total_phase * qt.num(cutoff_dim)).expm(), qt.qeye(cutoff_dim))
state_with_phase = phase_op * state_after_split

# Beam splitter implementation
theta_bs = np.pi/4
H_bs = theta_bs * (a.dag() * b + a * b.dag())
U_input_bs = (-1j * H_bs).expm()
```

### Measurements

```python
# Detector measurements
n_mode0 = qt.tensor(qt.num(cutoff_dim), qt.qeye(cutoff_dim))
n_mode1 = qt.tensor(qt.qeye(cutoff_dim), qt.num(cutoff_dim))
intensity_1 = float(abs(qt.expect(n_mode0, final_state))) * detector_efficiency
intensity_2 = float(abs(qt.expect(n_mode1, final_state))) * detector_efficiency
```

## How Design Maps to Code

The design intent calls for classical optical path length differences creating geometric phases e^(iφ) that modulate interference visibility. However, the code implements quantum number operator phases e^(iφn̂) that fundamentally alter photon statistics rather than just adding geometric phases. This is like trying to model a classical wave interference pattern using particle creation/annihilation operators - the physics domains don't match. The correct implementation would apply simple phase factors to field amplitudes, not exponential number operators to quantum states.

## Identified Limitations

- Phase shifts applied via number operator instead of geometric optical path phases
- Fock space formalism cannot capture laser coherence length effects
- No modeling of temporal coherence or wavepacket distinguishability
- Enormous path differences would exceed laser coherence in real systems
- Beam splitter implementation may not preserve proper interference statistics

## Recommendations

1. Verify the theoretical visibility calculation for unbalanced interferometers - the formula may not account for the specific asymmetric configuration
2. Check beam splitter ratios and detector coupling efficiencies as these significantly affect visibility in unbalanced designs
3. Implement proper coherence length analysis since the 85.8 μm path difference may exceed coherence length for some light sources

## Conclusion

⚠️ Simulation could not fully capture the design's intended physics.
