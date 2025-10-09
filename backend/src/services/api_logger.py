"""
API Logger Service
Centralized logging for all external API calls
"""
import json
import time
from datetime import datetime
from typing import Dict, Optional, Any
from backend.src.storage.database import get_session
from backend.src.models.api_log import APILog


class APILogger:
    """Logs all API interactions for observability"""
    
    # Cost per 1M tokens (update these as needed)
    COST_PER_1M_TOKENS = {
        'meta-llama/llama-3.1-8b-instruct': 0.06,  # $0.06 per 1M tokens
        'gpt-4': 30.0,
        'gpt-3.5-turbo': 0.50,
    }
    
    @staticmethod
    def log_api_call(
        service: str,
        endpoint: str,
        request_data: Dict[str, Any],
        response_data: Optional[Dict[str, Any]] = None,
        response_time_ms: Optional[int] = None,
        status: str = 'success',
        error_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> APILog:
        """
        Log an API call to the database
        
        Args:
            service: Service name ('openrouter', 'x_api', etc.)
            endpoint: Full API endpoint URL
            request_data: Request parameters
            response_data: Response data (if successful)
            response_time_ms: Response time in milliseconds
            status: 'success', 'error', or 'timeout'
            error_message: Error details if failed
            context: Additional context (post_id, algorithm_id, etc.)
        
        Returns:
            APILog object
        """
        session = get_session()
        
        try:
            # Extract common fields
            model = request_data.get('model')
            system_prompt = None
            user_message = None
            
            # Extract LLM-specific fields
            if 'messages' in request_data:
                messages = request_data['messages']
                for msg in messages:
                    if msg.get('role') == 'system':
                        system_prompt = msg.get('content')
                    elif msg.get('role') == 'user':
                        user_message = msg.get('content')
            
            # Calculate tokens and cost (for LLM calls)
            tokens_used = None
            cost_usd = None
            
            if response_data and 'usage' in response_data:
                tokens_used = response_data['usage'].get('total_tokens')
                if tokens_used and model:
                    cost_per_token = APILogger.COST_PER_1M_TOKENS.get(model, 0) / 1_000_000
                    cost_usd = tokens_used * cost_per_token
            
            # Create log entry
            log_entry = APILog(
                timestamp=datetime.utcnow(),
                service=service,
                endpoint=endpoint,
                model=model,
                system_prompt=system_prompt,
                user_message=user_message,
                request_params=json.dumps(request_data),
                response_raw=json.dumps(response_data) if response_data else None,
                response_parsed=response_data,
                response_time_ms=response_time_ms,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                post_id=context.get('post_id') if context else None,
                algorithm_id=context.get('algorithm_id') if context else None,
                status=status,
                error_message=error_message
            )
            
            session.add(log_entry)
            session.commit()
            session.refresh(log_entry)
            
            return log_entry
            
        finally:
            session.close()
    
    @staticmethod
    def get_recent_logs(limit: int = 10, service: Optional[str] = None):
        """Get recent API logs"""
        session = get_session()
        
        try:
            query = session.query(APILog).order_by(APILog.timestamp.desc())
            
            if service:
                query = query.filter(APILog.service == service)
            
            return query.limit(limit).all()
            
        finally:
            session.close()
    
    @staticmethod
    def get_stats(hours: int = 24):
        """Get API usage statistics for the last N hours"""
        from datetime import timedelta
        
        session = get_session()
        
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            logs = session.query(APILog).filter(
                APILog.timestamp >= cutoff
            ).all()
            
            total_calls = len(logs)
            successful = sum(1 for log in logs if log.status == 'success')
            failed = sum(1 for log in logs if log.status == 'error')
            total_cost = sum(log.cost_usd for log in logs if log.cost_usd)
            avg_latency = sum(log.response_time_ms for log in logs if log.response_time_ms) / total_calls if total_calls > 0 else 0
            
            return {
                'total_calls': total_calls,
                'successful': successful,
                'failed': failed,
                'success_rate': (successful / total_calls * 100) if total_calls > 0 else 0,
                'total_cost_usd': total_cost,
                'avg_latency_ms': avg_latency
            }
            
        finally:
            session.close()


class APICallTimer:
    """Context manager to time API calls"""
    
    def __init__(self):
        self.start_time = None
        self.elapsed_ms = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_ms = int((time.time() - self.start_time) * 1000)
