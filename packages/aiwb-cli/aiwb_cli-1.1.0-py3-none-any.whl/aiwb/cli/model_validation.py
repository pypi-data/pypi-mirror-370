# aiwb/cli/model_validation.py

import click
import json
import sys
import time

from .cli import CLIGroup


@click.group(cls=CLIGroup, help="Commands to manage model validation.")
@click.pass_obj
def model_validation(client):
    pass


@model_validation.command(name="model-list", help="List available models for validation.")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
@click.pass_obj
def model_list(client, output):
    """List all available models for validation grouped by task type."""
    model = client.model("model_validation", output=output)
    model.list_models()


@model_validation.command(name="queue-experiment", help="Queue a model validation experiment.")
@click.option("--tenant-id", type=str, help="Tenant ID (e.g., 'mlops')")
@click.option("--user-id", type=str, help="User ID (e.g., 'aiwb')")
@click.option("--model", "str_model", type=str, help="Model name (e.g., 'ResNet50')")
@click.option("--dataset", "str_dataset", type=str, help="Dataset name (e.g., 'Imagenet')")
@click.option("--task", "str_task", type=str, help="Task type (e.g., 'classification')")
@click.option("--workflow-dag", type=str, help="Workflow DAG (e.g., 'NNPerf_v2.0.1')")
@click.option("--subset-size", "int_subset_size", type=int, help="Subset size (e.g., 50)")
@click.option("--batch-size", "int_batch_size", type=int, help="Batch size (e.g., 0)")
@click.option("--description", "str_description", type=str, help="Experiment description")
@click.option("--compile-only", is_flag=True, help="Compile only mode")
@click.option("--use-configured", is_flag=True, help="Use configured settings")
@click.option("--deploy-config", type=str, help="Deploy config as JSON string")
@click.option("--json-file", type=click.File('r'), help="Path to JSON file containing experiment configuration")
@click.option("--json", "json_string", type=str, help="JSON string containing experiment configuration")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
@click.pass_obj
def queue_experiment(client, output, json_file, json_string, deploy_config, **kwargs):
    """Queue a model validation experiment.
    
    You can provide experiment configuration in three ways:
    1. Individual options (--tenant-id, --model, etc.)
    2. JSON file (--json-file path/to/config.json)
    3. JSON string (--json '{"tenant_id": "mlops", ...}')
    
    JSON input takes precedence over individual options.
    """
    
    # Handle JSON input
    experiment_data = None
    
    if json_file:
        try:
            experiment_data = json.load(json_file)
        except json.JSONDecodeError as e:
            click.echo(f"Error: Invalid JSON in file: {e}", err=True)
            sys.exit(1)
    elif json_string:
        try:
            experiment_data = json.loads(json_string)
        except json.JSONDecodeError as e:
            click.echo(f"Error: Invalid JSON string: {e}", err=True)
            sys.exit(1)
    else:
        # Build from individual options
        experiment_data = {}
        
        # Map CLI options to API fields
        option_mapping = {
            'tenant_id': kwargs.get('tenant_id'),
            'user_id': kwargs.get('user_id'),
            'str_model': kwargs.get('str_model'),
            'str_dataset': kwargs.get('str_dataset'),
            'str_task': kwargs.get('str_task'),
            'workflow_dag': kwargs.get('workflow_dag'),
            'int_subset_size': kwargs.get('int_subset_size'),
            'int_batch_size': kwargs.get('int_batch_size'),
            'str_description': kwargs.get('str_description'),
            'compile_only': kwargs.get('compile_only', False),
            'use_configured': kwargs.get('use_configured', False),
        }
        
        # Only include non-None values
        for key, value in option_mapping.items():
            if value is not None:
                experiment_data[key] = value
        
        # Handle deploy_config separately as it needs JSON parsing
        if deploy_config:
            try:
                experiment_data['dict_deploy_config'] = json.loads(deploy_config)
            except json.JSONDecodeError as e:
                click.echo(f"Error: Invalid JSON in --deploy-config: {e}", err=True)
                sys.exit(1)
    
    if not experiment_data:
        click.echo("Error: No experiment configuration provided. Use individual options, --json-file, or --json.", err=True)
        sys.exit(1)
    
    model = client.model("model_validation", output=output)
    model.queue_experiment(experiment_data)


@model_validation.command(name="experiment-status", help="Get the status of an experiment.")
@click.option("--tenant-id", type=str, help="Tenant ID (e.g., 'mlops')")
@click.option("--user-id", type=str, help="User ID (e.g., 'aiwb')")
@click.option("--run-id", type=str, help="Run ID (e.g., 'aiwb_20250708_123456')")
@click.option("--watch", is_flag=True, help="Keep watching until experiment completes (auto-refresh)")
@click.option("--interval", type=int, default=30, help="Polling interval in seconds for watch mode (default: 30)")
@click.option("--json-file", type=click.File('r'), help="Path to JSON file containing status request")
@click.option("--json", "json_string", type=str, help="JSON string containing status request")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
@click.pass_obj
def experiment_status(client, output, watch, interval, json_file, json_string, **kwargs):
    """Get the status of a model validation experiment.
    
    Examples:
        # Check status once
        aiwb model-validation experiment-status --tenant-id mlops --user-id faisal --run-id faisal_20250724_024654
        
        # Watch until completion (auto-refresh every 30 seconds)
        aiwb model-validation experiment-status --tenant-id mlops --user-id faisal --run-id faisal_20250724_024654 --watch
        
        # Watch with custom interval (every 10 seconds)
        aiwb model-validation experiment-status --tenant-id mlops --user-id faisal --run-id faisal_20250724_024654 --watch --interval 10
        
        # Using JSON file
        aiwb model-validation experiment-status --json-file status_request.json --watch
    """
    
    # Handle JSON input
    request_data = None
    
    if json_file:
        try:
            request_data = json.load(json_file)
        except json.JSONDecodeError as e:
            click.echo(f"Error: Invalid JSON in file: {e}", err=True)
            sys.exit(1)
    elif json_string:
        try:
            request_data = json.loads(json_string)
        except json.JSONDecodeError as e:
            click.echo(f"Error: Invalid JSON string: {e}", err=True)
            sys.exit(1)
    else:
        # Build from individual options
        tenant_id = kwargs.get('tenant_id')
        user_id = kwargs.get('user_id')
        run_id = kwargs.get('run_id')
        
        # Validate required individual options only when no JSON provided
        if not tenant_id:
            click.echo("Error: Missing option '--tenant-id'.", err=True)
            sys.exit(1)
        if not user_id:
            click.echo("Error: Missing option '--user-id'.", err=True)
            sys.exit(1)
        if not run_id:
            click.echo("Error: Missing option '--run-id'.", err=True)
            sys.exit(1)
            
        request_data = {
            'tenant_id': tenant_id,
            'user_id': user_id,
            'run_id': run_id
        }
    
    # Validate that we have the required fields in the final request_data
    required_fields = ['tenant_id', 'user_id', 'run_id']
    for field in required_fields:
        if not request_data.get(field):
            click.echo(f"Error: Missing required field '{field}' in request data.", err=True)
            sys.exit(1)
    
    model = client.model("model_validation", output=output)
    
    if watch:
        # Watch mode - use the new public method from ModelValidation class
        try:
            success = model.watch_experiment_status(request_data, interval)
            if not success:
                sys.exit(1)
        except KeyboardInterrupt:
            click.echo(f"\n\n🛑 Stopped watching experiment {request_data.get('run_id')}")
            click.echo(f"💡 You can check status again with:")
            click.echo(f"   aiwb model-validation experiment-status --tenant-id {request_data['tenant_id']} --user-id {request_data['user_id']} --run-id {request_data['run_id']}")
        except Exception as e:
            click.echo(f"\n❌ Error during watch: {e}", err=True)
            sys.exit(1)
    else:
        # Single check mode
        model.get_experiment_status(request_data)


@model_validation.command(name="experiment-result", help="Get the results of experiments.")
@click.option("--run-id", type=str, help="Single run ID (e.g., 'faisal_20250724_024654')")
@click.option("--user-id", type=str, help="Single user ID (e.g., 'faisal')")
@click.option("--tenant-id", type=str, help="Single tenant ID (e.g., 'mlops')")
@click.option("--tenant-ids", type=str, help="Comma-separated list of tenant IDs (e.g., 'mlops,tenant2')")
@click.option("--user-ids", type=str, help="Comma-separated list of user IDs (e.g., 'faisal,user2')")
@click.option("--run-ids", type=str, help="Comma-separated list of run IDs (e.g., 'run1,run2')")
@click.option("--top-n", type=int, default=10, help="Number of top results to return (default: 10)")
@click.option("--json-file", type=click.File('r'), help="Path to JSON file containing result request")
@click.option("--json", "json_string", type=str, help="JSON string containing result request")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
@click.pass_obj
def experiment_result(client, output, run_id, user_id, tenant_id, json_file, json_string, **kwargs):
    """Get the results of model validation experiments.
    
    Examples:
        # Single experiment (simple)
        aiwb model-validation experiment-result --tenant-id mlops --user-id faisal --run-id faisal_20250724_024654
        
        # Multiple experiments (advanced)
        aiwb model-validation experiment-result --tenant-ids "mlops,tenant2" --user-ids "faisal,user2" --run-ids "run1,run2"
        
        # Using JSON file
        aiwb model-validation experiment-result --json-file results_request.json
    """
    
    # Handle JSON input first
    request_data = None
    
    if json_file:
        try:
            request_data = json.load(json_file)
        except json.JSONDecodeError as e:
            click.echo(f"Error: Invalid JSON in file: {e}", err=True)
            sys.exit(1)
    elif json_string:
        try:
            request_data = json.loads(json_string)
        except json.JSONDecodeError as e:
            click.echo(f"Error: Invalid JSON string: {e}", err=True)
            sys.exit(1)
    else:
        # Handle both singular and plural options
        request_data = {}
        
        # Determine tenant IDs
        if tenant_id:
            # Single tenant
            request_data['list_tenant_id'] = [tenant_id]
        elif kwargs.get('tenant_ids'):
            # Multiple tenants
            request_data['list_tenant_id'] = [t.strip() for t in kwargs.get('tenant_ids').split(',')]
        else:
            click.echo("Error: Either --tenant-id or --tenant-ids must be provided.", err=True)
            sys.exit(1)
        
        # Determine user IDs
        if user_id:
            # Single user
            request_data['list_user_id'] = [user_id]
        elif kwargs.get('user_ids'):
            # Multiple users
            request_data['list_user_id'] = [u.strip() for u in kwargs.get('user_ids').split(',')]
        else:
            click.echo("Error: Either --user-id or --user-ids must be provided.", err=True)
            sys.exit(1)
        
        # Determine run IDs
        if run_id:
            # Single run
            request_data['list_run_ids'] = [run_id]
        elif kwargs.get('run_ids'):
            # Multiple runs
            request_data['list_run_ids'] = [r.strip() for r in kwargs.get('run_ids').split(',')]
        else:
            click.echo("Error: Either --run-id or --run-ids must be provided.", err=True)
            sys.exit(1)
        
        request_data['top_n'] = kwargs.get('top_n', 10)
    
    if not request_data:
        click.echo("Error: No request parameters provided. Use individual options, --json-file, or --json.", err=True)
        sys.exit(1)
    
    model = client.model("model_validation", output=output)
    model.get_experiment_results(request_data)

@model_validation.command(name="experiment-logs", help="Download experiment logs.")
@click.option("--run-id", type=str, required=True, help="Run ID (e.g., 'aiwb_20250708_123456')")
@click.option("--output-file", type=str, help="Output file path (default: {run_id}_logs.zip)")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
@click.pass_obj
def experiment_logs(client, output, run_id, output_file):
    """Download experiment logs as a zip file.
    
    Example:
        aiwb model-validation experiment-logs --run-id aiwb_20250708_123456
        aiwb model-validation experiment-logs --run-id aiwb_20250708_123456 --output-file my_logs.zip
    """
    
    if not output_file:
        output_file = f"{run_id}_logs.zip"
    
    model = client.model("model_validation", output=output)
    model.download_experiment_logs(run_id, output_file)

@model_validation.command(name="view-logs", help="View experiment log file contents.")
@click.option("--zip-file", type=str, required=True, help="Path to the downloaded logs zip file")
@click.option("--log-file", type=str, help="Specific log file to view (e.g., 'NNPerf_v2.0.1/inference_branch.log')")
@click.option("--list-files", is_flag=True, help="List all files in the zip archive")
@click.option("--max-lines", type=int, default=50, help="Maximum lines to display (default: 50)")
@click.pass_obj
def view_logs(client, zip_file, log_file, list_files, max_lines):
    """View contents of experiment log files from a downloaded zip archive.
    
    Examples:
        # Show log summary
        aiwb model-validation view-logs --zip-file faisal_20250724_005444_logs.zip
        
        # List all files
        aiwb model-validation view-logs --zip-file faisal_20250724_005444_logs.zip --list-files
        
        # View specific log
        aiwb model-validation view-logs --zip-file faisal_20250724_005444_logs.zip --log-file "NNPerf_v2.0.1/inference_branch.log"
    """
    
    model = client.model("model_validation")
    model.view_experiment_logs(zip_file, log_file, list_files, max_lines)