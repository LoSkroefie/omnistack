import pytest
import torch
from ai_core.context_analyzer import ContextAnalyzer

@pytest.fixture
def context_analyzer():
    return ContextAnalyzer()

@pytest.fixture
def sample_code():
    return """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
    """

@pytest.fixture
def project_files():
    return [
        "main.py",
        "utils.py",
        "tests/test_main.py"
    ]

def test_analyze_code_context(context_analyzer, sample_code, project_files):
    result = context_analyzer.analyze_code_context(
        sample_code,
        project_files
    )
    
    assert isinstance(result, dict)
    assert "code_quality_score" in result
    assert "potential_issues" in result
    assert "optimization_suggestions" in result
    assert "related_patterns" in result
    
    assert 0 <= result["code_quality_score"] <= 1

def test_analyze_code_context_with_empty_code(context_analyzer):
    result = context_analyzer.analyze_code_context("", [])
    
    assert isinstance(result, dict)
    assert result["code_quality_score"] <= 0.5

def test_analyze_code_context_with_complex_code(context_analyzer):
    complex_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
    """
    
    result = context_analyzer.analyze_code_context(complex_code, [])
    
    assert isinstance(result, dict)
    assert len(result["potential_issues"]) > 0
    assert any(
        issue for issue in result["potential_issues"]
        if "complexity" in issue.get("type", "").lower()
    )

@pytest.mark.asyncio
async def test_analyze_code_context_async(context_analyzer, sample_code):
    with torch.no_grad():
        result = context_analyzer.analyze_code_context(sample_code, [])
    
    assert isinstance(result, dict)
    assert "code_quality_score" in result

def test_analyze_code_context_with_syntax_error(context_analyzer):
    invalid_code = """
    def invalid_function(
        print("Missing closing parenthesis"
    """
    
    result = context_analyzer.analyze_code_context(invalid_code, [])
    
    assert isinstance(result, dict)
    assert result["code_quality_score"] < 0.5
    assert any(
        issue for issue in result["potential_issues"]
        if "syntax" in issue.get("type", "").lower()
    )

def test_analyze_code_context_with_file_context(
    context_analyzer,
    sample_code
):
    file_context = {
        "main.py": """
def main():
    numbers = [1, 2, 3, 4, 5]
    result = calculate_sum(numbers)
    print(result)
        """
    }
    
    result = context_analyzer.analyze_code_context(
        sample_code,
        ["main.py"],
        file_context
    )
    
    assert isinstance(result, dict)
    assert len(result["related_patterns"]) > 0
