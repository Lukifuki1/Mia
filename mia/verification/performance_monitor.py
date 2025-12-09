#!/usr/bin/env python3
"""
MIA Enterprise AGI - Performance Monitor
========================================

Performance monitoring and benchmarking system.
"""

import logging
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import psutil


class PerformanceMonitor:
    """Performance monitoring and benchmarking system"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = self._setup_logging()
        
        # Monitoring configuration
        self.config = {
            "monitoring_interval": 1.0,  # seconds
            "max_monitoring_duration": 300,  # 5 minutes
            "memory_threshold_mb": 1024,
            "cpu_threshold_percent": 80,
            "disk_threshold_percent": 90
        }
        
        # Performance data storage
        self.performance_data = {}
        self.monitoring_sessions = {}
        self.active_monitors = {}
        
        self.logger.info("📊 Performance Monitor initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.Verification.PerformanceMonitor")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _get_deterministic_time(self) -> float:
        """Return deterministic time for testing"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC
    
    def start_performance_monitoring(self, session_name: str, duration: Optional[int] = None) -> Dict[str, Any]:
        """Start performance monitoring session"""
        try:
            if session_name in self.active_monitors:
                return {
                    "success": False,
                    "error": f"Monitoring session already active: {session_name}"
                }
            
            session_id = f"session_{session_name}_{int(self._get_deterministic_time())}"
            monitoring_duration = duration or self.config["max_monitoring_duration"]
            
            session_info = {
                "session_id": session_id,
                "session_name": session_name,
                "start_time": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "duration_seconds": monitoring_duration,
                "status": "active",
                "data_points": []
            }
            
            # Start monitoring thread
            monitor_thread = threading.Thread(
                target=self._monitor_performance,
                args=(session_id, session_info, monitoring_duration),
                daemon=True
            )
            monitor_thread.start()
            
            self.active_monitors[session_name] = {
                "session_id": session_id,
                "thread": monitor_thread,
                "session_info": session_info
            }
            
            self.logger.info(f"📊 Performance monitoring started: {session_name}")
            
            return {
                "success": True,
                "session_id": session_id,
                "session_name": session_name,
                "monitoring_duration": monitoring_duration
            }
            
        except Exception as e:
            self.logger.error(f"Performance monitoring start error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def stop_performance_monitoring(self, session_name: str) -> Dict[str, Any]:
        """Stop performance monitoring session"""
        try:
            if session_name not in self.active_monitors:
                return {
                    "success": False,
                    "error": f"No active monitoring session: {session_name}"
                }
            
            monitor_info = self.active_monitors[session_name]
            session_info = monitor_info["session_info"]
            
            # Mark session as stopped
            session_info["status"] = "stopped"
            session_info["end_time"] = deterministic_helpers.get_deterministic_timestamp().isoformat()
            
            # Store session data
            session_id = session_info["session_id"]
            self.monitoring_sessions[session_id] = session_info
            
            # Remove from active monitors
            del self.active_monitors[session_name]
            
            self.logger.info(f"📊 Performance monitoring stopped: {session_name}")
            
            return {
                "success": True,
                "session_id": session_id,
                "session_name": session_name,
                "data_points_collected": len(session_info["data_points"])
            }
            
        except Exception as e:
            self.logger.error(f"Performance monitoring stop error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _monitor_performance(self, session_id: str, session_info: Dict[str, Any], duration: int):
        """Monitor performance in background thread"""
        try:
            start_time = deterministic_helpers.get_deterministic_epoch()
            interval = self.config["monitoring_interval"]
            
            while (deterministic_helpers.get_deterministic_epoch() - start_time) < duration and session_info["status"] == "active":
                # Collect performance data
                data_point = self._collect_performance_data()
                data_point["timestamp"] = deterministic_helpers.get_deterministic_timestamp().isoformat()
                data_point["elapsed_seconds"] = deterministic_helpers.get_deterministic_epoch() - start_time
                
                session_info["data_points"].append(data_point)
                
                # Check thresholds
                self._check_performance_thresholds(data_point, session_info)
                
                time.sleep(interval)
            
            # Mark session as completed
            if session_info["status"] == "active":
                session_info["status"] = "completed"
                session_info["end_time"] = deterministic_helpers.get_deterministic_timestamp().isoformat()
            
        except Exception as e:
            self.logger.error(f"Performance monitoring thread error: {e}")
            session_info["status"] = "error"
            session_info["error"] = str(e)
    
    def _collect_performance_data(self) -> Dict[str, Any]:
        """Collect current performance data"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            
            # Disk usage
            disk = psutil.disk_usage(str(self.project_root))
            disk_percent = (disk.used / disk.total) * 100
            
            # Process information
            process = psutil.Process()
            process_memory_mb = process.memory_info().rss / (1024 * 1024)
            process_cpu_percent = process.cpu_percent()
            
            return {
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "memory_used_mb": round(memory_used_mb, 2),
                    "disk_percent": round(disk_percent, 2)
                },
                "process": {
                    "memory_mb": round(process_memory_mb, 2),
                    "cpu_percent": process_cpu_percent
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat()
            }
    
    def _check_performance_thresholds(self, data_point: Dict[str, Any], session_info: Dict[str, Any]):
        """Check performance thresholds and log warnings"""
        try:
            system_data = data_point.get("system", {})
            process_data = data_point.get("process", {})
            
            # Check CPU threshold
            cpu_percent = system_data.get("cpu_percent", 0)
            if cpu_percent > self.config["cpu_threshold_percent"]:
                self.logger.warning(f"📊 High CPU usage: {cpu_percent}%")
            
            # Check memory threshold
            memory_mb = process_data.get("memory_mb", 0)
            if memory_mb > self.config["memory_threshold_mb"]:
                self.logger.warning(f"📊 High memory usage: {memory_mb}MB")
            
            # Check disk threshold
            disk_percent = system_data.get("disk_percent", 0)
            if disk_percent > self.config["disk_threshold_percent"]:
                self.logger.warning(f"📊 High disk usage: {disk_percent}%")
                
        except Exception as e:
            self.logger.error(f"Performance threshold check error: {e}")
    
    def run_performance_benchmark(self, benchmark_name: str) -> Dict[str, Any]:
        """Run performance benchmark"""
        try:
            self.logger.info(f"📊 Running performance benchmark: {benchmark_name}")
            
            benchmark_id = f"benchmark_{benchmark_name}_{int(self._get_deterministic_time())}"
            
            benchmark_result = {
                "benchmark_id": benchmark_id,
                "benchmark_name": benchmark_name,
                "start_time": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "benchmark_tests": [],
                "overall_score": 0
            }
            
            # Benchmark 1: CPU performance
            cpu_benchmark = self._benchmark_cpu_performance()
            benchmark_result["benchmark_tests"].append({
                "test": "cpu_performance",
                "result": cpu_benchmark,
                "score": cpu_benchmark.get("score", 0)
            })
            
            # Benchmark 2: Memory performance
            memory_benchmark = self._benchmark_memory_performance()
            benchmark_result["benchmark_tests"].append({
                "test": "memory_performance",
                "result": memory_benchmark,
                "score": memory_benchmark.get("score", 0)
            })
            
            # Benchmark 3: Disk I/O performance
            disk_benchmark = self._benchmark_disk_performance()
            benchmark_result["benchmark_tests"].append({
                "test": "disk_performance",
                "result": disk_benchmark,
                "score": disk_benchmark.get("score", 0)
            })
            
            # Benchmark 4: Network performance
            network_benchmark = self._benchmark_network_performance()
            benchmark_result["benchmark_tests"].append({
                "test": "network_performance",
                "result": network_benchmark,
                "score": network_benchmark.get("score", 0)
            })
            
            # Calculate overall score
            scores = [test["score"] for test in benchmark_result["benchmark_tests"]]
            benchmark_result["overall_score"] = sum(scores) / len(scores) if scores else 0
            
            benchmark_result["end_time"] = deterministic_helpers.get_deterministic_timestamp().isoformat()
            
            # Store benchmark results
            self.performance_data[benchmark_id] = benchmark_result
            
            self.logger.info(f"📊 Performance benchmark completed: {benchmark_name}")
            
            return benchmark_result
            
        except Exception as e:
            self.logger.error(f"Performance benchmark error: {e}")
            return {
                "success": False,
                "error": str(e),
                "benchmark_name": benchmark_name
            }
    
    def _benchmark_cpu_performance(self) -> Dict[str, Any]:
        """Benchmark CPU performance"""
        try:
            start_time = deterministic_helpers.get_deterministic_epoch()
            
            # CPU-intensive calculation
            result = 0
            for i in range(1000000):
                result += i * i
            
            execution_time = deterministic_helpers.get_deterministic_epoch() - start_time
            
            # Score based on execution time (lower is better)
            score = max(0, 100 - (execution_time * 10))
            
            return {
                "execution_time_seconds": execution_time,
                "operations_per_second": 1000000 / execution_time,
                "score": score,
                "grade": "excellent" if score > 80 else "good" if score > 60 else "fair" if score > 40 else "poor"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "score": 0
            }
    
    def _benchmark_memory_performance(self) -> Dict[str, Any]:
        """Benchmark memory performance"""
        try:
            start_time = deterministic_helpers.get_deterministic_epoch()
            
            # Memory allocation and access test
            data_size = 10 * 1024 * 1024  # 10MB
            test_data = bytearray(data_size)
            
            # Write test
            for i in range(0, data_size, 1024):
                test_data[i] = i % 256
            
            # Read test
            checksum = 0
            for i in range(0, data_size, 1024):
                checksum += test_data[i]
            
            execution_time = deterministic_helpers.get_deterministic_epoch() - start_time
            
            # Score based on execution time and data size
            throughput_mb_s = (data_size / (1024 * 1024)) / execution_time
            score = min(100, throughput_mb_s * 2)  # Scale to 0-100
            
            return {
                "execution_time_seconds": execution_time,
                "data_size_mb": data_size / (1024 * 1024),
                "throughput_mb_s": throughput_mb_s,
                "score": score,
                "grade": "excellent" if score > 80 else "good" if score > 60 else "fair" if score > 40 else "poor"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "score": 0
            }
    
    def _benchmark_disk_performance(self) -> Dict[str, Any]:
        """Benchmark disk I/O performance"""
        try:
            test_file = self.project_root / "performance_test.tmp"
            test_data = b"x" * (1024 * 1024)  # 1MB of data
            
            start_time = deterministic_helpers.get_deterministic_epoch()
            
            # Write test
            with open(test_file, 'wb') as f:
                for _ in range(10):  # Write 10MB total
                    f.write(test_data)
            
            # Read test
            with open(test_file, 'rb') as f:
                while f.read(1024 * 1024):
                    pass
            
            execution_time = time.time() - start_time
            
            # Cleanup
            test_file.unlink()
            
            # Score based on execution time
            throughput_mb_s = 20 / execution_time  # 20MB total (10MB write + 10MB read)
            score = min(100, throughput_mb_s * 5)  # Scale to 0-100
            
            return {
                "execution_time_seconds": execution_time,
                "data_size_mb": 20,
                "throughput_mb_s": throughput_mb_s,
                "score": score,
                "grade": "excellent" if score > 80 else "good" if score > 60 else "fair" if score > 40 else "poor"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "score": 0
            }
    
    def _benchmark_network_performance(self) -> Dict[str, Any]:
        """Benchmark network performance"""
        try:
            start_time = deterministic_helpers.get_deterministic_epoch()
            
            # Simple network test - DNS resolution
            import socket
            test_hosts = ["google.com", "github.com", "python.org"]
            successful_resolutions = 0
            
            for host in test_hosts:
                try:
                    socket.gethostbyname(host)
                    successful_resolutions += 1
                except Exception as e:
                    self.logger.debug(f"DNS resolution failed for {host}: {e}")
                    
            execution_time = deterministic_helpers.get_deterministic_epoch() - start_time
            
            # Score based on success rate and speed
            success_rate = successful_resolutions / len(test_hosts)
            speed_score = max(0, 100 - (execution_time * 20))
            score = (success_rate * 50) + (speed_score * 0.5)
            
            return {
                "execution_time_seconds": execution_time,
                "successful_resolutions": successful_resolutions,
                "total_hosts": len(test_hosts),
                "success_rate": success_rate,
                "score": score,
                "grade": "excellent" if score > 80 else "good" if score > 60 else "fair" if score > 40 else "poor"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "score": 0
            }
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get performance monitoring status"""
        return {
            "active_monitors": len(self.active_monitors),
            "completed_sessions": len(self.monitoring_sessions),
            "benchmark_results": len(self.performance_data),
            "config": self.config
        }
    
    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get monitoring session data"""
        return self.monitoring_sessions.get(session_id)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate performance monitoring report"""
        try:
            status = self.get_monitoring_status()
            
            return {
                "report_type": "performance_monitoring",
                "timestamp": deterministic_helpers.get_deterministic_timestamp().isoformat(),
                "statistics": status,
                "recent_benchmarks": list(self.performance_data.values())[-5:],  # Last 5
                "active_sessions": list(self.active_monitors.keys()),
                "recommendations": self.get_recommendations()
            }
            
        except Exception as e:
            self.logger.error(f"Performance monitoring report generation error: {e}")
            return {
                "error": str(e)
            }
    
    def get_recommendations(self) -> List[str]:
        """Get performance monitoring recommendations"""
        recommendations = []
        
        status = self.get_monitoring_status()
        
        if status["benchmark_results"] == 0:
            recommendations.append("Run initial performance benchmarks")
        
        if status["active_monitors"] == 0:
            recommendations.append("Start performance monitoring for critical operations")
        
        recommendations.extend([
            "Regular performance benchmarking",
            "Monitor resource usage during peak loads",
            "Set up automated performance alerts",
            "Optimize based on performance data"
        ])
        
        return recommendations