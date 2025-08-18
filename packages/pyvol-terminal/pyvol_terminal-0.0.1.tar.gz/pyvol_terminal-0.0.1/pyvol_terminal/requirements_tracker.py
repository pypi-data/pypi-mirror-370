from collections import deque, defaultdict
from typing import Dict, List, Set, Tuple, Optional, NamedTuple

class RequirementSpec(NamedTuple):
    """
    Specification for a calculation requirement
    - metric: The financial metric to calculate
    - px_type_option: px type for the option (bid/ask/mid)
    - px_type_underlying: px type for the underlying (bid/ask/mid)
    """
    metric: str
    px_type_option: Optional[str] = None
    px_type_underlying: Optional[str] = None

    def __repr__(self):
        parts = []
        if self.px_type_option:
            parts.append(f"option:{self.px_type_option}")
        if self.px_type_underlying:
            parts.append(f"underlying:{self.px_type_underlying}")
        return f"{self.metric}" + (f" ({', '.join(parts)})" if parts else "")

class RequirementsTracker:
    # Dependency relationships between metrics
    DEPENDENCIES: Dict[str, List[str]] = {
                                        "px": [],
                                        "underlying_px": [],
                                        "ivol": ["px", "underlying_px"],
                                        "delta": ["ivol"],
                                        "gamma": ["ivol"],
                                        "vega": ["ivol"],
                                        "theta": ["ivol"],
                                        "rho": ["ivol"],
                                        "standardised_moneyness": ["ivol"],
                                        "moneyness": ["underlying_px"],
                                        "log_moneyness": ["underlying_px"],
                                        "forward_moneyness": ["underlying_px"],
                                        "OTM": ["underlying_px"],
                                        "valid_px": ["px"]
                                    }
    
    # Metrics that use option px type
    OPTION_px_METRICS = {"px",
                        "ivol",
                        "delta",
                        "gamma",
                        "vega",
                        "theta",
                        "rho", 
                        "standardised_moneyness",
                        "valid_px"
                        }
    
    # Metrics that use underlying px type
    UNDERLYING_px_METRICS = {"underlying_px", "ivol", "delta", "gamma", "vega", "theta", 
                               "rho", "standardised_moneyness", "moneyness", "log_moneyness", 
                               "forward_moneyness", "OTM"}

    def __init__(self):
        """Initialize with empty requirements"""
        # Tracks all requirements including dependencies
        self.current_requirements: Set[RequirementSpec] = set()
        
        # Tracks explicitly added requirements
        self.explicit_requirements: Set[RequirementSpec] = set()
        
        # Tracks requirements by metric
        self.requirements_by_metric: Dict[str, Set[RequirementSpec]] = defaultdict(set)

    def add_interface_requirement(self, requirement: RequirementSpec):
        """
        Add a requirement for a specific interface
        Resolves and stores all necessary dependencies
        """
        self.explicit_requirements.add(requirement)
        
        # BFS to resolve dependencies
        queue = deque([requirement])
        visited = set()
        
        while queue:
            current = queue.popleft()
            
            # Skip already processed requirements
            if current in visited:
                continue
            visited.add(current)
            
            # Add to current requirements if new
            if current not in self.current_requirements:
                self.current_requirements.add(current)
                self.requirements_by_metric[current.metric].add(current)
                
                # Process dependencies
                for dep_metric in self.DEPENDENCIES.get(current.metric, []):
                    # Create dependency requirement with inherited px types
                    dep_req = self._create_dependency_requirement(
                        dep_metric, 
                        current.px_type_option,
                        current.px_type_underlying
                    )
                    queue.append(dep_req)

    def _create_dependency_requirement(self, metric: str, 
                                       option_pt: Optional[str], 
                                       underlying_pt: Optional[str]
                                       ) -> RequirementSpec:
        """Create requirement for a dependency with inherited px types"""
        # Inherit option px type if metric uses it
        inherit_option_pt = option_pt if metric in self.OPTION_px_METRICS else None
        
        # Inherit underlying px type if metric uses it
        inherit_underlying_pt = underlying_pt if metric in self.UNDERLYING_px_METRICS else None
        
        return RequirementSpec(metric=metric,
                               px_type_option=inherit_option_pt,
                               px_type_underlying=inherit_underlying_pt
                               )

    def remove_interface_requirement(self, requirement: RequirementSpec):
        """
        Remove a requirement and its dependencies
        (if not used by other requirements)
        """
        if requirement not in self.explicit_requirements:
            return
            
        self.explicit_requirements.remove(requirement)
        
        # Find all requirements to remove
        to_remove = set()
        queue = deque([requirement])
        
        while queue:
            current = queue.popleft()
            to_remove.add(current)
            
            # Find dependencies that might be removable
            for dep_metric in self.DEPENDENCIES.get(current.metric, []):
                # Get all possible dependency requirements
                for dep_req in self.requirements_by_metric.get(dep_metric, set()):
                    # Check if this dependency is only used by the current requirement
                    if all(
                        req in to_remove 
                        for req in self.current_requirements 
                        if dep_req in self._get_dependencies(req)
                    ):
                        queue.append(dep_req)
        
        # Remove identified requirements
        for req in to_remove:
            self.current_requirements.discard(req)
            self.requirements_by_metric[req.metric].discard(req)
            # Clean up empty metric entries
            if not self.requirements_by_metric[req.metric]:
                del self.requirements_by_metric[req.metric]

    def _get_dependencies(self, requirement: RequirementSpec) -> Set[RequirementSpec]:
        """Get direct dependencies for a requirement"""
        dependencies = set()
        for dep_metric in self.DEPENDENCIES.get(requirement.metric, []):
            dep_req = self._create_dependency_requirement(
                dep_metric,
                requirement.px_type_option,
                requirement.px_type_underlying
            )
            dependencies.add(dep_req)
        return dependencies

    def get_current_requirements(self) -> Set[RequirementSpec]:
        """Get all current requirements including dependencies"""
        return self.current_requirements.copy()

    def get_explicit_requirements(self) -> Set[RequirementSpec]:
        """Get requirements explicitly added for interfaces"""
        return self.explicit_requirements.copy()

    def get_requirements_for_metric(self, metric: str) -> Set[RequirementSpec]:
        """Get all requirements for a specific metric"""
        return self.requirements_by_metric.get(metric, set()).copy()

    def get_required_px_types(self) -> Dict[str, Set[str]]:
        """Get required px types by metric type"""
        px_types = {
            "option": set(),
            "underlying": set()
        }
        
        for req in self.current_requirements:
            if req.px_type_option:
                px_types["option"].add(req.px_type_option)
            if req.px_type_underlying:
                px_types["underlying"].add(req.px_type_underlying)
                
        return px_types

    def clear_all_requirements(self):
        """Reset all requirements"""
        self.current_requirements = set()
        self.explicit_requirements = set()
        self.requirements_by_metric = defaultdict(set)

    def __repr__(self):
        return f"RequirementsTracker({len(self.current_requirements)} requirements)"