"""
Professional optical table diagram generation using PyOpticalTable.

Maps quantum experiment components to optical elements and creates
matplotlib-based diagrams for visualization.
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Any, Tuple, Optional
import numpy as np

# Import PyOpticalTable (should be in parent directory)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
try:
    from pyopticaltable import OpticalTable, LaserBeam
    PYOPTICALTABLE_AVAILABLE = True
except ImportError:
    PYOPTICALTABLE_AVAILABLE = False
    print("Warning: PyOpticalTable not found, using fallback rendering")


def create_optical_table_figure(experiment_dict: Dict[str, Any], 
                                figsize: Tuple[int, int] = (14, 8),
                                dpi: int = 100) -> plt.Figure:
    """
    Create a professional optical table diagram from experiment description.
    
    Args:
        experiment_dict: Dictionary containing experiment steps and components
        figsize: Figure size (width, height) in inches
        dpi: Dots per inch for rendering
        
    Returns:
        matplotlib Figure object with optical table diagram
    """
    if PYOPTICALTABLE_AVAILABLE:
        return _create_pyopticaltable_figure(experiment_dict, figsize, dpi)
    else:
        return _create_fallback_figure(experiment_dict, figsize, dpi)


def _create_pyopticaltable_figure(experiment_dict: Dict[str, Any],
                                  figsize: Tuple[int, int],
                                  dpi: int) -> plt.Figure:
    """Create optical table using PyOpticalTable library."""
    
    # Parse experiment steps
    steps = experiment_dict.get('steps', [])
    if not steps:
        return _create_fallback_figure(experiment_dict, figsize, dpi)
    
    # Create optical table (coordinates from -5 to 5 in x, -3 to 3 in y)
    table = OpticalTable(length=10, width=6, size_factor=15.0, 
                        show_edge=False, show_grid=False)
    
    # Layout components horizontally along y=0 line
    x_positions = []
    y_position = 0
    spacing = 2.5  # spacing between elements
    current_x = -4.0  # start position
    
    # Store optical elements for beam tracing
    optics = []
    
    # Process each step and place optical elements with numbers
    for i, step in enumerate(steps, 1):
        step_type = step.get('step_type', '')
        component = step.get('component', {})
        comp_type = component.get('type', '')
        
        # Use number instead of descriptive label
        label = str(i)
        
        if step_type == 'state' or comp_type == 'state':
            # Photon source
            elem = table.box_source(current_x, y_position, 
                                   size_x=0.8, size_y=0.6, 
                                   angle=0, output_side='right',
                                   label=label, label_pos='bottom',
                                   colour='#d4a574', textcolour='#f0d9c0')
            optics.append(elem)
            current_x += spacing
            
        elif comp_type == 'beam_splitter':
            # 50:50 beam splitter cube
            elem = table.beamsplitter_cube(current_x, y_position,
                                          size=0.6, angle=45, direction='L',
                                          label=label,
                                          label_pos='bottom',
                                          colour='#d4a574', textcolour='#f0d9c0')
            optics.append(elem)
            current_x += spacing
            
        elif comp_type == 'phase_shift':
            # Phase shifter
            elem = table.transmissive_plate(current_x, y_position,
                                           size=0.5, angle=0,
                                           label=label,
                                           label_pos='bottom',
                                           colour='#d4a574', textcolour='#f0d9c0')
            optics.append(elem)
            current_x += spacing
            
        elif comp_type == 'displacement':
            # Displacement operator
            elem = table.transmissive_plate(current_x, y_position,
                                           size=0.5, angle=0,
                                           label=label,
                                           label_pos='bottom',
                                           colour='#d4a574', textcolour='#f0d9c0')
            optics.append(elem)
            current_x += spacing
            
        elif comp_type == 'squeezing':
            # Squeezing operator
            elem = table.transmissive_plate(current_x, y_position,
                                           size=0.5, angle=0,
                                           label=label,
                                           label_pos='bottom',
                                           colour='#d4a574', textcolour='#f0d9c0')
            optics.append(elem)
            current_x += spacing
            
        elif comp_type == 'measurement' or step_type == 'measurement' or comp_type == 'photon_number' or comp_type == 'homodyne':
            # Detector (angle 0 means facing the beam from the left)
            elem = table.beam_dump(current_x, y_position,
                                  size=0.6, angle=0,
                                  label=label, label_pos='bottom',
                                  colour='#d4a574', textcolour='#f0d9c0')
            optics.append(elem)
            current_x += spacing
    
    # Draw laser beam through all elements
    if len(optics) > 1:
        beam = LaserBeam(colour='#d4a574', width=2)
        beam.draw(table, optics)
    
    # Set dark background
    fig = plt.gcf()
    fig.patch.set_facecolor('#1a1410')
    table.ax.set_facecolor('#1a1410')
    
    # Add title
    table.ax.text(0, 3.5, 'Quantum Optical Setup', 
                 ha='center', va='top', fontsize=16, 
                 color='#f0d9c0', weight='bold')
    
    return fig


def _create_fallback_figure(experiment_dict: Dict[str, Any],
                           figsize: Tuple[int, int],
                           dpi: int) -> plt.Figure:
    """Create simple fallback diagram without PyOpticalTable."""
    
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Set dark warm background
    fig.patch.set_facecolor('#1a1410')
    ax.set_facecolor('#1a1410')
    
    # Title
    ax.text(50, 55, 'Quantum Optical Setup', 
            ha='center', va='top', fontsize=18, color='#f0d9c0', weight='bold')
    
    # Parse and draw components
    steps = experiment_dict.get('steps', [])
    if not steps:
        ax.text(50, 30, 'No components defined', 
                ha='center', va='center', fontsize=14, color='#d4a574')
        return fig
    
    x_start = 10
    y_pos = 30
    spacing = 18
    current_x = x_start
    
    # Draw beam line
    beam_length = spacing * (len(steps) - 1) + 10
    ax.plot([x_start, x_start + beam_length], [y_pos, y_pos], 
            'o-', color='#d4a574', linewidth=3, markersize=8, alpha=0.7)
    
    # Draw components with numbers
    for i, step in enumerate(steps, 1):
        comp_type = step.get('component', {}).get('type', step.get('step_type', ''))
        
        # Component box
        rect = patches.Rectangle((current_x - 3, y_pos - 4), 6, 8,
                                linewidth=2, edgecolor='#d4a574',
                                facecolor='#2d1810', alpha=0.8)
        ax.add_patch(rect)
        
        # Component NUMBER (matches justifications numbering)
        ax.text(current_x, y_pos, str(i), ha='center', va='center',
               fontsize=20, color='#f0d9c0', weight='bold')
        
        current_x += spacing
    
    # Add experiment info
    _add_experiment_info(ax, experiment_dict)
    
    plt.tight_layout()
    return fig


def _get_component_icon(comp_type: str) -> str:
    """Get unicode icon for component type."""
    icons = {
        'state': '🌟',
        'beam_splitter': '⚡',
        'phase_shift': 'φ',
        'displacement': 'D',
        'squeezing': 'S',
        'measurement': '📊'
    }
    return icons.get(comp_type, '◯')


def _get_component_name(comp_type: str) -> str:
    """Get display name for component type."""
    names = {
        'state': 'Source',
        'beam_splitter': 'Beam Splitter',
        'phase_shift': 'Phase Shift',
        'displacement': 'Displacement',
        'squeezing': 'Squeezing',
        'measurement': 'Detector'
    }
    return names.get(comp_type, comp_type.replace('_', ' ').title())


def _add_experiment_info(ax, experiment_dict: Dict[str, Any]):
    """Add experiment information as text annotations."""
    
    description = experiment_dict.get('description', '')
    if description:
        # Wrap text if too long
        if len(description) > 80:
            description = description[:77] + '...'
        ax.text(50, 5, description, ha='center', va='bottom',
               fontsize=11, color='#c0a080', style='italic')
    
    # Add component count
    steps = experiment_dict.get('steps', [])
    ax.text(95, 3, f'Total: {len(steps)} components', 
           fontsize=9, color='#a08060', ha='right')


def test_optical_table():
    """Test function to verify optical table rendering."""
    
    # Sample experiment
    test_experiment = {
        'experiment_id': 'test_001',
        'description': 'Bell state generator with beam splitter',
        'steps': [
            {
                'step_type': 'state',
                'component': {'type': 'state'},
                'description': 'Single photon source |1,0⟩'
            },
            {
                'step_type': 'operation',
                'component': {
                    'type': 'beam_splitter',
                    'parameters': {'transmittance': 0.5, 'phase': 0}
                },
                'description': '50:50 beam splitter'
            },
            {
                'step_type': 'measurement',
                'component': {'type': 'measurement'},
                'description': 'Photon detection'
            }
        ]
    }
    
    fig = create_optical_table_figure(test_experiment)
    plt.savefig('optical_table_test.png', dpi=150, facecolor='#1a1410')
    print("Test diagram saved as optical_table_test.png")
    return fig


if __name__ == '__main__':
    test_optical_table()
