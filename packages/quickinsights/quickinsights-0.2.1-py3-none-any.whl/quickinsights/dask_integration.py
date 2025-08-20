"""
Dask Integration Module
Focused on big data processing and distributed computing
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union, Callable, Tuple
import time
import os

# Try to import Dask, but don't fail if not available
try:
    import dask.dataframe as dd
    import dask.array as da
    from dask.distributed import Client, LocalCluster
    from dask.diagnostics import ProgressBar
    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False

class DaskIntegration:
    """Big Data Processing with Dask for QuickInsights"""
    
    def __init__(self):
        self.client = None
        self.cluster = None
        self.dask_available = DASK_AVAILABLE
        
    def smart_dask_analysis(
        self,
        data: Union[pd.DataFrame, str, "dd.DataFrame"],
        analysis_type: str = 'auto',
        chunk_size: Optional[str] = None,
        n_workers: int = 4,
        memory_limit: str = '2GB',
        save_results: bool = False,
        output_dir: str = "./quickinsights_output"
    ) -> Dict[str, Any]:
        """
        Perform intelligent big data analysis using Dask
        
        Args:
            data: DataFrame, file path, or Dask DataFrame
            analysis_type: 'auto', 'descriptive', 'correlation', 'groupby'
            chunk_size: Chunk size for data partitioning
            n_workers: Number of worker processes
            memory_limit: Memory limit per worker
            save_results: Save results to files
            output_dir: Output directory
            
        Returns:
            Dictionary with analysis results and performance metrics
        """
        if not self.dask_available:
            return {
                'error': 'Dask not available. Install with: pip install dask[complete]',
                'dask_available': False
            }
        
        start_time = time.time()
        
        try:
            # Initialize Dask client
            self._setup_dask_client(n_workers, memory_limit)
            
            # Load and prepare data
            dask_df = self._prepare_dask_data(data, chunk_size)
            
            # Auto-detect analysis type
            if analysis_type == 'auto':
                analysis_type = self._detect_optimal_analysis(dask_df)
            
            # Perform analysis with strict branch to avoid ambiguous truth
            if analysis_type == 'correlation':
                results = self._correlation_analysis(dask_df)
            elif analysis_type == 'groupby':
                results = self._groupby_analysis(dask_df)
            else:
                results = self._descriptive_analysis(dask_df)

            # Fallback: if correlation fails, degrade to descriptive
            if isinstance(results, dict) and 'error' in results and analysis_type == 'correlation':
                fallback = self._descriptive_analysis(dask_df)
                if 'error' not in fallback:
                    results = fallback
                    results['warning'] = 'Correlation failed; returned descriptive statistics instead.'
                    results['analysis_type'] = 'descriptive'
            
            # Performance metrics
            execution_time = time.time() - start_time
            # Safely report performance without lazy dask shape
            results['performance'] = {
                'execution_time': execution_time,
                'n_workers': n_workers,
                'memory_limit': memory_limit,
                'npartitions': dask_df.npartitions
            }
            
            # Save results if requested
            if save_results:
                self._save_dask_results(results, output_dir)
            
            return results
            
        except Exception as e:
            import traceback as _tb
            return {
                'error': str(e),
                'traceback': _tb.format_exc(),
                'execution_time': time.time() - start_time,
                'dask_available': True,
                'stage': 'smart_dask_analysis'
            }
        finally:
            # Cleanup
            self._cleanup_dask_client()
    
    def distributed_compute(
        self,
        func: Callable,
        data_chunks: List[Any],
        n_workers: int = 4,
        memory_limit: str = '2GB',
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Execute distributed computation using Dask
        
        Args:
            func: Function to apply to each chunk
            data_chunks: List of data chunks
            n_workers: Number of worker processes
            memory_limit: Memory limit per worker
            show_progress: Show progress bar
            
        Returns:
            Dictionary with computation results
        """
        if not self.dask_available:
            return {
                'error': 'Dask not available. Install with: pip install dask[complete]',
                'dask_available': False
            }
        
        start_time = time.time()
        
        try:
            # Setup Dask client
            self._setup_dask_client(n_workers, memory_limit)
            
            # Convert to Dask delayed tasks
            from dask import delayed, compute
            delayed_results = [delayed(func)(chunk) for chunk in data_chunks]
            
            # Compute with progress bar
            if show_progress:
                with ProgressBar():
                    results = compute(*delayed_results)
            else:
                results = compute(*delayed_results)
            
            execution_time = time.time() - start_time
            
            return {
                'results': results,
                'n_chunks': len(data_chunks),
                'n_workers': n_workers,
                'execution_time': execution_time,
                'success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'execution_time': time.time() - start_time,
                'dask_available': True
            }
        finally:
            self._cleanup_dask_client()
    
    def big_data_pipeline(
        self,
        data_source: Union[str, pd.DataFrame],
        operations: List[Dict[str, Any]],
        chunk_size: str = '100MB',
        n_workers: int = 4,
        memory_limit: str = '2GB',
        save_intermediate: bool = False,
        output_dir: str = "./quickinsights_output"
    ) -> Dict[str, Any]:
        """
        Execute big data processing pipeline
        
        Args:
            data_source: Data source (file path or DataFrame)
            operations: List of operations to apply
            chunk_size: Size of data chunks
            n_workers: Number of worker processes
            memory_limit: Memory limit per worker
            save_intermediate: Save intermediate results
            output_dir: Output directory
            
        Returns:
            Dictionary with pipeline results
        """
        if not self.dask_available:
            return {
                'error': 'Dask not available. Install with: pip install dask[complete]',
                'dask_available': False
            }
        
        start_time = time.time()
        
        try:
            # Setup Dask client
            self._setup_dask_client(n_workers, memory_limit)
            
            # Load data
            dask_df = self._prepare_dask_data(data_source, chunk_size)
            
            # Apply operations pipeline
            pipeline_results = []
            current_df = dask_df
            
            for i, operation in enumerate(operations):
                op_name = operation.get('name', f'operation_{i}')
                op_type = operation.get('type', 'unknown')
                op_params = operation.get('params', {})
                
                print(f"🔄 Applying {op_name} ({op_type})...")
                
                # Apply operation
                result = self._apply_dask_operation(current_df, op_type, op_params)
                
                if 'error' in result:
                    return {'error': f'Pipeline failed at {op_name}: {result["error"]}'}
                
                current_df = result['result']
                pipeline_results.append({
                    'operation': op_name,
                    'type': op_type,
                    'result_shape': current_df.shape,
                    'npartitions': current_df.npartitions
                })
                
                # Save intermediate if requested
                if save_intermediate:
                    self._save_intermediate_result(current_df, op_name, output_dir)
            
            # Final computation
            final_result = current_df.compute()
            
            execution_time = time.time() - start_time
            
            results = {
                'pipeline_operations': pipeline_results,
                'final_result': final_result,
                'final_shape': final_result.shape,
                'performance': {
                    'execution_time': execution_time,
                    'n_operations': len(operations),
                    'n_workers': n_workers,
                    'chunk_size': chunk_size
                }
            }
            
            return results
            
        except Exception as e:
            return {
                'error': str(e),
                'execution_time': time.time() - start_time,
                'dask_available': True
            }
        finally:
            self._cleanup_dask_client()
    
    def _setup_dask_client(self, n_workers: int, memory_limit: str):
        """Setup Dask distributed client"""
        if self.client is None:
            self.cluster = LocalCluster(
                n_workers=n_workers,
                memory_limit=memory_limit,
                threads_per_worker=2
            )
            self.client = Client(self.cluster)
            print(f"🚀 Dask client initialized with {n_workers} workers")
    
    def _cleanup_dask_client(self):
        """Cleanup Dask client and cluster"""
        if self.client:
            self.client.close()
            self.client = None
        if self.cluster:
            self.cluster.close()
            self.cluster = None
    
    def distributed_compute(self, data, custom_function, chunk_size=1000, n_workers=4, 
                           memory_limit='2GB', output_dir='./quickinsights_output'):
        """Execute custom function in parallel across Dask workers"""
        if not self.dask_available:
            return {
                'error': 'Dask not available. Install with: pip install dask[complete]',
                'dask_available': False
            }
        
        start_time = time.time()
        
        try:
            # Setup Dask client
            self._setup_dask_client(n_workers, memory_limit)
            
            # Convert to Dask DataFrame if needed
            if isinstance(data, pd.DataFrame):
                dask_df = dd.from_pandas(data, npartitions=max(1, len(data) // chunk_size))
            else:
                dask_df = data
            
            # Apply custom function to each partition
            results = dask_df.map_partitions(custom_function).compute()
            
            execution_time = time.time() - start_time
            
            # Save results if output directory specified
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                import json
                with open(f"{output_dir}/distributed_compute_results.json", 'w') as f:
                    json.dump({
                        'results': str(results),
                        'execution_time': execution_time,
                        'n_workers': n_workers,
                        'chunk_size': chunk_size
                    }, f, indent=2, default=str)
            
            return {
                'results': results,
                'execution_time': execution_time,
                'n_workers': n_workers,
                'chunk_size': chunk_size,
                'success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'execution_time': time.time() - start_time,
                'dask_available': True
            }
        finally:
            self._cleanup_dask_client()
    
    def _prepare_dask_data(self, data: Union[pd.DataFrame, str, "dd.DataFrame"],
        chunk_size: Optional[str]) -> "dd.DataFrame":
        """Prepare Dask DataFrame from various input types"""
        if isinstance(data, "dd.DataFrame"):
            return data
        
        if isinstance(data, str):
            # File path - auto-detect format
            if data.endswith('.csv'):
                return dd.read_csv(data, blocksize=chunk_size)
            elif data.endswith('.parquet'):
                return dd.read_parquet(data)
            else:
                return dd.read_csv(data, blocksize=chunk_size)
        
        # Pandas DataFrame
        if isinstance(data, pd.DataFrame):
            return dd.from_pandas(data, npartitions=4)
        
        raise ValueError(f"Unsupported data type: {type(data)}")
    
    def _detect_optimal_analysis(self, dask_df: "dd.DataFrame") -> str:
        """Detect optimal analysis type. For stability, prefer 'descriptive' by default."""
        return 'descriptive'

    def _safe_head_df(self, dask_df: "dd.DataFrame", columns: List[str], n: int = 50000) -> pd.DataFrame:
        """Safely fetch up to n rows from the first non-empty partition as a Pandas DataFrame.
        Avoids dask_expr head-optimization path that can trigger ambiguous truth errors.
        """
        target_columns = columns if columns else list(dask_df.columns)
        for partition_index in range(dask_df.npartitions):
            try:
                partition = dask_df.get_partition(partition_index)[target_columns]
                pdf = partition.compute()
                if not pdf.empty:
                    if len(pdf) > n:
                        return pdf.head(n)
                    return pdf
            except Exception:
                continue
        # Fallback: compute a small slice via map_partitions
        try:
            sample = (
                dask_df[target_columns]
                .map_partitions(lambda p: p.head(min(len(p), n)))
                .compute()
            )
            if len(sample) > n:
                return sample.head(n)
            return sample
        except Exception:
            # Last resort: compute the very first partition entirely
            first = dask_df.get_partition(0)[target_columns].compute()
            if len(first) > n:
                return first.head(n)
            return first
    
    def _perform_dask_analysis(self, dask_df: "dd.DataFrame", analysis_type: str) -> Dict[str, Any]:
        """Perform specific type of Dask analysis"""
        if analysis_type == 'descriptive':
            return self._descriptive_analysis(dask_df)
        elif analysis_type == 'correlation':
            return self._correlation_analysis(dask_df)
        elif analysis_type == 'groupby':
            return self._groupby_analysis(dask_df)
        else:
            return {'error': f'Unknown analysis type: {analysis_type}'}
    
    def _descriptive_analysis(self, dask_df: "dd.DataFrame") -> Dict[str, Any]:
        """Perform descriptive statistics analysis"""
        numeric_cols = dask_df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return {'error': 'No numeric columns found for descriptive analysis'}
        
        # Robust descriptive statistics: safe head -> clean -> describe
        sample_pdf = self._safe_head_df(dask_df, list(numeric_cols), 50000)
        sample_pdf = sample_pdf.apply(pd.to_numeric, errors='coerce')
        col_means = sample_pdf.mean(numeric_only=True)
        sample_pdf = sample_pdf.fillna(col_means)
        desc_stats = sample_pdf.describe()
        
        return {
            'analysis_type': 'descriptive',
            'numeric_columns': numeric_cols.tolist(),
            'descriptive_stats': desc_stats.to_dict(),
            'npartitions': dask_df.npartitions
        }
    
    def _correlation_analysis(self, dask_df: "dd.DataFrame") -> Dict[str, Any]:
        """Perform correlation analysis robustly via sampling and NumPy."""
        numeric_cols = dask_df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            return {'error': 'Need at least 2 numeric columns for correlation analysis'}

        try:
            # Safely sample to avoid dask_expr head path
            sample_pdf = self._safe_head_df(dask_df, list(numeric_cols), 50000)
            sample_pdf = sample_pdf.apply(pd.to_numeric, errors='coerce')
            col_means = sample_pdf.mean(numeric_only=True)
            sample_pdf = sample_pdf.fillna(col_means)

            values = sample_pdf.to_numpy(dtype=float, copy=False)
            if values.ndim != 2 or values.shape[1] < 2:
                return {'error': 'Insufficient numeric data after cleaning for correlation'}

            import numpy as _np
            corr_arr = _np.corrcoef(values, rowvar=False)
            import pandas as _pd
            corr_matrix = _pd.DataFrame(corr_arr, index=numeric_cols, columns=numeric_cols)
        except Exception as inner_e:
            return {'error': f'Correlation failed: {inner_e}'}

        return {
            'analysis_type': 'correlation',
            'numeric_columns': numeric_cols.tolist(),
            'correlation_matrix': corr_matrix.to_dict(),
            'npartitions': dask_df.npartitions
        }
    
    def _groupby_analysis(self, dask_df: "dd.DataFrame") -> Dict[str, Any]:
        """Perform groupby analysis"""
        # Find categorical columns for grouping
        categorical_cols = dask_df.select_dtypes(include=['object', 'category']).columns
        numeric_cols = dask_df.select_dtypes(include=[np.number]).columns
        
        if len(categorical_cols) == 0 or len(numeric_cols) == 0:
            return {'error': 'Need both categorical and numeric columns for groupby analysis'}
        
        # Use first categorical column for grouping
        group_col = categorical_cols[0]
        agg_col = numeric_cols[0]
        
        # Perform groupby operation with robust fallback
        try:
            grouped = dask_df.groupby(group_col)[agg_col].agg(['mean', 'count', 'std']).compute()
        except Exception:
            sample_pdf = self._safe_head_df(dask_df, [group_col, agg_col], 50000)
            grouped = sample_pdf.groupby(group_col)[agg_col].agg(['mean', 'count', 'std'])
        
        return {
            'analysis_type': 'groupby',
            'group_column': group_col,
            'aggregation_column': agg_col,
            'grouped_stats': grouped.to_dict(),
            'npartitions': dask_df.npartitions
        }
    
    def _apply_dask_operation(self, dask_df: "dd.DataFrame", op_type: str, 
                             params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply specific Dask operation"""
        try:
            if op_type == 'filter':
                condition = params.get('condition')
                if condition:
                    result = dask_df.query(condition)
                else:
                    return {'error': 'Filter condition not provided'}
            
            elif op_type == 'select':
                columns = params.get('columns', [])
                if columns:
                    result = dask_df[columns]
                else:
                    return {'error': 'Columns not specified for select operation'}
            
            elif op_type == 'groupby':
                group_col = params.get('group_column')
                agg_col = params.get('aggregation_column')
                agg_func = params.get('agg_function', 'mean')
                
                if group_col and agg_col:
                    result = dask_df.groupby(group_col)[agg_col].agg(agg_func)
                else:
                    return {'error': 'Groupby parameters incomplete'}
            
            else:
                return {'error': f'Unknown operation type: {op_type}'}
            
            return {'result': result, 'success': True}
            
        except Exception as e:
            return {'error': str(e)}
    
    def _save_dask_results(self, results: Dict[str, Any], output_dir: str):
        """Save Dask analysis results"""
        os.makedirs(output_dir, exist_ok=True)
        
        import json
        # Make results JSON serializable
        serializable_results = {}
        for key, value in results.items():
            if key == 'final_result' and hasattr(value, 'to_dict'):
                serializable_results[key] = 'DataFrame saved separately'
            elif hasattr(value, 'to_dict'):
                serializable_results[key] = value.to_dict()
            else:
                serializable_results[key] = value
        
        with open(f"{output_dir}/dask_analysis_results.json", 'w') as f:
            json.dump(serializable_results, f, indent=2, default=str)
    
    def _save_intermediate_result(self, dask_df: "dd.DataFrame", operation_name: str, output_dir: str):
        """Save intermediate pipeline result"""
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Save as parquet for efficiency
            output_path = f"{output_dir}/intermediate_{operation_name}.parquet"
            # Handle Series case
            try:
                from dask.dataframe.core import Series as _DaskSeries
            except Exception:
                _DaskSeries = None
            if _DaskSeries is not None and isinstance(dask_df, _DaskSeries):
                dask_df.to_frame().to_parquet(output_path)
            else:
                # If object is a pandas object inadvertently, save via pandas
                if hasattr(dask_df, 'to_parquet'):
                    dask_df.to_parquet(output_path)
                else:
                    # compute to pandas and save
                    pdf = dask_df.compute()
                    if hasattr(pdf, 'to_parquet'):
                        pdf.to_parquet(output_path)
                    else:
                        pdf.to_csv(output_path.replace('.parquet', '.csv'), index=False)
            print(f"💾 Saved intermediate result: {output_path}")
        except Exception as e:
            print(f"⚠️  Could not save intermediate result: {e}")
    
    def big_data_pipeline(self, operations: List[Tuple[str, Callable]], data_source: Union[pd.DataFrame, str],
                          chunk_size: Optional[str] = None, n_workers: int = 4, memory_limit: str = '2GB',
                          save_intermediate: bool = False, output_dir: str = './quickinsights_output') -> Dict[str, Any]:
        """Execute a chain of big data operations with intermediate result saving."""
        if not self.dask_available:
            return {
                'error': 'Dask not available. Install with: pip install dask[complete]',
                'dask_available': False
            }
        
        start_time = time.time()
        
        try:
            # Setup Dask client
            self._setup_dask_client(n_workers, memory_limit)
            
            # Load data
            dask_df = self._prepare_dask_data(data_source, chunk_size)
            
            # Apply operations pipeline
            pipeline_results = []
            current_df = dask_df
            
            for i, (op_name, op_func) in enumerate(operations):
                print(f"🔄 Applying {op_name}...")
                
                # Apply operation directly
                try:
                    current_df = op_func(current_df)
                    pipeline_results.append({
                        'operation': op_name,
                        'success': True
                    })
                except Exception as e:
                    return {'error': f'Pipeline failed at {op_name}: {str(e)}'}
                
                # Save intermediate if requested
                if save_intermediate:
                    self._save_intermediate_result(current_df, op_name, output_dir)
            
            # Final computation
            final_result = current_df.compute()
            
            execution_time = time.time() - start_time
            
            results = {
                'pipeline_operations': pipeline_results,
                'final_result': final_result,
                'performance': {
                    'execution_time': execution_time,
                    'n_operations': len(operations),
                    'n_workers': n_workers,
                    'chunk_size': chunk_size
                }
            }
            
            return results
            
        except Exception as e:
            return {
                'error': str(e),
                'execution_time': time.time() - start_time,
                'dask_available': True
            }
        finally:
            self._cleanup_dask_client()

# Convenience functions
def smart_dask_analysis(*args, **kwargs):
    """Convenience function for smart_dask_analysis"""
    dask_integration = DaskIntegration()
    return dask_integration.smart_dask_analysis(*args, **kwargs)

def distributed_compute(*args, **kwargs):
    """Convenience function for distributed_compute"""
    dask_integration = DaskIntegration()
    return dask_integration.distributed_compute(*args, **kwargs)

def big_data_pipeline(*args, **kwargs):
    """Convenience function for big_data_pipeline"""
    dask_integration = DaskIntegration()
    return dask_integration.big_data_pipeline(*args, **kwargs)
