# awpr
Library that helps an application report progress to Argo Workflows.


## Installation 
```shell
pip install awpr
```

## Usage
Set the environment variable and run your application:
`ARGO_PROGRESS_FILE=/tmp/progress.txt`

```shell
from awpr.awpr import ArgoWorkflowsProgressReporter

awpr = ArgoWorkflowsProgressReporter()
awpr.set_total_progress(100)
awpr.start_reporting()

awpr.set_current_progress(20)
awpr.set_current_progress(30)
awpr.get_progress_percent()

awpr.set_progress_complete()
awpr.get_progress_percent()
```