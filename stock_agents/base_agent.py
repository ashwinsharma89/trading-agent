"""
Base Agent Class for Multi-Agent Architecture
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents
    """
    
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight
        self.execution_time = 0
        self.last_error = None
        
    @abstractmethod
    def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method - must be implemented by each agent
        
        Args:
            state: Shared state containing ticker, market data, etc.
            
        Returns:
            Dict with signal, strength, confidence, reasoning
        """
        pass
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute analysis with error handling and timing
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"🤖 {self.name} starting analysis...")
            result = self.analyze(state)
            
            # Add metadata
            result['agent'] = self.name
            result['execution_time'] = (datetime.now() - start_time).total_seconds()
            result['timestamp'] = datetime.now().isoformat()
            result['success'] = True
            
            self.execution_time = result['execution_time']
            logger.info(f"✅ {self.name} completed in {result['execution_time']:.2f}s")
            
            return result
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"❌ {self.name} failed: {e}")
            
            return {
                'agent': self.name,
                'success': False,
                'error': str(e),
                'signal': 'HOLD',
                'strength': 0,
                'confidence': 0,
                'reasoning': [f"Agent failed: {str(e)}"]
            }
    
    def validate_state(self, state: Dict[str, Any], required_keys: List[str]) -> bool:
        """
        Validate that state contains required keys
        """
        missing = [key for key in required_keys if key not in state]
        if missing:
            raise ValueError(f"{self.name} missing required state keys: {missing}")
        return True
