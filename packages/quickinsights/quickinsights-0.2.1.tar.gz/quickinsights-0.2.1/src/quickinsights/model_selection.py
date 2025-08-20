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


def performance_benchmark(
    models: List,
    X: Union[np.ndarray, pd.DataFrame],
    y: Union[np.ndarray, pd.Series],
    cv_folds: int = 5,
    metrics: Optional[List[str]] = None,
    include_timing: bool = True,
    save_results: bool = False,
    output_dir: str = "./quickinsights_output"
) -> Dict[str, Any]:
    """
    Comprehensive performance benchmarking of multiple models
    
    Parameters:
    -----------
    models : list
        List of model objects to benchmark
    X : array-like
        Training features
    y : array-like
        Training targets
    cv_folds : int
        Number of cross-validation folds
    metrics : list, optional
        List of metrics to compute
    include_timing : bool
        Include timing information
    save_results : bool
        Save results to files
    output_dir : str
        Output directory for saved files
        
    Returns:
    --------
    dict : Benchmark results
    """
    
    try:
        import time
        from sklearn.model_selection import cross_val_score
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, f1_score,
            r2_score, mean_squared_error, mean_absolute_error
        )
        
        print(f"🏁 Starting performance benchmark for {len(models)} models...")
        
        # Auto-detect task type
        unique_targets = len(np.unique(y))
        task_type = 'classification' if unique_targets <= 20 else 'regression'
        
        # Default metrics
        if metrics is None:
            if task_type == 'classification':
                metrics = ['accuracy', 'precision', 'recall', 'f1']
            else:
                metrics = ['r2', 'rmse', 'mae']
        
        results = {
            'task_type': task_type,
            'cv_folds': cv_folds,
            'metrics': metrics,
            'models': {},
            'summary': {},
            'rankings': {},
            'insights': []
        }
        
        # Benchmark each model
        for i, model in enumerate(models):
            model_name = f"Model_{i+1}"
            if hasattr(model, '__class__'):
                model_name = model.__class__.__name__
            
            print(f"🔍 Benchmarking {model_name}...")
            
            model_results = {
                'name': model_name,
                'type': type(model).__name__,
                'cv_scores': {},
                'metrics': {},
                'timing': {}
            }
            
            # Cross-validation scores
            for metric in metrics:
                try:
                    if metric in ['accuracy', 'precision', 'recall', 'f1'] and task_type == 'classification':
                        scoring = metric
                    elif metric in ['r2', 'rmse', 'mae'] and task_type == 'regression':
                        scoring = metric
                    else:
                        # Use default scoring for the task
                        scoring = 'accuracy' if task_type == 'classification' else 'r2'
                    
                    cv_scores = cross_val_score(model, X, y, cv=cv_folds, scoring=scoring)
                    model_results['cv_scores'][metric] = {
                        'mean': float(cv_scores.mean()),
                        'std': float(cv_scores.std()),
                        'min': float(cv_scores.min()),
                        'max': float(cv_scores.max())
                    }
                except Exception as e:
                    model_results['cv_scores'][metric] = {'error': str(e)}
            
            # Training and prediction timing
            if include_timing:
                try:
                    # Training time
                    start_time = time.time()
                    model.fit(X, y)
                    training_time = time.time() - start_time
                    
                    # Prediction time
                    start_time = time.time()
                    y_pred = model.predict(X)
                    prediction_time = time.time() - start_time
                    
                    model_results['timing'] = {
                        'training_time': training_time,
                        'prediction_time': prediction_time,
                        'total_time': training_time + prediction_time
                    }
                except Exception as e:
                    model_results['timing'] = {'error': str(e)}
            
            # Additional metrics
            try:
                y_pred = model.predict(X)
                
                if task_type == 'classification':
                    model_results['metrics'] = {
                        'accuracy': float(accuracy_score(y, y_pred)),
                        'precision': float(precision_score(y, y_pred, average='weighted')),
                        'recall': float(recall_score(y, y_pred, average='weighted')),
                        'f1': float(f1_score(y, y_pred, average='weighted'))
                    }
                else:  # Regression
                    model_results['metrics'] = {
                        'r2': float(r2_score(y, y_pred)),
                        'rmse': float(np.sqrt(mean_squared_error(y, y_pred))),
                        'mae': float(mean_absolute_error(y, y_pred))
                    }
            except Exception as e:
                model_results['metrics'] = {'error': str(e)}
            
            results['models'][model_name] = model_results
        
        # Generate rankings
        for metric in metrics:
            if metric in ['accuracy', 'precision', 'recall', 'f1', 'r2']:
                # Higher is better
                rankings = sorted(
                    [(name, results['models'][name]['cv_scores'].get(metric, {}).get('mean', 0)) 
                     for name in results['models'].keys()],
                    key=lambda x: x[1], reverse=True
                )
            else:  # RMSE, MAE - lower is better
                rankings = sorted(
                    [(name, results['models'][name]['cv_scores'].get(metric, {}).get('mean', float('inf'))) 
                     for name in results['models'].keys()],
                    key=lambda x: x[1] if x[1] != float('inf') else 0
                )
            
            results['rankings'][metric] = rankings
        
        # Generate summary
        results['summary'] = {
            'total_models': len(models),
            'best_model_overall': results['rankings'].get(metrics[0], [])[0][0] if results['rankings'] else None,
            'average_training_time': np.mean([m['timing'].get('training_time', 0) for m in results['models'].values() if 'training_time' in m['timing']]),
            'fastest_model': min([(name, m['timing'].get('training_time', float('inf'))) for name, m in results['models'].items() if 'training_time' in m['timing']], key=lambda x: x[1])[0] if any('training_time' in m['timing'] for m in results['models'].values()) else None
        }
        
        # Generate insights
        if results['summary']['best_model_overall']:
            results['insights'].append(f"🏆 {results['summary']['best_model_overall']} is the best performing model overall")
        
        if results['summary']['fastest_model']:
            results['insights'].append(f"⚡ {results['summary']['fastest_model']} is the fastest training model")
        
        # Performance analysis
        cv_means = [m['cv_scores'].get(metrics[0], {}).get('mean', 0) for m in results['models'].values()]
        if cv_means:
            cv_std = np.std(cv_means)
            if cv_std < 0.05:
                results['insights'].append("📊 Models show consistent performance (low variance)")
            elif cv_std > 0.1:
                results['insights'].append("📊 Models show high performance variance - consider ensemble methods")
        
        # Save results
        if save_results:
            os.makedirs(output_dir, exist_ok=True)
            import json
            
            # Make results JSON serializable
            serializable_results = {}
            for key, value in results.items():
                if key == 'models':
                    serializable_results[key] = {}
                    for model_name, model_result in value.items():
                        serializable_results[key][model_name] = {
                            k: v for k, v in model_result.items() 
                            if k not in ['model']
                        }
                else:
                    serializable_results[key] = value
            
            with open(f"{output_dir}/performance_benchmark_results.json", 'w') as f:
                json.dump(serializable_results, f, indent=2, default=str)
            
            print(f"💾 Benchmark results saved to: {output_dir}")
        
        print(f"✅ Performance benchmark completed for {len(models)} models")
        return results
        
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")
        return {"error": str(e)}



