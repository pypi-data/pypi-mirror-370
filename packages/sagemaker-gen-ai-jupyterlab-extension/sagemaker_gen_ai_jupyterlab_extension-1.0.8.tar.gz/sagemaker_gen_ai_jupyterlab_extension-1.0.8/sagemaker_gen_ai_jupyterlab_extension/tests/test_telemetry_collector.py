import unittest
from unittest.mock import patch, MagicMock
import os
from sagemaker_gen_ai_jupyterlab_extension.telemetry_collector import TelemetryCollector


class TestTelemetryCollector(unittest.TestCase):
    
    def test_extract_account_id_from_arn_valid(self):
        """Test extracting account ID from valid ARN"""
        arn = "arn:aws:codewhisperer:us-east-1:756160874543:profile/N4X4X9CQEXRP"
        account_id = TelemetryCollector._extract_account_id_from_arn(arn)
        self.assertEqual(account_id, "756160874543")
    
    def test_extract_account_id_from_arn_invalid(self):
        """Test extracting account ID from invalid ARN"""
        invalid_arn = "invalid-arn-format"
        account_id = TelemetryCollector._extract_account_id_from_arn(invalid_arn)
        self.assertIsNone(account_id)
    
    def test_extract_account_id_from_arn_none(self):
        """Test extracting account ID from None"""
        account_id = TelemetryCollector._extract_account_id_from_arn(None)
        self.assertIsNone(account_id)
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.telemetry_collector.EnvironmentDetector.get_environment')
    @patch('asyncio.new_event_loop')
    def test_detect_environment_md_idc(self, mock_new_loop, mock_get_env):
        """Test environment detection for MD_IDC"""
        mock_env = MagicMock()
        mock_env.name = "MD_IDC"
        mock_get_env.return_value = mock_env
        
        mock_loop = MagicMock()
        mock_new_loop.return_value = mock_loop
        mock_loop.run_until_complete.return_value = mock_env
        
        env = TelemetryCollector._detect_environment()
        self.assertEqual(env, "MD_IDC")
    
    @patch('asyncio.run')
    def test_detect_environment_exception(self, mock_run):
        """Test environment detection fallback on exception"""
        mock_run.side_effect = Exception("Test error")
        
        env = TelemetryCollector._detect_environment()
        self.assertEqual(env, "UNKNOWN")
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.telemetry_collector.TelemetryCollector._detect_environment')
    @patch('sagemaker_gen_ai_jupyterlab_extension.telemetry_collector.get_new_metrics_context')
    @patch('sagemaker_gen_ai_jupyterlab_extension.telemetry_collector.flush_metrics')
    def test_collect_telemetry_basic(self, mock_flush, mock_get_context, mock_detect_env):
        """Test basic telemetry collection"""
        mock_detect_env.return_value = "MD_IDC"
        mock_metrics = MagicMock()
        mock_get_context.return_value = mock_metrics
        
        telemetry_params = {
            "name": "amazonq_enterFocusConversation",
            "data": {
                "latency": 150,
                "result": "Succeeded"
            }
        }
        
        TelemetryCollector.collect_telemetry(telemetry_params)
        
        # Verify metrics context was created
        mock_get_context.assert_called_once_with("LSP_Telemetry_Event", "MD_IDC")
        
        # Verify dimensions were added (EventName and Result)
        expected_dimension_calls = [
            unittest.mock.call({"EventName": "amazonq_enterFocusConversation"}),
            unittest.mock.call({"Result": "Succeeded"})
        ]
        mock_metrics.put_dimensions.assert_has_calls(expected_dimension_calls, any_order=True)
        
        # Verify metric was added
        mock_metrics.put_metric.assert_called_with("RequestLatency", 150, "Milliseconds")
        
        # Verify metrics were flushed
        mock_flush.assert_called_once_with(mock_metrics)
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.telemetry_collector.TelemetryCollector._detect_environment')
    @patch('sagemaker_gen_ai_jupyterlab_extension.telemetry_collector.get_new_metrics_context')
    @patch('sagemaker_gen_ai_jupyterlab_extension.telemetry_collector.flush_metrics')
    def test_collect_telemetry_with_account_id(self, mock_flush, mock_get_context, mock_detect_env):
        """Test telemetry collection with account ID extraction"""
        mock_detect_env.return_value = "MD_IDC"
        mock_metrics = MagicMock()
        mock_get_context.return_value = mock_metrics
        
        telemetry_params = {
            "name": "test_event",
            "data": {
                "credentialStartUrl": "arn:aws:codewhisperer:us-east-1:756160874543:profile/test",
                "cwsprChatRequestLength": 100
            }
        }
        
        TelemetryCollector.collect_telemetry(telemetry_params)
        
        # Verify account ID was set (check that it was called at some point)
        mock_metrics.set_property.assert_any_call("AccountId", "756160874543")
        
        # Verify QProfileArn was also set
        mock_metrics.set_property.assert_any_call("QProfileArn", "arn:aws:codewhisperer:us-east-1:756160874543:profile/test")
        
        # Verify metric was added with correct mapping
        mock_metrics.put_metric.assert_called_with("ChatRequestSize", 100, "Count")
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.telemetry_collector.TelemetryCollector._detect_environment')
    @patch('sagemaker_gen_ai_jupyterlab_extension.telemetry_collector.get_new_metrics_context')
    @patch('sagemaker_gen_ai_jupyterlab_extension.telemetry_collector.flush_metrics')
    def test_collect_telemetry_string_to_int_conversion(self, mock_flush, mock_get_context, mock_detect_env):
        """Test string to int conversion in telemetry collection"""
        mock_detect_env.return_value = "MD_IDC"
        mock_metrics = MagicMock()
        mock_get_context.return_value = mock_metrics
        
        telemetry_params = {
            "name": "test_event",
            "data": {
                "latency": "250"  # String number
            }
        }
        
        TelemetryCollector.collect_telemetry(telemetry_params)
        
        # Verify string was converted to int
        mock_metrics.put_metric.assert_called_with("RequestLatency", 250, "Milliseconds")
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.telemetry_collector.TelemetryCollector._detect_environment')
    @patch('sagemaker_gen_ai_jupyterlab_extension.telemetry_collector.get_new_metrics_context')
    @patch('sagemaker_gen_ai_jupyterlab_extension.telemetry_collector.flush_metrics')
    def test_collect_telemetry_with_common_properties(self, mock_flush, mock_get_context, mock_detect_env):
        """Test telemetry collection with common properties"""
        mock_detect_env.return_value = "MD_IDC"
        mock_metrics = MagicMock()
        mock_get_context.return_value = mock_metrics
        
        telemetry_params = {
            "name": "test_event",
            "data": {
                "cwsprChatConversationId": "conv-123",
                "cwsprChatMessageId": "msg-456",
                "result": "Succeeded",
                "cwsprChatConversationType": "chat"
            }
        }
        
        TelemetryCollector.collect_telemetry(telemetry_params)
        
        # Verify properties were set
        expected_property_calls = [
            unittest.mock.call("ConversationID", "conv-123"),
            unittest.mock.call("MessageID", "msg-456")
        ]
        mock_metrics.set_property.assert_has_calls(expected_property_calls, any_order=True)
        
        # Verify dimensions were set
        expected_dimension_calls = [
            unittest.mock.call({"EventName": "test_event"}),
            unittest.mock.call({"Result": "Succeeded"}),
            unittest.mock.call({"ConversationType": "chat"})
        ]
        mock_metrics.put_dimensions.assert_has_calls(expected_dimension_calls, any_order=True)
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.telemetry_collector.logger')
    @patch('sagemaker_gen_ai_jupyterlab_extension.telemetry_collector.TelemetryCollector._detect_environment')
    def test_collect_telemetry_exception_handling(self, mock_detect_env, mock_logger):
        """Test exception handling in telemetry collection"""
        mock_detect_env.side_effect = Exception("Test error")
        
        telemetry_params = {"name": "test_event", "data": {}}
        
        TelemetryCollector.collect_telemetry(telemetry_params)
        
        # Verify error was logged
        mock_logger.error.assert_called_once_with("Error collecting LSP telemetry: Test error")





if __name__ == '__main__':
    unittest.main()