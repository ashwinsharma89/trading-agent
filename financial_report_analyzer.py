"""
Financial Report Analyzer
Extracts detailed metrics from annual reports, quarterly filings
"""

import os
import PyPDF2
import requests
from typing import Dict, Any, List
import json
import re


class FinancialReportAnalyzer:
    """
    Analyze financial reports (PDFs) for detailed metrics
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.cache_dir = 'data/financial_reports'
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def fetch_report(self, ticker: str, report_type: str = 'annual') -> str:
        """
        Fetch financial report PDF
        Sources: NSE, BSE, company website
        """
        cache_file = f"{self.cache_dir}/{ticker}_{report_type}.pdf"
        
        if os.path.exists(cache_file):
            return cache_file
        
        # Try to download from sources
        # 1. NSE website
        # 2. BSE website  
        # 3. Company IR page
        
        pdf_url = self._find_report_url(ticker, report_type)
        
        if pdf_url:
            response = requests.get(pdf_url)
            with open(cache_file, 'wb') as f:
                f.write(response.content)
            return cache_file
        
        return None
    
    def _find_report_url(self, ticker: str, report_type: str) -> str:
        """
        Find URL for financial report
        """
        # Placeholder - implement actual URL finding
        # This would search NSE/BSE/company websites
        return None
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF report
        """
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            print(f"PDF extraction failed: {e}")
            return ""
    
    def analyze_report(self, ticker: str) -> Dict[str, Any]:
        """
        Analyze financial report and extract detailed metrics
        """
        # Fetch report
        pdf_path = self.fetch_report(ticker)
        
        if not pdf_path:
            return {
                'available': False,
                'metrics': {}
            }
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            return {
                'available': False,
                'metrics': {}
            }
        
        # Extract metrics
        metrics = self._extract_metrics(text, ticker)
        
        # AI-powered analysis
        insights = self._ai_analysis(text, ticker)
        
        return {
            'available': True,
            'metrics': metrics,
            'insights': insights,
            'quality_score': self._calculate_quality_score(metrics)
        }
    
    def _extract_metrics(self, text: str, ticker: str) -> Dict[str, Any]:
        """
        Extract financial metrics from report text
        """
        metrics = {}
        
        # Revenue patterns
        revenue_pattern = r'revenue.*?(\d+\.?\d*)\s*(crore|million|billion)'
        matches = re.findall(revenue_pattern, text.lower())
        if matches:
            metrics['revenue'] = self._parse_number(matches[0])
        
        # Profit patterns
        profit_pattern = r'net profit.*?(\d+\.?\d*)\s*(crore|million|billion)'
        matches = re.findall(profit_pattern, text.lower())
        if matches:
            metrics['net_profit'] = self._parse_number(matches[0])
        
        # Debt patterns
        debt_pattern = r'total debt.*?(\d+\.?\d*)\s*(crore|million|billion)'
        matches = re.findall(debt_pattern, text.lower())
        if matches:
            metrics['total_debt'] = self._parse_number(matches[0])
        
        # Cash patterns
        cash_pattern = r'cash.*?(\d+\.?\d*)\s*(crore|million|billion)'
        matches = re.findall(cash_pattern, text.lower())
        if matches:
            metrics['cash'] = self._parse_number(matches[0])
        
        # Extract more metrics...
        # - Operating cash flow
        # - Capital expenditure
        # - Working capital
        # - Inventory turnover
        # - Receivables days
        # - Payables days
        
        return metrics
    
    def _parse_number(self, match: tuple) -> float:
        """
        Parse number with unit (crore, million, billion)
        """
        number = float(match[0])
        unit = match[1].lower()
        
        if unit == 'crore':
            return number * 10_000_000
        elif unit == 'million':
            return number * 1_000_000
        elif unit == 'billion':
            return number * 1_000_000_000
        
        return number
    
    def _ai_analysis(self, text: str, ticker: str) -> Dict[str, Any]:
        """
        Use AI to extract insights from report
        """
        try:
            import openai
            
            # Truncate text to fit in context
            text_sample = text[:5000]
            
            prompt = f"""
            Analyze this financial report for {ticker}.
            
            Extract:
            1. Key financial highlights
            2. Management discussion insights
            3. Risk factors mentioned
            4. Growth initiatives
            5. Competitive advantages
            6. Red flags or concerns
            7. Overall financial health (0-100 score)
            
            Report excerpt:
            {text_sample}
            
            Return as JSON.
            """
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial analyst expert at analyzing annual reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"AI analysis failed: {e}")
            return {
                'highlights': [],
                'insights': [],
                'risks': [],
                'growth_initiatives': [],
                'competitive_advantages': [],
                'concerns': [],
                'health_score': 50
            }
    
    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> int:
        """
        Calculate quality score based on extracted metrics
        """
        score = 50  # Base score
        
        # Revenue growth
        if 'revenue' in metrics and 'revenue_growth' in metrics:
            if metrics['revenue_growth'] > 20:
                score += 15
            elif metrics['revenue_growth'] > 10:
                score += 10
        
        # Profitability
        if 'net_profit' in metrics and 'revenue' in metrics:
            margin = (metrics['net_profit'] / metrics['revenue']) * 100
            if margin > 15:
                score += 15
            elif margin > 10:
                score += 10
        
        # Debt levels
        if 'total_debt' in metrics and 'revenue' in metrics:
            debt_ratio = metrics['total_debt'] / metrics['revenue']
            if debt_ratio < 0.5:
                score += 10
            elif debt_ratio > 2:
                score -= 10
        
        # Cash position
        if 'cash' in metrics and 'total_debt' in metrics:
            if metrics['cash'] > metrics['total_debt']:
                score += 10
        
        return max(0, min(100, score))
    
    def compare_with_previous(self, ticker: str, current_metrics: Dict,
                             previous_metrics: Dict) -> Dict[str, Any]:
        """
        Compare current report with previous period
        """
        comparison = {}
        
        for key in current_metrics:
            if key in previous_metrics:
                current = current_metrics[key]
                previous = previous_metrics[key]
                
                if isinstance(current, (int, float)) and isinstance(previous, (int, float)):
                    change = ((current - previous) / previous) * 100
                    comparison[f"{key}_change"] = change
        
        return comparison


if __name__ == "__main__":
    # Test
    analyzer = FinancialReportAnalyzer()
    
    ticker = "KPIGREEN"
    analysis = analyzer.analyze_report(ticker)
    
    if analysis['available']:
        print(f"Quality Score: {analysis['quality_score']}")
        print(f"Metrics: {analysis['metrics']}")
        print(f"Insights: {analysis['insights']}")
    else:
        print("No report available")
