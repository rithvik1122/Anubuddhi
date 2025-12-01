"""
Simple optical table renderer for LLM-designed experiments.
Takes LLM component positions and renders them directly.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch
from typing import Dict, List, Any, Tuple
import numpy as np


def create_optical_table_figure(experiment_dict: Dict[str, Any], 
                                figsize: Tuple[int, int] = (14, 8),
                                dpi: int = 100) -> plt.Figure:
    """
    Create optical table diagram from LLM-designed experiment.
    
    Args:
        experiment_dict: Dict with 'steps' containing components with x, y positions
        figsize: Figure size
        dpi: Resolution
        
    Returns:
        matplotlib Figure
    """
    
    steps = experiment_dict.get('steps', [])
    if not steps:
        return _create_empty_figure(figsize, dpi)
    
    # Create figure with dark warm background
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor='#1a1410')
    ax.set_facecolor('#2d1810')
    
    # Set up coordinate system (0-10 x, 0-6 y as LLM uses)
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.5, 6.5)
    ax.set_aspect('equal')
    
    # Draw optical table grid
    ax.grid(True, alpha=0.2, color='#d4a574', linestyle=':', linewidth=0.5)
    
    # Remove axis labels but keep grid
    ax.set_xticks(range(0, 11))
    ax.set_yticks(range(0, 7))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    # Title
    title = experiment_dict.get('title', 'Quantum Experiment')
    ax.set_title(title, color='#f0d9c0', fontsize=16, pad=20, fontweight='light')
    
    # First, get or generate beam paths (needed for component angle calculation)
    beam_paths_raw = experiment_dict.get('beam_path', None)
    beam_paths_list = []  # List of paths, each path is list of (x,y)
    
    if beam_paths_raw:
        # Accept either a single path (list of coords) or a list of paths
        if isinstance(beam_paths_raw, list) and beam_paths_raw and isinstance(beam_paths_raw[0][0], (int, float)):
            # Single path provided as list of (x,y)
            beam_paths_list = [beam_paths_raw]
        else:
            # Multiple paths provided
            beam_paths_list = beam_paths_raw
    else:
        # Auto-generate sensible paths from sources to detectors
        positions_map = []  # list of (type, x, y, original_step)
        for step in steps:
            x = step.get('position', [0, 0])[0] if isinstance(step.get('position'), (list, tuple)) else step.get('x', 0)
            y = step.get('position', [0, 0])[1] if isinstance(step.get('position'), (list, tuple)) else step.get('y', 0)
            positions_map.append((step.get('type', 'unknown'), float(x), float(y), step))

        # Find sources
        sources = [p for p in positions_map if p[0] in ['laser', 'source']]
        if not sources:
            # fallback: connect in order
            positions = [(p[1], p[2]) for p in positions_map]
            if len(positions) > 1:
                beam_paths_list = [positions]
        else:
            # For each source, follow nearest-neighbour forward in +x direction and branch on beam_splitter
            paths = []
            for s in sources:
                path = [(s[1], s[2])]
                current_x = s[1]
                visited_idx = set()
                # index of source in positions_map
                try:
                    start_idx = positions_map.index(s)
                except ValueError:
                    start_idx = None
                if start_idx is not None:
                    visited_idx.add(start_idx)

                # Keep adding nearest components with x >= current_x - small epsilon
                while True:
                    candidates = [(idx, p) for idx, p in enumerate(positions_map) if idx not in visited_idx and p[1] >= current_x - 0.1]
                    if not candidates:
                        break
                    # choose candidate with smallest x distance
                    candidates.sort(key=lambda item: (item[1][1]-current_x, abs(item[1][2]-s[2])))
                    next_idx, next_p = candidates[0]
                    visited_idx.add(next_idx)
                    path.append((next_p[1], next_p[2]))
                    current_x = next_p[1]
                    if next_p[0] in ['detector']:
                        break
                    if next_p[0] in ['beam_splitter']:
                        # Branch: find other nearby component roughly at same x and offset y
                        others = [(idx, q) for idx, q in enumerate(positions_map) if idx not in visited_idx and abs(q[1]-next_p[1]) < 1.0 and abs(q[2]-next_p[2]) > 0.2]
                        if others:
                            # create second path from splitter
                            other_idx, other = others[0]
                            visited_idx.add(other_idx)
                            branch = [(next_p[1], next_p[2]), (other[1], other[2])]
                            # then continue from branch end to nearest detector
                            dets = [q for q in positions_map if q[0]=='detector']
                            if dets:
                                det = min(dets, key=lambda d: (d[1]-other[1])**2 + (d[2]-other[2])**2)
                                branch.append((det[1], det[2]))
                            paths.append(branch)
                paths.append(path)

            # Store for angle calculation
            beam_paths_list = paths
    
    # Now draw components (no angle calculation needed - LLM provides angles)
    for i, step in enumerate(steps, 1):  # Start numbering from 1
        x = step.get('position', [0, 0])[0] if isinstance(step.get('position'), (list, tuple)) else step.get('x', i*2)
        y = step.get('position', [0, 0])[1] if isinstance(step.get('position'), (list, tuple)) else step.get('y', 3)
        comp_type = step.get('type', 'unknown')
        # Use number instead of description
        label = str(i)
        
        _draw_component(ax, comp_type, x, y, label, '#d4a574')
    
    # Draw beam paths
    for i, path in enumerate(beam_paths_list):
        _draw_beam_path(ax, path, path_index=i)
    
    plt.tight_layout()
    return fig


def _draw_component(ax, comp_type: str, x: float, y: float, label: str, color: str):
    """Draw a single optical component."""
    
    color = '#d4a574'
    text_color = '#f0d9c0'
    
    if comp_type == 'laser' or comp_type == 'source':
        # Laser source - rectangle with beam output
        rect = FancyBboxPatch((x-0.3, y-0.2), 0.6, 0.4, 
                             boxstyle="round,pad=0.05",
                             edgecolor=color, facecolor='#3d2810',
                             linewidth=2)
        ax.add_patch(rect)
        # Beam indicator
        ax.arrow(x+0.3, y, 0.2, 0, head_width=0.1, head_length=0.1,
                fc=color, ec=color, alpha=0.7)
        
    elif comp_type == 'beam_splitter':
        # Beam splitter - diamond shape at 45° (default)
        diamond = patches.RegularPolygon((x, y), 4, radius=0.35,
                                        orientation=np.pi/4,
                                        edgecolor=color, facecolor='#3d2810',
                                        linewidth=2)
        ax.add_patch(diamond)
        # Add split indicator
        ax.plot([x-0.25, x+0.25], [y-0.25, y+0.25], 
               color=color, linewidth=1, alpha=0.5)
        
    elif comp_type == 'mirror':
        # Mirror - angled line with reflective backing at 45° (default)
        ax.plot([x-0.25, x+0.25], [y-0.25, y+0.25], 
               color=color, linewidth=5, solid_capstyle='round', zorder=4)
        # Add backing to show it's reflective
        ax.plot([x-0.27, x+0.27], [y-0.27, y+0.27], 
               color='#1a1410', linewidth=7, solid_capstyle='round', zorder=3, alpha=0.5)
        
    elif comp_type == 'detector':
        # Detector - circle
        circle = Circle((x, y), 0.25, 
                       edgecolor=color, facecolor='#3d2810',
                       linewidth=2)
        ax.add_patch(circle)
        # Add detector symbol
        ax.plot([x-0.1, x+0.1], [y, y], color=color, linewidth=2)
        ax.plot([x, x], [y-0.1, y+0.1], color=color, linewidth=2)
        
    elif comp_type == 'crystal':
        # Nonlinear crystal - hexagon
        hexagon = patches.RegularPolygon((x, y), 6, radius=0.3,
                                        edgecolor=color, facecolor='#3d2810',
                                        linewidth=2)
        ax.add_patch(hexagon)
        
    elif comp_type == 'phase_shifter':
        # Phase shifter - small rectangle
        rect = Rectangle((x-0.15, y-0.25), 0.3, 0.5,
                        edgecolor=color, facecolor='#3d2810',
                        linewidth=2)
        ax.add_patch(rect)
        # Add phase symbol
        ax.text(x, y, 'φ', ha='center', va='center',
               color=text_color, fontsize=10, weight='bold')
        
    elif comp_type == 'lens' or comp_type == 'convex_lens':
        # Convex lens - biconvex shape
        ax.plot([x-0.2, x], [y-0.3, y], color=color, linewidth=2)
        ax.plot([x-0.2, x], [y+0.3, y], color=color, linewidth=2)
        ax.plot([x, x+0.2], [y, y-0.3], color=color, linewidth=2)
        ax.plot([x, x+0.2], [y, y+0.3], color=color, linewidth=2)
    
    elif comp_type == 'concave_lens':
        # Concave lens - biconcave shape
        ax.plot([x-0.2, x], [y-0.3, y], color=color, linewidth=2)
        ax.plot([x-0.2, x], [y+0.3, y], color=color, linewidth=2)
        ax.plot([x+0.2, x], [y, y-0.3], color=color, linewidth=2)
        ax.plot([x+0.2, x], [y, y+0.3], color=color, linewidth=2)
    
    elif comp_type == 'cylindrical_lens':
        # Cylindrical lens - flat on one side
        ax.plot([x-0.2, x-0.2], [y-0.3, y+0.3], color=color, linewidth=2)
        ax.plot([x-0.2, x+0.2], [y-0.3, y], color=color, linewidth=2)
        ax.plot([x-0.2, x+0.2], [y+0.3, y], color=color, linewidth=2)
    
    elif comp_type == 'concave_mirror' or comp_type == 'curved_mirror':
        # Curved mirror - arc shape
        theta = np.linspace(-np.pi/4, np.pi/4, 20)
        r = 0.3
        arc_x = x + r * np.cos(theta + np.pi)
        arc_y = y + r * np.sin(theta + np.pi)
        ax.plot(arc_x, arc_y, color=color, linewidth=4, solid_capstyle='round', zorder=4)
        # Add backing
        ax.plot(arc_x, arc_y, color='#1a1410', linewidth=6, solid_capstyle='round', zorder=3, alpha=0.5)
        
    elif comp_type == 'slit' or comp_type == 'double_slit':
        # Slit(s) - vertical line(s) with gap(s)
        if 'double' in comp_type:
            # Double slit - two narrow gaps
            ax.plot([x, x], [y-0.35, y-0.08], color=color, linewidth=3)
            ax.plot([x, x], [y-0.04, y+0.04], color=color, linewidth=3)
            ax.plot([x, x], [y+0.08, y+0.35], color=color, linewidth=3)
        else:
            # Single slit - one gap
            ax.plot([x, x], [y-0.35, y-0.1], color=color, linewidth=3)
            ax.plot([x, x], [y+0.1, y+0.35], color=color, linewidth=3)
    
    elif comp_type == 'screen':
        # Screen - perpendicular to beam direction
        # Default: vertical (for horizontal beams)
        # If beam comes from above/below, make horizontal
        screen_angle = 0  # Default vertical
        
        # Draw screen perpendicular to typical beam direction
        dx = 0.4 * np.sin(screen_angle)
        dy = 0.4 * np.cos(screen_angle)
        ax.plot([x-dx, x+dx], [y-dy, y+dy], color=color, linewidth=4, alpha=0.7)
        # Add small perpendicular lines at ends
        end_dx = 0.05 * np.cos(screen_angle)
        end_dy = 0.05 * np.sin(screen_angle)
        ax.plot([x-dx-end_dx, x-dx+end_dx], [y-dy-end_dy, y-dy+end_dy], color=color, linewidth=2)
        ax.plot([x+dx-end_dx, x+dx+end_dx], [y+dy-end_dy, y+dy+end_dy], color=color, linewidth=2)
    
    elif comp_type == 'aperture' or comp_type == 'iris':
        # Aperture/Iris - circle with opening
        circle = Circle((x, y), 0.3, 
                       edgecolor=color, facecolor='none',
                       linewidth=2)
        ax.add_patch(circle)
        # Add iris blades indication
        for angle in [0, 60, 120, 180, 240, 300]:
            rad = np.radians(angle)
            ax.plot([x, x+0.15*np.cos(rad)], [y, y+0.15*np.sin(rad)], 
                   color=color, linewidth=1, alpha=0.6)
    
    elif comp_type == 'polarizer':
        # Polarizer - square with double arrows
        rect = Rectangle((x-0.2, y-0.2), 0.4, 0.4,
                        edgecolor=color, facecolor='#3d2810',
                        linewidth=2)
        ax.add_patch(rect)
        # Polarization direction indicator
        ax.arrow(x-0.12, y-0.12, 0.24, 0.24, head_width=0.08, head_length=0.08,
                fc=color, ec=color, alpha=0.7, linewidth=1)
    
    elif comp_type == 'wave_plate' or comp_type == 'waveplate':
        # Wave plate - thin rectangle
        rect = Rectangle((x-0.25, y-0.15), 0.5, 0.3,
                        edgecolor=color, facecolor='#3d2810',
                        linewidth=2)
        ax.add_patch(rect)
        # Add λ/2 or λ/4 label (will be in description)
        ax.text(x, y, 'λ', ha='center', va='center',
               color=text_color, fontsize=9, weight='bold')
    
    elif comp_type == 'filter':
        # Optical filter - square with gradient indication
        rect = Rectangle((x-0.2, y-0.2), 0.4, 0.4,
                        edgecolor=color, facecolor='#3d2810',
                        linewidth=2)
        ax.add_patch(rect)
        # Add filter pattern
        for i, offset in enumerate([-0.1, 0, 0.1]):
            alpha = 0.3 + i*0.2
            ax.plot([x-0.15, x+0.15], [y+offset, y+offset], 
                   color=color, linewidth=1, alpha=alpha)
    
    elif comp_type == 'prism':
        # Prism - triangle
        triangle = patches.RegularPolygon((x, y), 3, radius=0.3,
                                         orientation=np.pi/6,
                                         edgecolor=color, facecolor='#3d2810',
                                         linewidth=2)
        ax.add_patch(triangle)
    
    elif comp_type == 'attenuator' or comp_type == 'nd_filter':
        # Neutral density filter / attenuator - circle with gradient
        circle = Circle((x, y), 0.25, 
                       edgecolor=color, facecolor='#2a1a10',
                       linewidth=2)
        ax.add_patch(circle)
        ax.text(x, y, 'ND', ha='center', va='center',
               color=text_color, fontsize=8, weight='bold')
    
    elif comp_type == 'delay' or comp_type == 'delay_stage':
        # Delay stage - rectangle with motion indicator
        rect = Rectangle((x-0.3, y-0.15), 0.6, 0.3,
                        edgecolor=color, facecolor='#3d2810',
                        linewidth=2)
        ax.add_patch(rect)
        # Add motion arrows
        ax.arrow(x-0.15, y, 0.1, 0, head_width=0.08, head_length=0.05,
                fc=color, ec=color, alpha=0.5, linewidth=1)
        ax.arrow(x+0.15, y, -0.1, 0, head_width=0.08, head_length=0.05,
                fc=color, ec=color, alpha=0.5, linewidth=1)
    
    elif comp_type == 'beam_dump' or comp_type == 'absorber':
        # Beam dump - filled triangle pointing toward beam
        triangle = patches.RegularPolygon((x, y), 3, radius=0.3,
                                         orientation=0,
                                         edgecolor=color, facecolor='#1a1410',
                                         linewidth=2)
        ax.add_patch(triangle)
    
    elif comp_type == 'dichroic_mirror' or comp_type == 'dichroic':
        # Dichroic mirror - mirror with wavelength symbol
        ax.plot([x-0.25, x+0.25], [y-0.25, y+0.25], 
               color=color, linewidth=5, solid_capstyle='round', zorder=4)
        ax.plot([x-0.27, x+0.27], [y-0.27, y+0.27], 
               color='#1a1410', linewidth=7, solid_capstyle='round', zorder=3, alpha=0.5)
        # Add λ symbol
        ax.text(x+0.15, y-0.35, 'λ', ha='center', va='center',
               color=text_color, fontsize=8, weight='bold')
    
    elif comp_type == 'beam_expander':
        # Beam expander - two lenses
        ax.plot([x-0.25, x-0.15], [y-0.2, y], color=color, linewidth=2)
        ax.plot([x-0.25, x-0.15], [y+0.2, y], color=color, linewidth=2)
        ax.plot([x+0.15, x+0.25], [y-0.3, y], color=color, linewidth=2)
        ax.plot([x+0.15, x+0.25], [y+0.3, y], color=color, linewidth=2)
    
    elif comp_type == 'spatial_filter' or comp_type == 'pinhole':
        # Spatial filter/pinhole - small circle
        circle = Circle((x, y), 0.15, 
                       edgecolor=color, facecolor='#3d2810',
                       linewidth=2)
        ax.add_patch(circle)
        # Tiny center hole
        center = Circle((x, y), 0.03, 
                       edgecolor='none', facecolor='#2d1810',
                       linewidth=1)
        ax.add_patch(center)
    
    elif comp_type == 'fiber' or comp_type == 'fiber_coupler':
        # Fiber coupler - circle with fiber line
        circle = Circle((x, y), 0.2, 
                       edgecolor=color, facecolor='#3d2810',
                       linewidth=2)
        ax.add_patch(circle)
        # Fiber line
        ax.plot([x+0.2, x+0.4], [y, y], color=color, linewidth=2, linestyle='--')
    
    elif comp_type == 'grating' or comp_type == 'diffraction_grating':
        # Diffraction grating - vertical lines
        rect = Rectangle((x-0.15, y-0.3), 0.3, 0.6,
                        edgecolor=color, facecolor='#3d2810',
                        linewidth=2)
        ax.add_patch(rect)
        # Grating lines
        for offset in np.linspace(-0.1, 0.1, 5):
            ax.plot([x+offset, x+offset], [y-0.25, y+0.25], 
                   color=color, linewidth=0.5, alpha=0.7)
    
    elif comp_type == 'etalon' or comp_type == 'fabry_perot':
        # Etalon/Fabry-Perot - two parallel mirrors
        ax.plot([x-0.2, x-0.2], [y-0.25, y+0.25], color=color, linewidth=3)
        ax.plot([x+0.2, x+0.2], [y-0.25, y+0.25], color=color, linewidth=3)
        # Add FP label
        ax.text(x, y, 'FP', ha='center', va='center',
               color=text_color, fontsize=7, weight='bold')
    
    elif comp_type == 'rotator' or comp_type == 'faraday_rotator':
        # Faraday rotator - rectangle with rotation symbol
        rect = Rectangle((x-0.2, y-0.2), 0.4, 0.4,
                        edgecolor=color, facecolor='#3d2810',
                        linewidth=2)
        ax.add_patch(rect)
        # Rotation arrow
        circle_arc = patches.Arc((x, y), 0.25, 0.25, angle=0, theta1=45, theta2=315,
                                edgecolor=color, linewidth=1.5)
        ax.add_patch(circle_arc)
    
    elif comp_type == 'isolator' or comp_type == 'optical_isolator':
        # Optical isolator - arrow box
        rect = Rectangle((x-0.25, y-0.15), 0.5, 0.3,
                        edgecolor=color, facecolor='#3d2810',
                        linewidth=2)
        ax.add_patch(rect)
        # One-way arrow
        ax.arrow(x-0.15, y, 0.25, 0, head_width=0.12, head_length=0.1,
                fc=color, ec=color, linewidth=2)
    
    elif comp_type == 'modulator' or comp_type == 'eom' or comp_type == 'aom':
        # Electro-optic or acousto-optic modulator
        rect = Rectangle((x-0.25, y-0.2), 0.5, 0.4,
                        edgecolor=color, facecolor='#3d2810',
                        linewidth=2)
        ax.add_patch(rect)
        # Modulation symbol (sine wave)
        wave_x = np.linspace(x-0.15, x+0.15, 20)
        wave_y = y + 0.08 * np.sin((wave_x - x) * 15)
        ax.plot(wave_x, wave_y, color=color, linewidth=1.5, alpha=0.7)
    
    elif comp_type == 'spectrometer':
        # Spectrometer - box with dispersion symbol
        rect = Rectangle((x-0.3, y-0.25), 0.6, 0.5,
                        edgecolor=color, facecolor='#3d2810',
                        linewidth=2)
        ax.add_patch(rect)
        # Rainbow dispersion
        colors_spec = ['#ff0000', '#ffaa00', '#00ff00', '#0000ff']
        for i, c in enumerate(colors_spec):
            y_offset = -0.15 + i * 0.1
            ax.plot([x-0.2, x+0.2], [y+y_offset, y+y_offset], 
                   color=c, linewidth=1.5, alpha=0.6)
    
    elif comp_type == 'camera' or comp_type == 'ccd' or comp_type == 'cmos':
        # Camera/CCD/CMOS - rectangle with pixel grid
        rect = Rectangle((x-0.3, y-0.25), 0.6, 0.5,
                        edgecolor=color, facecolor='#3d2810',
                        linewidth=2)
        ax.add_patch(rect)
        # Pixel grid
        for i in range(3):
            ax.plot([x-0.2+i*0.2, x-0.2+i*0.2], [y-0.15, y+0.15], 
                   color=color, linewidth=0.5, alpha=0.5)
            ax.plot([x-0.2, x+0.2], [y-0.15+i*0.15, y-0.15+i*0.15], 
                   color=color, linewidth=0.5, alpha=0.5)
    
    elif comp_type == 'photodiode' or comp_type == 'apd' or comp_type == 'spad':
        # Photodiode/APD/SPAD - triangle in circle
        circle = Circle((x, y), 0.25, 
                       edgecolor=color, facecolor='#3d2810',
                       linewidth=2)
        ax.add_patch(circle)
        # Diode triangle
        triangle = patches.Polygon([[x-0.1, y-0.1], [x-0.1, y+0.1], [x+0.1, y]], 
                                   closed=True, edgecolor=color, facecolor='none', linewidth=1.5)
        ax.add_patch(triangle)
        # Arrows for incoming light
        ax.arrow(x-0.25, y+0.15, 0.1, -0.1, head_width=0.05, head_length=0.05,
                fc=color, ec=color, alpha=0.6, linewidth=1)
    
    elif comp_type == 'pmt' or comp_type == 'photomultiplier':
        # Photomultiplier tube - cylinder
        rect = Rectangle((x-0.25, y-0.3), 0.5, 0.6,
                        edgecolor=color, facecolor='#3d2810',
                        linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, 'PMT', ha='center', va='center',
               color=text_color, fontsize=7, weight='bold')
    
    else:
        # Generic/Custom component - rounded square with distinct styling
        # Check if this is a custom component (has description in name or special marker)
        is_custom = comp_type.startswith('custom_') or '(' in label
        
        if is_custom:
            # Custom component - distinct rounded square with dashed border
            fancy_box = FancyBboxPatch((x-0.25, y-0.25), 0.5, 0.5,
                                      boxstyle="round,pad=0.05",
                                      edgecolor='#ffa500', facecolor='#3d2810',
                                      linewidth=2.5, linestyle='--', alpha=0.9)
            ax.add_patch(fancy_box)
            # Add "C" marker for custom
            ax.text(x, y, 'C', ha='center', va='center',
                   color='#ffa500', fontsize=12, weight='bold', 
                   family='monospace')
        else:
            # Unknown standard component - simple square
            rect = Rectangle((x-0.2, y-0.2), 0.4, 0.4,
                            edgecolor=color, facecolor='#3d2810',
                            linewidth=2)
            ax.add_patch(rect)
    
    # Add label below component
    ax.text(x, y-0.5, label, ha='center', va='top',
           color=text_color, fontsize=16, weight='bold')


def _draw_beam_path(ax, path: List[Tuple[float, float]], path_index: int = 0):
    """Draw laser beam path connecting points.

    Supports multiple paths and backtracking (reflections) by drawing each segment.
    """
    
    if len(path) < 2:
        return
    
    # Color palette for multiple paths
    palette = ['#ff6b6b', '#4dabf7', '#ffd166', '#6a4c93', '#2ecc71', '#f08a5d']
    color = palette[path_index % len(palette)]

    # Draw each segment individually to handle backtracking/reflections
    for i in range(len(path)-1):
        x0, y0 = path[i]
        x1, y1 = path[i+1]
        
        # Check if this is a backtracking segment (return path)
        # by seeing if we've been to (x1,y1) before in the path
        is_return = (x1, y1) in path[:i]
        
        # Slightly offset return paths so they're visible
        offset = 0.0
        if is_return:
            offset = 0.1  # Small perpendicular offset for return beam
            # Calculate perpendicular direction
            dx = x1 - x0
            dy = y1 - y0
            length = np.sqrt(dx**2 + dy**2)
            if length > 0:
                perp_x = -dy / length * offset
                perp_y = dx / length * offset
                x0 += perp_x
                y0 += perp_y
                x1 += perp_x
                y1 += perp_y
        
        # Draw segment with glow
        ax.plot([x0, x1], [y0, y1], color=color, linewidth=8, 
               alpha=0.12, zorder=1)
        ax.plot([x0, x1], [y0, y1], color=color, linewidth=3, 
               alpha=0.6, zorder=2)
        
        # Add small arrow to show direction
        dx = x1 - x0
        dy = y1 - y0
        mid_x = x0 + dx * 0.6
        mid_y = y0 + dy * 0.6
        
        # Use smaller arrow for clarity
        arrow = FancyArrowPatch((mid_x - dx*0.1, mid_y - dy*0.1), 
                                (mid_x + dx*0.1, mid_y + dy*0.1),
                                arrowstyle='->', mutation_scale=15, 
                                linewidth=2, color=color, alpha=0.9, zorder=3)
        ax.add_patch(arrow)


def check_disconnected_components(steps, beam_paths_list):
    """
    Check if all components are connected by beam paths.
    Returns list of disconnected component names for validation feedback.
    """
    if not beam_paths_list:
        return []
    
    # Get all component positions
    component_positions = []
    for step in steps:
        x = step.get('position', [0, 0])[0] if isinstance(step.get('position'), (list, tuple)) else step.get('x', 0)
        y = step.get('position', [0, 0])[1] if isinstance(step.get('position'), (list, tuple)) else step.get('y', 0)
        comp_type = step.get('type', 'unknown')
        name = step.get('name', comp_type)
        component_positions.append((float(x), float(y), name))
    
    # Get all beam path coordinates
    beam_coords = set()
    for path in beam_paths_list:
        for coord in path:
            if len(coord) >= 2:
                beam_coords.add((round(coord[0], 1), round(coord[1], 1)))
    
    # Check each component
    disconnected = []
    for cx, cy, name in component_positions:
        # Check if component is near any beam path point (within 0.4 units)
        is_connected = False
        for bx, by in beam_coords:
            distance = np.sqrt((cx - bx)**2 + (cy - by)**2)
            if distance < 0.4:  # Tolerance for connection
                is_connected = True
                break
        
        if not is_connected:
            disconnected.append(name)
    
    return disconnected


def _create_empty_figure(figsize: Tuple[int, int], dpi: int) -> plt.Figure:
    """Create empty figure with message."""
    
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor='#1a1410')
    ax.set_facecolor('#2d1810')
    ax.text(0.5, 0.5, 'No components to display',
           ha='center', va='center', color='#d4a574',
           fontsize=14, transform=ax.transAxes)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    return fig
