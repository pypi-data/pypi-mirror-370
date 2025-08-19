"""
QuickInsights - NumPy Integration Module

This module integrates the most powerful NumPy mathematical operations with intelligent automation
and enhanced functionality for QuickInsights library.
"""

import numpy as np
import pandas as pd
from typing import Union, List, Dict, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class NumPyIntegration:
    """
    Enhanced NumPy functionality with intelligent automation
    """
    
    def __init__(self):
        self.analysis_history = []
        self.performance_metrics = {}
    
    def auto_math_analysis(
        self,
        data: Union[np.ndarray, pd.DataFrame, pd.Series],
        analysis_types: Optional[List[str]] = None,
        auto_detect_operations: bool = True,
        include_visualizations: bool = True,
        save_results: bool = False,
        output_dir: str = "./quickinsights_output"
    ) -> Dict[str, Any]:
        """
        Automatic mathematical analysis with intelligent operation selection
        
        Parameters:
        -----------
        data : np.ndarray, pd.DataFrame, or pd.Series
            Input data for analysis
        analysis_types : list, optional
            Types of analysis to perform
        auto_detect_operations : bool
            Automatically detect best mathematical operations
        include_visualizations : bool
            Generate visualizations
        save_results : bool
            Save results to files
        output_dir : str
            Output directory for saved files
            
        Returns:
        --------
        dict : Comprehensive mathematical analysis results
        """
        
        try:
            # Convert to numpy array if needed
            if isinstance(data, pd.DataFrame):
                data_array = data.select_dtypes(include=[np.number]).values
                print(f"🔍 Converted DataFrame to NumPy array: {data_array.shape}")
            elif isinstance(data, pd.Series):
                data_array = data.values.reshape(-1, 1)
                print(f"🔍 Converted Series to NumPy array: {data_array.shape}")
            else:
                data_array = np.asarray(data)
                print(f"🔍 Using NumPy array: {data_array.shape}")
            
            # Input validation
            if data_array.size == 0:
                raise ValueError("Data array is empty")
            
            print("🧮 Starting automatic mathematical analysis...")
            
            # Auto-detect operations if requested
            if auto_detect_operations:
                suggested_ops = self._detect_optimal_operations(data_array)
                analysis_types = suggested_ops
                print(f"🎯 Auto-detected operations: {analysis_types}")
            
            # Perform mathematical analysis
            results = {}
            
            for op_type in analysis_types:
                print(f"📊 Performing {op_type} analysis...")
                
                if op_type == 'descriptive':
                    results[op_type] = self._descriptive_statistics(data_array)
                elif op_type == 'correlation':
                    results[op_type] = self._correlation_analysis(data_array)
                elif op_type == 'eigenvalues':
                    results[op_type] = self._eigenvalue_analysis(data_array)
                elif op_type == 'singular_values':
                    results[op_type] = self._singular_value_analysis(data_array)
                elif op_type == 'fft':
                    results[op_type] = self._fft_analysis(data_array)
                elif op_type == 'optimization':
                    results[op_type] = self._optimization_analysis(data_array)
            
            # Performance metrics
            performance_metrics = self._calculate_math_performance(data_array, analysis_types)
            
            # Create comprehensive results
            final_results = {
                'mathematical_analysis': results,
                'performance_metrics': performance_metrics,
                'data_info': {
                    'shape': data_array.shape,
                    'dtype': str(data_array.dtype),
                    'size': data_array.size,
                    'memory_usage_mb': data_array.nbytes / 1024**2
                },
                'analysis_types': analysis_types,
                'analysis_timestamp': pd.Timestamp.now()
            }
            
            # Generate visualizations if requested
            if include_visualizations:
                visualizations = self._generate_math_visualizations(results, data_array, output_dir)
                final_results['visualizations'] = visualizations
            
            # Save results if requested
            if save_results:
                self._save_math_results(final_results, output_dir)
            
            # Update analysis history
            self.analysis_history.append({
                'function': 'auto_math_analysis',
                'timestamp': pd.Timestamp.now(),
                'analysis_types': analysis_types
            })
            
            print("✅ Mathematical analysis completed successfully!")
            return final_results
            
        except Exception as e:
            print(f"❌ Error in auto_math_analysis: {str(e)}")
            raise
    
    def _detect_optimal_operations(self, data_array: np.ndarray) -> List[str]:
        """Detect optimal mathematical operations based on data characteristics"""
        
        operations = ['descriptive']  # Always include descriptive statistics
        
        # Check data dimensions
        if data_array.ndim == 1:
            # 1D data - good for FFT, optimization
            operations.extend(['fft', 'optimization'])
        elif data_array.ndim == 2:
            # 2D data - good for correlation, eigenvalues, SVD
            operations.extend(['correlation', 'eigenvalues', 'singular_values'])
            if data_array.shape[0] == data_array.shape[1]:
                operations.append('optimization')  # Square matrix
        else:
            # Multi-dimensional data
            operations.extend(['correlation', 'singular_values'])
        
        # Check data size
        if data_array.size > 10000:
            # Large data - avoid expensive operations
            operations = [op for op in operations if op not in ['eigenvalues', 'singular_values']]
        
        return operations
    
    def _descriptive_statistics(self, data_array: np.ndarray) -> Dict[str, Any]:
        """Calculate comprehensive descriptive statistics"""
        
        stats = {}
        
        # Basic statistics
        stats['basic'] = {
            'mean': np.mean(data_array),
            'median': np.median(data_array),
            'std': np.std(data_array),
            'variance': np.var(data_array),
            'min': np.min(data_array),
            'max': np.max(data_array),
            'range': np.max(data_array) - np.min(data_array),
            'sum': np.sum(data_array)
        }
        
        # Percentiles
        percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
        stats['percentiles'] = {
            f'p{p}': np.percentile(data_array, p) for p in percentiles
        }
        
        # Shape statistics
        stats['shape'] = {
            'skewness': self._calculate_skewness(data_array),
            'kurtosis': self._calculate_kurtosis(data_array)
        }
        
        # Missing values
        stats['missing'] = {
            'nan_count': np.isnan(data_array).sum(),
            'inf_count': np.isinf(data_array).sum(),
            'finite_count': np.isfinite(data_array).sum()
        }
        
        return stats
    
    def _correlation_analysis(self, data_array: np.ndarray) -> Dict[str, Any]:
        """Perform correlation analysis"""
        
        if data_array.ndim == 1:
            # 1D data - no correlation
            return {'error': '1D data cannot have correlation'}
        
        # Calculate correlation matrix
        corr_matrix = np.corrcoef(data_array.T)
        
        # Find high correlations
        high_corr = np.where(np.abs(corr_matrix) > 0.8)
        high_corr_pairs = []
        
        for i, j in zip(high_corr[0], high_corr[1]):
            if i != j:  # Avoid diagonal
                high_corr_pairs.append({
                    'row': int(i),
                    'col': int(j),
                    'correlation': float(corr_matrix[i, j])
                })
        
        return {
            'correlation_matrix': corr_matrix,
            'high_correlations': high_corr_pairs[:10],  # Top 10
            'mean_correlation': np.mean(np.abs(corr_matrix[np.triu_indices_from(corr_matrix, k=1)]))
        }
    
    def _eigenvalue_analysis(self, data_array: np.ndarray) -> Dict[str, Any]:
        """Perform eigenvalue analysis"""
        
        if data_array.ndim != 2:
            return {'error': 'Eigenvalue analysis requires 2D data'}
        
        try:
            # Calculate eigenvalues
            eigenvalues = np.linalg.eigvals(data_array)
            
            # Sort by magnitude
            sorted_eigenvalues = np.sort(np.abs(eigenvalues))[::-1]
            
            return {
                'eigenvalues': eigenvalues,
                'sorted_eigenvalues': sorted_eigenvalues,
                'largest_eigenvalue': float(np.max(np.abs(eigenvalues))),
                'smallest_eigenvalue': float(np.min(np.abs(eigenvalues))),
                'condition_number': float(np.max(np.abs(eigenvalues)) / np.min(np.abs(eigenvalues)))
            }
        except np.linalg.LinAlgError:
            return {'error': 'Matrix is not diagonalizable'}
    
    def _singular_value_analysis(self, data_array: np.ndarray) -> Dict[str, Any]:
        """Perform singular value decomposition analysis"""
        
        if data_array.ndim != 2:
            return {'error': 'SVD analysis requires 2D data'}
        
        try:
            # Perform SVD
            U, s, Vt = np.linalg.svd(data_array)
            
            return {
                'singular_values': s,
                'rank': np.sum(s > 1e-10),  # Numerical rank
                'largest_singular_value': float(s[0]),
                'smallest_singular_value': float(s[-1]),
                'condition_number': float(s[0] / s[-1])
            }
        except np.linalg.LinAlgError:
            return {'error': 'SVD computation failed'}
    
    def _fft_analysis(self, data_array: np.ndarray) -> Dict[str, Any]:
        """Perform Fast Fourier Transform analysis"""
        
        # Flatten data for FFT
        flat_data = data_array.flatten()
        
        # Perform FFT
        fft_result = np.fft.fft(flat_data)
        fft_magnitude = np.abs(fft_result)
        
        # Find dominant frequencies
        dominant_freq_idx = np.argsort(fft_magnitude)[-5:]  # Top 5
        dominant_frequencies = dominant_freq_idx / len(flat_data)
        
        return {
            'fft_result': fft_result,
            'fft_magnitude': fft_magnitude,
            'dominant_frequencies': dominant_frequencies,
            'max_magnitude': float(np.max(fft_magnitude)),
            'mean_magnitude': float(np.mean(fft_magnitude))
        }
    
    def _optimization_analysis(self, data_array: np.ndarray) -> Dict[str, Any]:
        """Perform optimization analysis"""
        
        if data_array.ndim == 1:
            # 1D optimization
            return {
                'global_min': float(np.min(data_array)),
                'global_max': float(np.max(data_array)),
                'argmin': int(np.argmin(data_array)),
                'argmax': int(np.argmax(data_array))
            }
        elif data_array.ndim == 2 and data_array.shape[0] == data_array.shape[1]:
            # Square matrix - find optimal values
            return {
                'min_value': float(np.min(data_array)),
                'max_value': float(np.max(data_array)),
                'trace': float(np.trace(data_array)),
                'determinant': float(np.linalg.det(data_array))
            }
        else:
            return {'error': 'Optimization analysis not applicable for this data shape'}
    
    def _calculate_skewness(self, data_array: np.ndarray) -> float:
        """Calculate skewness of the data"""
        mean = np.mean(data_array)
        std = np.std(data_array)
        if std == 0:
            return 0.0
        return float(np.mean(((data_array - mean) / std) ** 3))
    
    def _calculate_kurtosis(self, data_array: np.ndarray) -> float:
        """Calculate kurtosis of the data"""
        mean = np.mean(data_array)
        std = np.std(data_array)
        if std == 0:
            return 0.0
        return float(np.mean(((data_array - mean) / std) ** 4) - 3)
    
    def _calculate_math_performance(self, data_array: np.ndarray, analysis_types: List[str]) -> Dict[str, Any]:
        """Calculate performance metrics for mathematical operations"""
        
        start_time = pd.Timestamp.now()
        
        # Simple operation for timing
        try:
            _ = np.mean(data_array)
        except:
            pass
        
        end_time = pd.Timestamp.now()
        operation_time = (end_time - start_time).total_seconds() * 1000  # milliseconds
        
        return {
            'operation_time_ms': operation_time,
            'data_size': data_array.size,
            'memory_usage_mb': data_array.nbytes / 1024**2,
            'analysis_count': len(analysis_types)
        }
    
    def _generate_math_visualizations(self, results: Dict, data_array: np.ndarray, output_dir: str) -> Dict[str, str]:
        """Generate visualizations for mathematical analysis"""
        
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # Set style
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")
            
            visualizations = {}
            
            # Create output directory if it doesn't exist
            import os
            os.makedirs(output_dir, exist_ok=True)
            
            # 1. Data distribution
            plt.figure(figsize=(12, 6))
            
            plt.subplot(1, 2, 1)
            plt.hist(data_array.flatten(), bins=50, alpha=0.7, edgecolor='black')
            plt.title('Data Distribution')
            plt.xlabel('Value')
            plt.ylabel('Frequency')
            
            plt.subplot(1, 2, 2)
            plt.boxplot(data_array.flatten())
            plt.title('Data Box Plot')
            plt.ylabel('Value')
            
            plt.tight_layout()
            
            viz_path = f"{output_dir}/math_data_distribution.png"
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            plt.close()
            visualizations['data_distribution'] = viz_path
            
            # 2. Correlation heatmap (if available)
            if 'correlation' in results and 'correlation_matrix' in results['correlation']:
                plt.figure(figsize=(10, 8))
                sns.heatmap(results['correlation']['correlation_matrix'], 
                           annot=True, fmt='.2f', cmap='RdBu_r', center=0)
                plt.title('Correlation Matrix')
                plt.tight_layout()
                
                viz_path = f"{output_dir}/math_correlation_heatmap.png"
                plt.savefig(viz_path, dpi=300, bbox_inches='tight')
                plt.close()
                visualizations['correlation_heatmap'] = viz_path
            
            # 3. FFT magnitude (if available)
            if 'fft' in results and 'fft_magnitude' in results['fft']:
                plt.figure(figsize=(12, 6))
                plt.plot(results['fft']['fft_magnitude'][:len(results['fft']['fft_magnitude'])//2])
                plt.title('FFT Magnitude Spectrum')
                plt.xlabel('Frequency Index')
                plt.ylabel('Magnitude')
                plt.yscale('log')
                plt.grid(True)
                plt.tight_layout()
                
                viz_path = f"{output_dir}/math_fft_spectrum.png"
                plt.savefig(viz_path, dpi=300, bbox_inches='tight')
                plt.close()
                visualizations['fft_spectrum'] = viz_path
            
            print(f"📊 Generated {len(visualizations)} mathematical visualizations")
            return visualizations
            
        except ImportError:
            print("⚠️  Visualization libraries not available. Skipping visualizations.")
            return {}
        except Exception as e:
            print(f"⚠️  Error generating mathematical visualizations: {str(e)}")
            return {}
    
    def _save_math_results(self, results: Dict[str, Any], output_dir: str):
        """Save mathematical analysis results to files"""
        
        try:
            import os
            import json
            from datetime import datetime
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Save results to JSON
            json_path = f"{output_dir}/math_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Convert numpy types to native Python types for JSON serialization
            serializable_results = self._make_json_serializable(results)
            
            with open(json_path, 'w') as f:
                json.dump(serializable_results, f, indent=2, default=str)
            
            print(f"💾 Saved mathematical analysis to: {json_path}")
                
        except Exception as e:
            print(f"⚠️  Error saving mathematical results: {str(e)}")
    
    def _make_json_serializable(self, obj: Any) -> Any:
        """Convert numpy types to native Python types for JSON serialization"""
        
        if isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        else:
            return obj


# Convenience function for easy access
def auto_math_analysis(
    data: Union[np.ndarray, pd.DataFrame, pd.Series],
    analysis_types: Optional[List[str]] = None,
    auto_detect_operations: bool = True,
    include_visualizations: bool = True,
    save_results: bool = False,
    output_dir: str = "./quickinsights_output"
) -> Dict[str, Any]:
    """
    Convenience function for automatic mathematical analysis
    
    This is the main function users will call for mathematical analysis.
    """
    
    integrator = NumPyIntegration()
    return integrator.auto_math_analysis(
        data=data,
        analysis_types=analysis_types,
        auto_detect_operations=auto_detect_operations,
        include_visualizations=include_visualizations,
        save_results=save_results,
        output_dir=output_dir
    )


# Example usage and testing
if __name__ == "__main__":
    # Create sample data for testing
    np.random.seed(42)
    sample_data = np.random.normal(0, 1, (100, 5))
    
    print("🧪 Testing NumPy Integration Module...")
    print(f"📊 Sample data shape: {sample_data.shape}")
    
    # Test auto math analysis
    try:
        results = auto_math_analysis(
            data=sample_data,
            auto_detect_operations=True,
            include_visualizations=True,
            save_results=True
        )
        
        print("✅ Test completed successfully!")
        print(f"📈 Generated {len(results.get('visualizations', {}))} visualizations")
        print(f"💾 Results saved to: ./quickinsights_output/")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
