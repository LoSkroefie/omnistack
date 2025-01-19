import pytest
from ai_core.code_optimizer import CodeOptimizer, OptimizationSuggestion

@pytest.fixture
def optimizer():
    return CodeOptimizer()

@pytest.fixture
def sample_code():
    return """
def process_list(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item * 2)
    return result
    """

def test_optimize_code_basic(optimizer, sample_code):
    suggestions = optimizer.optimize_code(sample_code)
    
    assert isinstance(suggestions, list)
    assert all(isinstance(s, OptimizationSuggestion) for s in suggestions)
    assert len(suggestions) > 0

def test_optimize_code_list_comprehension(optimizer):
    code = """
def square_positives(numbers):
    result = []
    for n in numbers:
        if n > 0:
            result.append(n * n)
    return result
    """
    
    suggestions = optimizer.optimize_code(code)
    
    assert any(
        s.type == "list_comprehension" and
        "list comprehension" in s.description.lower()
        for s in suggestions
    )

def test_optimize_code_generator_expression(optimizer):
    code = """
def process_large_data(items):
    results = []
    for item in items:
        results.append(item.process())
    return results
    """
    
    suggestions = optimizer.optimize_code(code)
    
    assert any(
        s.type == "generator_expression" and
        "generator" in s.description.lower()
        for s in suggestions
    )

def test_optimize_code_complexity(optimizer):
    code = """
def find_pairs(arr):
    n = len(arr)
    for i in range(n):
        for j in range(i + 1, n):
            if arr[i] + arr[j] == 0:
                return (arr[i], arr[j])
    return None
    """
    
    suggestions = optimizer.optimize_code(code)
    
    assert any(
        "complexity" in s.type.lower() and
        s.performance_impact > 0.3
        for s in suggestions
    )

def test_optimize_code_with_context(optimizer, sample_code):
    context = {
        "performance_critical": True,
        "memory_constrained": False
    }
    
    suggestions = optimizer.optimize_code(sample_code, context)
    
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0
    assert all(s.confidence > 0 for s in suggestions)

def test_ast_optimizations(optimizer):
    code = """
def sort_and_process(items):
    # Sort multiple times
    sorted_items = sorted(items)
    result1 = process(sorted_items)
    sorted_again = sorted(items)
    result2 = process(sorted_again)
    return result1, result2
    """
    
    suggestions = optimizer._analyze_ast_optimizations(code)
    
    assert any(
        "caching" in s.description.lower() and
        "sorted" in s.original_code
        for s in suggestions
    )

def test_ml_optimizations(optimizer):
    code = """
def process_data(data):
    intermediate = []
    for item in data:
        if item.is_valid():
            intermediate.append(item.process())
    
    result = []
    for processed in intermediate:
        if processed is not None:
            result.append(processed.optimize())
    return result
    """
    
    suggestions = optimizer._analyze_ml_optimizations(code, None)
    
    assert isinstance(suggestions, list)
    assert all(
        isinstance(s, OptimizationSuggestion) and
        s.confidence > 0
        for s in suggestions
    )

def test_empty_code(optimizer):
    suggestions = optimizer.optimize_code("")
    
    assert isinstance(suggestions, list)
    assert len(suggestions) == 0

def test_syntax_error(optimizer):
    invalid_code = """
    def invalid_function(x:
        return x * 2
    """
    
    suggestions = optimizer.optimize_code(invalid_code)
    
    assert isinstance(suggestions, list)
    assert len(suggestions) == 0

def test_optimize_nested_loops(optimizer):
    code = """
def matrix_multiplication(a, b):
    n = len(a)
    result = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                result[i][j] += a[i][k] * b[k][j]
    return result
    """
    
    suggestions = optimizer.optimize_code(code)
    
    assert any(
        "matrix operation" in s.description.lower() and
        "numpy" in s.optimized_code.lower()
        for s in suggestions
    )
