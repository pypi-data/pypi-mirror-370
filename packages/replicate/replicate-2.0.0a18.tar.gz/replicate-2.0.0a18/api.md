# Collections

Types:

```python
from replicate.types import CollectionListResponse, CollectionGetResponse
```

Methods:

- <code title="get /collections">replicate.collections.<a href="./src/replicate/resources/collections.py">list</a>() -> <a href="./src/replicate/types/collection_list_response.py">SyncCursorURLPage[CollectionListResponse]</a></code>
- <code title="get /collections/{collection_slug}">replicate.collections.<a href="./src/replicate/resources/collections.py">get</a>(\*, collection_slug) -> <a href="./src/replicate/types/collection_get_response.py">CollectionGetResponse</a></code>

# Deployments

Types:

```python
from replicate.types import (
    DeploymentCreateResponse,
    DeploymentUpdateResponse,
    DeploymentListResponse,
    DeploymentGetResponse,
)
```

Methods:

- <code title="post /deployments">replicate.deployments.<a href="./src/replicate/resources/deployments/deployments.py">create</a>(\*\*<a href="src/replicate/types/deployment_create_params.py">params</a>) -> <a href="./src/replicate/types/deployment_create_response.py">DeploymentCreateResponse</a></code>
- <code title="patch /deployments/{deployment_owner}/{deployment_name}">replicate.deployments.<a href="./src/replicate/resources/deployments/deployments.py">update</a>(\*, deployment_owner, deployment_name, \*\*<a href="src/replicate/types/deployment_update_params.py">params</a>) -> <a href="./src/replicate/types/deployment_update_response.py">DeploymentUpdateResponse</a></code>
- <code title="get /deployments">replicate.deployments.<a href="./src/replicate/resources/deployments/deployments.py">list</a>() -> <a href="./src/replicate/types/deployment_list_response.py">SyncCursorURLPage[DeploymentListResponse]</a></code>
- <code title="delete /deployments/{deployment_owner}/{deployment_name}">replicate.deployments.<a href="./src/replicate/resources/deployments/deployments.py">delete</a>(\*, deployment_owner, deployment_name) -> None</code>
- <code title="get /deployments/{deployment_owner}/{deployment_name}">replicate.deployments.<a href="./src/replicate/resources/deployments/deployments.py">get</a>(\*, deployment_owner, deployment_name) -> <a href="./src/replicate/types/deployment_get_response.py">DeploymentGetResponse</a></code>

## Predictions

Methods:

- <code title="post /deployments/{deployment_owner}/{deployment_name}/predictions">replicate.deployments.predictions.<a href="./src/replicate/resources/deployments/predictions.py">create</a>(\*, deployment_owner, deployment_name, \*\*<a href="src/replicate/types/deployments/prediction_create_params.py">params</a>) -> <a href="./src/replicate/types/prediction.py">Prediction</a></code>

# Hardware

Types:

```python
from replicate.types import HardwareListResponse
```

Methods:

- <code title="get /hardware">replicate.hardware.<a href="./src/replicate/resources/hardware.py">list</a>() -> <a href="./src/replicate/types/hardware_list_response.py">HardwareListResponse</a></code>

# Account

Types:

```python
from replicate.types import AccountGetResponse
```

Methods:

- <code title="get /account">replicate.account.<a href="./src/replicate/resources/account.py">get</a>() -> <a href="./src/replicate/types/account_get_response.py">AccountGetResponse</a></code>

# Models

Types:

```python
from replicate.types import (
    ModelCreateResponse,
    ModelListResponse,
    ModelGetResponse,
    ModelSearchResponse,
)
```

Methods:

- <code title="post /models">replicate.models.<a href="./src/replicate/resources/models/models.py">create</a>(\*\*<a href="src/replicate/types/model_create_params.py">params</a>) -> <a href="./src/replicate/types/model_create_response.py">ModelCreateResponse</a></code>
- <code title="get /models">replicate.models.<a href="./src/replicate/resources/models/models.py">list</a>() -> <a href="./src/replicate/types/model_list_response.py">SyncCursorURLPage[ModelListResponse]</a></code>
- <code title="delete /models/{model_owner}/{model_name}">replicate.models.<a href="./src/replicate/resources/models/models.py">delete</a>(\*, model_owner, model_name) -> None</code>
- <code title="get /models/{model_owner}/{model_name}">replicate.models.<a href="./src/replicate/resources/models/models.py">get</a>(\*, model_owner, model_name) -> <a href="./src/replicate/types/model_get_response.py">ModelGetResponse</a></code>
- <code title="query /models">replicate.models.<a href="./src/replicate/resources/models/models.py">search</a>(\*\*<a href="src/replicate/types/model_search_params.py">params</a>) -> <a href="./src/replicate/types/model_search_response.py">SyncCursorURLPage[ModelSearchResponse]</a></code>

## Examples

Methods:

- <code title="get /models/{model_owner}/{model_name}/examples">replicate.models.examples.<a href="./src/replicate/resources/models/examples.py">list</a>(\*, model_owner, model_name) -> <a href="./src/replicate/types/prediction.py">SyncCursorURLPage[Prediction]</a></code>

## Predictions

Methods:

- <code title="post /models/{model_owner}/{model_name}/predictions">replicate.models.predictions.<a href="./src/replicate/resources/models/predictions.py">create</a>(\*, model_owner, model_name, \*\*<a href="src/replicate/types/models/prediction_create_params.py">params</a>) -> <a href="./src/replicate/types/prediction.py">Prediction</a></code>

## Readme

Types:

```python
from replicate.types.models import ReadmeGetResponse
```

Methods:

- <code title="get /models/{model_owner}/{model_name}/readme">replicate.models.readme.<a href="./src/replicate/resources/models/readme.py">get</a>(\*, model_owner, model_name) -> str</code>

## Versions

Types:

```python
from replicate.types.models import VersionListResponse, VersionGetResponse
```

Methods:

- <code title="get /models/{model_owner}/{model_name}/versions">replicate.models.versions.<a href="./src/replicate/resources/models/versions.py">list</a>(\*, model_owner, model_name) -> <a href="./src/replicate/types/models/version_list_response.py">SyncCursorURLPage[VersionListResponse]</a></code>
- <code title="delete /models/{model_owner}/{model_name}/versions/{version_id}">replicate.models.versions.<a href="./src/replicate/resources/models/versions.py">delete</a>(\*, model_owner, model_name, version_id) -> None</code>
- <code title="get /models/{model_owner}/{model_name}/versions/{version_id}">replicate.models.versions.<a href="./src/replicate/resources/models/versions.py">get</a>(\*, model_owner, model_name, version_id) -> <a href="./src/replicate/types/models/version_get_response.py">VersionGetResponse</a></code>

# Predictions

Types:

```python
from replicate.types import Prediction, PredictionOutput, PredictionRequest
```

Methods:

- <code title="post /predictions">replicate.predictions.<a href="./src/replicate/resources/predictions.py">create</a>(\*\*<a href="src/replicate/types/prediction_create_params.py">params</a>) -> <a href="./src/replicate/types/prediction.py">Prediction</a></code>
- <code title="get /predictions">replicate.predictions.<a href="./src/replicate/resources/predictions.py">list</a>(\*\*<a href="src/replicate/types/prediction_list_params.py">params</a>) -> <a href="./src/replicate/types/prediction.py">SyncCursorURLPageWithCreatedFilters[Prediction]</a></code>
- <code title="post /predictions/{prediction_id}/cancel">replicate.predictions.<a href="./src/replicate/resources/predictions.py">cancel</a>(\*, prediction_id) -> <a href="./src/replicate/types/prediction.py">Prediction</a></code>
- <code title="get /predictions/{prediction_id}">replicate.predictions.<a href="./src/replicate/resources/predictions.py">get</a>(\*, prediction_id) -> <a href="./src/replicate/types/prediction.py">Prediction</a></code>

# Trainings

Types:

```python
from replicate.types import (
    TrainingCreateResponse,
    TrainingListResponse,
    TrainingCancelResponse,
    TrainingGetResponse,
)
```

Methods:

- <code title="post /models/{model_owner}/{model_name}/versions/{version_id}/trainings">replicate.trainings.<a href="./src/replicate/resources/trainings.py">create</a>(\*, model_owner, model_name, version_id, \*\*<a href="src/replicate/types/training_create_params.py">params</a>) -> <a href="./src/replicate/types/training_create_response.py">TrainingCreateResponse</a></code>
- <code title="get /trainings">replicate.trainings.<a href="./src/replicate/resources/trainings.py">list</a>() -> <a href="./src/replicate/types/training_list_response.py">SyncCursorURLPage[TrainingListResponse]</a></code>
- <code title="post /trainings/{training_id}/cancel">replicate.trainings.<a href="./src/replicate/resources/trainings.py">cancel</a>(\*, training_id) -> <a href="./src/replicate/types/training_cancel_response.py">TrainingCancelResponse</a></code>
- <code title="get /trainings/{training_id}">replicate.trainings.<a href="./src/replicate/resources/trainings.py">get</a>(\*, training_id) -> <a href="./src/replicate/types/training_get_response.py">TrainingGetResponse</a></code>

# Webhooks

## Default

### Secret

Types:

```python
from replicate.types.webhooks.default import SecretGetResponse
```

Methods:

- <code title="get /webhooks/default/secret">replicate.webhooks.default.secret.<a href="./src/replicate/resources/webhooks/default/secret.py">get</a>() -> <a href="./src/replicate/types/webhooks/default/secret_get_response.py">SecretGetResponse</a></code>

# Files

Types:

```python
from replicate.types import FileCreateResponse, FileListResponse, FileGetResponse
```
