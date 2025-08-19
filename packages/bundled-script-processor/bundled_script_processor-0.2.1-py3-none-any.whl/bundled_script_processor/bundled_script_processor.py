import os
import tempfile
from textwrap import dedent
from typing import List
from pathlib import PurePosixPath
from sagemaker.processing import ScriptProcessor, ProcessingInput
from sagemaker.fw_utils import tar_and_upload_dir


class BundledScriptProcessor(ScriptProcessor):
    """Extends ScriptProcessor functionality by allowing to push a source_dir as a code bundle"""

    bundled_entrypoint_command = ["/bin/bash"]

    def __init__(
        self,
        role,
        image_uri,
        instance_type,
        command=None,
        instance_count=1,
        volume_size_in_gb=30,
        volume_kms_key=None,
        output_kms_key=None,
        max_runtime_in_seconds=None,
        base_job_name=None,
        sagemaker_session=None,
        env=None,
        tags=None,
        network_config=None
    ):
        """Initialize the ``BundledScriptProcessor`` instance.

        The ``BundledScriptProcessor`` handles Amazon SageMaker Processing tasks and extends
        ``ScriptProcessor`` functionality by allowing to push a local source_dir as a code bundle,
        along with any "dependencies", or local folders.

        Args:
            role (str): An AWS IAM role name or ARN. Amazon SageMaker Processing uses
                this role to access AWS resources, such as data stored in Amazon S3.
            image_uri (str): The URI of the Docker image to use for the
                processing jobs (default: None).
            instance_type (str): The type of EC2 instance to use for processing, for
                example, 'ml.c4.xlarge'.
            command ([str]): The command to run, along with any command-line flags
                to *precede* the ```code script```. Example: ["python3", "-v"]. If not
                provided, ["python3"] will be chosen (default: None).
            instance_count (int): The number of instances to run a processing job with (default: 1).
            volume_size_in_gb (int): Size in GB of the EBS volume
                to use for storing data during processing (default: 30).
            volume_kms_key (str): A KMS key for the processing volume (default: None).
            output_kms_key (str): The KMS key ID for processing job outputs (default: None).
            max_runtime_in_seconds (int): Timeout in seconds (default: None).
                After this amount of time, Amazon SageMaker terminates the job,
                regardless of its current status. If `max_runtime_in_seconds` is not
                specified, the default value is 24 hours.
            base_job_name (str): Prefix for processing name. If not specified,
                the processor generates a default job name, based on the
                processing image name and current timestamp (default: None).
            sagemaker_session (:class:`~sagemaker.session.Session`):
                Session object which manages interactions with Amazon SageMaker and
                any other AWS services needed. If not specified, the processor creates
                one using the default AWS configuration chain (default: None).
            env (dict[str, str]): Environment variables to be passed to
                the processing jobs (default: None).
            tags (list[dict]): List of tags to be passed to the processing job
                (default: None). For more, see
                https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html.
            network_config (:class:`~sagemaker.network.NetworkConfig`):
                A :class:`~sagemaker.network.NetworkConfig`
                object that configures network isolation, encryption of
                inter-container traffic, security group IDs, and subnets (default: None).
        """
        if command is None:
            self.command = ["python3"]
        else:
            self.command = command

        self._CODE_CONTAINER_BASE_PATH = "/opt/ml/processing/input/"

        # This subclass uses the "code" input for actual payload (tarball), and the ScriptProcessor parent's
        # functionality ("entrypoint" input) for uploading just a small entrypoint script to invoke it.
        self._CODE_CONTAINER_INPUT_NAME = "entrypoint"

        super(ScriptProcessor, self).__init__(
            role=role,
            image_uri=image_uri,
            instance_count=instance_count,
            instance_type=instance_type,
            volume_size_in_gb=volume_size_in_gb,
            volume_kms_key=volume_kms_key,
            output_kms_key=output_kms_key,
            max_runtime_in_seconds=max_runtime_in_seconds,
            base_job_name=base_job_name,
            sagemaker_session=sagemaker_session,
            env=env,
            tags=tags,
            network_config=network_config,
        )

    def run(
            self,
            source_dir: str,
            code="main.py",
            inputs=None,
            outputs=None,
            arguments=None,
            job_name=None,
            dependencies=None,
            *args,
            **kwargs
    ):
        """Runs a processing job.

        Args:
            source_dir (str): absolute Path to a directory
                with any other processing source code dependencies aside from the entry
                point file (default: None). Structure within this directory is preserved
                when processing on Amazon SageMaker (default: None).
            code (str): Filename of a local file inside the root of ``source_dir`` with the
                Python source file which should be executed as the entry point for the job.
            inputs (list[:class:`~sagemaker.processing.ProcessingInput`]): Input files for
                the processing job. These must be provided as
                :class:`~sagemaker.processing.ProcessingInput` objects (default: None).
            outputs (list[:class:`~sagemaker.processing.ProcessingOutput`]): Outputs for
                the processing job. These can be specified as either path strings or
                :class:`~sagemaker.processing.ProcessingOutput` objects (default: None).
            arguments (list[str]): A list of string arguments to be passed to a
                processing job (default: None).
            job_name (str): Processing job name. If not specified, the processor generates
                a default job name, based on the base job name and current timestamp.
            dependencies (list[str]): A list of paths to directories (absolute) with any
                additional files (libraries, Python modules, etc.) that will be exported
                to the container (default: []). The library folders will be
                copied to SageMaker in the same folder where the entrypoint is
                copied (default: None).
        """
        code_s3_uri, script_name = tar_and_upload_dir(
            session=self.sagemaker_session.boto_session,
            bucket=self.sagemaker_session.default_bucket(),
            s3_key_prefix=f"{self._generate_current_job_name(job_name=job_name)}/input/code",
            script=code,
            directory=source_dir,
            dependencies=dependencies
        )

        runproc_sh = self._create_runproc_sh(code)
        patched_inputs = self._patch_inputs_with_payload(inputs, code_s3_uri)

        super().run(
            code=runproc_sh,
            inputs=patched_inputs,
            outputs=outputs,
            arguments=arguments,
            *args, **kwargs
        )

        # Remove temporary runproc.sh file
        if os.path.exists(runproc_sh):
            os.remove(runproc_sh)

    def _create_runproc_sh(self, user_py_script) -> str:
        content = dedent(
            """\
            #!/bin/bash
                
            cd /opt/ml/processing/input/code/
            tar -xzf sourcedir.tar.gz
            
            rm -f sourcedir.tar.gz
            
            # Exit on any error. SageMaker uses error code to mark failed job.
            set -e
            
            {entry_point_command} {entry_point} "$@"
            """
        ).format(
            entry_point_command=" ".join(self.command),
            entry_point=user_py_script
        )
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".sh") as f:
            f.write(content.strip())
            return f.name

    # noinspection PyMethodMayBeStatic
    def _patch_inputs_with_payload(self, inputs, s3_payload) -> List[ProcessingInput]:
        """Add payload sourcedir.tar.gz to processing input.

        This method follows the same mechanism as in ScriptProcessor.
        """

        # Follow the exact same mechanism that ScriptProcessor does, which
        # is to inject the S3 code artifact as a processing input. Note that
        # BundledScriptProcessor takes over /opt/ml/processing/input/code for
        # sourcedir.tar.gz, and let ScriptProcessor place runproc.sh under
        # /opt/ml/processing/input/{self._CODE_CONTAINER_INPUT_NAME}.
        if inputs is None:
            inputs = []
        inputs.append(
            ProcessingInput(
                input_name="code",
                source=s3_payload,
                destination="/opt/ml/processing/input/code/",
            )
        )
        return inputs

    def _set_entrypoint(self, command, user_script_name):
        """BundledScriptProcessor override for setting processing job entrypoint.

        Args:
            command ([str]): Ignored in favor of ``self.bundled_entrypoint_command``
            user_script_name (str): A filename with an extension.
        """

        user_script_location = str(
            PurePosixPath(
                self._CODE_CONTAINER_BASE_PATH, self._CODE_CONTAINER_INPUT_NAME, user_script_name
            )
        )
        self.entrypoint = self.bundled_entrypoint_command + [user_script_location]
