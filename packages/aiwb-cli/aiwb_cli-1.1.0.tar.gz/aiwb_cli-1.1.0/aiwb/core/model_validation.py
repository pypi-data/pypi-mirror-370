# aiwb/core/model_validation.py

import json
import logging
import os
import time
import zipfile
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth

from .model import ServiceModel
from .client import Client
from aiwb.utils.console import show_loading_status

logger = logging.getLogger(__name__)


class ModelValidation(ServiceModel):
    service_name = "model_validation"

    def __init__(self, client: Client | None = None, output: str | None = "json"):
        super().__init__(client, output)
        # Override the URL to use the model validation service
        self._model_validation_url = os.getenv('AIWB_MODEL_VALIDATION_URL')
        self._nginx_username = os.getenv('AIWB_NGINX_USERNAME')
        self._nginx_password = os.getenv('AIWB_NGINX_PASSWORD')
        
        # Validate required environment variables
        if not self._model_validation_url:
            raise ValueError("AIWB_MODEL_VALIDATION_URL environment variable is required")
        if not self._nginx_username:
            raise ValueError("AIWB_NGINX_USERNAME environment variable is required")
        if not self._nginx_password:
            raise ValueError("AIWB_NGINX_PASSWORD environment variable is required")

    def _get_nginx_auth(self):
        """Get HTTP Basic Authentication for nginx server."""
        return HTTPBasicAuth(self._nginx_username, self._nginx_password)

    def _check_aiwb_authentication(self):
        """Check if user is logged in to AIWB system with valid token."""
        try:
            token = self._client.load_auth_token()
            
            if not token or not token.get('access_token'):
                error_msg = {
                    "success": False,
                    "message": "AIWB authentication required. Please run 'aiwb login' first to authenticate with AIWB.",
                    "code": "AIWB_AUTHENTICATION_REQUIRED"
                }
                self.stderr(error_msg)
                return False
            
            # Validate token by making a test API call to AIWB userinfo endpoint
            try:
                # Use the same endpoint as 'aiwb whoami' command
                response, error = self._client.request(
                    f"{self._client.url}/api/auth/userinfo", 
                    "GET",
                    headers={"Authorization": f"Bearer {token.get('access_token')}"},
                    timeout=300
                )
                
                if error:
                    # Debug: Let's see what the actual error is
                    print(f"Token validation error: {error}")
                    print(f"Response: {response}")
                    error_msg = {
                        "success": False,
                        "message": "AIWB authentication token is expired or invalid. Please run 'aiwb login' to refresh your token.",
                        "code": "AIWB_TOKEN_EXPIRED"
                    }
                    self.stderr(error_msg)
                    return False
                
            except Exception as validation_error:
                # Debug: Let's see what exception is occurring
                print(f"Token validation exception: {validation_error}")
                error_msg = {
                    "success": False,
                    "message": "AIWB authentication token is expired or invalid. Please run 'aiwb login' to refresh your token.",
                    "code": "AIWB_TOKEN_EXPIRED"
                }
                self.stderr(error_msg)
                return False
                
        except Exception as e:
            print(f"Authentication check exception: {e}")
            error_msg = {
                "success": False,
                "message": "AIWB authentication required. Please run 'aiwb login' first to authenticate with AIWB.",
                "code": "AIWB_AUTHENTICATION_REQUIRED"
            }
            self.stderr(error_msg)
            return False
            
        return True

    def list_models(self):
        """List all available models for validation."""
        # Check AIWB authentication first
        if not self._check_aiwb_authentication():
            return
            
        # Use Basic Auth for nginx server communication
        with show_loading_status("Fetching model list..."):
            response, error = self._client.request(
                f"{self._model_validation_url}/models",
                "GET",
                auth=self._get_nginx_auth()
            )

        if error:
            self.stderr(response)
        else:
            self._format_model_list(response)

    def _format_model_list(self, response):
        """Format model list for pretty CLI output."""
        try:
            # Check output format
            if self.output == 'json':
                self.stdout(response)
                return
            
            # Pretty text format
            print(f"\n{'='*80}")
            print(f"🤖 AVAILABLE MODELS FOR VALIDATION")
            print(f"{'='*80}")
            
            total_models = 0
            
            for task_type, task_data in response.items():
                models = task_data.get('list_models', [])
                datasets = task_data.get('list_dataset', [])
                
                total_models += len(models)
                
                print(f"\n📋 {task_type.upper()}")
                print("-" * 60)
                
                # Create model-dataset pairs
                for i, (model, dataset) in enumerate(zip(models, datasets), 1):
                    print(f"   {i:2d}. 🔹 {model}")
                    print(f"       📊 Dataset: {dataset}")
                    if i < len(models):
                        print()
            
            print(f"\n{'='*80}")
            print(f"✨ Summary: {total_models} models available across {len(response)} task types")
            
            # Show task type summary
            task_summary = []
            for task_type, task_data in response.items():
                model_count = len(task_data.get('list_models', []))
                task_summary.append(f"{task_type} ({model_count})")
            
            print(f"📊 Task Types: {', '.join(task_summary)}")
            print(f"{'='*80}\n")
            
        except Exception as e:
            print(f"Error formatting model list: {e}")
            # Fallback to original output
            self.stdout(response)

    def queue_experiment(self, experiment_data):
        """Queue a model validation experiment."""
        # Check AIWB authentication first
        if not self._check_aiwb_authentication():
            return
            
        # Use Basic Auth for nginx server communication
        with show_loading_status("Queuing experiment..."):
            response, error = self._client.request(
                f"{self._model_validation_url}/experiments",
                "POST",
                json=experiment_data,
                auth=self._get_nginx_auth()
            )

        if error:
            self.stderr(response)
        else:
            self._format_queue_experiment_result(response, experiment_data)

    def _format_queue_experiment_result(self, response, experiment_data):
        """Format queue experiment result for pretty CLI output."""
        try:
            # Check output format
            if self.output == 'json':
                self.stdout(response)
                return
            
            # Pretty text format
            print(f"\n{'='*80}")
            print(f"🚀 EXPERIMENT QUEUED SUCCESSFULLY")
            print(f"{'='*80}")
            
            # Main experiment info
            print(f"✅ Experiment has been queued for processing!")
            print(f"\n📋 Experiment Details:")
            print("-" * 60)
            
            # Show key information
            run_id = response.get('run_id', 'N/A')
            user_id = response.get('user_id', 'N/A')
            model = response.get('model', 'N/A')
            created_at = response.get('created_at', 'N/A')
            
            print(f"   🆔 Run ID: {run_id}")
            print(f"   👤 User: {user_id}")
            print(f"   🤖 Model: {model}")
            print(f"   📅 Created: {created_at}")
            
            # Initialize run_state outside conditional block
            run_state = 'unknown'
            
            # Show backend response status
            backend_response = response.get('backend_response', {})
            if backend_response:
                print(f"\n🔍 Queue Status:")
                print("-" * 60)
                
                run_state = backend_response.get('run_state', 'unknown')
                
                # Status with emoji
                status_emoji = {
                    'queued': '📋',
                    'pending': '⏳',
                    'running': '🔄',
                    'success': '✅',
                    'failed': '❌',
                    'error': '❌'
                }.get(run_state.lower(), '❓')
                
                print(f"   Status: {status_emoji} {run_state.upper()}")
                
                logs = backend_response.get('logs', '')
                if logs:
                    print(f"   Logs: {logs}")
                else:
                    print(f"   Logs: No logs yet")
            
            # Show experiment configuration summary
            print(f"\n⚙️  Configuration Summary:")
            print("-" * 60)
            
            config_fields = [
                ('tenant_id', 'Tenant'),
                ('str_dataset', 'Dataset'),
                ('str_task', 'Task'),
                ('workflow_dag', 'Workflow'),
                ('int_subset_size', 'Subset Size'),
                ('int_batch_size', 'Batch Size'),
                ('compile_only', 'Compile Only'),
                ('use_configured', 'Use Configured')
            ]
            
            for field, label in config_fields:
                value = experiment_data.get(field)
                if value is not None:
                    if isinstance(value, bool):
                        value = "✅ Yes" if value else "❌ No"
                    print(f"   {label}: {value}")
            
            # Show deployment configuration if present
            deploy_config = experiment_data.get('dict_deploy_config', {})
            if deploy_config:
                print(f"\n📦 Deployment Configuration:")
                print("-" * 60)
                
                for category, settings in deploy_config.items():
                    if isinstance(settings, dict):
                        print(f"   {category.title()}:")
                        enabled_count = sum(1 for v in settings.values() if v)
                        total_count = len(settings)
                        print(f"      {enabled_count}/{total_count} options enabled")
                        
                        # Show enabled options
                        enabled_options = [k for k, v in settings.items() if v]
                        if enabled_options:
                            for option in enabled_options[:3]:  # Show first 3
                                print(f"         ✅ {option}")
                            if len(enabled_options) > 3:
                                print(f"         ... and {len(enabled_options) - 3} more")
                        print()
            
            # Show description if present
            description = experiment_data.get('str_description')
            if description:
                print(f"📝 Description: {description}")
            
            # Next steps
            print(f"\n💡 Next Steps:")
            print("-" * 60)
            print(f"   • Check status: aiwb model-validation experiment-status --run-id <run_id> --user-id <user_id> --tenant-id <tenant_id>")
            print(f"   • View results: aiwb model-validation experiment-result --tenant-id <tenant_id> --user-id <user_id> --run-id <run_id>")
            print(f"   • Download logs: aiwb model-validation experiment-logs --run-id <run_id>")
            
            print(f"\n{'='*80}")
            
            if run_state == 'queued':
                print(f"⏳ Your experiment is now in the queue and will start processing soon...")
            elif run_state == 'running':
                print(f"🔄 Your experiment is already running!")
            else:
                print(f"📊 Experiment status: {run_state}")
                
            print(f"{'='*80}\n")
            
        except Exception as e:
            print(f"Error formatting queue result: {e}")
            # Fallback to original output
            self.stdout(response)

    def get_experiment_status(self, request_data):
        """Get the status of an experiment."""
        # Check AIWB authentication first
        if not self._check_aiwb_authentication():
            return
            
        # Use Basic Auth for nginx server communication
        with show_loading_status("Fetching experiment status..."):
            response, error = self._client.request(
                f"{self._model_validation_url}/experiments/status",
                "POST",
                json=request_data,
                auth=self._get_nginx_auth()
            )

        if error:
            self.stderr(response)
        else:
            self._format_experiment_status(response)

    def watch_experiment_status(self, request_data, interval=30):
        """Watch experiment status with periodic updates for CLI usage."""
        
        if not self._check_aiwb_authentication():
            return False
        
        run_id = request_data.get('run_id')
        print(f"🔄 Watching experiment {run_id}... (Press Ctrl+C to stop)")
        print(f"⏰ Checking every {interval} seconds")
        print("=" * 80)
        
        iteration = 0
        
        try:
            while True:
                iteration += 1
                
                # Clear screen on subsequent iterations (optional)
                if iteration > 1 and self.output != 'json':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    print(f"🔄 Watching experiment {run_id}... (Press Ctrl+C to stop)")
                    print(f"⏰ Check #{iteration} - {time.strftime('%H:%M:%S')}")
                    print("=" * 80)
                
                # Get current status
                response, error = self._client.request(
                    f"{self._model_validation_url}/experiments/status",
                    "POST",
                    json=request_data,
                    auth=self._get_nginx_auth()
                )
                
                if error:
                    print(f"❌ Error checking status: {response}")
                    return False
                
                # Show current status
                self._format_experiment_status(response)
                
                # Check if experiment is complete
                status_data = response.get('status', {})
                if isinstance(status_data, dict):
                    # Look for status fields
                    for status_field in ['status', 'run_state', 'state']:
                        if status_field in status_data:
                            current_status = str(status_data.get(status_field)).lower()
                            
                            # Check if experiment is finished
                            if current_status in ['success', 'completed', 'failed', 'error', 'cancelled']:
                                if current_status in ['success', 'completed']:
                                    print(f"\n🎉 Experiment completed successfully!")
                                    print(f"✅ Final status: {current_status.upper()}")
                                else:
                                    print(f"\n💥 Experiment finished with status: {current_status.upper()}")
                                
                                print(f"\n💡 Next steps:")
                                print(f"   • View results: aiwb model-validation experiment-result --tenant-id {request_data['tenant_id']} --user-id {request_data['user_id']} --run-id {request_data['run_id']}")
                                print(f"   • Download logs: aiwb model-validation experiment-logs --run-id {request_data['run_id']}")
                                return True  # Exit successfully
                            
                            elif current_status in ['running', 'queued', 'pending']:
                                # Still running, continue watching
                                print(f"\n⏳ Still {current_status}... checking again in {interval} seconds")
                                break
                
                # Wait before next check
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Stopped watching experiment {run_id}")
            print(f"💡 You can check status again with:")
            print(f"   aiwb model-validation experiment-status --tenant-id {request_data['tenant_id']} --user-id {request_data['user_id']} --run-id {request_data['run_id']}")
            return True
        except Exception as e:
            print(f"\n❌ Error during watch: {e}")
            return False

    def _format_experiment_status(self, response):
        """Format experiment status for pretty CLI output."""
        try:
            # Check output format
            if self.output == 'json':
                self.stdout(response)
                return
            
            # Pretty text format
            print(f"\n{'='*80}")
            print(f"⚡ EXPERIMENT STATUS")
            print(f"{'='*80}")
            
            # Show request info
            request_info = response.get('request', {})
            if request_info:
                print(f"📋 Request Details:")
                print(f"   • Tenant ID: {request_info.get('tenant_id', 'N/A')}")
                print(f"   • User ID: {request_info.get('user_id', 'N/A')}")
                print(f"   • Run ID: {request_info.get('run_id', 'N/A')}")
            else:
                # Fallback - extract from response
                print(f"📋 Request Details:")
                print(f"   • Tenant ID: {response.get('tenant_id', 'N/A')}")
                print(f"   • User ID: {response.get('user_id', 'N/A')}")
                print(f"   • Run ID: {response.get('run_id', 'N/A')}")
            
            # Show timestamp
            checked_at = response.get('checked_at')
            if checked_at:
                print(f"   • Checked: {checked_at}")
            
            print(f"\n🔍 Status Information:")
            print("-" * 60)
            
            # Get the actual status data
            status_data = response.get('status', {})
            
            if isinstance(status_data, dict):
                # Handle different status response formats
                status_value = None
                
                # Check for different status field names
                for status_field in ['status', 'run_state', 'state']:
                    if status_field in status_data:
                        status_value = status_data.get(status_field)
                        break
                
                if status_value:
                    # Status with emoji
                    status_emoji = {
                        'success': '✅',
                        'completed': '✅', 
                        'running': '🔄',
                        'pending': '⏳',
                        'queued': '📋',
                        'failed': '❌',
                        'error': '❌',
                        'cancelled': '🚫',
                        'unknown': '❓'
                    }.get(str(status_value).lower(), '❓')
                    
                    print(f"   Status: {status_emoji} {str(status_value).upper()}")
                
                # Show all fields with nice formatting
                for key, value in status_data.items():
                    if key.lower() in ['status', 'run_state', 'state']:
                        continue  # Already shown above
                    
                    display_key = key.replace('_', ' ').title()
                    
                    # Special handling for empty/null values
                    if value == "" or value is None:
                        display_value = "None"
                    elif key.lower() == 'logs' and not value:
                        display_value = "No logs available"
                    else:
                        display_value = str(value)
                    
                    print(f"   {display_key}: {display_value}")
            else:
                # Status is a simple string or other type
                print(f"   Status: {status_data}")
            
            print(f"\n{'='*80}")
            
            # Quick status summary
            status_value = None
            if isinstance(status_data, dict):
                # Check for different status field names
                for status_field in ['status', 'run_state', 'state']:
                    if status_field in status_data:
                        status_value = str(status_data.get(status_field)).lower()
                        break
            
            if status_value:
                if status_value in ['success', 'completed']:
                    print(f"🎉 Experiment completed successfully!")
                elif status_value == 'running':
                    print(f"⚙️  Experiment is currently running...")
                elif status_value in ['pending', 'queued']:
                    print(f"⏳ Experiment is waiting to start...")
                elif status_value in ['failed', 'error']:
                    print(f"💥 Experiment has failed!")
                else:
                    print(f"📊 Current status: {status_value}")
            else:
                print(f"📊 Status information retrieved")
            
        except Exception as e:
            print(f"Error formatting status: {e}")
            # Fallback to original output
            self.stdout(response)

    def get_experiment_results(self, request_data):
        """Get the results of experiments."""
        # Check AIWB authentication first
        if not self._check_aiwb_authentication():
            return
            
        # Use Basic Auth for nginx server communication
        with show_loading_status("Fetching experiment results..."):
            response, error = self._client.request(
                f"{self._model_validation_url}/experiments/results",
                "POST",
                json=request_data,
                auth=self._get_nginx_auth()
            )

        if error:
            self.stderr(response)
        else:
            # Pretty format the response
            self._format_experiment_results(response)

    def _format_experiment_results(self, response):
        """Format experiment results for pretty CLI output."""
        try:
            # Parse the results string if it's a JSON string
            results_data = response.get('results', [])
            if isinstance(results_data, str):
                results_data = json.loads(results_data)
            
            # Check output format
            if self.output == 'json':
                self.stdout(response)
                return
            
            # Pretty text format
            print(f"\n{'='*80}")
            print(f"🧪 EXPERIMENT RESULTS")
            print(f"{'='*80}")
            
            # Show request summary
            request_info = response.get('request', {})
            print(f"📋 Request Summary:")
            print(f"   • Tenants: {', '.join(request_info.get('list_tenant_id', []))}")
            print(f"   • Users: {', '.join(request_info.get('list_user_id', []))}")
            print(f"   • Run IDs: {', '.join(request_info.get('list_run_ids', []))}")
            print(f"   • Top N: {request_info.get('top_n', 'N/A')}")
            print(f"   • Retrieved: {response.get('retrieved_at', 'N/A')}")
            
            print(f"\n📊 Results ({len(results_data)} experiment{'s' if len(results_data) != 1 else ''}):")
            print("-" * 80)
            
            for i, result in enumerate(results_data, 1):
                print(f"\n🔬 Experiment #{i}")
                print(f"   Run ID: {result.get('run_id', 'N/A')}")
                print(f"   Model: {result.get('str_model', 'N/A')}")
                print(f"   Dataset: {result.get('str_dataset', 'N/A')}")
                print(f"   Task: {result.get('str_task', 'N/A')}")
                print(f"   Status: {'✅' if result.get('status') == 'success' else '❌'} {result.get('status', 'N/A')}")
                print(f"   Time: {result.get('time', 'N/A')}")
                print(f"   Subset Size: {result.get('int_subset_size', 'N/A')}")
                print(f"   Batch Size: {result.get('int_batch_size', 'N/A')}")
                
                # Parse and display deployment config
                deploy_config = result.get('dict_deploy_config', '{}')
                if isinstance(deploy_config, str):
                    try:
                        deploy_config = json.loads(deploy_config)
                        print(f"   📦 Deployment Config:")
                        for category, settings in deploy_config.items():
                            print(f"      {category.title()}:")
                            for setting, enabled in settings.items():
                                status = "✅" if enabled else "❌"
                                print(f"         {status} {setting}")
                    except json.JSONDecodeError:
                        print(f"   📦 Deployment Config: {deploy_config}")
                
                # Parse and display metrics
                metrics = result.get('dict_metrics', '{}')
                if isinstance(metrics, str):
                    try:
                        metrics = json.loads(metrics)
                        if metrics:
                            print(f"   📈 Performance Metrics:")
                            for metric_type, values in metrics.items():
                                print(f"      {metric_type}:")
                                if isinstance(values, dict):
                                    for key, value in values.items():
                                        # Add units based on metric patterns
                                        formatted_value = self._format_metric_with_units(key, value)
                                        print(f"         • {key}: {formatted_value}")
                                else:
                                    print(f"         • {values}")
                    except json.JSONDecodeError:
                        print(f"   📈 Metrics: {metrics}")
                
                # Parse and display tags/description
                tags = result.get('tags', '{}')
                if isinstance(tags, str):
                    try:
                        tags = json.loads(tags)
                        if tags and tags.get('description'):
                            print(f"   📝 Description: {tags.get('description')}")
                    except json.JSONDecodeError:
                        if tags:
                            print(f"   📝 Tags: {tags}")
                
                if i < len(results_data):
                    print("-" * 40)
            
            print(f"\n{'='*80}")
            print(f"✨ Summary: {len(results_data)} experiment{'s' if len(results_data) != 1 else ''} found")
            print(f"{'='*80}\n")
            
        except Exception as e:
            print(f"Error formatting results: {e}")
            # Fallback to original output
            self.stdout(response)

    def download_experiment_logs(self, run_id, output_file):
        """Download experiment logs as a zip file."""
        # Check AIWB authentication first
        if not self._check_aiwb_authentication():
            return
            
        # Use Basic Auth for nginx server communication
        with show_loading_status(f"Downloading logs for {run_id}..."):
            try:
                # Make direct request to handle file download
                response = requests.get(
                    f"{self._model_validation_url}/api/v2/download-logs/{run_id}",
                    auth=self._get_nginx_auth(),
                    headers={"accept": "application/json"},
                    stream=True
                )
                
                if response.status_code == 200:
                    with open(output_file, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    result = {
                        "success": True,
                        "message": f"Logs downloaded successfully to {output_file}",
                        "file_path": output_file,
                        "run_id": run_id
                    }
                    self._format_logs_download_result(result, output_file)
                else:
                    error_result = {
                        "success": False,
                        "message": f"Failed to download logs. HTTP {response.status_code}: {response.text}",
                        "code": response.status_code
                    }
                    self.stderr(error_result)
                    
            except Exception as e:
                error_result = {
                    "success": False,
                    "message": f"Error downloading logs: {str(e)}",
                    "code": "DOWNLOAD_ERROR"
                }
                self.stderr(error_result)

    def _format_logs_download_result(self, result, output_file):
        """Format logs download result for pretty CLI output."""
        try:
            # Check output format
            if self.output == 'json':
                self.stdout(result)
                return
            
            # Pretty text format
            print(f"\n{'='*80}")
            print(f"📦 EXPERIMENT LOGS DOWNLOADED")
            print(f"{'='*80}")
            
            print(f"✅ Success! Logs downloaded successfully")
            print(f"📁 File: {output_file}")
            print(f"🔬 Run ID: {result['run_id']}")
            
            # Get file size
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"📊 File Size: {self._format_file_size(file_size)}")
                
                # Try to get zip info
                try:
                    with zipfile.ZipFile(output_file, 'r') as zip_file:
                        file_list = zip_file.filelist
                        total_files = len(file_list)
                        total_uncompressed = sum(f.file_size for f in file_list)
                        
                        print(f"📋 Contents: {total_files} log files")
                        print(f"📈 Uncompressed Size: {self._format_file_size(total_uncompressed)}")
                        
                        # Show some sample files
                        print(f"\n📝 Sample Log Files:")
                        print("-" * 60)
                        
                        # Group files by type and show summary
                        file_types = {}
                        for file_info in file_list[:10]:  # Show first 10 files
                            name = file_info.filename
                            size = file_info.file_size
                            
                            # Extract log type from filename
                            if '/' in name:
                                log_type = name.split('/')[-1].replace('.log', '')
                            else:
                                log_type = name.replace('.log', '')
                            
                            file_types[log_type] = file_types.get(log_type, 0) + 1
                            
                            print(f"   📄 {name}")
                            print(f"      Size: {self._format_file_size(size)}")
                            if size > 100:  # Only mention if there's actual content
                                print(f"      📊 Contains log data")
                            else:
                                print(f"      📭 Empty/minimal content")
                            print()
                        
                        if total_files > 10:
                            print(f"   ... and {total_files - 10} more files")
                        
                except zipfile.BadZipFile:
                    print("⚠️  Warning: Downloaded file is not a valid zip archive")
                except Exception as e:
                    print(f"⚠️  Warning: Could not read zip contents: {e}")
            
            print(f"\n💡 Tips:")
            print(f"   • Use 'aiwb model-validation view-logs --zip-file {output_file}' to view log contents")
            print(f"   • Or you can extract with 'unzip {output_file}' to access individual files")
            
            print(f"\n{'='*80}\n")
            
        except Exception as e:
            print(f"Error formatting download result: {e}")
            # Fallback to original output
            self.stdout(result)

    def _format_file_size(self, size_bytes):
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    def _format_metric_with_units(self, metric_name, value):
        """Add appropriate units to performance metrics based on naming patterns."""
        metric_lower = metric_name.lower()
        value_str = str(value)
        
        # Latency metrics - typically in milliseconds
        if any(keyword in metric_lower for keyword in ['latency', 'delay', 'inference_time', 'processing_time']):
            if '(' in value_str and ')' in value_str:
                # Handle format like "3.77 ( 2.12/ 1.54)"
                return f"{value_str} ms"
            else:
                return f"{value} ms"
        
        # Throughput/Performance metrics - could be FPS, TOPS, or scores
        elif any(keyword in metric_lower for keyword in ['throughput', 'fps', 'frames', 'performance', 'tvm', 'cnnip', 'dsp']):
            if '/' in value_str and not '(' in value_str:
                # Handle format like "88.0/98.0" - likely performance scores or FPS
                return f"{value_str} (score/fps)"
            else:
                return f"{value} fps"
        
        # Power metrics
        elif any(keyword in metric_lower for keyword in ['power', 'energy', 'watts']):
            return f"{value} W"
        
        # Memory metrics
        elif any(keyword in metric_lower for keyword in ['memory', 'ram', 'mem']):
            return f"{value} MB"
        
        # Accuracy metrics - typically percentages
        elif any(keyword in metric_lower for keyword in ['accuracy', 'acc', 'precision', 'recall']):
            return f"{value}%"
        
        # TOPS/GOPS metrics
        elif any(keyword in metric_lower for keyword in ['tops', 'gops', 'operations']):
            return f"{value} TOPS"
        
        # Default - return as-is but note units are unclear
        else:
            return f"{value} (units unknown)"

    def view_experiment_logs(self, zip_file, log_file=None, list_files=False, max_lines=50):
        """View contents of experiment logs from a zip file."""
        try:
            if not os.path.exists(zip_file):
                error_result = {
                    "success": False,
                    "message": f"Zip file not found: {zip_file}",
                    "code": "FILE_NOT_FOUND"
                }
                self.stderr(error_result)
                return
            
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                if list_files:
                    # List all files in the zip
                    print(f"\n{'='*80}")
                    print(f"📦 LOG FILES IN {os.path.basename(zip_file)}")
                    print(f"{'='*80}")
                    
                    for i, filename in enumerate(file_list, 1):
                        file_info = zip_ref.getinfo(filename)
                        size = file_info.file_size
                        print(f"{i:2d}. 📄 {filename}")
                        print(f"     Size: {self._format_file_size(size)}")
                        if size > 100:
                            print(f"     📊 Contains log data")
                        else:
                            print(f"     📭 Empty/minimal content")
                        print()
                    
                    print(f"{'='*80}")
                    print(f"💡 Use --log-file <filename> to view specific log content")
                    print(f"{'='*80}\n")
                    return
                
                if log_file:
                    # View specific log file
                    if log_file not in file_list:
                        # Try to find partial matches
                        matches = [f for f in file_list if log_file in f]
                        if matches:
                            if len(matches) == 1:
                                log_file = matches[0]
                                print(f"📝 Found matching file: {log_file}")
                            else:
                                print(f"❓ Multiple matches found:")
                                for i, match in enumerate(matches, 1):
                                    print(f"   {i}. {match}")
                                print(f"Please specify the exact filename.")
                                return
                        else:
                            error_result = {
                                "success": False,
                                "message": f"Log file '{log_file}' not found in zip archive",
                                "code": "LOG_FILE_NOT_FOUND"
                            }
                            self.stderr(error_result)
                            return
                    
                    # Read and display the log file
                    with zip_ref.open(log_file) as log_content:
                        content = log_content.read().decode('utf-8', errors='ignore')
                        
                        print(f"\n{'='*80}")
                        print(f"📄 LOG FILE: {log_file}")
                        print(f"{'='*80}")
                        
                        lines = content.split('\n')
                        total_lines = len(lines)
                        
                        print(f"📊 File Info:")
                        print(f"   • Size: {self._format_file_size(len(content.encode('utf-8')))}")
                        print(f"   • Lines: {total_lines}")
                        
                        if total_lines > max_lines:
                            print(f"   • Showing first {max_lines} lines (use --max-lines to see more)")
                        
                        print(f"\n📝 Content:")
                        print("-" * 80)
                        
                        for i, line in enumerate(lines[:max_lines], 1):
                            if line.strip():  # Only show non-empty lines
                                print(f"{i:4d} | {line}")
                        
                        if total_lines > max_lines:
                            print(f"...")
                            print(f"({total_lines - max_lines} more lines)")
                        
                        print(f"\n{'='*80}\n")
                else:
                    # Show summary and suggest what to do
                    print(f"\n{'='*80}")
                    print(f"📦 EXPERIMENT LOGS: {os.path.basename(zip_file)}")
                    print(f"{'='*80}")
                    
                    print(f"📊 Archive contains {len(file_list)} log files")
                    
                    # Show files with actual content
                    content_files = []
                    empty_files = []
                    
                    for filename in file_list:
                        file_info = zip_ref.getinfo(filename)
                        if file_info.file_size > 100:  # Has meaningful content
                            content_files.append((filename, file_info.file_size))
                        else:
                            empty_files.append(filename)
                    
                    if content_files:
                        print(f"\n📝 Files with content ({len(content_files)}):")
                        for filename, size in sorted(content_files, key=lambda x: x[1], reverse=True)[:10]:
                            print(f"   📄 {filename} ({self._format_file_size(size)})")
                        
                        if len(content_files) > 10:
                            print(f"   ... and {len(content_files) - 10} more")
                    
                    if empty_files:
                        print(f"\n📭 Empty/minimal files ({len(empty_files)}):")
                        for filename in empty_files[:5]:
                            print(f"   📄 {filename}")
                        if len(empty_files) > 5:
                            print(f"   ... and {len(empty_files) - 5} more")
                    
                    print(f"\n💡 Commands:")
                    print(f"   • List all files: --list-files")
                    print(f"   • View specific log: --log-file <filename>")
                    if content_files:
                        largest_file = content_files[0][0]
                        print(f"   • View largest log: --log-file '{largest_file}'")
                    
                    print(f"\n{'='*80}\n")
                    
        except zipfile.BadZipFile:
            error_result = {
                "success": False,
                "message": f"Invalid zip file: {zip_file}",
                "code": "INVALID_ZIP"
            }
            self.stderr(error_result)
        except Exception as e:
            error_result = {
                "success": False,
                "message": f"Error reading logs: {str(e)}",
                "code": "READ_ERROR"
            }
            self.stderr(error_result)