# FluidizeSDK

Methods:

- <code title="get /">client.<a href="./src/fluidize_sdk/_client.py">retrieve_root</a>() -> object</code>

# TestConnection

Types:

```python
from fluidize_sdk.types import TestConnectionCheckResponse
```

Methods:

- <code title="get /test-connection">client.test_connection.<a href="./src/fluidize_sdk/resources/test_connection.py">check</a>() -> <a href="./src/fluidize_sdk/types/test_connection_check_response.py">TestConnectionCheckResponse</a></code>

# Candy

Methods:

- <code title="get /candy">client.candy.<a href="./src/fluidize_sdk/resources/candy.py">list</a>() -> object</code>

# Graph

Types:

```python
from fluidize_sdk.types import (
    GraphEdge,
    GraphNode,
    InsertNodeRequest,
    Parameter,
    GraphRetrieveResponse,
    GraphGetParametersResponse,
    GraphSetParametersResponse,
)
```

Methods:

- <code title="get /graph">client.graph.<a href="./src/fluidize_sdk/resources/graph.py">retrieve</a>(\*\*<a href="src/fluidize_sdk/types/graph_retrieve_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/graph_retrieve_response.py">GraphRetrieveResponse</a></code>
- <code title="delete /graph/delete_edge/{edge_id}">client.graph.<a href="./src/fluidize_sdk/resources/graph.py">delete_edge</a>(edge_id, \*\*<a href="src/fluidize_sdk/types/graph_delete_edge_params.py">params</a>) -> object</code>
- <code title="delete /graph/delete_node/{node_id}">client.graph.<a href="./src/fluidize_sdk/resources/graph.py">delete_node</a>(node_id, \*\*<a href="src/fluidize_sdk/types/graph_delete_node_params.py">params</a>) -> object</code>
- <code title="get /graph/get_parameters/{node_id}">client.graph.<a href="./src/fluidize_sdk/resources/graph.py">get_parameters</a>(node_id, \*\*<a href="src/fluidize_sdk/types/graph_get_parameters_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/graph_get_parameters_response.py">GraphGetParametersResponse</a></code>
- <code title="put /graph/insert_node">client.graph.<a href="./src/fluidize_sdk/resources/graph.py">insert_node</a>(\*\*<a href="src/fluidize_sdk/types/graph_insert_node_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/graph_node.py">GraphNode</a></code>
- <code title="post /graph/set_parameters/{node_id}">client.graph.<a href="./src/fluidize_sdk/resources/graph.py">set_parameters</a>(node_id, \*\*<a href="src/fluidize_sdk/types/graph_set_parameters_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/graph_set_parameters_response.py">GraphSetParametersResponse</a></code>
- <code title="post /graph/sync">client.graph.<a href="./src/fluidize_sdk/resources/graph.py">sync</a>(\*\*<a href="src/fluidize_sdk/types/graph_sync_params.py">params</a>) -> object</code>
- <code title="put /graph/update_node_position">client.graph.<a href="./src/fluidize_sdk/resources/graph.py">update_node_position</a>(\*\*<a href="src/fluidize_sdk/types/graph_update_node_position_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/graph_node.py">GraphNode</a></code>
- <code title="put /graph/upsert_edge">client.graph.<a href="./src/fluidize_sdk/resources/graph.py">upsert_edge</a>(\*\*<a href="src/fluidize_sdk/types/graph_upsert_edge_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/graph_edge.py">GraphEdge</a></code>
- <code title="post /graph/upsert_parameter/{path}">client.graph.<a href="./src/fluidize_sdk/resources/graph.py">upsert_parameter</a>(path, \*\*<a href="src/fluidize_sdk/types/graph_upsert_parameter_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/parameter.py">Parameter</a></code>

# Projects

Types:

```python
from fluidize_sdk.types import ProjectSummary, ProjectListResponse
```

Methods:

- <code title="get /projects/{project_id}">client.projects.<a href="./src/fluidize_sdk/resources/projects.py">retrieve</a>(project_id) -> <a href="./src/fluidize_sdk/types/project_summary.py">ProjectSummary</a></code>
- <code title="get /projects">client.projects.<a href="./src/fluidize_sdk/resources/projects.py">list</a>() -> <a href="./src/fluidize_sdk/types/project_list_response.py">ProjectListResponse</a></code>
- <code title="delete /projects/{project_id}">client.projects.<a href="./src/fluidize_sdk/resources/projects.py">delete</a>(project_id) -> object</code>
- <code title="post /projects/sync">client.projects.<a href="./src/fluidize_sdk/resources/projects.py">sync</a>() -> object</code>
- <code title="put /projects/insert_project">client.projects.<a href="./src/fluidize_sdk/resources/projects.py">upsert</a>(\*\*<a href="src/fluidize_sdk/types/project_upsert_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/project_summary.py">ProjectSummary</a></code>

# Files

Types:

```python
from fluidize_sdk.types import (
    SaveFile,
    SaveFileResponse,
    SignedURL,
    FileGetProjectNodePathResponse,
    FileGetSimulationPathResponse,
    FileListDirectoryResponse,
    FileLoadEditorFileResponse,
)
```

Methods:

- <code title="get /files/fetch-download-signed-url/{file_path}">client.files.<a href="./src/fluidize_sdk/resources/files.py">fetch_download_signed_url</a>(file_path) -> <a href="./src/fluidize_sdk/types/signed_url.py">SignedURL</a></code>
- <code title="get /files/fetch-upload-signed-url/{file_path}">client.files.<a href="./src/fluidize_sdk/resources/files.py">fetch_upload_signed_url</a>(file_path) -> <a href="./src/fluidize_sdk/types/signed_url.py">SignedURL</a></code>
- <code title="get /files/get_project_node_path/">client.files.<a href="./src/fluidize_sdk/resources/files.py">get_project_node_path</a>(\*\*<a href="src/fluidize_sdk/types/file_get_project_node_path_params.py">params</a>) -> str</code>
- <code title="get /files/get_simulation_path/">client.files.<a href="./src/fluidize_sdk/resources/files.py">get_simulation_path</a>(\*\*<a href="src/fluidize_sdk/types/file_get_simulation_path_params.py">params</a>) -> str</code>
- <code title="get /files/list-directory/{file_path}">client.files.<a href="./src/fluidize_sdk/resources/files.py">list_directory</a>(file_path) -> <a href="./src/fluidize_sdk/types/file_list_directory_response.py">FileListDirectoryResponse</a></code>
- <code title="get /files/load-editor-file/{file_path}">client.files.<a href="./src/fluidize_sdk/resources/files.py">load_editor_file</a>(file_path) -> <a href="./src/fluidize_sdk/types/file_load_editor_file_response.py">FileLoadEditorFileResponse</a></code>
- <code title="post /files/save-editor-file">client.files.<a href="./src/fluidize_sdk/resources/files.py">save_editor_file</a>(\*\*<a href="src/fluidize_sdk/types/file_save_editor_file_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/save_file_response.py">SaveFileResponse</a></code>
- <code title="post /files/content/{file_path}">client.files.<a href="./src/fluidize_sdk/resources/files.py">save_file_content</a>(file_path, \*\*<a href="src/fluidize_sdk/types/file_save_file_content_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/save_file_response.py">SaveFileResponse</a></code>
- <code title="get /files/stream-file/{file_path}">client.files.<a href="./src/fluidize_sdk/resources/files.py">stream_file</a>(file_path) -> object</code>

# Runs

Types:

```python
from fluidize_sdk.types import (
    RunStatus,
    RunListResponse,
    RunFetchRunNodesResponse,
    RunGetPropertiesResponse,
    RunRunFlowResponse,
)
```

Methods:

- <code title="post /runs/list_runs">client.runs.<a href="./src/fluidize_sdk/resources/runs/runs.py">list</a>(\*\*<a href="src/fluidize_sdk/types/run_list_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/run_list_response.py">RunListResponse</a></code>
- <code title="get /runs/fetch_run_nodes/{run_folder}">client.runs.<a href="./src/fluidize_sdk/resources/runs/runs.py">fetch_run_nodes</a>(run_folder, \*\*<a href="src/fluidize_sdk/types/run_fetch_run_nodes_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/run_fetch_run_nodes_response.py">RunFetchRunNodesResponse</a></code>
- <code title="get /runs/file/{path}">client.runs.<a href="./src/fluidize_sdk/resources/runs/runs.py">get_file</a>(path) -> None</code>
- <code title="get /runs/get_runs_properties/{run_folder}">client.runs.<a href="./src/fluidize_sdk/resources/runs/runs.py">get_properties</a>(run_folder, \*\*<a href="src/fluidize_sdk/types/run_get_properties_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/run_get_properties_response.py">RunGetPropertiesResponse</a></code>
- <code title="post /runs/run_flow">client.runs.<a href="./src/fluidize_sdk/resources/runs/runs.py">run_flow</a>(\*\*<a href="src/fluidize_sdk/types/run_run_flow_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/run_run_flow_response.py">RunRunFlowResponse</a></code>

## Logs

Methods:

- <code title="get /runs/logs/{run_id}/stream">client.runs.logs.<a href="./src/fluidize_sdk/resources/runs/logs.py">stream</a>(run_id, \*\*<a href="src/fluidize_sdk/types/runs/log_stream_params.py">params</a>) -> object</code>

# Auth

Types:

```python
from fluidize_sdk.types import AuthSessionLoginResponse
```

Methods:

- <code title="post /auth/logout">client.auth.<a href="./src/fluidize_sdk/resources/auth/auth.py">logout</a>() -> None</code>
- <code title="post /auth/session-login">client.auth.<a href="./src/fluidize_sdk/resources/auth/auth.py">session_login</a>(\*\*<a href="src/fluidize_sdk/types/auth_session_login_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/auth_session_login_response.py">AuthSessionLoginResponse</a></code>

## SSH

Types:

```python
from fluidize_sdk.types.auth import SSHConnectResponse
```

Methods:

- <code title="post /auth/ssh/connect">client.auth.ssh.<a href="./src/fluidize_sdk/resources/auth/ssh.py">connect</a>(\*\*<a href="src/fluidize_sdk/types/auth/ssh_connect_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/auth/ssh_connect_response.py">SSHConnectResponse</a></code>
- <code title="post /auth/ssh/disconnect">client.auth.ssh.<a href="./src/fluidize_sdk/resources/auth/ssh.py">disconnect</a>() -> object</code>
- <code title="get /auth/ssh/status">client.auth.ssh.<a href="./src/fluidize_sdk/resources/auth/ssh.py">status</a>() -> object</code>

# ListEnvironments

Types:

```python
from fluidize_sdk.types import ListEnvironmentListResponse
```

Methods:

- <code title="get /list_environments">client.list_environments.<a href="./src/fluidize_sdk/resources/list_environments.py">list</a>() -> <a href="./src/fluidize_sdk/types/list_environment_list_response.py">ListEnvironmentListResponse</a></code>

# UpsertSimulation

Types:

```python
from fluidize_sdk.types import UpsertSimulationCreateResponse
```

Methods:

- <code title="post /upsert_simulation">client.upsert_simulation.<a href="./src/fluidize_sdk/resources/upsert_simulation.py">create</a>(\*\*<a href="src/fluidize_sdk/types/upsert_simulation_create_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/upsert_simulation_create_response.py">UpsertSimulationCreateResponse</a></code>

# Utils

## RetrievalMode

Types:

```python
from fluidize_sdk.types.utils import RetrievalMode
```

Methods:

- <code title="get /utils/retrieval_mode">client.utils.retrieval_mode.<a href="./src/fluidize_sdk/resources/utils/retrieval_mode.py">retrieve</a>() -> <a href="./src/fluidize_sdk/types/utils/retrieval_mode.py">RetrievalMode</a></code>
- <code title="put /utils/retrieval_mode">client.utils.retrieval_mode.<a href="./src/fluidize_sdk/resources/utils/retrieval_mode.py">update</a>(\*\*<a href="src/fluidize_sdk/types/utils/retrieval_mode_update_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/utils/retrieval_mode.py">RetrievalMode</a></code>

# Simulation

Types:

```python
from fluidize_sdk.types import NodeMetadataSimulation, SimulationListSimulationsResponse
```

Methods:

- <code title="get /simulation/list_simulations">client.simulation.<a href="./src/fluidize_sdk/resources/simulation.py">list_simulations</a>(\*\*<a href="src/fluidize_sdk/types/simulation_list_simulations_params.py">params</a>) -> <a href="./src/fluidize_sdk/types/simulation_list_simulations_response.py">SimulationListSimulationsResponse</a></code>
