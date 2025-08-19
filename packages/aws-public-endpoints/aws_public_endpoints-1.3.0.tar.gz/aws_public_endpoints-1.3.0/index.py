#!/usr/bin/env python3
"""
AWS Public Endpoints MCP Server - Simple Version
MCP server for scanning AWS service public endpoints
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Sequence

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aws-public-endpoints")

# Initialize MCP server
server = Server("aws-public-endpoints")


class PublicEndpointsFinder:
    """AWS public endpoints finder class"""

    def __init__(self, region: str = "us-east-1", profile: Optional[str] = None):
        self.region = region
        self.session = (
            boto3.Session(profile_name=profile) if profile else boto3.Session()
        )

    def get_client(self, service: str):
        """Create AWS client"""
        return self.session.client(service, region_name=self.region)

    async def find_ec2_endpoints(self) -> List[Dict[str, Any]]:
        """Find EC2 public instances"""
        endpoints = []
        try:
            ec2 = self.get_client("ec2")
            response = ec2.describe_instances()

            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    if instance.get("PublicIpAddress"):
                        endpoints.append(
                            {
                                "id": instance["InstanceId"],
                                "public_ip": instance["PublicIpAddress"],
                                "public_dns": instance.get("PublicDnsName", ""),
                                "state": instance["State"]["Name"],
                            }
                        )
        except ClientError as e:
            logger.error(f"EC2 scan error: {e}")

        return endpoints

    async def find_elb_endpoints(self) -> List[Dict[str, Any]]:
        """Find load balancer endpoints"""
        endpoints = []
        try:
            # ALB/NLB
            elbv2 = self.get_client("elbv2")
            response = elbv2.describe_load_balancers()

            for lb in response["LoadBalancers"]:
                if lb["Scheme"] == "internet-facing":
                    endpoints.append(
                        {
                            "id": lb["LoadBalancerName"],
                            "dns_name": lb["DNSName"],
                            "type": lb["Type"],
                            "state": lb["State"]["Code"],
                        }
                    )
        except ClientError as e:
            logger.error(f"ELB scan error: {e}")

        return endpoints

    async def find_s3_endpoints(self) -> List[Dict[str, Any]]:
        """Find S3 bucket list"""
        endpoints = []
        try:
            s3 = self.get_client("s3")
            response = s3.list_buckets()

            for bucket in response["Buckets"]:
                bucket_name = bucket["Name"]
                endpoints.append(
                    {
                        "id": bucket_name,
                        "url": f"https://{bucket_name}.s3.amazonaws.com",
                        "created": bucket["CreationDate"].isoformat(),
                    }
                )
        except ClientError as e:
            logger.error(f"S3 scan error: {e}")

        return endpoints

    async def find_api_endpoints(self) -> List[Dict[str, Any]]:
        """Find API Gateway endpoints"""
        endpoints = []
        try:
            # REST API
            api = self.get_client("apigateway")
            response = api.get_rest_apis()

            for rest_api in response["items"]:
                endpoints.append(
                    {
                        "id": rest_api["id"],
                        "name": rest_api["name"],
                        "url": f"https://{rest_api['id']}.execute-api.{self.region}.amazonaws.com",
                        "type": "REST",
                    }
                )
        except ClientError as e:
            logger.error(f"API Gateway scan error: {e}")

        return endpoints

    async def find_cloudfront_endpoints(self) -> List[Dict[str, Any]]:
        """Find CloudFront distribution endpoints"""
        endpoints = []
        try:
            cloudfront = self.get_client("cloudfront")
            response = cloudfront.list_distributions()

            if (
                "DistributionList" in response
                and "Items" in response["DistributionList"]
            ):
                for distribution in response["DistributionList"]["Items"]:
                    endpoints.append(
                        {
                            "id": distribution["Id"],
                            "domain_name": distribution["DomainName"],
                            "url": f"https://{distribution['DomainName']}",
                            "status": distribution["Status"],
                            "enabled": distribution["Enabled"],
                            "comment": distribution.get("Comment", ""),
                        }
                    )
        except ClientError as e:
            logger.error(f"CloudFront scan error: {e}")

        return endpoints

    async def scan_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Scan all services"""
        logger.info(f"Starting scan for region {self.region}")

        # Scan all services in parallel
        tasks = [
            self.find_ec2_endpoints(),
            self.find_elb_endpoints(),
            self.find_s3_endpoints(),
            self.find_api_endpoints(),
            self.find_cloudfront_endpoints(),
        ]

        (
            ec2_results,
            elb_results,
            s3_results,
            api_results,
            cloudfront_results,
        ) = await asyncio.gather(*tasks, return_exceptions=True)

        results = {
            "EC2": ec2_results if isinstance(ec2_results, list) else [],
            "ELB": elb_results if isinstance(elb_results, list) else [],
            "S3": s3_results if isinstance(s3_results, list) else [],
            "API Gateway": api_results if isinstance(api_results, list) else [],
            "CloudFront": cloudfront_results
            if isinstance(cloudfront_results, list)
            else [],
        }

        total = sum(len(endpoints) for endpoints in results.values())
        logger.info(f"Found {total} total endpoints")

        return results


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="scan_public_endpoints",
            description="Scan AWS public endpoints",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "AWS region (default: us-east-1)",
                        "default": "us-east-1",
                    },
                    "profile": {
                        "type": "string",
                        "description": "AWS profile (optional)",
                    },
                },
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """Execute tool"""

    if name == "scan_public_endpoints":
        region = arguments.get("region", "us-east-1")
        profile = arguments.get("profile")

        try:
            finder = PublicEndpointsFinder(region=region, profile=profile)
            results = await finder.scan_all()

            # Format results
            output = "# AWS Public Endpoints Scan Results\n\n"
            output += f"**Region:** {region}\n"
            if profile:
                output += f"**Profile:** {profile}\n"

            total = sum(len(endpoints) for endpoints in results.values())
            output += f"**Total Found:** {total}\n\n"

            for service, endpoints in results.items():
                output += f"## {service} ({len(endpoints)} items)\n\n"

                if not endpoints:
                    output += "No endpoints found\n\n"
                    continue

                for endpoint in endpoints:
                    output += f"- **{endpoint['id']}**\n"
                    for key, value in endpoint.items():
                        if key != "id" and value:
                            output += f"  - {key}: {value}\n"
                    output += "\n"

            return [TextContent(type="text", text=output)]

        except NoCredentialsError:
            return [TextContent(type="text", text="Error: AWS credentials not found.")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="aws-public-endpoints",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def run_server():
    """Entry point for the MCP server"""
    asyncio.run(main())


if __name__ == "__main__":
    run_server()
    run_server()
