# Deep Analysis: Design vs Simulation vs Results

**Experiment:** Michelson Interferometer

**Timestamp:** 20251124_190302

**Quality Rating:** 9/10 (EXCELLENT)

---

## Overview

The designer wants to demonstrate a Michelson interferometer where coherent laser light is split, travels different path lengths, and recombines to create interference fringes that shift when one mirror moves. The simulation code correctly models this quantum mechanically using a two-mode system with coherent states and beam splitter operations. The key physics - coherent beam splitting, phase accumulation from path differences, and recombination interference - are all properly captured. The code correctly uses the adjoint beam splitter operation (U_bs.dag()) for recombination, which is crucial since the returning beams interact with the beam splitter from the opposite direction. The results show perfect visibility (≈1.0) and excellent energy conservation, exactly matching theoretical expectations for a Michelson interferometer with coherent light. The phase sensitivity of 1.25 photons/radian is reasonable for the coherent state amplitude used. This simulation successfully validates the designer's claims about fringe formation and phase sensitivity.

## Key Insight

This simulation excellently captures Michelson interferometer physics in the quantum regime, correctly modeling coherent state interference with proper beam splitter reciprocity.

## Design Intent

**Components:**
- HeNe laser: 632.8nm coherent source at 5mW power
- Beam expander: 3x magnification for proper beam size
- 50:50 beam splitter: splits light into two perpendicular arms
- Fixed mirror M1: reflects transmission arm back
- Piezo mirror M2: reflects reflection arm with controllable phase
- Detection screen: observes interference pattern

**Physics Goal:** Demonstrate coherent beam interference with phase-sensitive fringe patterns that shift when mirror position changes

**Key Parameters:**
- wavelength: 632.8nm
- transmittance: 0.5 (50:50 split)
- mirror_reflectivity: 0.99
- phase_shift_range: 0 to π radians

## QuTiP Implementation

### State Init

```python
# Initial coherent state from laser
coherent_input = qt.coherent(cutoff_dim, alpha)
vacuum_mode = qt.fock(cutoff_dim, 0)
initial_state = qt.tensor(coherent_input, vacuum_mode)
```

### Operations

```python
# Beam splitter operation
theta_bs = np.pi/4  # 50:50 beam splitter angle
a = qt.tensor(qt.destroy(cutoff_dim), qt.qeye(cutoff_dim))
b = qt.tensor(qt.qeye(cutoff_dim), qt.destroy(cutoff_dim))
H_bs = theta_bs * (a.dag() * b + a * b.dag())
U_bs = (-1j * H_bs).expm()

# Phase shift from movable mirror
phase_op_pi = qt.tensor(qt.qeye(cutoff_dim), (1j * phase_shift_pi * qt.num(cutoff_dim)).expm())

# Recombination with adjoint operation
state_phase_pi = U_bs.dag() * (phase_op_pi * state_after_mirrors)
```

### Measurements

```python
# Intensity detection at screen
n_screen = qt.tensor(qt.num(cutoff_dim), qt.qeye(cutoff_dim))
intensity_phase_0 = float(abs(qt.expect(n_screen, state_phase_0)))
intensity_phase_pi = float(abs(qt.expect(n_screen, state_phase_pi)))

# Visibility calculation
visibility = float((I_max - I_min) / (I_max + I_min + 1e-12))
```

## How Design Maps to Code

The code implementation faithfully captures the designer's intent. The two-mode approach correctly represents the two interferometer arms, the beam splitter operations properly model the 50:50 splitting and recombination, and the phase shift operator accurately represents the movable mirror's effect. The use of U_bs.dag() for recombination is particularly sophisticated, showing deep understanding of beam splitter reciprocity. The coherent state initialization matches the laser source, and the intensity measurements at the screen correspond exactly to the designer's detection scheme. The only minor gap is that beam expansion is noted but not quantum-mechanically modeled, which is appropriate since it mainly affects classical beam parameters rather than quantum interference.

## Identified Limitations

- No spatial beam profile modeling - assumes perfect mode matching
- No temporal dynamics - instantaneous propagation assumed
- Classical mirror vibrations/noise not included
- Beam alignment and wavefront errors not modeled
- Limited to quantum shot noise - no technical noise sources

## Recommendations

1. Consider adding realistic noise sources (thermal fluctuations, mechanical vibrations) to better model experimental conditions
2. Implement beam splitter losses and detector efficiency to simulate practical limitations
3. Add phase drift modeling to test long-term stability requirements

## Conclusion

✅ Simulation successfully captured the design's intended physics.
