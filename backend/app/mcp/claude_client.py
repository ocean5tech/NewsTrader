import asyncio
from typing import Dict, List, Any, Optional
from anthropic import AsyncAnthropic
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)


class ClaudeAnalyzer:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def analyze_news_impact(
        self,
        title: str,
        content: str,
        symbols: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze news article for trading impact using Claude
        """
        prompt = self._build_analysis_prompt(title, content, symbols)
        
        try:
            message = await self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse Claude's response
            response_text = message.content[0].text
            return self._parse_analysis_response(response_text)
            
        except Exception as e:
            logger.error(f"Claude analysis failed: {e}")
            return self._default_analysis()
    
    def _build_analysis_prompt(
        self,
        title: str,
        content: str,
        symbols: List[str]
    ) -> str:
        return f"""
Analyze this financial news article for trading impact. Provide a structured analysis in JSON format.

Article Title: {title}
Article Content: {content[:2000]}...

Trading Symbols to Consider: {', '.join(symbols)}

Please provide analysis in this exact JSON format:
{{
    "impact_score": <float 0-10>,
    "sentiment_score": <float -1 to 1>,
    "confidence_score": <float 0-1>,
    "affected_symbols": [
        {{
            "symbol": "<symbol>",
            "impact_direction": "<up/down/neutral>",
            "impact_magnitude": <float 0-1>,
            "reasoning": "<brief explanation>"
        }}
    ],
    "key_factors": ["<factor1>", "<factor2>"],
    "time_sensitivity": "<immediate/short_term/long_term>",
    "categories": ["<category1>", "<category2>"],
    "summary": "<2-3 sentence summary of impact>"
}}

Focus on:
1. Direct market impact potential (0-10 scale)
2. Sentiment (negative to positive)
3. Which specific symbols will be affected and how
4. Key driving factors
5. Time sensitivity of the impact
6. Your confidence in the analysis
"""
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's JSON response"""
        try:
            # Extract JSON from response if it's wrapped in text
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                logger.warning("No JSON found in Claude response")
                return self._default_analysis()
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            return self._default_analysis()
    
    def _default_analysis(self) -> Dict[str, Any]:
        """Default analysis when Claude fails"""
        return {
            "impact_score": 0.0,
            "sentiment_score": 0.0,
            "confidence_score": 0.0,
            "affected_symbols": [],
            "key_factors": [],
            "time_sensitivity": "unknown",
            "categories": [],
            "summary": "Analysis unavailable"
        }
    
    async def batch_analyze(
        self,
        articles: List[Dict[str, Any]],
        symbols: List[str]
    ) -> List[Dict[str, Any]]:
        """Analyze multiple articles in batch"""
        tasks = []
        for article in articles:
            task = self.analyze_news_impact(
                article['title'],
                article['content'],
                symbols
            )
            tasks.append(task)
        
        # Process in batches to avoid rate limits
        batch_size = 5
        results = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch analysis failed: {result}")
                    results.append(self._default_analysis())
                else:
                    results.append(result)
            
            # Rate limiting delay
            await asyncio.sleep(1)
        
        return results