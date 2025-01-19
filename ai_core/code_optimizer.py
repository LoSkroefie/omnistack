from typing import Dict, List, Optional, Tuple
import ast
import astor
from dataclasses import dataclass
import numpy as np
from transformers import AutoTokenizer, AutoModel

@dataclass
class OptimizationSuggestion:
    type: str
    description: str
    original_code: str
    optimized_code: str
    performance_impact: float
    confidence: float

class CodeOptimizer:
    def __init__(self, model_name: str = "microsoft/codebert-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()

    def optimize_code(
        self,
        code: str,
        context: Optional[Dict] = None
    ) -> List[OptimizationSuggestion]:
        """
        Analyze and optimize code for better performance and efficiency.
        """
        suggestions = []
        
        # Perform AST-based optimization analysis
        ast_suggestions = self._analyze_ast_optimizations(code)
        suggestions.extend(ast_suggestions)
        
        # Perform ML-based optimization analysis
        ml_suggestions = self._analyze_ml_optimizations(code, context)
        suggestions.extend(ml_suggestions)
        
        # Analyze algorithm complexity
        complexity_suggestions = self._analyze_complexity(code)
        suggestions.extend(complexity_suggestions)
        
        return suggestions

    def _analyze_ast_optimizations(
        self,
        code: str
    ) -> List[OptimizationSuggestion]:
        """Analyze code using AST for optimization opportunities."""
        suggestions = []
        try:
            tree = ast.parse(code)
            optimizer = ASTOptimizer()
            optimizer.visit(tree)
            suggestions.extend(optimizer.suggestions)
        except SyntaxError:
            pass
        return suggestions

    def _analyze_ml_optimizations(
        self,
        code: str,
        context: Optional[Dict]
    ) -> List[OptimizationSuggestion]:
        """Use ML models to suggest code optimizations."""
        suggestions = []
        
        # Tokenize code
        inputs = self.tokenizer(
            code,
            return_tensors="np",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        # Get embeddings
        outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state.mean(axis=1)
        
        # Analyze patterns for optimization opportunities
        patterns = self._identify_optimization_patterns(embeddings)
        
        for pattern in patterns:
            if pattern.confidence > 0.7:
                suggestions.append(
                    OptimizationSuggestion(
                        type=pattern.type,
                        description=pattern.description,
                        original_code=pattern.original,
                        optimized_code=pattern.optimized,
                        performance_impact=pattern.impact,
                        confidence=pattern.confidence
                    )
                )
        
        return suggestions
    
    def _analyze_complexity(self, code: str) -> List[OptimizationSuggestion]:
        """Analyze code complexity and suggest optimizations."""
        suggestions = []
        try:
            tree = ast.parse(code)
            analyzer = ComplexityAnalyzer()
            analyzer.visit(tree)
            suggestions.extend(analyzer.suggestions)
        except SyntaxError:
            pass
        return suggestions
    
    def _identify_optimization_patterns(
        self,
        embeddings: np.ndarray
    ) -> List[Dict]:
        """Identify common optimization patterns."""
        patterns = []
        
        # Example patterns (to be expanded)
        pattern_templates = [
            {
                "type": "loop_optimization",
                "description": "Convert nested loops to vectorized operations",
                "confidence_threshold": 0.8
            },
            {
                "type": "memory_optimization",
                "description": "Optimize memory usage with generators",
                "confidence_threshold": 0.75
            },
            {
                "type": "algorithm_optimization",
                "description": "Use more efficient algorithm",
                "confidence_threshold": 0.85
            }
        ]
        
        # Calculate pattern scores using embeddings
        for template in pattern_templates:
            score = np.mean(embeddings)  # Simplified scoring
            if score > template["confidence_threshold"]:
                patterns.append({
                    "type": template["type"],
                    "description": template["description"],
                    "confidence": float(score)
                })
        
        return patterns

class ASTOptimizer(ast.NodeVisitor):
    def __init__(self):
        self.suggestions = []
        
    def visit_For(self, node):
        """Analyze for loops for optimization opportunities."""
        # Check if loop can be converted to list comprehension
        if isinstance(node.target, ast.Name) and isinstance(node.body, list) and len(node.body) == 1:
            if isinstance(node.body[0], ast.Assign):
                self.suggestions.append(
                    OptimizationSuggestion(
                        type="list_comprehension",
                        description="Convert loop to list comprehension",
                        original_code=astor.to_source(node),
                        optimized_code="[... for ... in ...]",  # Placeholder
                        performance_impact=0.2,
                        confidence=0.8
                    )
                )
        self.generic_visit(node)

class ComplexityAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.suggestions = []
        self.loop_depth = 0
        
    def visit_For(self, node):
        """Analyze nested loops for complexity issues."""
        self.loop_depth += 1
        if self.loop_depth > 2:
            self.suggestions.append(
                OptimizationSuggestion(
                    type="complexity",
                    description="Nested loops detected. Consider optimizing algorithm",
                    original_code=astor.to_source(node),
                    optimized_code="# Consider using more efficient data structures or algorithms",
                    performance_impact=0.5,
                    confidence=0.9
                )
            )
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_Call(self, node):
        """Analyze function calls for potential optimizations."""
        if isinstance(node.func, ast.Name):
            if node.func.id in ['sorted', 'sort']:
                self.suggestions.append(
                    OptimizationSuggestion(
                        type="sorting",
                        description="Consider caching sorted results if used multiple times",
                        original_code=astor.to_source(node),
                        optimized_code="sorted_result = sorted(...)",
                        performance_impact=0.3,
                        confidence=0.7
                    )
                )
        self.generic_visit(node)
