"""
Administrative functionality for the Astronomy TAP Client.
"""
import requests
from typing import Dict, List, Optional, Any

from ..exceptions import (
    AuthenticationError, ResourceNotFoundError, PermissionDeniedError, 
    ValidationError
)
from ..utils import handle_response_errors, format_permission
from ..models.user import User, Role, SchemaPermission, TablePermission, RolePermissions


class AdminEndpoint:
    """
    Handles administrative operations (superuser/staff only).
    """
    
    def __init__(self, base_url: str, auth_manager):
        """
        Initialize the Admin endpoint.
        
        Args:
            base_url: The base URL of the API server
            auth_manager: Authentication manager providing auth headers
        """
        self.base_url = base_url.rstrip('/')
        self.auth_manager = auth_manager
    
    def create_role(self, name: str, description: Optional[str] = None, **kwargs) -> Role:
        """
        Create a new role (superuser only).
        
        Args:
            name: Role name
            description: Optional role description
            **kwargs: Additional keyword arguments to pass to the request (e.g., verify=False)
            
        Returns:
            The newly created Role object
            
        Raises:
            AuthenticationError: If not authenticated
            PermissionDeniedError: If not a superuser
            ValidationError: If input validation fails
        """
        data = {
            "name": name
        }
        
        if description:
            data["description"] = description
        
        try:
            response = self.auth_manager.request(
                method="POST",
                url="/adss/v1/users/roles",
                json=data,
                auth_required=True,
                **kwargs
            )
            handle_response_errors(response)
            
            role_data = response.json()
            return Role.from_dict(role_data)
            
        except Exception as e:
            if hasattr(e, 'response'):
                if e.response.status_code == 401:
                    raise AuthenticationError("Authentication required")
                elif e.response.status_code == 403:
                    raise PermissionDeniedError("Superuser access required")
                elif e.response.status_code == 400:
                    try:
                        error_data = e.response.json()
                        raise ValidationError(
                            f"Role creation failed: {error_data.get('detail', str(e))}",
                            error_data.get('errors')
                        )
                    except (ValueError, AttributeError):
                        pass
            raise
    
    def get_roles(self, skip: int = 0, limit: int = 100, **kwargs) -> List[Role]:
        """
        Get a list of roles (staff only).
        
        Args:
            skip: Number of roles to skip (for pagination)
            limit: Maximum number of roles to return
            **kwargs: Additional keyword arguments to pass to the request (e.g., verify=False)
            
        Returns:
            List of Role objects
            
        Raises:
            AuthenticationError: If not authenticated
            PermissionDeniedError: If not a staff user
        """
        params = {"skip": skip, "limit": limit}
        
        try:
            response = self.auth_manager.request(
                method="GET",
                url="/adss/v1/users/roles",
                params=params,
                auth_required=True,
                **kwargs
            )
            handle_response_errors(response)
            
            roles_data = response.json()
            return [Role.from_dict(role_data) for role_data in roles_data]
            
        except Exception as e:
            if hasattr(e, 'response'):
                if e.response.status_code == 401:
                    raise AuthenticationError("Authentication required")
                elif e.response.status_code == 403:
                    raise PermissionDeniedError("Staff access required")
            raise
    
    def add_user_to_role(self, user_id: str, role_id: int, **kwargs) -> bool:
        """
        Add a user to a role (superuser only).
        
        Args:
            user_id: ID of the user
            role_id: ID of the role
            **kwargs: Additional keyword arguments to pass to the request (e.g., verify=False)
            
        Returns:
            True if the user was successfully added to the role
            
        Raises:
            AuthenticationError: If not authenticated
            PermissionDeniedError: If not a superuser
            ResourceNotFoundError: If the user or role doesn't exist
        """
        try:
            response = self.auth_manager.request(
                method="POST",
                url=f"/adss/v1/users/{user_id}/roles/{role_id}",
                auth_required=True,
                **kwargs
            )
            handle_response_errors(response)
            
            return True
            
        except Exception as e:
            if hasattr(e, 'response'):
                if e.response.status_code == 401:
                    raise AuthenticationError("Authentication required")
                elif e.response.status_code == 403:
                    raise PermissionDeniedError("Superuser access required")
                elif e.response.status_code == 404:
                    raise ResourceNotFoundError("User or role not found")
            raise
    
    def remove_user_from_role(self, user_id: str, role_id: int, **kwargs) -> bool:
        """
        Remove a user from a role (superuser only).
        
        Args:
            user_id: ID of the user
            role_id: ID of the role
            **kwargs: Additional keyword arguments to pass to the request (e.g., verify=False)
            
        Returns:
            True if the user was successfully removed from the role
            
        Raises:
            AuthenticationError: If not authenticated
            PermissionDeniedError: If not a superuser
            ResourceNotFoundError: If the user or role doesn't exist
        """
        try:
            response = self.auth_manager.request(
                method="DELETE",
                url=f"/adss/v1/users/{user_id}/roles/{role_id}",
                auth_required=True,
                **kwargs
            )
            handle_response_errors(response)
            
            return True
            
        except Exception as e:
            if hasattr(e, 'response'):
                if e.response.status_code == 401:
                    raise AuthenticationError("Authentication required")
                elif e.response.status_code == 403:
                    raise PermissionDeniedError("Superuser access required")
                elif e.response.status_code == 404:
                    raise ResourceNotFoundError("User or role not found")
            raise
    
    def add_schema_permission(self, role_id: int, schema_name: str, permission: str, **kwargs) -> bool:
        """
        Add a schema permission to a role (superuser only).
        
        Args:
            role_id: ID of the role
            schema_name: Name of the schema
            permission: Permission type ('read', 'write', or 'all')
            **kwargs: Additional keyword arguments to pass to the request (e.g., verify=False)
            
        Returns:
            True if the permission was successfully added
            
        Raises:
            AuthenticationError: If not authenticated
            PermissionDeniedError: If not a superuser
            ResourceNotFoundError: If the role doesn't exist
            ValidationError: If the permission type is invalid
        """
        # Validate and format permission
        permission = format_permission(permission)
        
        data = {
            "schema_name": schema_name,
            "permission": permission
        }
        
        try:
            response = self.auth_manager.request(
                method="POST",
                url=f"/adss/v1/users/roles/{role_id}/schema-permissions",
                json=data,
                auth_required=True,
                **kwargs
            )
            handle_response_errors(response)
            
            return True
            
        except Exception as e:
            if hasattr(e, 'response'):
                if e.response.status_code == 401:
                    raise AuthenticationError("Authentication required")
                elif e.response.status_code == 403:
                    raise PermissionDeniedError("Superuser access required")
                elif e.response.status_code == 404:
                    raise ResourceNotFoundError("Role not found")
                elif e.response.status_code == 400:
                    try:
                        error_data = e.response.json()
                        raise ValidationError(
                            f"Adding schema permission failed: {error_data.get('detail', str(e))}",
                            error_data.get('errors')
                        )
                    except (ValueError, AttributeError):
                        pass
            raise
    
    def add_table_permission(self, role_id: int, schema_name: str, table_name: str, permission: str, **kwargs) -> bool:
        """
        Add a table permission to a role (superuser only).
        
        Args:
            role_id: ID of the role
            schema_name: Name of the schema
            table_name: Name of the table
            permission: Permission type ('read', 'write', or 'all')
            **kwargs: Additional keyword arguments to pass to the request (e.g., verify=False)
            
        Returns:
            True if the permission was successfully added
            
        Raises:
            AuthenticationError: If not authenticated
            PermissionDeniedError: If not a superuser
            ResourceNotFoundError: If the role doesn't exist
            ValidationError: If the permission type is invalid
        """
        # Validate and format permission
        permission = format_permission(permission)
        
        data = {
            "schema_name": schema_name,
            "table_name": table_name,
            "permission": permission
        }
        
        try:
            response = self.auth_manager.request(
                method="POST",
                url=f"/adss/v1/users/roles/{role_id}/table-permissions",
                json=data,
                auth_required=True,
                **kwargs
            )
            handle_response_errors(response)
            
            return True
            
        except Exception as e:
            if hasattr(e, 'response'):
                if e.response.status_code == 401:
                    raise AuthenticationError("Authentication required")
                elif e.response.status_code == 403:
                    raise PermissionDeniedError("Superuser access required")
                elif e.response.status_code == 404:
                    raise ResourceNotFoundError("Role not found")
                elif e.response.status_code == 400:
                    try:
                        error_data = e.response.json()
                        raise ValidationError(
                            f"Adding table permission failed: {error_data.get('detail', str(e))}",
                            error_data.get('errors')
                        )
                    except (ValueError, AttributeError):
                        pass
            raise
    
    def remove_schema_permission(self, role_id: int, schema_name: str, **kwargs) -> bool:
        """
        Remove a schema permission from a role (superuser only).
        
        Args:
            role_id: ID of the role
            schema_name: Name of the schema
            **kwargs: Additional keyword arguments to pass to the request (e.g., verify=False)
            
        Returns:
            True if the permission was successfully removed
            
        Raises:
            AuthenticationError: If not authenticated
            PermissionDeniedError: If not a superuser
            ResourceNotFoundError: If the role doesn't exist
        """
        try:
            response = self.auth_manager.request(
                method="DELETE",
                url=f"/adss/v1/users/roles/{role_id}/schema-permissions/{schema_name}",
                auth_required=True,
                **kwargs
            )
            handle_response_errors(response)
            
            return True
            
        except Exception as e:
            if hasattr(e, 'response'):
                if e.response.status_code == 401:
                    raise AuthenticationError("Authentication required")
                elif e.response.status_code == 403:
                    raise PermissionDeniedError("Superuser access required")
                elif e.response.status_code == 404:
                    raise ResourceNotFoundError("Role or schema permission not found")
            raise
    
    def remove_table_permission(self, role_id: int, schema_name: str, table_name: str, **kwargs) -> bool:
        """
        Remove a table permission from a role (superuser only).
        
        Args:
            role_id: ID of the role
            schema_name: Name of the schema
            table_name: Name of the table
            **kwargs: Additional keyword arguments to pass to the request (e.g., verify=False)
            
        Returns:
            True if the permission was successfully removed
            
        Raises:
            AuthenticationError: If not authenticated
            PermissionDeniedError: If not a superuser
            ResourceNotFoundError: If the role doesn't exist
        """
        try:
            response = self.auth_manager.request(
                method="DELETE",
                url=f"/adss/v1/users/roles/{role_id}/table-permissions/{schema_name}/{table_name}",
                auth_required=True,
                **kwargs
            )
            handle_response_errors(response)
            
            return True
            
        except Exception as e:
            if hasattr(e, 'response'):
                if e.response.status_code == 401:
                    raise AuthenticationError("Authentication required")
                elif e.response.status_code == 403:
                    raise PermissionDeniedError("Superuser access required")
                elif e.response.status_code == 404:
                    raise ResourceNotFoundError("Role or table permission not found")
            raise
    
    def get_role_permissions(self, role_id: int, **kwargs) -> RolePermissions:
        """
        Get permissions for a role (staff only).
        
        Args:
            role_id: ID of the role
            **kwargs: Additional keyword arguments to pass to the request (e.g., verify=False)
            
        Returns:
            RolePermissions object containing schema and table permissions
            
        Raises:
            AuthenticationError: If not authenticated
            PermissionDeniedError: If not a staff user
            ResourceNotFoundError: If the role doesn't exist
        """
        try:
            response = self.auth_manager.request(
                method="GET",
                url=f"/adss/v1/users/roles/{role_id}/permissions",
                auth_required=True,
                **kwargs
            )
            handle_response_errors(response)
            
            role_data = response.json()
            permissions_data = role_data.get("permissions", {})
            
            return RolePermissions.from_dict(permissions_data)
            
        except Exception as e:
            if hasattr(e, 'response'):
                if e.response.status_code == 401:
                    raise AuthenticationError("Authentication required")
                elif e.response.status_code == 403:
                    raise PermissionDeniedError("Staff access required")
                elif e.response.status_code == 404:
                    raise ResourceNotFoundError("Role not found")
            raise