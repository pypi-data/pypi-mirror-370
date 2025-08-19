"""
Feature Selection Module
Focused on intelligent feature selection for machine learning
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from sklearn.feature_selection import SelectKBest, f_classif, f_regression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import time
import os

class FeatureSelectionIntegration:
    """Intelligent Feature Selection for QuickInsights"""
    
    def __init__(self):
        self.selection_history = []
    
    def smart_feature_selection(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        task_type: str = 'auto',
        n_features: Optional[int] = None,
        save_results: bool = False,
        output_dir: str = "./quickinsights_output"
    ) -> Dict[str, Any]:
        """
        Perform intelligent feature selection using multiple methods
        """
        start_time = time.time()
        
        try:
            # Auto-detect task type
            if task_type == 'auto':
                task_type = self._detect_task_type(y)
            
            # Auto-detect number of features
            if n_features is None:
                n_features = min(X.shape[1], 50)
            
            # Apply feature selection methods
            f_score_result = self._f_score_selection(X, y, n_features, task_type)
            tree_result = self._tree_based_selection(X, y, n_features, task_type)
            
            # Get consensus features
            consensus_features = self._get_consensus_features([f_score_result, tree_result], n_features)
            
            execution_time = time.time() - start_time
            
            results = {
                'task_type': task_type,
                'n_features_selected': len(consensus_features),
                'consensus_features': consensus_features,
                'f_score_result': f_score_result,
                'tree_result': tree_result,
                'performance': {
                    'execution_time': execution_time,
                    'reduction_ratio': 1 - (len(consensus_features) / X.shape[1])
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
    
    def _f_score_selection(self, X: Union[np.ndarray, pd.DataFrame], 
                          y: Union[np.ndarray, pd.Series], 
                          n_features: int, 
                          task_type: str) -> Dict[str, Any]:
        """F-score based feature selection"""
        if task_type == 'classification':
            selector = SelectKBest(score_func=f_classif, k=n_features)
        else:
            selector = SelectKBest(score_func=f_regression, k=n_features)
        
        X_selected = selector.fit_transform(X, y)
        return {
            'method': 'f_score',
            'selected_features': selector.get_support(),
            'scores': selector.scores_,
            'X_selected': X_selected
        }
    
    def _tree_based_selection(self, X: Union[np.ndarray, pd.DataFrame], 
                             y: Union[np.ndarray, pd.Series], 
                             n_features: int, 
                             task_type: str) -> Dict[str, Any]:
        """Tree-based feature importance selection"""
        if task_type == 'classification':
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        model.fit(X, y)
        importances = model.feature_importances_
        top_indices = np.argsort(importances)[-n_features:]
        
        selected_features = np.zeros(X.shape[1], dtype=bool)
        selected_features[top_indices] = True
        
        return {
            'method': 'tree_based',
            'selected_features': selected_features,
            'importances': importances,
            'X_selected': X[:, selected_features]
        }
    
    def _get_consensus_features(self, results: List[Dict], n_features: int) -> List[int]:
        """Get consensus features across methods"""
        feature_votes = np.zeros(max([len(r.get('selected_features', [])) for r in results]), dtype=int)
        
        for result in results:
            if 'selected_features' in result:
                feature_votes += result['selected_features'].astype(int)
        
        consensus_features = np.where(feature_votes >= 1)[0]
        return consensus_features[-n_features:].tolist() if len(consensus_features) > n_features else consensus_features.tolist()
    
    def _save_results(self, results: Dict[str, Any], output_dir: str):
        """Save results to files"""
        os.makedirs(output_dir, exist_ok=True)
        import json
        with open(f"{output_dir}/feature_selection_results.json", 'w') as f:
            json.dump(results, f, indent=2, default=str)

# Convenience function
def smart_feature_selection(*args, **kwargs):
    """Convenience function for smart_feature_selection"""
    feature_selector = FeatureSelectionIntegration()
    return feature_selector.smart_feature_selection(*args, **kwargs)
