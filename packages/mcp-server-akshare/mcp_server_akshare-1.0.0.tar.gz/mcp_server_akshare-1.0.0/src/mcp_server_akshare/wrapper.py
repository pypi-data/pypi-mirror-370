"""
AkShare Interface Discovery and Wrapper
Automatically discovers and wraps AkShare functions for MCP
"""

import inspect
import akshare as ak
import pandas as pd
from typing import Dict, List, Any, Optional, Callable
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class AkShareWrapper:
    """Wrapper class for AkShare functions with automatic discovery"""
    
    def __init__(self):
        self.functions = {}
        self.categories = {}
        self._discover_functions()
    
    def _discover_functions(self):
        """Automatically discover all public AkShare functions"""
        
        # Common AkShare function categories
        categories = {
            'stock': ['stock_', 'sh_', 'sz_', 'index_', 'fund_'],
            'futures': ['futures_', 'option_'],
            'bond': ['bond_', 'convertible_'],
            'macro': ['macro_', 'gdp_', 'cpi_', 'pmi_'],
            'energy': ['energy_', 'oil_', 'gas_'],
            'crypto': ['crypto_', 'bitcoin_', 'ethereum_'],
            'forex': ['forex_', 'currency_'],
            'commodity': ['gold_', 'silver_', 'copper_'],
            'real_estate': ['real_estate_', 'house_'],
            'news': ['news_', 'report_'],
            'other': []
        }
        
        # Get all public functions from akshare
        for name in dir(ak):
            if not name.startswith('_'):
                obj = getattr(ak, name)
                if callable(obj) and hasattr(obj, '__module__'):
                    # Try to categorize the function
                    category = 'other'
                    for cat, prefixes in categories.items():
                        if any(name.startswith(prefix) for prefix in prefixes):
                            category = cat
                            break
                    
                    # Get function info
                    func_info = self._get_function_info(obj, name)
                    if func_info:
                        self.functions[name] = func_info
                        
                        if category not in self.categories:
                            self.categories[category] = []
                        self.categories[category].append(name)
        
        logger.info(f"Discovered {len(self.functions)} AkShare functions")
        logger.info(f"Categories: {list(self.categories.keys())}")
    
    def _get_function_info(self, func: Callable, name: str) -> Optional[Dict[str, Any]]:
        """Extract function information including parameters and documentation"""
        try:
            sig = inspect.signature(func)
            doc = inspect.getdoc(func) or f"AkShare function: {name}"
            
            # Parse parameters
            parameters = {}
            for param_name, param in sig.parameters.items():
                param_info = {
                    'name': param_name,
                    'required': param.default == inspect.Parameter.empty,
                    'default': None if param.default == inspect.Parameter.empty else param.default,
                    'type': 'string'  # Default to string, could be enhanced with type hints
                }
                
                # Try to infer type from default value
                if param.default != inspect.Parameter.empty:
                    if isinstance(param.default, bool):
                        param_info['type'] = 'boolean'
                    elif isinstance(param.default, int):
                        param_info['type'] = 'integer'
                    elif isinstance(param.default, float):
                        param_info['type'] = 'number'
                
                parameters[param_name] = param_info
            
            return {
                'function': func,
                'name': name,
                'description': doc,
                'parameters': parameters,
                'signature': sig
            }
        except Exception as e:
            logger.warning(f"Failed to get info for function {name}: {e}")
            return None
    
    def call_function(self, name: str, **kwargs) -> Dict[str, Any]:
        """Call an AkShare function with error handling and result formatting"""
        if name not in self.functions:
            raise ValueError(f"Function {name} not found")
        
        func_info = self.functions[name]
        func = func_info['function']
        
        try:
            # Filter kwargs to only include valid parameters
            sig = func_info['signature']
            filtered_kwargs = {}
            for param_name in sig.parameters:
                if param_name in kwargs:
                    filtered_kwargs[param_name] = kwargs[param_name]
            
            # Call the function
            result = func(**filtered_kwargs)
            
            # Format result
            return self._format_result(result, name)
            
        except Exception as e:
            logger.error(f"Error calling {name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'function': name,
                'parameters': kwargs
            }
    
    def _format_result(self, result: Any, function_name: str) -> Dict[str, Any]:
        """Format function result for MCP response"""
        formatted = {
            'success': True,
            'function': function_name,
            'data_type': type(result).__name__
        }
        
        if isinstance(result, pd.DataFrame):
            # Convert DataFrame to dict with metadata
            formatted.update({
                'data': result.to_dict('records'),
                'columns': list(result.columns),
                'rows': len(result),
                'summary': f"DataFrame with {len(result)} rows and {len(result.columns)} columns"
            })
        elif isinstance(result, (list, tuple)):
            formatted.update({
                'data': list(result),
                'length': len(result),
                'summary': f"List with {len(result)} items"
            })
        elif isinstance(result, dict):
            formatted.update({
                'data': result,
                'keys': list(result.keys()),
                'summary': f"Dictionary with {len(result)} keys"
            })
        else:
            # Simple value
            formatted.update({
                'data': result,
                'summary': f"Value: {result}"
            })
        
        return formatted
    
    def get_function_list(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available functions, optionally filtered by category"""
        if category and category in self.categories:
            function_names = self.categories[category]
        else:
            function_names = list(self.functions.keys())
        
        return [
            {
                'name': name,
                'description': self.functions[name]['description'][:100] + '...' 
                             if len(self.functions[name]['description']) > 100 
                             else self.functions[name]['description'],
                'parameters': list(self.functions[name]['parameters'].keys())
            }
            for name in function_names
        ]
    
    def get_categories(self) -> Dict[str, List[str]]:
        """Get all function categories"""
        return self.categories
