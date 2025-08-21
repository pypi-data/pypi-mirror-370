"""Mapping utilities between dbt models and Lightdash explores"""

import logging
from typing import Dict, Optional, List, Tuple
from functools import lru_cache

from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.config.config import LightdashConfig

logger = logging.getLogger(__name__)


class ModelExploreMapper:
    """Maps between dbt model names and Lightdash explore names"""
    
    def __init__(self, client: LightdashAPIClient):
        self.client = client
        self._explore_cache: Optional[List[Dict]] = None
        self._model_to_explore_map: Optional[Dict[str, str]] = None
        self._explore_to_model_map: Optional[Dict[str, str]] = None
        
    async def refresh_cache(self) -> None:
        """Refresh the explore cache from Lightdash"""
        try:
            self._explore_cache = await self.client.list_explores()
            self._build_mappings()
            logger.info(f"Cached {len(self._explore_cache)} explores")
        except Exception as e:
            logger.error(f"Failed to refresh explore cache: {e}")
            self._explore_cache = []
            self._model_to_explore_map = {}
            self._explore_to_model_map = {}
    
    def _build_mappings(self) -> None:
        """Build bidirectional mappings between models and explores"""
        self._model_to_explore_map = {}
        self._explore_to_model_map = {}
        
        if not self._explore_cache:
            return
        
        for explore in self._explore_cache:
            explore_name = explore.get('name', '')
            base_table = explore.get('baseTable', '')
            
            # Direct mapping from base table
            if base_table:
                self._model_to_explore_map[base_table] = explore_name
                self._explore_to_model_map[explore_name] = base_table
            
            # Also map the explore name as a model name (common pattern)
            self._model_to_explore_map[explore_name] = explore_name
            
            # Handle common naming patterns
            # e.g., 'orders' model might be 'orders_explore' in Lightdash
            if explore_name.endswith('_explore'):
                model_name = explore_name[:-8]  # Remove '_explore'
                self._model_to_explore_map[model_name] = explore_name
            
            # Handle plural/singular conversions
            if explore_name.endswith('s'):
                singular = explore_name[:-1]
                self._model_to_explore_map[singular] = explore_name
            else:
                plural = explore_name + 's'
                self._model_to_explore_map[plural] = explore_name
    
    async def get_explore_for_model(self, model_name: str) -> Optional[str]:
        """Get the Lightdash explore name for a dbt model"""
        if self._model_to_explore_map is None:
            await self.refresh_cache()
        
        # Direct lookup
        explore = self._model_to_explore_map.get(model_name)
        if explore:
            return explore
        
        # Case-insensitive lookup
        lower_model = model_name.lower()
        for model, explore in self._model_to_explore_map.items():
            if model.lower() == lower_model:
                return explore
        
        # Fuzzy matching - find explores containing the model name
        for explore in self._explore_cache or []:
            explore_name = explore.get('name', '').lower()
            if lower_model in explore_name or explore_name in lower_model:
                return explore.get('name')
        
        return None
    
    async def get_model_for_explore(self, explore_name: str) -> Optional[str]:
        """Get the dbt model name for a Lightdash explore"""
        if self._explore_to_model_map is None:
            await self.refresh_cache()
        
        return self._explore_to_model_map.get(explore_name, explore_name)
    
    async def find_explores_for_metrics(self, metric_names: List[str]) -> Dict[str, List[str]]:
        """Find which explores contain the specified metrics"""
        if self._explore_cache is None:
            await self.refresh_cache()
        
        metric_to_explores: Dict[str, List[str]] = {}
        
        for metric in metric_names:
            metric_to_explores[metric] = []
            metric_lower = metric.lower()
            
            for explore in self._explore_cache or []:
                explore_name = explore.get('name', '')
                fields = explore.get('fields', {})
                
                # Check if metric exists in this explore
                for field_name, field_data in fields.items():
                    if field_data.get('fieldType') == 'metric':
                        if field_name.lower() == metric_lower or metric_lower in field_name.lower():
                            metric_to_explores[metric].append(explore_name)
                            break
        
        return metric_to_explores
    
    async def suggest_explore(self, model_or_table_hint: Optional[str] = None, 
                            metrics: Optional[List[str]] = None) -> Optional[str]:
        """Suggest the best explore based on hints"""
        # If we have a model/table hint, try that first
        if model_or_table_hint:
            explore = await self.get_explore_for_model(model_or_table_hint)
            if explore:
                return explore
        
        # If we have metrics, find explores containing them
        if metrics:
            metric_explores = await self.find_explores_for_metrics(metrics)
            
            # Find explore that contains all metrics
            explore_counts: Dict[str, int] = {}
            for metric, explores in metric_explores.items():
                for explore in explores:
                    explore_counts[explore] = explore_counts.get(explore, 0) + 1
            
            # Return explore with most matching metrics
            if explore_counts:
                best_explore = max(explore_counts.items(), key=lambda x: x[1])
                if best_explore[1] == len(metrics):  # Contains all metrics
                    return best_explore[0]
        
        return None
    
    async def get_explore_info(self, explore_name: str) -> Optional[Dict]:
        """Get detailed information about an explore"""
        if self._explore_cache is None:
            await self.refresh_cache()
        
        for explore in self._explore_cache or []:
            if explore.get('name') == explore_name:
                return explore
        
        return None
    
    def get_cached_explores(self) -> List[Dict]:
        """Get all cached explores"""
        return self._explore_cache or []
    
    def clear_cache(self) -> None:
        """Clear the explore cache"""
        self._explore_cache = None
        self._model_to_explore_map = None
        self._explore_to_model_map = None


# Global mapper instance cache
_mapper_instances: Dict[str, ModelExploreMapper] = {}


async def get_model_explore_mapper(config: LightdashConfig) -> ModelExploreMapper:
    """Get or create a mapper instance for the given configuration"""
    # Use project_id as cache key
    cache_key = config.project_id
    
    if cache_key not in _mapper_instances:
        client = LightdashAPIClient(config)
        mapper = ModelExploreMapper(client)
        await mapper.refresh_cache()
        _mapper_instances[cache_key] = mapper
    
    return _mapper_instances[cache_key]


def clear_all_mappers() -> None:
    """Clear all cached mapper instances"""
    for mapper in _mapper_instances.values():
        mapper.clear_cache()
    _mapper_instances.clear()