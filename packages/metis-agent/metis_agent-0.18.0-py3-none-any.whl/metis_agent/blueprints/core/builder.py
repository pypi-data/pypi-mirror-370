#!/usr/bin/env python3
"""
Blueprint Builder - Dynamic Blueprint Creation

This module provides the BlueprintBuilder class for dynamically
creating blueprints in the Metis Agent framework.
"""

from typing import Dict, Any, List, Optional
from .blueprint import Blueprint, BlueprintStep, BlueprintInput, BlueprintOutput


class BlueprintBuilder:
    """
    Blueprint builder for dynamic workflow creation.
    
    This class provides a fluent interface for building
    blueprints programmatically.
    """
    
    def __init__(self, name: str):
        """
        Initialize the blueprint builder.
        
        Args:
            name: Name of the blueprint being built
        """
        self.blueprint = Blueprint()
        self.blueprint.metadata.name = name
    
    def description(self, desc: str) -> 'BlueprintBuilder':
        """Set blueprint description."""
        self.blueprint.metadata.description = desc
        return self
    
    def version(self, ver: str) -> 'BlueprintBuilder':
        """Set blueprint version."""
        self.blueprint.metadata.version = ver
        return self
    
    def add_input(self, name: str, input_type: str = "string", 
                  required: bool = True, default: Any = None,
                  description: str = "") -> 'BlueprintBuilder':
        """Add an input parameter."""
        input_param = BlueprintInput(
            name=name,
            type=input_type,
            required=required,
            default=default,
            description=description
        )
        self.blueprint.inputs.append(input_param)
        return self
    
    def add_step(self, step_id: str, tool: str, action: str = "execute",
                 inputs: Optional[Dict[str, Any]] = None,
                 outputs: Optional[Dict[str, str]] = None,
                 depends_on: Optional[List[str]] = None) -> 'BlueprintBuilder':
        """Add a step to the blueprint."""
        step = BlueprintStep(
            id=step_id,
            tool=tool,
            action=action,
            inputs=inputs or {},
            outputs=outputs or {},
            depends_on=depends_on or []
        )
        self.blueprint.steps.append(step)
        return self
    
    def build(self) -> Blueprint:
        """Build and return the completed blueprint."""
        # Validate the blueprint
        errors = self.blueprint.validate()
        if errors:
            raise ValueError(f"Blueprint validation failed: {errors}")
        
        return self.blueprint
