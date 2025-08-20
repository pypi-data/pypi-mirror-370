"""MCP KiCAD Schematic API Server Implementation

Standard MCP server providing KiCAD schematic manipulation tools.
"""

import asyncio
import sys
from typing import Any, Dict, List, Optional, Tuple
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import the KiCAD schematic API
try:
    import kicad_sch_api as ksa
except ImportError as e:
    print(f"Error: Could not import kicad-sch-api: {e}", file=sys.stderr)
    print("Please install: pip install kicad-sch-api", file=sys.stderr)
    sys.exit(1)

# Configure logging to stderr (not stdout for MCP)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Global schematic instance
current_schematic: Optional[Any] = None


async def main():
    """Main MCP server entry point."""
    logger.info("Starting MCP KiCAD Schematic API Server...")
    
    server = Server("mcp-kicad-sch-api")
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available KiCAD schematic tools."""
        return [
            Tool(
                name="create_schematic",
                description="Create a new KiCAD schematic",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name for the schematic"}
                    },
                    "additionalProperties": False
                }
            ),
            Tool(
                name="load_schematic", 
                description="Load an existing KiCAD schematic file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to the .kicad_sch file"}
                    },
                    "required": ["file_path"],
                    "additionalProperties": False
                }
            ),
            Tool(
                name="save_schematic",
                description="Save the current schematic to a file", 
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Optional path to save to"}
                    },
                    "additionalProperties": False
                }
            ),
            Tool(
                name="add_component",
                description="Add a component to the current schematic",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "lib_id": {"type": "string", "description": "Library ID (e.g., Device:R)"},
                        "reference": {"type": "string", "description": "Component reference (e.g., R1)"},
                        "value": {"type": "string", "description": "Component value (e.g., 10k)"},
                        "position": {"type": "array", "items": {"type": "number"}, "description": "[x, y] coordinates"},
                        "footprint": {"type": "string", "description": "Component footprint (e.g., Resistor_SMD:R_0603_1608Metric)"},
                        "properties": {"type": "string", "description": "Additional properties as key=value pairs"}
                    },
                    "required": ["lib_id", "reference", "value", "position"],
                    "additionalProperties": False
                }
            ),
            Tool(
                name="search_components",
                description="Search for components in KiCAD symbol libraries",
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "query": {"type": "string", "description": "Search term (e.g., resistor, op amp, 555)"},
                        "library": {"type": "string", "description": "Optional library to search in"},
                        "limit": {"type": "integer", "description": "Maximum number of results"}
                    },
                    "required": ["query"],
                    "additionalProperties": False
                }
            ),
            Tool(
                name="add_wire",
                description="Add a wire connection between two points",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start_pos": {"type": "array", "items": {"type": "number"}, "description": "[x, y] start coordinates"},
                        "end_pos": {"type": "array", "items": {"type": "number"}, "description": "[x, y] end coordinates"}
                    },
                    "required": ["start_pos", "end_pos"],
                    "additionalProperties": False
                }
            ),
            Tool(
                name="add_label",
                description="Add a text label to the schematic",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Label text"},
                        "position": {"type": "array", "items": {"type": "number"}, "description": "[x, y] coordinates"},
                        "rotation": {"type": "number", "description": "Text rotation in degrees"},
                        "size": {"type": "number", "description": "Font size"}
                    },
                    "required": ["text", "position"],
                    "additionalProperties": False
                }
            ),
            Tool(
                name="add_hierarchical_label",
                description="Add a hierarchical label to the schematic",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Label text"},
                        "position": {"type": "array", "items": {"type": "number"}, "description": "[x, y] coordinates"},
                        "shape": {"type": "string", "description": "Label shape (input, output, bidirectional, tristate, passive, unspecified)"},
                        "rotation": {"type": "number", "description": "Text rotation in degrees"},
                        "size": {"type": "number", "description": "Font size"}
                    },
                    "required": ["text", "position"],
                    "additionalProperties": False
                }
            ),
            Tool(
                name="add_junction",
                description="Add a junction (connection point) to the schematic",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "position": {"type": "array", "items": {"type": "number"}, "description": "[x, y] coordinates"},
                        "diameter": {"type": "number", "description": "Junction diameter (optional)"}
                    },
                    "required": ["position"],
                    "additionalProperties": False
                }
            ),
            Tool(
                name="list_components",
                description="List all components in the current schematic",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            ),
            Tool(
                name="get_schematic_info", 
                description="Get information about the current schematic",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            )
        ]
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
        """Handle tool calls by dispatching to appropriate functions."""
        global current_schematic
        
        try:
            if name == "create_schematic":
                schematic_name = arguments.get("name", "untitled")
                logger.info(f"Creating new schematic: {schematic_name}")
                current_schematic = ksa.create_schematic(schematic_name)
                
                return [TextContent(
                    type="text",
                    text=f"✅ Created new KiCAD schematic: '{schematic_name}'"
                )]
                
            elif name == "load_schematic":
                file_path = arguments.get("file_path")
                if not file_path:
                    return [TextContent(
                        type="text",
                        text="❌ file_path parameter is required"
                    )]
                
                logger.info(f"Loading schematic: {file_path}")
                current_schematic = ksa.load_schematic(file_path)
                
                return [TextContent(
                    type="text",
                    text=f"✅ Loaded KiCAD schematic: '{file_path}'"
                )]
                
            elif name == "save_schematic":
                if current_schematic is None:
                    return [TextContent(
                        type="text",
                        text="❌ No schematic loaded. Create or load a schematic first."
                    )]
                
                file_path = arguments.get("file_path")
                if file_path:
                    current_schematic.save(file_path)
                    logger.info(f"Saved schematic to: {file_path}")
                    return [TextContent(
                        type="text",
                        text=f"✅ Saved schematic to: {file_path}"
                    )]
                else:
                    current_schematic.save()
                    logger.info("Saved schematic to current file")
                    return [TextContent(
                        type="text", 
                        text="✅ Saved schematic to current file"
                    )]
                    
            elif name == "add_component":
                if current_schematic is None:
                    return [TextContent(
                        type="text",
                        text="❌ No schematic loaded. Create or load a schematic first."
                    )]
                
                lib_id = arguments.get("lib_id")
                reference = arguments.get("reference")
                value = arguments.get("value")
                position = arguments.get("position")
                footprint = arguments.get("footprint", "")
                properties = arguments.get("properties", "")
                
                if not all([lib_id, reference, value, position]):
                    return [TextContent(
                        type="text",
                        text="❌ lib_id, reference, value, and position parameters are required"
                    )]
                
                if len(position) != 2:
                    return [TextContent(
                        type="text",
                        text="❌ Position must be [x, y] coordinates"
                    )]
                
                logger.info(f"Adding component: {lib_id} {reference}={value} at {position}")
                
                # Use the correct API - components.add() method
                component = current_schematic.components.add(
                    lib_id=lib_id,
                    reference=reference,
                    value=value,
                    position=tuple(position),
                    footprint=footprint if footprint else None
                )
                
                # Add additional properties if provided
                if properties:
                    for prop in properties.split(","):
                        if "=" in prop:
                            key, val = prop.strip().split("=", 1)
                            component.set_property(key.strip(), val.strip())
                
                return [TextContent(
                    type="text",
                    text=f"✅ Added component: {reference} ({lib_id}) = {value} at {position}"
                )]
                
            elif name == "search_components":
                query = arguments.get("query")
                if not query:
                    return [TextContent(
                        type="text",
                        text="❌ query parameter is required"
                    )]
                    
                library = arguments.get("library")
                limit = arguments.get("limit", 20)
                
                logger.info(f"Searching components: {query}")
                
                try:
                    # Use the kicad-sch-api search functionality
                    from kicad_sch_api.discovery.search_index import search_components as search_func
                    
                    results = search_func(query, library=library, limit=limit)
                    
                    if not results:
                        return [TextContent(
                            type="text",
                            text=f"No components found matching '{query}'"
                        )]
                    
                    result_text = f"Found {len(results)} components matching '{query}':\n\n"
                    for result in results[:limit]:
                        result_text += f"• {result.get('lib_id', 'Unknown')}"
                        if 'description' in result:
                            result_text += f" - {result['description']}"
                        result_text += "\n"
                    
                    return [TextContent(type="text", text=result_text)]
                except ImportError:
                    return [TextContent(
                        type="text",
                        text="❌ Component search functionality not available"
                    )]
                
            elif name == "add_wire":
                if current_schematic is None:
                    return [TextContent(
                        type="text",
                        text="❌ No schematic loaded. Create or load a schematic first."
                    )]
                
                start_pos = arguments.get("start_pos")
                end_pos = arguments.get("end_pos")
                
                if not start_pos or not end_pos:
                    return [TextContent(
                        type="text",
                        text="❌ start_pos and end_pos parameters are required"
                    )]
                
                if len(start_pos) != 2 or len(end_pos) != 2:
                    return [TextContent(
                        type="text", 
                        text="❌ Positions must be [x, y] coordinates"
                    )]
                
                logger.info(f"Adding wire from {start_pos} to {end_pos}")
                
                # Use the correct API method - add_wire with start and end parameters
                wire_uuid = current_schematic.add_wire(
                    start=tuple(start_pos),
                    end=tuple(end_pos)
                )
                
                return [TextContent(
                    type="text",
                    text=f"✅ Added wire from {start_pos} to {end_pos} (UUID: {wire_uuid})"
                )]
                
            elif name == "add_label":
                if current_schematic is None:
                    return [TextContent(
                        type="text",
                        text="❌ No schematic loaded. Create or load a schematic first."
                    )]
                
                text = arguments.get("text")
                position = arguments.get("position")
                rotation = arguments.get("rotation", 0.0)
                size = arguments.get("size", 1.27)
                
                if not text or not position:
                    return [TextContent(
                        type="text",
                        text="❌ text and position parameters are required"
                    )]
                
                if len(position) != 2:
                    return [TextContent(
                        type="text",
                        text="❌ Position must be [x, y] coordinates"
                    )]
                
                logger.info(f"Adding label '{text}' at {position}")
                
                # Use the correct API method
                label_uuid = current_schematic.add_label(
                    text=text,
                    position=tuple(position),
                    rotation=rotation,
                    size=size
                )
                
                return [TextContent(
                    type="text",
                    text=f"✅ Added label '{text}' at {position} (UUID: {label_uuid})"
                )]
                
            elif name == "add_hierarchical_label":
                if current_schematic is None:
                    return [TextContent(
                        type="text",
                        text="❌ No schematic loaded. Create or load a schematic first."
                    )]
                
                text = arguments.get("text")
                position = arguments.get("position")
                shape = arguments.get("shape", "input")
                rotation = arguments.get("rotation", 0.0)
                size = arguments.get("size", 1.27)
                
                if not text or not position:
                    return [TextContent(
                        type="text",
                        text="❌ text and position parameters are required"
                    )]
                
                if len(position) != 2:
                    return [TextContent(
                        type="text",
                        text="❌ Position must be [x, y] coordinates"
                    )]
                
                logger.info(f"Adding hierarchical label '{text}' at {position}")
                
                # Import the shape enum
                from kicad_sch_api.core.types import HierarchicalLabelShape
                
                # Convert string shape to enum
                shape_map = {
                    "input": HierarchicalLabelShape.INPUT,
                    "output": HierarchicalLabelShape.OUTPUT,
                    "bidirectional": HierarchicalLabelShape.BIDIRECTIONAL,
                    "tristate": HierarchicalLabelShape.TRISTATE,
                    "passive": HierarchicalLabelShape.PASSIVE,
                    "unspecified": HierarchicalLabelShape.UNSPECIFIED
                }
                
                shape_enum = shape_map.get(shape.lower(), HierarchicalLabelShape.INPUT)
                
                # Use the correct API method
                label_uuid = current_schematic.add_hierarchical_label(
                    text=text,
                    position=tuple(position),
                    shape=shape_enum,
                    rotation=rotation,
                    size=size
                )
                
                return [TextContent(
                    type="text",
                    text=f"✅ Added hierarchical label '{text}' ({shape}) at {position} (UUID: {label_uuid})"
                )]
                
            elif name == "add_junction":
                if current_schematic is None:
                    return [TextContent(
                        type="text",
                        text="❌ No schematic loaded. Create or load a schematic first."
                    )]
                
                position = arguments.get("position")
                diameter = arguments.get("diameter", 0.0)
                
                if not position:
                    return [TextContent(
                        type="text",
                        text="❌ position parameter is required"
                    )]
                
                if len(position) != 2:
                    return [TextContent(
                        type="text",
                        text="❌ Position must be [x, y] coordinates"
                    )]
                
                logger.info(f"Adding junction at {position}")
                
                # Use the junction collection to add junction
                junction_uuid = current_schematic.junctions.add(
                    position=tuple(position),
                    diameter=diameter
                )
                
                return [TextContent(
                    type="text",
                    text=f"✅ Added junction at {position} (UUID: {junction_uuid})"
                )]
                
            elif name == "list_components":
                if current_schematic is None:
                    return [TextContent(
                        type="text",
                        text="❌ No schematic loaded. Create or load a schematic first."
                    )]
                
                components = list(current_schematic.components)
                
                if not components:
                    return [TextContent(
                        type="text",
                        text="No components in the current schematic."
                    )]
                
                result_text = f"Components in schematic ({len(components)} total):\n\n"
                for comp in components:
                    result_text += f"• {comp.reference} ({comp.lib_id}) = {comp.value}"
                    if hasattr(comp, 'position'):
                        result_text += f" at {comp.position}"
                    if hasattr(comp, 'footprint') and comp.footprint:
                        result_text += f" [{comp.footprint}]"
                    result_text += "\n"
                
                return [TextContent(type="text", text=result_text)]
                
            elif name == "get_schematic_info":
                if current_schematic is None:
                    return [TextContent(
                        type="text",
                        text="❌ No schematic loaded. Create or load a schematic first."
                    )]
                
                # Get comprehensive schematic information
                try:
                    summary = current_schematic.get_summary()
                    
                    info_text = "📋 Schematic Information:\n\n"
                    info_text += f"• Title: {summary.get('title', 'Untitled')}\n"
                    info_text += f"• Components: {summary.get('component_count', 0)}\n"
                    info_text += f"• Modified: {summary.get('modified', False)}\n"
                    
                    # Additional stats if available
                    if hasattr(current_schematic, 'wires'):
                        info_text += f"• Wires: {len(current_schematic.wires)}\n"
                    if hasattr(current_schematic, 'junctions'):
                        info_text += f"• Junctions: {len(current_schematic.junctions)}\n"
                    
                    return [TextContent(type="text", text=info_text)]
                except Exception as e:
                    # Fallback info
                    info_text = "📋 Schematic Information:\n\n"
                    info_text += f"• Components: {len(list(current_schematic.components))}\n"
                    info_text += f"• Status: Loaded and ready\n"
                    
                    return [TextContent(type="text", text=info_text)]
            
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Unknown tool: {name}"
                )]
                
        except Exception as e:
            logger.error(f"Error in tool {name}: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Error in {name}: {str(e)}"
            )]
    
    # Start the MCP server
    logger.info("MCP server ready, waiting for connections...")
    
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            options,
            raise_exceptions=True
        )


if __name__ == "__main__":
    asyncio.run(main())