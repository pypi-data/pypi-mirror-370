"""
CLI command to list available and loaded plugins.
"""

import argparse
from typing import List, Dict, Any
from janito.plugins.discovery import list_available_plugins, discover_plugins
import os
from janito.plugins.manager import PluginManager
from janito.plugins.builtin import BuiltinPluginRegistry


def handle_list_plugins(args: argparse.Namespace) -> None:
    """List plugins command handler."""
    
    if getattr(args, 'list_plugins_available', False):
        # List available plugins
        available = list_available_plugins()
        builtin_plugins = BuiltinPluginRegistry.list_builtin_plugins()
        
        if available or builtin_plugins:
            print("Available plugins:")
            
            # Show builtin plugins first
            if builtin_plugins:
                print("  Builtin plugins:")
                for plugin in builtin_plugins:
                    print(f"    - {plugin} [BUILTIN]")
            
            # Show other available plugins
            other_plugins = [p for p in available if p not in builtin_plugins]
            if other_plugins:
                print("  External plugins:")
                for plugin in other_plugins:
                    print(f"    - {plugin}")
        else:
            print("No plugins found in search paths")
            print("Search paths:")
            print(f"  - {os.getcwd()}/plugins")
            print(f"  - {os.path.expanduser('~')}/.janito/plugins")
    elif getattr(args, 'list_resources', False):
        # List all resources from loaded plugins
        manager = PluginManager()
        all_resources = manager.list_all_resources()
        
        if all_resources:
            print("Plugin Resources:")
            for plugin_name, resources in all_resources.items():
                metadata = manager.get_plugin_metadata(plugin_name)
                print(f"\n{plugin_name} v{metadata.version if metadata else 'unknown'}:")
                
                # Group resources by type
                tools = [r for r in resources if r['type'] == 'tool']
                commands = [r for r in resources if r['type'] == 'command']
                configs = [r for r in resources if r['type'] == 'config']
                
                if tools:
                    print("  Tools:")
                    for tool in tools:
                        print(f"    - {tool['name']}: {tool['description']}")
                
                if commands:
                    print("  Commands:")
                    for cmd in commands:
                        print(f"    - {cmd['name']}: {cmd['description']}")
                
                if configs:
                    print("  Configuration:")
                    for config in configs:
                        print(f"    - {config['name']}: {config['description']}")
        else:
            print("No plugins loaded")
    else:
        # List loaded plugins
        manager = PluginManager()
        loaded = manager.list_plugins()
        
        if loaded:
            print("Loaded plugins:")
            for plugin_name in loaded:
                metadata = manager.get_plugin_metadata(plugin_name)
                is_builtin = BuiltinPluginRegistry.is_builtin(plugin_name)
                if metadata:
                    builtin_tag = " [BUILTIN]" if is_builtin else ""
                    print(f"  - {metadata.name} v{metadata.version}{builtin_tag}")
                    print(f"    {metadata.description}")
                    if metadata.author:
                        print(f"    Author: {metadata.author}")
                    print()
        else:
            print("No plugins loaded")


