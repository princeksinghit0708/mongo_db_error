"""
LLM Prompt Templates for Error Analysis
Contains reusable prompt templates for Gemini LLM analysis
"""

from typing import Dict


class ErrorAnalysisPrompts:
    """Prompt templates for error analysis using LLM"""
    
    @staticmethod
    def get_error_analysis_prompt(error_record: Dict) -> str:
        """
        Generate a comprehensive prompt for error analysis
        
        Args:
            error_record: Dictionary containing error record data
            
        Returns:
            Formatted prompt string for LLM
        """
        # Extract error information
        error_type = error_record.get('errorType') or error_record.get('errorCode', 'Unknown')
        error_details = error_record.get('errorDetails') or error_record.get('errorMessage', 'N/A')
        data_type = error_record.get('type', error_record.get('header_businessCode', 'Unknown'))
        collection = error_record.get('source_collection', 'Unknown')
        timestamp = error_record.get('timestamp', error_record.get('dataSavedAtTimeStamp', 'N/A'))
        
        # Build base prompt
        prompt = f"""You are an expert data analyst specializing in error pattern analysis and root cause investigation.

Analyze the following error record from a MongoDB collection and provide a detailed, actionable analysis:

═══════════════════════════════════════════════════════════════
ERROR RECORD DETAILS
═══════════════════════════════════════════════════════════════
Error Type/Code: {error_type}
Error Details: {error_details}
Data Type/Business Code: {data_type}
Source Collection: {collection}
Timestamp: {timestamp}
"""
        
        # Add collection-specific fields dynamically
        if 'rawData' in error_record:
            prompt += f"Raw Data: {error_record.get('rawData', 'N/A')}\n"
        
        if 'header_domain' in error_record:
            prompt += f"\nBusiness Context:\n"
            prompt += f"  - Domain: {error_record.get('header_domain', 'N/A')}\n"
            prompt += f"  - Channel: {error_record.get('header_channel', 'N/A')}\n"
            prompt += f"  - Country Code: {error_record.get('header_countryCode', 'N/A')}\n"
            prompt += f"  - Processing Service: {error_record.get('header_processingMSName', 'N/A')}\n"
        
        if 'body_transactionAmount' in error_record:
            prompt += f"\nTransaction Details:\n"
            prompt += f"  - Transaction Amount: {error_record.get('body_transactionAmount', 'N/A')}\n"
            prompt += f"  - Merchant Identifier: {error_record.get('body_merchantIdentifier', 'N/A')}\n"
            prompt += f"  - Account Number: {error_record.get('body_accountNumber', 'N/A')[:20]}...\n" if error_record.get('body_accountNumber') else ""
        
        prompt += """
═══════════════════════════════════════════════════════════════
ANALYSIS REQUIREMENTS
═══════════════════════════════════════════════════════════════

Please provide a comprehensive analysis covering the following aspects:

1. ERROR REASON ANALYSIS
   - What is the likely technical reason for this error?
   - What specific condition or data state triggered it?
   - Is this a data validation, processing, or system error?

2. ROOT CAUSE INVESTIGATION
   - Why is this error occurring in the system?
   - What underlying issues might be causing this pattern?
   - Are there any data quality or system configuration problems?

3. FREQUENCY & PATTERN ANALYSIS
   - Based on the error type and context, how critical is this error?
   - What patterns can be observed (timing, data characteristics, etc.)?
   - Is this likely a recurring issue or a one-time occurrence?

4. PREVENTION RECOMMENDATIONS
   - What immediate actions can be taken to prevent this error?
   - What long-term solutions or improvements should be implemented?
   - Are there any data validation or preprocessing steps that could help?

5. BUSINESS IMPACT
   - What is the potential business impact of this error?
   - Which processes or transactions are affected?
   - What is the urgency level for resolution?

═══════════════════════════════════════════════════════════════

Format your response as a structured analysis with:
- Clear sections for each requirement above
- Specific, actionable insights
- Technical details where relevant
- Business context when applicable

Be concise but thorough in your analysis."""
        
        return prompt
    
    @staticmethod
    def get_batch_error_analysis_prompt(error_summary: Dict) -> str:
        """
        Generate a prompt for analyzing multiple errors at once
        
        Args:
            error_summary: Dictionary containing aggregated error statistics
            
        Returns:
            Formatted prompt string for batch analysis
        """
        prompt = f"""You are an expert data analyst specializing in error pattern analysis.

Analyze the following aggregated error patterns from MongoDB collections:

═══════════════════════════════════════════════════════════════
ERROR PATTERN SUMMARY
═══════════════════════════════════════════════════════════════
"""
        
        if 'error_types' in error_summary:
            prompt += "Error Types and Frequencies:\n"
            for error_type, count in error_summary['error_types'].items():
                prompt += f"  - {error_type}: {count} occurrences\n"
        
        if 'collections' in error_summary:
            prompt += "\nCollection Distribution:\n"
            for collection, count in error_summary['collections'].items():
                prompt += f"  - {collection}: {count} errors\n"
        
        if 'temporal_patterns' in error_summary:
            prompt += "\nTemporal Patterns:\n"
            prompt += f"  - {error_summary['temporal_patterns']}\n"
        
        prompt += """
═══════════════════════════════════════════════════════════════

Please provide:
1. Overall error pattern analysis
2. Common root causes across errors
3. Priority recommendations for error reduction
4. System-wide improvement suggestions

Format your response as a structured analysis."""
        
        return prompt
    
    @staticmethod
    def get_error_prediction_prompt(error_patterns: Dict, historical_data: Dict) -> str:
        """
        Generate a prompt for predicting future errors
        
        Args:
            error_patterns: Dictionary containing error pattern analysis
            historical_data: Dictionary containing historical error data
            
        Returns:
            Formatted prompt string for error prediction
        """
        prompt = f"""You are an expert data analyst specializing in predictive error analysis.

Based on the following historical error patterns and trends, provide predictions and recommendations:

Historical Error Patterns:
{error_patterns}

Historical Data Summary:
{historical_data}

Please provide:
1. Predicted error trends for the next period
2. High-risk error types to monitor
3. Recommended preventive measures
4. Early warning indicators to watch

Format your response as a structured prediction analysis."""
        
        return prompt
