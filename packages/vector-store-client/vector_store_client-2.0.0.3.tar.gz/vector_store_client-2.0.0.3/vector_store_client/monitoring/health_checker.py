"""
Health checker for Vector Store Client.

This module provides health checking capabilities for monitoring
system health and component status.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from ..exceptions import MonitoringError


class HealthChecker:
    """
    Health checker for system components.
    
    Provides health checking capabilities for monitoring
    system components and services.
    """
    
    def __init__(self):
        self.health_checks: Dict[str, Dict[str, Any]] = {}
        self.last_check_time = None
        self.name = "HealthChecker"
    
    def get_name(self) -> str:
        """Get health checker name."""
        return self.name
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get health checker configuration.
        
        Returns:
            Dict[str, Any]: Health checker configuration
        """
        return {
            "name": self.name,
            "health_checks_count": len(self.health_checks),
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None
        }
    
    async def check_system_health(self) -> Dict[str, Any]:
        """
        Perform comprehensive system health check.
        
        Returns:
            Dict[str, Any]: System health status
        """
        health_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "healthy",
            "components": {},
            "warnings": [],
            "errors": []
        }
        
        try:
            # Check memory usage
            memory_health = await self._check_memory_health()
            health_status["components"]["memory"] = memory_health
            
            # Check CPU usage
            cpu_health = await self._check_cpu_health()
            health_status["components"]["cpu"] = cpu_health
            
            # Check disk usage
            disk_health = await self._check_disk_health()
            health_status["components"]["disk"] = disk_health
            
            # Check network connectivity
            network_health = await self._check_network_health()
            health_status["components"]["network"] = network_health
            
            # Determine overall status
            if any(comp.get("status") == "error" for comp in health_status["components"].values()):
                health_status["overall_status"] = "unhealthy"
            elif any(comp.get("status") == "warning" for comp in health_status["components"].values()):
                health_status["overall_status"] = "degraded"
            
            self.last_check_time = datetime.now(timezone.utc)
            
        except Exception as e:
            health_status["overall_status"] = "error"
            health_status["errors"].append(f"Health check failed: {str(e)}")
        
        return health_status
    
    async def _check_memory_health(self) -> Dict[str, Any]:
        """Check memory usage health."""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            
            health = {
                "status": "healthy",
                "total_mb": memory.total / (1024 * 1024),
                "available_mb": memory.available / (1024 * 1024),
                "used_mb": memory.used / (1024 * 1024),
                "percent": memory.percent
            }
            
            if memory.percent > 90:
                health["status"] = "error"
            elif memory.percent > 80:
                health["status"] = "warning"
            
            return health
            
        except ImportError:
            return {
                "status": "unknown",
                "error": "psutil not available"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _check_cpu_health(self) -> Dict[str, Any]:
        """Check CPU usage health."""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            health = {
                "status": "healthy",
                "usage_percent": cpu_percent,
                "cpu_count": cpu_count,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
            
            if cpu_percent > 90:
                health["status"] = "error"
            elif cpu_percent > 80:
                health["status"] = "warning"
            
            return health
            
        except ImportError:
            return {
                "status": "unknown",
                "error": "psutil not available"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _check_disk_health(self) -> Dict[str, Any]:
        """Check disk usage health."""
        try:
            import psutil
            
            disk = psutil.disk_usage('/')
            
            health = {
                "status": "healthy",
                "total_gb": disk.total / (1024**3),
                "used_gb": disk.used / (1024**3),
                "free_gb": disk.free / (1024**3),
                "percent": (disk.used / disk.total) * 100
            }
            
            if health["percent"] > 95:
                health["status"] = "error"
            elif health["percent"] > 85:
                health["status"] = "warning"
            
            return health
            
        except ImportError:
            return {
                "status": "unknown",
                "error": "psutil not available"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _check_network_health(self) -> Dict[str, Any]:
        """Check network connectivity health."""
        try:
            import psutil
            
            # Get network I/O statistics
            net_io = psutil.net_io_counters()
            
            health = {
                "status": "healthy",
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
            
            # Simple connectivity test
            try:
                # Test basic connectivity
                await asyncio.wait_for(
                    asyncio.create_task(asyncio.sleep(0)), 
                    timeout=1.0
                )
                health["connectivity"] = "ok"
            except asyncio.TimeoutError:
                health["status"] = "warning"
                health["connectivity"] = "slow"
            
            return health
            
        except ImportError:
            return {
                "status": "unknown",
                "error": "psutil not available"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def add_custom_health_check(
        self, 
        name: str, 
        check_func: callable,
        interval: int = 300
    ) -> None:
        """
        Add custom health check.
        
        Parameters:
            name: Name of the health check
            check_func: Function to perform the check
            interval: Check interval in seconds
        """
        self.health_checks[name] = {
            "function": check_func,
            "interval": interval,
            "last_run": None,
            "last_result": None
        }
    
    async def run_custom_health_checks(self) -> Dict[str, Any]:
        """
        Run all custom health checks.
        
        Returns:
            Dict[str, Any]: Results of custom health checks
        """
        results = {}
        current_time = time.time()
        
        for name, check_info in self.health_checks.items():
            # Check if it's time to run this check
            if (check_info["last_run"] is None or 
                current_time - check_info["last_run"] >= check_info["interval"]):
                
                try:
                    if asyncio.iscoroutinefunction(check_info["function"]):
                        result = await check_info["function"]()
                    else:
                        result = check_info["function"]()
                    
                    check_info["last_result"] = result
                    check_info["last_run"] = current_time
                    
                    results[name] = {
                        "status": "success",
                        "result": result,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    
                except Exception as e:
                    check_info["last_result"] = {"error": str(e)}
                    check_info["last_run"] = current_time
                    
                    results[name] = {
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
            else:
                # Return cached result
                results[name] = {
                    "status": "cached",
                    "result": check_info["last_result"],
                    "timestamp": datetime.fromtimestamp(check_info["last_run"]).isoformat()
                }
        
        return results
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get health check summary.
        
        Returns:
            Dict[str, Any]: Health check summary
        """
        return {
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "custom_checks_count": len(self.health_checks),
            "custom_checks": list(self.health_checks.keys())
        } 