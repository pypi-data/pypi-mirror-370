"""
Configuration management for bootstrap workflows.
"""

import yaml
from typing import Dict, Any
from ..utils import console

def load_workflow_config(config_path: str) -> Dict[str, Any]:
    """Load workflow configuration from YAML file."""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Validate required fields
        required_fields = ['name', 'nodes']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        return config
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Workflow configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML format: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to load configuration: {str(e)}")

def create_sample_workflow_config(output_path: str = "workflow-example.yml"):
    """Create a sample workflow configuration file."""
    sample_config = {
        'name': 'Sample Calimero Workflow',
        'description': 'A sample workflow that demonstrates the bootstrap functionality with dynamic value capture',
        'stop_all_nodes': True,  # Stop all existing nodes before starting
        'wait_timeout': 60,  # Wait up to 60 seconds for nodes to be ready
        
        'nodes': {
            'count': 2,
            'prefix': 'calimero-node',
            'chain_id': 'testnet-1',
            'image': 'ghcr.io/calimero-network/merod:6a47604'
        },
        
        'steps': [
            {
                'name': 'Install Application on Node 1',
                'type': 'install_application',
                'node': 'calimero-node-1',
                'path': './kv_store.wasm',
                'dev': True
            },
            {
                'name': 'Create Context on Node 1',
                'type': 'create_context',
                'node': 'calimero-node-1',
                'application_id': '{{install.calimero-node-1}}'
            },
            {
                'name': 'Create Identity on Node 2',
                'type': 'create_identity',
                'node': 'calimero-node-2'
            },
            {
                'name': 'Wait for Identity Creation',
                'type': 'wait',
                'seconds': 5
            },
            {
                'name': 'Invite Node 2 from Node 1',
                'type': 'invite_identity',
                'node': 'calimero-node-1',
                'context_id': '{{context.calimero-node-1}}',
                'grantee_id': '{{identity.calimero-node-2}}',
                'granter_id': '{{context.calimero-node-1.memberPublicKey}}',
                'capability': 'member'
            },
            {
                'name': 'Join Context from Node 2',
                'type': 'join_context',
                'node': 'calimero-node-2',
                'context_id': '{{context.calimero-node-1}}',
                'invitee_id': '{{identity.calimero-node-2}}',
                'invitation': '{{invite.calimero-node-1_identity.calimero-node-2}}'
            },
            {
                'name': 'Execute Contract Call Example',
                'type': 'call',
                'node': 'calimero-node-1',
                'context_id': '{{context.calimero-node-1}}',
                'method': 'set',
                'args': {'key': 'hello', 'value': 'world'}
            }
        ]
    }
    
    try:
        with open(output_path, 'w') as file:
            yaml.dump(sample_config, file, default_flow_style=False, indent=2)
        
        console.print(f"[green]✓ Sample workflow configuration created: {output_path}[/green]")
        console.print("[yellow]Note: Dynamic values are automatically captured and used with placeholders[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Failed to create sample configuration: {str(e)}[/red]")
