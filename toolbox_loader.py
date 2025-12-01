"""
Toolbox loader for quantum optical components.
Loads both primitive components and learned composite building blocks.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ToolboxLoader:
    """
    Manages loading and accessing optical component toolbox.
    - Primitives: Hard-coded basic components (never modified)
    - Learned Composites: User-approved designs that become reusable blocks
    """
    
    def __init__(self, toolbox_dir: str = "./toolbox"):
        self.toolbox_dir = Path(toolbox_dir)
        self.primitives_path = self.toolbox_dir / "primitives.json"
        self.composites_path = self.toolbox_dir / "learned_composites.json"
        self.custom_components_path = self.toolbox_dir / "custom_components.json"
        
        self.primitives = self._load_primitives()
        self.composites = self._load_composites()
        self.custom_components = self._load_custom_components()
        
    def _load_primitives(self) -> Dict:
        """Load hard-coded primitive components."""
        try:
            with open(self.primitives_path, 'r') as f:
                data = json.load(f)
            logger.info(f"✓ Loaded {self._count_primitives(data)} primitive components")
            return data
        except Exception as e:
            logger.error(f"Failed to load primitives: {e}")
            return {}
    
    def _load_composites(self) -> Dict:
        """Load user-approved learned composite blocks."""
        try:
            with open(self.composites_path, 'r') as f:
                data = json.load(f)
            count = data.get('_total_composites', 0)
            if count > 0:
                logger.info(f"✓ Loaded {count} learned composite blocks")
            return data
        except Exception as e:
            logger.error(f"Failed to load composites: {e}")
            return {"composites": {}, "_total_composites": 0}
    
    def _load_custom_components(self) -> Dict:
        """Load custom components defined by LLM for non-standard equipment."""
        try:
            if self.custom_components_path.exists():
                with open(self.custom_components_path, 'r') as f:
                    data = json.load(f)
                count = len(data.get('components', {}))
                if count > 0:
                    logger.info(f"✓ Loaded {count} custom components")
                return data
            else:
                # Create empty file if doesn't exist
                default_data = {
                    "components": {},
                    "_description": "Custom components defined by LLM for specialized equipment not in standard library",
                    "_total_custom": 0
                }
                self.custom_components_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.custom_components_path, 'w') as f:
                    json.dump(default_data, f, indent=2)
                return default_data
        except Exception as e:
            logger.error(f"Failed to load custom components: {e}")
            return {"components": {}, "_total_custom": 0}
    
    def _count_primitives(self, primitives: Dict) -> int:
        """Count total primitive components across all categories."""
        count = 0
        for key, value in primitives.items():
            if key.startswith('_'):  # Skip metadata
                continue
            if isinstance(value, dict):
                count += len([k for k in value.keys() if not k.startswith('_')])
        return count
    
    def get_primitives_for_llm(self) -> str:
        """
        Format primitives as comprehensive list for LLM prompts.
        Returns the type names organized by category.
        """
        lines = ["**Available Primitive Components:**\n"]
        
        for category, components in self.primitives.items():
            if category.startswith('_'):  # Skip metadata
                continue
            
            # Convert category name to readable form
            category_name = category.replace('_', ' ').title()
            lines.append(f"\n**{category_name}:**")
            
            for comp_type, comp_info in components.items():
                if isinstance(comp_info, dict) and 'name' in comp_info:
                    name = comp_info['name']
                    desc = comp_info.get('description', '')
                    lines.append(f"  • `{comp_type}` - {name}: {desc}")
        
        return '\n'.join(lines)
    
    def get_composites_for_llm(self) -> str:
        """
        Format learned composites as list for LLM.
        Returns summary of available composite blocks.
        """
        composites = self.composites.get('composites', {})
        
        if not composites:
            return "\n**Learned Composite Blocks:** None yet (designs will appear here after user approval)\n"
        
        lines = ["\n**Learned Composite Blocks (User-Approved Designs):**\n"]
        lines.append("These are complete experimental setups that you can reference or reuse:\n")
        
        for comp_id, comp_data in composites.items():
            name = comp_data.get('name', comp_id)
            desc = comp_data.get('description', 'No description')
            use_case = comp_data.get('typical_use', '')
            lines.append(f"  • **{name}** (`{comp_id}`)")
            lines.append(f"    Description: {desc}")
            if use_case:
                lines.append(f"    Use when: {use_case}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def get_full_toolbox_for_llm(self) -> str:
        """
        Get complete toolbox description for LLM prompts.
        Includes primitives, learned composites, and custom components.
        """
        primitives_text = self.get_primitives_for_llm()
        composites_text = self.get_composites_for_llm()
        custom_text = self.get_custom_components_for_llm()
        
        if custom_text:
            return f"{primitives_text}\n\n{composites_text}\n\n{custom_text}"
        else:
            return f"{primitives_text}\n\n{composites_text}"
    
    def get_custom_components_for_llm(self) -> str:
        """Format custom components library for LLM prompt."""
        custom_data = self.custom_components.get('components', {})
        
        if not custom_data:
            return ""
        
        text = "**Previously Defined Custom Components:**\n"
        text += "These specialized components have been defined in past designs. You can reuse them instead of redefining:\n\n"
        
        for comp_id, comp_info in custom_data.items():
            name = comp_info.get('name', comp_id)
            description = comp_info.get('description', 'No description')
            usage_count = comp_info.get('usage_count', 1)
            last_used = comp_info.get('last_used', 'Unknown')
            
            text += f"• `{comp_id}` - {name}\n"
            text += f"  Description: {description}\n"
            text += f"  Used {usage_count} time(s), Last: {last_used.split('T')[0] if 'T' in last_used else last_used}\n\n"
        
        return text
    
    def add_custom_component(self,
                            component_type: str,
                            name: str,
                            description: str,
                            parameters: Dict = None) -> bool:
        """
        Add or update a custom component in the library.
        
        Args:
            component_type: Type identifier (e.g., "custom_coincidence_counter")
            name: Human-readable name
            description: What this component does
            parameters: Additional parameters/specifications
        
        Returns:
            True if successfully added/updated
        """
        try:
            # Load current custom components
            custom_data = self.custom_components
            
            if component_type in custom_data['components']:
                # Update existing - increment usage count
                custom_data['components'][component_type]['usage_count'] += 1
                custom_data['components'][component_type]['last_used'] = datetime.now().isoformat()
                logger.info(f"Updated custom component: {component_type} (usage: {custom_data['components'][component_type]['usage_count']})")
            else:
                # Add new custom component
                custom_entry = {
                    "name": name,
                    "description": description,
                    "added_date": datetime.now().isoformat(),
                    "last_used": datetime.now().isoformat(),
                    "usage_count": 1,
                    "parameters": parameters or {}
                }
                custom_data['components'][component_type] = custom_entry
                logger.info(f"Added new custom component: {component_type}")
            
            # Update metadata
            custom_data['_total_custom'] = len(custom_data['components'])
            custom_data['_last_updated'] = datetime.now().isoformat()
            
            # Save to file
            with open(self.custom_components_path, 'w') as f:
                json.dump(custom_data, f, indent=2)
            
            # Reload in memory
            self.custom_components = custom_data
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add custom component {component_type}: {e}")
            return False
    
    def add_learned_composite(self, 
                             composite_id: str,
                             name: str,
                             description: str,
                             components: List[Dict],
                             beam_path: Any,
                             physics_explanation: str,
                             typical_use: str,
                             full_design: Dict) -> bool:
        """
        Add a new learned composite block (called when user approves design).
        
        Args:
            composite_id: Unique identifier (e.g., "hom_interferometer_001")
            name: Human-readable name
            description: One-sentence description
            components: List of component dicts from the design
            beam_path: Beam path(s) from the design
            physics_explanation: Physics explanation
            typical_use: When to use this composite block
            full_design: Complete design dict for reference
        
        Returns:
            True if successfully added
        """
        try:
            # Load current composites
            composites_data = self._load_composites()
            
            # Create composite entry
            composite_entry = {
                "name": name,
                "type": "learned_composite",
                "approved_date": datetime.now().isoformat(),
                "description": description,
                "components": components,
                "beam_path": beam_path,
                "physics_explanation": physics_explanation,
                "typical_use": typical_use,
                "num_components": len(components),
                "full_design": full_design
            }
            
            # Add to composites
            composites_data['composites'][composite_id] = composite_entry
            composites_data['_total_composites'] = len(composites_data['composites'])
            composites_data['_last_updated'] = datetime.now().isoformat()
            
            # Save to file
            with open(self.composites_path, 'w') as f:
                json.dump(composites_data, f, indent=2)
            
            # Reload in memory
            self.composites = composites_data
            
            logger.info(f"✓ Added learned composite: {name} ({composite_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add learned composite: {e}")
            return False
    
    def get_composite(self, composite_id: str) -> Dict:
        """Get full details of a specific learned composite."""
        return self.composites.get('composites', {}).get(composite_id, {})
    
    def list_all_composites(self) -> List[Dict]:
        """Get list of all learned composites with basic info."""
        composites = self.composites.get('composites', {})
        return [
            {
                'id': comp_id,
                'name': comp_data.get('name', ''),
                'description': comp_data.get('description', ''),
                'approved_date': comp_data.get('approved_date', ''),
                'num_components': comp_data.get('num_components', 0)
            }
            for comp_id, comp_data in composites.items()
        ]
    
    def delete_composite(self, composite_id: str) -> bool:
        """Delete a specific learned composite."""
        try:
            composites_data = self.composites
            if composite_id in composites_data.get('composites', {}):
                del composites_data['composites'][composite_id]
                composites_data['_total_composites'] = len(composites_data['composites'])
                composites_data['_last_updated'] = datetime.now().isoformat()
                
                # Save to file
                with open(self.composites_path, 'w') as f:
                    json.dump(composites_data, f, indent=2)
                
                # Reload in memory
                self.composites = composites_data
                logger.info(f"✓ Deleted composite: {composite_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete composite: {e}")
            return False
    
    def clear_all_composites(self) -> bool:
        """Clear all learned composites (empty the toolbox)."""
        try:
            composites_data = {
                '_version': '1.0',
                '_total_composites': 0,
                '_last_updated': datetime.now().isoformat(),
                'composites': {}
            }
            
            # Save to file
            with open(self.composites_path, 'w') as f:
                json.dump(composites_data, f, indent=2)
            
            # Reload in memory
            self.composites = composites_data
            logger.info(f"✓ Cleared all composites")
            return True
        except Exception as e:
            logger.error(f"Failed to clear composites: {e}")
            return False


# Global instance for easy access
_toolbox_loader = None

def get_toolbox() -> ToolboxLoader:
    """Get global toolbox loader instance (singleton pattern)."""
    global _toolbox_loader
    if _toolbox_loader is None:
        _toolbox_loader = ToolboxLoader()
    return _toolbox_loader


def reload_toolbox():
    """Force reload of toolbox (useful after adding new composites)."""
    global _toolbox_loader
    _toolbox_loader = ToolboxLoader()
    return _toolbox_loader
