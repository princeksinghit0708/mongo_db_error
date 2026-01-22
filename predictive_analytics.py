"""
Predictive Analytics Module
Uses Machine Learning and LLM to predict error reasons and patterns
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ML Libraries
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import xgboost as xgb

# LLM Integration (using Google Gemini)
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
    logging.warning("Google Generative AI library not found. Install with: pip install google-generativeai")

# Import prompt templates
try:
    from llm_prompts import ErrorAnalysisPrompts
    HAS_PROMPTS = True
except ImportError:
    HAS_PROMPTS = False
    logging.warning("LLM prompts module not found. Using inline prompts.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictiveAnalytics:
    """Class for predictive analytics on error data"""
    
    def __init__(self, data: pd.DataFrame, gemini_api_key: Optional[str] = None):
        """
        Initialize predictive analytics
        
        Args:
            data: DataFrame containing error data
            gemini_api_key: Optional Google Gemini API key for LLM analysis
        """
        self.data = data.copy()
        self.gemini_api_key = gemini_api_key
        self.models = {}
        self.label_encoders = {}
        self.scaler = StandardScaler()
        
        if gemini_api_key and HAS_GEMINI:
            try:
                genai.configure(api_key=gemini_api_key)
                # Try to use Gemini 1.5 Pro (latest), fallback to gemini-pro if not available
                try:
                    self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
                    logger.info("Gemini 1.5 Pro model initialized")
                except Exception:
                    # Fallback to gemini-pro
                    self.gemini_model = genai.GenerativeModel('gemini-pro')
                    logger.info("Gemini Pro model initialized")
                self.llm_enabled = True
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {str(e)}")
                self.llm_enabled = False
                self.gemini_model = None
        else:
            self.llm_enabled = False
            self.gemini_model = None
            if not HAS_GEMINI:
                logger.warning("Google Generative AI library not installed. Install with: pip install google-generativeai")
    
    def prepare_features(self) -> pd.DataFrame:
        """Prepare features for machine learning"""
        df = self.data.copy()
        
        # Extract temporal features
        timestamp_cols = ['timestamp', 'dataSavedAtTimeStamp', 'eventTransactionTime', 'header_timestamp']
        for ts_col in timestamp_cols:
            if ts_col in df.columns:
                df['timestamp'] = pd.to_datetime(df[ts_col], errors='coerce')
                break
        
        if 'timestamp' in df.columns:
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['day_of_month'] = df['timestamp'].dt.day
            df['month'] = df['timestamp'].dt.month
        
        # Extract rawData features (for abc collection)
        if 'rawData' in df.columns:
            df['rawData_str'] = df['rawData'].astype(str)
            df['rawData_length'] = df['rawData_str'].str.len()
            df['rawData_is_numeric'] = df['rawData_str'].str.isdigit().astype(int)
            df['rawData_has_letters'] = df['rawData_str'].str.contains(r'[a-zA-Z]', regex=True).astype(int)
        
        # Extract account number features (for cde collection)
        if 'body_accountNumber' in df.columns:
            df['accountNumber_str'] = df['body_accountNumber'].astype(str)
            df['accountNumber_length'] = df['accountNumber_str'].str.len()
            df['accountNumber_is_numeric'] = df['accountNumber_str'].str.isdigit().astype(int)
        
        # Extract transaction amount features (for cde collection)
        if 'body_transactionAmount' in df.columns:
            df['transactionAmount'] = pd.to_numeric(df['body_transactionAmount'], errors='coerce')
            df['transactionAmount_log'] = np.log1p(df['transactionAmount'].fillna(0))
        
        # Extract merchant identifier features (for cde collection)
        if 'body_merchantIdentifier' in df.columns:
            df['merchantIdentifier_str'] = df['body_merchantIdentifier'].astype(str)
            df['merchantIdentifier_length'] = df['merchantIdentifier_str'].str.len()
        
        # Encode categorical features
        categorical_cols = ['type', 'source_collection']
        # Add cde collection specific categorical fields
        cde_categorical = ['header_businessCode', 'header_domain', 'header_channel', 
                          'header_countryCode', 'body_merchantCategoryCode']
        categorical_cols.extend([col for col in cde_categorical if col in df.columns])
        
        for col in categorical_cols:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        return df
    
    def train_error_prediction_model(self, target_column: Optional[str] = None, 
                                     test_size: float = 0.2) -> Dict:
        """
        Train ML models to predict error types
        
        Args:
            target_column: Column to predict (defaults to errorType or errorCode)
            test_size: Proportion of data for testing
            
        Returns:
            Dictionary with model performance metrics
        """
        # Auto-detect target column if not specified
        if target_column is None:
            if 'errorType' in self.data.columns:
                target_column = 'errorType'
            elif 'errorCode' in self.data.columns:
                target_column = 'errorCode'
            else:
                logger.error("No error column found (errorType or errorCode)")
                return {}
        
        if target_column not in self.data.columns:
            logger.error(f"Target column '{target_column}' not found in data")
            return {}
        
        # Prepare features
        df = self.prepare_features()
        
        # Select feature columns
        exclude_cols = [target_column, '_id', 'uuid', 'timestamp', 'rawData', 
                       'source_collection', 'type', 'errorType', 'errorCode',
                       'errorDetails', 'errorMessage', 'dataSavedAtTimeStamp',
                       'eventTransactionTime', 'header_timestamp', 'body_accountNumber',
                       'body_transactionAmount', 'body_merchantIdentifier']
        
        feature_cols = []
        for col in df.columns:
            if col not in exclude_cols and not col.endswith('_str'):
                if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                    feature_cols.append(col)
        
        if not feature_cols:
            logger.error("No suitable features found for training")
            return {}
        
        X = df[feature_cols].fillna(0)
        y = df[target_column]
        
        # Encode target if needed
        if y.dtype == 'object':
            le_target = LabelEncoder()
            y_encoded = le_target.fit_transform(y)
            self.label_encoders['target'] = le_target
        else:
            y_encoded = y
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=42, stratify=y_encoded
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        results = {}
        
        # Train Random Forest
        logger.info("Training Random Forest model...")
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf_model.fit(X_train_scaled, y_train)
        rf_pred = rf_model.predict(X_test_scaled)
        rf_accuracy = accuracy_score(y_test, rf_pred)
        
        self.models['random_forest'] = rf_model
        results['random_forest'] = {
            'accuracy': rf_accuracy,
            'classification_report': classification_report(y_test, rf_pred, output_dict=True),
            'feature_importance': dict(zip(feature_cols, rf_model.feature_importances_))
        }
        
        # Train Gradient Boosting
        logger.info("Training Gradient Boosting model...")
        gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        gb_model.fit(X_train_scaled, y_train)
        gb_pred = gb_model.predict(X_test_scaled)
        gb_accuracy = accuracy_score(y_test, gb_pred)
        
        self.models['gradient_boosting'] = gb_model
        results['gradient_boosting'] = {
            'accuracy': gb_accuracy,
            'classification_report': classification_report(y_test, gb_pred, output_dict=True),
            'feature_importance': dict(zip(feature_cols, gb_model.feature_importances_))
        }
        
        # Train XGBoost
        logger.info("Training XGBoost model...")
        xgb_model = xgb.XGBClassifier(n_estimators=100, random_state=42, eval_metric='mlogloss')
        xgb_model.fit(X_train_scaled, y_train)
        xgb_pred = xgb_model.predict(X_test_scaled)
        xgb_accuracy = accuracy_score(y_test, xgb_pred)
        
        self.models['xgboost'] = xgb_model
        results['xgboost'] = {
            'accuracy': xgb_accuracy,
            'classification_report': classification_report(y_test, xgb_pred, output_dict=True),
            'feature_importance': dict(zip(feature_cols, xgb_model.feature_importances_))
        }
        
        logger.info(f"Model training complete. Best accuracy: {max(rf_accuracy, gb_accuracy, xgb_accuracy):.4f}")
        
        return results
    
    def predict_error_reason_llm(self, error_record: Dict, model_name: Optional[str] = None) -> Dict:
        """
        Use Google Gemini LLM to analyze and explain error reasons
        
        Args:
            error_record: Dictionary containing error record
            model_name: Optional Gemini model name (defaults to initialized model)
            
        Returns:
            Dictionary with LLM analysis
        """
        if not self.llm_enabled:
            logger.warning("LLM not enabled. Provide Gemini API key to use this feature.")
            return {}
        
        try:
            # Use prompt template if available, otherwise use inline prompt
            if HAS_PROMPTS:
                prompt = ErrorAnalysisPrompts.get_error_analysis_prompt(error_record)
            else:
                # Fallback to inline prompt (backward compatibility)
                error_type = error_record.get('errorType') or error_record.get('errorCode', 'Unknown')
                error_details = error_record.get('errorDetails') or error_record.get('errorMessage', 'N/A')
                
                prompt = f"""You are an expert data analyst specializing in error pattern analysis.

Analyze the following error record from a MongoDB collection and provide a detailed analysis:

Error Record:
- Error Type/Code: {error_type}
- Error Details: {error_details}
- Type: {error_record.get('type', error_record.get('header_businessCode', 'Unknown'))}
- Collection: {error_record.get('source_collection', 'Unknown')}
- Timestamp: {error_record.get('timestamp', error_record.get('dataSavedAtTimeStamp', 'N/A'))}
"""
                
                # Add collection-specific fields
                if 'rawData' in error_record:
                    prompt += f"- Raw Data: {error_record.get('rawData', 'N/A')}\n"
                
                if 'header_domain' in error_record:
                    prompt += f"- Domain: {error_record.get('header_domain', 'N/A')}\n"
                    prompt += f"- Channel: {error_record.get('header_channel', 'N/A')}\n"
                    prompt += f"- Country Code: {error_record.get('header_countryCode', 'N/A')}\n"
                
                if 'body_transactionAmount' in error_record:
                    prompt += f"- Transaction Amount: {error_record.get('body_transactionAmount', 'N/A')}\n"
                    prompt += f"- Merchant Identifier: {error_record.get('body_merchantIdentifier', 'N/A')}\n"
                
                prompt += """
Please provide a comprehensive analysis covering:
1. The likely reason for this error
2. Why this error is occurring
3. Potential root causes
4. Recommendations to prevent this error

Format your response as a structured analysis with clear sections for each point above."""
            
            if HAS_GEMINI and self.gemini_model:
                # Use the specified model or default to initialized model
                if model_name:
                    model = genai.GenerativeModel(model_name)
                else:
                    model = self.gemini_model
                
                # Generate response
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=1000,
                    )
                )
                
                analysis_text = response.text
                
                return {
                    'llm_analysis': analysis_text,
                    'model_used': model_name or 'gemini-1.5-pro',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error in Gemini LLM analysis: {str(e)}")
            return {'error': str(e)}
    
    def analyze_error_frequency_patterns(self) -> Dict:
        """
        Analyze patterns in error frequency
        
        Returns:
            Dictionary with frequency pattern analysis
        """
        if self.data.empty:
            return {}
        
        df = self.data.copy()
        
        patterns = {}
        
        # Error frequency over time
        timestamp_cols = ['timestamp', 'dataSavedAtTimeStamp', 'eventTransactionTime']
        timestamp_col = None
        for ts_col in timestamp_cols:
            if ts_col in df.columns:
                timestamp_col = ts_col
                df['timestamp'] = pd.to_datetime(df[ts_col], errors='coerce')
                break
        
        if timestamp_col:
            df['date'] = df['timestamp'].dt.date
            
            # Daily error count
            daily_counts = df.groupby('date').size()
            if len(daily_counts) > 0:
                patterns['daily_trend'] = {
                    'mean': float(daily_counts.mean()),
                    'std': float(daily_counts.std()),
                    'trend': 'increasing' if len(daily_counts) > 1 and daily_counts.iloc[-1] > daily_counts.iloc[0] else 'decreasing'
                }
        
        # Error type frequency
        error_col = 'errorType' if 'errorType' in df.columns else 'errorCode'
        if error_col in df.columns:
            error_freq = df[error_col].value_counts().to_dict()
            patterns['error_type_frequency'] = error_freq
            
            # Most frequent error
            if error_freq:
                most_frequent = max(error_freq.items(), key=lambda x: x[1])
                patterns['most_frequent_error'] = {
                    'type': most_frequent[0],
                    'count': most_frequent[1],
                    'percentage': (most_frequent[1] / len(df)) * 100
                }
        
        # Collection-wise patterns
        if 'source_collection' in df.columns:
            collection_patterns = df.groupby('source_collection').size().to_dict()
            patterns['collection_distribution'] = collection_patterns
        
        return patterns
    
    def predict_future_errors(self, days_ahead: int = 7) -> pd.DataFrame:
        """
        Predict future error occurrences based on historical patterns
        
        Args:
            days_ahead: Number of days to predict ahead
            
        Returns:
            DataFrame with predictions
        """
        # Find timestamp and error columns
        timestamp_cols = ['timestamp', 'dataSavedAtTimeStamp', 'eventTransactionTime']
        timestamp_col = None
        for ts_col in timestamp_cols:
            if ts_col in self.data.columns:
                timestamp_col = ts_col
                break
        
        error_col = 'errorType' if 'errorType' in self.data.columns else 'errorCode'
        
        if not timestamp_col or error_col not in self.data.columns:
            logger.warning("Required columns not found for future prediction")
            return pd.DataFrame()
        
        df = self.data.copy()
        df['timestamp'] = pd.to_datetime(df[timestamp_col], errors='coerce')
        df['date'] = df['timestamp'].dt.date
        
        # Calculate daily error rates by type
        daily_errors = df.groupby(['date', error_col]).size().reset_index(name='count')
        daily_errors.rename(columns={error_col: 'errorType'}, inplace=True)
        
        # Simple moving average prediction
        predictions = []
        for error_type in df['errorType'].unique():
            error_data = daily_errors[daily_errors['errorType'] == error_type]
            if len(error_data) > 0:
                avg_daily = error_data['count'].mean()
                predicted_count = avg_daily * days_ahead
                
                predictions.append({
                    'errorType': error_type,
                    'predicted_count_next_7_days': predicted_count,
                    'avg_daily_rate': avg_daily,
                    'confidence': 'medium'  # Could be enhanced with statistical confidence intervals
                })
        
        return pd.DataFrame(predictions)
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance from trained models"""
        if not self.models:
            logger.warning("No models trained yet. Train models first.")
            return pd.DataFrame()
        
        importance_data = []
        for model_name, model in self.models.items():
            if hasattr(model, 'feature_importances_'):
                # Get feature names from the last prepared dataset
                df = self.prepare_features()
                exclude_cols = ['errorType', 'errorCode', '_id', 'uuid', 'timestamp', 
                               'rawData', 'source_collection', 'type', 'errorDetails',
                               'errorMessage', 'dataSavedAtTimeStamp', 'eventTransactionTime']
                feature_cols = [col for col in df.columns if col not in exclude_cols]
                feature_cols = [col for col in feature_cols 
                              if df[col].dtype in ['int64', 'float64', 'int32', 'float32']]
                
                importances = model.feature_importances_
                for feature, importance in zip(feature_cols, importances):
                    importance_data.append({
                        'model': model_name,
                        'feature': feature,
                        'importance': importance
                    })
        
        return pd.DataFrame(importance_data)
