"""
Visualization Module
Creates charts and visualizations for error analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class ErrorVisualizer:
    """Class for creating visualizations of error data"""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize visualizer
        
        Args:
            output_dir: Directory to save visualization files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def plot_error_frequency(self, error_freq_df: pd.DataFrame, 
                            title: str = "Error Type Frequency",
                            save_path: Optional[str] = None):
        """Plot error type frequency"""
        if error_freq_df.empty:
            logger.warning("No data to plot")
            return
        
        plt.figure(figsize=(12, 6))
        sns.barplot(data=error_freq_df, x='errorType', y='count', palette='viridis')
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('Error Type', fontsize=12)
        plt.ylabel('Count', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(self.output_dir / save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved plot to {save_path}")
        else:
            plt.savefig(self.output_dir / "error_frequency.png", dpi=300, bbox_inches='tight')
        
        plt.close()
    
    def plot_temporal_trends(self, temporal_data: Dict, 
                            save_path: Optional[str] = None):
        """Plot temporal trends of errors"""
        if 'daily' not in temporal_data or temporal_data['daily'].empty:
            logger.warning("No temporal data to plot")
            return
        
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # Daily trends
        daily_df = temporal_data['daily']
        daily_pivot = daily_df.pivot(index='date', columns='errorType', values='count').fillna(0)
        
        daily_pivot.plot(kind='line', ax=axes[0], marker='o')
        axes[0].set_title('Daily Error Trends', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Date', fontsize=12)
        axes[0].set_ylabel('Error Count', fontsize=12)
        axes[0].legend(title='Error Type', bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[0].grid(True, alpha=0.3)
        
        # Hourly trends
        if 'hourly' in temporal_data and not temporal_data['hourly'].empty:
            hourly_df = temporal_data['hourly']
            hourly_pivot = hourly_df.pivot(index='hour', columns='errorType', values='count').fillna(0)
            
            hourly_pivot.plot(kind='bar', ax=axes[1], width=0.8)
            axes[1].set_title('Hourly Error Distribution', fontsize=14, fontweight='bold')
            axes[1].set_xlabel('Hour of Day', fontsize=12)
            axes[1].set_ylabel('Error Count', fontsize=12)
            axes[1].legend(title='Error Type', bbox_to_anchor=(1.05, 1), loc='upper left')
            axes[1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(self.output_dir / save_path, dpi=300, bbox_inches='tight')
        else:
            plt.savefig(self.output_dir / "temporal_trends.png", dpi=300, bbox_inches='tight')
        
        plt.close()
        logger.info("Temporal trends plot saved")
    
    def plot_collection_distribution(self, collection_df: pd.DataFrame,
                                    save_path: Optional[str] = None):
        """Plot error distribution across collections"""
        if collection_df.empty:
            logger.warning("No collection data to plot")
            return
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(collection_df, annot=True, fmt='.0f', cmap='YlOrRd', 
                   cbar_kws={'label': 'Error Count'})
        plt.title('Error Distribution by Collection', fontsize=16, fontweight='bold')
        plt.xlabel('Collection', fontsize=12)
        plt.ylabel('Error Type', fontsize=12)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(self.output_dir / save_path, dpi=300, bbox_inches='tight')
        else:
            plt.savefig(self.output_dir / "collection_distribution.png", dpi=300, bbox_inches='tight')
        
        plt.close()
        logger.info("Collection distribution plot saved")
    
    def plot_model_performance(self, model_results: Dict,
                              save_path: Optional[str] = None):
        """Plot ML model performance comparison"""
        if not model_results:
            logger.warning("No model results to plot")
            return
        
        models = list(model_results.keys())
        accuracies = [model_results[m]['accuracy'] for m in models]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(models, accuracies, color=['#3498db', '#2ecc71', '#e74c3c'])
        plt.title('Model Performance Comparison', fontsize=16, fontweight='bold')
        plt.xlabel('Model', fontsize=12)
        plt.ylabel('Accuracy', fontsize=12)
        plt.ylim(0, 1)
        
        # Add value labels on bars
        for bar, acc in zip(bars, accuracies):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{acc:.3f}', ha='center', va='bottom', fontweight='bold')
        
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(self.output_dir / save_path, dpi=300, bbox_inches='tight')
        else:
            plt.savefig(self.output_dir / "model_performance.png", dpi=300, bbox_inches='tight')
        
        plt.close()
        logger.info("Model performance plot saved")
    
    def plot_feature_importance(self, importance_df: pd.DataFrame,
                               save_path: Optional[str] = None):
        """Plot feature importance from ML models"""
        if importance_df.empty:
            logger.warning("No feature importance data to plot")
            return
        
        # Get top features for each model
        fig, axes = plt.subplots(len(importance_df['model'].unique()), 1, 
                                figsize=(12, 6 * len(importance_df['model'].unique())))
        
        if len(importance_df['model'].unique()) == 1:
            axes = [axes]
        
        for idx, model_name in enumerate(importance_df['model'].unique()):
            model_data = importance_df[importance_df['model'] == model_name].sort_values(
                'importance', ascending=False).head(10)
            
            sns.barplot(data=model_data, x='importance', y='feature', 
                       ax=axes[idx], palette='coolwarm')
            axes[idx].set_title(f'Top Features - {model_name}', fontsize=14, fontweight='bold')
            axes[idx].set_xlabel('Importance', fontsize=12)
            axes[idx].set_ylabel('Feature', fontsize=12)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(self.output_dir / save_path, dpi=300, bbox_inches='tight')
        else:
            plt.savefig(self.output_dir / "feature_importance.png", dpi=300, bbox_inches='tight')
        
        plt.close()
        logger.info("Feature importance plot saved")
    
    def create_summary_dashboard(self, patterns: Dict, model_results: Optional[Dict] = None):
        """Create a comprehensive summary dashboard"""
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # Error frequency
        if 'error_type_frequency' in patterns and not patterns['error_type_frequency'].empty:
            ax1 = fig.add_subplot(gs[0, 0])
            error_freq = patterns['error_type_frequency']
            sns.barplot(data=error_freq, x='errorType', y='count', ax=ax1, palette='viridis')
            ax1.set_title('Error Type Frequency', fontweight='bold')
            ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
        
        # Temporal trends
        if 'temporal' in patterns and 'daily' in patterns['temporal']:
            ax2 = fig.add_subplot(gs[0, 1])
            daily_df = patterns['temporal']['daily']
            if not daily_df.empty:
                daily_pivot = daily_df.pivot(index='date', columns='errorType', values='count').fillna(0)
                daily_pivot.plot(kind='line', ax=ax2, marker='o')
                ax2.set_title('Daily Error Trends', fontweight='bold')
                ax2.legend(title='Error Type', fontsize=8)
        
        # Model performance (if available)
        if model_results:
            ax3 = fig.add_subplot(gs[1, 0])
            models = list(model_results.keys())
            accuracies = [model_results[m]['accuracy'] for m in models]
            ax3.bar(models, accuracies, color=['#3498db', '#2ecc71', '#e74c3c'])
            ax3.set_title('Model Accuracy', fontweight='bold')
            ax3.set_ylabel('Accuracy')
            ax3.set_ylim(0, 1)
        
        # Collection distribution
        if 'collection_distribution' in patterns and not patterns['collection_distribution'].empty:
            ax4 = fig.add_subplot(gs[1, 1])
            sns.heatmap(patterns['collection_distribution'], annot=True, fmt='.0f', 
                       cmap='YlOrRd', ax=ax4, cbar_kws={'label': 'Count'})
            ax4.set_title('Errors by Collection', fontweight='bold')
        
        # Summary statistics text
        ax5 = fig.add_subplot(gs[2, :])
        ax5.axis('off')
        
        summary_text = "Summary Statistics:\n\n"
        if 'total_records' in patterns:
            summary_text += f"Total Records: {patterns.get('total_records', 'N/A')}\n"
        if 'error_types' in patterns:
            summary_text += f"Unique Error Types: {patterns.get('error_types', {}).get('count', 'N/A')}\n"
        
        ax5.text(0.1, 0.5, summary_text, fontsize=12, verticalalignment='center',
                family='monospace')
        
        plt.suptitle('MongoDB Error Analysis Dashboard', fontsize=18, fontweight='bold', y=0.98)
        plt.savefig(self.output_dir / "summary_dashboard.png", dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("Summary dashboard saved")
