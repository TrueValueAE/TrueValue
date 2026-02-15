"""
Observability & Analytics Module
================================
Structured logging, metrics tracking, and analytics for Dubai Estate AI.
Exports metrics in Prometheus format for Grafana dashboards.
"""

import os
import json
import logging
import time
import traceback
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict

# =====================================================
# MULTIPROCESS PROMETHEUS SETUP
# =====================================================
# IMPORTANT: Must set environment variable BEFORE importing prometheus_client

# Set up multiprocess directory for Prometheus metrics sharing
PROMETHEUS_MULTIPROC_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'prometheus_multiproc_dir'
)

# Create the directory if it doesn't exist
os.makedirs(PROMETHEUS_MULTIPROC_DIR, exist_ok=True)

# Set environment variable for prometheus_client (MUST be before import)
os.environ['PROMETHEUS_MULTIPROC_DIR'] = PROMETHEUS_MULTIPROC_DIR

# NOW import prometheus_client after environment is configured
from prometheus_client import Counter as PromCounter, Histogram, Gauge, generate_latest, REGISTRY, CollectorRegistry
from prometheus_client import multiprocess, values


def cleanup_prometheus_multiproc_dir():
    """
    Clean up the multiprocess metrics directory.
    Call this ONCE at application startup (before any metrics are recorded).
    """
    if os.path.exists(PROMETHEUS_MULTIPROC_DIR):
        for filename in os.listdir(PROMETHEUS_MULTIPROC_DIR):
            file_path = os.path.join(PROMETHEUS_MULTIPROC_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Warning: Could not delete {file_path}: {e}")


# =====================================================
# STRUCTURED JSON LOGGING
# =====================================================

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for easy parsing and analysis"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add custom fields from extra dict
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'query'):
            log_data['query'] = record.query
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        if hasattr(record, 'cost_usd'):
            log_data['cost_usd'] = record.cost_usd
        if hasattr(record, 'tools_used'):
            log_data['tools_used'] = record.tools_used
        if hasattr(record, 'error_type'):
            log_data['error_type'] = record.error_type
        if hasattr(record, 'error_message'):
            log_data['error_message'] = record.error_message
        if hasattr(record, 'stack_trace'):
            log_data['stack_trace'] = record.stack_trace
        if hasattr(record, 'input_tokens'):
            log_data['input_tokens'] = record.input_tokens
        if hasattr(record, 'output_tokens'):
            log_data['output_tokens'] = record.output_tokens
        if hasattr(record, 'model'):
            log_data['model'] = record.model
        if hasattr(record, 'success'):
            log_data['success'] = record.success

        # Add any other extra attributes
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'message', 'pathname', 'process', 'processName',
                          'relativeCreated', 'thread', 'threadName', 'exc_info',
                          'exc_text', 'stack_info'] and key not in log_data:
                try:
                    json.dumps(value)  # Test if serializable
                    log_data[key] = value
                except (TypeError, ValueError):
                    log_data[key] = str(value)

        return json.dumps(log_data)


# =====================================================
# METRICS TRACKING
# =====================================================

@dataclass
class QueryMetrics:
    """Metrics for a single query"""
    user_id: str
    query: str
    success: bool
    duration_ms: float
    cost_usd: float
    tools_used: List[str]
    error: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"


class MetricsTracker:
    """Track application metrics for monitoring and analytics"""

    def __init__(self):
        self.queries_total = 0
        self.queries_success = 0
        self.queries_failed = 0
        self.costs_total_usd = 0.0
        self.response_times: List[float] = []
        self.tool_usage: Dict[str, int] = defaultdict(int)
        self.errors_by_type: Dict[str, int] = defaultdict(int)
        self.queries_by_user: Dict[str, int] = defaultdict(int)
        self.cost_by_user: Dict[str, float] = defaultdict(float)
        self.recent_queries: List[QueryMetrics] = []
        self.max_recent = 100  # Keep last 100 queries in memory

    def record_query(
        self,
        user_id: str,
        query: str,
        success: bool,
        duration_ms: float,
        cost_usd: float,
        tools: List[str],
        error: Optional[str] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        model: str = ""
    ):
        """Record metrics for a query"""
        self.queries_total += 1

        if success:
            self.queries_success += 1
        else:
            self.queries_failed += 1
            if error:
                error_type = type(error).__name__ if isinstance(error, Exception) else "Unknown"
                self.errors_by_type[error_type] += 1

        self.costs_total_usd += cost_usd
        self.response_times.append(duration_ms)
        self.queries_by_user[user_id] += 1
        self.cost_by_user[user_id] += cost_usd

        for tool in tools:
            self.tool_usage[tool] += 1

        # Store recent query
        metrics = QueryMetrics(
            user_id=user_id,
            query=query[:100],  # Truncate for privacy
            success=success,
            duration_ms=duration_ms,
            cost_usd=cost_usd,
            tools_used=tools,
            error=str(error) if error else None,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model
        )

        self.recent_queries.append(metrics)
        if len(self.recent_queries) > self.max_recent:
            self.recent_queries.pop(0)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        avg_response_time = (
            sum(self.response_times) / len(self.response_times)
            if self.response_times else 0
        )

        # Calculate percentiles
        sorted_times = sorted(self.response_times) if self.response_times else []
        p50 = sorted_times[len(sorted_times) // 2] if sorted_times else 0
        p95 = sorted_times[int(len(sorted_times) * 0.95)] if sorted_times else 0
        p99 = sorted_times[int(len(sorted_times) * 0.99)] if sorted_times else 0

        success_rate = (
            self.queries_success / self.queries_total
            if self.queries_total > 0 else 0
        )

        error_rate = (
            self.queries_failed / self.queries_total
            if self.queries_total > 0 else 0
        )

        return {
            "total_queries": self.queries_total,
            "success_queries": self.queries_success,
            "failed_queries": self.queries_failed,
            "success_rate": f"{success_rate * 100:.1f}%",
            "error_rate": f"{error_rate * 100:.1f}%",
            "total_cost_usd": f"${self.costs_total_usd:.4f}",
            "avg_cost_per_query": f"${self.costs_total_usd / self.queries_total:.4f}" if self.queries_total > 0 else "$0.00",
            "response_times": {
                "avg_ms": f"{avg_response_time:.0f}",
                "p50_ms": f"{p50:.0f}",
                "p95_ms": f"{p95:.0f}",
                "p99_ms": f"{p99:.0f}",
            },
            "most_used_tools": dict(sorted(
                self.tool_usage.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]),
            "errors_by_type": dict(self.errors_by_type),
            "unique_users": len(self.queries_by_user),
            "top_users_by_queries": dict(sorted(
                self.queries_by_user.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]),
        }

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get stats for a specific user"""
        user_queries = [q for q in self.recent_queries if q.user_id == user_id]

        if not user_queries:
            return {"queries": 0, "cost_usd": 0, "avg_duration_ms": 0}

        total_duration = sum(q.duration_ms for q in user_queries)
        total_cost = sum(q.cost_usd for q in user_queries)
        successful = sum(1 for q in user_queries if q.success)

        return {
            "queries": len(user_queries),
            "success_rate": f"{successful / len(user_queries) * 100:.1f}%",
            "total_cost_usd": f"${total_cost:.4f}",
            "avg_cost_per_query": f"${total_cost / len(user_queries):.4f}",
            "avg_duration_ms": f"{total_duration / len(user_queries):.0f}",
        }


# =====================================================
# USER ANALYTICS
# =====================================================

class UserAnalytics:
    """Track user behavior for business intelligence"""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.max_events = 1000  # Keep last 1000 events in memory

    def track_event(
        self,
        user_id: str,
        event: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        """
        Track user events for analytics

        Events:
        - user_signup: New user registered
        - query_sent: User sent a query
        - subscription_upgrade: User upgraded tier
        - query_limit_hit: User hit daily limit
        - feature_used: User used a specific feature
        - error_occurred: User encountered an error
        """
        event_data = {
            'user_id': user_id,
            'event': event,
            'timestamp': datetime.utcnow().isoformat() + "Z",
            'properties': properties or {}
        }

        self.events.append(event_data)
        if len(self.events) > self.max_events:
            self.events.pop(0)

    def get_funnel(self) -> Dict[str, int]:
        """Get conversion funnel metrics"""
        signups = len([e for e in self.events if e['event'] == 'user_signup'])
        first_queries = len(set(
            e['user_id'] for e in self.events
            if e['event'] == 'query_sent'
        ))
        limit_hits = len(set(
            e['user_id'] for e in self.events
            if e['event'] == 'query_limit_hit'
        ))
        upgrades = len([e for e in self.events if e['event'] == 'subscription_upgrade'])

        return {
            "signups": signups,
            "users_with_queries": first_queries,
            "users_hit_limit": limit_hits,
            "upgrades": upgrades,
            "signup_to_query_rate": f"{first_queries / signups * 100:.1f}%" if signups > 0 else "0%",
            "limit_to_upgrade_rate": f"{upgrades / limit_hits * 100:.1f}%" if limit_hits > 0 else "0%",
        }


# =====================================================
# COST CALCULATOR
# =====================================================

class CostCalculator:
    """Calculate API costs based on token usage"""

    # Claude Sonnet 4 pricing (as of Feb 2025)
    PRICING = {
        "claude-sonnet-4-20250514": {
            "input": 3.00 / 1_000_000,   # $3 per million input tokens
            "output": 15.00 / 1_000_000,  # $15 per million output tokens
        },
        "claude-opus-4-6": {
            "input": 15.00 / 1_000_000,   # $15 per million input tokens
            "output": 75.00 / 1_000_000,  # $75 per million output tokens
        },
        "claude-haiku-4-5-20251001": {
            "input": 1.00 / 1_000_000,    # $1 per million input tokens
            "output": 5.00 / 1_000_000,   # $5 per million output tokens
        }
    }

    @classmethod
    def calculate_cost(
        cls,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost in USD for a Claude API call"""
        if model not in cls.PRICING:
            # Default to Sonnet 4 pricing if model unknown
            model = "claude-sonnet-4-20250514"

        pricing = cls.PRICING[model]
        cost = (input_tokens * pricing["input"]) + (output_tokens * pricing["output"])
        return cost


# =====================================================
# GLOBAL INSTANCES
# =====================================================

# Create global tracker instances
metrics_tracker = MetricsTracker()
user_analytics = UserAnalytics()


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def setup_json_logging(logger_name: str = "dubai_estate_ai") -> logging.Logger:
    """Set up JSON structured logging for a logger"""
    logger = logging.getLogger(logger_name)

    # Remove existing handlers
    logger.handlers.clear()

    # Add JSON handler for file output
    file_handler = logging.FileHandler("dubai_estate_ai.log")
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)

    # Add standard handler for console (easier to read during development)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    ))
    logger.addHandler(console_handler)

    logger.setLevel(logging.INFO)

    return logger


def log_user_error(
    logger: logging.Logger,
    user_id: str,
    error_message: str,
    exception: Exception,
    query: Optional[str] = None
):
    """Log an error that was sent to a user"""
    logger.error(
        "Error sent to user",
        extra={
            'user_id': user_id,
            'error_message': error_message[:200],
            'error_type': type(exception).__name__,
            'stack_trace': traceback.format_exc(),
            'query': query[:100] if query else None,
        }
    )

    # Track in analytics
    user_analytics.track_event(
        user_id=user_id,
        event='error_occurred',
        properties={
            'error_type': type(exception).__name__,
            'error_message': error_message[:200],
        }
    )


def log_query_start(
    logger: logging.Logger,
    user_id: str,
    query: str
) -> float:
    """Log query start and return start time"""
    start_time = time.time()

    logger.info(
        "Query started",
        extra={
            'user_id': user_id,
            'query': query[:100],
        }
    )

    return start_time


def log_query_complete(
    logger: logging.Logger,
    user_id: str,
    query: str,
    start_time: float,
    tools_used: List[str],
    input_tokens: int = 0,
    output_tokens: int = 0,
    model: str = "claude-sonnet-4-20250514",
    success: bool = True,
    error: Optional[Exception] = None
):
    """Log query completion with full metrics"""
    duration_ms = (time.time() - start_time) * 1000
    duration_seconds = duration_ms / 1000.0
    cost_usd = CostCalculator.calculate_cost(model, input_tokens, output_tokens)

    if success:
        logger.info(
            "Query completed successfully",
            extra={
                'user_id': user_id,
                'query': query[:100],
                'duration_ms': duration_ms,
                'cost_usd': cost_usd,
                'tools_used': tools_used,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'model': model,
                'success': True,
            }
        )
    else:
        logger.error(
            "Query failed",
            extra={
                'user_id': user_id,
                'query': query[:100],
                'duration_ms': duration_ms,
                'cost_usd': cost_usd,
                'tools_used': tools_used,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'model': model,
                'success': False,
                'error_type': type(error).__name__ if error else "Unknown",
                'error_message': str(error) if error else "Unknown error",
            }
        )

    # Record in metrics tracker
    metrics_tracker.record_query(
        user_id=user_id,
        query=query,
        success=success,
        duration_ms=duration_ms,
        cost_usd=cost_usd,
        tools=tools_used,
        error=error,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        model=model
    )

    # Track in analytics
    user_analytics.track_event(
        user_id=user_id,
        event='query_sent',
        properties={
            'duration_ms': duration_ms,
            'cost_usd': cost_usd,
            'tools_used': tools_used,
            'success': success,
        }
    )

    # Record Prometheus metrics
    record_query_metrics(
        user_id=user_id,
        success=success,
        duration_seconds=duration_seconds,
        cost_usd=cost_usd,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        tools=tools_used
    )


# =====================================================
# PROMETHEUS METRICS
# =====================================================

# Query metrics
query_total = PromCounter(
    'dubai_estate_queries_total',
    'Total number of queries processed',
    ['status', 'user_id', 'model']
)

query_duration = Histogram(
    'dubai_estate_query_duration_seconds',
    'Query processing duration in seconds',
    ['status', 'model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0]
)

query_cost = Histogram(
    'dubai_estate_query_cost_usd',
    'Query cost in USD',
    ['model'],
    buckets=[0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
)

# Token metrics
tokens_used = PromCounter(
    'dubai_estate_tokens_total',
    'Total tokens used',
    ['type', 'model']  # type: input/output
)

# Tool metrics
tool_usage = PromCounter(
    'dubai_estate_tool_usage_total',
    'Tool usage count',
    ['tool_name', 'status']
)

# User metrics
active_users = Gauge(
    'dubai_estate_active_users',
    'Number of active users',
    ['tier']
)

user_signups = PromCounter(
    'dubai_estate_user_signups_total',
    'Total user signups',
    ['tier']
)

subscription_upgrades = PromCounter(
    'dubai_estate_subscription_upgrades_total',
    'Subscription upgrades',
    ['from_tier', 'to_tier']
)

query_limit_hits = PromCounter(
    'dubai_estate_query_limit_hits_total',
    'Query limit hits by tier',
    ['tier']
)

# Command metrics
command_usage = PromCounter(
    'dubai_estate_command_usage_total',
    'Telegram command usage',
    ['command', 'user_id']
)

# Error metrics
errors_total = PromCounter(
    'dubai_estate_errors_total',
    'Total errors',
    ['error_type', 'user_id']
)

# Business metrics
revenue_total = Gauge(
    'dubai_estate_revenue_total_aed',
    'Total revenue in AED',
    []
)

mrr = Gauge(
    'dubai_estate_mrr_aed',
    'Monthly Recurring Revenue in AED',
    []
)

# Conversation metrics
followup_detected_total = PromCounter(
    'dubai_estate_followup_detected_total',
    'Follow-up vs fresh query classification',
    ['type']  # type: followup / fresh
)

active_conversations = Gauge(
    'dubai_estate_active_conversations',
    'Number of active conversation sessions',
    []
)

conversation_resets_total = PromCounter(
    'dubai_estate_conversation_resets_total',
    'Conversation reset events',
    ['reason']  # reason: command / timeout
)

# Web search metrics
web_search_total = PromCounter(
    'dubai_estate_web_search_total',
    'Web search queries',
    ['status']  # success / failure / unavailable
)

# Database metrics
db_queries_total = PromCounter(
    'dubai_estate_db_queries_total',
    'Database query count',
    ['operation']  # get_user / create_user / log_conversation / etc.
)

db_query_duration = Histogram(
    'dubai_estate_db_query_duration_seconds',
    'Database query duration',
    ['operation'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

# Cache metrics
cache_hits_total = PromCounter(
    'dubai_estate_cache_hits_total',
    'Cache hit count',
    ['tool_name']
)

cache_misses_total = PromCounter(
    'dubai_estate_cache_misses_total',
    'Cache miss count',
    ['tool_name']
)

# PDF generation metrics
pdf_generations_total = PromCounter(
    'dubai_estate_pdf_generations_total',
    'PDF report generations',
    ['status']  # success / failure
)

# Voice transcription metrics
voice_transcriptions_total = PromCounter(
    'dubai_estate_voice_transcriptions_total',
    'Voice message transcriptions',
    ['status']  # success / failure
)

# Payment metrics
payment_events_total = PromCounter(
    'dubai_estate_payment_events_total',
    'Payment lifecycle events',
    ['event_type']  # checkout_completed / subscription_updated / subscription_cancelled / payment_failed
)


# =====================================================
# PROMETHEUS EXPORTER FUNCTIONS
# =====================================================

def record_query_metrics(
    user_id: str,
    success: bool,
    duration_seconds: float,
    cost_usd: float,
    model: str,
    input_tokens: int,
    output_tokens: int,
    tools: List[str]
):
    """Record query metrics for Prometheus"""
    status = 'success' if success else 'failure'
    
    # Query metrics
    query_total.labels(status=status, user_id=user_id, model=model).inc()
    query_duration.labels(status=status, model=model).observe(duration_seconds)
    query_cost.labels(model=model).observe(cost_usd)
    
    # Token metrics
    tokens_used.labels(type='input', model=model).inc(input_tokens)
    tokens_used.labels(type='output', model=model).inc(output_tokens)
    
    # Tool metrics
    for tool in tools:
        tool_usage.labels(tool_name=tool, status=status).inc()


def record_command_metrics(command: str, user_id: str):
    """Record command usage"""
    command_usage.labels(command=command, user_id=user_id).inc()


def record_error_metrics(error_type: str, user_id: str):
    """Record error occurrence"""
    errors_total.labels(error_type=error_type, user_id=user_id).inc()


def record_user_signup(tier: str = 'free'):
    """Record user signup"""
    user_signups.labels(tier=tier).inc()


def record_subscription_upgrade(from_tier: str, to_tier: str):
    """Record subscription upgrade"""
    subscription_upgrades.labels(from_tier=from_tier, to_tier=to_tier).inc()


def record_query_limit_hit(tier: str):
    """Record query limit hit"""
    query_limit_hits.labels(tier=tier).inc()


def update_active_users(tier_counts: Dict[str, int]):
    """Update active users gauge by tier"""
    for tier, count in tier_counts.items():
        active_users.labels(tier=tier).set(count)


def update_revenue_metrics(total_revenue: float, monthly_revenue: float):
    """Update revenue metrics"""
    revenue_total.set(total_revenue)
    mrr.set(monthly_revenue)


def record_followup_detected(is_followup: bool):
    """Record whether a query was classified as follow-up or fresh."""
    followup_detected_total.labels(type='followup' if is_followup else 'fresh').inc()


def record_conversation_reset(reason: str = 'command'):
    """Record a conversation reset event."""
    conversation_resets_total.labels(reason=reason).inc()


def update_active_conversations(count: int):
    """Update the active conversations gauge."""
    active_conversations.set(count)


def record_web_search(status: str):
    """Record a web search event. Status: success / failure / unavailable"""
    web_search_total.labels(status=status).inc()


def record_db_query(operation: str, duration_seconds: float = 0):
    """Record a database query."""
    db_queries_total.labels(operation=operation).inc()
    if duration_seconds > 0:
        db_query_duration.labels(operation=operation).observe(duration_seconds)


def record_cache_hit(tool_name: str):
    """Record a cache hit."""
    cache_hits_total.labels(tool_name=tool_name).inc()


def record_cache_miss(tool_name: str):
    """Record a cache miss."""
    cache_misses_total.labels(tool_name=tool_name).inc()


def record_pdf_generation(status: str):
    """Record a PDF generation event."""
    pdf_generations_total.labels(status=status).inc()


def record_voice_transcription(status: str):
    """Record a voice transcription event."""
    voice_transcriptions_total.labels(status=status).inc()


def record_payment_event(event_type: str):
    """Record a payment lifecycle event."""
    payment_events_total.labels(event_type=event_type).inc()


def get_prometheus_metrics() -> str:
    """Generate Prometheus metrics in text format (multiprocess-aware)"""
    # Create a new registry and collect metrics from all processes
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return generate_latest(registry).decode('utf-8')
