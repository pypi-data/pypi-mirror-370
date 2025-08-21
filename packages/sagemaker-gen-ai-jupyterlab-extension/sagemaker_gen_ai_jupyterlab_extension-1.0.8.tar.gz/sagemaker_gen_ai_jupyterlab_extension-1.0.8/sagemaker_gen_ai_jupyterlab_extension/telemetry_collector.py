import logging
import re
import asyncio
from .request_logger import get_new_metrics_context, flush_metrics
from sagemaker_jupyterlab_extension_common.util.environment import EnvironmentDetector

logger = logging.getLogger('SageMakerGenAIJupyterLabExtension')

class TelemetryCollector:
    """Collects and processes LSP server telemetry events"""
    
    # Mapping of LSP telemetry data fields to CloudWatch metric names and units
    # Key: field name from LSP telemetry data, Value: (metric_name, unit)
    # lsp server code ref: https://github.com/aws/language-servers/blob/main/server/aws-lsp-codewhisperer/src/shared/telemetry/types.ts

    METRIC_MAPPINGS = {
        'latency': ('RequestLatency', 'Milliseconds'),  # General request latency
        'cwsprChatTimeToFirstChunk': ('ChatTimeToFirstChunk', 'Milliseconds'),  # Time to first response chunk
        'cwsprChatFullResponseLatency': ('ChatFullResponseLatency', 'Milliseconds'),  # Complete response time
        'amazonqTimeToLoadHistory': ('ChatHistoryLoadTime', 'Milliseconds'),  # History loading time
        'cwsprChatRequestLength': ('ChatRequestSize', 'Count'),  # Request character count
        'cwsprChatResponseLength': ('ChatResponseSize', 'Count'),  # Response character count
        'cwsprChatSourceLinkCount': ('ChatSourceLinks', 'Count'),  # Number of source links
        'cwsprChatReferencesCount': ('ChatReferences', 'Count'),  # Number of code references
        'cwsprChatFollowUpCount': ('ChatFollowUps', 'Count'),  # Number of follow-up suggestions
        'numActiveServers': ('ActiveLSPServers', 'Count'),  # Active MCP server 
        'numGlobalServers': ('GlobalLSPServers', 'Count'),  # Total MCP server 
        'openTabCount': ('OpenChatTabs', 'Count')  # Number of open chat tabs
    }
    
    @staticmethod
    def _extract_account_id_from_arn(credential_start_url):
        """Extract account ID from ARN format credentialStartUrl"""
        if not credential_start_url:
            return None
        # ARN format: arn:aws:codewhisperer:region:account-id:profile/profile-id
        match = re.match(r'arn:aws:[^:]+:[^:]+:([^:]+):', credential_start_url)
        return match.group(1) if match else None
    
    @staticmethod
    def _detect_environment():
        """Detect the runtime environment using EnvironmentDetector"""
        try:
            environment = asyncio.run(EnvironmentDetector.get_environment())
            logger.info(f"Detected environment: {environment.name}")
            return environment.name
        except Exception as e:
            logger.error(f"Failed to detect environment: {e}", exc_info=True)
            return "UNKNOWN"
    
    @staticmethod
    def collect_telemetry(telemetry_params):
        """Collect telemetry metrics from LSP server events and send to CloudWatch"""
        try:
            # Detect runtime environment using common environment detector
            environment_name = TelemetryCollector._detect_environment()
            
            # Extract telemetry event data
            event_data = telemetry_params.get("data", {})
            event_name = telemetry_params.get("name", "unknown")
            
            # Try to extract account ID from credential ARN if available
            credential_start_url = event_data.get("credentialStartUrl")
            account_id = TelemetryCollector._extract_account_id_from_arn(credential_start_url)
            
            # Initialize metrics context with operation and environment
            metrics = get_new_metrics_context("LSP_Telemetry_Event", environment_name)
            
            # Override default account ID if we extracted one from telemetry
            if account_id:
                metrics.set_property("AccountId", account_id)
            
            # Add event name as a dimension for filtering/grouping
            metrics.put_dimensions({"EventName": event_name})
            
            # Process all numeric metrics from the telemetry data
            for data_field, (metric_name, unit) in TelemetryCollector.METRIC_MAPPINGS.items():
                if data_field in event_data:
                    value = event_data[data_field]
                    # Convert string numbers to numeric values
                    if isinstance(value, str) and value.isdigit():
                        value = int(value)
                    # Only emit numeric metrics
                    if isinstance(value, (int, float)):
                        metrics.put_metric(metric_name, value, unit)
            
            # Add additional properties and dimensions from event data
            TelemetryCollector._add_common_properties(metrics, event_data)
            
            # Send metrics to CloudWatch via embedded metrics format
            flush_metrics(metrics)
            
        except Exception as e:
            logger.error(f"Error collecting LSP telemetry: {e}")
    
    @staticmethod
    def _add_common_properties(metrics, event_data):
        """Add common properties and dimensions from telemetry event data"""
        # Properties (metadata, not aggregated in CloudWatch)
        if "cwsprChatConversationId" in event_data:
            metrics.set_property("ConversationID", event_data["cwsprChatConversationId"])
        if "cwsprChatMessageId" in event_data:
            metrics.set_property("MessageID", event_data["cwsprChatMessageId"])
        if "languageServerVersion" in event_data:
            metrics.set_property("LSPVersion", event_data["languageServerVersion"])
        if "requestId" in event_data:
            metrics.set_property("RequestID", event_data["requestId"])
        
        # Dimensions (used for metric aggregation and filtering)
        if "result" in event_data:
            metrics.put_dimensions({"Result": event_data["result"]})  # Result = 'Succeeded' | 'Failed' | 'Cancelled'
        if "cwsprChatConversationType" in event_data:
            metrics.put_dimensions({"ConversationType": event_data["cwsprChatConversationType"]})  # Chat type
        if "credentialStartUrl" in event_data:
            metrics.set_property("QProfileArn", event_data["credentialStartUrl"])