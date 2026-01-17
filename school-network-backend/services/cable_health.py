"""
Cable health monitoring and analysis service.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models.link import Link
from models.cable_health import CableHealthMetrics, CableHealthStatusEnum, CableTypeEnum
from schemas.cable_health import CableHealthCreate, CableHealthUpdate
from services.base import BaseService
from icmplib import ping, async_ping
import asyncio
import logging

logger = logging.getLogger(__name__)


class CableHealthAnalyzer:
    """
    Monitor and analyze network cable health.
    Measures: latency, packet loss, jitter, error rates.
    """

    # Health score thresholds
    HEALTH_THRESHOLDS = {
        "latency_warning_ms": 50.0,
        "latency_critical_ms": 100.0,
        "packet_loss_warning_percent": 2.0,
        "packet_loss_critical_percent": 5.0,
        "jitter_warning_ms": 10.0,
        "jitter_critical_ms": 20.0,
    }

    # Cable type speed capabilities (Mbps)
    CABLE_SPEEDS = {
        CableTypeEnum.CAT5: 100,
        CableTypeEnum.CAT5E: 1000,
        CableTypeEnum.CAT6: 10000,
        CableTypeEnum.CAT6A: 10000,
        CableTypeEnum.CAT7: 10000,
        CableTypeEnum.FIBER_SM: 100000,
        CableTypeEnum.FIBER_MM: 40000,
        CableTypeEnum.COAX: 1000,
        CableTypeEnum.UNKNOWN: 1000,
    }

    async def test_link(self, target_ip: str, count: int = 10) -> Dict:
        """
        Test network link quality via ICMP ping.
        
        Args:
            target_ip: IP address to test
            count: Number of ping packets to send
            
        Returns:
            Dictionary with comprehensive health metrics
        """
        try:
            # Async ICMP test
            host = await async_ping(target_ip, count=count, timeout=2)

            if not host.is_alive:
                return {
                    "target_ip": target_ip,
                    "is_reachable": False,
                    "latency_ms": None,
                    "packet_loss_percent": 100.0,
                    "jitter_ms": None,
                    "health_score": 0.0,
                    "status": CableHealthStatusEnum.CRITICAL,
                    "timestamp": datetime.utcnow(),
                }

            # Calculate jitter (difference between max and min RTT)
            jitter = host.max_rtt - host.min_rtt if host.max_rtt and host.min_rtt else 0.0

            # Calculate health score (0-100)
            health_score = self._calculate_health_score(
                host.avg_rtt,
                host.packet_loss * 100,  # Convert to percentage
                jitter
            )

            # Determine status
            status = self._determine_status(health_score)

            return {
                "target_ip": target_ip,
                "is_reachable": True,
                "latency_min_ms": host.min_rtt,
                "latency_avg_ms": host.avg_rtt,
                "latency_max_ms": host.max_rtt,
                "packet_loss_percent": host.packet_loss * 100,
                "jitter_ms": jitter,
                "health_score": health_score,
                "status": status,
                "packets_sent": count,
                "packets_received": host.packets_received,
                "timestamp": datetime.utcnow(),
            }

        except Exception as e:
            logger.error(f"Link test failed for {target_ip}: {e}")
            return {
                "target_ip": target_ip,
                "is_reachable": False,
                "health_score": 0.0,
                "status": CableHealthStatusEnum.UNKNOWN,
                "error": str(e),
                "timestamp": datetime.utcnow(),
            }

    def _calculate_health_score(
        self,
        latency_ms: float,
        packet_loss_percent: float,
        jitter_ms: float,
    ) -> float:
        """
        Calculate health score 0-100 based on metrics.
        """
        score = 100.0

        # Latency penalty
        if latency_ms > self.HEALTH_THRESHOLDS["latency_critical_ms"]:
            score -= 40
        elif latency_ms > self.HEALTH_THRESHOLDS["latency_warning_ms"]:
            score -= 20

        # Packet loss penalty
        if packet_loss_percent > self.HEALTH_THRESHOLDS["packet_loss_critical_percent"]:
            score -= 40
        elif packet_loss_percent > self.HEALTH_THRESHOLDS["packet_loss_warning_percent"]:
            score -= 20

        # Jitter penalty
        if jitter_ms > self.HEALTH_THRESHOLDS["jitter_critical_ms"]:
            score -= 20
        elif jitter_ms > self.HEALTH_THRESHOLDS["jitter_warning_ms"]:
            score -= 10

        return max(0.0, score)

    def _determine_status(self, health_score: float) -> CableHealthStatusEnum:
        """Determine cable health status from health score."""
        if health_score >= 90:
            return CableHealthStatusEnum.EXCELLENT
        elif health_score >= 80:
            return CableHealthStatusEnum.GOOD
        elif health_score >= 60:
            return CableHealthStatusEnum.FAIR
        elif health_score >= 40:
            return CableHealthStatusEnum.POOR
        else:
            return CableHealthStatusEnum.CRITICAL

    async def validate_cable_type(self, speed_mbps: float, cable_type: CableTypeEnum) -> Dict:
        """
        Validate if actual speed matches cable type capability.
        
        Returns:
            Validation result and recommendations
        """
        expected_speed = self.CABLE_SPEEDS.get(cable_type, 1000)
        utilization = (speed_mbps / expected_speed * 100) if expected_speed else 0

        # Valid if operating at 80% or more of rated speed
        is_valid = speed_mbps >= (expected_speed * 0.8)

        return {
            "cable_type": cable_type,
            "expected_speed_mbps": expected_speed,
            "actual_speed_mbps": speed_mbps,
            "utilization_percent": utilization,
            "is_valid": is_valid,
            "status": "OK" if is_valid else "WARNING",
            "recommendation": (
                f"Cable operating normally at {utilization:.1f}% capacity"
                if is_valid
                else f"Speed below expected ({speed_mbps}/{expected_speed} Mbps). Check cable condition."
            ),
        }

    def _generate_recommendations(
        self,
        test_results: Dict,
        cable_validation: Optional[Dict] = None,
    ) -> List[str]:
        """Generate actionable recommendations based on test results."""
        recommendations = []

        status = test_results.get("status")
        if status == CableHealthStatusEnum.CRITICAL:
            recommendations.append("🔴 CRITICAL: Link is DOWN or severely degraded. Immediate action required.")
        
        packet_loss = test_results.get("packet_loss_percent", 0)
        if packet_loss > 5:
            recommendations.append(f"⚠️  HIGH packet loss ({packet_loss:.1f}%). Check cable connections and quality.")
        elif packet_loss > 1:
            recommendations.append(f"⚠️  Elevated packet loss ({packet_loss:.1f}%). Monitor closely.")

        latency = test_results.get("latency_avg_ms", 0)
        if latency > 100:
            recommendations.append(f"⚠️  HIGH latency ({latency:.1f}ms). Consider shorter cable runs or upgrade.")
        elif latency > 50:
            recommendations.append(f"⚠️  Elevated latency ({latency:.1f}ms). Monitor performance.")

        jitter = test_results.get("jitter_ms", 0)
        if jitter > 20:
            recommendations.append(f"⚠️  HIGH jitter ({jitter:.1f}ms). May impact real-time applications.")

        if cable_validation and not cable_validation.get("is_valid"):
            recommendations.append(
                f"⚠️  Cable not meeting specifications: {cable_validation.get('recommendation')}"
            )

        if not recommendations:
            recommendations.append("✅ Link health is EXCELLENT. No issues detected.")

        return recommendations


class CableHealthService(BaseService[CableHealthMetrics, CableHealthCreate, CableHealthUpdate]):
    """Service for cable health metrics management."""

    def __init__(self, db: AsyncSession):
        super().__init__(CableHealthMetrics, db)
        self.analyzer = CableHealthAnalyzer()

    async def test_link_health(self, link: Link) -> Dict:
        """
        Test health of a specific link.
        
        Args:
            link: Link model instance
            
        Returns:
            Test results dictionary
        """
        # Get target device IP from link
        from models.device import Device
        
        result = await self.db.execute(
            select(Device).where(Device.id == link.target_device_id)
        )
        target_device = result.scalar_one_or_none()
        
        if not target_device or not target_device.ip: # type: ignore
            return {
                "error": "Target device IP not available",
                "status": CableHealthStatusEnum.UNKNOWN
            }

        # Run ping test
        test_results = await self.analyzer.test_link(target_device.ip) # type: ignore

        # Validate cable type if speed is available
        cable_validation = None
        if link.speed_mbps: # type: ignore
            cable_validation = await self.analyzer.validate_cable_type(
                link.speed_mbps, # type: ignore
                link.cable_type if hasattr(link, 'cable_type') else CableTypeEnum.UNKNOWN
            )

        # Generate recommendations
        recommendations = self.analyzer._generate_recommendations(
            test_results,
            cable_validation
        )

        return {
            "link_id": link.id,
            "test_results": test_results,
            "cable_validation": cable_validation,
            "recommendations": recommendations,
            "timestamp": datetime.utcnow(),
        }

    async def create_health_metric(self, link_id: str, test_results: Dict) -> CableHealthMetrics:
        """
        Create new health metric record from test results.
        
        Args:
            link_id: Link ID
            test_results: Test results dictionary
            
        Returns:
            Created CableHealthMetrics instance
        """
        metric_data = CableHealthCreate(
            link_id=link_id,
            latency_ms=test_results.get("latency_avg_ms"), # type: ignore
            packet_loss_percent=test_results.get("packet_loss_percent"), # type: ignore
            jitter_ms=test_results.get("jitter_ms"), # type: ignore
            signal_quality=int(test_results.get("health_score", 0)),
            status=test_results.get("status", CableHealthStatusEnum.UNKNOWN), # type: ignore
        )
        
        return await self.create(metric_data)

    async def get_link_history(
        self,
        link_id: str,
        hours: int = 24,
        limit: int = 100
    ) -> List[CableHealthMetrics]:
        """
        Get historical health metrics for a link.
        
        Args:
            link_id: Link ID
            hours: Number of hours of history to retrieve
            limit: Maximum number of records
            
        Returns:
            List of health metric records
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(CableHealthMetrics).where(
            and_(
                CableHealthMetrics.link_id == link_id,
                CableHealthMetrics.measured_at >= since
            )
        ).order_by(CableHealthMetrics.measured_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_unhealthy_links(
        self,
        threshold_score: float = 70.0
    ) -> List[CableHealthMetrics]:
        """
        Get all links with health score below threshold.
        
        Args:
            threshold_score: Health score threshold (0-100)
            
        Returns:
            List of unhealthy cable health metrics
        """
        # Get most recent metric for each link
        query = select(CableHealthMetrics).where(
            CableHealthMetrics.health_score < threshold_score
        ).order_by(CableHealthMetrics.measured_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())