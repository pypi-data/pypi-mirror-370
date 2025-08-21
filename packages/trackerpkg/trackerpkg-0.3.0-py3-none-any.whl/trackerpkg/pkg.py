import json
import os
import time
import functools
import aiohttp
import psutil
import threading
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from confluent_kafka import Producer
import inspect
from urllib.parse import urlparse
import requests
import http.client
import urllib.request
from collections import Counter

EXCLUDED_DOMAINS = {"api.openai.com"}

def get_api_config():
    """Get FastAPI configuration from environment variables."""
    load_dotenv()
    
    try:
        return {
            'base_url': os.environ.get('DYNAMETER_API_BASE_URL', 'http://34.12.91.235:8000'),
            # 'api_key': os.environ.get('DYNAMETER_API_KEY', ''),  # Optional API key for authentication
            'timeout': int(os.environ.get('DYNAMETER_API_TIMEOUT', '30'))
        }
    except Exception as e:
        raise ValueError(f"Error getting API configuration: {e}")

def read_kafka_config():
    """Read Kafka configuration from client.properties file."""
    config = {}
    with open("testing-for-kafka/client.properties") as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                config[parameter] = value.strip()
    return config

def get_kafka_producer():
    """Get Kafka producer instance."""
    cfg = read_kafka_config()
    return Producer(cfg)

def send_to_api(endpoint: str, data: Dict[str, Any], timeout: int = 30) -> bool:
    """
    Send data to FastAPI endpoint.
    
    Args:
        endpoint: API endpoint (relative to base URL)
        data: Data to send
        timeout: Request timeout
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        config = get_api_config()
        url = f"{config['base_url']}{endpoint}"
        
        headers = {'Content-Type': 'application/json'}
        # if config['api_key']:
        #     headers['Authorization'] = f"Bearer {config['api_key']}"
        
        response = requests.post(
            url, 
            json=data, 
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending data to API endpoint {endpoint}: {e}")
        return False

def compute_dynabits(
    input_tokens: int,
    output_tokens: int,
    cpu_seconds: float,
    gb_seconds: float,
    cpu_utilization: float,   # fraction (0–1)
    total_ram_used: float,    # GB
    total_ram_free: float     # GB
) -> float:
    """
    Compute dynabits based on dummy weights.
    """
    # Base cost
    base = (
        0.00008 * input_tokens
        + 0.00012 * output_tokens
        + 0.03 * cpu_seconds
        + 0.002 * gb_seconds
    )
    # CPU utilization penalty (inefficiency if < 50%)
    penalty = 0.02 * cpu_seconds * max(0, 0.5 - cpu_utilization)
    # RAM pressure fraction
    total_ram = total_ram_used + total_ram_free
    ru = total_ram_used / total_ram if total_ram > 0 else 0.0
    # Congestion multiplier (surcharge if > 80% RAM used)
    multiplier = 1 + 0.5 * max(0, ru - 0.8)
    # Dynabits total
    dynabits = multiplier * base + penalty
    # Safeguards
    dynabits = max(dynabits, 0.5)  # minimum charge
    penalty_cap = 0.2 * base
    if penalty > penalty_cap:
        dynabits = multiplier * base + penalty_cap
    dynabits = round(dynabits, 2)
    return dynabits

def openai_token_usage(response):
    """
    Unified extractor for OpenAI responses
    """
    model = None
    prompt = None
    completion = None
    total = None

    if hasattr(response, "model") and hasattr(response, "usage"):
        model = getattr(response, "model", None)
        usage = getattr(response, "usage", None)
        if usage:
            prompt = getattr(usage, "prompt_tokens", None) or getattr(usage, "input_tokens", None)
            completion = getattr(usage, "completion_tokens", None) or getattr(usage, "output_tokens", None)
            total = getattr(usage, "total_tokens", None)
        return {"model": model, "prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": total}

    if isinstance(response, dict):
        model = response.get("model")
        usage = response.get("usage", {}) or {}
        prompt = usage.get("prompt_tokens") or usage.get("input_tokens")
        completion = usage.get("completion_tokens") or usage.get("output_tokens")
        total = usage.get("total_tokens")
        return {"model": model, "prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": total}

    raise ValueError("Unsupported response object: model or usage not found")

class DynabitsCalculator:
    """Helper class to calculate weighted dynabits with normalization."""
    
    # Normalization ranges - adjust based on your actual usage patterns
    MAX_INPUT_TOKENS = 8000
    MAX_OUTPUT_TOKENS = 2000
    MAX_CPU_SECONDS = 300      # 5 minutes
    MAX_GB_SECONDS = 600       # 10GB for 1 minute or 1GB for 10 minutes
    MAX_API_CALLS = 50
    MAX_TOTAL_DURATION = 30    # 30 seconds
    OPTIMAL_CPU_UTIL = 0.7     # Target 70% utilization
    PRESSURE_THRESHOLD = 0.8   # Start penalizing at 80% RAM usage
    
    # Equal weights for all components (sum = 1.0)
    DEFAULT_WEIGHTS = {
        'tokens': 0.20,        # 20% each component
        'cpu': 0.20,
        'memory': 0.20,
        'api_calls': 0.20,
        'efficiency': 0.20
    }
    
    BASE_DYNABITS_RATE = 1.0   # Base rate multiplier
    
    @classmethod
    def normalize_tokens(cls, input_tokens: int, output_tokens: int) -> float:
        """Normalize token usage to 0-1 scale."""
        input_score = min(input_tokens / cls.MAX_INPUT_TOKENS, 1.0)
        output_score = min(output_tokens / cls.MAX_OUTPUT_TOKENS, 1.0)
        
        # Weight output 1.5x higher (generation more expensive than input)
        return (input_score + 1.5 * output_score) / 2.5
    
    @classmethod
    def normalize_cpu(cls, cpu_seconds: float, cpu_utilization: float) -> float:
        """Normalize CPU usage considering both time and efficiency."""
        time_score = min(cpu_seconds / cls.MAX_CPU_SECONDS, 1.0)
        efficiency_score = min(cpu_utilization / cls.OPTIMAL_CPU_UTIL, 1.0)
        
        # Combine time and efficiency
        return time_score * (1.0 + efficiency_score) / 2.0
    
    @classmethod
    def normalize_memory(cls, gb_seconds: float, ram_pressure_ratio: float) -> float:
        """Normalize memory usage considering both consumption and pressure."""
        consumption_score = min(gb_seconds / cls.MAX_GB_SECONDS, 1.0)
        pressure_penalty = max(0, ram_pressure_ratio - cls.PRESSURE_THRESHOLD) * 2.5
        
        return min(consumption_score + pressure_penalty, 1.0)
    
    @classmethod
    def normalize_apis(cls, total_calls: int, total_duration: float) -> float:
        """Normalize third-party API usage."""
        call_score = min(total_calls / cls.MAX_API_CALLS, 1.0)
        duration_score = min(total_duration / cls.MAX_TOTAL_DURATION, 1.0)
        
        # Weight frequent calls more heavily than duration
        return (1.5 * call_score + duration_score) / 2.5
    
    @classmethod
    def calculate_efficiency_score(cls, cpu_utilization: float, ram_pressure: float) -> float:
        """Calculate efficiency penalty (higher score = less efficient = more cost)."""
        cpu_inefficiency = max(0, 0.5 - cpu_utilization) * 2  # Penalty below 50%
        memory_inefficiency = max(0, ram_pressure - cls.PRESSURE_THRESHOLD) * 1.25  # Penalty above 80%
        
        return min(cpu_inefficiency + memory_inefficiency, 1.0)
    
    @classmethod
    def calculate_weighted_dynabits(
        cls,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cpu_seconds: float = 0,
        gb_seconds: float = 0,
        cpu_utilization: float = 0,
        ram_pressure_ratio: float = 0,
        api_calls: int = 0,
        api_duration: float = 0,
        weights: Dict[str, float] = None,
        base_rate: float = None
    ) -> Dict[str, float]:
        """
        Calculate weighted dynabits with normalization.
        
        Returns dict with breakdown and total.
        """
        if weights is None:
            weights = cls.DEFAULT_WEIGHTS.copy()
        if base_rate is None:
            base_rate = cls.BASE_DYNABITS_RATE
        
        # Normalize all components to 0-1 scale
        normalized_components = {
            'tokens': cls.normalize_tokens(input_tokens, output_tokens),
            'cpu': cls.normalize_cpu(cpu_seconds, cpu_utilization),
            'memory': cls.normalize_memory(gb_seconds, ram_pressure_ratio),
            'api_calls': cls.normalize_apis(api_calls, api_duration),
            'efficiency': cls.calculate_efficiency_score(cpu_utilization, ram_pressure_ratio)
        }
        
        # Apply business weights
        weighted_components = {
            component: weights[component] * normalized_components[component]
            for component in weights.keys()
        }
        
        # Calculate total weighted score
        total_weighted_score = sum(weighted_components.values())
        
        # Scale to dynabits
        total_dynabits = total_weighted_score * base_rate
        
        # Apply minimum threshold
        total_dynabits = max(total_dynabits, 0.001)
        
        return {
            'total_dynabits': round(total_dynabits, 4),
            'normalized_components': normalized_components,
            'weighted_components': weighted_components,
            'weights_used': weights,
            'base_rate': base_rate
        }
    
    @staticmethod
    def calculate_api_call_dynabits(
        input_tokens: int, 
        output_tokens: int,
        call_duration: float,
        avg_memory_gb: float,
        cpu_utilization: float,
        system_memory_info: Dict[str, float]
    ) -> float:
        """
        Calculate weighted dynabits for an individual OpenAI API call.
        """
        # Calculate RAM pressure ratio
        total_ram = system_memory_info.get('used_gb', 0) + system_memory_info.get('available_gb', 8)
        ram_pressure_ratio = system_memory_info.get('used_gb', 0) / total_ram if total_ram > 0 else 0.0
        
        # For individual API calls, focus mainly on token component
        result = DynabitsCalculator.calculate_weighted_dynabits(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cpu_seconds=call_duration * cpu_utilization,  # Estimated CPU usage
            gb_seconds=avg_memory_gb * call_duration,
            cpu_utilization=cpu_utilization,
            ram_pressure_ratio=ram_pressure_ratio,
            api_calls=0,  # No third-party APIs in OpenAI calls
            api_duration=0,
            weights={
                'tokens': 0.70,    # Higher weight for tokens in API calls
                'cpu': 0.15,
                'memory': 0.10,
                'api_calls': 0.0,
                'efficiency': 0.05
            }
        )
        
        return result['total_dynabits']
    
    @staticmethod
    def calculate_resource_only_dynabits(
        cpu_seconds: float,
        gb_seconds: float,
        cpu_utilization_percent: float,
        memory_info: Dict[str, float]
    ) -> float:
        """
        Calculate weighted dynabits for resource usage only.
        """
        cpu_utilization = cpu_utilization_percent / 100.0
        total_ram = memory_info.get('used_gb', 0) + memory_info.get('available_gb', 8)
        ram_pressure_ratio = memory_info.get('used_gb', 0) / total_ram if total_ram > 0 else 0.0
        
        # For resource tracking, focus on CPU, memory, and efficiency
        result = DynabitsCalculator.calculate_weighted_dynabits(
            input_tokens=0,
            output_tokens=0,
            cpu_seconds=cpu_seconds,
            gb_seconds=gb_seconds,
            cpu_utilization=cpu_utilization,
            ram_pressure_ratio=ram_pressure_ratio,
            api_calls=0,
            api_duration=0,
            weights={
                'tokens': 0.0,
                'cpu': 0.50,       # Higher weight for CPU in resource tracking
                'memory': 0.30,    # Higher weight for memory
                'api_calls': 0.0,
                'efficiency': 0.20  # Higher weight for efficiency
            }
        )
        
        return result['total_dynabits']
    
    @staticmethod
    def calculate_third_party_api_dynabits(
        domain: str, 
        call_count: int, 
        avg_duration: float
    ) -> float:
        """
        Calculate weighted dynabits for third-party API usage.
        """
        total_duration = avg_duration * call_count
        
        # For API tracking, focus on API calls component
        result = DynabitsCalculator.calculate_weighted_dynabits(
            input_tokens=0,
            output_tokens=0,
            cpu_seconds=0,
            gb_seconds=0,
            cpu_utilization=0.2,  # Low CPU utilization for API calls
            ram_pressure_ratio=0.5,  # Moderate pressure
            api_calls=call_count,
            api_duration=total_duration,
            weights={
                'tokens': 0.0,
                'cpu': 0.20,       # Some CPU for processing responses
                'memory': 0.10,    # Minimal memory for API handling
                'api_calls': 0.65,  # Primary focus on API usage
                'efficiency': 0.05
            }
        )
        
        return result['total_dynabits']

class TokenTracker:
    """Context manager that automatically tracks OpenAI calls with dynabits calculation"""
    
    def __init__(self, request_id: str, customer_id: str, function_name: str):
        self.customer_id = customer_id
        self.request_id = request_id
        self.function_name = function_name
        self.responses = []
        self.original_methods = {}
        self.call_stack = []  # Track which function made each call
        self.call_timestamps = []  # Track timing for each call
        self.memory_samples = []  # Track memory during execution
        self._start_time = None
        self._process = psutil.Process(os.getpid())
    
    def __enter__(self):
        self._start_time = time.time()
        # Import here to avoid circular imports
        try:
            from openai import OpenAI
            from openai.resources.chat import completions
            from openai.resources import embeddings
            import inspect
            
            # Store original methods
            self.original_chat_create = completions.Completions.create
            self.original_embeddings_create = embeddings.Embeddings.create
            
            # Create wrapper functions that track the calling function
            def chat_wrapper(self_inner, *args, **kwargs):
                call_start = time.time()
                # Find the calling function name
                calling_frame = inspect.currentframe().f_back
                calling_function = calling_frame.f_code.co_name
                
                response = self.original_chat_create(self_inner, *args, **kwargs)
                call_end = time.time()
                
                self.responses.append(response)
                self.call_stack.append(calling_function)
                self.call_timestamps.append({
                    'start': call_start,
                    'end': call_end,
                    'duration': call_end - call_start
                })
                # Sample memory at call time
                try:
                    memory_gb = self._process.memory_info().rss / (1024 ** 3)
                    self.memory_samples.append(memory_gb)
                except:
                    self.memory_samples.append(0)
                    
                return response
            
            def embeddings_wrapper(self_inner, *args, **kwargs):
                call_start = time.time()
                # Find the calling function name
                calling_frame = inspect.currentframe().f_back
                calling_function = calling_frame.f_code.co_name
                
                response = self.original_embeddings_create(self_inner, *args, **kwargs)
                call_end = time.time()
                
                self.responses.append(response)
                self.call_stack.append(calling_function)
                self.call_timestamps.append({
                    'start': call_start,
                    'end': call_end,
                    'duration': call_end - call_start
                })
                # Sample memory at call time
                try:
                    memory_gb = self._process.memory_info().rss / (1024 ** 3)
                    self.memory_samples.append(memory_gb)
                except:
                    self.memory_samples.append(0)
                    
                return response
            
            # Monkey patch the methods GLOBALLY (this is key!)
            completions.Completions.create = chat_wrapper
            embeddings.Embeddings.create = embeddings_wrapper
            
        except ImportError:
            pass  # OpenAI not available
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original methods
        try:
            from openai.resources.chat import completions
            from openai.resources import embeddings
            
            completions.Completions.create = self.original_chat_create
            embeddings.Embeddings.create = self.original_embeddings_create
        except:
            pass
        
        # Get system memory info for dynabits calculation
        try:
            mem_info = psutil.virtual_memory()
            system_memory_info = {
                'used_gb': mem_info.used / (1024**3),
                'available_gb': mem_info.available / (1024**3)
            }
        except:
            system_memory_info = {'used_gb': 0, 'available_gb': 8}  # fallback
        
        # Log all collected responses with their calling functions and dynabits
        for i, (response, calling_function, timing) in enumerate(zip(self.responses, self.call_stack, self.call_timestamps)):
            try:
                usage = openai_token_usage(response)
                if usage:
                    # Create descriptive function names based on where the call was made
                    if calling_function == self.function_name:
                        # Direct call from decorated function
                        function_name = f"{self.function_name}_call_{i+1}" if len(self.responses) > 1 else self.function_name
                    else:
                        # Call from nested function
                        function_name = f"{self.function_name}_{calling_function}_call_{i+1}"
                    
                    # Calculate token-only dynabits for this individual API call
                    avg_memory = self.memory_samples[i] if i < len(self.memory_samples) else 0
                    cpu_utilization = 0.3  # 30% estimate for API calls
                    
                    api_call_dynabits = DynabitsCalculator.calculate_api_call_dynabits(
                        input_tokens=usage.get('prompt_tokens', 0),
                        output_tokens=usage.get('completion_tokens', 0),
                        call_duration=timing['duration'],
                        avg_memory_gb=avg_memory,
                        cpu_utilization=cpu_utilization,
                        system_memory_info=system_memory_info
                    )
                    
                    # Add dynabits to usage info
                    usage['dynabits'] = api_call_dynabits
                    usage['call_duration'] = timing['duration']
                    
                    log_token_usage_to_api(self.request_id, self.customer_id, function_name, usage)
            except Exception as e:
                print(f"Error tracking token usage for call {i+1}: {e}")

def track_token_usage(request_id, customer_id):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with TokenTracker(request_id, customer_id, func.__name__):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

def log_token_usage_to_api(request_id, customer_id, function_name, usage):
    """
    Send token usage with dynabits to FastAPI endpoint.
    """
    data = {
        'request_id': request_id,
        'customer_id': customer_id,
        'function_name': function_name,
        'model': usage.get('model'),
        'prompt_tokens': usage.get('prompt_tokens'),
        'completion_tokens': usage.get('completion_tokens'),
        'total_tokens': usage.get('total_tokens'),
        'dynabits': usage.get('dynabits'),
        'call_duration': usage.get('call_duration'),
    }
    
    send_to_api('/token-usage', data)

# Resource tracking functions (shared by both decorators)
def get_process():
    return psutil.Process(os.getpid())

def get_memory_gb(process):
    """Returns memory in GB from RSS (resident set size)"""
    return process.memory_info().rss / (1024 ** 3)

def log_to_api(request_id, customer_id, function_name, duration, cpu_seconds, gb_seconds, detailed_cpu_metrics, resource_dynabits):
    """
    Send resource metrics to FastAPI endpoint.
    """
    data = {
        'request_id': request_id,
        'customer_id': customer_id,
        'function_name': function_name,
        'duration_sec': duration,
        'cpu_seconds': cpu_seconds,
        'gb_seconds': gb_seconds,
        'detailed_cpu_metrics': detailed_cpu_metrics,
        'dynabits': resource_dynabits,
    }
    
    send_to_api('/resource-metrics', data)

def track_resources_db(request_id, customer_id):
    """
    Decorator that tracks CPU-seconds and GB-seconds used by a function,
    monitors system-wide CPU, threading, and memory usage, calculates dynabits,
    and sends everything to FastAPI endpoint.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            process = get_process()
            mem_samples = []
            cpu_samples = []
            thread_samples = []

            def sample_metrics():
                while not stop_event.is_set():
                    try:
                        mem_samples.append(get_memory_gb(process))
                        sample = {
                            "timestamp": time.time(),
                            "cpu_percent": process.cpu_percent(),
                            "num_threads": process.num_threads(),
                            "ctx_switches": (
                                process.num_ctx_switches().voluntary 
                                if hasattr(process, 'num_ctx_switches') 
                                else None
                            ),
                            "memory_rss": process.memory_info().rss
                        }
                        cpu_samples.append(sample)
                        thread_samples.append(threading.active_count())
                    except (psutil.NoSuchProcess, psutil.AccessDenied, NotImplementedError):
                        break
                    time.sleep(0.1)

            # Initial readings
            mem_info_before = psutil.virtual_memory()
            mem_before = mem_info_before.percent
            logical_cores = psutil.cpu_count(logical=True)
            physical_cores = psutil.cpu_count(logical=False)
            cpu_times_start = process.cpu_times()
            process_start_time = time.time()

            stop_event = threading.Event()
            sampler = threading.Thread(target=sample_metrics)
            sampler.start()

            start_time = time.time()
            cpu_time_start = cpu_times_start.user + cpu_times_start.system

            result = func(*args, **kwargs)

            end_time = time.time()
            cpu_times_end = process.cpu_times()
            cpu_time_end = cpu_times_end.user + cpu_times_end.system
            stop_event.set()
            sampler.join()

            mem_info_after = psutil.virtual_memory()
            mem_after = mem_info_after.percent

            process_duration = end_time - process_start_time
            user_cpu_time = cpu_times_end.user - cpu_times_start.user
            system_cpu_time = cpu_times_end.system - cpu_times_start.system
            total_cpu_time = user_cpu_time + system_cpu_time
            cpu_utilization_percent = (total_cpu_time / process_duration * 100) if process_duration > 0 else 0

            try:
                system_cpu_usage = psutil.cpu_percent(interval=None)
            except:
                system_cpu_usage = 0.0

            duration = end_time - start_time
            cpu_seconds = cpu_time_end - cpu_time_start
            avg_memory_gb = sum(mem_samples) / len(mem_samples) if mem_samples else 0
            gb_seconds = avg_memory_gb * duration

            cpu_efficiency = (total_cpu_time / (process_duration * logical_cores)) * 100 if process_duration > 0 else 0

            # Calculate resource-only dynabits for the function execution
            memory_info = {
                'used_gb': mem_info_after.used / (1024**3),
                'available_gb': mem_info_after.available / (1024**3)
            }
            
            resource_only_dynabits = DynabitsCalculator.calculate_resource_only_dynabits(
                cpu_seconds=cpu_seconds,
                gb_seconds=gb_seconds,
                cpu_utilization_percent=cpu_utilization_percent,
                memory_info=memory_info
            )

            # Detailed system usage report
            system_usage_report = {
                "time_taken_sec": round(duration, 2),
                "logical_cores": logical_cores,
                "physical_cores": physical_cores,
                "memory_usage_before_percent": round(mem_before, 2),
                "memory_usage_after_percent": round(mem_after, 2),
                "memory_available_gb": round(mem_info_after.available / (1024**3), 2),
                "memory_available_mb": round(mem_info_after.available / (1024**2), 2),
                "memory_used_gb": round(mem_info_after.used / (1024**3), 2),
                "memory_used_mb": round(mem_info_after.used / (1024**2), 2),
                "memory_total_gb": round(mem_info_after.total / (1024**3), 2),
                "memory_total_mb": round(mem_info_after.total / (1024**2), 2),
                "process_memory_gb": round(avg_memory_gb, 4),
                "process_memory_mb": round(avg_memory_gb * 1024, 2),
                "process_memory_rss_gb": round(process.memory_info().rss / (1024**3), 4),
                "process_memory_rss_mb": round(process.memory_info().rss / (1024**2), 2),
                "process_cpu_seconds_total": round(total_cpu_time, 4),
                "process_cpu_seconds_user": round(user_cpu_time, 4),
                "process_cpu_seconds_system": round(system_cpu_time, 4),
                "process_cpu_utilization_percent": round(cpu_utilization_percent, 2),
                "cpu_efficiency_percent": round(cpu_efficiency, 2),
                "container_isolated": system_cpu_usage == 0.0,
                "measurement_notes": "System CPU/memory metrics may be limited due to Cloud Run container isolation",
                "resource_dynabits": resource_only_dynabits
            }

            detailed_cpu_metrics_str = json.dumps(system_usage_report)

            log_to_api(
                request_id,
                customer_id,
                func.__name__, 
                duration, 
                cpu_seconds, 
                gb_seconds, 
                detailed_cpu_metrics_str,
                resource_only_dynabits
            )

            return result
        return wrapper
    return decorator

def get_token_usage_summary(request_id):
    """Get total token usage for a request from the FastAPI endpoint."""
    try:
        config = get_api_config()
        url = f"{config['base_url']}/token-usage-summary/{request_id}"
        
        headers = {}
        if config['api_key']:
            headers['Authorization'] = f"Bearer {config['api_key']}"
        
        response = requests.get(url, headers=headers, timeout=config['timeout'])
        response.raise_for_status()
        
        data = response.json()
        return data.get('prompt_tokens', 0), data.get('completion_tokens', 0)
    except Exception as e:
        print(f"Error getting token usage summary: {e}")
        return 0, 0

def track_resources_kafka(request_id: str, customer_id: str, topic: str):
    """
    Decorator that tracks CPU-seconds, GB-seconds, detailed CPU/memory/thread usage,
    calculates dynabits, and sends the metrics to Kafka.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            producer = get_kafka_producer()
            process = get_process()
            mem_samples = []
            cpu_samples = []
            thread_samples = []
            stop_event = threading.Event()

            def sample_metrics():
                while not stop_event.is_set():
                    try:
                        mem_samples.append(get_memory_gb(process))
                        sample = {
                            "timestamp": time.time(),
                            "cpu_percent": process.cpu_percent(),
                            "num_threads": process.num_threads(),
                            "ctx_switches": process.num_ctx_switches().voluntary if hasattr(process, 'num_ctx_switches') else None,
                            "memory_rss": process.memory_info().rss
                        }
                        cpu_samples.append(sample)
                        thread_samples.append(threading.active_count())
                    except (psutil.NoSuchProcess, psutil.AccessDenied, NotImplementedError):
                        break
                    time.sleep(0.1)

            # Initial system & process state
            mem_info_before = psutil.virtual_memory()
            mem_before = mem_info_before.percent
            logical_cores = psutil.cpu_count(logical=True)
            physical_cores = psutil.cpu_count(logical=False)
            cpu_times_start = process.cpu_times()
            process_start_time = time.time()
            cpu_time_start = cpu_times_start.user + cpu_times_start.system

            sampler = threading.Thread(target=sample_metrics)
            sampler.start()

            result = func(*args, **kwargs)

            # End measurements
            end_time = time.time()
            cpu_times_end = process.cpu_times()
            cpu_time_end = cpu_times_end.user + cpu_times_end.system
            stop_event.set()
            sampler.join()

            mem_info_after = psutil.virtual_memory()
            mem_after = mem_info_after.percent

            process_duration = end_time - process_start_time
            user_cpu_time = cpu_times_end.user - cpu_times_start.user
            system_cpu_time = cpu_times_end.system - cpu_times_start.system
            total_cpu_time = user_cpu_time + system_cpu_time
            cpu_utilization_percent = (total_cpu_time / process_duration * 100) if process_duration > 0 else 0

            try:
                system_cpu_usage = psutil.cpu_percent(interval=None)
            except:
                system_cpu_usage = 0.0

            duration = end_time - process_start_time
            cpu_seconds = cpu_time_end - cpu_time_start
            avg_memory_gb = sum(mem_samples) / len(mem_samples) if mem_samples else 0
            gb_seconds = avg_memory_gb * duration

            cpu_efficiency = (total_cpu_time / (process_duration * logical_cores)) * 100 if process_duration > 0 else 0

            # Calculate resource-only dynabits for the function execution
            memory_info = {
                'used_gb': mem_info_after.used / (1024**3),
                'available_gb': mem_info_after.available / (1024**3)
            }
            
            resource_only_dynabits = DynabitsCalculator.calculate_resource_only_dynabits(
                cpu_seconds=cpu_seconds,
                gb_seconds=gb_seconds,
                cpu_utilization_percent=cpu_utilization_percent,
                memory_info=memory_info
            )

            # Match DB-level detailed metrics with resource dynabits only
            detailed_cpu_metrics = {
                "time_taken_sec": round(duration, 2),
                "logical_cores": logical_cores,
                "physical_cores": physical_cores,
                "memory_usage_before_percent": round(mem_before, 2),
                "memory_usage_after_percent": round(mem_after, 2),
                "memory_available_gb": round(mem_info_after.available / (1024**3), 2),
                "memory_available_mb": round(mem_info_after.available / (1024**2), 2),
                "memory_used_gb": round(mem_info_after.used / (1024**3), 2),
                "memory_used_mb": round(mem_info_after.used / (1024**2), 2),
                "memory_total_gb": round(mem_info_after.total / (1024**3), 2),
                "memory_total_mb": round(mem_info_after.total / (1024**2), 2),
                "process_memory_gb": round(avg_memory_gb, 4),
                "process_memory_mb": round(avg_memory_gb * 1024, 2),
                "process_memory_rss_gb": round(process.memory_info().rss / (1024**3), 4),
                "process_memory_rss_mb": round(process.memory_info().rss / (1024**2), 2),
                "process_cpu_seconds_total": round(total_cpu_time, 4),
                "process_cpu_seconds_user": round(user_cpu_time, 4),
                "process_cpu_seconds_system": round(system_cpu_time, 4),
                "process_cpu_utilization_percent": round(cpu_utilization_percent, 2),
                "cpu_efficiency_percent": round(cpu_efficiency, 2),
                "container_isolated": system_cpu_usage == 0.0,
                "measurement_notes": "System CPU/memory metrics may be limited due to Cloud Run container isolation",
                "resource_dynabits": resource_only_dynabits
            }

            metrics = {
                "customer_id": customer_id,
                "request_id": request_id,
                "function_name": func.__name__,
                "duration_sec": duration,
                "cpu_seconds": cpu_seconds,
                "gb_seconds": gb_seconds,
                "detailed_cpu_metrics": detailed_cpu_metrics,
                "dynabits": resource_only_dynabits,
                "timestamp": time.time()
            }

            try:
                producer.produce(topic, key=func.__name__, value=json.dumps(metrics))
                producer.flush()
            except Exception as e:
                print(f"Error sending resource metrics to Kafka: {e}")

            return result
        return wrapper
    return decorator

class TokenTrackerKafka:
    """Context manager that automatically tracks OpenAI calls and sends to Kafka with dynabits"""
    
    def __init__(self, request_id: str, customer_id: str, function_name: str, topic: str):
        self.customer_id = customer_id
        self.request_id = request_id
        self.function_name = function_name
        self.topic = topic
        self.responses = []
        self.original_methods = {}
        self.call_stack = []  # Track which function made each call
        self.call_timestamps = []  # Track timing for each call
        self.memory_samples = []  # Track memory during execution
        self.producer = get_kafka_producer()  # Get producer instance
        self._process = psutil.Process(os.getpid())
    
    def __enter__(self):
        # Import here to avoid circular imports
        try:
            from openai import OpenAI
            from openai.resources.chat import completions
            from openai.resources import embeddings
            
            # Store original methods
            self.original_chat_create = completions.Completions.create
            self.original_embeddings_create = embeddings.Embeddings.create
            
            # Create wrapper functions that track the calling function
            def chat_wrapper(self_inner, *args, **kwargs):
                call_start = time.time()
                # Find the calling function name
                calling_frame = inspect.currentframe().f_back
                calling_function = calling_frame.f_code.co_name
                
                response = self.original_chat_create(self_inner, *args, **kwargs)
                call_end = time.time()
                
                self.responses.append(response)
                self.call_stack.append(calling_function)
                self.call_timestamps.append({
                    'start': call_start,
                    'end': call_end,
                    'duration': call_end - call_start
                })
                # Sample memory at call time
                try:
                    memory_gb = self._process.memory_info().rss / (1024 ** 3)
                    self.memory_samples.append(memory_gb)
                except:
                    self.memory_samples.append(0)
                    
                return response
            
            def embeddings_wrapper(self_inner, *args, **kwargs):
                call_start = time.time()
                # Find the calling function name
                calling_frame = inspect.currentframe().f_back
                calling_function = calling_frame.f_code.co_name
                
                response = self.original_embeddings_create(self_inner, *args, **kwargs)
                call_end = time.time()
                
                self.responses.append(response)
                self.call_stack.append(calling_function)
                self.call_timestamps.append({
                    'start': call_start,
                    'end': call_end,
                    'duration': call_end - call_start
                })
                # Sample memory at call time
                try:
                    memory_gb = self._process.memory_info().rss / (1024 ** 3)
                    self.memory_samples.append(memory_gb)
                except:
                    self.memory_samples.append(0)
                    
                return response
            
            # Monkey patch the methods GLOBALLY (this is key!)
            completions.Completions.create = chat_wrapper
            embeddings.Embeddings.create = embeddings_wrapper
            
        except ImportError:
            pass  # OpenAI not available
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original methods
        try:
            from openai.resources.chat import completions
            from openai.resources import embeddings
            
            completions.Completions.create = self.original_chat_create
            embeddings.Embeddings.create = self.original_embeddings_create
        except:
            pass
        
        # Get system memory info for dynabits calculation
        try:
            mem_info = psutil.virtual_memory()
            system_memory_info = {
                'used_gb': mem_info.used / (1024**3),
                'available_gb': mem_info.available / (1024**3)
            }
        except:
            system_memory_info = {'used_gb': 0, 'available_gb': 8}  # fallback
        
        # Send all collected responses to Kafka with their calling functions and dynabits
        for i, (response, calling_function, timing) in enumerate(zip(self.responses, self.call_stack, self.call_timestamps)):
            try:
                usage = openai_token_usage(response)
                if usage:
                    # Create descriptive function names based on where the call was made
                    if calling_function == self.function_name:
                        # Direct call from decorated function
                        function_name = f"{self.function_name}_call_{i+1}" if len(self.responses) > 1 else self.function_name
                    else:
                        # Call from nested function
                        function_name = f"{self.function_name}_{calling_function}_call_{i+1}"
                    
                    # Calculate token-only dynabits for this individual API call
                    avg_memory = self.memory_samples[i] if i < len(self.memory_samples) else 0
                    cpu_utilization = 0.3  # 30% estimate for API calls
                    
                    api_call_dynabits = DynabitsCalculator.calculate_api_call_dynabits(
                        input_tokens=usage.get('prompt_tokens', 0),
                        output_tokens=usage.get('completion_tokens', 0),
                        call_duration=timing['duration'],
                        avg_memory_gb=avg_memory,
                        cpu_utilization=cpu_utilization,
                        system_memory_info=system_memory_info
                    )
                    
                    # Add dynabits to usage info
                    usage['dynabits'] = api_call_dynabits
                    usage['call_duration'] = timing['duration']
                    
                    self._send_token_usage_to_kafka(function_name, usage)
            except Exception as e:
                print(f"Error tracking token usage for call {i+1}: {e}")
    
    def _send_token_usage_to_kafka(self, function_name: str, usage: Dict[str, Any]):
        """Send token usage metrics with dynabits to Kafka"""
        message = {
            'customer_id': self.customer_id,
            'request_id': self.request_id,
            'function_name': function_name,
            'model': usage['model'],
            'prompt_tokens': usage['prompt_tokens'],
            'completion_tokens': usage['completion_tokens'],
            'total_tokens': usage['total_tokens'],
            'dynabits': usage['dynabits'],
            'call_duration': usage['call_duration'],
            'timestamp': time.time()
        }
        
        try:
            # Use function_name as the key for better partitioning
            self.producer.produce(
                self.topic, 
                key=function_name, 
                value=json.dumps(message)
            )
            self.producer.flush()  # Ensure message is sent
        except Exception as e:
            print(f"Error sending token usage to Kafka: {e}")


def track_token_usage_kafka(request_id: str, customer_id: str, topic: str):
    """
    Decorator that tracks OpenAI token usage, calculates dynabits, and sends metrics to Kafka.
    
    Args:
        request_id: Unique identifier for the request
        customer_id: Customer identifier
        topic: Kafka topic to send token usage metrics to
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with TokenTrackerKafka(request_id, customer_id, func.__name__, topic):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

# Alternative: Direct logging function for Kafka (similar to log_token_usage_to_db)
def log_token_usage_to_kafka(request_id: str, customer_id: str, function_name: str, usage: Dict[str, Any], topic: str):
    """
    Log token usage with dynabits directly to Kafka (alternative to decorator approach).
    
    Args:
        request_id: Unique identifier for the request
        customer_id: Customer identifier
        function_name: Name of the function that made the OpenAI call
        usage: Token usage dictionary from openai_token_usage() (should include dynabits)
        topic: Kafka topic to send metrics to
    """
    producer = get_kafka_producer()
    
    message = {
        'customer_id': customer_id,
        'request_id': request_id,
        'function_name': function_name,
        'model': usage['model'],
        'prompt_tokens': usage['prompt_tokens'],
        'completion_tokens': usage['completion_tokens'],
        'total_tokens': usage['total_tokens'],
        'dynabits': usage.get('dynabits', 0),
        'call_duration': usage.get('call_duration', 0),
        'timestamp': time.time()
    }
    
    try:
        producer.produce(topic, key=function_name, value=json.dumps(message))
        producer.flush()
    except Exception as e:
        print(f"Error sending token usage to Kafka: {e}")
        raise

class ThirdPartyAPITracker:
    """Context manager that tracks third-party API calls with dynabits calculation."""

    def __init__(self, request_id, customer_id, function_name, kafka_topic='TP_APIS'):
        self.request_id = request_id
        self.customer_id = customer_id
        self.function_name = function_name
        self.kafka_topic = kafka_topic
        self.api_counter = Counter()
        self.api_timings = {}  # Track timing per domain
        self.api_dynabits = {}  # Track dynabits per domain
        self._counter_lock = threading.Lock()
        self.original_methods = {}
        self.producer = get_kafka_producer() if kafka_topic else None
        self._process = psutil.Process(os.getpid())
        self._start_time = time.time()

    def _should_track(self, url: str) -> bool:
        try:
            domain = urlparse(url).netloc
            return domain and domain.lower() not in EXCLUDED_DOMAINS
        except Exception:
            return False

    def _record_api_call(self, domain: str, duration: float = 0.1):
        """Record an API call with timing information."""
        with self._counter_lock:
            self.api_counter[domain] += 1
            if domain not in self.api_timings:
                self.api_timings[domain] = []
            self.api_timings[domain].append(duration)

    def _calculate_api_dynabits(self, domain: str, call_count: int, avg_duration: float) -> float:
        """
        Calculate dynabits for third-party API usage only.
        
        Args:
            domain: API domain
            call_count: Number of calls to this domain
            avg_duration: Average duration per call
        """
        return DynabitsCalculator.calculate_third_party_api_dynabits(
            domain=domain,
            call_count=call_count,
            avg_duration=avg_duration
        )

    # --- PATCHING ---
    def _patch_requests(self):
        original = requests.Session.request
        self.original_methods["requests"] = original
        tracker = self  # Capture the tracker instance

        def wrapped(session, method, url, *args, **kwargs):
            if tracker._should_track(url):
                domain = urlparse(url).netloc
                start_time = time.time()
                try:
                    response = original(session, method, url, *args, **kwargs)
                    duration = time.time() - start_time
                    tracker._record_api_call(domain, duration)
                    return response
                except Exception as e:
                    duration = time.time() - start_time
                    tracker._record_api_call(domain, duration)
                    raise e
            else:
                return original(session, method, url, *args, **kwargs)

        requests.Session.request = wrapped

    def _patch_http_client(self):
        original = http.client.HTTPConnection.request
        self.original_methods["http_client"] = original
        tracker = self  # Capture the tracker instance

        def wrapped(conn, method, url, *args, **kwargs):
            host = getattr(conn, "host", None)
            scheme = getattr(conn, "scheme", "http")
            if host:
                full_url = f"{scheme}://{host}{url}"
                if tracker._should_track(full_url):
                    start_time = time.time()
                    try:
                        response = original(conn, method, url, *args, **kwargs)
                        duration = time.time() - start_time
                        tracker._record_api_call(host, duration)
                        return response
                    except Exception as e:
                        duration = time.time() - start_time
                        tracker._record_api_call(host, duration)
                        raise e
            return original(conn, method, url, *args, **kwargs)

        http.client.HTTPConnection.request = wrapped

    def _patch_urllib(self):
        original = urllib.request.OpenerDirector.open
        self.original_methods["urllib"] = original
        tracker = self  # Capture the tracker instance

        def wrapped(opener, fullurl, *args, **kwargs):
            url_str = fullurl.get_full_url() if hasattr(fullurl, "get_full_url") else str(fullurl)
            if tracker._should_track(url_str):
                domain = urlparse(url_str).netloc
                start_time = time.time()
                try:
                    response = original(opener, fullurl, *args, **kwargs)
                    duration = time.time() - start_time
                    tracker._record_api_call(domain, duration)
                    return response
                except Exception as e:
                    duration = time.time() - start_time
                    tracker._record_api_call(domain, duration)
                    raise e
            else:
                return original(opener, fullurl, *args, **kwargs)

        urllib.request.OpenerDirector.open = wrapped

    def _patch_aiohttp(self):
        if aiohttp is None:
            return  # Skip if aiohttp not available

        original = aiohttp.ClientSession._request
        self.original_methods["aiohttp"] = original
        tracker = self  # Capture the tracker instance

        async def wrapped(session, method, url, *args, **kwargs):
            if tracker._should_track(url):
                domain = urlparse(url).netloc
                start_time = time.time()
                try:
                    response = await original(session, method, url, *args, **kwargs)
                    duration = time.time() - start_time
                    tracker._record_api_call(domain, duration)
                    return response
                except Exception as e:
                    duration = time.time() - start_time
                    tracker._record_api_call(domain, duration)
                    raise e
            else:
                return await original(session, method, url, *args, **kwargs)

        aiohttp.ClientSession._request = wrapped

    # --- CONTEXT MANAGER ---
    def __enter__(self):
        self._patch_requests()
        self._patch_http_client()
        self._patch_urllib()
        self._patch_aiohttp()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Calculate dynabits for each domain
        for domain, count in self.api_counter.items():
            if domain in self.api_timings and self.api_timings[domain]:
                avg_duration = sum(self.api_timings[domain]) / len(self.api_timings[domain])
            else:
                avg_duration = 0.1  # Default duration for calls without timing
            
            dynabits = self._calculate_api_dynabits(domain, count, avg_duration)
            self.api_dynabits[domain] = dynabits
        
        # Restore originals
        for key, method in self.original_methods.items():
            if key == "requests":
                requests.Session.request = method
            elif key == "http_client":
                http.client.HTTPConnection.request = method
            elif key == "urllib":
                urllib.request.OpenerDirector.open = method
            elif key == "aiohttp" and aiohttp:
                aiohttp.ClientSession._request = method

        if self.kafka_topic:
            self._send_to_kafka()
        else:
            self._log_to_api()

    # --- LOGGING ---
    def _send_to_kafka(self):
        total_dynabits = sum(self.api_dynabits.values())
        
        message = {
            "customer_id": self.customer_id,
            "request_id": self.request_id,
            "function_name": self.function_name,
            "api_calls": dict(self.api_counter),
            "api_dynabits": self.api_dynabits,
            "total_api_dynabits": total_dynabits,
            "api_timings": {domain: {
                "avg_duration": sum(timings) / len(timings) if timings else 0,
                "total_calls": len(timings)
            } for domain, timings in self.api_timings.items()},
            "timestamp": time.time()
        }
        try:
            self.producer.produce(self.kafka_topic, key=self.function_name, value=json.dumps(message))
            self.producer.flush()
        except Exception as e:
            print(f"Error sending API tracker metrics to Kafka: {e}")

    def _log_to_api(self):
        """Send third-party API usage to FastAPI endpoint."""
        for domain, count in self.api_counter.items():
            dynabits = self.api_dynabits.get(domain, 0)
            avg_duration = 0
            if domain in self.api_timings and self.api_timings[domain]:
                avg_duration = sum(self.api_timings[domain]) / len(self.api_timings[domain])
            
            data = {
                'request_id': self.request_id,
                'customer_id': self.customer_id,
                'function_name': self.function_name,
                'api_domain': domain,
                'call_count': count,
                'avg_duration': avg_duration,
                'dynabits': dynabits,
            }
            
            send_to_api('/api-usage', data)

# --- DECORATORS ---
def track_api_usage_kafka(request_id: str, customer_id: str, topic: str):
    """Decorator to track third-party API usage and send to Kafka."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with ThirdPartyAPITracker(request_id, customer_id, func.__name__, kafka_topic=topic):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def track_api_usage_db(request_id: str, customer_id: str):
    """Decorator to track third-party API usage and send to FastAPI."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with ThirdPartyAPITracker(request_id, customer_id, func.__name__, kafka_topic=None):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Combined decorators for complete tracking
def track_all_metrics_db(request_id: str, customer_id: str):
    """
    Combined decorator that tracks all metrics (tokens, resources, APIs) and sends to FastAPI with dynabits.
    """
    def decorator(func):
        @functools.wraps(func)
        @track_resources_db(request_id, customer_id)
        @track_token_usage(request_id, customer_id)
        @track_api_usage_db(request_id, customer_id)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

def track_all_metrics_kafka(request_id: str, customer_id: str, resource_topic: str, token_topic: str, api_topic: str):
    """
    Combined decorator that tracks all metrics (tokens, resources, APIs) and sends to Kafka with dynabits.
    """
    def decorator(func):
        @functools.wraps(func)
        @track_resources_kafka(request_id, customer_id, resource_topic)
        @track_token_usage_kafka(request_id, customer_id, token_topic)
        @track_api_usage_kafka(request_id, customer_id, api_topic)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Utility function to get dynabits summary for a request
def get_request_dynabits_summary(request_id: str) -> Dict[str, float]:
    """
    Get a comprehensive summary of dynabits for a specific request from the FastAPI endpoint.
    
    Returns:
        Dict with total_dynabits, token_dynabits, resource_dynabits, and third_party_api_dynabits
    """
    try:
        config = get_api_config()
        url = f"{config['base_url']}/dynabits-summary/{request_id}"
        
        headers = {}
        if config['api_key']:
            headers['Authorization'] = f"Bearer {config['api_key']}"
        
        response = requests.get(url, headers=headers, timeout=config['timeout'])
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'total_dynabits': data.get('total_billable_dynabits', 0),
            'function_dynabits': data.get('function_total_dynabits', 0),
            'token_dynabits': data.get('openai_api_dynabits', 0),
            'resource_dynabits': data.get('function_resource_dynabits', 0),
            'third_party_api_dynabits': data.get('third_party_api_dynabits', 0),
            'individual_api_calls_dynabits': data.get('openai_api_dynabits', 0)
        }
    except Exception as e:
        print(f"Error getting dynabits summary: {e}")
        return {
            'total_dynabits': 0,
            'function_dynabits': 0,
            'token_dynabits': 0,
            'resource_dynabits': 0,
            'third_party_api_dynabits': 0,
            'individual_api_calls_dynabits': 0
        }