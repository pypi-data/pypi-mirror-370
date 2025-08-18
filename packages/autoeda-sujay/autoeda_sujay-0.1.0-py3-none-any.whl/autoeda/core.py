import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Dict, Any, List, Union
import warnings
import logging
from datetime import datetime

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoEDAReport:
    """Container for EDA analysis results with comprehensive data insights"""
    
    def __init__(self, dataframe: pd.DataFrame, sample_size: Optional[int] = None):
        self.df = dataframe.copy()  # Create copy to avoid modifying original
        self.original_shape = dataframe.shape
        self.sample_size = sample_size
        self.results = {}
        self.analysis_timestamp = datetime.now()
        
        if sample_size and len(self.df) > sample_size:
            logger.info(f"Sampling {sample_size} rows from {len(self.df)} total rows")
            self.df = self.df.sample(n=sample_size, random_state=42)
        
        self._generate_analysis()
    
    def _generate_analysis(self):
        """Generate comprehensive analysis with enhanced features"""
        logger.info("🔍 Starting comprehensive dataset analysis...")
        
        try:
            # Basic info
            self.results['shape'] = self.df.shape
            self.results['original_shape'] = self.original_shape
            self.results['columns'] = list(self.df.columns)
            self.results['dtypes'] = self.df.dtypes.to_dict()
            
            memory_usage = self.df.memory_usage(deep=True)
            self.results['memory_usage'] = {
                'total_mb': memory_usage.sum() / 1024**2,
                'per_column': memory_usage.to_dict()
            }
            
            # Missing data analysis
            missing = self.df.isnull().sum()
            self.results['missing_data'] = missing[missing > 0].to_dict()
            self.results['missing_percentage'] = (missing / len(self.df) * 100).round(2).to_dict()
            
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                self.results['numeric_summary'] = self.df[numeric_cols].describe().to_dict()
                
                # Outlier detection using IQR method
                self.results['outliers'] = {}
                for col in numeric_cols:
                    Q1 = self.df[col].quantile(0.25)
                    Q3 = self.df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)][col]
                    self.results['outliers'][col] = len(outliers)
                
            cat_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
            if cat_cols:
                self.results['categorical_summary'] = {}
                for col in cat_cols:
                    unique_count = self.df[col].nunique()
                    self.results['categorical_summary'][col] = {
                        'unique_count': unique_count,
                        'top_values': self.df[col].value_counts().head().to_dict(),
                        'cardinality': 'high' if unique_count > len(self.df) * 0.5 else 'low'
                    }
            
            self.results['data_quality'] = {
                'duplicates': self.df.duplicated().sum(),
                'duplicate_percentage': (self.df.duplicated().sum() / len(self.df) * 100).round(2),
                'completeness': ((self.df.size - self.df.isnull().sum().sum()) / self.df.size * 100).round(2)
            }
            
            self._generate_recommendations()
            
            logger.info("✅ Analysis complete!")
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            raise
    
    def _generate_recommendations(self):
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Missing data recommendations
        if self.results['missing_data']:
            high_missing = [col for col, pct in self.results['missing_percentage'].items() if pct > 50]
            if high_missing:
                recommendations.append(f"Consider dropping columns with >50% missing data: {high_missing}")
        
        # Outlier recommendations
        if 'outliers' in self.results:
            high_outliers = [col for col, count in self.results['outliers'].items() if count > len(self.df) * 0.05]
            if high_outliers:
                recommendations.append(f"Investigate outliers in: {high_outliers}")
        
        # High cardinality recommendations
        if 'categorical_summary' in self.results:
            high_card = [col for col, info in self.results['categorical_summary'].items() 
                        if info['cardinality'] == 'high']
            if high_card:
                recommendations.append(f"Consider encoding high-cardinality columns: {high_card}")
        
        self.results['recommendations'] = recommendations
    
    def show_summary(self):
        """Display comprehensive analysis summary"""
        print("\n" + "="*60)
        print("📊 AUTOEDA COMPREHENSIVE ANALYSIS REPORT")
        print("="*60)
        print(f"📅 Generated: {self.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n📋 Dataset Overview:")
        print(f"   Original Shape: {self.results['original_shape'][0]:,} rows × {self.results['original_shape'][1]} columns")
        if self.results['shape'] != self.results['original_shape']:
            print(f"   Analyzed Shape: {self.results['shape'][0]:,} rows × {self.results['shape'][1]} columns (sampled)")
        print(f"   Memory Usage: {self.results['memory_usage']['total_mb']:.2f} MB")
        print(f"   Data Completeness: {self.results['data_quality']['completeness']:.1f}%")
        
        print(f"\n🔍 Data Quality:")
        print(f"   Duplicates: {self.results['data_quality']['duplicates']} ({self.results['data_quality']['duplicate_percentage']:.1f}%)")
        
        if self.results['missing_data']:
            print(f"\n❌ Missing Data:")
            for col, count in list(self.results['missing_data'].items())[:5]:  # Show top 5
                pct = self.results['missing_percentage'][col]
                print(f"   {col}: {count:,} ({pct:.1f}%)")
            if len(self.results['missing_data']) > 5:
                print(f"   ... and {len(self.results['missing_data']) - 5} more columns")
        else:
            print(f"\n✅ No missing data found!")
        
        # Numeric summary
        numeric_cols = [col for col in self.df.columns if col in self.results.get('numeric_summary', {})]
        if numeric_cols:
            print(f"\n🔢 Numerical Columns ({len(numeric_cols)}):")
            for col in numeric_cols[:3]:  # Show first 3
                stats = self.results['numeric_summary'][col]
                print(f"   {col}: mean={stats['mean']:.2f}, std={stats['std']:.2f}")
        
        # Categorical summary
        if 'categorical_summary' in self.results:
            print(f"\n📝 Categorical Columns ({len(self.results['categorical_summary'])}):")
            for col, info in list(self.results['categorical_summary'].items())[:3]:
                print(f"   {col}: {info['unique_count']} unique values")
        
        if self.results['recommendations']:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(self.results['recommendations'], 1):
                print(f"   {i}. {rec}")
    
    def plot_missing_data(self, figsize: tuple = (12, 6)):
        """Plot missing data visualization with enhanced styling"""
        if not self.results['missing_data']:
            print("✅ No missing data to visualize!")
            return
            
        missing_df = pd.DataFrame({
            'Column': list(self.results['missing_data'].keys()),
            'Missing_Count': list(self.results['missing_data'].values()),
            'Missing_Percentage': [self.results['missing_percentage'][col] for col in self.results['missing_data'].keys()]
        }).sort_values('Missing_Percentage', ascending=False)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Count plot
        bars1 = ax1.bar(range(len(missing_df)), missing_df['Missing_Count'], 
                       color='lightcoral', alpha=0.7)
        ax1.set_title('Missing Data Count', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Columns')
        ax1.set_ylabel('Missing Count')
        ax1.set_xticks(range(len(missing_df)))
        ax1.set_xticklabels(missing_df['Column'], rotation=45, ha='right')
        
        # Percentage plot
        bars2 = ax2.bar(range(len(missing_df)), missing_df['Missing_Percentage'], 
                       color='lightblue', alpha=0.7)
        ax2.set_title('Missing Data Percentage', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Columns')
        ax2.set_ylabel('Missing Percentage (%)')
        ax2.set_xticks(range(len(missing_df)))
        ax2.set_xticklabels(missing_df['Column'], rotation=45, ha='right')
        
        plt.tight_layout()
        plt.show()
    
    def plot_distributions(self):
        """Plot distributions for numerical columns"""
        numeric_cols = [col for col in self.df.columns if col in self.results.get('numeric_summary', {})]
        
        if not numeric_cols:
            print("No numerical columns to plot!")
            return
        
        n_cols = min(len(numeric_cols), 4)  # Max 4 plots
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        axes = axes.flatten()
        
        for i, col in enumerate(numeric_cols[:n_cols]):
            self.df[col].hist(bins=30, ax=axes[i], alpha=0.7)
            axes[i].set_title(f'Distribution of {col}')
            axes[i].set_xlabel(col)
            axes[i].set_ylabel('Frequency')
        
        # Hide empty subplots
        for i in range(n_cols, 4):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.show()
    
    def plot_correlation_matrix(self):
        """Plot correlation matrix for numerical columns"""
        numeric_cols = [col for col in self.df.columns if col in self.results.get('numeric_summary', {})]
        
        if len(numeric_cols) < 2:
            print("Need at least 2 numerical columns for correlation matrix!")
            return
        
        plt.figure(figsize=(10, 8))
        correlation_matrix = self.df[numeric_cols].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, linewidths=0.5)
        plt.title('Correlation Matrix')
        plt.tight_layout()
        plt.show()
    
    def generate_report(self, filename: Optional[str] = None) -> str:
        """Generate a comprehensive text report"""
        report_lines = [
            "="*60,
            "AUTOEDA COMPREHENSIVE ANALYSIS REPORT",
            "="*60,
            f"Generated: {self.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "DATASET OVERVIEW:",
            f"Shape: {self.results['shape'][0]:,} rows × {self.results['shape'][1]} columns",
            f"Memory Usage: {self.results['memory_usage']['total_mb']:.2f} MB",
            f"Data Completeness: {self.results['data_quality']['completeness']:.1f}%",
            ""
        ]
        
        # Add all analysis sections
        if self.results['missing_data']:
            report_lines.extend([
                "MISSING DATA:",
                *[f"  {col}: {count} ({self.results['missing_percentage'][col]:.1f}%)" 
                  for col, count in self.results['missing_data'].items()]
            ])
        
        if self.results['recommendations']:
            report_lines.extend([
                "",
                "RECOMMENDATIONS:",
                *[f"  {i}. {rec}" for i, rec in enumerate(self.results['recommendations'], 1)]
            ])
        
        report_text = "\n".join(report_lines)
        
        if filename:
            with open(filename, 'w') as f:
                f.write(report_text)
            logger.info(f"Report saved to {filename}")
        
        return report_text

def analyze(dataframe: pd.DataFrame, sample_size: Optional[int] = None, 
           quick_mode: bool = False) -> AutoEDAReport:
    """
    Perform automated exploratory data analysis on a pandas DataFrame
    
    Args:
        dataframe: pandas DataFrame to analyze
        sample_size: Optional sample size for large datasets (default: None)
        quick_mode: If True, performs faster analysis with fewer visualizations
        
    Returns:
        AutoEDAReport object with analysis results and visualization methods
        
    Raises:
        TypeError: If input is not a pandas DataFrame
        ValueError: If DataFrame is empty or invalid
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Input must be a pandas DataFrame, got {type(dataframe)}")
    
    if dataframe.empty:
        raise ValueError("DataFrame is empty - cannot perform analysis")
    
    if len(dataframe.columns) == 0:
        raise ValueError("DataFrame has no columns")
    
    if sample_size is None and len(dataframe) > 100000:
        logger.warning(f"Large dataset detected ({len(dataframe):,} rows). Consider using sample_size parameter.")
        sample_size = 50000
    
    logger.info(f"Starting AutoEDA analysis on dataset with shape {dataframe.shape}")
    
    return AutoEDAReport(dataframe, sample_size=sample_size)



