"""
Join context step executor.
"""

from typing import Dict, Any
from ...utils import get_node_rpc_url, console
from ...join import join_context_via_admin_api
from .base import BaseStep


class JoinContextStep(BaseStep):
    """Execute a join context step."""
    
    def _get_exportable_variables(self):
        """
        Define which variables this step can export.
        
        Available variables from join_context API response:
        - contextId: ID of the context joined (this is what the API actually returns)
        - memberPublicKey: Public key of the member who joined
        """
        return [
            ('contextId', 'join_context_id_{node_name}_{invitee_id}', 'ID of the context joined'),
            ('memberPublicKey', 'join_member_public_key_{node_name}_{invitee_id}', 'Public key of the member who joined'),
        ]
    
    async def execute(self, workflow_results: Dict[str, Any], dynamic_values: Dict[str, Any]) -> bool:
        node_name = self.config['node']
        context_id = self._resolve_dynamic_value(self.config['context_id'], workflow_results, dynamic_values)
        invitee_id = self._resolve_dynamic_value(self.config['invitee_id'], workflow_results, dynamic_values)
        invitation = self._resolve_dynamic_value(self.config['invitation'], workflow_results, dynamic_values)
        
        # Validate export configuration
        if not self._validate_export_config():
            console.print(f"[yellow]⚠️  Join step export configuration validation failed[/yellow]")
        
        # Debug: Show resolved values
        console.print(f"[blue]Debug: Resolved values for join step:[/blue]")
        console.print(f"  context_id: {context_id}")
        console.print(f"  invitee_id: {invitee_id}")
        console.print(f"  invitation: {invitation[:50] if isinstance(invitation, str) and len(invitation) > 50 else invitation}")
        console.print(f"  invitation type: {type(invitation)}")
        console.print(f"  invitation length: {len(invitation) if isinstance(invitation, str) else 'N/A'}")
        
        # Get node RPC URL
        try:
            from ...manager import CalimeroManager
            manager = CalimeroManager()
            rpc_url = get_node_rpc_url(node_name, manager)
        except Exception as e:
            console.print(f"[red]Failed to get RPC URL for node {node_name}: {str(e)}[/red]")
            return False
        
        # Execute join
        console.print(f"[blue]About to call join function...[/blue]")
        result = await join_context_via_admin_api(
            rpc_url, context_id, invitee_id, invitation
        )
        console.print(f"[blue]Join function returned: {result}[/blue]")
        
        # Log detailed API response
        console.print(f"[cyan]🔍 Join API Response for {node_name}:[/cyan]")
        console.print(f"  Success: {result.get('success')}")
        console.print(f"  Data: {result.get('data')}")
        console.print(f"  Endpoint: {result.get('endpoint', 'N/A')}")
        console.print(f"  Payload Format: {result.get('payload_format', 'N/A')}")
        if not result.get('success'):
            console.print(f"  Error: {result.get('error')}")
            if 'tried_payloads' in result:
                console.print(f"  Tried Payloads: {result['tried_payloads']}")
            if 'errors' in result:
                console.print(f"  Detailed Errors: {result['errors']}")
        
        if result['success']:
            # Check if the JSON-RPC response contains an error
            if self._check_jsonrpc_error(result['data']):
                return False
            
            # Store result for later use
            step_key = f"join_{node_name}_{invitee_id}"
            workflow_results[step_key] = result['data']
            
            # Export variables using the new standardized approach
            # Note: We need to handle the invitee_id dynamically for the export
            self._export_variables(result['data'], node_name, dynamic_values)
            
            return True
        else:
            console.print(f"[red]Join failed: {result.get('error', 'Unknown error')}[/red]")
            return False
