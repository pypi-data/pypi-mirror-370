"""
Base plugin classes for Vector Store Client.

This module provides the foundation for the plugin architecture,
including the base plugin class and plugin registry.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Type
from datetime import datetime

from ..models import SemanticChunk
from ..exceptions import PluginError


class BasePlugin(ABC):
    """
    Base class for all plugins.
    
    Plugins can be used to extend the functionality of the Vector Store Client
    with custom preprocessing, post-processing, and analysis capabilities.
    
    Attributes:
        name (str): Plugin name
        version (str): Plugin version
        description (str): Plugin description
        enabled (bool): Whether the plugin is enabled
    """
    
    def __init__(self):
        self.name = self.get_name()
        self.version = self.get_version()
        self.description = self.get_description()
        self.enabled = True
        self.logger = logging.getLogger(f"plugin.{self.name}")
    
    @abstractmethod
    def get_name(self) -> str:
        """Get plugin name."""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Get plugin version."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get plugin description."""
        pass
    
    @abstractmethod
    async def execute(
        self, 
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute plugin logic.
        
        Parameters:
            data: Input data for the plugin
            context: Optional context information
            
        Returns:
            Dict[str, Any]: Processed data
            
        Raises:
            PluginError: If plugin execution fails
        """
        pass
    
    async def pre_execute(
        self, 
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Pre-execution hook.
        
        Called before the main execute method. Can be used for validation,
        data preparation, or other pre-processing tasks.
        
        Parameters:
            data: Input data
            context: Optional context
            
        Returns:
            Dict[str, Any]: Prepared data
        """
        return data
    
    async def post_execute(
        self, 
        result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Post-execution hook.
        
        Called after the main execute method. Can be used for cleanup,
        result validation, or other post-processing tasks.
        
        Parameters:
            result: Execution result
            context: Optional context
            
        Returns:
            Dict[str, Any]: Final result
        """
        return result
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate plugin configuration.
        
        Parameters:
            config: Plugin configuration
            
        Returns:
            bool: True if configuration is valid
            
        Raises:
            PluginError: If configuration is invalid
        """
        return True
    
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Get plugin configuration schema.
        
        Returns:
            Dict[str, Any]: Configuration schema
        """
        return {}
    
    def enable(self) -> None:
        """Enable the plugin."""
        self.enabled = True
        self.logger.info(f"Plugin {self.name} enabled")
    
    def disable(self) -> None:
        """Disable the plugin."""
        self.enabled = False
        self.logger.info(f"Plugin {self.name} disabled")
    
    def is_enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self.enabled


class PluginRegistry:
    """
    Registry for managing plugins.
    
    Provides functionality for registering, discovering, and managing
    plugins in the Vector Store Client.
    
    Attributes:
        plugins (Dict[str, BasePlugin]): Registered plugins
        plugin_classes (Dict[str, Type[BasePlugin]]): Plugin classes
    """
    
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_classes: Dict[str, Type[BasePlugin]] = {}
        self.logger = logging.getLogger("plugin_registry")
    
    def register_plugin(self, plugin: BasePlugin) -> None:
        """
        Register a plugin instance.
        
        Parameters:
            plugin: Plugin instance to register
            
        Raises:
            PluginError: If plugin registration fails
        """
        if not isinstance(plugin, BasePlugin):
            raise PluginError(f"Invalid plugin type: {type(plugin)}")
        
        if plugin.name in self.plugins:
            self.logger.warning(f"Plugin {plugin.name} already registered, overwriting")
        
        self.plugins[plugin.name] = plugin
        self.logger.info(f"Registered plugin: {plugin.name} v{plugin.version}")
    
    def register_plugin_class(self, plugin_class: Type[BasePlugin]) -> None:
        """
        Register a plugin class.
        
        Parameters:
            plugin_class: Plugin class to register
        """
        if not issubclass(plugin_class, BasePlugin):
            raise PluginError(f"Invalid plugin class: {plugin_class}")
        
        # Create instance to get name
        temp_instance = plugin_class()
        name = temp_instance.name
        
        self.plugin_classes[name] = plugin_class
        self.logger.info(f"Registered plugin class: {name}")
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """
        Get plugin by name.
        
        Parameters:
            name: Plugin name
            
        Returns:
            Optional[BasePlugin]: Plugin instance or None
        """
        return self.plugins.get(name)
    
    def get_plugin_class(self, name: str) -> Optional[Type[BasePlugin]]:
        """
        Get plugin class by name.
        
        Parameters:
            name: Plugin name
            
        Returns:
            Optional[Type[BasePlugin]]: Plugin class or None
        """
        return self.plugin_classes.get(name)
    
    def create_plugin(self, name: str, **kwargs) -> Optional[BasePlugin]:
        """
        Create plugin instance by name.
        
        Parameters:
            name: Plugin name
            **kwargs: Plugin constructor arguments
            
        Returns:
            Optional[BasePlugin]: Plugin instance or None
        """
        plugin_class = self.get_plugin_class(name)
        if plugin_class:
            return plugin_class(**kwargs)
        return None
    
    def list_plugins(self) -> List[str]:
        """
        List all registered plugin names.
        
        Returns:
            List[str]: List of plugin names
        """
        return list(self.plugins.keys())
    
    def list_plugin_classes(self) -> List[str]:
        """
        List all registered plugin class names.
        
        Returns:
            List[str]: List of plugin class names
        """
        return list(self.plugin_classes.keys())
    
    def unregister_plugin(self, name: str) -> bool:
        """
        Unregister a plugin.
        
        Parameters:
            name: Plugin name
            
        Returns:
            bool: True if plugin was unregistered
        """
        if name in self.plugins:
            del self.plugins[name]
            self.logger.info(f"Unregistered plugin: {name}")
            return True
        return False
    
    def unregister_plugin_class(self, name: str) -> bool:
        """
        Unregister a plugin class.
        
        Parameters:
            name: Plugin class name
            
        Returns:
            bool: True if plugin class was unregistered
        """
        if name in self.plugin_classes:
            del self.plugin_classes[name]
            self.logger.info(f"Unregistered plugin class: {name}")
            return True
        return False
    
    async def execute_plugins(
        self,
        data: Dict[str, Any],
        plugin_names: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute multiple plugins on data.
        
        Parameters:
            data: Input data
            plugin_names: List of plugin names to execute (None for all)
            context: Optional context
            
        Returns:
            Dict[str, Any]: Processed data
        """
        result = data
        
        plugins_to_execute = plugin_names or list(self.plugins.keys())
        
        for plugin_name in plugins_to_execute:
            plugin = self.get_plugin(plugin_name)
            if plugin and plugin.is_enabled():
                try:
                    # Pre-execute
                    result = await plugin.pre_execute(result, context)
                    
                    # Execute
                    result = await plugin.execute(result, context)
                    
                    # Post-execute
                    result = await plugin.post_execute(result, context)
                    
                    self.logger.debug(f"Executed plugin: {plugin_name}")
                    
                except Exception as e:
                    self.logger.error(f"Plugin {plugin_name} execution failed: {e}")
                    raise PluginError(f"Plugin {plugin_name} execution failed: {e}")
        
        return result
    
    def get_plugin_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get plugin information.
        
        Parameters:
            name: Plugin name
            
        Returns:
            Optional[Dict[str, Any]]: Plugin information
        """
        plugin = self.get_plugin(name)
        if plugin:
            return {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "enabled": plugin.enabled,
                "config_schema": plugin.get_config_schema()
            }
        return None
    
    def get_all_plugin_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information for all plugins.
        
        Returns:
            Dict[str, Dict[str, Any]]: Plugin information dictionary
        """
        return {
            name: self.get_plugin_info(name)
            for name in self.list_plugins()
        } 