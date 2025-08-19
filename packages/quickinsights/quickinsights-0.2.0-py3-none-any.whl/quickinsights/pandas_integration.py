"""
QuickInsights - Pandas Integration Module

This module integrates the most powerful Pandas commands with intelligent automation
and enhanced functionality for QuickInsights library.
"""

import pandas as pd
import numpy as np
from typing import Union, List, Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')


class PandasIntegration:
    """
    Enhanced Pandas functionality with intelligent automation
    """
    
    def __init__(self):
        self.analysis_history = []
        self.performance_metrics = {}
    
    def smart_group_analysis(
        self, 
        df: pd.DataFrame, 
        group_columns: Optional[Union[str, List[str]]] = None,
        value_columns: Optional[Union[str, List[str]]] = None,
        auto_detect_groups: bool = True,
        auto_detect_values: bool = True,
        aggregation_functions: Optional[Dict[str, List[str]]] = None,
        include_visualizations: bool = True,
        save_results: bool = False,
        output_dir: str = "./quickinsights_output"
    ) -> Dict[str, Any]:
        """
        Intelligent group analysis with automatic detection and optimization
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
        group_columns : str or list, optional
            Columns to group by
        value_columns : str or list, optional
            Columns to aggregate
        auto_detect_groups : bool
            Automatically detect categorical columns for grouping
        auto_detect_values : bool
            Automatically detect numerical columns for aggregation
        aggregation_functions : dict, optional
            Custom aggregation functions for specific columns
        include_visualizations : bool
            Generate visualizations
        save_results : bool
            Save results to files
        output_dir : str
            Output directory for saved files
            
        Returns:
        --------
        dict : Comprehensive group analysis results
        """
        
        try:
            # Input validation
            if df.empty:
                raise ValueError("DataFrame is empty")
            
            # Auto-detect group columns if not specified
            if auto_detect_groups and group_columns is None:
                group_columns = self._auto_detect_group_columns(df)
                print(f"🔍 Auto-detected group columns: {group_columns}")
            
            # Auto-detect value columns if not specified
            if auto_detect_values and value_columns is None:
                value_columns = self._auto_detect_value_columns(df)
                print(f"🔍 Auto-detected value columns: {value_columns}")
            
            # Validate columns exist
            self._validate_columns(df, group_columns, value_columns)
            
            # Create default aggregation functions if not specified
            if aggregation_functions is None:
                aggregation_functions = self._create_default_aggregations(value_columns)
            
            # Perform group analysis
            print("📊 Performing intelligent group analysis...")
            
            # Basic groupby with aggregation
            grouped = df.groupby(group_columns).agg(aggregation_functions)
            
            # Enhanced statistics
            enhanced_stats = self._calculate_enhanced_statistics(df, group_columns, value_columns)
            
            # Performance metrics
            performance_metrics = self._calculate_performance_metrics(df, group_columns)
            
            # Create comprehensive results
            results = {
                'grouped_data': grouped,
                'enhanced_statistics': enhanced_stats,
                'performance_metrics': performance_metrics,
                'group_columns': group_columns,
                'value_columns': value_columns,
                'aggregation_functions': aggregation_functions,
                'data_shape': df.shape,
                'memory_usage': df.memory_usage(deep=True).sum() / 1024**2,  # MB
                'analysis_timestamp': pd.Timestamp.now()
            }
            
            # Generate visualizations if requested
            if include_visualizations:
                visualizations = self._generate_group_visualizations(df, group_columns, value_columns, output_dir)
                results['visualizations'] = visualizations
            
            # Save results if requested
            if save_results:
                self._save_group_analysis_results(results, output_dir)
            
            # Update analysis history
            self.analysis_history.append({
                'function': 'smart_group_analysis',
                'timestamp': pd.Timestamp.now(),
                'group_columns': group_columns,
                'value_columns': value_columns
            })
            
            print("✅ Group analysis completed successfully!")
            return results
            
        except Exception as e:
            print(f"❌ Error in smart_group_analysis: {str(e)}")
            raise
    
    def smart_pivot_table(
        self,
        df: pd.DataFrame,
        index_columns: Optional[Union[str, List[str]]] = None,
        columns: Optional[Union[str, List[str]]] = None,
        values: Optional[Union[str, List[str]]] = None,
        auto_detect_structure: bool = True,
        suggest_aggregations: bool = True,
        include_visualizations: bool = True,
        save_results: bool = False,
        output_dir: str = "./quickinsights_output"
    ) -> Dict[str, Any]:
        """
        Intelligent pivot table creation with automatic suggestions and optimization
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
        index_columns : str or list, optional
            Columns to use as index
        columns : str or list, optional
            Columns to use as columns
        values : str or list, optional
            Values to aggregate
        auto_detect_structure : bool
            Automatically detect optimal pivot table structure
        suggest_aggregations : bool
            Suggest best aggregation functions
        include_visualizations : bool
            Generate visualizations
        save_results : bool
            Save results to files
        output_dir : str
            Output directory for saved files
            
        Returns:
        --------
        dict : Comprehensive pivot table analysis results
        """
        
        try:
            # Input validation
            if df.empty:
                raise ValueError("DataFrame is empty")
            
            print("🔍 Analyzing data structure for optimal pivot table...")
            
            # Auto-detect optimal structure if requested
            if auto_detect_structure:
                detected_structure = self._detect_optimal_pivot_structure(df)
                index_columns = detected_structure.get('index', index_columns)
                columns = detected_structure.get('columns', columns)
                values = detected_structure.get('values', values)
                print(f"🎯 Auto-detected structure: Index={index_columns}, Columns={columns}, Values={values}")
            
            # Validate columns exist
            self._validate_pivot_columns(df, index_columns, columns, values)
            
            # Suggest best aggregation functions
            if suggest_aggregations:
                suggested_aggs = self._suggest_aggregation_functions(df, values)
                print(f"💡 Suggested aggregations: {suggested_aggs}")
            
            # Create pivot table
            print("📊 Creating intelligent pivot table...")
            
            # Create multiple pivot tables with different aggregations
            pivot_tables = {}
            for value_col in values:
                pivot_tables[value_col] = {}
                
                # Try different aggregation functions
                for agg_func in ['mean', 'sum', 'count', 'median']:
                    try:
                        pivot = df.pivot_table(
                            index=index_columns,
                            columns=columns,
                            values=value_col,
                            aggfunc=agg_func,
                            fill_value=0
                        )
                        pivot_tables[value_col][agg_func] = pivot
                    except Exception as e:
                        print(f"⚠️  Could not create pivot table with {agg_func}: {str(e)}")
            
            # Calculate insights
            insights = self._calculate_pivot_insights(pivot_tables, df, index_columns, columns, values)
            
            # Performance metrics
            performance_metrics = self._calculate_pivot_performance(df, index_columns, columns, values)
            
            # Create comprehensive results
            results = {
                'pivot_tables': pivot_tables,
                'insights': insights,
                'performance_metrics': performance_metrics,
                'structure': {
                    'index_columns': index_columns,
                    'columns': columns,
                    'values': values
                },
                'data_shape': df.shape,
                'memory_usage': df.memory_usage(deep=True).sum() / 1024**2,  # MB
                'analysis_timestamp': pd.Timestamp.now()
            }
            
            # Generate visualizations if requested
            if include_visualizations:
                visualizations = self._generate_pivot_visualizations(
                    pivot_tables, df, index_columns, columns, values, output_dir
                )
                results['visualizations'] = visualizations
            
            # Save results if requested
            if save_results:
                self._save_pivot_results(results, output_dir)
            
            # Update analysis history
            self.analysis_history.append({
                'function': 'smart_pivot_table',
                'timestamp': pd.Timestamp.now(),
                'structure': results['structure']
            })
            
            print("✅ Smart pivot table analysis completed successfully!")
            return results
            
        except Exception as e:
            print(f"❌ Error in smart_pivot_table: {str(e)}")
            raise
    
    def intelligent_merge(
        self,
        left_df: pd.DataFrame,
        right_df: pd.DataFrame,
        left_key: Optional[Union[str, List[str]]] = None,
        right_key: Optional[Union[str, List[str]]] = None,
        auto_detect_keys: bool = True,
        suggest_merge_strategy: bool = True,
        include_validation: bool = True,
        save_results: bool = False,
        output_dir: str = "./quickinsights_output"
    ) -> Dict[str, Any]:
        """
        Intelligent data merging with automatic key detection and strategy optimization
        
        Parameters:
        -----------
        left_df : pd.DataFrame
            Left dataframe for merging
        right_df : pd.DataFrame
            Right dataframe for merging
        left_key : str or list, optional
            Key columns in left dataframe
        right_key : str or list, optional
            Key columns in right dataframe
        auto_detect_keys : bool
            Automatically detect best merge keys
        suggest_merge_strategy : bool
            Suggest optimal merge strategy
        include_validation : bool
            Include data validation and quality checks
        save_results : bool
            Save results to files
        output_dir : str
            Output directory for saved files
            
        Returns:
        --------
        dict : Comprehensive merge analysis results
        """
        
        try:
            # Input validation
            if left_df.empty or right_df.empty:
                raise ValueError("One or both DataFrames are empty")
            
            print("🔍 Analyzing data for intelligent merging...")
            
            # Auto-detect merge keys if requested
            if auto_detect_keys:
                detected_keys = self._detect_optimal_merge_keys(left_df, right_df)
                left_key = detected_keys.get('left_key', left_key)
                right_key = detected_keys.get('right_key', right_key)
                print(f"🎯 Auto-detected keys: Left={left_key}, Right={right_key}")
            
            # If no keys detected, use default common columns
            if not left_key or not right_key:
                common_cols = list(set(left_df.columns) & set(right_df.columns))
                if common_cols:
                    left_key = [common_cols[0]]
                    right_key = [common_cols[0]]
                    print(f"🔧 Using default key: {common_cols[0]}")
                else:
                    raise ValueError("No common columns found for merging")
            
            # Validate keys exist
            self._validate_merge_keys(left_df, right_df, left_key, right_key)
            
            # Suggest merge strategy
            if suggest_merge_strategy:
                strategy = self._suggest_merge_strategy(left_df, right_df, left_key, right_key)
                print(f"💡 Suggested merge strategy: {strategy}")
            
            # Perform merge with different strategies
            merge_results = {}
            
            # 1. Inner merge
            print("📊 Performing inner merge...")
            inner_merge = left_df.merge(right_df, left_on=left_key, right_on=right_key, how='inner')
            merge_results['inner'] = inner_merge
            
            # 2. Left merge
            print("📊 Performing left merge...")
            left_merge = left_df.merge(right_df, left_on=left_key, right_on=right_key, how='left')
            merge_results['left'] = left_merge
            
            # 3. Right merge
            print("📊 Performing right merge...")
            right_merge = left_df.merge(right_df, left_on=left_key, right_on=right_key, how='right')
            merge_results['right'] = right_merge
            
            # 4. Outer merge
            print("📊 Performing outer merge...")
            outer_merge = left_df.merge(right_df, left_on=left_key, right_on=right_key, how='outer')
            merge_results['outer'] = outer_merge
            
            # Calculate merge insights
            insights = self._calculate_merge_insights(merge_results, left_df, right_df, left_key, right_key)
            
            # Data validation if requested
            validation_results = {}
            if include_validation:
                validation_results = self._validate_merge_results(merge_results, left_df, right_df)
            
            # Performance metrics
            performance_metrics = self._calculate_merge_performance(left_df, right_df, left_key, right_key)
            
            # Create comprehensive results
            results = {
                'merge_results': merge_results,
                'insights': insights,
                'validation_results': validation_results,
                'performance_metrics': performance_metrics,
                'merge_keys': {
                    'left_key': left_key,
                    'right_key': right_key
                },
                'data_shapes': {
                    'left_df': left_df.shape,
                    'right_df': right_df.shape,
                    'inner_merge': inner_merge.shape,
                    'left_merge': left_merge.shape,
                    'right_merge': right_merge.shape,
                    'outer_merge': outer_merge.shape
                },
                'memory_usage': {
                    'left_df_mb': left_df.memory_usage(deep=True).sum() / 1024**2,
                    'right_df_mb': right_df.memory_usage(deep=True).sum() / 1024**2,
                    'inner_merge_mb': inner_merge.memory_usage(deep=True).sum() / 1024**2
                },
                'analysis_timestamp': pd.Timestamp.now()
            }
            
            # Save results if requested
            if save_results:
                self._save_merge_results(results, output_dir)
            
            # Update analysis history
            self.analysis_history.append({
                'function': 'intelligent_merge',
                'timestamp': pd.Timestamp.now(),
                'merge_keys': results['merge_keys']
            })
            
            print("✅ Intelligent merge analysis completed successfully!")
            return results
            
        except Exception as e:
            print(f"❌ Error in intelligent_merge: {str(e)}")
            raise
    
    def _auto_detect_group_columns(self, df: pd.DataFrame) -> List[str]:
        """Automatically detect columns suitable for grouping"""
        categorical_cols = []
        
        for col in df.columns:
            # Check if column is categorical
            if df[col].dtype in ['object', 'category', 'string']:
                # Check unique values ratio (good for grouping if not too many unique values)
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio < 0.5:  # Less than 50% unique values
                    categorical_cols.append(col)
            
            # Check if column is datetime (good for time-based grouping)
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                categorical_cols.append(col)
        
        # If no categorical columns found, use first few columns with low cardinality
        if not categorical_cols:
            for col in df.columns[:5]:  # Check first 5 columns
                if df[col].nunique() < min(20, len(df) // 10):
                    categorical_cols.append(col)
        
        return categorical_cols[:3]  # Return max 3 columns
    
    def _auto_detect_value_columns(self, df: pd.DataFrame) -> List[str]:
        """Automatically detect columns suitable for aggregation"""
        numerical_cols = []
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Skip columns with too many missing values
                if df[col].isnull().sum() / len(df) < 0.5:
                    numerical_cols.append(col)
        
        return numerical_cols[:5]  # Return max 5 columns
    
    def _validate_columns(self, df: pd.DataFrame, group_columns: List[str], value_columns: List[str]):
        """Validate that specified columns exist in dataframe"""
        missing_group = [col for col in group_columns if col not in df.columns]
        missing_value = [col for col in value_columns if col not in df.columns]
        
        if missing_group:
            raise ValueError(f"Group columns not found: {missing_group}")
        if missing_value:
            raise ValueError(f"Value columns not found: {missing_value}")
    
    def _create_default_aggregations(self, value_columns: List[str]) -> Dict[str, List[str]]:
        """Create default aggregation functions for value columns"""
        aggregations = {}
        
        for col in value_columns:
            aggregations[col] = ['count', 'mean', 'std', 'min', 'max', 'median']
        
        return aggregations
    
    def _calculate_enhanced_statistics(
        self, 
        df: pd.DataFrame, 
        group_columns: List[str], 
        value_columns: List[str]
    ) -> Dict[str, Any]:
        """Calculate enhanced statistics beyond basic aggregation"""
        
        enhanced_stats = {}
        
        for group_col in group_columns:
            group_stats = {}
            
            for value_col in value_columns:
                if pd.api.types.is_numeric_dtype(df[value_col]):
                    # Calculate statistics for each group
                    group_values = df.groupby(group_col)[value_col]
                    
                    # Calculate statistics individually to avoid compatibility issues
                    group_stats[value_col] = {
                        'mean': group_values.mean(),
                        'std': group_values.std(),
                        'median': group_values.median(),
                        'q25': group_values.quantile(0.25),
                        'q75': group_values.quantile(0.75),
                        'iqr': group_values.quantile(0.75) - group_values.quantile(0.25),
                        'skewness': 0,  # Temporarily disabled due to compatibility issues
                        'kurtosis': 0,   # Temporarily disabled due to compatibility issues
                        'missing_count': group_values.apply(lambda x: x.isnull().sum()),
                        'unique_count': group_values.apply(lambda x: x.nunique())
                    }
            
            enhanced_stats[group_col] = group_stats
        
        return enhanced_stats
    
    def _calculate_performance_metrics(
        self, 
        df: pd.DataFrame, 
        group_columns: List[str]
    ) -> Dict[str, Any]:
        """Calculate performance metrics for grouping operations"""
        
        # Measure grouping performance
        start_time = pd.Timestamp.now()
        
        # Simple grouping operation for timing
        _ = df.groupby(group_columns).size()
        
        end_time = pd.Timestamp.now()
        grouping_time = (end_time - start_time).total_seconds() * 1000  # milliseconds
        
        # Calculate memory efficiency
        original_memory = df.memory_usage(deep=True).sum()
        
        # Estimate grouped memory usage
        grouped_memory = original_memory * 0.8  # Rough estimate
        
        return {
            'grouping_time_ms': grouping_time,
            'original_memory_mb': original_memory / 1024**2,
            'estimated_grouped_memory_mb': grouped_memory / 1024**2,
            'memory_efficiency': (original_memory - grouped_memory) / original_memory * 100
        }
    
    def _generate_group_visualizations(
        self, 
        df: pd.DataFrame, 
        group_columns: List[str], 
        value_columns: List[str], 
        output_dir: str
    ) -> Dict[str, str]:
        """Generate visualizations for group analysis"""
        
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
            
            # 1. Group size distribution
            if len(group_columns) == 1:
                plt.figure(figsize=(12, 6))
                group_sizes = df.groupby(group_columns[0]).size()
                group_sizes.plot(kind='bar')
                plt.title(f'Group Sizes by {group_columns[0]}')
                plt.xlabel(group_columns[0])
                plt.ylabel('Count')
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                viz_path = f"{output_dir}/group_sizes_{group_columns[0]}.png"
                plt.savefig(viz_path, dpi=300, bbox_inches='tight')
                plt.close()
                visualizations['group_sizes'] = viz_path
            
            # 2. Value distribution by group
            for value_col in value_columns[:3]:  # Limit to first 3 value columns
                if pd.api.types.is_numeric_dtype(df[value_col]):
                    plt.figure(figsize=(12, 6))
                    
                    # Box plot
                    plt.subplot(1, 2, 1)
                    df.boxplot(column=value_col, by=group_columns[0], ax=plt.gca())
                    plt.title(f'{value_col} Distribution by {group_columns[0]}')
                    plt.suptitle('')  # Remove default suptitle
                    
                    # Violin plot
                    plt.subplot(1, 2, 2)
                    sns.violinplot(data=df, x=group_columns[0], y=value_col)
                    plt.title(f'{value_col} Distribution by {group_columns[0]}')
                    plt.xticks(rotation=45)
                    
                    plt.tight_layout()
                    
                    viz_path = f"{output_dir}/distribution_{value_col}_by_{group_columns[0]}.png"
                    plt.savefig(viz_path, dpi=300, bbox_inches='tight')
                    plt.close()
                    visualizations[f'distribution_{value_col}'] = viz_path
            
            # 3. Heatmap for multiple groups
            if len(group_columns) >= 2 and len(value_columns) >= 1:
                plt.figure(figsize=(10, 8))
                
                # Create pivot table for heatmap
                pivot_data = df.pivot_table(
                    values=value_columns[0],
                    index=group_columns[0],
                    columns=group_columns[1],
                    aggfunc='mean',
                    fill_value=0
                )
                
                sns.heatmap(pivot_data, annot=True, fmt='.2f', cmap='YlOrRd')
                plt.title(f'{value_columns[0]} Heatmap by {group_columns[0]} and {group_columns[1]}')
                plt.tight_layout()
                
                viz_path = f"{output_dir}/heatmap_{value_columns[0]}.png"
                plt.savefig(viz_path, dpi=300, bbox_inches='tight')
                plt.close()
                visualizations['heatmap'] = viz_path
            
            print(f"📊 Generated {len(visualizations)} visualizations")
            return visualizations
            
        except ImportError:
            print("⚠️  Visualization libraries not available. Skipping visualizations.")
            return {}
        except Exception as e:
            print(f"⚠️  Error generating visualizations: {str(e)}")
            return {}
    
    def _save_group_analysis_results(self, results: Dict[str, Any], output_dir: str):
        """Save group analysis results to files"""
        
        try:
            import os
            import json
            from datetime import datetime
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Save grouped data to CSV
            if 'grouped_data' in results:
                csv_path = f"{output_dir}/grouped_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                results['grouped_data'].to_csv(csv_path)
                print(f"💾 Saved grouped data to: {csv_path}")
            
            # Save enhanced statistics to JSON
            if 'enhanced_statistics' in results:
                json_path = f"{output_dir}/enhanced_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                # Convert numpy types to native Python types for JSON serialization
                serializable_stats = self._make_json_serializable(results['enhanced_statistics'])
                
                with open(json_path, 'w') as f:
                    json.dump(serializable_stats, f, indent=2, default=str)
                
                print(f"💾 Saved enhanced statistics to: {json_path}")
            
            # Save performance metrics
            if 'performance_metrics' in results:
                metrics_path = f"{output_dir}/performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                serializable_metrics = self._make_json_serializable(results['performance_metrics'])
                
                with open(metrics_path, 'w') as f:
                    json.dump(serializable_metrics, f, indent=2, default=str)
                
                print(f"💾 Saved performance metrics to: {metrics_path}")
                
        except Exception as e:
            print(f"⚠️  Error saving results: {str(e)}")
    
    def _make_json_serializable(self, obj: Any) -> Any:
        """Convert complex/numpy/pandas types to JSON-serializable Python types."""
        
        # Handle pandas containers first
        if isinstance(obj, pd.DataFrame):
            # Column-wise lists preserves structure and is JSON friendly
            return {col: self._make_json_serializable(obj[col].tolist()) for col in obj.columns}
        if isinstance(obj, (pd.Series, pd.Index)):
            try:
                return self._make_json_serializable(obj.to_dict())
            except Exception:
                return self._make_json_serializable(list(obj))

        # Native containers
        if isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        if isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]

        # NumPy scalars/arrays
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()

        # Scalars including None/NaN
        try:
            import numpy as _np
            if _np.isscalar(obj):
                try:
                    import pandas as _pd
                    if _pd.isna(obj):
                        return None
                except Exception:
                    pass
                return obj
        except Exception:
            pass

        # Fallback: stringify unknown objects
        return str(obj)

    def _detect_optimal_pivot_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect optimal pivot table structure based on data characteristics"""
        
        structure = {}
        
        # Detect index columns (categorical with moderate cardinality)
        categorical_cols = []
        for col in df.columns:
            if df[col].dtype in ['object', 'category', 'string']:
                unique_ratio = df[col].nunique() / len(df)
                if 0.01 < unique_ratio < 0.3:  # Good for pivot index
                    categorical_cols.append((col, unique_ratio))
        
        # Sort by cardinality (lower is better for index)
        categorical_cols.sort(key=lambda x: x[1])
        structure['index'] = [col[0] for col in categorical_cols[:2]]  # Max 2 index columns
        
        # Detect column columns (categorical with low cardinality)
        column_cols = []
        for col in df.columns:
            if df[col].dtype in ['object', 'category', 'string']:
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio < 0.1:  # Very low cardinality for columns
                    column_cols.append((col, unique_ratio))
        
        column_cols.sort(key=lambda x: x[1])
        structure['columns'] = [col[0] for col in column_cols[:1]]  # Max 1 column column
        
        # Detect value columns (numerical)
        numerical_cols = []
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                if df[col].isnull().sum() / len(df) < 0.3:  # Not too many missing values
                    numerical_cols.append(col)
        
        structure['values'] = numerical_cols[:3]  # Max 3 value columns
        
        return structure
    
    def _validate_pivot_columns(self, df: pd.DataFrame, index_columns: List[str], 
                               columns: List[str], values: List[str]):
        """Validate that specified columns exist and are suitable for pivot table"""
        
        missing_index = [col for col in index_columns if col not in df.columns]
        missing_cols = [col for col in columns if col not in df.columns]
        missing_values = [col for col in values if col not in df.columns]
        
        if missing_index:
            raise ValueError(f"Index columns not found: {missing_index}")
        if missing_cols:
            raise ValueError(f"Column columns not found: {missing_cols}")
        if missing_values:
            raise ValueError(f"Value columns not found: {missing_values}")
        
        # Check for high cardinality in columns (can cause memory issues)
        for col in columns:
            if df[col].nunique() > 50:
                print(f"⚠️  Warning: Column '{col}' has high cardinality ({df[col].nunique()} unique values)")
    
    def _suggest_aggregation_functions(self, df: pd.DataFrame, values: List[str]) -> Dict[str, List[str]]:
        """Suggest best aggregation functions for each value column"""
        
        suggestions = {}
        
        for value_col in values:
            if pd.api.types.is_numeric_dtype(df[value_col]):
                # Check data characteristics
                has_negative = (df[value_col] < 0).any()
                has_zero = (df[value_col] == 0).any()
                has_outliers = self._has_outliers(df[value_col])
                
                # Suggest aggregations based on data characteristics
                if has_negative:
                    suggestions[value_col] = ['mean', 'median', 'std', 'min', 'max']
                elif has_outliers:
                    suggestions[value_col] = ['median', 'mean', 'q25', 'q75', 'count']
                else:
                    suggestions[value_col] = ['sum', 'mean', 'count', 'min', 'max']
                
                # Add count if not already included
                if 'count' not in suggestions[value_col]:
                    suggestions[value_col].append('count')
        
        return suggestions
    
    def _has_outliers(self, series: pd.Series) -> bool:
        """Check if series has outliers using IQR method"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        return ((series < lower_bound) | (series > upper_bound)).any()
    
    def _calculate_pivot_insights(self, pivot_tables: Dict, df: pd.DataFrame, 
                                 index_columns: List[str], columns: List[str], 
                                 values: List[str]) -> Dict[str, Any]:
        """Calculate insights from pivot tables"""
        
        insights = {}
        
        for value_col in values:
            if value_col in pivot_tables:
                value_insights = {}
                
                # Get the mean pivot table for analysis
                if 'mean' in pivot_tables[value_col]:
                    pivot = pivot_tables[value_col]['mean']
                    
                    # Calculate insights
                    value_insights['total_cells'] = pivot.size
                    value_insights['non_zero_cells'] = (pivot != 0).sum().sum()
                    value_insights['sparsity'] = 1 - (value_insights['non_zero_cells'] / value_insights['total_cells'])
                    
                    # Find patterns
                    value_insights['row_totals'] = pivot.sum(axis=1).to_dict()
                    value_insights['column_totals'] = pivot.sum(axis=0).to_dict()
                    
                    # Identify top performers
                    top_rows = pivot.sum(axis=1).nlargest(5)
                    top_cols = pivot.sum(axis=0).nlargest(5)
                    
                    value_insights['top_performing_rows'] = top_rows.to_dict()
                    value_insights['top_performing_columns'] = top_cols.to_dict()
                
                insights[value_col] = value_insights
        
        return insights
    
    def _calculate_pivot_performance(self, df: pd.DataFrame, index_columns: List[str], 
                                   columns: List[str], values: List[str]) -> Dict[str, Any]:
        """Calculate performance metrics for pivot table operations"""
        
        # Measure pivot table creation performance
        start_time = pd.Timestamp.now()
        
        # Simple pivot table operation for timing
        try:
            _ = df.pivot_table(
                index=index_columns[0] if index_columns else None,
                columns=columns[0] if columns else None,
                values=values[0] if values else None,
                aggfunc='mean'
            )
        except:
            pass
        
        end_time = pd.Timestamp.now()
        pivot_time = (end_time - start_time).total_seconds() * 1000  # milliseconds
        
        # Calculate memory efficiency
        original_memory = df.memory_usage(deep=True).sum()
        
        # Estimate pivot table memory usage
        estimated_pivot_memory = original_memory * 0.5  # Rough estimate
        
        return {
            'pivot_creation_time_ms': pivot_time,
            'original_memory_mb': original_memory / 1024**2,
            'estimated_pivot_memory_mb': estimated_pivot_memory / 1024**2,
            'memory_efficiency': (original_memory - estimated_pivot_memory) / original_memory * 100
        }
    
    def _generate_pivot_visualizations(self, pivot_tables: Dict, df: pd.DataFrame,
                                     index_columns: List[str], columns: List[str], 
                                     values: List[str], output_dir: str) -> Dict[str, str]:
        """Generate visualizations for pivot table analysis"""
        
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
            
            # 1. Heatmap for each value column
            for value_col in values:
                if value_col in pivot_tables and 'mean' in pivot_tables[value_col]:
                    pivot = pivot_tables[value_col]['mean']
                    
                    plt.figure(figsize=(12, 8))
                    sns.heatmap(pivot, annot=True, fmt='.2f', cmap='YlOrRd', cbar=True)
                    plt.title(f'{value_col} Heatmap')
                    plt.xlabel('Columns')
                    plt.ylabel('Index')
                    plt.xticks(rotation=45)
                    plt.yticks(rotation=0)
                    plt.tight_layout()
                    
                    viz_path = f"{output_dir}/pivot_heatmap_{value_col}.png"
                    plt.savefig(viz_path, dpi=300, bbox_inches='tight')
                    plt.close()
                    visualizations[f'heatmap_{value_col}'] = viz_path
            
            # 2. Bar chart for top performing rows/columns
            if values:
                value_col = values[0]
                if value_col in pivot_tables and 'mean' in pivot_tables[value_col]:
                    pivot = pivot_tables[value_col]['mean']
                    
                    # Top rows
                    plt.figure(figsize=(12, 6))
                    top_rows = pivot.sum(axis=1).nlargest(10)
                    top_rows.plot(kind='bar')
                    plt.title(f'Top 10 Rows by {value_col}')
                    plt.xlabel('Index')
                    plt.ylabel(value_col)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    
                    viz_path = f"{output_dir}/pivot_top_rows_{value_col}.png"
                    plt.savefig(viz_path, dpi=300, bbox_inches='tight')
                    plt.close()
                    visualizations[f'top_rows_{value_col}'] = viz_path
                    
                    # Top columns
                    plt.figure(figsize=(12, 6))
                    top_cols = pivot.sum(axis=0).nlargest(10)
                    top_cols.plot(kind='bar')
                    plt.title(f'Top 10 Columns by {value_col}')
                    plt.xlabel('Columns')
                    plt.ylabel(value_col)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    
                    viz_path = f"{output_dir}/pivot_top_columns_{value_col}.png"
                    plt.savefig(viz_path, dpi=300, bbox_inches='tight')
                    plt.close()
                    visualizations[f'top_columns_{value_col}'] = viz_path
            
            print(f"📊 Generated {len(visualizations)} pivot table visualizations")
            return visualizations
            
        except ImportError:
            print("⚠️  Visualization libraries not available. Skipping visualizations.")
            return {}
        except Exception as e:
            print(f"⚠️  Error generating pivot visualizations: {str(e)}")
            return {}
    
    def _save_pivot_results(self, results: Dict[str, Any], output_dir: str):
        """Save pivot table results to files"""
        
        try:
            import os
            import json
            from datetime import datetime
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Save pivot tables to CSV
            if 'pivot_tables' in results:
                for value_col, aggs in results['pivot_tables'].items():
                    for agg_func, pivot in aggs.items():
                        csv_path = f"{output_dir}/pivot_{value_col}_{agg_func}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                        pivot.to_csv(csv_path)
                        print(f"💾 Saved pivot table to: {csv_path}")
            
            # Save insights to JSON
            if 'insights' in results:
                json_path = f"{output_dir}/pivot_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                # Convert numpy types to native Python types for JSON serialization
                serializable_insights = self._make_json_serializable(results['insights'])
                
                with open(json_path, 'w') as f:
                    json.dump(serializable_insights, f, indent=2, default=str)
                
                print(f"💾 Saved pivot insights to: {json_path}")
            
            # Save performance metrics
            if 'performance_metrics' in results:
                metrics_path = f"{output_dir}/pivot_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                serializable_metrics = self._make_json_serializable(results['performance_metrics'])
                
                with open(metrics_path, 'w') as f:
                    json.dump(serializable_metrics, f, indent=2, default=str)
                
                print(f"💾 Saved pivot performance metrics to: {metrics_path}")
                
        except Exception as e:
            print(f"⚠️  Error saving pivot results: {str(e)}")

    def _detect_optimal_merge_keys(self, left_df: pd.DataFrame, right_df: pd.DataFrame) -> Dict[str, Any]:
        """Detect optimal merge keys based on data characteristics"""
        
        keys = {}
        
        # Find common columns between dataframes
        common_columns = set(left_df.columns) & set(right_df.columns)
        
        # Filter for potential key columns (categorical or low cardinality numerical)
        potential_keys = []
        for col in common_columns:
            # Check if column is categorical
            if left_df[col].dtype in ['object', 'category', 'string']:
                left_unique = left_df[col].nunique()
                right_unique = right_df[col].nunique()
                
                # Good key if moderate cardinality
                if 0.01 < (left_unique / len(left_df)) < 0.5 and 0.01 < (right_unique / len(right_df)) < 0.5:
                    potential_keys.append((col, left_unique, right_unique))
            
            # Check if column is numerical with low cardinality
            elif pd.api.types.is_numeric_dtype(left_df[col]):
                left_unique = left_df[col].nunique()
                right_unique = right_df[col].nunique()
                
                # Good key if very low cardinality (like ID columns)
                if (left_unique / len(left_df)) < 0.1 and (right_unique / len(right_df)) < 0.1:
                    potential_keys.append((col, left_unique, right_unique))
        
        # Sort by cardinality (lower is better for keys)
        potential_keys.sort(key=lambda x: (x[1] + x[2]) / 2)
        
        # Select best keys
        if potential_keys:
            best_key = potential_keys[0][0]
            keys['left_key'] = [best_key]
            keys['right_key'] = [best_key]
            
            # If we have multiple good keys, suggest composite key
            if len(potential_keys) >= 2:
                composite_keys = [k[0] for k in potential_keys[:2]]
                keys['left_key'] = composite_keys
                keys['right_key'] = composite_keys
        
        return keys
    
    def _validate_merge_keys(self, left_df: pd.DataFrame, right_df: pd.DataFrame, 
                            left_key: List[str], right_key: List[str]):
        """Validate that specified merge keys exist and are suitable"""
        
        missing_left = [col for col in left_key if col not in left_df.columns]
        missing_right = [col for col in right_key if col not in right_df.columns]
        
        if missing_left:
            raise ValueError(f"Left key columns not found: {missing_left}")
        if missing_right:
            raise ValueError(f"Right key columns not found: {missing_right}")
        
        # Check for high cardinality in keys (can cause memory issues)
        for col in left_key:
            if left_df[col].nunique() > 10000:
                print(f"⚠️  Warning: Left key column '{col}' has very high cardinality ({left_df[col].nunique()} unique values)")
        
        for col in right_key:
            if right_df[col].nunique() > 10000:
                print(f"⚠️  Warning: Right key column '{col}' has very high cardinality ({right_df[col].nunique()} unique values)")
    
    def _suggest_merge_strategy(self, left_df: pd.DataFrame, right_df: pd.DataFrame, 
                               left_key: List[str], right_key: List[str]) -> str:
        """Suggest optimal merge strategy based on data characteristics"""
        
        # Calculate overlap in key values
        left_keys = left_df[left_key].drop_duplicates()
        right_keys = right_df[right_key].drop_duplicates()
        
        # For single key columns
        if len(left_key) == 1:
            left_key_values = set(left_df[left_key[0]].dropna())
            right_key_values = set(right_df[right_key[0]].dropna())
            
            intersection = left_key_values & right_key_values
            left_only = left_key_values - right_key_values
            right_only = right_key_values - left_key_values
            
            total_keys = len(left_key_values | right_key_values)
            overlap_ratio = len(intersection) / total_keys if total_keys > 0 else 0
            
            if overlap_ratio > 0.8:
                return "inner (high overlap, use inner merge for clean data)"
            elif overlap_ratio > 0.5:
                return "left (moderate overlap, preserve left data structure)"
            elif len(left_only) > len(right_only):
                return "left (more left-only keys, preserve left data)"
            else:
                return "outer (low overlap, preserve all data)"
        
        return "inner (default strategy)"
    
    def _calculate_merge_insights(self, merge_results: Dict, left_df: pd.DataFrame, 
                                 right_df: pd.DataFrame, left_key: List[str], 
                                 right_key: List[str]) -> Dict[str, Any]:
        """Calculate insights from merge results"""
        
        insights = {}
        
        for merge_type, merged_df in merge_results.items():
            type_insights = {}
            
            # Basic statistics
            type_insights['rows'] = len(merged_df)
            type_insights['columns'] = len(merged_df.columns)
            
            # Duplicate analysis
            if len(left_key) == 1:
                key_col = left_key[0]
                duplicates = merged_df[merged_df.duplicated(subset=key_col, keep=False)]
                type_insights['duplicate_keys'] = len(duplicates)
                type_insights['duplicate_ratio'] = len(duplicates) / len(merged_df) if len(merged_df) > 0 else 0
            
            # Missing value analysis
            missing_counts = merged_df.isnull().sum()
            type_insights['missing_values'] = missing_counts.to_dict()
            type_insights['total_missing'] = missing_counts.sum()
            
            # Column overlap analysis
            left_cols = set(left_df.columns)
            right_cols = set(right_df.columns)
            type_insights['left_only_columns'] = list(left_cols - right_cols)
            type_insights['right_only_columns'] = list(right_cols - left_cols)
            type_insights['common_columns'] = list(left_cols & right_cols)
            
            insights[merge_type] = type_insights
        
        return insights
    
    def _validate_merge_results(self, merge_results: Dict, left_df: pd.DataFrame, 
                               right_df: pd.DataFrame) -> Dict[str, Any]:
        """Validate merge results for data quality"""
        
        validation = {}
        
        for merge_type, merged_df in merge_results.items():
            type_validation = {}
            
            # Check for data loss
            if merge_type == 'inner':
                expected_rows = len(left_df)  # Should be less than or equal
                actual_rows = len(merged_df)
                type_validation['data_loss'] = expected_rows - actual_rows
                type_validation['data_loss_ratio'] = (expected_rows - actual_rows) / expected_rows if expected_rows > 0 else 0
            
            # Check for unexpected columns
            expected_cols = len(left_df.columns) + len(right_df.columns)
            actual_cols = len(merged_df.columns)
            type_validation['unexpected_columns'] = actual_cols - expected_cols
            
            # Check for data type consistency
            type_validation['data_type_changes'] = []
            for col in left_df.columns:
                if col in merged_df.columns:
                    if left_df[col].dtype != merged_df[col].dtype:
                        type_validation['data_type_changes'].append({
                            'column': col,
                            'original_type': str(left_df[col].dtype),
                            'new_type': str(merged_df[col].dtype)
                        })
            
            validation[merge_type] = type_validation
        
        return validation
    
    def _calculate_merge_performance(self, left_df: pd.DataFrame, right_df: pd.DataFrame, 
                                   left_key: List[str], right_key: List[str]) -> Dict[str, Any]:
        """Calculate performance metrics for merge operations"""
        
        # Measure merge performance
        start_time = pd.Timestamp.now()
        
        # Simple merge operation for timing
        try:
            _ = left_df.merge(right_df, left_on=left_key, right_on=right_key, how='inner')
        except:
            pass
        
        end_time = pd.Timestamp.now()
        merge_time = (end_time - start_time).total_seconds() * 1000  # milliseconds
        
        # Calculate memory efficiency
        left_memory = left_df.memory_usage(deep=True).sum()
        right_memory = right_df.memory_usage(deep=True).sum()
        total_input_memory = left_memory + right_memory
        
        # Estimate merged memory usage
        estimated_merged_memory = total_input_memory * 0.8  # Rough estimate
        
        return {
            'merge_time_ms': merge_time,
            'left_memory_mb': left_memory / 1024**2,
            'right_memory_mb': right_memory / 1024**2,
            'total_input_memory_mb': total_input_memory / 1024**2,
            'estimated_merged_memory_mb': estimated_merged_memory / 1024**2,
            'memory_efficiency': (total_input_memory - estimated_merged_memory) / total_input_memory * 100
        }
    
    def _save_merge_results(self, results: Dict[str, Any], output_dir: str):
        """Save merge results to files"""
        
        try:
            import os
            import json
            from datetime import datetime
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Save merged dataframes to CSV
            if 'merge_results' in results:
                for merge_type, merged_df in results['merge_results'].items():
                    csv_path = f"{output_dir}/merge_{merge_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    merged_df.to_csv(csv_path, index=False)
                    print(f"💾 Saved {merge_type} merge to: {csv_path}")
            
            # Save insights to JSON
            if 'insights' in results:
                json_path = f"{output_dir}/merge_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                # Convert numpy types to native Python types for JSON serialization
                serializable_insights = self._make_json_serializable(results['insights'])
                
                with open(json_path, 'w') as f:
                    json.dump(serializable_insights, f, indent=2, default=str)
                
                print(f"💾 Saved merge insights to: {json_path}")
            
            # Save validation results
            if 'validation_results' in results:
                validation_path = f"{output_dir}/merge_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                serializable_validation = self._make_json_serializable(results['validation_results'])
                
                with open(validation_path, 'w') as f:
                    json.dump(serializable_validation, f, indent=2, default=str)
                
                print(f"💾 Saved merge validation to: {validation_path}")
            
            # Save performance metrics
            if 'performance_metrics' in results:
                metrics_path = f"{output_dir}/merge_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                serializable_metrics = self._make_json_serializable(results['performance_metrics'])
                
                with open(metrics_path, 'w') as f:
                    json.dump(serializable_metrics, f, indent=2, default=str)
                
                print(f"💾 Saved merge performance metrics to: {json_path}")
                
        except Exception as e:
            print(f"⚠️  Error saving merge results: {str(e)}")


# Convenience functions for easy access
def smart_group_analysis(
    df: pd.DataFrame, 
    group_columns: Optional[Union[str, List[str]]] = None,
    value_columns: Optional[Union[str, List[str]]] = None,
    auto_detect_groups: bool = True,
    auto_detect_values: bool = True,
    aggregation_functions: Optional[Dict[str, List[str]]] = None,
    include_visualizations: bool = True,
    save_results: bool = False,
    output_dir: str = "./quickinsights_output"
) -> Dict[str, Any]:
    """
    Convenience function for smart group analysis
    
    This is the main function users will call for intelligent group analysis.
    """
    
    integrator = PandasIntegration()
    return integrator.smart_group_analysis(
        df=df,
        group_columns=group_columns,
        value_columns=value_columns,
        auto_detect_groups=auto_detect_groups,
        auto_detect_values=auto_detect_values,
        aggregation_functions=aggregation_functions,
        include_visualizations=include_visualizations,
        save_results=save_results,
        output_dir=output_dir
    )


def smart_pivot_table(
    df: pd.DataFrame,
    index_columns: Optional[Union[str, List[str]]] = None,
    columns: Optional[Union[str, List[str]]] = None,
    values: Optional[Union[str, List[str]]] = None,
    auto_detect_structure: bool = True,
    suggest_aggregations: bool = True,
    include_visualizations: bool = True,
    save_results: bool = False,
    output_dir: str = "./quickinsights_output"
) -> Dict[str, Any]:
    """
    Convenience function for smart pivot table analysis
    
    This is the main function users will call for intelligent pivot table creation.
    """
    
    integrator = PandasIntegration()
    return integrator.smart_pivot_table(
        df=df,
        index_columns=index_columns,
        columns=columns,
        values=values,
        auto_detect_structure=auto_detect_structure,
        suggest_aggregations=suggest_aggregations,
        include_visualizations=include_visualizations,
        save_results=save_results,
        output_dir=output_dir
    )


def intelligent_merge(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    left_key: Optional[Union[str, List[str]]] = None,
    right_key: Optional[Union[str, List[str]]] = None,
    auto_detect_keys: bool = True,
    suggest_merge_strategy: bool = True,
    include_validation: bool = True,
    save_results: bool = False,
    output_dir: str = "./quickinsights_output"
) -> Dict[str, Any]:
    """
    Convenience function for intelligent data merging
    
    This is the main function users will call for intelligent data merging.
    """
    
    integrator = PandasIntegration()
    return integrator.intelligent_merge(
        left_df=left_df,
        right_df=right_df,
        left_key=left_key,
        right_key=right_key,
        auto_detect_keys=auto_detect_keys,
        suggest_merge_strategy=suggest_merge_strategy,
        include_validation=include_validation,
        save_results=save_results,
        output_dir=output_dir
    )


# Example usage and testing
if __name__ == "__main__":
    # Create sample data for testing
    np.random.seed(42)
    sample_data = pd.DataFrame({
        'category': np.random.choice(['A', 'B', 'C'], 1000),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 1000),
        'sales': np.random.normal(1000, 200, 1000),
        'profit': np.random.normal(100, 30, 1000),
        'customer_count': np.random.poisson(50, 1000)
    })
    
    print("🧪 Testing Pandas Integration Module...")
    print(f"📊 Sample data shape: {sample_data.shape}")
    
    # Test smart group analysis
    try:
        results = smart_group_analysis(
            df=sample_data,
            auto_detect_groups=True,
            auto_detect_values=True,
            include_visualizations=True,
            save_results=True
        )
        
        print("✅ Test completed successfully!")
        print(f"📈 Generated {len(results.get('visualizations', {}))} visualizations")
        print(f"💾 Results saved to: ./quickinsights_output/")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
