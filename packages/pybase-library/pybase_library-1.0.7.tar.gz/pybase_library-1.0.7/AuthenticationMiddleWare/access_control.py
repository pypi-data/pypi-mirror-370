from typing import Callable
from enum import Enum
import logging
logger = logging.getLogger(__name__)
class AccessController:
    """Flexible access control system that allows users to customize routes and permissions"""
    
    def __init__(self):
        # Default public routes (always accessible)
        self.public_routes = {
            "/",
            "/health", 
            "/mock-token",
            "/test-headers",
            "/favicon.ico",
            "/docs",
            "/redoc",
            "/openapi.json"
        }
        
        # Route-based permissions: {route: {required_roles: []}}
        self.route_permissions = {}
        
        # Custom access function (user can override this)
        self.custom_access_function = None
    
    def add_public_route(self, route: str):
        """Add a route that doesn't require authentication"""
        self.public_routes.add(route)
    
    def remove_public_route(self, route: str):
        """Remove a route from public access"""
        self.public_routes.discard(route)
    
    def set_route_permission(self, route: str, required_roles: list = None):
        """Set specific permissions for a route"""
        self.route_permissions[route] = {
            "required_roles": required_roles or []
        }
    
    def set_custom_access_function(self, func: Callable[[str, dict], bool]):
        """Allow users to set their own custom access control function"""
        self.custom_access_function = func
    
    def check_access(self, url: str, claims: dict = None, custom_position_of_roles: Callable[[dict], list] = None) -> bool:
        """Main access control logic"""
        """func: user custom position of roles alter claims.roles"""
        
        # If user provided custom function, use it first
        if self.custom_access_function:
            try:
                return self.custom_access_function(url, claims)
            except Exception as e:
                logger.error(f"Custom access function error: {e}")
                return False
        
        # Check if route is public
        if url in self.public_routes:
            return True
        
        # If no claims provided, deny access to protected routes
        if not claims:
            return False
        
        # Check route-specific permissions
        if url in self.route_permissions:
            route_config = self.route_permissions[url]
            
            # Check required roles
            if custom_position_of_roles:
                user_roles = custom_position_of_roles(claims)
            else:
                # default position of roles
                user_roles = claims.get("roles", [])
            if not any(role in user_roles for role in route_config["required_roles"]):
                return False
            return True
        
        # Default: if route is not explicitly configured, require authentication
        return claims is not None
