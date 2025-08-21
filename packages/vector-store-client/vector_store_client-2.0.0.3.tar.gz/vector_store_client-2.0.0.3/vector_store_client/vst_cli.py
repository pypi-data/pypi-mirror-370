#!/usr/bin/env python3
"""
Vector Store CLI (vst-cli) - Unified Command Line Interface.

A comprehensive CLI for Vector Store operations including:
- Text chunking and storage
- Semantic and BM25 search
- Hybrid search
- Health monitoring
- Configuration management

Usage:
    python -m vector_store_client.vst_cli health
    python -m vector_store_client.vst_cli create --text "Your text here"
    python -m vector_store_client.vst_cli search --query "machine learning"
    python -m vector_store_client.vst_cli hybrid --semantic "AI" --bm25 "artificial intelligence"

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 2.0.0
"""

import asyncio
import json
import sys
import logging
from typing import Optional, List
import os

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Enable logging
logging.basicConfig(level=logging.INFO)

from .client import VectorStoreClient
from .models import SemanticChunk, ChunkQuery, HybridSearchConfig
from .adapters.svo_adapter import SVOChunkerAdapter

# Initialize Rich console
console = Console()


@click.group()
@click.option('--url', '-u', default='http://localhost:8007', help='Vector Store server URL')
@click.option('--chunker-url', default='http://localhost:8009', help='SVO Chunker URL')
@click.option('--timeout', '-t', default=30.0, type=float, help='Request timeout in seconds')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx: click.Context, url: str, chunker_url: str, timeout: float, verbose: bool) -> None:
    """Vector Store CLI (vst-cli) - Unified interface for Vector Store operations."""
    ctx.ensure_object(dict)
    ctx.obj['url'] = url
    ctx.obj['chunker_url'] = chunker_url
    ctx.obj['timeout'] = timeout
    ctx.obj['verbose'] = verbose
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command()
@click.pass_context
def health(ctx: click.Context) -> None:
    """Check server health status."""
    async def _health():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Checking server health...", total=None)
                
                client = await VectorStoreClient.create(
                    ctx.obj['url'], 
                    ctx.obj['timeout']
                )
                health_data = await client.health_check()
                await client.close()
                
                progress.update(task, description="Health check completed")
            
            # Display results
            table = Table(title="Server Health Status")
            table.add_column("Service", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Version", style="yellow")
            table.add_column("Model", style="blue")
            
            table.add_row(
                "Vector Store",
                health_data.status,
                getattr(health_data, 'version', 'N/A'),
                getattr(health_data, 'model', 'N/A')
            )
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
    
    asyncio.run(_health())


@cli.command()
@click.option('--command', '-c', help='Specific command to get help for')
@click.pass_context
def help(ctx: click.Context, command: Optional[str]) -> None:
    """Get help information for commands."""
    async def _help():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            if command:
                help_data = await client.get_help(command)
                console.print(f"[cyan]Help for '{command}':[/cyan]")
                console.print(json.dumps(help_data, indent=2))
            else:
                help_data = await client.get_help()
                console.print("[cyan]Available commands:[/cyan]")
                console.print(json.dumps(help_data, indent=2))
            
            await client.close()
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
    
    asyncio.run(_help())


@cli.command()
@click.option('--path', '-p', help='Configuration path')
@click.pass_context
def config(ctx: click.Context, path: Optional[str]) -> None:
    """Get server configuration."""
    async def _config():
        try:
            client = await VectorStoreClient.create(
                ctx.obj['url'], 
                ctx.obj['timeout']
            )
            
            if path:
                config_value = await client.get_config(path)
                console.print(f"[cyan]{path}:[/cyan] {config_value}")
            else:
                config_data = await client.get_config()
                console.print("[cyan]Server configuration:[/cyan]")
                console.print(json.dumps(config_data, indent=2))
            
            await client.close()
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
    
    asyncio.run(_config())


@cli.command()
@click.option('--text', '-t', required=True, help='Text content to chunk and store')
@click.option('--type', '-y', default='DocBlock', help='Chunk type')
@click.option('--language', '-l', default='en', help='Language code')
@click.option('--category', help='Business category')
@click.option('--title', help='Chunk title')
@click.option('--tags', help='Comma-separated tags')
@click.option('--window', '-w', default=3, type=int, help='SVO chunker window size')
@click.option('--output', '-o', help='Output file for chunk data (JSON)')
@click.pass_context
def create(ctx: click.Context, text: str, type: str, language: str, 
           category: Optional[str], title: Optional[str], tags: Optional[str], 
           window: int, output: Optional[str]) -> None:
    """Create chunks from text using SVO chunker and store them."""
    async def _create():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                # Step 1: Chunk text
                task1 = progress.add_task("Chunking text...", total=None)
                
                svo_adapter = SVOChunkerAdapter()
                async with svo_adapter:
                    chunks = await svo_adapter.chunk_text(
                        text=text,
                        chunk_type=type,
                        language=language,
                        window=window
                    )
                
                progress.update(task1, description=f"Created {len(chunks)} chunks")
                
                # Add metadata
                tags_list = tags.split(',') if tags else []
                for chunk in chunks:
                    if category:
                        chunk.category = category
                    if title:
                        chunk.title = title
                    if tags_list:
                        chunk.tags = tags_list
                
                # Step 2: Store chunks
                task2 = progress.add_task("Storing chunks...", total=None)
                
                client = await VectorStoreClient.create(
                    ctx.obj['url'], 
                    ctx.obj['timeout']
                )
                result = await client.create_chunks(chunks)
                await client.close()
                
                progress.update(task2, description="Chunks stored")
            
            # Display results
            if result.success:
                console.print(f"[green]✅ Successfully created {len(result.uuids)} chunks[/green]")
                
                table = Table(title="Created Chunks")
                table.add_column("UUID", style="cyan")
                table.add_column("Text", style="white")
                table.add_column("Type", style="green")
                
                for i, uuid in enumerate(result.uuids):
                    chunk_text = chunks[i].body[:50] + "..." if len(chunks[i].body) > 50 else chunks[i].body
                    table.add_row(uuid, chunk_text, chunks[i].type)
                
                console.print(table)
                
                # Save to file if requested
                if output:
                    chunks_data = [chunk.model_dump() for chunk in chunks]
                    with open(output, 'w') as f:
                        json.dump(chunks_data, f, indent=2)
                    console.print(f"[yellow]Chunk data saved to {output}[/yellow]")
            else:
                console.print(f"[red]❌ Failed to create chunks: {result.error}[/red]")
                sys.exit(1)
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
    
    asyncio.run(_create())


@cli.command()
@click.option('--query', '-q', required=True, help='Search query')
@click.option('--limit', '-l', default=10, type=int, help='Maximum results')
@click.option('--filter', '-f', help='Metadata filter (JSON string)')
@click.option('--relevance', '-r', default=0.0, type=float, help='Minimum relevance threshold')
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def search(ctx: click.Context, query: str, limit: int, filter: Optional[str], 
           relevance: float, output_format: str) -> None:
    """Search for chunks using semantic search."""
    async def _search():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Searching...", total=None)
                
                client = await VectorStoreClient.create(
                    ctx.obj['url'], 
                    ctx.obj['timeout']
                )
                
                # Build metadata filter
                metadata_filter = None
                if filter:
                    try:
                        metadata_filter = json.loads(filter)
                    except json.JSONDecodeError:
                        console.print("[red]Error: Invalid JSON in filter[/red]")
                        sys.exit(1)
                
                results = await client.search_chunks(
                    search_str=query,
                    limit=limit,
                    level_of_relevance=relevance,
                    metadata_filter=metadata_filter
                )
                
                await client.close()
                progress.update(task, description="Search completed")
            
            # Display results
            if output_format == 'json':
                output_data = []
                for result in results:
                    output_data.append({
                        'uuid': result.uuid,
                        'body': result.body,
                        'text': result.text,
                        'type': result.type,
                        'category': result.category,
                        'tags': result.tags
                    })
                console.print(json.dumps(output_data, indent=2))
            else:
                if results:
                    console.print(f"[green]Found {len(results)} results:[/green]")
                    
                    table = Table(title=f"Search Results for '{query}'")
                    table.add_column("UUID", style="cyan")
                    table.add_column("Text", style="white")
                    table.add_column("Type", style="green")
                    table.add_column("Category", style="yellow")
                    
                    for result in results:
                        text = result.body[:80] + "..." if len(result.body) > 80 else result.body
                        table.add_row(
                            result.uuid[:8] + "...",
                            text,
                            result.type,
                            result.category or "N/A"
                        )
                    
                    console.print(table)
                else:
                    console.print("[yellow]No results found. Try adjusting search parameters.[/yellow]")
                    console.print("Suggestions:")
                    console.print("  - Lower the relevance threshold (--relevance 0.0)")
                    console.print("  - Increase the limit (--limit 20)")
                    console.print("  - Try different search terms")
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
    
    asyncio.run(_search())


@cli.command()
@click.option('--semantic', '-s', required=True, help='Semantic search query')
@click.option('--bm25', '-b', required=True, help='BM25 search query')
@click.option('--limit', '-l', default=10, type=int, help='Maximum results')
@click.option('--bm25-weight', default=0.5, type=float, help='BM25 weight (0.0-1.0)')
@click.option('--semantic-weight', default=0.5, type=float, help='Semantic weight (0.0-1.0)')
@click.option('--min-score', default=0.0, type=float, help='Minimum score threshold')
@click.pass_context
def hybrid(ctx: click.Context, semantic: str, bm25: str, limit: int, 
           bm25_weight: float, semantic_weight: float, min_score: float) -> None:
    """Perform hybrid search combining BM25 and semantic search."""
    async def _hybrid_search():
        try:
            # Validate weights
            if abs(bm25_weight + semantic_weight - 1.0) > 0.001:
                console.print("[red]Error: BM25 and semantic weights must sum to 1.0[/red]")
                sys.exit(1)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Performing hybrid search...", total=None)
                
                client = await VectorStoreClient.create(
                    ctx.obj['url'], 
                    ctx.obj['timeout']
                )
                
                # Create hybrid search configuration
                hybrid_config = HybridSearchConfig(
                    bm25_weight=bm25_weight,
                    semantic_weight=semantic_weight,
                    strategy="weighted_sum",
                    min_score_threshold=min_score
                )
                
                # Perform hybrid search
                results = await client.hybrid_search(
                    semantic_query=semantic,
                    bm25_query=bm25,
                    search_fields=['body', 'text', 'title'],
                    limit=limit,
                    level_of_relevance=min_score
                )
                
                await client.close()
                progress.update(task, description="Hybrid search completed")
            
            # Display results
            console.print(f"[green]Hybrid Search Results (BM25: {bm25_weight}, Semantic: {semantic_weight}):[/green]")
            console.print(f"[green]Found {len(results)} results:[/green]")
            
            if results:
                table = Table(title="Hybrid Search Results")
                table.add_column("Score", style="cyan")
                table.add_column("UUID", style="blue")
                table.add_column("Text", style="white")
                table.add_column("Type", style="green")
                
                for result in results:
                    text = result.chunk.body[:80] + "..." if len(result.chunk.body) > 80 else result.chunk.body
                    table.add_row(
                        f"{result.score:.3f}",
                        result.chunk.uuid[:8] + "...",
                        text,
                        result.chunk.type
                    )
                
                console.print(table)
            else:
                console.print("[yellow]No results found.[/yellow]")
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
    
    asyncio.run(_hybrid_search())


@cli.command()
@click.option('--text', '-t', required=True, help='Text to chunk')
@click.option('--type', '-y', default='DocBlock', help='Chunk type')
@click.option('--language', '-l', default='en', help='Language code')
@click.option('--window', '-w', default=3, type=int, help='Window size for sentence grouping')
@click.option('--output', '-o', help='Output file for chunks (JSON)')
@click.pass_context
def chunk(ctx: click.Context, text: str, type: str, language: str, 
          window: int, output: Optional[str]) -> None:
    """Chunk text using SVO chunker without storing."""
    async def _chunk():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Chunking text...", total=None)
                
                svo_adapter = SVOChunkerAdapter()
                async with svo_adapter:
                    chunks = await svo_adapter.chunk_text(
                        text=text,
                        chunk_type=type,
                        language=language,
                        window=window
                    )
                
                progress.update(task, description="Chunking completed")
            
            # Display results
            console.print(f"[green]Created {len(chunks)} chunks:[/green]")
            
            chunks_data = []
            for i, chunk in enumerate(chunks, 1):
                chunk_info = {
                    'index': i,
                    'uuid': chunk.uuid,
                    'body': chunk.body,
                    'text': chunk.text,
                    'type': chunk.type,
                    'language': chunk.language,
                    'ordinal': chunk.ordinal,
                    'bm25_tokens': chunk.get_bm25_tokens(),
                    'tokens': chunk.get_tokens(),
                    'has_embedding': chunk.embedding is not None
                }
                chunks_data.append(chunk_info)
                
                console.print(f"[cyan]Chunk {i}:[/cyan]")
                console.print(f"  UUID: {chunk.uuid}")
                console.print(f"  Text: {chunk.body}")
                console.print(f"  Type: {chunk.type}")
                console.print(f"  Language: {chunk.language}")
                console.print(f"  BM25 Tokens: {chunk.get_bm25_tokens()}")
                console.print(f"  Has Embedding: {chunk.embedding is not None}")
                console.print()
            
            # Save to file if requested
            if output:
                with open(output, 'w') as f:
                    json.dump(chunks_data, f, indent=2)
                console.print(f"[yellow]Chunks saved to {output}[/yellow]")
        
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
    
    asyncio.run(_chunk())


@cli.command()
@click.option('--uuids', '-u', required=True, help='Comma-separated list of UUIDs to delete')
@click.pass_context
def delete(ctx: click.Context, uuids: str) -> None:
    """Delete chunks by UUIDs."""
    async def _delete():
        try:
            uuid_list = [u.strip() for u in uuids.split(',') if u.strip()]
            if not uuid_list:
                console.print("[red]Error: No valid UUIDs provided[/red]")
                sys.exit(1)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Deleting chunks...", total=None)
                
                client = await VectorStoreClient.create(
                    ctx.obj['url'], 
                    ctx.obj['timeout']
                )
                result = await client.delete_chunks(uuids=uuid_list)
                await client.close()
                
                progress.update(task, description="Deletion completed")
            
            if result.success:
                console.print(f"[green]✅ Successfully deleted {result.deleted_count} chunks[/green]")
                if result.deleted_uuids:
                    console.print("[cyan]Deleted UUIDs:[/cyan]")
                    for uuid in result.deleted_uuids:
                        console.print(f"  {uuid}")
            else:
                console.print(f"[red]❌ Error: {result.error}[/red]")
                sys.exit(1)
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
    
    asyncio.run(_delete())


@cli.command()
@click.pass_context
def svo_health(ctx: click.Context) -> None:
    """Check SVO chunker health."""
    async def _svo_health():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Checking SVO chunker health...", total=None)
                
                svo_adapter = SVOChunkerAdapter()
                async with svo_adapter:
                    health_data = await svo_adapter.health_check()
                
                progress.update(task, description="Health check completed")
            
            console.print("[cyan]SVO Chunker Health Status:[/cyan]")
            console.print(json.dumps(health_data, indent=2))
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
    
    asyncio.run(_svo_health())


@cli.command()
@click.pass_context
def version(ctx: click.Context) -> None:
    """Show version information."""
    version_info = {
        "vst-cli": "2.0.0",
        "vector-store-client": "2.0.0.0",
        "python": sys.version,
        "author": "Vasily Zdanovskiy",
        "email": "vasilyvz@gmail.com",
        "license": "MIT"
    }
    
    console.print("[cyan]Vector Store CLI (vst-cli)[/cyan]")
    for key, value in version_info.items():
        console.print(f"  {key}: {value}")


if __name__ == '__main__':
    cli()
