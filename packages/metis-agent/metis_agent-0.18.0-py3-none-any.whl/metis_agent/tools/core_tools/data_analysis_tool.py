from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import re
import time
import json
import statistics
import math
from collections import Counter, defaultdict
from ..base import BaseTool

class DataAnalysisTool(BaseTool):
    """Production-ready data analysis tool with intelligent task detection.
    
    This tool performs comprehensive data analysis including statistical analysis,
    data summarization, trend analysis, correlation analysis, and data visualization
    recommendations across various data types and formats.
    """
    
    def __init__(self):
        """Initialize data analysis tool with required attributes."""
        # Required attributes
        self.name = "DataAnalysisTool"
        self.description = "Performs comprehensive data analysis including statistics, trends, correlations, and insights generation"
        
        # Optional metadata
        self.version = "2.0.0"
        self.category = "core_tools"
        
        # Supported analysis types
        self.analysis_types = {
            'descriptive': {
                'keywords': ['describe', 'summary', 'overview', 'basic stats', 'descriptive'],
                'operations': ['mean', 'median', 'mode', 'standard_deviation', 'variance', 'range']
            },
            'statistical': {
                'keywords': ['statistics', 'statistical', 'hypothesis', 'significance', 'p-value'],
                'operations': ['correlation', 'regression', 'distribution', 'confidence_interval']
            },
            'trend': {
                'keywords': ['trend', 'pattern', 'time series', 'growth', 'decline', 'seasonal'],
                'operations': ['moving_average', 'growth_rate', 'seasonality', 'forecasting']
            },
            'comparative': {
                'keywords': ['compare', 'comparison', 'versus', 'difference', 'relative'],
                'operations': ['group_comparison', 'variance_analysis', 'ranking']
            },
            'distribution': {
                'keywords': ['distribution', 'histogram', 'frequency', 'percentile', 'quartile'],
                'operations': ['frequency_analysis', 'percentile_calculation', 'outlier_detection']
            },
            'correlation': {
                'keywords': ['correlation', 'relationship', 'association', 'dependence'],
                'operations': ['pearson_correlation', 'spearman_correlation', 'cross_correlation']
            }
        }
        
        # Data format detection patterns
        self.data_formats = {
            'csv': [r'\.csv', r'comma.separated', r'delimiter'],
            'json': [r'\.json', r'\{.*\}', r'javascript object'],
            'numeric_list': [r'\[[\d\s,\.]+\]', r'numbers?.*list'],
            'table': [r'table', r'rows? and columns?', r'spreadsheet'],
            'time_series': [r'time series', r'temporal', r'date.*data'],
            'categorical': [r'categories', r'groups?', r'classes']
        }
        
        # Statistical functions mapping
        self.stat_functions = {
            'mean': statistics.mean,
            'median': statistics.median,
            'mode': lambda x: statistics.mode(x) if x else None,
            'stdev': statistics.stdev,
            'variance': statistics.variance,
            'min': min,
            'max': max,
            'sum': sum,
            'count': len
        }
        
        # Analysis operation types
        self.operation_types = {
            'analyze': ['analyze', 'analysis', 'examine', 'study', 'investigate'],
            'calculate': ['calculate', 'compute', 'determine', 'find'],
            'compare': ['compare', 'contrast', 'versus', 'difference'],
            'summarize': ['summarize', 'summary', 'overview', 'aggregate'],
            'visualize': ['plot', 'chart', 'graph', 'visualize', 'display'],
            'predict': ['predict', 'forecast', 'project', 'estimate']
        }
        
        # Common data quality indicators
        self.quality_checks = [
            'missing_values',
            'duplicates',
            'outliers',
            'data_types',
            'completeness',
            'consistency'
        ]
    
    def can_handle(self, task: str) -> bool:
        """Intelligent data analysis task detection.
        
        Uses multi-layer analysis to determine if a task requires
        data analysis capabilities.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task requires data analysis, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_lower = task.strip().lower()
        
        # Early exclusion for content creation tasks
        content_creation_patterns = [
            'write.*blog', 'create.*email', 'generate.*content', 'write.*post',
            'create.*article', 'write.*story', 'compose.*message'
        ]
        
        for pattern in content_creation_patterns:
            if re.search(pattern, task_lower):
                return False
        
        # Layer 1: Direct Data Analysis Keywords
        data_keywords = {
            'data', 'dataset', 'statistics', 'statistical', 'analysis', 'analyze',
            'correlation', 'trend', 'pattern', 'distribution', 'frequency',
            'mean', 'median', 'mode', 'variance', 'deviation', 'percentile'
        }
        
        if any(keyword in task_lower for keyword in data_keywords):
            # Additional check for content creation context
            if any(word in task_lower for word in ['write', 'blog', 'post', 'article', 'story']):
                return False
            return True
        
        # Layer 2: Analysis Type Detection
        for analysis_type, info in self.analysis_types.items():
            if any(keyword in task_lower for keyword in info['keywords']):
                return True
        
        # Layer 3: Operation Detection
        for operation, keywords in self.operation_types.items():
            if any(keyword in task_lower for keyword in keywords):
                # Check if combined with data context
                data_context = any(word in task_lower for word in [
                    'data', 'numbers', 'values', 'dataset', 'table', 'csv', 'statistics'
                ])
                if data_context:
                    return True
        
        # Layer 4: Data Format Recognition
        for data_format, patterns in self.data_formats.items():
            if any(re.search(pattern, task_lower) for pattern in patterns):
                return True
        
        # Layer 5: Mathematical Operations on Data
        math_data_patterns = [
            r'calculate.*average',
            r'find.*correlation',
            r'compute.*statistics',
            r'analyze.*numbers',
            r'summarize.*data',
            r'compare.*values'
        ]
        
        if any(re.search(pattern, task_lower) for pattern in math_data_patterns):
            return True
        
        # Layer 6: Numeric Data Detection
        # Look for sequences of numbers that might be data
        numeric_sequences = re.findall(r'\b\d+(?:\.\d+)?\b', task)
        if len(numeric_sequences) >= 3:  # Multiple numbers suggest data analysis
            return True
        
        # Layer 7: Exclusion Rules (early exclusion for non-data tasks)
        non_data_indicators = {
            'write a blog', 'create email', 'generate code', 'debug code',
            'weather forecast', 'temperature today', 'cooking recipe',
            'install software', 'create directory', 'translate text',
            'search online', 'browse web', 'send message'
        }
        
        # Early exclusion for clearly non-data tasks
        for indicator in non_data_indicators:
            if indicator in task_lower:
                return False
        
        # Additional exclusion for content creation without data context
        if any(word in task_lower for word in ['write', 'create', 'generate']) and 'blog' in task_lower:
            # Only exclude if no data context
            data_context = any(word in task_lower for word in ['data', 'statistics', 'analysis', 'numbers', 'dataset'])
            if not data_context:
                return False
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute data analysis with robust error handling.
        
        Args:
            task: Data analysis task to perform
            **kwargs: Additional parameters (data, analysis_type, format, etc.)
            
        Returns:
            Structured dictionary with analysis results
        """
        start_time = time.time()
        
        try:
            # Input validation
            if not task or not isinstance(task, str):
                return self._error_response("Task must be a non-empty string")
            
            if not self.can_handle(task):
                return self._error_response("Task does not appear to be data analysis related")
            
            # Detect analysis parameters
            analysis_type = self._detect_analysis_type(task, kwargs.get('analysis_type'))
            operation = self._detect_operation(task)
            data_format = self._detect_data_format(task, kwargs.get('format'))
            
            # Extract or receive data
            data = self._extract_or_receive_data(task, kwargs)
            
            if data is None:
                return self._error_response("No valid data found for analysis")
            
            # Perform data analysis
            result = self._perform_analysis(analysis_type, operation, data, task, kwargs)
            
            if result is None:
                return self._error_response("Could not complete the data analysis")
            
            execution_time = time.time() - start_time
            
            # Success response
            return {
                'success': True,
                'result': result,
                'message': f"Data analysis completed successfully",
                'metadata': {
                    'tool_name': self.name,
                    'execution_time': execution_time,
                    'task_type': 'data_analysis',
                    'analysis_type': analysis_type,
                    'operation': operation,
                    'data_format': data_format,
                    'data_points': len(data) if isinstance(data, (list, tuple)) else 'N/A',
                    'data_type': type(data).__name__
                }
            }
            
        except Exception as e:
            return self._error_response(f"Data analysis failed: {str(e)}", e)
    
    def _detect_analysis_type(self, task: str, explicit_type: str = None) -> str:
        """Detect the type of data analysis required."""
        if explicit_type and explicit_type in self.analysis_types:
            return explicit_type
        
        task_lower = task.lower()
        
        # Priority-based detection for specific keywords
        if any(word in task_lower for word in ['correlation', 'relationship', 'association', 'dependence']):
            return 'correlation'
        elif any(word in task_lower for word in ['distribution', 'histogram', 'frequency', 'percentile', 'quartile']):
            return 'distribution'
        elif any(word in task_lower for word in ['trend', 'pattern', 'time series', 'growth', 'decline', 'seasonal']):
            return 'trend'
        elif any(word in task_lower for word in ['compare', 'comparison', 'versus', 'difference', 'relative']):
            return 'comparative'
        elif any(word in task_lower for word in ['describe', 'summary', 'overview', 'basic stats', 'descriptive', 'mean', 'median', 'average']):
            return 'descriptive'
        elif 'descriptive statistics' in task_lower:
            return 'descriptive'
        elif any(word in task_lower for word in ['statistics', 'statistical', 'hypothesis', 'significance', 'p-value']):
            return 'statistical'
        
        # Score each analysis type based on keyword matches
        scores = {}
        for analysis_type, info in self.analysis_types.items():
            score = 0
            for keyword in info['keywords']:
                if keyword in task_lower:
                    score += 1
            # Bonus for operation matches
            for operation in info['operations']:
                if operation.replace('_', ' ') in task_lower:
                    score += 2
            scores[analysis_type] = score
        
        # Return highest scoring type
        if scores and max(scores.values()) > 0:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        # Default
        return 'descriptive'
    
    def _detect_operation(self, task: str) -> str:
        """Detect the specific operation type."""
        task_lower = task.lower()
        
        for operation, keywords in self.operation_types.items():
            if any(keyword in task_lower for keyword in keywords):
                return operation
        
        return 'analyze'  # Default operation
    
    def _detect_data_format(self, task: str, explicit_format: str = None) -> str:
        """Detect the data format from task or parameters."""
        if explicit_format and explicit_format in self.data_formats:
            return explicit_format
        
        task_lower = task.lower()
        
        for data_format, patterns in self.data_formats.items():
            if any(re.search(pattern, task_lower) for pattern in patterns):
                return data_format
        
        return 'numeric_list'  # Default format
    
    def _extract_or_receive_data(self, task: str, kwargs: Dict[str, Any]) -> Optional[Any]:
        """Extract data from task or receive from parameters."""
        # Check if data is provided in kwargs
        if 'data' in kwargs and kwargs['data'] is not None:
            return self._parse_data(kwargs['data'])
        
        # Try to extract data from task text
        extracted_data = self._extract_data_from_text(task)
        if extracted_data:
            return extracted_data
        
        # Check for file references
        file_data = self._extract_file_references(task)
        if file_data:
            return file_data
        
        return None
    
    def _parse_data(self, data: Any) -> Optional[Any]:
        """Parse and validate data input."""
        try:
            # Handle string data
            if isinstance(data, str):
                # Try parsing as JSON
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    pass
                
                # Try parsing as CSV-like data
                if ',' in data:
                    return [float(x.strip()) for x in data.split(',') if x.strip().replace('.', '').replace('-', '').isdigit()]
                
                # Try parsing as space-separated numbers
                numbers = re.findall(r'-?\d+(?:\.\d+)?', data)
                if numbers:
                    return [float(x) for x in numbers]
            
            # Handle list/tuple data
            elif isinstance(data, (list, tuple)):
                # Try to convert to numeric if possible
                try:
                    return [float(x) for x in data if str(x).replace('.', '').replace('-', '').isdigit()]
                except (ValueError, TypeError):
                    return list(data)
            
            # Handle dictionary data
            elif isinstance(data, dict):
                return data
            
            # Handle numeric data
            elif isinstance(data, (int, float)):
                return [data]
            
            return data
            
        except Exception:
            return None
    
    def _extract_data_from_text(self, task: str) -> Optional[List[float]]:
        """Extract numeric data from task text."""
        # Look for arrays or lists in the text
        array_patterns = [
            r'\[([^\]]+)\]',  # [1, 2, 3, 4]
            r'\(([^\)]+)\)',  # (1, 2, 3, 4)
            r'data[:\s]+([^\n.!?]+)',  # data: 1, 2, 3, 4
            r'values[:\s]+([^\n.!?]+)',  # values: 1, 2, 3, 4
            r'numbers[:\s]+([^\n.!?]+)'  # numbers: 1, 2, 3, 4
        ]
        
        for pattern in array_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            for match in matches:
                # Extract numbers from the match
                numbers = re.findall(r'-?\d+(?:\.\d+)?', match)
                if len(numbers) >= 2:  # Need at least 2 numbers for analysis
                    try:
                        return [float(x) for x in numbers]
                    except ValueError:
                        continue
        
        # Look for scattered numbers (need at least 3 for meaningful analysis)
        all_numbers = re.findall(r'\b-?\d+(?:\.\d+)?\b', task)
        if len(all_numbers) >= 3:
            try:
                return [float(x) for x in all_numbers]
            except ValueError:
                pass
        
        return None
    
    def _extract_file_references(self, task: str) -> Optional[str]:
        """Extract file references for data loading."""
        file_patterns = [
            r'file[:\s]+([^\s]+\.(csv|json|xlsx|txt))',
            r'dataset[:\s]+([^\s]+)',
            r'load[:\s]+([^\s]+\.(csv|json|xlsx|txt))'
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            if matches:
                return matches[0][0] if isinstance(matches[0], tuple) else matches[0]
        
        return None
    
    def _perform_analysis(self, analysis_type: str, operation: str, data: Any, task: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the specific data analysis operation."""
        
        if analysis_type == 'descriptive':
            return self._descriptive_analysis(data, operation)
        elif analysis_type == 'statistical':
            return self._statistical_analysis(data, operation, kwargs)
        elif analysis_type == 'trend':
            return self._trend_analysis(data, operation, kwargs)
        elif analysis_type == 'comparative':
            return self._comparative_analysis(data, operation, kwargs)
        elif analysis_type == 'distribution':
            return self._distribution_analysis(data, operation)
        elif analysis_type == 'correlation':
            return self._correlation_analysis(data, operation, kwargs)
        else:
            return self._descriptive_analysis(data, operation)  # Default
    
    def _descriptive_analysis(self, data: Any, operation: str) -> Dict[str, Any]:
        """Perform descriptive statistical analysis."""
        if not isinstance(data, (list, tuple)) or not data:
            return {'error': 'Invalid data format for descriptive analysis'}
        
        # Convert to numeric if possible
        try:
            numeric_data = [float(x) for x in data if str(x).replace('.', '').replace('-', '').isdigit()]
            if not numeric_data:
                return {'error': 'No numeric data found for analysis'}
            
            data = numeric_data
        except (ValueError, TypeError):
            return {'error': 'Could not convert data to numeric format'}
        
        results = {
            'data_summary': {
                'count': len(data),
                'data_type': 'numeric',
                'sample_values': data[:5] if len(data) > 5 else data
            },
            'central_tendency': {},
            'variability': {},
            'extremes': {},
            'data_quality': {}
        }
        
        try:
            # Central tendency measures
            results['central_tendency'] = {
                'mean': statistics.mean(data),
                'median': statistics.median(data),
                'mode': statistics.mode(data) if len(set(data)) < len(data) else 'No mode',
            }
            
            # Variability measures
            if len(data) > 1:
                results['variability'] = {
                    'range': max(data) - min(data),
                    'variance': statistics.variance(data),
                    'standard_deviation': statistics.stdev(data),
                    'coefficient_of_variation': statistics.stdev(data) / statistics.mean(data) if statistics.mean(data) != 0 else 'Undefined'
                }
            
            # Extreme values
            results['extremes'] = {
                'minimum': min(data),
                'maximum': max(data),
                'sum': sum(data)
            }
            
            # Data quality assessment
            results['data_quality'] = {
                'missing_values': 0,  # Simplified for numeric data
                'duplicates': len(data) - len(set(data)),
                'outliers': self._detect_outliers(data),
                'completeness': '100%'
            }
            
            # Additional insights
            results['insights'] = self._generate_descriptive_insights(data, results)
            
        except Exception as e:
            results['error'] = f"Analysis error: {str(e)}"
        
        return results
    
    def _statistical_analysis(self, data: Any, operation: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform advanced statistical analysis."""
        if not isinstance(data, (list, tuple)) or not data:
            return {'error': 'Invalid data format for statistical analysis'}
        
        try:
            numeric_data = [float(x) for x in data if str(x).replace('.', '').replace('-', '').isdigit()]
            if len(numeric_data) < 2:
                return {'error': 'Insufficient data for statistical analysis (need at least 2 points)'}
            
            results = {
                'sample_statistics': {
                    'sample_size': len(numeric_data),
                    'degrees_of_freedom': len(numeric_data) - 1
                },
                'distribution_tests': {},
                'confidence_intervals': {},
                'hypothesis_testing': {}
            }
            
            # Basic distribution characteristics
            mean_val = statistics.mean(numeric_data)
            std_val = statistics.stdev(numeric_data) if len(numeric_data) > 1 else 0
            
            results['distribution_tests'] = {
                'normality_assumption': 'Cannot determine without advanced tests',
                'skewness': self._calculate_skewness(numeric_data),
                'kurtosis': self._calculate_kurtosis(numeric_data)
            }
            
            # Confidence intervals (assuming normal distribution)
            if len(numeric_data) > 1:
                margin_of_error = 1.96 * (std_val / math.sqrt(len(numeric_data)))  # 95% CI
                results['confidence_intervals'] = {
                    'mean_95_percent': {
                        'lower_bound': mean_val - margin_of_error,
                        'upper_bound': mean_val + margin_of_error
                    }
                }
            
            # Basic hypothesis testing framework
            results['hypothesis_testing'] = {
                'one_sample_t_test': 'Framework available for specific hypotheses',
                'recommended_tests': self._recommend_statistical_tests(numeric_data)
            }
            
            results['insights'] = self._generate_statistical_insights(numeric_data, results)
            
        except Exception as e:
            results = {'error': f"Statistical analysis error: {str(e)}"}
        
        return results
    
    def _trend_analysis(self, data: Any, operation: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform trend and time series analysis."""
        if not isinstance(data, (list, tuple)) or not data:
            return {'error': 'Invalid data format for trend analysis'}
        
        try:
            numeric_data = [float(x) for x in data if str(x).replace('.', '').replace('-', '').isdigit()]
            if len(numeric_data) < 3:
                return {'error': 'Insufficient data for trend analysis (need at least 3 points)'}
            
            results = {
                'trend_characteristics': {},
                'patterns': {},
                'forecasting': {},
                'volatility': {}
            }
            
            # Basic trend analysis
            first_half = numeric_data[:len(numeric_data)//2]
            second_half = numeric_data[len(numeric_data)//2:]
            
            first_avg = statistics.mean(first_half)
            second_avg = statistics.mean(second_half)
            
            results['trend_characteristics'] = {
                'overall_direction': 'Increasing' if second_avg > first_avg else 'Decreasing' if second_avg < first_avg else 'Stable',
                'trend_strength': abs(second_avg - first_avg) / first_avg if first_avg != 0 else 'Undefined',
                'data_points': len(numeric_data)
            }
            
            # Moving averages
            if len(numeric_data) >= 5:
                window_size = min(5, len(numeric_data) // 2)
                moving_avg = self._calculate_moving_average(numeric_data, window_size)
                results['patterns'] = {
                    'moving_average': moving_avg,
                    'smoothed_trend': 'Calculated' if moving_avg else 'Not available'
                }
            
            # Simple growth rate calculation
            if len(numeric_data) >= 2:
                growth_rates = []
                for i in range(1, len(numeric_data)):
                    if numeric_data[i-1] != 0:
                        growth_rate = (numeric_data[i] - numeric_data[i-1]) / numeric_data[i-1]
                        growth_rates.append(growth_rate)
                
                if growth_rates:
                    results['patterns']['average_growth_rate'] = statistics.mean(growth_rates)
                    results['patterns']['growth_volatility'] = statistics.stdev(growth_rates) if len(growth_rates) > 1 else 0
            
            # Volatility analysis
            if len(numeric_data) > 1:
                std_dev = statistics.stdev(numeric_data)
                mean_val = statistics.mean(numeric_data)
                results['volatility'] = {
                    'coefficient_of_variation': std_dev / mean_val if mean_val != 0 else 'Undefined',
                    'volatility_classification': self._classify_volatility(std_dev / mean_val if mean_val != 0 else 0)
                }
            
            # Simple forecasting
            if len(numeric_data) >= 3:
                recent_trend = (numeric_data[-1] - numeric_data[-3]) / 2
                next_value = numeric_data[-1] + recent_trend
                results['forecasting'] = {
                    'next_period_estimate': next_value,
                    'trend_based_method': 'Linear extrapolation',
                    'confidence': 'Low (simple method)'
                }
            
            results['insights'] = self._generate_trend_insights(numeric_data, results)
            
        except Exception as e:
            results = {'error': f"Trend analysis error: {str(e)}"}
        
        return results
    
    def _comparative_analysis(self, data: Any, operation: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comparative analysis between groups or datasets."""
        results = {
            'comparison_type': 'single_dataset',
            'group_analysis': {},
            'relative_performance': {},
            'ranking': {}
        }
        
        try:
            if isinstance(data, dict):
                # Multiple groups comparison
                results['comparison_type'] = 'multi_group'
                group_stats = {}
                
                for group_name, group_data in data.items():
                    if isinstance(group_data, (list, tuple)):
                        numeric_group = [float(x) for x in group_data if str(x).replace('.', '').replace('-', '').isdigit()]
                        if numeric_group:
                            group_stats[group_name] = {
                                'count': len(numeric_group),
                                'mean': statistics.mean(numeric_group),
                                'median': statistics.median(numeric_group),
                                'std_dev': statistics.stdev(numeric_group) if len(numeric_group) > 1 else 0,
                                'min': min(numeric_group),
                                'max': max(numeric_group)
                            }
                
                results['group_analysis'] = group_stats
                
                # Rankings
                if group_stats:
                    mean_ranking = sorted(group_stats.items(), key=lambda x: x[1]['mean'], reverse=True)
                    results['ranking'] = {
                        'by_mean': [{'group': group, 'value': stats['mean']} for group, stats in mean_ranking]
                    }
                
            elif isinstance(data, (list, tuple)):
                # Single dataset comparative analysis
                numeric_data = [float(x) for x in data if str(x).replace('.', '').replace('-', '').isdigit()]
                if numeric_data:
                    mean_val = statistics.mean(numeric_data)
                    
                    above_mean = [x for x in numeric_data if x > mean_val]
                    below_mean = [x for x in numeric_data if x < mean_val]
                    
                    results['group_analysis'] = {
                        'above_mean': {
                            'count': len(above_mean),
                            'percentage': (len(above_mean) / len(numeric_data)) * 100,
                            'average': statistics.mean(above_mean) if above_mean else 0
                        },
                        'below_mean': {
                            'count': len(below_mean),
                            'percentage': (len(below_mean) / len(numeric_data)) * 100,
                            'average': statistics.mean(below_mean) if below_mean else 0
                        }
                    }
                    
                    # Quartile analysis
                    sorted_data = sorted(numeric_data)
                    n = len(sorted_data)
                    q1_idx, q3_idx = n // 4, (3 * n) // 4
                    
                    results['relative_performance'] = {
                        'quartiles': {
                            'Q1': sorted_data[q1_idx] if q1_idx < n else sorted_data[0],
                            'Q2_median': statistics.median(numeric_data),
                            'Q3': sorted_data[q3_idx] if q3_idx < n else sorted_data[-1]
                        }
                    }
            
            results['insights'] = self._generate_comparative_insights(data, results)
            
        except Exception as e:
            results = {'error': f"Comparative analysis error: {str(e)}"}
        
        return results
    
    def _distribution_analysis(self, data: Any, operation: str) -> Dict[str, Any]:
        """Perform distribution and frequency analysis."""
        if not isinstance(data, (list, tuple)) or not data:
            return {'error': 'Invalid data format for distribution analysis'}
        
        try:
            # Handle both numeric and categorical data
            results = {
                'data_type': 'unknown',
                'frequency_analysis': {},
                'distribution_shape': {},
                'percentiles': {}
            }
            
            # Try numeric analysis first
            try:
                numeric_data = [float(x) for x in data if str(x).replace('.', '').replace('-', '').isdigit()]
                if len(numeric_data) >= len(data) * 0.8:  # Mostly numeric
                    results['data_type'] = 'numeric'
                    data = numeric_data
                else:
                    results['data_type'] = 'categorical'
            except:
                results['data_type'] = 'categorical'
            
            # Frequency analysis
            frequency_count = Counter(data)
            results['frequency_analysis'] = {
                'unique_values': len(frequency_count),
                'most_common': frequency_count.most_common(5),
                'frequency_distribution': dict(frequency_count)
            }
            
            if results['data_type'] == 'numeric' and len(data) > 1:
                # Percentile analysis
                sorted_data = sorted(data)
                n = len(sorted_data)
                
                percentiles = {}
                for p in [10, 25, 50, 75, 90, 95, 99]:
                    idx = int((p / 100) * (n - 1))
                    percentiles[f'P{p}'] = sorted_data[idx]
                
                results['percentiles'] = percentiles
                
                # Distribution shape analysis
                mean_val = statistics.mean(data)
                median_val = statistics.median(data)
                
                results['distribution_shape'] = {
                    'skewness': self._calculate_skewness(data),
                    'mean_median_comparison': {
                        'mean': mean_val,
                        'median': median_val,
                        'difference': mean_val - median_val,
                        'interpretation': self._interpret_mean_median_diff(mean_val, median_val)
                    }
                }
                
                # Outlier detection using IQR method
                q1_idx, q3_idx = int(0.25 * (n - 1)), int(0.75 * (n - 1))
                q1, q3 = sorted_data[q1_idx], sorted_data[q3_idx]
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers = [x for x in data if x < lower_bound or x > upper_bound]
                results['outlier_analysis'] = {
                    'outliers_count': len(outliers),
                    'outliers': outliers[:10],  # Show up to 10 outliers
                    'outlier_percentage': (len(outliers) / len(data)) * 100
                }
            
            results['insights'] = self._generate_distribution_insights(data, results)
            
        except Exception as e:
            results = {'error': f"Distribution analysis error: {str(e)}"}
        
        return results
    
    def _correlation_analysis(self, data: Any, operation: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform correlation and relationship analysis."""
        results = {
            'analysis_type': 'correlation',
            'relationships': {},
            'correlation_matrix': {},
            'insights': []
        }
        
        try:
            # Handle different data structures
            if isinstance(data, dict):
                # Dictionary with x_values and y_values keys (test format)
                if 'x_values' in data and 'y_values' in data:
                    x_values = data['x_values']
                    y_values = data['y_values']
                    
                    if len(x_values) == len(y_values) and len(x_values) >= 2:
                        corr = self._calculate_correlation(x_values, y_values)
                        results['relationships']['x_vs_y'] = {
                            'correlation_coefficient': corr,
                            'strength': self._interpret_correlation_strength(corr),
                            'direction': 'positive' if corr > 0 else 'negative' if corr < 0 else 'none',
                            'sample_size': len(x_values)
                        }
                
                # Multiple variables for correlation
                elif len(data) >= 2:
                    variables = {}
                    for key, values in data.items():
                        if isinstance(values, (list, tuple)):
                            numeric_values = [float(x) for x in values if str(x).replace('.', '').replace('-', '').isdigit()]
                            if numeric_values:
                                variables[key] = numeric_values
                    
                    if len(variables) >= 2:
                        var_names = list(variables.keys())
                        correlations = {}
                        
                        # Calculate pairwise correlations
                        for i, var1 in enumerate(var_names):
                            for j, var2 in enumerate(var_names[i+1:], i+1):
                                if len(variables[var1]) == len(variables[var2]):
                                    corr = self._calculate_correlation(variables[var1], variables[var2])
                                    correlations[f"{var1}_vs_{var2}"] = {
                                        'correlation_coefficient': corr,
                                        'strength': self._interpret_correlation_strength(corr),
                                        'direction': 'positive' if corr > 0 else 'negative' if corr < 0 else 'none'
                                    }
                        
                        results['relationships'] = correlations
                
            elif isinstance(data, (list, tuple)) and len(data) >= 4:
                # Assume first half is X, second half is Y for single correlation
                mid_point = len(data) // 2
                x_values = data[:mid_point]
                y_values = data[mid_point:]
                
                # Convert to numeric
                try:
                    x_numeric = [float(x) for x in x_values if str(x).replace('.', '').replace('-', '').isdigit()]
                    y_numeric = [float(y) for y in y_values if str(y).replace('.', '').replace('-', '').isdigit()]
                    
                    if len(x_numeric) == len(y_numeric) and len(x_numeric) >= 2:
                        corr = self._calculate_correlation(x_numeric, y_numeric)
                        results['relationships']['x_vs_y'] = {
                            'correlation_coefficient': corr,
                            'strength': self._interpret_correlation_strength(corr),
                            'direction': 'positive' if corr > 0 else 'negative' if corr < 0 else 'none',
                            'sample_size': len(x_numeric)
                        }
                except:
                    return {'error': 'Could not perform correlation analysis on provided data'}
            
            # Generate insights if we have relationships
            if results['relationships']:
                results['insights'] = self._generate_correlation_insights(results['relationships'])
            else:
                return {'error': 'Insufficient or improperly formatted data for correlation analysis'}
            
        except Exception as e:
            return {'error': f"Correlation analysis error: {str(e)}"}
        
        return results
    
    def _detect_outliers(self, data: List[float]) -> List[float]:
        """Detect outliers using the IQR method."""
        if len(data) < 4:
            return []
        
        sorted_data = sorted(data)
        n = len(sorted_data)
        q1_idx, q3_idx = int(0.25 * (n - 1)), int(0.75 * (n - 1))
        q1, q3 = sorted_data[q1_idx], sorted_data[q3_idx]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        return [x for x in data if x < lower_bound or x > upper_bound]
    
    def _calculate_skewness(self, data: List[float]) -> float:
        """Calculate skewness of the distribution."""
        if len(data) < 3:
            return 0
        
        n = len(data)
        mean_val = statistics.mean(data)
        std_val = statistics.stdev(data)
        
        if std_val == 0:
            return 0
        
        skewness = (n / ((n - 1) * (n - 2))) * sum(((x - mean_val) / std_val) ** 3 for x in data)
        return round(skewness, 4)
    
    def _calculate_kurtosis(self, data: List[float]) -> float:
        """Calculate kurtosis of the distribution."""
        if len(data) < 4:
            return 0
        
        n = len(data)
        mean_val = statistics.mean(data)
        std_val = statistics.stdev(data)
        
        if std_val == 0:
            return 0
        
        kurtosis = (n * (n + 1) / ((n - 1) * (n - 2) * (n - 3))) * sum(((x - mean_val) / std_val) ** 4 for x in data) - (3 * (n - 1) ** 2) / ((n - 2) * (n - 3))
        return round(kurtosis, 4)
    
    def _calculate_moving_average(self, data: List[float], window_size: int) -> List[float]:
        """Calculate moving average with specified window size."""
        if window_size > len(data):
            return []
        
        moving_avg = []
        for i in range(window_size - 1, len(data)):
            window = data[i - window_size + 1:i + 1]
            moving_avg.append(statistics.mean(window))
        
        return moving_avg
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        sum_y2 = sum(yi * yi for yi in y)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
        
        if denominator == 0:
            return 0
        
        correlation = numerator / denominator
        return round(correlation, 4)
    
    def _classify_volatility(self, cv: float) -> str:
        """Classify volatility based on coefficient of variation."""
        if cv < 0.1:
            return 'Low volatility'
        elif cv < 0.25:
            return 'Moderate volatility'
        elif cv < 0.5:
            return 'High volatility'
        else:
            return 'Very high volatility'
    
    def _interpret_correlation_strength(self, corr: float) -> str:
        """Interpret correlation coefficient strength."""
        abs_corr = abs(corr)
        if abs_corr < 0.1:
            return 'Very weak'
        elif abs_corr < 0.3:
            return 'Weak'
        elif abs_corr < 0.5:
            return 'Moderate'
        elif abs_corr < 0.7:
            return 'Strong'
        else:
            return 'Very strong'
    
    def _interpret_mean_median_diff(self, mean: float, median: float) -> str:
        """Interpret the difference between mean and median."""
        diff = mean - median
        if abs(diff) < 0.1 * abs(median):
            return 'Symmetric distribution'
        elif diff > 0:
            return 'Right-skewed (positive skew)'
        else:
            return 'Left-skewed (negative skew)'
    
    def _recommend_statistical_tests(self, data: List[float]) -> List[str]:
        """Recommend appropriate statistical tests based on data characteristics."""
        recommendations = []
        n = len(data)
        
        if n >= 30:
            recommendations.append('One-sample z-test (large sample)')
        else:
            recommendations.append('One-sample t-test (small sample)')
        
        if n >= 8:
            recommendations.append('Normality tests (Shapiro-Wilk)')
        
        recommendations.append('Non-parametric tests (Wilcoxon signed-rank)')
        
        return recommendations
    
    def _generate_descriptive_insights(self, data: List[float], results: Dict[str, Any]) -> List[str]:
        """Generate insights from descriptive analysis."""
        insights = []
        
        try:
            mean_val = results['central_tendency']['mean']
            median_val = results['central_tendency']['median']
            std_val = results['variability']['standard_deviation']
            
            # Distribution shape insight
            if abs(mean_val - median_val) < 0.1 * abs(median_val):
                insights.append("The data shows a relatively symmetric distribution with mean and median close together")
            elif mean_val > median_val:
                insights.append("The data is right-skewed with some high values pulling the mean above the median")
            else:
                insights.append("The data is left-skewed with some low values pulling the mean below the median")
            
            # Variability insight
            cv = std_val / mean_val if mean_val != 0 else 0
            if cv < 0.1:
                insights.append("The data shows low variability with values clustered closely around the mean")
            elif cv > 0.5:
                insights.append("The data shows high variability with values spread widely around the mean")
            
            # Sample size insight
            if len(data) < 10:
                insights.append("Small sample size - results should be interpreted with caution")
            elif len(data) > 100:
                insights.append("Large sample size provides good statistical power for analysis")
            
            # Outlier insight
            outliers = results['data_quality']['outliers']
            if len(outliers) > 0:
                insights.append(f"Found {len(outliers)} potential outliers that may need investigation")
                
        except Exception:
            insights.append("Basic descriptive analysis completed")
        
        return insights
    
    def _generate_statistical_insights(self, data: List[float], results: Dict[str, Any]) -> List[str]:
        """Generate insights from statistical analysis."""
        insights = []
        
        try:
            n = len(data)
            
            # Sample size insights
            if n < 30:
                insights.append("Small sample size - consider using t-distribution for confidence intervals")
            else:
                insights.append("Sample size is adequate for normal approximation")
            
            # Distribution insights
            skewness = results['distribution_tests']['skewness']
            if abs(skewness) > 1:
                insights.append("Distribution shows significant skewness - consider non-parametric methods")
            elif abs(skewness) < 0.5:
                insights.append("Distribution appears relatively symmetric")
            
            # Confidence interval insight
            if 'confidence_intervals' in results:
                insights.append("95% confidence interval provided assuming normal distribution")
                
        except Exception:
            insights.append("Statistical analysis framework applied")
        
        return insights
    
    def _generate_trend_insights(self, data: List[float], results: Dict[str, Any]) -> List[str]:
        """Generate insights from trend analysis."""
        insights = []
        
        try:
            direction = results['trend_characteristics']['overall_direction']
            insights.append(f"Overall trend direction: {direction}")
            
            if 'average_growth_rate' in results['patterns']:
                growth_rate = results['patterns']['average_growth_rate']
                if abs(growth_rate) > 0.1:
                    insights.append(f"Strong average growth rate of {growth_rate:.2%} per period")
                else:
                    insights.append("Relatively stable with minimal growth/decline")
            
            if 'volatility_classification' in results['volatility']:
                vol_class = results['volatility']['volatility_classification']
                insights.append(f"Data exhibits {vol_class.lower()}")
                
        except Exception:
            insights.append("Trend analysis completed")
        
        return insights
    
    def _generate_comparative_insights(self, data: Any, results: Dict[str, Any]) -> List[str]:
        """Generate insights from comparative analysis."""
        insights = []
        
        try:
            if results['comparison_type'] == 'multi_group':
                if 'ranking' in results and 'by_mean' in results['ranking']:
                    top_group = results['ranking']['by_mean'][0]
                    insights.append(f"Highest performing group: {top_group['group']} with mean value of {top_group['value']:.2f}")
            else:
                if 'above_mean' in results['group_analysis']:
                    above_pct = results['group_analysis']['above_mean']['percentage']
                    insights.append(f"{above_pct:.1f}% of values are above the mean")
                    
        except Exception:
            insights.append("Comparative analysis completed")
        
        return insights
    
    def _generate_distribution_insights(self, data: Any, results: Dict[str, Any]) -> List[str]:
        """Generate insights from distribution analysis."""
        insights = []
        
        try:
            data_type = results['data_type']
            unique_count = results['frequency_analysis']['unique_values']
            
            insights.append(f"Data type: {data_type} with {unique_count} unique values")
            
            if data_type == 'numeric':
                if 'outlier_analysis' in results:
                    outlier_pct = results['outlier_analysis']['outlier_percentage']
                    if outlier_pct > 5:
                        insights.append(f"High proportion of outliers ({outlier_pct:.1f}%) detected")
                    elif outlier_pct > 0:
                        insights.append(f"Some outliers ({outlier_pct:.1f}%) detected")
                    else:
                        insights.append("No outliers detected using IQR method")
            
            most_common = results['frequency_analysis']['most_common'][0]
            insights.append(f"Most frequent value: {most_common[0]} (appears {most_common[1]} times)")
            
        except Exception:
            insights.append("Distribution analysis completed")
        
        return insights
    
    def _generate_correlation_insights(self, relationships: Dict[str, Any]) -> List[str]:
        """Generate insights from correlation analysis."""
        insights = []
        
        try:
            for rel_name, rel_data in relationships.items():
                corr = rel_data['correlation_coefficient']
                strength = rel_data['strength']
                direction = rel_data['direction']
                
                if abs(corr) > 0.7:
                    insights.append(f"Strong {direction} correlation found in {rel_name} (r = {corr})")
                elif abs(corr) > 0.3:
                    insights.append(f"Moderate {direction} correlation found in {rel_name} (r = {corr})")
                else:
                    insights.append(f"Weak correlation found in {rel_name} (r = {corr})")
                    
        except Exception:
            insights.append("Correlation analysis completed")
        
        return insights
    
    def _error_response(self, message: str, exception: Exception = None) -> Dict[str, Any]:
        """Generate standardized error response."""
        return {
            'success': False,
            'error': message,
            'error_type': type(exception).__name__ if exception else 'ValidationError',
            'suggestions': [
                "Ensure the task contains a clear data analysis request",
                "Provide data in a supported format (list of numbers, CSV format, or JSON)",
                "Include sufficient data points for meaningful analysis (minimum 2-3 values)",
                "Examples: 'Analyze this data: [1,2,3,4,5]', 'Calculate statistics for: 10,20,30,40'",
                f"Supported analysis types: {', '.join(self.analysis_types.keys())}",
                "For correlation analysis, provide paired data or multiple variables"
            ],
            'metadata': {
                'tool_name': self.name,
                'error_timestamp': datetime.now().isoformat(),
                'supported_analysis_types': list(self.analysis_types.keys()),
                'supported_operations': list(self.operation_types.keys()),
                'supported_data_formats': list(self.data_formats.keys())
            }
        }