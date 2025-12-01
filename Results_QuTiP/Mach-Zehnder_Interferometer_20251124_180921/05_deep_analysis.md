# Deep Analysis: Design vs Simulation vs Results

**Experiment:** Mach-Zehnder Interferometer

**Timestamp:** 20251124_180921

**Quality Rating:** 7/10 (GOOD)

---

## Overview

The designer wants to demonstrate quantum interference in a Mach-Zehnder interferometer using coherent laser light, showing how the interference pattern I ∝ 1 + cos(φ) emerges from quantum superposition. The simulation code attempts to model this using QuTip's coherent states and beam splitter operators, and surprisingly produces excellent results that closely match the theoretical expectations.

The simulation correctly implements the key physics: (1) Initial coherent state |α⟩ representing laser light, (2) 50:50 beam splitter creating superposition between two spatial modes, (3) Phase shifter on one arm introducing controllable phase difference, (4) Second beam splitter for recombination, and (5) Photon number measurements at both outputs.

The results show near-perfect visibility (≈1.0) and complementary oscillations between the two detectors as phase varies, exactly matching the expected I ∝ 1 + cos(φ) behavior. The outputs show proper anti-correlation: when detector 1 is minimum (~0), detector 2 is maximum (~2.7), and vice versa.

However, there's a significant energy conservation violation (15% loss) that suggests either numerical errors in the beam splitter implementation or issues with the two-mode coherent state evolution. The high state purity (≈1.0) after the first beam splitter is actually incorrect - a coherent state split by a beam splitter should create an entangled two-mode state with reduced purity.

Despite these issues, the core interference physics is captured correctly. The Fock state basis can represent coherent states and their interference, unlike temporal effects that require continuous variables. This simulation successfully validates the basic design concept.

## Key Insight

Fock state basis successfully captures coherent light interference in Mach-Zehnder geometry, validating the core quantum optics despite some numerical implementation issues.

## Design Intent

**Components:**
- Coherent laser: 632.8nm, 5mW power source
- Input beam splitter: 50:50 splitting for superposition creation
- Phase shifter: Controllable 0-2π phase difference
- Output beam splitter: Recombination for interference
- Two detectors: Complementary intensity measurements

**Physics Goal:** Demonstrate quantum interference from coherent light superposition showing I ∝ 1 + cos(φ) oscillations

**Key Parameters:**
- wavelength: 632.8nm
- transmittance: 0.5
- phase_range: 6.28 radians
- detector_efficiency: 85%

## QuTiP Implementation

### State Init

```python
coherent_state = qt.coherent(cutoff_dim, alpha)
vacuum_state = qt.fock(cutoff_dim, 0)
initial_state = qt.tensor(coherent_state, vacuum_state)
```

### Operations

```python
theta_bs = np.pi/4  # 50:50 beam splitter angle
H_bs = theta_bs * (a.dag() * b + a * b.dag())
U_bs1 = (-1j * H_bs).expm()
phase_op = qt.tensor(qt.qeye(cutoff_dim), (1j * phi * qt.num(cutoff_dim)).expm())
```

### Measurements

```python
n_mode0 = qt.tensor(qt.num(cutoff_dim), qt.qeye(cutoff_dim))
output1 = float(abs(qt.expect(n_mode0, final_state))) * detector_efficiency
```

## How Design Maps to Code

The code implementation correctly maps the designer's intent: coherent states represent laser light, tensor products model spatial mode splitting, beam splitter Hamiltonians create superposition, phase operators introduce controllable phase shifts, and photon number operators measure detector outputs. The physics is fundamentally sound, though numerical issues affect energy conservation.

## Identified Limitations

- Energy conservation violation indicates numerical or implementation errors
- State purity calculation suggests incorrect entanglement modeling after beam splitting
- No temporal coherence effects - assumes perfect spatial mode overlap
- Fixed cutoff dimension may truncate coherent state representation
- Classical detector model doesn't include quantum efficiency fluctuations

## Recommendations

1. Fix the energy conservation implementation - check beam splitter transmission/reflection coefficients sum to unity
2. Verify detector efficiency is properly accounted for in energy calculations
3. Validate that the initial coherent state energy calculation matches the quantum field theory expectation

## Conclusion

✅ Simulation successfully captured the design's intended physics.
