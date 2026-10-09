"""Base class and registry for property calculators."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


class CalculatorResult:
    """Container for calculator output."""
    def __init__(self):
        self.values: Dict[str, float] = {}       # scalar results
        self.text: List[str] = []                # textual conclusions
        self.figure: Optional[Figure] = None     # plot (matplotlib Figure)

    def add_value(self, name: str, value: float, unit: str = ""):
        self.values[name] = (value, unit)

    def add_text(self, msg: str):
        self.text.append(msg)


class BaseCalculator(ABC):
    """Every property module must inherit from this."""
    name: str = "Unnamed"
    description: str = ""
    required_inputs: List[str] = []   # parameter names needed
    example_inputs: Dict[str, float] = {}
    expected_summary: str = ""  # For validation by non-experts

    @abstractmethod
    def calculate(self, params: Dict[str, float]) -> CalculatorResult:
        ...

    def validate(self, params: Dict[str, float]) -> bool:
        return all(k in params for k in self.required_inputs)


# Global registry — calculators register themselves here
REGISTRY: Dict[str, BaseCalculator] = {}


def register(calc_cls):
    """Decorator to auto-register a calculator."""
    instance = calc_cls()
    REGISTRY[instance.name] = instance
    return calc_cls
