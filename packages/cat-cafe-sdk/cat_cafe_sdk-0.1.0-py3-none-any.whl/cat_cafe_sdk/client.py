"""CAT Cafe SDK client for external experiment integration."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Union
import httpx
import asyncio
import inspect
import json
import warnings
import uuid
from pathlib import Path
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class Experiment:
    """Experiment configuration."""
    __test__ = False  # Tell pytest this is not a test class
    
    name: str
    description: str
    dataset_id: str
    dataset_version: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentResult:
    """A single experiment result."""
    __test__ = False  # Tell pytest this is not a test class
    
    example_id: str
    input_data: Dict[str, Any]
    expected_output: Optional[str]
    actual_output: str
    evaluation_scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class DatasetConfig:
    """Dataset configuration for creation."""
    name: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DatasetExample:
    """Dataset example for creation."""
    input: List[Dict[str, Any]]  # LLM input messages
    expected_output: List[Dict[str, Any]]  # LLM expected output messages
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_trace_id: Optional[str] = None  # Original trace ID
    source_node_id: Optional[str] = None   # Original LLM span node ID


@dataclass
class DatasetImport:
    """Complete dataset with examples for import."""
    name: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    examples: List[DatasetExample] = field(default_factory=list)


@dataclass
class Example:
    """A dataset example retrieved from the API."""
    id: str
    input: List[Dict[str, Any]]  # LLM input messages
    expected_output: List[Dict[str, Any]]  # LLM expected output messages
    source_trace_id: Optional[str] = None
    source_node_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class Dataset:
    """A dataset retrieved from the API."""
    id: str
    name: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    example_count: int = 0
    version: int = 1
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    examples: List[Example] = field(default_factory=list)


@dataclass
class ExperimentDetail:
    """Complete experiment details including metadata and results."""
    experiment_id: str
    name: str
    description: str
    dataset_id: str
    dataset_version: Optional[str]
    tags: List[str]
    metadata: Dict[str, Any]
    status: str
    created_at: str
    completed_at: Optional[str]
    summary: Dict[str, Any]
    created_by: str
    results: List[ExperimentResult]


class CATExperimentClient:
    """Client for running external experiments against CAT."""
    
    def __init__(self, base_url: str = "http://localhost:8000", project_id: str = "default", session = None, cache_dir: Optional[str] = None):
        self.base_url = base_url
        self.project_id = project_id
        self._session: Optional[Any] = session  # For testing or custom sessions
        self.cache_dir = Path(cache_dir) if cache_dir else Path(".cat_cache")
        self.offline_mode = "warn"  # Can be set later
    
    def _build_project_url(self, endpoint: str) -> str:
        """Build project-scoped URL for an endpoint."""
        # Remove leading slash if present
        endpoint = endpoint.lstrip('/')
        return f"/api/projects/{self.project_id}/{endpoint}"
    
    def _make_request(self, method: str, url: str, **kwargs):
        """Make HTTP request using either httpx client or test client."""
        if self._session:
            # Use test client (for testing)
            if method.upper() == "GET":
                return self._session.get(url, **kwargs)
            elif method.upper() == "POST":
                return self._session.post(url, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        else:
            # Use httpx client
            full_url = f"{self.base_url}{url}"
            with httpx.Client() as client:
                if method.upper() == "GET":
                    return client.get(full_url, **kwargs)
                elif method.upper() == "POST":
                    return client.post(full_url, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
    
    def _get_dataset_cache_path(self, dataset_id: str) -> Path:
        """Get the cache file path for a dataset."""
        return self.cache_dir / "datasets" / f"{dataset_id}.json"
    
    def _cache_dataset(self, dataset_id: str, dataset_data: Union[Dict, Dataset]) -> None:
        """Cache dataset data to local file system."""
        cache_path = self._get_dataset_cache_path(dataset_id)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert Dataset object to dict if needed
        if isinstance(dataset_data, Dataset):
            data_to_cache = {
                "id": dataset_data.id,
                "name": dataset_data.name,
                "description": dataset_data.description,
                "tags": dataset_data.tags,
                "metadata": dataset_data.metadata,
                "example_count": dataset_data.example_count,
                "version": dataset_data.version,
                "created_at": dataset_data.created_at,
                "updated_at": dataset_data.updated_at,
                "examples": [
                    {
                        "id": ex.id,
                        "input": ex.input,
                        "expected_output": ex.expected_output,
                        "source_trace_id": ex.source_trace_id,
                        "source_node_id": ex.source_node_id,
                        "metadata": ex.metadata,
                        "tags": ex.tags,
                        "created_at": ex.created_at,
                        "updated_at": ex.updated_at
                    } for ex in dataset_data.examples
                ]
            }
        else:
            data_to_cache = dataset_data
        
        # Add cache metadata
        cache_data = {
            "cached_at": datetime.now().isoformat(),
            "dataset": data_to_cache
        }
        
        with open(cache_path, "w") as f:
            json.dump(cache_data, f, indent=2)
    
    def _get_cached_dataset(self, dataset_id: str, ttl_hours: float = 24) -> Optional[Dataset]:
        """Get dataset from cache if available and not expired."""
        cache_path = self._get_dataset_cache_path(dataset_id)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, "r") as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            cached_at = datetime.fromisoformat(cache_data["cached_at"])
            if ttl_hours != float('inf') and datetime.now() - cached_at > timedelta(hours=ttl_hours):
                return None
            
            # Convert to Dataset object
            dataset_data = cache_data["dataset"]
            examples = []
            for ex_data in dataset_data.get("examples", []):
                example = Example(
                    id=ex_data["id"],
                    input=ex_data["input"],
                    expected_output=ex_data["expected_output"],
                    source_trace_id=ex_data.get("source_trace_id"),
                    source_node_id=ex_data.get("source_node_id"),
                    metadata=ex_data.get("metadata", {}),
                    tags=ex_data.get("tags", []),
                    created_at=ex_data.get("created_at"),
                    updated_at=ex_data.get("updated_at")
                )
                examples.append(example)
            
            dataset = Dataset(
                id=dataset_data["id"],
                name=dataset_data["name"],
                description=dataset_data.get("description"),
                tags=dataset_data.get("tags", []),
                metadata=dataset_data.get("metadata", {}),
                example_count=dataset_data.get("example_count", len(examples)),
                version=dataset_data.get("version", 1),
                created_at=dataset_data.get("created_at"),
                updated_at=dataset_data.get("updated_at"),
                examples=examples
            )
            
            return dataset
            
        except (json.JSONDecodeError, KeyError, ValueError):
            # Invalid cache file
            return None
    
    def is_dataset_stale(self, dataset_id: str) -> bool:
        """Check if the cached dataset is stale (expired or outdated)."""
        cache_path = self._get_dataset_cache_path(dataset_id)
        
        if not cache_path.exists():
            return True
        
        try:
            with open(cache_path, "r") as f:
                cache_data = json.load(f)
            
            cached_at = datetime.fromisoformat(cache_data["cached_at"])
            # Consider stale if older than 24 hours
            return datetime.now() - cached_at > timedelta(hours=24)
            
        except (json.JSONDecodeError, KeyError, ValueError):
            return True
    
    def cache_dataset(self, dataset_id: str, ttl_hours: int = 24) -> None:
        """Explicitly cache a dataset from the server."""
        try:
            dataset = self.fetch_dataset(dataset_id, use_cache=False)  # Force fresh fetch
            self._cache_dataset(dataset_id, dataset)
        except Exception as e:
            if self.offline_mode == "fail":
                raise
            elif self.offline_mode == "warn":
                warnings.warn(f"Failed to cache dataset {dataset_id}: {e}")
    
    def get_cached_dataset(self, dataset_id: str) -> Optional[Dataset]:
        """Get a dataset from cache, regardless of age."""
        return self._get_cached_dataset(dataset_id, ttl_hours=float('inf'))
    
    # Recovery cache methods for experiments
    def _get_experiment_cache_dir(self, experiment_id: str) -> Path:
        """Get the cache directory for an experiment."""
        return self.cache_dir / "experiments" / experiment_id
    
    def _cache_experiment_metadata(self, experiment_id: str, dataset: Dataset, config: Dict[str, Any]) -> None:
        """Cache experiment metadata including full dataset snapshot."""
        cache_dir = self._get_experiment_cache_dir(experiment_id)
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            "experiment_id": experiment_id,
            "cached_at": datetime.now().isoformat(),
            "config": config,
            "dataset": {
                "id": dataset.id,
                "name": dataset.name,
                "description": dataset.description,
                "tags": dataset.tags,
                "metadata": dataset.metadata,
                "example_count": dataset.example_count,
                "version": dataset.version,
                "examples": [
                    {
                        "id": ex.id,
                        "input": ex.input,
                        "expected_output": ex.expected_output,
                        "source_trace_id": ex.source_trace_id,
                        "source_node_id": ex.source_node_id,
                        "metadata": ex.metadata,
                        "tags": ex.tags
                    } for ex in dataset.examples
                ]
            }
        }
        
        with open(cache_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
    
    def _get_cached_experiment_metadata(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get cached experiment metadata if available."""
        metadata_file = self._get_experiment_cache_dir(experiment_id) / "metadata.json"
        
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def _cache_example_result(self, experiment_id: str, example_id: str, result: Dict[str, Any]) -> None:
        """Cache a successful example result."""
        results_dir = self._get_experiment_cache_dir(experiment_id) / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Use atomic write
        result_file = results_dir / f"{example_id}.json"
        temp_file = result_file.with_suffix('.tmp')
        
        result_data = {
            "example_id": example_id,
            "cached_at": datetime.now().isoformat(),
            **result
        }
        
        with open(temp_file, "w") as f:
            json.dump(result_data, f, indent=2)
        
        # Atomic rename
        temp_file.rename(result_file)
        
        # Remove error file if it exists
        error_file = results_dir / f"{example_id}.error"
        if error_file.exists():
            error_file.unlink()
    
    def _cache_example_error(self, experiment_id: str, example_id: str, error: str) -> None:
        """Cache a failed example for retry."""
        results_dir = self._get_experiment_cache_dir(experiment_id) / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        error_file = results_dir / f"{example_id}.error"
        error_data = {
            "example_id": example_id,
            "error": error,
            "failed_at": datetime.now().isoformat()
        }
        
        with open(error_file, "w") as f:
            json.dump(error_data, f, indent=2)
    
    def _get_cached_example_result(self, experiment_id: str, example_id: str) -> Optional[Dict[str, Any]]:
        """Get cached result for an example if available."""
        result_file = self._get_experiment_cache_dir(experiment_id) / "results" / f"{example_id}.json"
        
        if not result_file.exists():
            return None
        
        try:
            with open(result_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def _is_example_completed(self, experiment_id: str, example_id: str) -> bool:
        """Check if an example has been successfully completed."""
        result_file = self._get_experiment_cache_dir(experiment_id) / "results" / f"{example_id}.json"
        return result_file.exists()
    
    def _get_completed_example_ids(self, experiment_id: str) -> set:
        """Get set of completed example IDs."""
        results_dir = self._get_experiment_cache_dir(experiment_id) / "results"
        
        if not results_dir.exists():
            return set()
        
        completed = set()
        for file in results_dir.glob("*.json"):
            # Extract example ID from filename
            completed.add(file.stem)
        
        return completed
    
    def _has_experiment_cache(self, experiment_id: str) -> bool:
        """Check if experiment has existing cache."""
        metadata_file = self._get_experiment_cache_dir(experiment_id) / "metadata.json"
        return metadata_file.exists()
    
    def _mark_experiment_completed(self, experiment_id: str) -> None:
        """Mark an experiment as completed in cache."""
        cache_dir = self._get_experiment_cache_dir(experiment_id)
        cache_dir.mkdir(parents=True, exist_ok=True)
        completed_file = cache_dir / "completed"
        completed_file.write_text(datetime.now().isoformat())
    
    def _clean_experiment_cache(self, experiment_id: str) -> None:
        """Remove experiment cache directory."""
        import shutil
        cache_dir = self._get_experiment_cache_dir(experiment_id)
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    
    def _generate_experiment_id(self) -> str:
        """Generate a unique experiment ID."""
        # Format: exp-YYYY-MM-DD-XXXXXX (date + 6 char random)
        date_str = datetime.now().strftime("%Y-%m-%d")
        random_str = str(uuid.uuid4())[:6]
        return f"exp-{date_str}-{random_str}"
    
    def get_dataset(self, dataset_id: str, version: Optional[str] = None) -> Dict:
        """Fetch dataset examples from CAT server."""
        url = self._build_project_url(f"datasets/{dataset_id}/examples")
        params = {"version": version} if version else {}
        response = self._make_request("GET", url, params=params)
        response.raise_for_status()
        return response.json()
    
    def start_experiment(self, experiment_config: Experiment) -> str:
        """Create experiment record, returns experiment_id."""
        url = self._build_project_url("experiments")
        response = self._make_request("POST", url, json={
            "name": experiment_config.name,
            "description": experiment_config.description,
            "dataset_id": experiment_config.dataset_id,
            "dataset_version": experiment_config.dataset_version,
            "tags": experiment_config.tags,
            "metadata": experiment_config.metadata
        })
        response.raise_for_status()
        return response.json()["experiment_id"]
    
    def get_experiment(self, experiment_id: str) -> Dict:
        """Get experiment details."""
        url = self._build_project_url(f"experiments/{experiment_id}")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()
    
    def submit_results(self, experiment_id: str, results: List[ExperimentResult]):
        """Submit experiment results to CAT server."""
        url = self._build_project_url(f"experiments/{experiment_id}/results")
        results_data = [
            {
                "example_id": r.example_id,
                "input_data": r.input_data,
                "expected_output": r.expected_output,
                "actual_output": r.actual_output,
                "evaluation_scores": r.evaluation_scores,
                "metadata": r.metadata,
                "error": r.error
            } for r in results
        ]
        response = self._make_request("POST", url, json={"results": results_data})
        response.raise_for_status()
    
    def complete_experiment(self, experiment_id: str, summary: Optional[Dict[str, Any]] = None):
        """Mark experiment as completed."""
        url = self._build_project_url(f"experiments/{experiment_id}/complete")
        response = self._make_request("POST", url, json={
            "summary": summary or {}
        })
        response.raise_for_status()
    
    def get_experiment_results(self, experiment_id: str) -> List[Dict]:
        """Get experiment results for an experiment."""
        url = self._build_project_url(f"experiments/{experiment_id}/results")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()["results"]
    
    def list_experiments(self) -> List[Dict]:
        """List all experiments."""
        url = self._build_project_url("experiments")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()["experiments"]
    
    def list_experiments_by_dataset(self, dataset_id: str) -> List[Dict]:
        """List experiments for a specific dataset."""
        url = self._build_project_url(f"datasets/{dataset_id}/experiments")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()["experiments"]
    
    def get_experiment_detail(self, experiment_id: str) -> Dict:
        """Get experiment with its results.
        
        Returns a dict with 'experiment' and 'results' keys.
        """
        url = self._build_project_url(f"experiments/{experiment_id}/detail")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()
    
    def compare_experiments(self, experiment_a: str, experiment_b: str) -> Dict:
        """Compare two experiments side-by-side.
        
        Args:
            experiment_a: ID of the first experiment
            experiment_b: ID of the second experiment
            
        Returns:
            Comparison data including results and summary statistics
        """
        url = self._build_project_url("experiments/compare")
        params = {
            "experiment_a": experiment_a,
            "experiment_b": experiment_b
        }
        response = self._make_request("GET", url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_experiment_timeline(self, dataset_id: str) -> Dict:
        """Get timeline data for experiments on a dataset.
        
        Returns timeline data optimized for visualization including
        aggregated metrics and experiment metadata.
        """
        url = self._build_project_url(f"datasets/{dataset_id}/experiments/timeline")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()
    
    def get_evaluation_metrics(self) -> List[Dict]:
        """Get available evaluation metrics from CAT."""
        url = self._build_project_url("evaluation-metrics")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()["metrics"]
    
    def create_dataset(self, dataset: DatasetConfig) -> str:
        """Create a new dataset and return its ID."""
        url = self._build_project_url("datasets")
        response = self._make_request("POST", url, json={
            "name": dataset.name,
            "description": dataset.description,
            "tags": dataset.tags,
            "metadata": dataset.metadata
        })
        response.raise_for_status()
        return response.json()["id"]
    
    def get_dataset_info(self, dataset_id: str) -> Dict:
        """Get dataset information by ID."""
        url = self._build_project_url(f"datasets/{dataset_id}")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()
    
    def add_dataset_example(self, dataset_id: str, example: DatasetExample) -> str:
        """Add an example to a dataset and return the example ID."""
        url = self._build_project_url(f"datasets/{dataset_id}/examples")
        response = self._make_request("POST", url, json={
            "input": example.input,
            "expected_output": example.expected_output,
            "tags": example.tags,
            "metadata": example.metadata
        })
        response.raise_for_status()
        return response.json()["example_id"]
    
    def get_dataset_examples(self, dataset_id: str, version: Optional[str] = None) -> List[Dict]:
        """Get examples from a dataset."""
        url = self._build_project_url(f"datasets/{dataset_id}/examples")
        params = {"version": version} if version else {}
        response = self._make_request("GET", url, params=params)
        response.raise_for_status()
        return response.json()
    
    def list_datasets(self) -> List[Dict]:
        """List all datasets."""
        url = self._build_project_url("datasets")
        response = self._make_request("GET", url)
        response.raise_for_status()
        return response.json()
    
    def find_dataset_by_name(self, name: str) -> Optional[Dict]:
        """Find a dataset by name. Returns None if not found."""
        datasets = self.list_datasets()
        for dataset in datasets:
            if dataset.get("name") == name:
                return dataset
        return None
    
    def fetch_dataset(self, dataset_id: str, version: Optional[str] = None, use_cache: bool = True, cache_ttl_hours: int = 24) -> Dataset:
        """Fetch a complete dataset with its examples as structured objects.
        
        Args:
            dataset_id: The dataset ID to fetch
            version: Optional specific version to fetch
            use_cache: Whether to use cached version if available
            cache_ttl_hours: How long cached datasets are considered fresh
            
        Returns:
            Dataset object with examples
        """
        # Try to get from cache first if enabled
        if use_cache and version is None:  # Only cache latest version
            cached_dataset = self._get_cached_dataset(dataset_id, ttl_hours=cache_ttl_hours)
            if cached_dataset:
                return cached_dataset
        
        try:
            # Get dataset info
            dataset_info = self.get_dataset_info(dataset_id)
            
            # Get examples
            examples_data = self.get_dataset_examples(dataset_id, version=version)
            
            # Convert examples to structured objects
            examples = []
            for example_data in examples_data:
                example = Example(
                    id=example_data["id"],
                    input=example_data["input"],
                    expected_output=example_data["expected_output"],
                    source_trace_id=example_data.get("source_trace_id"),
                    source_node_id=example_data.get("source_node_id"),
                    metadata=example_data.get("metadata", {}),
                    tags=example_data.get("tags", []),
                    created_at=example_data.get("created_at"),
                    updated_at=example_data.get("updated_at")
                )
                examples.append(example)
            
            # Create structured dataset object
            dataset = Dataset(
                id=dataset_info["id"],
                name=dataset_info["name"],
                description=dataset_info.get("description"),
                tags=dataset_info.get("tags", []),
                metadata=dataset_info.get("metadata", {}),
                example_count=dataset_info.get("example_count", 0),
                version=dataset_info.get("version", 1),
                created_at=dataset_info.get("created_at"),
                updated_at=dataset_info.get("updated_at"),
                examples=examples
            )
            
            # Cache the dataset if caching is enabled
            if use_cache and version is None:
                self._cache_dataset(dataset_id, dataset)
            
            return dataset
            
        except Exception as e:
            # If fetching fails, try cache as fallback
            if use_cache:
                cached_dataset = self._get_cached_dataset(dataset_id, ttl_hours=float('inf'))  # Accept any age
                if cached_dataset:
                    if self.offline_mode == "warn":
                        warnings.warn(f"Failed to fetch dataset from server, using cached version: {e}")
                    return cached_dataset
            
            # Re-raise if no cache available
            raise
    
    def fetch_dataset_by_name(self, name: str) -> Optional[Dataset]:
        """Fetch a complete dataset by name with its examples as structured objects."""
        dataset_info = self.find_dataset_by_name(name)
        if not dataset_info:
            return None
        
        return self.fetch_dataset(dataset_info["id"])
    
    def import_dataset(self, dataset_import: DatasetImport) -> Dict:
        """Import a complete dataset with examples in one API call."""
        url = self._build_project_url("datasets/import")
        
        # Convert DatasetExample objects to dictionaries
        examples_data = []
        for example in dataset_import.examples:
            example_dict = {
                "input": example.input,
                "expected_output": example.expected_output,
                "tags": example.tags,
                "metadata": example.metadata
            }
            # Add source fields if present
            if example.source_trace_id is not None:
                example_dict["source_trace_id"] = example.source_trace_id
            if example.source_node_id is not None:
                example_dict["source_node_id"] = example.source_node_id
            examples_data.append(example_dict)
        
        response = self._make_request("POST", url, json={
            "name": dataset_import.name,
            "description": dataset_import.description,
            "tags": dataset_import.tags,
            "metadata": dataset_import.metadata,
            "examples": examples_data
        })
        response.raise_for_status()
        return response.json()
    
    def run_experiment(
        self,
        dataset: Union[Dataset, str, Dict],
        test_function: Callable,
        evaluators: Optional[List[Callable]] = None,
        metadata_function: Optional[Callable] = None,
        *,
        # Experiment configuration
        experiment_config: Optional[Experiment] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        dataset_id: Optional[str] = None,
        dataset_version: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        # New parameters
        experiment_id: Optional[str] = None,
        max_workers: int = 1,
        cache_dir: Optional[str] = None,
        use_cache: bool = True,
        offline_mode: Optional[str] = None,
        submit_partial: bool = False,
        progress_callback: Optional[Callable] = None,
        clean_cache_on_success: bool = True
    ) -> ExperimentDetail:
        """
        Run an experiment on a dataset with recovery and parallel execution support.
        
        This method only supports synchronous test functions, evaluators, and metadata functions.
        For async components, use run_experiment_async() instead.
        
        Args:
            dataset: Dataset object, dataset ID string, or dict with examples
            test_function: Synchronous function that takes Example and returns output string
            evaluators: List of synchronous functions that take (output, expected) and return (score, reason)
            metadata_function: Synchronous function that takes (example, output) and returns metadata dict
            
            # Experiment configuration (use either experiment_config OR individual parameters):
            experiment_config: Experiment configuration object
            name: Name of the experiment
            description: Description of the experiment
            dataset_id: Dataset ID for the experiment
            dataset_version: Dataset version to use
            tags: Tags for the experiment
            metadata: Metadata for the experiment
            
            # New functionality:
            experiment_id: Specific experiment ID (for recovery), auto-generated if None
            max_workers: Number of parallel workers (1 = sequential)
            cache_dir: Override default cache directory
            use_cache: Whether to use recovery cache
            offline_mode: How to handle offline scenarios ('warn', 'silent', 'fail')
            submit_partial: Submit results incrementally (default: wait for completion)
            progress_callback: Function called with (completed, total, current_example)
            clean_cache_on_success: Remove cache after successful completion
            
        Returns:
            ExperimentDetail: A dataclass containing the complete experiment metadata
            and all results. This allows immediate access to results without needing
            a separate API call.
        """
        # Set cache directory if provided
        if cache_dir:
            old_cache_dir = self.cache_dir
            self.cache_dir = Path(cache_dir)
        
        # Set offline mode if provided
        if offline_mode:
            old_offline_mode = self.offline_mode
            self.offline_mode = offline_mode
        
        try:
            # Generate or use provided experiment ID
            if not experiment_id and use_cache:
                experiment_id = self._generate_experiment_id()
            
            # Handle dataset input types and prepare Dataset object
            dataset_obj = self._prepare_dataset(dataset, use_cache)
            
            # Check for existing cache
            resuming = False
            if experiment_id and use_cache and self._has_experiment_cache(experiment_id):
                resuming = True
                # Load cached dataset
                cached_metadata = self._get_cached_experiment_metadata(experiment_id)
                if cached_metadata:
                    dataset_data = cached_metadata["dataset"]
                    dataset_obj = self._dataset_from_cache_data(dataset_data)
                    if progress_callback:
                        completed = len(self._get_completed_example_ids(experiment_id))
                        progress_callback(completed, len(dataset_obj.examples), None)
            
            # Create experiment configuration
            exp_config = self._create_experiment_config(
                experiment_config, name, description, dataset_id or dataset_obj.id,
                dataset_version, tags, metadata
            )
            
            # Cache experiment metadata if new
            if experiment_id and use_cache and not resuming:
                config_dict = {
                    "name": exp_config.name,
                    "description": exp_config.description,
                    "dataset_id": exp_config.dataset_id,
                    "dataset_version": exp_config.dataset_version,
                    "tags": exp_config.tags,
                    "metadata": exp_config.metadata
                }
                self._cache_experiment_metadata(experiment_id, dataset_obj, config_dict)
            
            # Start experiment on server (if online)
            server_experiment_id = None
            if self._should_create_server_experiment():
                try:
                    server_experiment_id = self.start_experiment(exp_config)
                except Exception as e:
                    if self.offline_mode == "fail":
                        raise
                    elif self.offline_mode == "warn":
                        warnings.warn(f"Failed to create experiment on server: {e}")
            
            # Process examples
            results = []
            
            # Check for async components and raise error
            if (inspect.iscoroutinefunction(test_function) or
                (evaluators and any(inspect.iscoroutinefunction(e) for e in evaluators)) or
                (metadata_function and inspect.iscoroutinefunction(metadata_function))):
                raise TypeError(
                    "Async test functions, evaluators, or metadata functions are not supported in run_experiment. "
                    "Use run_experiment_async() instead for async components."
                )
            
            if max_workers > 1:
                # Parallel execution (sync only)
                results = self._run_parallel_sync(
                    dataset_obj, test_function, evaluators, metadata_function,
                    experiment_id, max_workers, progress_callback
                )
            else:
                # Sequential execution (sync only)
                results = self._run_sequential(
                    dataset_obj, test_function, evaluators, metadata_function,
                    experiment_id, progress_callback
                )
            
            # Calculate summary
            summary = self._calculate_summary(results)
            
            # Submit results to server
            completed_at = None
            if server_experiment_id and results:
                try:
                    self.submit_results(server_experiment_id, results)
                    self.complete_experiment(server_experiment_id, summary)
                    # Get the completed timestamp from server if available
                    try:
                        server_exp = self.get_experiment(server_experiment_id)
                        completed_at = server_exp.get("completed_at")
                    except Exception:
                        pass
                except Exception as e:
                    if self.offline_mode == "fail":
                        raise
                    elif self.offline_mode == "warn":
                        warnings.warn(f"Failed to submit results to server: {e}")
            
            # Mark as completed in cache
            if experiment_id and use_cache:
                self._mark_experiment_completed(experiment_id)
                
                # Clean cache if requested
                if clean_cache_on_success:
                    self._clean_experiment_cache(experiment_id)
            
            # Return ExperimentDetail dataclass
            return ExperimentDetail(
                experiment_id=server_experiment_id or experiment_id or "offline-experiment",
                name=exp_config.name,
                description=exp_config.description,
                dataset_id=exp_config.dataset_id,
                dataset_version=exp_config.dataset_version,
                tags=exp_config.tags,
                metadata=exp_config.metadata,
                status="completed",
                created_at=datetime.now(timezone.utc).isoformat(),
                completed_at=completed_at or datetime.now(timezone.utc).isoformat(),
                summary=summary,
                created_by="sdk",
                results=results
            )
            
        finally:
            # Restore original settings
            if cache_dir:
                self.cache_dir = old_cache_dir
            if offline_mode:
                self.offline_mode = old_offline_mode
    
    async def run_experiment_async(
        self,
        dataset: Union[Dataset, str, Dict],
        test_function: Callable,
        evaluators: Optional[List[Callable]] = None,
        metadata_function: Optional[Callable] = None,
        *,
        # Experiment configuration
        experiment_config: Optional[Experiment] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        dataset_id: Optional[str] = None,
        dataset_version: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        # New parameters
        experiment_id: Optional[str] = None,
        max_workers: int = 1,
        cache_dir: Optional[str] = None,
        use_cache: bool = True,
        offline_mode: Optional[str] = None,
        submit_partial: bool = False,
        progress_callback: Optional[Callable] = None,
        clean_cache_on_success: bool = True
    ) -> ExperimentDetail:
        """
        Async version of run_experiment for use in async contexts (e.g., Jupyter notebooks).
        
        This method avoids calling asyncio.run() and can be awaited directly.
        All parameters are the same as run_experiment.
        
        Returns:
            ExperimentDetail: A dataclass containing the complete experiment metadata
            and all results. This allows immediate access to results without needing
            a separate API call.
        """
        # Set cache directory if provided
        if cache_dir:
            old_cache_dir = self.cache_dir
            self.cache_dir = Path(cache_dir)
        
        # Set offline mode if provided
        if offline_mode:
            old_offline_mode = self.offline_mode
            self.offline_mode = offline_mode
        
        try:
            # Generate or use provided experiment ID
            if not experiment_id and use_cache:
                experiment_id = self._generate_experiment_id()
            
            # Handle dataset input types and prepare Dataset object
            dataset_obj = self._prepare_dataset(dataset, use_cache)
            
            # Check for existing cache
            resuming = False
            if experiment_id and use_cache and self._has_experiment_cache(experiment_id):
                resuming = True
                # Load cached dataset
                cached_metadata = self._get_cached_experiment_metadata(experiment_id)
                if cached_metadata:
                    dataset_data = cached_metadata["dataset"]
                    dataset_obj = self._dataset_from_cache_data(dataset_data)
                    if progress_callback:
                        completed = len(self._get_completed_example_ids(experiment_id))
                        progress_callback(completed, len(dataset_obj.examples), None)
            
            # Create experiment configuration
            exp_config = self._create_experiment_config(
                experiment_config, name, description, dataset_id or dataset_obj.id,
                dataset_version, tags, metadata
            )
            
            # Cache experiment metadata if new
            if experiment_id and use_cache and not resuming:
                config_dict = {
                    "name": exp_config.name,
                    "description": exp_config.description,
                    "dataset_id": exp_config.dataset_id,
                    "dataset_version": exp_config.dataset_version,
                    "tags": exp_config.tags,
                    "metadata": exp_config.metadata
                }
                self._cache_experiment_metadata(experiment_id, dataset_obj, config_dict)
            
            # Start experiment on server (if online)
            server_experiment_id = None
            if self._should_create_server_experiment():
                try:
                    server_experiment_id = self.start_experiment(exp_config)
                except Exception as e:
                    if self.offline_mode == "fail":
                        raise
                    elif self.offline_mode == "warn":
                        warnings.warn(f"Failed to create experiment on server: {e}")
            
            # Process examples
            results = []
            
            # Check if we have any async components
            has_async = (
                inspect.iscoroutinefunction(test_function) or
                (evaluators and any(inspect.iscoroutinefunction(e) for e in evaluators)) or
                (metadata_function and inspect.iscoroutinefunction(metadata_function))
            )
            
            if max_workers > 1:
                # Parallel execution
                if has_async:
                    # Use async parallel for any async components
                    results = await self._run_parallel_async(
                        dataset_obj, test_function, evaluators, metadata_function,
                        experiment_id, max_workers, progress_callback
                    )
                else:
                    # Pure sync - use run_in_executor to avoid blocking
                    loop = asyncio.get_event_loop()
                    results = await loop.run_in_executor(
                        None,
                        self._run_parallel_sync,
                        dataset_obj, test_function, evaluators, metadata_function,
                        experiment_id, max_workers, progress_callback
                    )
            else:
                # Sequential execution
                if has_async:
                    # Use async sequential for any async components
                    results = await self._run_sequential_async(
                        dataset_obj, test_function, evaluators, metadata_function,
                        experiment_id, progress_callback
                    )
                else:
                    # Pure sync - use run_in_executor
                    loop = asyncio.get_event_loop()
                    results = await loop.run_in_executor(
                        None,
                        self._run_sequential,
                        dataset_obj, test_function, evaluators, metadata_function,
                        experiment_id, progress_callback
                    )
            
            # Calculate summary
            summary = self._calculate_summary(results)
            
            # Submit results to server
            completed_at = None
            if server_experiment_id and results:
                try:
                    self.submit_results(server_experiment_id, results)
                    self.complete_experiment(server_experiment_id, summary)
                    # Get the completed timestamp from server if available
                    try:
                        server_exp = self.get_experiment(server_experiment_id)
                        completed_at = server_exp.get("completed_at")
                    except Exception:
                        pass
                except Exception as e:
                    if self.offline_mode == "fail":
                        raise
                    elif self.offline_mode == "warn":
                        warnings.warn(f"Failed to submit results to server: {e}")
            
            # Mark as completed in cache
            if experiment_id and use_cache:
                self._mark_experiment_completed(experiment_id)
                
                # Clean cache if requested
                if clean_cache_on_success:
                    self._clean_experiment_cache(experiment_id)
            
            # Return ExperimentDetail dataclass
            return ExperimentDetail(
                experiment_id=server_experiment_id or experiment_id or "offline-experiment",
                name=exp_config.name,
                description=exp_config.description,
                dataset_id=exp_config.dataset_id,
                dataset_version=exp_config.dataset_version,
                tags=exp_config.tags,
                metadata=exp_config.metadata,
                status="completed",
                created_at=datetime.now(timezone.utc).isoformat(),
                completed_at=completed_at or datetime.now(timezone.utc).isoformat(),
                summary=summary,
                created_by="sdk",
                results=results
            )
            
        finally:
            # Restore original settings
            if cache_dir:
                self.cache_dir = old_cache_dir
            if offline_mode:
                self.offline_mode = old_offline_mode
    
    def _prepare_dataset(self, dataset: Union[Dataset, str, Dict], use_cache: bool) -> Dataset:
        """Prepare dataset object from various input types."""
        if isinstance(dataset, str):
            # Fetch dataset by ID
            return self.fetch_dataset(dataset, use_cache=use_cache)
        elif isinstance(dataset, dict):
            # Convert dict to Dataset object
            return self._dataset_from_dict(dataset)
        else:
            # Already a Dataset object
            return dataset
    
    def _dataset_from_dict(self, dataset_dict: Dict) -> Dataset:
        """Convert a dictionary to a Dataset object."""
        examples = []
        for ex_data in dataset_dict.get("examples", []):
            example = Example(
                id=ex_data.get("id", ""),
                input=ex_data.get("input", []),
                expected_output=ex_data.get("expected_output", []),
                source_trace_id=ex_data.get("source_trace_id"),
                source_node_id=ex_data.get("source_node_id"),
                metadata=ex_data.get("metadata", {}),
                tags=ex_data.get("tags", [])
            )
            examples.append(example)
        
        return Dataset(
            id=dataset_dict.get("id", "unknown"),
            name=dataset_dict.get("name", "Unknown Dataset"),
            description=dataset_dict.get("description"),
            tags=dataset_dict.get("tags", []),
            metadata=dataset_dict.get("metadata", {}),
            example_count=len(examples),
            version=dataset_dict.get("version", 1),
            examples=examples
        )
    
    def _dataset_from_cache_data(self, cache_data: Dict) -> Dataset:
        """Convert cached dataset data to Dataset object."""
        examples = []
        for ex_data in cache_data.get("examples", []):
            example = Example(
                id=ex_data["id"],
                input=ex_data["input"],
                expected_output=ex_data["expected_output"],
                source_trace_id=ex_data.get("source_trace_id"),
                source_node_id=ex_data.get("source_node_id"),
                metadata=ex_data.get("metadata", {}),
                tags=ex_data.get("tags", [])
            )
            examples.append(example)
        
        return Dataset(
            id=cache_data["id"],
            name=cache_data["name"],
            description=cache_data.get("description"),
            tags=cache_data.get("tags", []),
            metadata=cache_data.get("metadata", {}),
            example_count=cache_data.get("example_count", len(examples)),
            version=cache_data.get("version", 1),
            examples=examples
        )
    
    def _create_experiment_config(
        self, experiment_config: Optional[Experiment], name: Optional[str],
        description: Optional[str], dataset_id: str, dataset_version: Optional[str],
        tags: Optional[List[str]], metadata: Optional[Dict[str, Any]]
    ) -> Experiment:
        """Create experiment configuration from parameters."""
        if experiment_config:
            return experiment_config
        
        if not name:
            raise ValueError("Either 'experiment_config' or 'name' parameter must be provided")
        
        return Experiment(
            name=name,
            description=description or "",
            dataset_id=dataset_id,
            dataset_version=dataset_version,
            tags=tags or [],
            metadata=metadata or {}
        )
    
    def _should_create_server_experiment(self) -> bool:
        """Check if we should try to create experiment on server."""
        if self.offline_mode == "fail":
            return True
        # Try to ping server
        try:
            self._make_request("GET", "/health")
            return True
        except Exception:
            return False
    
    def _process_example(
        self, example: Example, test_function: Callable,
        evaluators: Optional[List[Callable]], metadata_function: Optional[Callable],
        experiment_id: Optional[str]
    ) -> ExperimentResult:
        """Process a single example with caching."""
        # Check cache first
        if experiment_id and self._is_example_completed(experiment_id, example.id):
            cached = self._get_cached_example_result(experiment_id, example.id)
            if cached:
                return ExperimentResult(
                    example_id=example.id,
                    input_data={"input": example.input},
                    expected_output=self._format_expected_output(example.expected_output),
                    actual_output=cached.get("output", ""),
                    evaluation_scores=cached.get("scores", {}),
                    metadata=cached.get("metadata", {}),
                    error=cached.get("error")
                )
        
        # Process the example
        try:
            # Run test function
            if inspect.iscoroutinefunction(test_function):
                output = asyncio.run(test_function(example))
            else:
                output = test_function(example)
            
            # Run evaluators
            scores = {}
            if evaluators:
                for evaluator in evaluators:
                    score, reason = evaluator(output, example.expected_output)
                    scores[evaluator.__name__] = score
            
            # Extract metadata
            metadata = {}
            if metadata_function:
                metadata = metadata_function(example, output) or {}
            
            # Cache successful result
            if experiment_id:
                self._cache_example_result(experiment_id, example.id, {
                    "output": output,
                    "scores": scores,
                    "metadata": metadata
                })
            
            return ExperimentResult(
                example_id=example.id,
                input_data={"input": example.input},
                expected_output=self._format_expected_output(example.expected_output),
                actual_output=output,
                evaluation_scores=scores,
                metadata=metadata
            )
            
        except Exception as e:
            # Cache error for retry
            if experiment_id:
                self._cache_example_error(experiment_id, example.id, str(e))
            
            return ExperimentResult(
                example_id=example.id,
                input_data={"input": example.input},
                expected_output=self._format_expected_output(example.expected_output),
                actual_output="",
                error=str(e)
            )
    
    def _format_expected_output(self, expected_output: List[Dict]) -> Optional[str]:
        """Format expected output for result."""
        if not expected_output:
            return None
        if isinstance(expected_output, list) and len(expected_output) > 0:
            return expected_output[0].get("content", str(expected_output))
        return str(expected_output)
    
    def _run_sequential(
        self, dataset: Dataset, test_function: Callable,
        evaluators: Optional[List[Callable]], metadata_function: Optional[Callable],
        experiment_id: Optional[str], progress_callback: Optional[Callable]
    ) -> List[ExperimentResult]:
        """Run examples sequentially."""
        results = []
        total = len(dataset.examples)
        
        for i, example in enumerate(dataset.examples):
            result = self._process_example(
                example, test_function, evaluators, metadata_function, experiment_id
            )
            results.append(result)
            
            if progress_callback:
                progress_callback(i + 1, total, example)
        
        return results
    
    async def _run_sequential_async(
        self, dataset: Dataset, test_function: Callable,
        evaluators: Optional[List[Callable]], metadata_function: Optional[Callable],
        experiment_id: Optional[str], progress_callback: Optional[Callable]
    ) -> List[ExperimentResult]:
        """Run examples sequentially with async support."""
        results = []
        total = len(dataset.examples)
        
        for i, example in enumerate(dataset.examples):
            # Check cache first
            if experiment_id and self._is_example_completed(experiment_id, example.id):
                cached = self._get_cached_example_result(experiment_id, example.id)
                if cached:
                    result = ExperimentResult(
                        example_id=example.id,
                        input_data={"input": example.input},
                        expected_output=self._format_expected_output(example.expected_output),
                        actual_output=cached.get("output", ""),
                        evaluation_scores=cached.get("scores", {}),
                        metadata=cached.get("metadata", {}),
                        error=cached.get("error")
                    )
                    results.append(result)
                    if progress_callback:
                        progress_callback(i + 1, total, example)
                    continue
            
            # Process the example
            try:
                # Run test function
                if inspect.iscoroutinefunction(test_function):
                    output = await test_function(example)
                else:
                    # Run sync function in executor
                    loop = asyncio.get_event_loop()
                    output = await loop.run_in_executor(None, test_function, example)
                
                # Run evaluators
                scores = {}
                if evaluators:
                    for evaluator in evaluators:
                        if inspect.iscoroutinefunction(evaluator):
                            score, reason = await evaluator(output, example.expected_output)
                        else:
                            score, reason = evaluator(output, example.expected_output)
                        scores[evaluator.__name__] = score
                
                # Run metadata function
                metadata = {}
                if metadata_function:
                    if inspect.iscoroutinefunction(metadata_function):
                        metadata = await metadata_function(example, output)
                    else:
                        metadata = metadata_function(example, output)
                
                result = ExperimentResult(
                    example_id=example.id,
                    input_data={"input": example.input},
                    expected_output=self._format_expected_output(example.expected_output),
                    actual_output=output,
                    evaluation_scores=scores,
                    metadata=metadata,
                    error=None
                )
                
                # Cache successful result
                if experiment_id:
                    self._cache_example_result(experiment_id, example.id, {
                        "output": output,
                        "scores": scores,
                        "metadata": metadata
                    })
                
            except Exception as e:
                result = ExperimentResult(
                    example_id=example.id,
                    input_data={"input": example.input},
                    expected_output=self._format_expected_output(example.expected_output),
                    actual_output="",
                    evaluation_scores={},
                    metadata={},
                    error=str(e)
                )
                
                # Cache error
                if experiment_id:
                    self._cache_example_error(experiment_id, example.id, str(e))
            
            results.append(result)
            
            if progress_callback:
                progress_callback(i + 1, total, example)
        
        return results
    
    def _run_parallel_sync(
        self, dataset: Dataset, test_function: Callable,
        evaluators: Optional[List[Callable]], metadata_function: Optional[Callable],
        experiment_id: Optional[str], max_workers: int,
        progress_callback: Optional[Callable]
    ) -> List[ExperimentResult]:
        """Run examples in parallel using ThreadPoolExecutor."""
        results = []
        total = len(dataset.examples)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_example = {
                executor.submit(
                    self._process_example, example, test_function,
                    evaluators, metadata_function, experiment_id
                ): example
                for example in dataset.examples
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_example):
                example = future_to_example[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    if progress_callback:
                        progress_callback(completed, total, example)
                        
                except Exception as e:
                    # Should not happen as _process_example catches exceptions
                    results.append(ExperimentResult(
                        example_id=example.id,
                        input_data={"input": example.input},
                        expected_output=self._format_expected_output(example.expected_output),
                        actual_output="",
                        error=str(e)
                    ))
                    completed += 1
        
        # Sort results to match original order
        example_id_to_idx = {ex.id: i for i, ex in enumerate(dataset.examples)}
        results.sort(key=lambda r: example_id_to_idx.get(r.example_id, 0))
        
        return results
    
    async def _run_parallel_async(
        self, dataset: Dataset, test_function: Callable,
        evaluators: Optional[List[Callable]], metadata_function: Optional[Callable],
        experiment_id: Optional[str], max_workers: int,
        progress_callback: Optional[Callable]
    ) -> List[ExperimentResult]:
        """Run examples in parallel using asyncio."""
        semaphore = asyncio.Semaphore(max_workers)
        completed_count = 0
        total = len(dataset.examples)
        
        async def process_with_semaphore(example):
            nonlocal completed_count
            async with semaphore:
                # Check cache first
                if experiment_id and self._is_example_completed(experiment_id, example.id):
                    cached = self._get_cached_example_result(experiment_id, example.id)
                    if cached:
                        completed_count += 1
                        if progress_callback:
                            progress_callback(completed_count, total, example)
                        return ExperimentResult(
                            example_id=example.id,
                            input_data={"input": example.input},
                            expected_output=self._format_expected_output(example.expected_output),
                            actual_output=cached.get("output", ""),
                            evaluation_scores=cached.get("scores", {}),
                            metadata=cached.get("metadata", {}),
                            error=cached.get("error")
                        )
                
                # Process the example
                try:
                    if inspect.iscoroutinefunction(test_function):
                        output = await test_function(example)
                    else:
                        # Run sync function in executor to avoid blocking
                        loop = asyncio.get_event_loop()
                        output = await loop.run_in_executor(None, test_function, example)
                    
                    # Run evaluators
                    scores = {}
                    if evaluators:
                        for evaluator in evaluators:
                            if inspect.iscoroutinefunction(evaluator):
                                score, reason = await evaluator(output, example.expected_output)
                            else:
                                score, reason = evaluator(output, example.expected_output)
                            scores[evaluator.__name__] = score
                    
                    # Extract metadata
                    metadata = {}
                    if metadata_function:
                        if inspect.iscoroutinefunction(metadata_function):
                            metadata = await metadata_function(example, output) or {}
                        else:
                            metadata = metadata_function(example, output) or {}
                    
                    # Cache result
                    if experiment_id:
                        self._cache_example_result(experiment_id, example.id, {
                            "output": output,
                            "scores": scores,
                            "metadata": metadata
                        })
                    
                    completed_count += 1
                    if progress_callback:
                        progress_callback(completed_count, total, example)
                    
                    return ExperimentResult(
                        example_id=example.id,
                        input_data={"input": example.input},
                        expected_output=self._format_expected_output(example.expected_output),
                        actual_output=output,
                        evaluation_scores=scores,
                        metadata=metadata
                    )
                    
                except Exception as e:
                    if experiment_id:
                        self._cache_example_error(experiment_id, example.id, str(e))
                    
                    completed_count += 1
                    if progress_callback:
                        progress_callback(completed_count, total, example)
                    
                    return ExperimentResult(
                        example_id=example.id,
                        input_data={"input": example.input},
                        expected_output=self._format_expected_output(example.expected_output),
                        actual_output="",
                        error=str(e)
                    )
        
        # Process all examples
        tasks = [process_with_semaphore(example) for example in dataset.examples]
        results = await asyncio.gather(*tasks)
        
        return results
    
    def _submit_experiment_results(
        self, experiment_id: str, results: List[ExperimentResult],
        config: Experiment, submit_partial: bool
    ) -> None:
        """Submit results to server."""
        try:
            if submit_partial:
                # Submit in batches as we go (future enhancement)
                self.submit_results(experiment_id, results)
            else:
                # Submit all at once
                self.submit_results(experiment_id, results)
            
            # Calculate summary
            summary = self._calculate_summary(results)
            
            # Complete the experiment
            self.complete_experiment(experiment_id, summary)
            
        except Exception as e:
            if self.offline_mode == "fail":
                raise
            elif self.offline_mode == "warn":
                warnings.warn(f"Failed to submit results to server: {e}")
    
    def _calculate_summary(self, results: List[ExperimentResult]) -> Dict[str, Any]:
        """Calculate summary statistics from results."""
        total = len(results)
        successful = len([r for r in results if r.error is None])
        
        # Aggregate scores
        score_totals = {}
        score_counts = {}
        
        for result in results:
            if result.error is None:
                for metric, score in result.evaluation_scores.items():
                    if metric not in score_totals:
                        score_totals[metric] = 0
                        score_counts[metric] = 0
                    score_totals[metric] += score
                    score_counts[metric] += 1
        
        # Calculate averages
        score_averages = {}
        for metric, total_score in score_totals.items():
            if score_counts[metric] > 0:
                score_averages[f"{metric}_avg"] = total_score / score_counts[metric]
        
        return {
            "total_examples": total,
            "successful_examples": successful,
            "success_rate": successful / total if total > 0 else 0.0,
            **score_averages
        }
    
    def run_test_on_dataset(
        self, 
        dataset: Union[Dataset, str, Dict], 
        test_function: Callable,
        evaluators: Optional[List[Callable]] = None,
        metadata_function: Optional[Callable] = None,
        *,
        # Experiment config parameters (can be passed directly or via experiment_config)
        experiment_config: Optional[Experiment] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        dataset_id: Optional[str] = None,
        dataset_version: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Convenience function to run experiments on a dataset automatically.
        
        Args:
            dataset: Dataset object with structured examples OR dataset ID string OR dict with examples
            test_function: Function (sync or async) that takes Example object and returns output string
            evaluators: List of evaluation functions that take (actual_output, expected_output) 
                       and return (score, reason) tuple
            metadata_function: Function that takes (example, output) and returns metadata dict
            
            # Experiment configuration (use either experiment_config OR individual parameters):
            experiment_config: Experiment configuration object
            name: Name of the experiment (required if experiment_config not provided)
            description: Description of the experiment
            dataset_id: Dataset ID for the experiment (auto-inferred from dataset if not provided)
            dataset_version: Dataset version to use
            tags: Tags for the experiment
            metadata: Metadata for the experiment
            
        Returns:
            experiment_id: The ID of the completed experiment
            
        Usage Examples:
            # Direct parameters style
            experiment_id = client.run_test_on_dataset(
                dataset="dataset-123",
                test_function=my_test_func,
                name="My Experiment",
                description="Testing with direct params",
                tags=["automated", "test"]
            )
            
            # Configuration object style
            config = Experiment(name="My Experiment", description="Test desc", dataset_id="dataset-123")
            experiment_id = client.run_test_on_dataset(
                dataset="dataset-123",
                test_function=my_test_func,
                experiment_config=config
            )
            
        Note:
            The test_function can be either synchronous or asynchronous. Async functions will be
            automatically detected and run using asyncio.run(). However, async test functions
            cannot be used when run_test_on_dataset is called from within an async context
            (such as pytest with pytest-asyncio). In such cases, use synchronous test functions.
        """
        # Deprecation warning
        warnings.warn(
            "run_test_on_dataset is deprecated and will be removed in a future version. "
            "Please use run_experiment instead, which provides better recovery, parallel execution, "
            "and offline support.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Create Experiment configuration from either experiment_config object or individual parameters
        if experiment_config is not None:
            # Use provided experiment_config object
            experiment_config_obj = experiment_config
        else:
            # Create Experiment from individual parameters
            if name is None:
                raise ValueError("Either 'experiment_config' or 'name' parameter must be provided")
            
            # Auto-infer dataset_id if not provided
            inferred_dataset_id = dataset_id
            if inferred_dataset_id is None:
                if isinstance(dataset, str):
                    inferred_dataset_id = dataset
                elif isinstance(dataset, dict):
                    inferred_dataset_id = dataset.get("id", "unknown")
                else:  # Dataset object
                    inferred_dataset_id = dataset.id
            
            experiment_config_obj = Experiment(
                name=name,
                description=description or "",
                dataset_id=inferred_dataset_id,
                dataset_version=dataset_version,
                tags=tags or [],
                metadata=metadata or {}
            )
        
        # Handle different dataset input types
        if isinstance(dataset, str):
            # Fetch dataset if ID string is provided
            dataset_obj = self.fetch_dataset(dataset)
        elif isinstance(dataset, dict):
            # Convert raw dict to Dataset object for consistency
            examples = []
            for example_data in dataset.get("examples", []):
                example = Example(
                    id=example_data.get("id", ""),
                    input=example_data.get("input", []),
                    expected_output=example_data.get("expected_output", []),
                    source_trace_id=example_data.get("source_trace_id"),
                    source_node_id=example_data.get("source_node_id"),
                    metadata=example_data.get("metadata", {}),
                    tags=example_data.get("tags", []),
                    created_at=example_data.get("created_at"),
                    updated_at=example_data.get("updated_at")
                )
                examples.append(example)
            
            dataset_obj = Dataset(
                id=dataset.get("id", ""),
                name=dataset.get("name", ""),
                description=dataset.get("description"),
                tags=dataset.get("tags", []),
                metadata=dataset.get("metadata", {}),
                example_count=len(examples),
                version=dataset.get("version", 1),
                created_at=dataset.get("created_at"),
                updated_at=dataset.get("updated_at"),
                examples=examples
            )
        else:
            # Assume it's already a Dataset object
            dataset_obj = dataset
        
        # Start the experiment
        experiment_id = self.start_experiment(experiment_config_obj)
        
        try:
            results = []
            
            # Process each example in the dataset
            for example in dataset_obj.examples:
                try:
                    # Run the test function (handle both sync and async functions)
                    if inspect.iscoroutinefunction(test_function):
                        # Async function - handle event loop properly
                        try:
                            # Try to get current event loop
                            asyncio.get_running_loop()
                            # If we're already in an async context, we can't use run_until_complete
                            # This would happen in pytest with pytest-asyncio
                            raise RuntimeError("Cannot use run_until_complete in async context")
                        except RuntimeError:
                            # No running loop or we're in async context
                            try:
                                # Try to run in new event loop
                                actual_output = asyncio.run(test_function(example))
                            except RuntimeError as e:
                                if "cannot be called from a running event loop" in str(e):
                                    # We're in an async context, need to await differently
                                    # For now, we'll raise a helpful error
                                    raise RuntimeError(
                                        "Async test functions are not supported when run_test_on_dataset "
                                        "is called from within an async context (like pytest-asyncio). "
                                        "Please use a synchronous test function instead."
                                    )
                                else:
                                    raise
                    else:
                        # Sync function
                        actual_output = test_function(example)
                    
                    # Calculate evaluation scores
                    evaluation_scores = {}
                    if evaluators:
                        for evaluator in evaluators:
                            evaluator_name = evaluator.__name__
                            expected_output = example.expected_output
                            score, _reason = evaluator(actual_output, expected_output)
                            evaluation_scores[evaluator_name] = score
                    
                    # Extract metadata
                    metadata = {}
                    if metadata_function:
                        metadata_result = metadata_function(example, actual_output)
                        if metadata_result is not None:
                            metadata = metadata_result
                    
                    # Create test case result
                    # Convert expected_output to string if it's a list of messages
                    expected_output_str = None
                    if example.expected_output:
                        if isinstance(example.expected_output, list) and len(example.expected_output) > 0:
                            expected_output_str = example.expected_output[0].get("content", str(example.expected_output))
                        else:
                            expected_output_str = str(example.expected_output)
                    
                    result = ExperimentResult(
                        example_id=example.id or "",
                        input_data={"input": example.input},
                        expected_output=expected_output_str,
                        actual_output=actual_output,
                        evaluation_scores=evaluation_scores or {},
                        metadata=metadata or {}
                    )
                    results.append(result)
                    
                except Exception as e:
                    # Handle errors in test execution
                    # Convert expected_output to string for error case too
                    expected_output_str = None
                    if example.expected_output:
                        if isinstance(example.expected_output, list) and len(example.expected_output) > 0:
                            expected_output_str = example.expected_output[0].get("content", str(example.expected_output))
                        else:
                            expected_output_str = str(example.expected_output)
                    
                    error_result = ExperimentResult(
                        example_id=example.id,
                        input_data={"input": example.input},
                        expected_output=expected_output_str,
                        actual_output="",
                        error=str(e)
                    )
                    results.append(error_result)
            
            # Submit all results
            self.submit_results(experiment_id, results)
            
            # Calculate summary
            total_examples = len(results)
            successful_examples = len([r for r in results if r.error is None])
            success_rate = successful_examples / total_examples if total_examples > 0 else 0.0
            
            # Calculate average scores from evaluators
            score_averages = {}
            if evaluators and successful_examples > 0:
                successful_results = [r for r in results if r.error is None]
                for evaluator in evaluators:
                    evaluator_name = evaluator.__name__
                    scores = [r.evaluation_scores.get(evaluator_name, 0.0) for r in successful_results]
                    if scores:
                        score_averages[f"{evaluator_name}_avg"] = sum(scores) / len(scores)
            
            summary = {
                "total_examples": total_examples,
                "successful_examples": successful_examples,
                "success_rate": success_rate,
                **score_averages
            }
            
            # Complete the test run
            self.complete_experiment(experiment_id, summary)
            
            return experiment_id
            
        except Exception as e:
            # If something goes wrong, still try to complete the run with error
            try:
                self.complete_experiment(experiment_id, {"error": str(e)})
            except Exception:
                pass  # Best effort to complete
            raise

    # Legacy method name for backwards compatibility
    run_experiment_on_dataset = run_test_on_dataset


# Alias for backwards compatibility with examples
CATTestRunClient = CATExperimentClient