"""
SNMP client service for querying network devices.

- On environments where pysnmp + asyncore work, the full implementation is used.
- On Python 3.12+ (where asyncore is removed), a stub is used so the app can start
  and SNMP endpoints can return HTTP 501.
"""

from typing import Dict, List, Optional, Tuple
import asyncio
import logging
import sys

logger = logging.getLogger(__name__)

# Flag to let the API layer know whether real SNMP is available
SNMP_REAL_IMPL = False

# Try to import pysnmp async hlapi; if it fails (e.g. Python 3.12 asyncore issues),
# fall back to stub mode.
try:
    # Python 3.12 removed asyncore; most pysnmp versions still depend on it.
    if sys.version_info >= (3, 12):
        raise ImportError("pysnmp asyncore stack is not supported on Python 3.12+")

    from pysnmp.hlapi.v3arch.asyncio import (  # type: ignore
        getCmd,
        nextCmd,
        bulkCmd,
        SnmpEngine,
        CommunityData,
        UdpTransportTarget,
        ContextData,
        ObjectType,
        ObjectIdentity,
    )

    SNMP_REAL_IMPL = True
    logger.info("SNMPClient: using real pysnmp async implementation")

except ImportError as e:
    logger.warning(
        "SNMPClient: running in STUB mode (pysnmp not available or not supported): %s",
        e,
    )

    # Define dummy types so type hints still work; implementations below will raise.
    getCmd = nextCmd = bulkCmd = None  # type: ignore

    class SnmpEngine:  # type: ignore[no-redef]
        pass

    class CommunityData:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

    class UdpTransportTarget:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

    class ContextData:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

    class ObjectType:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

    class ObjectIdentity:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass


class SNMPClient:
    """
    SNMP client for querying network devices.
    Supports SNMPv2c and SNMPv3 when SNMP_REAL_IMPL is True.
    In stub mode, all async methods raise NotImplementedError.
    """

    # Standard OID mappings (MIB-II)
    OIDS = {
        # System Information
        "sysDescr": "1.3.6.1.2.1.1.1.0",
        "sysObjectID": "1.3.6.1.2.1.1.2.0",
        "sysUpTime": "1.3.6.1.2.1.1.3.0",
        "sysContact": "1.3.6.1.2.1.1.4.0",
        "sysName": "1.3.6.1.2.1.1.5.0",
        "sysLocation": "1.3.6.1.2.1.1.6.0",
        "sysServices": "1.3.6.1.2.1.1.7.0",
        # Interfaces
        "interfaces": "1.3.6.1.2.1.2",
        "ifNumber": "1.3.6.1.2.1.2.1.0",
        "ifTable": "1.3.6.1.2.1.2.2",
        "ifIndex": "1.3.6.1.2.1.2.2.1.1",
        "ifDescr": "1.3.6.1.2.1.2.2.1.2",
        "ifType": "1.3.6.1.2.1.2.2.1.3",
        "ifMtu": "1.3.6.1.2.1.2.2.1.4",
        "ifSpeed": "1.3.6.1.2.1.2.2.1.5",
        "ifPhysAddress": "1.3.6.1.2.1.2.2.1.6",
        "ifAdminStatus": "1.3.6.1.2.1.2.2.1.7",
        "ifOperStatus": "1.3.6.1.2.1.2.2.1.8",
        "ifLastChange": "1.3.6.1.2.1.2.2.1.9",
        "ifInOctets": "1.3.6.1.2.1.2.2.1.10",
        "ifInUcastPkts": "1.3.6.1.2.1.2.2.1.11",
        "ifInDiscards": "1.3.6.1.2.1.2.2.1.13",
        "ifInErrors": "1.3.6.1.2.1.2.2.1.14",
        "ifOutOctets": "1.3.6.1.2.1.2.2.1.16",
        "ifOutUcastPkts": "1.3.6.1.2.1.2.2.1.17",
        "ifOutDiscards": "1.3.6.1.2.1.2.2.1.19",
        "ifOutErrors": "1.3.6.1.2.1.2.2.1.20",
        # IP
        "ipForwarding": "1.3.6.1.2.1.4.1.0",
        "ipDefaultTTL": "1.3.6.1.2.1.4.2.0",
        # LLDP
        "lldpRemTable": "1.0.8802.1.1.2.1.4.1",
        "lldpRemChassisId": "1.0.8802.1.1.2.1.4.1.1.5",
        "lldpRemPortId": "1.0.8802.1.1.2.1.4.1.1.7",
        "lldpRemSysName": "1.0.8802.1.1.2.1.4.1.1.9",
        # Host Resources
        "hrProcessorLoad": "1.3.6.1.2.1.25.3.3.1.2",
        "hrStorageTable": "1.3.6.1.2.1.25.2.3",
        "hrStorageDescr": "1.3.6.1.2.1.25.2.3.1.3",
        "hrStorageSize": "1.3.6.1.2.1.25.2.3.1.5",
        "hrStorageUsed": "1.3.6.1.2.1.25.2.3.1.6",
    }

    def __init__(
        self,
        host: str,
        community: str = "public",
        version: str = "2c",
        port: int = 161,
        timeout: int = 5,
        retries: int = 3,
    ):
        """
        Initialize SNMP client.

        Args:
            host: Target device IP or hostname
            community: SNMP community string
            version: SNMP version ("2c" or "3")
            port: SNMP port (default: 161)
            timeout: Timeout in seconds
            retries: Number of retry attempts
        """
        self.host = host
        self.community = community
        self.version = version
        self.port = port
        self.timeout = timeout
        self.retries = retries
        self.engine = SnmpEngine()

        if not SNMP_REAL_IMPL:
            logger.warning(
                "SNMPClient created in stub mode for host %s: "
                "SNMP operations are not available on this environment",
                host,
            )

    def _get_transport(self) -> "UdpTransportTarget":
        """Create UDP transport target."""
        return UdpTransportTarget(
            (self.host, self.port),
            timeout=self.timeout,  # type: ignore[arg-type]
            retries=self.retries,
        )

    def _get_credentials(self) -> "CommunityData":
        """Create SNMP credentials for v2c."""
        return CommunityData(self.community, mpModel=1)  # 1 = SNMPv2c

    async def get(self, oid: str) -> Optional[str]:
        """
        Query single OID (SNMP GET).

        Returns None in stub mode.
        """
        if not SNMP_REAL_IMPL:
            raise NotImplementedError("SNMP not available on this Python version/environment")

        try:
            errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
                self.engine,
                self._get_credentials(),
                self._get_transport(),
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
            ) # type: ignore

            if errorIndication:
                logger.warning("SNMP GET error for %s:%s: %s", self.host, oid, errorIndication)
                return None

            if errorStatus:
                logger.warning(
                    "SNMP GET status error for %s: %s at %s",
                    self.host,
                    errorStatus.prettyPrint(),
                    varBinds[int(errorIndex) - 1][0] if errorIndex else "?",
                )
                return None

            if varBinds:
                return str(varBinds[0][1])
            return None

        except Exception as e:
            logger.error("SNMP GET failed for %s:%s: %s", self.host, oid, e)
            return None

    async def walk(self, base_oid: str, max_rows: int = 100) -> List[Tuple[str, str]]:
        """
        Walk SNMP table (SNMP GETNEXT/GETBULK).

        Returns empty list in stub mode.
        """
        if not SNMP_REAL_IMPL:
            raise NotImplementedError("SNMP not available on this Python version/environment")

        results: List[Tuple[str, str]] = []
        try:
            async for errorIndication, errorStatus, errorIndex, varBinds in nextCmd(
                self.engine,
                self._get_credentials(),
                self._get_transport(),
                ContextData(),
                ObjectType(ObjectIdentity(base_oid)),
                lexicographicMode=False,
            ): # type: ignore
                if errorIndication:
                    logger.warning("SNMP WALK error: %s", errorIndication)
                    break

                if errorStatus:
                    logger.warning(
                        "SNMP WALK status error: %s at %s",
                        errorStatus.prettyPrint(),
                        varBinds[int(errorIndex) - 1][0] if errorIndex else "?",
                    )
                    break

                for varBind in varBinds:
                    results.append((str(varBind[0]), str(varBind[1])))

                if len(results) >= max_rows:
                    break

            return results

        except Exception as e:
            logger.error("SNMP WALK failed for %s:%s: %s", self.host, base_oid, e)
            return []

    async def get_system_info(self) -> Dict:
        """
        Query basic system information.
        """
        if not SNMP_REAL_IMPL:
            raise NotImplementedError("SNMP not available on this Python version/environment")

        info = {
            "host": self.host,
            "sysDescr": await self.get(self.OIDS["sysDescr"]),
            "sysName": await self.get(self.OIDS["sysName"]),
            "sysLocation": await self.get(self.OIDS["sysLocation"]),
            "sysContact": await self.get(self.OIDS["sysContact"]),
            "sysUpTime": await self.get(self.OIDS["sysUpTime"]),
        }

        info["device_type"] = self._classify_device(info.get("sysDescr"))
        return info

    async def get_interfaces(self) -> List[Dict]:
        """
        Query all network interfaces.
        """
        if not SNMP_REAL_IMPL:
            raise NotImplementedError("SNMP not available on this Python version/environment")

        interfaces: List[Dict] = []

        try:
            if_table = await self.walk(self.OIDS["ifTable"])
            if not if_table:
                return interfaces

            current_if: Dict = {}
            for oid, value in if_table:
                oid_parts = oid.split(".")
                if len(oid_parts) < 2:
                    continue

                if_index = oid_parts[-1]

                if ".2.2.1.1." in oid:  # ifIndex
                    if current_if:
                        interfaces.append(current_if)
                    current_if = {"ifIndex": value, "index": if_index}
                elif ".2.2.1.2." in oid:  # ifDescr
                    current_if["ifDescr"] = value
                elif ".2.2.1.5." in oid:  # ifSpeed
                    current_if["ifSpeed"] = int(value) if str(value).isdigit() else value
                elif ".2.2.1.7." in oid:  # ifAdminStatus
                    current_if["ifAdminStatus"] = self._map_status(str(value))
                elif ".2.2.1.8." in oid:  # ifOperStatus
                    current_if["ifOperStatus"] = self._map_status(str(value))
                elif ".2.2.1.10." in oid:  # ifInOctets
                    current_if["ifInOctets"] = int(value) if str(value).isdigit() else 0
                elif ".2.2.1.16." in oid:  # ifOutOctets
                    current_if["ifOutOctets"] = int(value) if str(value).isdigit() else 0
                elif ".2.2.1.14." in oid:  # ifInErrors
                    current_if["ifInErrors"] = int(value) if str(value).isdigit() else 0
                elif ".2.2.1.20." in oid:  # ifOutErrors
                    current_if["ifOutErrors"] = int(value) if str(value).isdigit() else 0

            if current_if:
                interfaces.append(current_if)

            logger.info("Retrieved %d interfaces from %s", len(interfaces), self.host)
            return interfaces

        except Exception as e:
            logger.error("Failed to get interfaces from %s: %s", self.host, e)
            return []

    async def get_interface_stats(self, if_index: str) -> Dict:
        """
        Get statistics for a specific interface.
        """
        if not SNMP_REAL_IMPL:
            raise NotImplementedError("SNMP not available on this Python version/environment")

        stats: Dict[str, str] = {}
        oid_base = "1.3.6.1.2.1.2.2.1."

        fields = {
            "2": "ifDescr",
            "5": "ifSpeed",
            "7": "ifAdminStatus",
            "8": "ifOperStatus",
            "10": "ifInOctets",
            "11": "ifInUcastPkts",
            "13": "ifInDiscards",
            "14": "ifInErrors",
            "16": "ifOutOctets",
            "17": "ifOutUcastPkts",
            "19": "ifOutDiscards",
            "20": "ifOutErrors",
        }

        for field_id, field_name in fields.items():
            oid = f"{oid_base}{field_id}.{if_index}"
            value = await self.get(oid)
            if value is not None:
                stats[field_name] = value

        return stats

    def _map_status(self, status_code: str) -> str:
        """Map SNMP status code to readable string."""
        status_map = {
            "1": "UP",
            "2": "DOWN",
            "3": "TESTING",
            "4": "UNKNOWN",
            "5": "DORMANT",
            "6": "NOT_PRESENT",
            "7": "LOWER_LAYER_DOWN",
        }
        return status_map.get(status_code, "UNKNOWN")

    def _classify_device(self, sys_descr: Optional[str]) -> str:
        """Classify device type from sysDescr."""
        if not sys_descr:
            return "UNKNOWN"

        sys_descr_lower = sys_descr.lower()

        if any(x in sys_descr_lower for x in ["cisco", "catalyst"]):
            if "switch" in sys_descr_lower or "catalyst" in sys_descr_lower:
                return "SWITCH"
            return "ROUTER"
        elif any(x in sys_descr_lower for x in ["hp", "arista", "juniper", "dell", "netgear"]):
            return "SWITCH"
        elif any(x in sys_descr_lower for x in ["windows", "linux", "ubuntu", "centos"]):
            return "SERVER"
        elif "printer" in sys_descr_lower:
            return "PRINTER"
        elif any(x in sys_descr_lower for x in ["access point", "wireless", "ap"]):
            return "AP"

        return "UNKNOWN"


class SNMPService:
    """High-level SNMP service for device discovery and monitoring."""

    def __init__(self, community: str = "public"):
        """
        Initialize SNMP service.

        Args:
            community: Default SNMP community string
        """
        self.community = community
        self.clients: Dict[str, SNMPClient] = {}

        if not SNMP_REAL_IMPL:
            logger.warning(
                "SNMPService created in stub mode: SNMP discovery is not available"
            )

    def add_device(self, host: str, community: Optional[str] = None) -> None:
        """
        Add device for SNMP monitoring.
        """
        community = community or self.community
        self.clients[host] = SNMPClient(host, community)

    async def discover_device(self, host: str, community: Optional[str] = None) -> Dict:
        """
        Discover single device via SNMP.
        """
        if not SNMP_REAL_IMPL:
            raise NotImplementedError("SNMP not available on this Python version/environment")

        community = community or self.community
        client = SNMPClient(host, community)

        try:
            system_info, interfaces = await asyncio.gather(
                client.get_system_info(),
                client.get_interfaces(),
                return_exceptions=True,
            )

            if isinstance(system_info, Exception):
                logger.error("Failed to get system info from %s: %s", host, system_info)
                system_info = {}

            if isinstance(interfaces, Exception):
                logger.error("Failed to get interfaces from %s: %s", host, interfaces)
                interfaces = []

            return {
                "host": host,
                "status": "SUCCESS",
                "system_info": system_info,
                "interfaces": interfaces,
                "interface_count": len(interfaces),  # type: ignore[arg-type]
            }

        except Exception as e:
            logger.error("SNMP discovery failed for %s: %s", host, e)
            return {"host": host, "status": "FAILED", "error": str(e)}

    async def discover_all(self) -> List[Dict]:
        """
        Discover all registered devices in parallel.
        """
        if not SNMP_REAL_IMPL:
            raise NotImplementedError("SNMP not available on this Python version/environment")

        if not self.clients:
            logger.warning("No devices registered for SNMP discovery")
            return []

        logger.info("Discovering %d devices via SNMP", len(self.clients))

        tasks = [
            self.discover_device(host, client.community)
            for host, client in self.clients.items()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_results: List[Dict] = []
        for result in results:
            if isinstance(result, dict):
                valid_results.append(result)
            else:
                logger.error("Discovery task failed: %s", result)

        return valid_results
