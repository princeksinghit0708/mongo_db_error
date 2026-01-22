"""
Main Execution Script
Orchestrates the entire error analysis and predictive analytics pipeline
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Optional
import logging

from mongodb_connector import MongoDBConnector
from error_analyzer import ErrorAnalyzer
from predictive_analytics import PredictiveAnalytics
from visualizer import ErrorVisualizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorAnalysisPipeline:
    """Main pipeline for error analysis and predictive analytics"""
    
    def __init__(self, connection_string: str, database_name: str, 
                 gemini_api_key: Optional[str] = None):
        """
        Initialize the pipeline
        
        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database
            gemini_api_key: Optional Google Gemini API key for LLM analysis
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.gemini_api_key = gemini_api_key
        
        self.connector = None
        self.analyzer = None
        self.predictor = None
        self.visualizer = ErrorVisualizer()
        
    def run_full_analysis(self, collection_names: Optional[list] = None,
                         limit: Optional[int] = None):
        """
        Run the complete analysis pipeline
        
        Args:
            collection_names: Optional list of specific collections to analyze
            limit: Optional limit on documents per collection
        """
        logger.info("=" * 60)
        logger.info("Starting MongoDB Error Analysis Pipeline")
        logger.info("=" * 60)
        
        # Step 1: Connect to MongoDB
        logger.info("\n[Step 1] Connecting to MongoDB...")
        self.connector = MongoDBConnector(self.connection_string, self.database_name)
        if not self.connector.connect():
            logger.error("Failed to connect to MongoDB. Exiting.")
            return
        
        try:
            # Step 2: Read collections
            logger.info("\n[Step 2] Reading MongoDB collections...")
            if collection_names:
                data_dict = self.connector.read_multiple_collections(collection_names, limit=limit)
            else:
                # Auto-detect error collections
                data_dict = self.connector.get_error_collections()
            
            if not data_dict:
                logger.error("No data found in collections. Exiting.")
                return
            
            logger.info(f"Successfully read {len(data_dict)} collections")
            
            # Step 3: Analyze error patterns
            logger.info("\n[Step 3] Analyzing error patterns...")
            self.analyzer = ErrorAnalyzer(data_dict)
            
            # Get error patterns
            patterns = self.analyzer.get_error_patterns()
            summary = self.analyzer.get_summary_statistics()
            
            logger.info(f"Total records analyzed: {summary.get('total_records', 0)}")
            logger.info(f"Unique error types: {summary.get('error_types', {}).get('count', 0)}")
            
            # Step 4: Predictive Analytics
            logger.info("\n[Step 4] Running predictive analytics...")
            combined_df = self.analyzer.combined_df
            
            if not combined_df.empty:
                self.predictor = PredictiveAnalytics(combined_df, self.gemini_api_key)
                
                # Train ML models
                logger.info("Training machine learning models...")
                model_results = self.predictor.train_error_prediction_model()
                
                # Analyze frequency patterns
                frequency_patterns = self.predictor.analyze_error_frequency_patterns()
                
                # Predict future errors
                future_predictions = self.predictor.predict_future_errors(days_ahead=7)
                
                # Get feature importance
                feature_importance = self.predictor.get_feature_importance()
                
                logger.info("Predictive analytics complete")
            else:
                logger.warning("No data available for predictive analytics")
                model_results = {}
                frequency_patterns = {}
                future_predictions = pd.DataFrame()
                feature_importance = pd.DataFrame()
            
            # Step 5: LLM Analysis (sample)
            llm_analysis = {}
            if self.gemini_api_key and not combined_df.empty:
                logger.info("\n[Step 5] Running Gemini LLM analysis on sample errors...")
                # Analyze a sample of each error type
                error_col = 'errorType' if 'errorType' in combined_df.columns else 'errorCode'
                if error_col in combined_df.columns:
                    sample_errors = combined_df.groupby(error_col).first().to_dict('index')
                    for error_type, record in list(sample_errors.items())[:3]:  # Limit to 3 for cost
                        logger.info(f"Analyzing error type: {error_type}")
                        analysis = self.predictor.predict_error_reason_llm(record)
                        if analysis:
                            llm_analysis[error_type] = analysis
            
            # Step 6: Generate visualizations
            logger.info("\n[Step 6] Generating visualizations...")
            self._generate_visualizations(patterns, model_results, feature_importance)
            
            # Step 7: Generate report
            logger.info("\n[Step 7] Generating analysis report...")
            self._generate_report(patterns, summary, model_results, frequency_patterns, 
                               future_predictions, llm_analysis)
            
            logger.info("\n" + "=" * 60)
            logger.info("Analysis Pipeline Complete!")
            logger.info("=" * 60)
            logger.info(f"Results saved in 'output' directory")
            
        finally:
            # Cleanup
            self.connector.disconnect()
    
    def _generate_visualizations(self, patterns: dict, model_results: dict, 
                                feature_importance: pd.DataFrame):
        """Generate all visualizations"""
        # Error frequency
        if 'error_type_frequency' in patterns and not patterns['error_type_frequency'].empty:
            self.visualizer.plot_error_frequency(patterns['error_type_frequency'])
        
        # Temporal trends
        if 'temporal' in patterns:
            self.visualizer.plot_temporal_trends(patterns['temporal'])
        
        # Collection distribution
        if 'collection_distribution' in patterns and not patterns['collection_distribution'].empty:
            self.visualizer.plot_collection_distribution(patterns['collection_distribution'])
        
        # Model performance
        if model_results:
            self.visualizer.plot_model_performance(model_results)
        
        # Feature importance
        if not feature_importance.empty:
            self.visualizer.plot_feature_importance(feature_importance)
        
        # Summary dashboard
        self.visualizer.create_summary_dashboard(patterns, model_results)
    
    def _generate_report(self, patterns: dict, summary: dict, model_results: dict,
                        frequency_patterns: dict, future_predictions: pd.DataFrame,
                        llm_analysis: dict):
        """Generate comprehensive analysis report"""
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'summary': summary,
            'error_patterns': {},
            'predictive_analytics': {},
            'recommendations': []
        }
        
        # Error patterns
        if 'error_type_frequency' in patterns:
            report['error_patterns']['error_frequency'] = patterns['error_type_frequency'].to_dict('records')
        
        if 'most_frequent_error' in frequency_patterns:
            report['error_patterns']['most_frequent'] = frequency_patterns['most_frequent_error']
        
        # Predictive analytics
        if model_results:
            report['predictive_analytics']['model_performance'] = {
                model: {
                    'accuracy': results['accuracy'],
                    'best_model': max(model_results.items(), key=lambda x: x[1]['accuracy'])[0]
                }
                for model, results in model_results.items()
            }
        
        if not future_predictions.empty:
            report['predictive_analytics']['future_predictions'] = future_predictions.to_dict('records')
        
        # LLM Analysis
        if llm_analysis:
            report['llm_analysis'] = llm_analysis
        
        # Generate recommendations
        recommendations = []
        
        if 'most_frequent_error' in frequency_patterns:
            most_freq = frequency_patterns['most_frequent_error']
            recommendations.append(
                f"Priority: Address '{most_freq['type']}' errors - they account for "
                f"{most_freq['percentage']:.2f}% of all errors"
            )
        
        if model_results:
            best_model = max(model_results.items(), key=lambda x: x[1]['accuracy'])
            recommendations.append(
                f"Best predictive model: {best_model[0]} with {best_model[1]['accuracy']:.2%} accuracy"
            )
        
        if not future_predictions.empty:
            top_predicted = future_predictions.nlargest(1, 'predicted_count_next_7_days')
            if not top_predicted.empty:
                rec = top_predicted.iloc[0]
                recommendations.append(
                    f"Expected increase: '{rec['errorType']}' errors predicted to occur "
                    f"{rec['predicted_count_next_7_days']:.0f} times in next 7 days"
                )
        
        report['recommendations'] = recommendations
        
        # Save report
        report_path = self.visualizer.output_dir / "analysis_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Report saved to {report_path}")
        
        # Also save as readable text
        self._save_text_report(report)
    
    def _save_text_report(self, report: dict):
        """Save a human-readable text report"""
        report_path = self.visualizer.output_dir / "analysis_report.txt"
        
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("MONGODB ERROR ANALYSIS REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Analysis Date: {report['analysis_timestamp']}\n\n")
            
            # Summary
            f.write("SUMMARY\n")
            f.write("-" * 80 + "\n")
            summary = report['summary']
            f.write(f"Total Records: {summary.get('total_records', 'N/A')}\n")
            f.write(f"Collections Analyzed: {summary.get('collections_analyzed', 'N/A')}\n")
            if 'error_types' in summary:
                f.write(f"Unique Error Types: {summary['error_types']['count']}\n")
                f.write(f"Error Types: {', '.join(summary['error_types']['list'])}\n")
            f.write("\n")
            
            # Error Patterns
            if 'error_patterns' in report and 'error_frequency' in report['error_patterns']:
                f.write("ERROR FREQUENCY\n")
                f.write("-" * 80 + "\n")
                for error in report['error_patterns']['error_frequency']:
                    f.write(f"{error['errorType']}: {error['count']} ({error['percentage']}%)\n")
                f.write("\n")
            
            # Predictive Analytics
            if 'predictive_analytics' in report:
                f.write("PREDICTIVE ANALYTICS\n")
                f.write("-" * 80 + "\n")
                if 'model_performance' in report['predictive_analytics']:
                    for model, perf in report['predictive_analytics']['model_performance'].items():
                        if 'accuracy' in perf:
                            f.write(f"{model}: {perf['accuracy']:.2%} accuracy\n")
                f.write("\n")
            
            # Recommendations
            if report['recommendations']:
                f.write("RECOMMENDATIONS\n")
                f.write("-" * 80 + "\n")
                for i, rec in enumerate(report['recommendations'], 1):
                    f.write(f"{i}. {rec}\n")
                f.write("\n")
            
            # LLM Analysis
            if 'llm_analysis' in report:
                f.write("LLM ERROR ANALYSIS\n")
                f.write("-" * 80 + "\n")
                for error_type, analysis in report['llm_analysis'].items():
                    f.write(f"\n{error_type}:\n")
                    if 'llm_analysis' in analysis:
                        f.write(f"{analysis['llm_analysis']}\n")
        
        logger.info(f"Text report saved to {report_path}")


def main():
    """Main entry point"""
    # Configuration - Update these with your MongoDB connection details
    MONGODB_CONNECTION_STRING = os.getenv(
        'MONGODB_URI', 
        'mongodb://localhost:27017/'  # Default local connection
    )
    
    DATABASE_NAME = os.getenv('MONGODB_DATABASE', 'your_database_name')
    
    # Optional: Google Gemini API key for LLM analysis
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', None)
    
    # Optional: Specify collections to analyze (None = auto-detect)
    COLLECTIONS_TO_ANALYZE = None  # e.g., ['abc', 'errors', 'error_logs']
    
    # Optional: Limit documents per collection (None = all)
    DOCUMENT_LIMIT = None  # e.g., 10000
    
    # Create and run pipeline
    pipeline = ErrorAnalysisPipeline(
        connection_string=MONGODB_CONNECTION_STRING,
        database_name=DATABASE_NAME,
        gemini_api_key=GEMINI_API_KEY
    )
    
    pipeline.run_full_analysis(
        collection_names=COLLECTIONS_TO_ANALYZE,
        limit=DOCUMENT_LIMIT
    )


if __name__ == "__main__":
    main()
