"""
LoadBalancerConfig - supports load balancer settings for AWS CDK.
Maintainers: Eric Wilson
MIT License. See Project Root for license information.
"""

from typing import Any, Dict, List, Optional


class LoadBalancerConfig:
    """
    Load Balancer Configuration - supports Application and Network Load Balancer settings.
    Each property reads from the config dict and provides a sensible default if not set.
    """

    def __init__(self, config: dict = None, deployment=None) -> None:
        self.__config = config or {}
        self.__deployment = deployment

    @property
    def name(self) -> str:
        """Load Balancer name"""
        return self.__config.get("name", "load-balancer")

    @property
    def type(self) -> str:
        """Load Balancer type (APPLICATION or NETWORK)"""
        lb_type = self.__config.get("type", "APPLICATION")
        return lb_type.upper()

    @property
    def internet_facing(self) -> bool:
        """Whether the load balancer is internet-facing"""
        return self.__config.get("internet_facing", True)

    @property
    def vpc_id(self) -> str:
        """VPC ID for the load balancer"""
        return self.__config.get("vpc_id")

    @property
    def subnets(self) -> List[str]:
        """Subnet IDs for the load balancer"""
        return self.__config.get("subnets", [])

    @property
    def security_groups(self) -> List[str]:
        """Security group IDs for the load balancer"""
        return self.__config.get("security_groups", [])

    @property
    def deletion_protection(self) -> bool:
        """Whether deletion protection is enabled"""
        return self.__config.get("deletion_protection", False)

    @property
    def idle_timeout(self) -> int:
        """Idle timeout in seconds (for Application Load Balancer)"""
        return self.__config.get("idle_timeout", 60)

    @property
    def http2_enabled(self) -> bool:
        """Whether HTTP/2 is enabled (for Application Load Balancer)"""
        return self.__config.get("http2_enabled", True)

    @property
    def listeners(self) -> List[Dict[str, Any]]:
        """Load balancer listeners configuration"""
        return self.__config.get("listeners", [])

    @property
    def target_groups(self) -> List[Dict[str, Any]]:
        """Target groups configuration"""
        return self.__config.get("target_groups", [])

    @property
    def health_check(self) -> Dict[str, Any]:
        """Health check configuration"""
        return self.__config.get("health_check", {})

    @property
    def ssl_policy(self) -> str:
        """SSL policy for HTTPS listeners"""
        return self.__config.get("ssl_policy", "ELBSecurityPolicy-2016-08")

    @property
    def certificate_arns(self) -> List[str]:
        """Certificate ARNs for HTTPS listeners"""
        return self.__config.get("certificate_arns", [])

    @property
    def hosted_zone(self) -> Dict[str, Any]:
        """Route53 hosted zone configuration"""
        return self.__config.get("hosted_zone", {})

    @property
    def tags(self) -> Dict[str, str]:
        """Tags to apply to the load balancer"""
        return self.__config.get("tags", {})

    @property
    def vpc_id(self) -> str | None:
        """Returns the VPC ID for the Security Group"""
        return self.__config.get("vpc_id")

    @vpc_id.setter
    def vpc_id(self, value: str):
        """Sets the VPC ID for the Security Group"""
        self.__config["vpc_id"] = value
