import pytest
from ai_core.predictive_debugger import PredictiveDebugger, DebugIssue

@pytest.fixture
def debugger():
    return PredictiveDebugger()

@pytest.fixture
def sample_code():
    return """
def process_data(data):
    try:
        result = []
        for item in data:
            if item is "test":  # Using 'is' instead of '=='
                result.append(item.upper())
    except:  # Bare except clause
        pass
    return result
    """

def test_analyze_code_basic(debugger, sample_code):
    issues = debugger.analyze_code(sample_code)
    
    assert isinstance(issues, list)
    assert all(isinstance(issue, DebugIssue) for issue in issues)
    assert len(issues) > 0

def test_analyze_code_syntax_error(debugger):
    invalid_code = """
    def invalid_function(x:
        return x + 1
    """
    
    issues = debugger.analyze_code(invalid_code)
    
    assert isinstance(issues, list)
    assert any(
        issue.severity == "error" and "syntax" in issue.message.lower()
        for issue in issues
    )

def test_analyze_code_with_context(debugger, sample_code):
    context = {
        "file_history": ["previous_version.py"],
        "language": "python",
        "environment": "development"
    }
    
    issues = debugger.analyze_code(sample_code, context)
    
    assert isinstance(issues, list)
    assert len(issues) > 0

def test_static_analysis(debugger):
    code_with_issues = """
def example():
    try:
        value = 1 / 0
    except:
        pass
    
    if value is 1:
        return True
    """
    
    issues = debugger._static_analysis(code_with_issues)
    
    assert isinstance(issues, list)
    assert any(
        issue.severity == "warning" and "bare except" in issue.message.lower()
        for issue in issues
    )
    assert any(
        issue.severity == "warning" and "'is' comparison" in issue.message.lower()
        for issue in issues
    )

def test_ml_prediction(debugger):
    code = """
def complex_function(x, y):
    if x is None or y is None:
        return None
    return x + y
    """
    
    issues = debugger._ml_prediction(code, None)
    
    assert isinstance(issues, list)
    assert all(
        isinstance(issue, DebugIssue) and 0 <= issue.confidence <= 1
        for issue in issues
    )

def test_pattern_analysis(debugger):
    code_with_pattern = """
def search(items, target):
    for i in range(len(items)):
        if items[i] == target:
            return i
    return -1
    """
    
    issues = debugger._pattern_analysis(code_with_pattern)
    
    assert isinstance(issues, list)
    # Should suggest using 'enumerate' or 'in' operator
    assert any(
        "enumerate" in issue.suggestion.lower() or
        "in operator" in issue.suggestion.lower()
        for issue in issues
    )

def test_empty_code(debugger):
    issues = debugger.analyze_code("")
    
    assert isinstance(issues, list)
    assert len(issues) == 0

def test_complex_code_analysis(debugger):
    complex_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def binary_search(arr, target):
    if not arr:
        return -1
    
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
    """
    
    issues = debugger.analyze_code(complex_code)
    
    assert isinstance(issues, list)
    assert len(issues) > 0
    # Should identify O(n²) complexity in bubble_sort
    assert any(
        "complexity" in issue.message.lower() and
        issue.severity in ["warning", "info"]
        for issue in issues
    )
