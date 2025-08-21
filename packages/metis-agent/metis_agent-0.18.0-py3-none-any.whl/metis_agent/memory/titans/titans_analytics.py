"""
Titans Memory Analytics System

This module provides advanced analytics and monitoring capabilities
for the Titans memory system in production environments.
"""

import time
import numpy as np
import hashlib
import threading
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field


class TitansAnalytics:
    """Advanced analytics for Titans memory system"""
    
    def __init__(self):
        """Initialize the analytics system"""
        self.historical_data = []
        self.max_history_entries = 100
        self.last_analysis_time = time.time()
    
    def generate_memory_report(self, agent) -> Dict[str, Any]:
        """
        Generate comprehensive memory analysis
        
        Args:
            agent: Agent instance with Titans memory
            
        Returns:
            Dict with memory analysis
        """
        if not hasattr(agent, 'titans_memory_enabled') or not agent.titans_memory_enabled or not hasattr(agent, 'titans_adapter') or not agent.titans_adapter:
            return {"status": "disabled"}
            
        insights = agent.get_memory_insights()
        
        # Extract relevant metrics
        if not insights.get("adaptive_memory", {}).get("insights"):
            return {"status": "no_insights_available"}
            
        memory_insights = insights["adaptive_memory"]["insights"]
        performance_metrics = memory_insights.get("performance_metrics", {})
        health_indicators = memory_insights.get("health_indicators", {})
        
        # Calculate advanced metrics
        report = {
            "learning_velocity": self._calculate_learning_velocity(performance_metrics, health_indicators),
            "context_relevance": self._analyze_context_quality(agent),
            "surprise_distribution": self._analyze_surprise_patterns(performance_metrics, health_indicators),
            "memory_efficiency": self._calculate_memory_efficiency(health_indicators),
            "recommendations": self._generate_tuning_recommendations(performance_metrics, health_indicators)
        }
        
        # Store historical data point
        self._add_historical_data_point(performance_metrics, health_indicators)
        
        return report
    
    def _add_historical_data_point(self, metrics: Dict, health: Dict):
        """Add historical data point for trend analysis"""
        data_point = {
            "timestamp": time.time(),
            "metrics": metrics.copy(),
            "health": health.copy()
        }
        
        self.historical_data.append(data_point)
        
        # Maintain size limit
        if len(self.historical_data) > self.max_history_entries:
            self.historical_data = self.historical_data[-self.max_history_entries:]
    
    def _calculate_learning_velocity(self, metrics: Dict, health: Dict) -> Dict[str, Any]:
        """
        Measure how fast the system is learning
        
        Args:
            metrics: Performance metrics
            health: Health indicators
            
        Returns:
            Dict with learning velocity metrics
        """
        adaptations = metrics.get("adaptations_triggered", 0)
        queries = max(1, metrics.get("queries_processed", 1))  # Avoid division by zero
        first_update = metrics.get("first_update_time", time.time())
        last_update = metrics.get("last_update_time", time.time())
        
        # Calculate time span in hours (default to 1 hour if no updates yet)
        time_span_hours = max(1, (last_update - first_update) / 3600)
        
        # Calculate adaptations per hour and per query
        adaptations_per_hour = adaptations / time_span_hours
        adaptations_per_query = adaptations / queries
        
        # Determine learning trend
        if len(self.historical_data) >= 2:
            previous = self.historical_data[-2]["metrics"].get("adaptations_triggered", 0)
            current = adaptations
            
            if current > previous * 1.2:  # 20% increase
                trend = "accelerating"
            elif current < previous * 0.8:  # 20% decrease
                trend = "decelerating"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "adaptations_per_hour": adaptations_per_hour,
            "adaptations_per_query": adaptations_per_query,
            "learning_trend": trend,
            "learning_active": health.get("learning_active", False)
        }
    
    def _analyze_context_quality(self, agent) -> Dict[str, Any]:
        """
        Analyze the quality of context provided by memories
        
        Args:
            agent: Agent instance
            
        Returns:
            Dict with context quality metrics
        """
        # This is a placeholder that would typically analyze real query results
        # In a real implementation, you would track which memories were used
        # and whether they influenced the response
        
        return {
            "estimated_relevance": 0.8,  # Placeholder
            "context_usage_rate": 0.7,   # Placeholder
            "enhancement_quality": "good"
        }
    
    def _analyze_surprise_patterns(self, metrics: Dict, health: Dict) -> Dict[str, Any]:
        """
        Analyze what content is surprising the system
        
        Args:
            metrics: Performance metrics
            health: Health indicators
            
        Returns:
            Dict with surprise pattern analysis
        """
        avg_surprise = metrics.get("average_surprise", 0)
        threshold = health.get("surprise_threshold", 0.7)
        
        # Determine surprise level
        if avg_surprise > threshold * 1.5:
            surprise_level = "very_high"
        elif avg_surprise > threshold:
            surprise_level = "high"
        elif avg_surprise > threshold * 0.5:
            surprise_level = "moderate"
        else:
            surprise_level = "low"
        
        # Calculate learning efficiency
        learning_efficiency = avg_surprise / threshold if threshold > 0 else 0
        
        # Determine pattern
        if avg_surprise > threshold:
            pattern = "novelty_seeking"
        else:
            pattern = "familiar_content"
        
        return {
            "surprise_level": surprise_level,
            "learning_efficiency": learning_efficiency,
            "pattern": pattern,
            "average_surprise": avg_surprise,
            "threshold": threshold,
            "ratio": avg_surprise / threshold if threshold > 0 else 0
        }
    
    def _calculate_memory_efficiency(self, health: Dict) -> float:
        """
        Calculate memory utilization efficiency
        
        Args:
            health: Health indicators
            
        Returns:
            Efficiency score (0-1)
        """
        utilization = health.get("memory_utilization", 0)
        
        # Optimal range is 0.3-0.8
        if 0.3 <= utilization <= 0.8:
            # Scale to 0.8-1.0 for optimal range
            return 0.8 + (utilization - 0.3) * 0.4 / 0.5
        elif utilization < 0.3:
            # Scale to 0-0.8 for under-utilization
            return utilization * 0.8 / 0.3
        else:
            # Scale down from 0.8 for over-utilization
            return max(0, 0.8 - (utilization - 0.8) * 0.8 / 0.2)
    
    def _generate_tuning_recommendations(self, metrics: Dict, health: Dict) -> List[str]:
        """
        Generate tuning recommendations based on metrics
        
        Args:
            metrics: Performance metrics
            health: Health indicators
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check learning status
        if not health.get("learning_active", False):
            recommendations.append("Lower surprise_threshold to enable more learning")
        
        # Check memory utilization
        utilization = health.get("memory_utilization", 0)
        if utilization < 0.2:
            recommendations.append("Lower surprise_threshold or increase interaction frequency for better memory utilization")
        elif utilization > 0.9:
            recommendations.append("Increase short_term_capacity or implement memory cleanup")
        
        # Check adaptation rate
        adaptations = metrics.get("adaptations_triggered", 0)
        queries = max(1, metrics.get("queries_processed", 1))
        adaptation_rate = adaptations / queries
        
        if adaptation_rate < 0.05 and queries > 10:
            recommendations.append("Reduce chunk_size to trigger more frequent updates")
        elif adaptation_rate > 0.3:
            recommendations.append("Increase chunk_size to reduce update frequency")
        
        # Check surprise level
        avg_surprise = metrics.get("average_surprise", 0)
        if avg_surprise > 1.5:
            recommendations.append("Increase surprise_threshold - content may be too varied or noisy")
        elif avg_surprise < 0.3 and queries > 10:
            recommendations.append("Decrease surprise_threshold to improve novelty detection")
        
        return recommendations
    
    def analyze_trends(self) -> Dict[str, Any]:
        """
        Analyze trends over time using historical data
        
        Returns:
            Dict with trend analysis
        """
        if len(self.historical_data) < 2:
            return {"status": "insufficient_data"}
        
        # Get earliest and latest data points
        earliest = self.historical_data[0]
        latest = self.historical_data[-1]
        
        # Calculate time span
        time_span_hours = (latest["timestamp"] - earliest["timestamp"]) / 3600
        
        # Calculate change in key metrics
        metric_changes = {}
        for metric in ["queries_processed", "memories_stored", "adaptations_triggered", "average_surprise"]:
            if metric in earliest["metrics"] and metric in latest["metrics"]:
                start_value = earliest["metrics"].get(metric, 0)
                end_value = latest["metrics"].get(metric, 0)
                
                if start_value > 0:
                    percent_change = (end_value - start_value) / start_value * 100
                else:
                    percent_change = 0 if end_value == 0 else 100
                
                metric_changes[metric] = {
                    "start_value": start_value,
                    "end_value": end_value, 
                    "absolute_change": end_value - start_value,
                    "percent_change": percent_change
                }
        
        # Calculate change in health indicators
        health_changes = {}
        for indicator in ["memory_utilization", "learning_active"]:
            if indicator in earliest["health"] and indicator in latest["health"]:
                start_value = earliest["health"].get(indicator, 0)
                end_value = latest["health"].get(indicator, 0)
                
                if isinstance(start_value, bool):
                    change = "unchanged" if start_value == end_value else "changed"
                    health_changes[indicator] = {"start": start_value, "end": end_value, "change": change}
                elif start_value > 0:
                    percent_change = (end_value - start_value) / start_value * 100
                    health_changes[indicator] = {
                        "start_value": start_value,
                        "end_value": end_value,
                        "absolute_change": end_value - start_value,
                        "percent_change": percent_change
                    }
                else:
                    health_changes[indicator] = {
                        "start_value": start_value,
                        "end_value": end_value,
                        "absolute_change": end_value - start_value,
                        "percent_change": 0 if end_value == 0 else 100
                    }
        
        # Overall assessment
        overall_status = "improving"
        if "memory_utilization" in health_changes:
            util_change = health_changes["memory_utilization"].get("absolute_change", 0)
            if util_change > 0.2:
                overall_status = "rapidly_filling"
            elif util_change < -0.2:
                overall_status = "rapidly_emptying"
        
        # Determine if learning is becoming more or less active
        learning_trend = "stable"
        if "adaptations_triggered" in metric_changes:
            adapt_change = metric_changes["adaptations_triggered"].get("percent_change", 0)
            if adapt_change > 20:
                learning_trend = "more_active"
            elif adapt_change < -20:
                learning_trend = "less_active"
        
        return {
            "status": "success",
            "time_span_hours": time_span_hours,
            "data_points": len(self.historical_data),
            "metric_changes": metric_changes,
            "health_changes": health_changes,
            "overall_status": overall_status,
            "learning_trend": learning_trend
        }


class MemoryMonitor:
    """Monitor for Titans memory health and performance"""
    
    def __init__(self, agent, config=None):
        """
        Initialize the memory monitor
        
        Args:
            agent: Agent instance
            config: Monitoring configuration
        """
        self.agent = agent
        self.config = config or {}
        self.analytics = TitansAnalytics()
        self.running = False
        self.monitor_thread = None
        self.last_check_time = time.time()
        self.alert_history = []
    
    def start_monitoring(self, interval_seconds=600):
        """
        Start monitoring thread
        
        Args:
            interval_seconds: Monitoring interval in seconds
        """
        if self.running:
            print("⚠️ Monitoring already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, 
            args=(interval_seconds,),
            daemon=True
        )
        self.monitor_thread.start()
        print(f"+ Memory monitoring started (interval: {interval_seconds}s)")
    
    def stop_monitoring(self):
        """Stop monitoring thread"""
        self.running = False
        if self.monitor_thread:
            # Thread will terminate on next interval since it's a daemon
            print("+ Memory monitoring stopped")
    
    def _monitoring_loop(self, interval_seconds):
        """
        Main monitoring loop
        
        Args:
            interval_seconds: Check interval in seconds
        """
        while self.running:
            try:
                # Check memory health
                self._check_memory_health()
                
                # Analyze trends periodically (every 6 hours)
                hours_since_analysis = (time.time() - self.last_check_time) / 3600
                if hours_since_analysis >= 6:
                    self._analyze_trends()
                    self.last_check_time = time.time()
                
            except Exception as e:
                print(f"⚠️ Error in memory monitoring: {e}")
            
            # Sleep until next check
            for _ in range(int(interval_seconds / 10)):
                if not self.running:
                    break
                time.sleep(10)
    
    def _check_memory_health(self):
        """Check memory health and generate alerts if needed"""
        if not hasattr(self.agent, 'titans_memory_enabled') or not self.agent.titans_memory_enabled or not hasattr(self.agent, 'titans_adapter') or not self.agent.titans_adapter:
            return
        
        try:
            insights = self.agent.get_memory_insights()
            if not insights.get("adaptive_memory", {}).get("insights"):
                return
            
            health = insights["adaptive_memory"]["insights"]["health_indicators"]
            metrics = insights["adaptive_memory"]["insights"]["performance_metrics"]
            
            # Check for critical conditions
            alerts = []
            
            # Check memory utilization
            if health.get("memory_utilization", 0) > 0.95:
                alerts.append({
                    "type": "critical",
                    "message": "Memory utilization critical",
                    "details": f"Utilization: {health['memory_utilization']:.1%}"
                })
            elif health.get("memory_utilization", 0) > 0.85:
                alerts.append({
                    "type": "warning",
                    "message": "Memory utilization high",
                    "details": f"Utilization: {health['memory_utilization']:.1%}"
                })
            
            # Check learning status
            if not health.get("learning_active", True) and metrics.get("queries_processed", 0) > 10:
                alerts.append({
                    "type": "warning",
                    "message": "Adaptive learning inactive",
                    "details": "System is not learning from new interactions"
                })
            
            # Send alerts
            for alert in alerts:
                self._send_alert(alert["type"], alert["message"], alert["details"])
        
        except Exception as e:
            print(f"⚠️ Error checking memory health: {e}")
    
    def _analyze_trends(self):
        """Analyze memory performance trends"""
        try:
            trends = self.analytics.analyze_trends()
            if trends.get("status") == "insufficient_data":
                return
            
            # Log trend analysis
            print("\n+ Memory Trend Analysis:")
            print(f"  Time span: {trends['time_span_hours']:.1f} hours")
            print(f"  Overall status: {trends['overall_status']}")
            print(f"  Learning trend: {trends['learning_trend']}")
            
            # Check for concerning trends
            if trends["overall_status"] == "rapidly_filling":
                self._send_alert(
                    "warning",
                    "Memory filling rapidly",
                    f"Utilization increased by {trends['health_changes']['memory_utilization']['absolute_change']:.1%} over {trends['time_span_hours']:.1f} hours"
                )
            
            if trends["learning_trend"] == "less_active" and trends["time_span_hours"] > 12:
                self._send_alert(
                    "info",
                    "Learning activity decreasing",
                    f"Adaptations decreased by {abs(trends['metric_changes']['adaptations_triggered']['percent_change']):.1f}% over {trends['time_span_hours']:.1f} hours"
                )
        
        except Exception as e:
            print(f"⚠️ Error analyzing trends: {e}")
    
    def _send_alert(self, alert_type, message, details=None):
        """
        Send monitoring alert
        
        Args:
            alert_type: Alert type (info, warning, critical)
            message: Alert message
            details: Alert details
        """
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        icons = {
            "info": "INFO",
            "warning": "WARN",
            "critical": "CRITICAL"
        }
        
        icon = icons.get(alert_type, "WARN")
        alert_msg = f"{icon} {alert_type.upper()} [{timestamp}] {message}"
        if details:
            alert_msg += f": {details}"
        
        print(alert_msg)
        
        # Store in alert history
        self.alert_history.append({
            "type": alert_type,
            "message": message,
            "details": details,
            "timestamp": timestamp
        })
        
        # Limit history size
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]
    
    def get_alert_history(self, alert_type=None, limit=10):
        """
        Get alert history
        
        Args:
            alert_type: Filter by alert type
            limit: Maximum number of alerts to return
            
        Returns:
            List of alerts
        """
        if alert_type:
            filtered = [a for a in self.alert_history if a["type"] == alert_type]
            return filtered[-limit:]
        else:
            return self.alert_history[-limit:]
    
    def generate_health_report(self):
        """
        Generate comprehensive health report
        
        Returns:
            Dict with health report
        """
        if not hasattr(self.agent, 'titans_memory_enabled') or not self.agent.titans_memory_enabled or not hasattr(self.agent, 'titans_adapter') or not self.agent.titans_adapter:
            return {"status": "disabled"}
        
        try:
            # Get basic insights
            insights = self.agent.get_memory_insights()
            if not insights.get("adaptive_memory", {}).get("insights"):
                return {"status": "no_insights_available"}
            
            # Generate comprehensive report
            memory_report = self.analytics.generate_memory_report(self.agent)
            
            # Add alert statistics
            alert_stats = {}
            for alert_type in ["info", "warning", "critical"]:
                alert_stats[alert_type] = len([a for a in self.alert_history if a["type"] == alert_type])
            
            # Add trend analysis if available
            trend_analysis = self.analytics.analyze_trends()
            if trend_analysis.get("status") != "insufficient_data":
                memory_report["trends"] = trend_analysis
            
            # Add health summary
            memory_report["health_summary"] = self._generate_health_summary(insights, memory_report)
            memory_report["alert_stats"] = alert_stats
            
            return memory_report
        
        except Exception as e:
            print(f"⚠️ Error generating health report: {e}")
            return {"status": "error", "error": str(e)}
    
    def _generate_health_summary(self, insights, memory_report):
        """Generate health summary from insights and report"""
        health = insights["adaptive_memory"]["insights"]["health_indicators"]
        
        # Determine overall health status
        if health.get("memory_utilization", 0) > 0.95:
            status = "critical"
            message = "Memory utilization critical"
        elif health.get("memory_utilization", 0) > 0.85:
            status = "warning"
            message = "Memory utilization high"
        elif not health.get("learning_active", True):
            status = "warning"
            message = "Adaptive learning inactive"
        elif memory_report["memory_efficiency"] < 0.5:
            status = "warning"
            message = "Low memory efficiency"
        else:
            status = "healthy"
            message = "Memory system healthy"
        
        return {
            "status": status,
            "message": message,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "efficiency": memory_report["memory_efficiency"],
            "learning_active": health.get("learning_active", False),
            "memory_utilization": health.get("memory_utilization", 0)
        }