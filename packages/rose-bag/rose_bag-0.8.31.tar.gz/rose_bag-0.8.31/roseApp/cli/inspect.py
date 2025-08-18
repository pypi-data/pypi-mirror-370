#!/usr/bin/env python3
"""
Inspect command for ROS bag files - Using ResultHandler for rendering and export
"""
import asyncio
from pathlib import Path
from typing import Optional, List

import typer
from ..core.model import AnalysisLevel
from ..core.ui_control import UIControl, OutputFormat, ExportOptions, DisplayConfig, Message
from ..core.util import set_app_mode, AppMode, get_logger
from ..core.cache import create_bag_cache_manager
from .util import filter_topics, check_and_load_bag_cache
app = typer.Typer(help="Inspect ROS bag files")


@app.command()
def inspect(
    bag_path: Path = typer.Argument(..., help="Path to the ROS bag file"),
    topics: Optional[List[str]] = typer.Option(None, "--topics", "-t", help="Filter specific topics"),

    show_fields: bool = typer.Option(False, "--show-fields", help="Show field analysis for messages"),
    sort_by: str = typer.Option("size", "--sort", help="Sort topics by (name, count, frequency, size)"),
    reverse_sort: bool = typer.Option(False, "--reverse", help="Reverse sort order"),


    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    debug: bool = typer.Option(False, "--debug", help="Show debug logs"),

):
    """
    Inspect a ROS bag file and display comprehensive analysis
    
    If the bag file is not in cache, you will be prompted to load it automatically.
    This command uses cached bag analysis for fast inspection.
    """
    # Use UIControl for unified output management
    ui = UIControl()
    
    # Validate bag file exists
    if not bag_path.exists():
        ui.show_error(f"Bag file not found: {bag_path}")
        raise typer.Exit(1)
    
    # Get cache manager and check current status
    cache_manager = create_bag_cache_manager()
    cached_entry = cache_manager.get_analysis(bag_path)
    
    # Check if bag needs loading or re-loading for verbose mode
    needs_loading = False
    needs_index = False
    
    if cached_entry is None:
        needs_loading = True
        needs_index = verbose
    elif verbose and not cached_entry.bag_info.has_any_dataframes():
        # Verbose mode requires index, but current cache doesn't have DataFrames
        needs_index = True
        
    if needs_loading:
        # Bag not in cache at all
        build_index = verbose
        if not check_and_load_bag_cache(bag_path, auto_load=True, verbose=verbose, build_index=build_index):
            ui.show_error(f"Bag file '{bag_path}' is not available in cache and loading was cancelled.")
            raise typer.Exit(1)
        cached_entry = cache_manager.get_analysis(bag_path)
    elif needs_index:
        # Bag in cache but needs DataFrame index for verbose mode
        console = ui.get_console()
        console.print(f"[yellow]⚠[/yellow] Verbose mode requires DataFrame index, but cached data doesn't have it.")
        should_rebuild = typer.confirm("Would you like to rebuild the cache with DataFrame indexing?", default=True)
        
        if should_rebuild:
            console.print(f"[blue]Rebuilding cache with DataFrame indexing...[/blue]")
            # Clear current cache entry and reload with index
            cache_manager.clear(bag_path)
            if not check_and_load_bag_cache(bag_path, auto_load=True, verbose=verbose, build_index=True, force_load=True):
                ui.show_error(f"Failed to rebuild cache with DataFrame indexing.")
                raise typer.Exit(1)
            cached_entry = cache_manager.get_analysis(bag_path)
        else:
            console.print("[yellow]Continuing with cached data (statistics may be incomplete).[/yellow]")
    
    # Set output format based on verbose mode
    if verbose:
        output_format = OutputFormat.TABLE
    else:
        output_format = OutputFormat.LIST
    
    # Configure logging based on debug flag
    if not debug:
        # Suppress logs in standard output unless debug mode
        import logging
        logging.getLogger().setLevel(logging.CRITICAL)
        logging.getLogger('cache').setLevel(logging.CRITICAL)
        logging.getLogger('root').setLevel(logging.CRITICAL)
    
    # Create options object (simplified since we're using cache directly)
    class SimpleInspectOptions:
        def __init__(self):
            self.topics = topics

            self.show_fields = show_fields
            self.sort_by = sort_by
            self.reverse_sort = reverse_sort
    
            self.output_format = output_format
            self.output_file = output
            self.verbose = verbose
    
    options = SimpleInspectOptions()
    
    # Run the async inspection
    asyncio.run(_run_inspect(cached_entry, options, debug))


async def _run_inspect(cached_entry, options, debug: bool = False):
    """Run the bag inspection asynchronously using BagManager and ResultHandler"""
    
    # Use UIControl for unified output management
    ui = UIControl()
    console = ui.get_console()
    
    # No longer need BagManager - we use cache directly
    
    try:
        Message(f"Load {cached_entry.bag_info.file_path} from cache").render(console)
        # Convert cached bag info to result format expected by UI
        bag_info = cached_entry.bag_info
        
        # Refresh statistics from DataFrames if available
        if bag_info.has_any_dataframes():
            bag_info.refresh_all_statistics_from_dataframes()
        
        # Create the result structure expected by UIControl
        result = {
            'topics': [],
            'file_path': bag_info.file_path,
            'total_messages': bag_info.total_messages,
            'total_size': bag_info.total_size,
            'duration_seconds': bag_info.duration_seconds,
            'time_range': bag_info.time_range.to_dict() if bag_info.time_range else None,
            'bag_info': {
                'file_path': bag_info.file_path,
                'file_name': Path(bag_info.file_path).name,
                'file_size': bag_info.file_size or 0,
                'file_size_mb': bag_info.file_size_mb,
                'topics_count': len(bag_info.topics),
                'total_messages': bag_info.total_messages or 0,
                'duration_seconds': bag_info.duration_seconds or 0.0,
                'analysis_time': 0.0,  # From cache, so analysis time is 0
                'cached': True
            }
        }
        
        # Get all topic names for filtering
        all_topic_names = [topic if isinstance(topic, str) else topic.name for topic in bag_info.topics]
        
        # Apply topic filtering if specified
        if options.topics:
            filtered_topic_names = filter_topics(all_topic_names, options.topics, None)
        else:
            filtered_topic_names = all_topic_names
        
        # Convert topics to expected format using optimized TopicInfo structure
        for topic_info_obj in bag_info.topics:
            # Skip topics that don't match the filter
            if topic_info_obj.name not in filtered_topic_names:
                continue
            
            # Build topic info based on verbose mode
            if options.verbose:
                # Verbose mode: include all statistics (count, size, frequency)
                topic_info = {
                    'name': topic_info_obj.name,
                    'message_type': topic_info_obj.message_type,
                    'message_count': topic_info_obj.message_count or 0,
                    'frequency': topic_info_obj.message_frequency or 0.0,
                    'size_bytes': topic_info_obj.total_size_bytes or 0
                }
            else:
                # Non-verbose mode: only name and message type for list display
                topic_info = {
                    'name': topic_info_obj.name,
                    'message_type': topic_info_obj.message_type
                }
            
            # Add field analysis if available from MessageTypeInfo
            if options.show_fields:
                msg_type_info = bag_info.find_message_type(topic_info_obj.message_type)
                if msg_type_info and msg_type_info.fields:
                    # Convert MessageFieldInfo objects to field paths
                    topic_info['field_paths'] = msg_type_info.get_all_field_paths()
            
            result['topics'].append(topic_info)
        
        # Add field analysis if requested using optimized MessageTypeInfo structure
        if options.show_fields and len(bag_info.message_types) > 0 and len(bag_info.topics) > 0:
            # Convert MessageTypeInfo structure to topic-based field_analysis
            field_analysis = {}
            for topic_info_obj in bag_info.topics:
                # Skip topics that don't match the filter
                if topic_info_obj.name not in filtered_topic_names:
                    continue
                    
                msg_type_info = bag_info.find_message_type(topic_info_obj.message_type)
                if msg_type_info and msg_type_info.fields:
                    # Extract hierarchical field paths from MessageFieldInfo objects
                    field_paths = _extract_field_paths_from_message_type(msg_type_info)
                    
                    if field_paths:
                        field_analysis[topic_info_obj.name] = {
                            'message_type': topic_info_obj.message_type,
                            'field_paths': sorted(field_paths)
                        }
            
            if field_analysis:
                result['field_analysis'] = field_analysis
        
        # Determine if we should export to file or render to console
        if options.output_file:
            # Export to file
            export_options = ExportOptions(
                format=options.output_format,
                output_file=options.output_file,
                pretty=True,
                include_metadata=True
            )
            
            success = UIControl.export_result(result, export_options)
            if not success:
                ui.show_export_failed_error()
                raise typer.Exit(1)
        else:
            # Choose display method based on format
            if options.output_format == OutputFormat.LIST:
                # Simple list format for non-verbose mode
                _display_simple_list(result, console, options.verbose)
            else:
                # Display results in panel (table format)
                display_config = DisplayConfig(
                    show_summary=True,
                    show_details=True,
                    show_cache_stats=True,
                    verbose=options.verbose,
                    full_width=True
                )
                UIControl.display_inspection_result(result, display_config, console)
            
            
            # Handle fields display separately if requested
            if options.show_fields:
                field_analysis = result.get('field_analysis', {})
                topics = result.get('topics', [])
                if field_analysis or any('field_paths' in topic for topic in topics):
                    # Use unified UI method for field panel display
                    ui.show_fields_panel(field_analysis, topics)
            
    except Exception as e:
        ui.show_error(f"Error during bag inspection: {e}")
        raise typer.Exit(1)
    finally:
        pass


def _extract_field_paths_from_message_type(msg_type_info):
    """
    Extract hierarchical field paths from MessageTypeInfo structure
    
    Args:
        msg_type_info: MessageTypeInfo object containing fields as List of MessageFieldInfo objects
    
    Returns:
        List of hierarchical field paths (e.g., ['header.seq', 'header.stamp', 'header.frame_id', ...])
    """
    if not msg_type_info.fields:
        return []
    
    # Use the built-in method to get all flattened field paths
    return msg_type_info.get_all_field_paths()


def _display_simple_list(result: dict, console, verbose: bool):
    """Display topics in simple list format"""
    from rich.text import Text
    from rich.panel import Panel
    
    bag_info = result.get('bag_info', {})
    topics = result.get('topics', [])
    
    # Show summary consistent with verbose mode (no emojis)
    console.print(f"\nFile: {bag_info.get('file_path', 'Unknown')}")
    console.print(f"Topics: {len(topics)}")
    console.print(f"File Size: {bag_info.get('file_size_mb', 0):.1f} MB")
    console.print(f"Duration: {bag_info.get('duration_seconds', 0):.1f}s")
    
    # List topics
    console.print(f"\nTopics:")
    for topic in topics:
        topic_line = Text()
        topic_line.append(f"  • {topic['name']}", style="bold cyan")
        topic_line.append(f" ({topic['message_type']})", style="dim")
        console.print(topic_line)


if __name__ == "__main__":
    app() 