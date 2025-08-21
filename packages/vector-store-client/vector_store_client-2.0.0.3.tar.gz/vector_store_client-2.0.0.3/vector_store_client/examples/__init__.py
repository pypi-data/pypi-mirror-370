"""
Examples for Vector Store Client.

This package contains examples demonstrating how to use the Vector Store client
for various operations including basic usage, advanced features, and integration
scenarios.

Author: Vasily Zdanovskiy
Email: vasilyvz@gmail.com
License: MIT
Version: 1.0.0
"""

# Basic examples
from .basic_usage import basic_usage_example, simple_text_chunk_example, search_by_text_example
from .advanced_usage import batch_operations_example, error_handling_example, complex_search_example

# Workflow examples
from .full_workflow_example import full_workflow_example, chunking_workflow_example, search_workflow_example
from .deletion_and_maintenance_example import (
    deletion_operations_example, 
    maintenance_operations_example, 
    batch_operations_example as batch_maintenance_example,
    monitoring_and_health_example
)

# Comprehensive examples
from .comprehensive_api_example import comprehensive_api_example

# Specialized examples
from .batch_operations import batch_search_example, batch_deletion_example
from .error_handling import comprehensive_error_handling_example, retry_pattern_example, graceful_degradation_example
from .maintenance_operations import (
    example_find_duplicates, 
    example_cleanup_duplicates, 
    example_cleanup_operations,
    example_reindex_operations, 
    example_force_delete, 
    example_maintenance_health_check,
    example_full_maintenance, 
    example_maintenance_with_filters
)

# Phase 6 optimization examples
from .phase6_optimization_examples import (
    example_streaming_large_datasets, 
    example_bulk_operations, 
    example_backup_and_restore,
    example_data_migration, 
    example_performance_monitoring, 
    example_fallback_strategies
)

# Utility examples
from .utilities_examples import (
    basic_usage_example as text_processing_example, 
    advanced_usage_example as metadata_management_example, 
    batch_operations_example as search_optimization_example,
    statistics_and_analysis_example as data_analysis_example, 
    performance_optimization_example
)

__all__ = [
    # Basic examples
    'basic_usage_example',
    'simple_text_chunk_example', 
    'search_by_text_example',
    
    # Advanced examples
    'batch_operations_example',
    'error_handling_example',
    'complex_search_example',
    
    # Workflow examples
    'full_workflow_example',
    'chunking_workflow_example',
    'search_workflow_example',
    
    # Deletion and maintenance
    'deletion_operations_example',
    'maintenance_operations_example',
    'batch_maintenance_example',
    'monitoring_and_health_example',
    
    # Comprehensive examples
    'comprehensive_api_example',
    
    # Specialized examples
    'batch_search_example',
    'batch_deletion_example',
    'comprehensive_error_handling_example',
    'retry_pattern_example',
    'graceful_degradation_example',
    'example_find_duplicates',
    'example_cleanup_duplicates',
    'example_cleanup_operations',
    'example_reindex_operations',
    'example_force_delete',
    'example_maintenance_health_check',
    'example_full_maintenance',
    'example_maintenance_with_filters',
    
    # Phase 6 optimization
    'example_streaming_large_datasets',
    'example_bulk_operations',
    'example_backup_and_restore',
    'example_data_migration',
    'example_performance_monitoring',
    'example_fallback_strategies',
    
    # Utility examples
    'text_processing_example',
    'metadata_management_example',
    'search_optimization_example',
    'data_analysis_example',
    'performance_optimization_example'
] 