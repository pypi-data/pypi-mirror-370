"""
Model Selection Module
Focused on intelligent model selection for machine learning
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVC, SVR
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
import time
import os

class ModelSelectionIntegration:
    """Intelligent Model Selection for QuickInsights"""
    
    def __init__(self):
        self.model_history = []
        self.best_models = {}
    
    def intelligent_model_selection(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        task_type: str = 'auto',
        models_to_test: Optional[List[str]] = None,
        cv_folds: int = 5,
        save_results: bool = False,
        output_dir: str = "./quickinsights_output"
    ) -> Dict[str, Any]:
        """
        Perform intelligent model selection and hyperparameter tuning
        """
        start_time = time.time()
        
        try:
            # Auto-detect task type
            if task_type == 'auto':
                task_type = self._detect_task_type(y)
            
            # Auto-detect models to test
            if models_to_test is None:
                models_to_test = self._detect_optimal_models(X, y, task_type)
            
            # Test models
            model_results = {}
            for model_name in models_to_test:
                result = self._test_model(X, y, model_name, task_type, cv_folds)
                model_results[model_name] = result
            
            # Find best model
            best_model = self._find_best_model(model_results, task_type)
            
            execution_time = time.time() - start_time
            
            results = {
                'task_type': task_type,
                'models_tested': models_to_test,
                'cv_folds': cv_folds,
                'model_results': model_results,
                'best_model': best_model,
                'performance': {
                    'execution_time': execution_time,
                    'total_models': len(models_to_test)
                }
            }
            
            if save_results:
                self._save_results(results, output_dir)
            
            return results
            
        except Exception as e:
            return {'error': str(e), 'execution_time': time.time() - start_time}
    
    def _detect_task_type(self, y: Union[np.ndarray, pd.Series]) -> str:
        """Auto-detect task type"""
        unique_values = len(np.unique(y))
        return 'classification' if unique_values <= 20 else 'regression'
    
    def _detect_optimal_models(self, X: Union[np.ndarray, pd.DataFrame], 
                              y: Union[np.ndarray, pd.Series], 
                              task_type: str) -> List[str]:
        """Detect optimal models based on data characteristics"""
        models = []
        
        # Always include linear models
        models.append('linear')
        
        # Add tree-based models for larger datasets
        if X.shape[0] > 100:
            models.append('random_forest')
        
        # Add SVM for medium datasets
        if 50 <= X.shape[0] <= 1000:
            models.append('svm')
        
        return models[:3]  # Limit to top 3 models
    
    def _test_model(self, X: Union[np.ndarray, pd.DataFrame], 
                    y: Union[np.ndarray, pd.Series], 
                    model_name: str, 
                    task_type: str, 
                    cv_folds: int) -> Dict[str, Any]:
        """Test a specific model with cross-validation"""
        try:
            if model_name == 'linear':
                model, param_grid = self._get_linear_model(task_type)
            elif model_name == 'random_forest':
                model, param_grid = self._get_random_forest_model(task_type)
            elif model_name == 'svm':
                model, param_grid = self._get_svm_model(task_type)
            else:
                return {'error': f'Unknown model: {model_name}'}
            
            # Grid search with cross-validation
            grid_search = GridSearchCV(model, param_grid, cv=cv_folds, scoring=self._get_scoring(task_type))
            grid_search.fit(X, y)
            
            # Cross-validation scores
            cv_scores = cross_val_score(grid_search.best_estimator_, X, y, cv=cv_folds, 
                                      scoring=self._get_scoring(task_type))
            
            return {
                'model_name': model_name,
                'best_params': grid_search.best_params_,
                'best_score': grid_search.best_score_,
                'cv_scores': cv_scores,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'best_estimator': grid_search.best_estimator_
            }
            
        except Exception as e:
            return {'error': str(e), 'model_name': model_name}
    
    def _get_linear_model(self, task_type: str):
        """Get linear model and parameter grid"""
        if task_type == 'classification':
            model = LogisticRegression(random_state=42, max_iter=1000)
            param_grid = {'C': [0.1, 1, 10]}
        else:
            model = LinearRegression()
            param_grid = {}
        
        return model, param_grid
    
    def _get_random_forest_model(self, task_type: str):
        """Get random forest model and parameter grid"""
        if task_type == 'classification':
            model = RandomForestClassifier(random_state=42)
        else:
            model = RandomForestRegressor(random_state=42)
        
        param_grid = {
            'n_estimators': [50, 100],
            'max_depth': [5, 10, None]
        }
        
        return model, param_grid
    
    def _get_svm_model(self, task_type: str):
        """Get SVM model and parameter grid"""
        if task_type == 'classification':
            model = SVC(random_state=42)
        else:
            model = SVR()
        
        param_grid = {
            'C': [0.1, 1, 10],
            'gamma': ['scale', 'auto']
        }
        
        return model, param_grid
    
    def _get_scoring(self, task_type: str) -> str:
        """Get appropriate scoring metric"""
        return 'accuracy' if task_type == 'classification' else 'r2'
    
    def _find_best_model(self, model_results: Dict[str, Any], task_type: str) -> Dict[str, Any]:
        """Find the best performing model"""
        valid_results = {k: v for k, v in model_results.items() if 'error' not in v}
        
        if not valid_results:
            return {'error': 'No valid models found'}
        
        # Find best model based on CV mean score
        best_model_name = max(valid_results.keys(), 
                            key=lambda x: valid_results[x]['cv_mean'])
        
        best_result = valid_results[best_model_name]
        
        return {
            'name': best_model_name,
            'cv_mean': best_result['cv_mean'],
            'cv_std': best_result['cv_std'],
            'best_params': best_result['best_params'],
            'estimator': best_result['best_estimator']
        }
    
    def _save_results(self, results: Dict[str, Any], output_dir: str):
        """Save results to files"""
        os.makedirs(output_dir, exist_ok=True)
        import json
        
        # Make results JSON serializable
        serializable_results = {}
        for key, value in results.items():
            if key == 'model_results':
                serializable_results[key] = {}
                for model_name, model_result in value.items():
                    serializable_results[key][model_name] = {
                        k: v for k, v in model_result.items() 
                        if k not in ['best_estimator', 'estimator']
                    }
            elif key == 'best_model' and 'estimator' in value:
                serializable_results[key] = {
                    k: v for k, v in value.items() if k != 'estimator'
                }
            else:
                serializable_results[key] = value
        
        with open(f"{output_dir}/model_selection_results.json", 'w') as f:
            json.dump(serializable_results, f, indent=2, default=str)

# Convenience function
def intelligent_model_selection(*args, **kwargs):
    """Convenience function for intelligent_model_selection"""
    model_selector = ModelSelectionIntegration()
    return model_selector.intelligent_model_selection(*args, **kwargs)


