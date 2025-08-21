#!/bin/bash

# Install fastmcp
pip install fastmcp

# Create ~/.aws/amazonq directory if it doesn't exist
mkdir -p ~/.aws/amazonq

# Create or update fastmcp_proxy.py
cat > ~/.aws/amazonq/fastmcp_proxy.py << 'EOF'
import hashlib
import hmac
import logging
import os
from datetime import datetime
from typing import Optional

import boto3
import httpx
from fastmcp import FastMCP
from fastmcp.client.transports import StreamableHttpTransport
from httpx import Request

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("fastmcp_proxy")

# Option 1: Fetch AWS credentials from environment variables
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_session_token = os.getenv("AWS_SESSION_TOKEN")

# Option 2: Fetch AWS credentials from supplied AWS profile name
aws_profile_name = os.getenv("AWS_PROFILE_NAME")

# Option 3: either of above is supplied, the default aws profile will be used to fetch AWS credentials

domain_id = os.getenv("DOMAIN_ID")
project_id = os.getenv("PROJECT_ID")
mcp_url = os.getenv("MCP_URL") or "https://jsjuhi7499.execute-api.us-east-1.amazonaws.com/personal/project-context/mcp"

aws_region = os.getenv("AWS_REGION") or "us-east-1"  # Default region if not specified


class SigV4Signer:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        service: str,
        region: str,
        token: Optional[str] = None,
    ):
        self._access_key = access_key
        self._secret_key = secret_key
        self._token = token
        self._service = service
        self._region = region
        self._signed_headers = "host;x-amz-date"

        # the hashing algorithm that you use to calculate the digests in the canonical request
        self._algorithm = "AWS4-HMAC-SHA256"

    # ref: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_sigv-create-signed-request.html#derive-signing-key
    def get_signature_key(self, date_stamp: str) -> bytes:

        def hmacsha256(key, msg):
            return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

        date_key = hmacsha256(("AWS4" + self._secret_key).encode("utf-8"), date_stamp)
        date_region_key = hmacsha256(date_key, self._region)
        date_region_key_service_key = hmacsha256(date_region_key, self._service)
        signing_key = hmacsha256(date_region_key_service_key, "aws4_request")
        return signing_key

    def get_canonical_request(self, request: Request, timestamp: str) -> str:
        canonical_uri = request.url.path
        canonical_querystring = request.url.query.decode("utf-8")
        logger.debug(f"Canonical URI: {canonical_uri}")
        logger.debug(f"Canonical Query String: {canonical_querystring}")
        canonical_headers = f"host:{request.url.host}\nx-amz-date:{timestamp}\n"

        logger.debug(f"Payload: {request.content}")
        if request.content:
            payload_hash = hashlib.sha256(request.content).hexdigest()
        else:
            payload_hash = hashlib.sha256(("").encode("utf-8")).hexdigest()

        logger.debug(f"Payload hash: {payload_hash}")

        canonical_request = (
            f"{request.method}\n{canonical_uri}\n{canonical_querystring}\n"
            f"{canonical_headers}\n{self._signed_headers}\n{payload_hash}"
        )
        return canonical_request

    def get_authorization_header(self, credential_scope: str, signature: str) -> str:
        return (
            f"{self._algorithm} Credential={self._access_key}/{credential_scope},"
            f" SignedHeaders={self._signed_headers}, Signature={signature}"
        )

    def __call__(self, request: Request) -> Request:
        # Create a date for headers and the credential string
        current_time = datetime.utcnow()
        timestamp = current_time.strftime("%Y%m%dT%H%M%SZ")
        datestamp = current_time.strftime("%Y%m%d")  # Date w/o time, used in credential scope

        if request.content:
            payload_hash = hashlib.sha256(request.content).hexdigest()
        else:
            payload_hash = hashlib.sha256(("").encode("utf-8")).hexdigest()

        # CREATE A CANONICAL REQUEST
        canonical_request = self.get_canonical_request(request=request, timestamp=timestamp)
        canonical_request_hash = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()

        # CREATE THE STRING TO SIGN
        credential_scope = f"{datestamp}/{self._region}/{self._service}/aws4_request"
        string_to_sign = (
            f"{self._algorithm}\n{timestamp}\n{credential_scope}\n{canonical_request_hash}"
        )

        # CALCULATE THE SIGNATURE
        signing_key = self.get_signature_key(datestamp)
        signature = hmac.new(
            signing_key, (string_to_sign).encode("utf-8"), hashlib.sha256
        ).hexdigest()

        # GENERATE AUTHORIZATION HEADER
        authorization_header = self.get_authorization_header(
            credential_scope=credential_scope, signature=signature
        )

        # ADD SIGV4 HEADERS TO THE ORIGINAL REQUEST
        headers = {
            "x-amz-date": timestamp,
            "authorization": authorization_header,
            "x-amz-content": request.content,
            "x-amz-content-sha256": payload_hash,
            "x-amz-request-sha256": canonical_request_hash,
        }
        if domain_id:
            headers["amazondatazonedomain"] = domain_id

        if project_id:
            headers["amazondatazoneproject"] = project_id

        if self._token:
            headers["x-amz-security-token"] = self._token
        request.headers.update(headers)

        return request


class SigV4CustomAuth(httpx.Auth):
    """Custom SigV4 authentication implementation for HTTPX."""

    requires_request_body = True

    def __init__(self, service, region, algorithm="AWS4-HMAC-SHA256"):
        logger.debug(f"Initializing SigV4CustomAuth for service={service}, region={region}")
        self.service = service
        self.region = region
        self.algorithm = algorithm

    def auth_flow(self, request):
        logger.debug("SigV4CustomAuth.auth_flow called for request")

        # Get credentials from boto3 or environment variables
        if aws_access_key and aws_secret_key and aws_session_token:
            logger.debug("Using credentials from environment variables")
            access_key = aws_access_key
            secret_key = aws_secret_key
            token = aws_session_token
        elif aws_profile_name:
            logger.debug("Fetching credentials from aws profile {aws_profile_name}")
            credentials = boto3.Session(profile_name=aws_profile_name).get_credentials()
            access_key = credentials.access_key
            secret_key = credentials.secret_key
            token = credentials.token
            logger.debug(f"Successfully fetched credentials from aws profile {aws_profile_name}")
        else:
            logger.debug("Fetching credentials from default aws profile")
            credentials = boto3.Session().get_credentials()
            access_key = credentials.access_key
            secret_key = credentials.secret_key
            token = credentials.token
            logger.debug("Successfully fetched credentials from default aws profile")

        sigv4_signer = SigV4Signer(
            access_key=access_key,
            secret_key=secret_key,
            service=self.service,
            region=self.region,
            token=token,
        )

        request = sigv4_signer.__call__(request)

        logger.debug(f"Final request headers: {request.headers}")
        logger.debug(f"authorization: {request.headers.get('authorization')}")
        yield request


# Custom client factory to ensure each request is signed with SigV4
def create_sigv4_client(headers=None, auth=None, **kwargs):
    """
    Create an httpx.AsyncClient with SigV4 authentication.

    Args:
        headers: Headers to include in requests
        auth: Auth parameter (ignored as we provide our own)
        **kwargs: Additional arguments to pass to httpx.AsyncClient
    """
    # Create a copy of kwargs to avoid modifying the passed dict
    client_kwargs = {"follow_redirects": True, "timeout": httpx.Timeout(30.0), **kwargs}

    # Add headers if provided
    if headers is not None:
        client_kwargs["headers"] = headers

    logger.info(
        "Creating httpx.AsyncClient with custom headers: %s", client_kwargs.get("headers", {})
    )

    # Create the client with SigV4 auth
    logger.info("Creating httpx.AsyncClient with SigV4 authentication")

    return httpx.AsyncClient(
        auth=SigV4CustomAuth(region=aws_region, service="datazone"), **client_kwargs
    )


# Create transport with SigV4 authentication via custom client factory
transport = StreamableHttpTransport(
    url=mcp_url,
    httpx_client_factory=create_sigv4_client,
)

# Create proxy using the transport
proxy = FastMCP.as_proxy(transport, name="SMUS FastMCP Proxy")

if __name__ == "__main__":
    proxy.run()
EOF

# Get DataZone values from resource metadata
DOMAIN_ID=$(jq -r '.AdditionalMetadata.DataZoneDomainId' /opt/ml/metadata/resource-metadata.json)
PROJECT_ID=$(jq -r '.AdditionalMetadata.DataZoneProjectId' /opt/ml/metadata/resource-metadata.json)
AWS_REGION=$(jq -r '.AdditionalMetadata.DataZoneDomainRegion' /opt/ml/metadata/resource-metadata.json)

# Get AWS credentials from SageMaker
CREDS=$(sagemaker-studio credentials get-domain-execution-role-credential-in-space --domain-id $DOMAIN_ID --profile default)
ACCESS_KEY=$(echo $CREDS | jq -r '.AccessKeyId')
SECRET_KEY=$(echo $CREDS | jq -r '.SecretAccessKey')
SESSION_TOKEN=$(echo $CREDS | jq -r '.SessionToken')

# Create mcp.json with actual credentials
cat > ~/.aws/amazonq/mcp.json << EOF
{
  "mcpServers": {
    "smus-remote-mcp": {
      "command": "python",
      "args": [
        ".aws/amazonq/fastmcp_proxy.py"
      ],
      "env": {
        "AWS_PROFILE_NAME": "default",
        "DOMAIN_ID": "$DOMAIN_ID",
        "PROJECT_ID": "$PROJECT_ID",
        "AWS_REGION": "$AWS_REGION"
      },
      "autoApprove": []
    }
  }
}
EOF

echo "MCP setup complete. Files created or updated:"
echo "- ~/.aws/amazonq/fastmcp_proxy.py"
echo "- ~/.aws/amazonq/mcp.json"

# Restart SageMaker UI Jupyter server
restart-sagemaker-ui-jupyter-server