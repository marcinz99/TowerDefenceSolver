"""
Utility for different enemy health functions
"""
import numpy as np


# Functions defining enemy health
def spawn1(iteration: int) -> int:
    """Basic linear spawning function"""
    return 4 * iteration


def spawn2(iteration: int) -> int:
    """Custom spawning function"""
    return int(np.abs(10 * iteration + 20 * np.sin(iteration)))


# Non-deterministic functions
def spawn3(iteration: int) -> int:
    """Custom spawning function"""
    return int(np.abs(np.random.normal(10 * iteration, iteration / 10)))


def spawn4(iteration: int) -> int:
    """Custom spawning function"""
    return int(np.abs(np.random.normal(15 * iteration, 20)))


def spawn5(iteration: int) -> int:
    """Custom spawning function"""
    return int(np.sqrt(100 * iteration))
