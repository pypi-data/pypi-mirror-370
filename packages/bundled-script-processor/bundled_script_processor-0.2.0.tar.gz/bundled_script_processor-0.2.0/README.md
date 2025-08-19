# Bundled Script Processor


An extension of the Amazon SageMaker [ScriptProcessor](https://sagemaker.readthedocs.io/en/stable/api/training/processing.html#sagemaker.processing.ScriptProcessor) 
that adds support for bundling a local `source_dir` (and optional dependencies) into a tarball, uploading it to S3, and 
running it inside SageMaker Processing jobs. This makes it easier to organize your code into directories and 
run it in SageMaker without manually managing uploads.

## 🔍 How it works under the hood

BundledScriptProcessor extends the normal ScriptProcessor flow by injecting an extra packaging step before execution.

1. Bundle creation – It takes your `source_dir` (and any extra dependencies) and compresses them into a `sourcedir.tar.gz`.
2. Upload to S3 – This tarball is uploaded to your SageMaker default bucket and mounted in the container as a `ProcessingInput` named "code".
3. Custom entrypoint – A small `runproc.sh` script is generated and uploaded as a second `ProcessingInput` named "entrypoint". This script:
	• Unpacks `sourcedir.tar.gz`
	• Cleans up the archive
	• Executes your Python entrypoint (main.py by default) with the specified command (e.g. ["python3"]) and any additional arguments.
4. Entrypoint override – Finally, it overrides the default ScriptProcessor entrypoint to point to this generated shell script, so SageMaker runs it automatically when the job starts.

This design keeps the upload/extract/execute logic transparent to you, while still relying on SageMaker’s standard ProcessingJob mechanics.
Additionally, it builds on the existing SageMaker ScriptProcessor API for tasks like compressing and uploading code to S3.

---

## ✨ Features
- Extends `ScriptProcessor` with **`source_dir` support**
- Accepts a **source directory** instead of just a single script
- Supports bundling **dependencies / local folders**
- Automatically generates a lightweight entrypoint script, i.e. `runproc.sh`
- Cleans up temporary artifacts after execution

## 📦 Installation

```bash
pip install bundled-script-processor
```

## 🚀 Usage

### Example directory layout
```
demo_bundled_script_processor/
├─ main.py
├─ task/
│  ├─ callable.py
│  └─ helper.py
├─ common/
│  └─ lib.py
```

### main.py

```python
from bundled_script_processor import BundledScriptProcessor
from sagemaker import Session, get_execution_role

sm_session = Session()
role = get_execution_role(sagemaker_session=sm_session)

script = 'callable.py'
source_dir = f'/home/pmaslov/demo_bundled_script_processor/task'
dep1 = f'/home/pmaslov/demo_bundled_script_processor/common'


processor = BundledScriptProcessor(
    role=role,
    image_uri="123456789012.dkr.ecr.eu-central-1.amazonaws.com/my-image:latest",
    instance_type="ml.m4.xlarge"
)

# Run with a full source directory
processor.run(
    source_dir=source_dir,                # source_dir must contain callable.py (will be copied into /opt/ml/processing/input/code/)
    code=script,                          # python callable (python file name) to be executed inside ScriptProcessor
    dependencies=[dep1],                  # optional dependency (folder will be copied into /opt/ml/processing/input/code/)
    arguments=["--hello", "world"]        # optional CLI args
)
```

### task/callable.py
```python
from helper import helloworld
from common.lib import common_helloworld

if __name__ == '__main__':
    print(helloworld())
    print(common_helloworld())
```

### task/helper.py
```python
def helloworld():
    return 'Hello World!'
```

### common/lib.py
```python
def common_helloworld():
    return 'Common Hello World!'
```