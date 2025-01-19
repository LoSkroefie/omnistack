import pytest
from unittest.mock import Mock, patch
import torch
import numpy as np
from ai_core.context_analyzer import ContextAnalyzer
from ai_core.predictive_debugger import PredictiveDebugger
from ai_core.code_optimizer import CodeOptimizer

@pytest.fixture
def context_analyzer():
    return ContextAnalyzer()

@pytest.fixture
def predictive_debugger():
    return PredictiveDebugger()

@pytest.fixture
def code_optimizer():
    return CodeOptimizer()

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
def sample_error():
    try:
        raise ValueError("Test error")
    except ValueError as e:
        return e

class TestContextAnalyzer:
    async def test_analyze_code_quality(
        self,
        context_analyzer,
        sample_code
    ):
        result = await context_analyzer.analyze_code_quality(sample_code)
        assert isinstance(result, dict)
        assert 'quality_score' in result
        assert 0 <= result['quality_score'] <= 1
    
    async def test_detect_code_smells(
        self,
        context_analyzer,
        sample_code
    ):
        smells = await context_analyzer.detect_code_smells(sample_code)
        assert isinstance(smells, list)
        assert all(isinstance(smell, dict) for smell in smells)
    
    async def test_suggest_improvements(
        self,
        context_analyzer,
        sample_code
    ):
        suggestions = await context_analyzer.suggest_improvements(sample_code)
        assert isinstance(suggestions, list)
        assert all(isinstance(s, str) for s in suggestions)

class TestPredictiveDebugger:
    async def test_analyze_error(
        self,
        predictive_debugger,
        sample_error
    ):
        analysis = await predictive_debugger.analyze_error(sample_error)
        assert isinstance(analysis, dict)
        assert 'error_type' in analysis
        assert 'probability' in analysis
        assert 'suggested_fixes' in analysis
    
    async def test_predict_error_probability(
        self,
        predictive_debugger,
        sample_code
    ):
        prob = await predictive_debugger.predict_error_probability(sample_code)
        assert isinstance(prob, float)
        assert 0 <= prob <= 1
    
    @patch('torch.load')
    async def test_load_model(
        self,
        mock_load,
        predictive_debugger
    ):
        mock_model = Mock()
        mock_load.return_value = mock_model
        
        model = await predictive_debugger.load_model("test_model.pt")
        assert model == mock_model
        mock_load.assert_called_once()

class TestCodeOptimizer:
    async def test_optimize_code(
        self,
        code_optimizer,
        sample_code
    ):
        optimized = await code_optimizer.optimize_code(sample_code)
        assert isinstance(optimized, str)
        assert len(optimized) > 0
    
    async def test_measure_performance(
        self,
        code_optimizer,
        sample_code
    ):
        metrics = await code_optimizer.measure_performance(sample_code)
        assert isinstance(metrics, dict)
        assert 'execution_time' in metrics
        assert 'memory_usage' in metrics
    
    async def test_suggest_optimizations(
        self,
        code_optimizer,
        sample_code
    ):
        suggestions = await code_optimizer.suggest_optimizations(sample_code)
        assert isinstance(suggestions, list)
        assert all(isinstance(s, dict) for s in suggestions)
        assert all('type' in s for s in suggestions)
        assert all('description' in s for s in suggestions)

@pytest.mark.integration
class TestIntegration:
    async def test_end_to_end_analysis(
        self,
        context_analyzer,
        predictive_debugger,
        code_optimizer,
        sample_code
    ):
        # Analyze code quality
        quality = await context_analyzer.analyze_code_quality(sample_code)
        assert quality['quality_score'] >= 0
        
        # Predict errors
        error_prob = await predictive_debugger.predict_error_probability(
            sample_code
        )
        assert 0 <= error_prob <= 1
        
        # Optimize code
        optimized = await code_optimizer.optimize_code(sample_code)
        assert isinstance(optimized, str)
        
        # Verify optimized code quality
        opt_quality = await context_analyzer.analyze_code_quality(optimized)
        assert opt_quality['quality_score'] >= quality['quality_score']

@pytest.mark.performance
class TestPerformance:
    @pytest.mark.parametrize("code_size", [100, 1000, 10000])
    async def test_analyzer_performance(
        self,
        context_analyzer,
        code_size
    ):
        code = "x = 1\n" * code_size
        start_time = time.time()
        await context_analyzer.analyze_code_quality(code)
        duration = time.time() - start_time
        assert duration < code_size * 0.001  # 1ms per line maximum
    
    @pytest.mark.parametrize(
        "batch_size",
        [1, 10, 100]
    )
    async def test_batch_processing(
        self,
        predictive_debugger,
        batch_size
    ):
        codes = ["x = 1"] * batch_size
        start_time = time.time()
        results = await predictive_debugger.batch_analyze(codes)
        duration = time.time() - start_time
        assert len(results) == batch_size
        assert duration < batch_size * 0.1  # 100ms per item maximum
