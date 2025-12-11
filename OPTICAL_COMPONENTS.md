# Available Optical Components

The LLM designer can use any of these optical components when designing experiments:

## Sources
- `laser` - Laser source (coherent light)
- `source` - Generic light source

## Beam Manipulation
- `beam_splitter` - Splits beam into transmitted and reflected paths
- `mirror` - Reflects beam
- `prism` - Disperses or redirects light

## Phase & Polarization
- `phase_shifter` - Adjusts optical phase
- `polarizer` - Filters polarization state
- `wave_plate` / `waveplate` - Changes polarization (λ/2, λ/4, etc.)

## Intensity Control
- `filter` - Optical filter (spectral or spatial)
- `attenuator` - Reduces beam intensity
- `nd_filter` - Neutral density filter

## Focusing & Apertures
- `lens` - Focuses or collimates light
- `aperture` - Limits beam size
- `iris` - Adjustable aperture

## Nonlinear Optics
- `crystal` - Nonlinear crystal (SPDC, SHG, etc.)

## Detection
- `detector` - Photon detector (SPAD, APD, etc.)
- `screen` - Detection/observation screen

## Interference Elements
- `slit` - Single slit
- `double_slit` - Double slit for interference

## Timing
- `delay` / `delay_stage` - Optical delay line

## Usage Example

For a double-slit experiment:
```json
{
  "components": [
    {"type": "laser", "name": "HeNe Laser", "x": 1, "y": 3},
    {"type": "nd_filter", "name": "Attenuator", "x": 2, "y": 3},
    {"type": "lens", "name": "Collimating Lens", "x": 3, "y": 3},
    {"type": "double_slit", "name": "Double Slit", "x": 4, "y": 3},
    {"type": "screen", "name": "Detection Screen", "x": 8, "y": 3}
  ]
}
```

For a Hong-Ou-Mandel experiment:
```json
{
  "components": [
    {"type": "laser", "name": "Pump", "x": 1, "y": 3},
    {"type": "crystal", "name": "BBO Crystal", "x": 2, "y": 3},
    {"type": "mirror", "name": "Upper Mirror", "x": 4, "y": 4},
    {"type": "mirror", "name": "Lower Mirror", "x": 4, "y": 2},
    {"type": "beam_splitter", "name": "50:50 BS", "x": 6, "y": 3},
    {"type": "detector", "name": "Detector A", "x": 8, "y": 4},
    {"type": "detector", "name": "Detector B", "x": 8, "y": 2}
  ]
}
```
