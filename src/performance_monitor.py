"""
Performance Monitor for PDF Processing
Tracks processing times, resource usage, and performance metrics
"""

import time
import psutil
import threading
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from collections import defaultdict
from loguru import logger

class PerformanceMonitor:
    """Monitors and tracks performance metrics for PDF processing"""
    
    def __init__(self):
        self.active_processes = {}
        self.performance_history = []
        self.resource_usage = defaultdict(list)
        self.max_history_size = 1000
        
        # Start background monitoring
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Performance Monitor initialized")
    
    @contextmanager
    def track_process(self, process_name: str):
        """Context manager to track a processing task"""
        process_id = f"{process_name}_{int(time.time())}"
        
        # Record start metrics
        start_time = time.time()
        start_memory = psutil.virtual_memory().used
        start_cpu = psutil.cpu_percent()
        
        # Register process
        self.active_processes[process_id] = {
            "name": process_name,
            "start_time": start_time,
            "start_memory": start_memory,
            "start_cpu": start_cpu,
            "status": "running"
        }
        
        try:
            yield process_id
        finally:
            # Record end metrics
            end_time = time.time()
            end_memory = psutil.virtual_memory().used
            end_cpu = psutil.cpu_percent()
            
            # Calculate metrics
            duration = end_time - start_time
            memory_delta = end_memory - start_memory
            avg_cpu = (start_cpu + end_cpu) / 2
            
            # Update process info
            if process_id in self.active_processes:
                self.active_processes[process_id].update({
                    "end_time": end_time,
                    "duration": duration,
                    "end_memory": end_memory,
                    "memory_delta": memory_delta,
                    "avg_cpu": avg_cpu,
                    "status": "completed"
                })
            
            # Record performance data
            self._record_performance(process_id, duration, memory_delta, avg_cpu)
            
            # Clean up after delay
            threading.Timer(60.0, self._cleanup_process, args=[process_id]).start()
    
    def _record_performance(self, process_id: str, duration: float, memory_delta: int, avg_cpu: float):
        """Record performance metrics"""
        try:
            performance_data = {
                "process_id": process_id,
                "timestamp": time.time(),
                "duration": duration,
                "memory_delta_mb": memory_delta / (1024 * 1024),
                "avg_cpu_percent": avg_cpu,
                "memory_usage_mb": psutil.virtual_memory().used / (1024 * 1024),
                "cpu_usage_percent": psutil.cpu_percent()
            }
            
            self.performance_history.append(performance_data)
            
            # Limit history size
            if len(self.performance_history) > self.max_history_size:
                self.performance_history = self.performance_history[-self.max_history_size:]
            
            # Log performance
            logger.info(f"Performance: {process_id} - Duration: {duration:.2f}s, "
                       f"Memory: {memory_delta/(1024*1024):.1f}MB, CPU: {avg_cpu:.1f}%")
            
        except Exception as e:
            logger.error(f"Error recording performance: {e}")
    
    def _monitor_resources(self):
        """Background thread to monitor system resources"""
        while self.monitoring:
            try:
                # Record current resource usage
                current_time = time.time()
                memory_usage = psutil.virtual_memory().percent
                cpu_usage = psutil.cpu_percent()
                disk_usage = psutil.disk_usage('/').percent
                
                self.resource_usage["memory"].append((current_time, memory_usage))
                self.resource_usage["cpu"].append((current_time, cpu_usage))
                self.resource_usage["disk"].append((current_time, disk_usage))
                
                # Limit resource history
                for resource_type in self.resource_usage:
                    if len(self.resource_usage[resource_type]) > 1000:
                        self.resource_usage[resource_type] = self.resource_usage[resource_type][-1000:]
                
                # Check for resource warnings
                if memory_usage > 90:
                    logger.warning(f"High memory usage: {memory_usage:.1f}%")
                if cpu_usage > 90:
                    logger.warning(f"High CPU usage: {cpu_usage:.1f}%")
                if disk_usage > 90:
                    logger.warning(f"High disk usage: {disk_usage:.1f}%")
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                time.sleep(10)
    
    def _cleanup_process(self, process_id: str):
        """Clean up completed process data"""
        if process_id in self.active_processes:
            del self.active_processes[process_id]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        try:
            if not self.performance_history:
                return {"error": "No performance data available"}
            
            # Calculate statistics
            durations = [p["duration"] for p in self.performance_history]
            memory_deltas = [p["memory_delta_mb"] for p in self.performance_history]
            cpu_usage = [p["avg_cpu_percent"] for p in self.performance_history]
            
            stats = {
                "total_processes": len(self.performance_history),
                "active_processes": len(self.active_processes),
                "duration_stats": {
                    "mean": sum(durations) / len(durations),
                    "median": sorted(durations)[len(durations)//2],
                    "min": min(durations),
                    "max": max(durations),
                    "std": self._calculate_std(durations)
                },
                "memory_stats": {
                    "mean_delta_mb": sum(memory_deltas) / len(memory_deltas),
                    "max_delta_mb": max(memory_deltas),
                    "total_delta_mb": sum(memory_deltas)
                },
                "cpu_stats": {
                    "mean_percent": sum(cpu_usage) / len(cpu_usage),
                    "max_percent": max(cpu_usage)
                },
                "current_resources": {
                    "memory_percent": psutil.virtual_memory().percent,
                    "cpu_percent": psutil.cpu_percent(),
                    "disk_percent": psutil.disk_usage('/').percent
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting performance stats: {e}")
            return {"error": str(e)}
    
    def get_process_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent process history"""
        try:
            recent_processes = self.performance_history[-limit:] if self.performance_history else []
            return recent_processes
        except Exception as e:
            logger.error(f"Error getting process history: {e}")
            return []
    
    def get_resource_usage(self, resource_type: str = "memory", limit: int = 100) -> List[tuple]:
        """Get resource usage history"""
        try:
            if resource_type not in self.resource_usage:
                return []
            
            return self.resource_usage[resource_type][-limit:]
        except Exception as e:
            logger.error(f"Error getting resource usage: {e}")
            return []
    
    def _calculate_std(self, values: list) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def get_performance_alerts(self) -> List[str]:
        """Get performance alerts based on thresholds"""
        alerts = []
        
        try:
            # Check current resource usage
            memory_usage = psutil.virtual_memory().percent
            cpu_usage = psutil.cpu_percent()
            disk_usage = psutil.disk_usage('/').percent
            
            if memory_usage > 85:
                alerts.append(f"High memory usage: {memory_usage:.1f}%")
            if cpu_usage > 85:
                alerts.append(f"High CPU usage: {cpu_usage:.1f}%")
            if disk_usage > 85:
                alerts.append(f"High disk usage: {disk_usage:.1f}%")
            
            # Check performance trends
            if len(self.performance_history) >= 10:
                recent_durations = [p["duration"] for p in self.performance_history[-10:]]
                avg_duration = sum(recent_durations) / len(recent_durations)
                
                if avg_duration > 30:  # More than 30 seconds average
                    alerts.append(f"Slow processing detected: {avg_duration:.1f}s average")
            
            # Check active processes
            if len(self.active_processes) > 10:
                alerts.append(f"High number of active processes: {len(self.active_processes)}")
            
        except Exception as e:
            logger.error(f"Error generating performance alerts: {e}")
        
        return alerts
    
    def cleanup_old_data(self, max_age_hours: int = 24):
        """Clean up old performance data"""
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            # Clean performance history
            self.performance_history = [
                p for p in self.performance_history
                if current_time - p["timestamp"] < max_age_seconds
            ]
            
            # Clean resource usage data
            for resource_type in self.resource_usage:
                self.resource_usage[resource_type] = [
                    (timestamp, value) for timestamp, value in self.resource_usage[resource_type]
                    if current_time - timestamp < max_age_seconds
                ]
            
            logger.info("Cleaned up old performance data")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def stop_monitoring(self):
        """Stop the background monitoring thread"""
        self.monitoring = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5) 