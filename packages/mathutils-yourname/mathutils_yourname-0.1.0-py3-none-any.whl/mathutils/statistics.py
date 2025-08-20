"""
Statistical functions
"""
from collections import Counter
import math


def mean(numbers):
    """
    Calculate the arithmetic mean of a list of numbers.
    
    Args:
        numbers (list): List of numbers
        
    Returns:
        float: Arithmetic mean
        
    Raises:
        ValueError: If the list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate mean of empty list")
    return sum(numbers) / len(numbers)


def median(numbers):
    """
    Calculate the median of a list of numbers.
    
    Args:
        numbers (list): List of numbers
        
    Returns:
        float: Median value
        
    Raises:
        ValueError: If the list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate median of empty list")
    
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    
    if n % 2 == 0:
        return (sorted_numbers[n//2 - 1] + sorted_numbers[n//2]) / 2
    else:
        return sorted_numbers[n//2]


def mode(numbers):
    """
    Calculate the mode of a list of numbers.
    
    Args:
        numbers (list): List of numbers
        
    Returns:
        list: List of most frequent values
        
    Raises:
        ValueError: If the list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate mode of empty list")
    
    counter = Counter(numbers)
    max_count = max(counter.values())
    return [num for num, count in counter.items() if count == max_count]


def standard_deviation(numbers, sample=True):
    """
    Calculate the standard deviation of a list of numbers.
    
    Args:
        numbers (list): List of numbers
        sample (bool): If True, calculate sample standard deviation (n-1),
                      if False, calculate population standard deviation (n)
        
    Returns:
        float: Standard deviation
        
    Raises:
        ValueError: If the list is empty or has only one element when sample=True
    """
    if not numbers:
        raise ValueError("Cannot calculate standard deviation of empty list")
    
    if sample and len(numbers) == 1:
        raise ValueError("Cannot calculate sample standard deviation with only one data point")
    
    avg = mean(numbers)
    variance = sum((x - avg) ** 2 for x in numbers)
    
    if sample:
        variance /= (len(numbers) - 1)
    else:
        variance /= len(numbers)
    
    return math.sqrt(variance)