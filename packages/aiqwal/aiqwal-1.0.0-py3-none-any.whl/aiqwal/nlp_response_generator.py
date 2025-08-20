# aiqwal/nlp_response_generator.py
"""
Natural Language Response Generator
Takes SQL results and generates human-friendly explanations using AI
"""

from pathlib import Path
from llama_cpp import Llama
from aiqwal.config import AI_MODEL_PATH
import json
from typing import Dict, List, Any

class NLPResponseGenerator:
    """
    Generates natural language responses from SQL query results
    Completes the full cycle: NL Question → SQL → Results → NL Answer
    """
    
    def __init__(self, model_path: str = AI_MODEL_PATH):
        # Use the same model for consistency (could be a different smaller model for responses)
        model_file = Path(model_path)
        if not model_file.exists():
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        self.model = Llama(
            model_path=str(model_file), 
            n_ctx=2048,  # Smaller context for response generation
            n_threads=4,  # Fewer threads for faster response
            verbose=False,
            temperature=0.3  # Slightly more creative for natural responses
        )

    def generate_natural_response(self, 
                                original_question: str, 
                                sql_query: str, 
                                results: List[Dict], 
                                execution_time: float = None) -> str:
        """
        Generate a natural language response explaining the query results
        
        Args:
            original_question: User's original natural language question
            sql_query: The SQL query that was executed
            results: Query results (list of dictionaries)
            execution_time: How long the query took to execute
            
        Returns:
            Natural language explanation of the results
        """
        
        # Prepare data summary
        result_summary = self._summarize_results(results)
        
        # Create context-aware prompt
        prompt = self._create_response_prompt(
            original_question, 
            sql_query, 
            result_summary, 
            execution_time
        )
        
        try:
            response = self.model(
                prompt,
                max_tokens=200,
                temperature=0.3,
                stop=["Question:", "SQL:", "Results:", "\n\n"],
                repeat_penalty=1.1
            )
            
            generated_response = response['choices'][0]['text'].strip()
            
            # Clean and enhance the response
            final_response = self._polish_response(generated_response, result_summary)
            
            return final_response
            
        except Exception as e:
            # Fallback to template-based response if AI fails
            return self._fallback_response(original_question, result_summary)

    def _summarize_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Create a structured summary of the query results"""
        if not results:
            return {
                'count': 0,
                'message': 'No results found',
                'data_type': 'empty'
            }
        
        result_count = len(results)
        first_result = results[0]
        columns = list(first_result.keys()) if first_result else []
        
        summary = {
            'count': result_count,
            'columns': columns,
            'sample_data': results[:3] if result_count <= 3 else results[:2],
            'data_type': self._determine_data_type(results),
            'key_insights': self._extract_key_insights(results)
        }
        
        return summary

    def _determine_data_type(self, results: List[Dict]) -> str:
        """Determine what type of data this is"""
        if not results:
            return 'empty'
        
        first_result = results[0]
        columns = list(first_result.keys())
        
        # Single number result (COUNT, AVG, etc.)
        if len(results) == 1 and len(columns) == 1:
            col_name = columns[0].lower()
            if any(word in col_name for word in ['count', 'total', 'sum', 'avg', 'average', 'max', 'min']):
                return 'aggregation'
        
        # Multiple rows of data
        if len(results) > 1:
            return 'dataset'
        
        # Single row with multiple columns
        if len(results) == 1 and len(columns) > 1:
            return 'single_record'
        
        return 'general'

    def _extract_key_insights(self, results: List[Dict]) -> Dict[str, Any]:
        """Extract key insights from the data"""
        if not results:
            return {}
        
        insights = {}
        
        # For aggregation results
        if len(results) == 1:
            result = results[0]
            for key, value in result.items():
                if isinstance(value, (int, float)):
                    insights['primary_value'] = {
                        'metric': key,
                        'value': value,
                        'formatted': self._format_number(value)
                    }
        
        # For dataset results
        elif len(results) > 1:
            insights['record_count'] = len(results)
            
            # Find numeric columns for insights
            numeric_columns = []
            first_result = results[0]
            for key, value in first_result.items():
                if isinstance(value, (int, float)):
                    numeric_columns.append(key)
            
            # Get ranges for numeric data
            if numeric_columns:
                insights['numeric_insights'] = {}
                for col in numeric_columns[:2]:  # Limit to first 2 numeric columns
                    values = [float(row[col]) for row in results if row[col] is not None]
                    if values:
                        insights['numeric_insights'][col] = {
                            'min': min(values),
                            'max': max(values),
                            'range': f"{self._format_number(min(values))} to {self._format_number(max(values))}"
                        }
        
        return insights

    def _create_response_prompt(self, question: str, sql: str, summary: Dict, execution_time: float) -> str:
        """Create an AI prompt for generating natural language response"""
        
        prompt = f"""You are a helpful data analyst. Explain query results in natural language.

User asked: "{question}"

Query executed: {sql}

Results summary:
- Found {summary['count']} result(s)
- Data type: {summary['data_type']}

"""
        
        # Add specific data insights
        if summary['data_type'] == 'aggregation' and 'key_insights' in summary and 'primary_value' in summary['key_insights']:
            insight = summary['key_insights']['primary_value']
            prompt += f"- {insight['metric']}: {insight['formatted']}\n"
        
        elif summary['count'] > 0:
            prompt += f"- Columns: {', '.join(summary['columns'])}\n"
            if 'key_insights' in summary and 'numeric_insights' in summary['key_insights']:
                for col, stats in summary['key_insights']['numeric_insights'].items():
                    prompt += f"- {col} range: {stats['range']}\n"
        
        if execution_time:
            prompt += f"- Execution time: {execution_time:.3f}s\n"
        
        prompt += f"""
Respond naturally as if explaining to a business user. Be concise and helpful.

Natural response:"""
        
        return prompt

    def _polish_response(self, generated_response: str, summary: Dict) -> str:
        """Polish and enhance the AI-generated response"""
        if not generated_response or len(generated_response.strip()) < 10:
            return self._fallback_response("your question", summary)
        
        # Clean up common AI response issues
        response = generated_response.strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            "Based on the query results,",
            "According to the data,", 
            "The results show that",
            "Looking at the results,",
            "Response:"
        ]
        
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        
        # Ensure response starts with capital letter
        if response and not response[0].isupper():
            response = response[0].upper() + response[1:]
        
        # Add helpful context if missing
        if summary['count'] == 0 and "no" not in response.lower():
            response = f"No results found. {response}"
        
        return response

    def _fallback_response(self, question: str, summary: Dict) -> str:
        """Generate a fallback response if AI generation fails"""
        count = summary['count']
        
        if count == 0:
            return "I didn't find any results for your query."
        
        elif summary['data_type'] == 'aggregation' and 'key_insights' in summary:
            if 'primary_value' in summary['key_insights']:
                insight = summary['key_insights']['primary_value']
                return f"The {insight['metric']} is {insight['formatted']}."
        
        elif count == 1:
            return f"I found 1 record matching your query."
        
        else:
            return f"I found {count} records matching your query."

    def _format_number(self, value: float) -> str:
        """Format numbers for natural language"""
        if value == int(value):
            return f"{int(value):,}"
        else:
            return f"{value:,.2f}"

    def generate_contextual_followup_suggestions(self, 
                                               original_question: str, 
                                               results: List[Dict]) -> List[str]:
        """Generate suggested follow-up questions based on the results"""
        if not results:
            return [
                "Try asking about a different table or time period",
                "Check what tables are available with 'schema'",
                "Ask for help with 'help'"
            ]
        
        suggestions = []
        columns = list(results[0].keys()) if results else []
        
        # Suggest drill-downs based on columns
        for col in columns:
            col_lower = col.lower()
            if 'date' in col_lower or 'time' in col_lower:
                suggestions.append(f"Show trends by {col}")
            elif 'id' in col_lower and col_lower != 'id':
                suggestions.append(f"Group by {col}")
            elif col_lower in ['department', 'category', 'type', 'status']:
                suggestions.append(f"Break down by {col}")
        
        # Add general suggestions
        if len(results) > 1:
            suggestions.append("Show me the top 10 results")
            suggestions.append("Calculate the average")
        
        # Limit to 3 most relevant suggestions
        return suggestions[:3]