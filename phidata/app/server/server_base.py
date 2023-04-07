from pathlib import Path
from typing import Optional, Dict, Any, List, Union

from phidata.app.phidata_app import PhidataApp, PhidataAppArgs, WorkspaceVolumeType
from phidata.k8s.enums.service_type import ServiceType
from phidata.k8s.enums.image_pull_policy import ImagePullPolicy
from phidata.k8s.enums.restart_policy import RestartPolicy
from phidata.utils.log import logger


class ServerBaseArgs(PhidataAppArgs):
    name: str = "server"
    version: str = "1"
    enabled: bool = True

    # -*- Image Configuration
    image_name: str = "phidata/server"
    image_tag: str = "1.5.0"
    entrypoint: Optional[Union[str, List]] = None
    command: Optional[Union[str, List]] = None

    # -*- AWS Configuration
    ecs_cluster: Optional[Any] = None
    ecs_launch_type: str = "FARGATE"
    ecs_task_cpu: str = "256"
    ecs_task_memory: str = "512"
    ecs_service_count: int = 1
    assign_public_ip: bool = True
    elb: Optional[Any] = None


class ServerBase(PhidataApp):
    def __init__(
        self,
        name: str = "server",
        version: str = "1",
        enabled: bool = True,
        # -*- Image Configuration,
        # Image can be provided as a DockerImage object or as image_name:image_tag
        image: Optional[Any] = None,
        image_name: str = "phidata/server",
        image_tag: str = "1.5.0",
        entrypoint: Optional[Union[str, List]] = None,
        command: Optional[Union[str, List]] = None,
        # Install python dependencies using a requirements.txt file,
        install_requirements: bool = False,
        # Path to the requirements.txt file relative to the workspace_root,
        requirements_file: str = "requirements.txt",
        # -*- Container Configuration,
        container_name: Optional[str] = None,
        # Overwrite the PYTHONPATH env var,
        # which is usually set to the workspace_root_container_path,
        python_path: Optional[str] = None,
        # Add to the PYTHONPATH env var. If python_path is set, this is ignored
        # Does not overwrite the PYTHONPATH env var - adds to it.
        add_python_path: Optional[str] = None,
        # Add labels to the container,
        container_labels: Optional[Dict[str, Any]] = None,
        # Container env passed to the PhidataApp,
        # Add env variables to container env,
        env: Optional[Dict[str, str]] = None,
        # Read env variables from a file in yaml format,
        env_file: Optional[Path] = None,
        # Container secrets,
        # Add secret variables to container env,
        secrets: Optional[Dict[str, str]] = None,
        # Read secret variables from a file in yaml format,
        secrets_file: Optional[Path] = None,
        # Read secret variables from AWS Secrets,
        aws_secrets: Optional[Any] = None,
        # Container ports,
        # Open a container port if open_container_port=True,
        open_container_port: bool = False,
        # Port number on the container,
        container_port: int = 8080,
        # Port name: Only used by the K8sContainer,
        container_port_name: str = "http",
        # Host port: Only used by the DockerContainer,
        container_host_port: int = 8080,
        # Container volumes,
        # Mount the workspace directory on the container,
        mount_workspace: bool = False,
        workspace_volume_name: Optional[str] = None,
        workspace_volume_type: Optional[WorkspaceVolumeType] = None,
        # Path to mount the workspace volume inside the container,
        workspace_volume_container_path: str = "/usr/local/server",
        # How to mount the workspace volume,
        # Option 1: Mount the workspace from the host machine,
        # If None, use the workspace_root_path,
        # Note: This is the default on DockerContainers. We assume that DockerContainers,
        # are running locally on the user's machine so the local workspace_root_path,
        # is mounted to the workspace_volume_container_path,
        workspace_volume_host_path: Optional[str] = None,
        # Option 2: Load the workspace from git using a git-sync sidecar container,
        # This the default on K8sContainers.,
        create_git_sync_sidecar: bool = False,
        # Required to create an initial copy of the workspace,
        create_git_sync_init_container: bool = True,
        git_sync_image_name: str = "k8s.gcr.io/git-sync",
        git_sync_image_tag: str = "v3.1.1",
        git_sync_repo: Optional[str] = None,
        git_sync_branch: Optional[str] = None,
        git_sync_wait: int = 1,
        # -*- Docker configuration,
        # Run container in the background and return a Container object.,
        container_detach: bool = True,
        # Enable auto-removal of the container on daemon side when the container’s process exits.,
        container_auto_remove: bool = True,
        # Remove the container when it has finished running. Default: True.,
        container_remove: bool = True,
        # Username or UID to run commands as inside the container.,
        container_user: Optional[Union[str, int]] = None,
        # Keep STDIN open even if not attached.,
        container_stdin_open: bool = True,
        container_tty: bool = True,
        # Specify a test to perform to check that the container is healthy.,
        container_healthcheck: Optional[Dict[str, Any]] = None,
        # Optional hostname for the container.,
        container_hostname: Optional[str] = None,
        # Platform in the format os[/arch[/variant]].,
        container_platform: Optional[str] = None,
        # Path to the working directory.,
        container_working_dir: Optional[str] = None,
        # Restart the container when it exits. Configured as a dictionary with keys:,
        # Name: One of on-failure, or always.,
        # MaximumRetryCount: Number of times to restart the container on failure.,
        # For example: {"Name": "on-failure", "MaximumRetryCount": 5},
        container_restart_policy_docker: Optional[Dict[str, Any]] = None,
        # Add volumes to DockerContainer,
        # container_volumes is a dictionary which adds the volumes to mount,
        # inside the container. The key is either the host path or a volume name,,
        # and the value is a dictionary with 2 keys:,
        #   bind - The path to mount the volume inside the container,
        #   mode - Either rw to mount the volume read/write, or ro to mount it read-only.,
        # For example:,
        # {,
        #   '/home/user1/': {'bind': '/mnt/vol2', 'mode': 'rw'},,
        #   '/var/www': {'bind': '/mnt/vol1', 'mode': 'ro'},
        # },
        container_volumes_docker: Optional[Dict[str, dict]] = None,
        # Add ports to DockerContainer,
        # The keys of the dictionary are the ports to bind inside the container,,
        # either as an integer or a string in the form port/protocol, where the protocol is either tcp, udp.,
        # The values of the dictionary are the corresponding ports to open on the host, which can be either:,
        #   - The port number, as an integer.,
        #       For example, {'2222/tcp': 3333} will expose port 2222 inside the container as port 3333 on the host.,
        #   - None, to assign a random host port. For example, {'2222/tcp': None}.,
        #   - A tuple of (address, port) if you want to specify the host interface.,
        #       For example, {'1111/tcp': ('127.0.0.1', 1111)}.,
        #   - A list of integers, if you want to bind multiple host ports to a single container port.,
        #       For example, {'1111/tcp': [1234, 4567]}.,
        container_ports_docker: Optional[Dict[str, Any]] = None,
        # -*- K8s configuration,
        # K8s Deployment configuration,
        replicas: int = 1,
        pod_name: Optional[str] = None,
        deploy_name: Optional[str] = None,
        secret_name: Optional[str] = None,
        configmap_name: Optional[str] = None,
        # Type: ImagePullPolicy,
        image_pull_policy: Optional[ImagePullPolicy] = None,
        pod_annotations: Optional[Dict[str, str]] = None,
        pod_node_selector: Optional[Dict[str, str]] = None,
        # Type: RestartPolicy,
        deploy_restart_policy: Optional[RestartPolicy] = None,
        deploy_labels: Optional[Dict[str, Any]] = None,
        termination_grace_period_seconds: Optional[int] = None,
        # How to spread the deployment across a topology,
        # Key to spread the pods across,
        topology_spread_key: Optional[str] = None,
        # The degree to which pods may be unevenly distributed,
        topology_spread_max_skew: Optional[int] = None,
        # How to deal with a pod if it doesn't satisfy the spread constraint.,
        topology_spread_when_unsatisfiable: Optional[str] = None,
        # K8s Service Configuration,
        create_service: bool = False,
        service_name: Optional[str] = None,
        # Type: ServiceType,
        service_type: Optional[ServiceType] = None,
        # The port exposed by the service.,
        service_port: int = 8000,
        # The node_port exposed by the service if service_type = ServiceType.NODE_PORT,
        service_node_port: Optional[int] = None,
        # The target_port is the port to access on the pods targeted by the service.,
        # It can be the port number or port name on the pod.,
        service_target_port: Optional[Union[str, int]] = None,
        # Extra ports exposed by the webserver service. Type: List[CreatePort],
        service_ports: Optional[List[Any]] = None,
        # Service labels,
        service_labels: Optional[Dict[str, Any]] = None,
        # Service annotations,
        service_annotations: Optional[Dict[str, str]] = None,
        # If ServiceType == ServiceType.LoadBalancer,
        service_health_check_node_port: Optional[int] = None,
        service_internal_traffic_policy: Optional[str] = None,
        service_load_balancer_class: Optional[str] = None,
        service_load_balancer_ip: Optional[str] = None,
        service_load_balancer_source_ranges: Optional[List[str]] = None,
        service_allocate_load_balancer_node_ports: Optional[bool] = None,
        # K8s RBAC Configuration,
        use_rbac: bool = False,
        # Create a Namespace with name ns_name & default values,
        ns_name: Optional[str] = None,
        # or Provide the full Namespace definition,
        # Type: CreateNamespace,
        namespace: Optional[Any] = None,
        # Create a ServiceAccount with name sa_name & default values,
        sa_name: Optional[str] = None,
        # or Provide the full ServiceAccount definition,
        # Type: CreateServiceAccount,
        service_account: Optional[Any] = None,
        # Create a ClusterRole with name cr_name & default values,
        cr_name: Optional[str] = None,
        # or Provide the full ClusterRole definition,
        # Type: CreateClusterRole,
        cluster_role: Optional[Any] = None,
        # Create a ClusterRoleBinding with name crb_name & default values,
        crb_name: Optional[str] = None,
        # or Provide the full ClusterRoleBinding definition,
        # Type: CreateClusterRoleBinding,
        cluster_role_binding: Optional[Any] = None,
        # Add additional Kubernetes resources to the App,
        # Type: CreateSecret,
        extra_secrets: Optional[List[Any]] = None,
        # Type: CreateConfigMap,
        extra_configmaps: Optional[List[Any]] = None,
        # Type: CreateService,
        extra_services: Optional[List[Any]] = None,
        # Type: CreateDeployment,
        extra_deployments: Optional[List[Any]] = None,
        # Type: CreatePersistentVolume,
        extra_pvs: Optional[List[Any]] = None,
        # Type: CreatePVC,
        extra_pvcs: Optional[List[Any]] = None,
        # Type: CreateContainer,
        extra_containers: Optional[List[Any]] = None,
        # Type: CreateContainer,
        extra_init_containers: Optional[List[Any]] = None,
        # Type: CreatePort,
        extra_ports: Optional[List[Any]] = None,
        # Type: CreateVolume,
        extra_volumes: Optional[List[Any]] = None,
        # Type: CreateStorageClass,
        extra_storage_classes: Optional[List[Any]] = None,
        # Type: CreateCustomObject,
        extra_custom_objects: Optional[List[Any]] = None,
        # Type: CreateCustomResourceDefinition,
        extra_crds: Optional[List[Any]] = None,
        # -*- AWS configuration,
        ecs_cluster: Optional[Any] = None,
        ecs_launch_type: str = "FARGATE",
        ecs_task_cpu: str = "256",
        ecs_task_memory: str = "512",
        ecs_service_count: int = 1,
        assign_public_ip: bool = True,
        elb: Optional[Any] = None,
        aws_subnets: Optional[List[str]] = None,
        aws_security_groups: Optional[List[str]] = None,
        # Other args,
        print_env_on_load: bool = False,
        skip_create: bool = False,
        skip_read: bool = False,
        skip_update: bool = False,
        recreate_on_update: bool = False,
        skip_delete: bool = False,
        wait_for_creation: bool = True,
        wait_for_update: bool = True,
        wait_for_deletion: bool = True,
        waiter_delay: int = 30,
        waiter_max_attempts: int = 50,
        # If True, skip resource creation if active resources with the same name exist.,
        use_cache: bool = True,
        **kwargs,
    ):
        super().__init__()
        try:
            self.args: ServerBaseArgs = ServerBaseArgs(
                name=name,
                version=version,
                enabled=enabled,
                image=image,
                image_name=image_name,
                image_tag=image_tag,
                entrypoint=entrypoint,
                command=command,
                install_requirements=install_requirements,
                requirements_file=requirements_file,
                container_name=container_name,
                python_path=python_path,
                add_python_path=add_python_path,
                container_labels=container_labels,
                env=env,
                env_file=env_file,
                secrets=secrets,
                secrets_file=secrets_file,
                aws_secrets=aws_secrets,
                open_container_port=open_container_port,
                container_port=container_port,
                container_port_name=container_port_name,
                container_host_port=container_host_port,
                mount_workspace=mount_workspace,
                workspace_volume_name=workspace_volume_name,
                workspace_volume_type=workspace_volume_type,
                workspace_volume_container_path=workspace_volume_container_path,
                workspace_volume_host_path=workspace_volume_host_path,
                create_git_sync_sidecar=create_git_sync_sidecar,
                create_git_sync_init_container=create_git_sync_init_container,
                git_sync_image_name=git_sync_image_name,
                git_sync_image_tag=git_sync_image_tag,
                git_sync_repo=git_sync_repo,
                git_sync_branch=git_sync_branch,
                git_sync_wait=git_sync_wait,
                container_detach=container_detach,
                container_auto_remove=container_auto_remove,
                container_remove=container_remove,
                container_user=container_user,
                container_stdin_open=container_stdin_open,
                container_tty=container_tty,
                container_healthcheck=container_healthcheck,
                container_hostname=container_hostname,
                container_platform=container_platform,
                container_working_dir=container_working_dir,
                container_restart_policy_docker=container_restart_policy_docker,
                container_volumes_docker=container_volumes_docker,
                container_ports_docker=container_ports_docker,
                replicas=replicas,
                pod_name=pod_name,
                deploy_name=deploy_name,
                secret_name=secret_name,
                configmap_name=configmap_name,
                image_pull_policy=image_pull_policy,
                pod_annotations=pod_annotations,
                pod_node_selector=pod_node_selector,
                deploy_restart_policy=deploy_restart_policy,
                deploy_labels=deploy_labels,
                termination_grace_period_seconds=termination_grace_period_seconds,
                topology_spread_key=topology_spread_key,
                topology_spread_max_skew=topology_spread_max_skew,
                topology_spread_when_unsatisfiable=topology_spread_when_unsatisfiable,
                create_service=create_service,
                service_name=service_name,
                service_type=service_type,
                service_port=service_port,
                service_node_port=service_node_port,
                service_target_port=service_target_port,
                service_ports=service_ports,
                service_labels=service_labels,
                service_annotations=service_annotations,
                service_health_check_node_port=service_health_check_node_port,
                service_internal_traffic_policy=service_internal_traffic_policy,
                service_load_balancer_class=service_load_balancer_class,
                service_load_balancer_ip=service_load_balancer_ip,
                service_load_balancer_source_ranges=service_load_balancer_source_ranges,
                service_allocate_load_balancer_node_ports=service_allocate_load_balancer_node_ports,
                use_rbac=use_rbac,
                ns_name=ns_name,
                namespace=namespace,
                sa_name=sa_name,
                service_account=service_account,
                cr_name=cr_name,
                cluster_role=cluster_role,
                crb_name=crb_name,
                cluster_role_binding=cluster_role_binding,
                extra_secrets=extra_secrets,
                extra_configmaps=extra_configmaps,
                extra_services=extra_services,
                extra_deployments=extra_deployments,
                extra_pvs=extra_pvs,
                extra_pvcs=extra_pvcs,
                extra_containers=extra_containers,
                extra_init_containers=extra_init_containers,
                extra_ports=extra_ports,
                extra_volumes=extra_volumes,
                extra_storage_classes=extra_storage_classes,
                extra_custom_objects=extra_custom_objects,
                extra_crds=extra_crds,
                ecs_cluster=ecs_cluster,
                ecs_launch_type=ecs_launch_type,
                ecs_task_cpu=ecs_task_cpu,
                ecs_task_memory=ecs_task_memory,
                ecs_service_count=ecs_service_count,
                assign_public_ip=assign_public_ip,
                elb=elb,
                aws_subnets=aws_subnets,
                aws_security_groups=aws_security_groups,
                print_env_on_load=print_env_on_load,
                skip_create=skip_create,
                skip_read=skip_read,
                skip_update=skip_update,
                recreate_on_update=recreate_on_update,
                skip_delete=skip_delete,
                wait_for_creation=wait_for_creation,
                wait_for_update=wait_for_update,
                wait_for_deletion=wait_for_deletion,
                waiter_delay=waiter_delay,
                waiter_max_attempts=waiter_max_attempts,
                use_cache=use_cache,
                extra_kwargs=kwargs,
            )
        except Exception as e:
            logger.error(f"Args for {self.name} are not valid")
            raise

    ######################################################
    ## Docker Resources
    ######################################################

    def get_docker_rg(self, docker_build_context: Any) -> Optional[Any]:
        app_name = self.args.name
        logger.debug(f"Building {app_name} DockerResourceGroup")

        from phidata.constants import (
            PYTHONPATH_ENV_VAR,
            PHIDATA_RUNTIME_ENV_VAR,
            SCRIPTS_DIR_ENV_VAR,
            STORAGE_DIR_ENV_VAR,
            META_DIR_ENV_VAR,
            PRODUCTS_DIR_ENV_VAR,
            NOTEBOOKS_DIR_ENV_VAR,
            WORKFLOWS_DIR_ENV_VAR,
            WORKSPACE_ROOT_ENV_VAR,
            WORKSPACES_MOUNT_ENV_VAR,
            WORKSPACE_CONFIG_DIR_ENV_VAR,
        )
        from phidata.docker.resource.group import (
            DockerNetwork,
            DockerContainer,
            DockerResourceGroup,
            DockerBuildContext,
        )
        from phidata.types.context import ContainerPathContext
        from phidata.utils.common import get_default_volume_name

        if docker_build_context is None or not isinstance(
            docker_build_context, DockerBuildContext
        ):
            logger.error("docker_build_context must be a DockerBuildContext")
            return None

        # Workspace paths
        if self.workspace_root_path is None:
            logger.error("Invalid workspace_root_path")
            return None

        workspace_name = self.workspace_root_path.stem
        container_paths: Optional[ContainerPathContext] = self.get_container_paths()
        if container_paths is None:
            logger.error("Could not build container paths")
            return None
        logger.debug(f"Container Paths: {container_paths.json(indent=2)}")

        # Container pythonpath
        python_path = self.args.python_path
        if python_path is None:
            python_path = "{}{}".format(
                container_paths.workspace_root,
                f":{self.args.add_python_path}" if self.args.add_python_path else "",
            )

        # Container Environment
        container_env: Dict[str, Any] = {
            # Env variables used by data workflows and data assets
            PYTHONPATH_ENV_VAR: python_path,
            PHIDATA_RUNTIME_ENV_VAR: "docker",
            SCRIPTS_DIR_ENV_VAR: container_paths.scripts_dir,
            STORAGE_DIR_ENV_VAR: container_paths.storage_dir,
            META_DIR_ENV_VAR: container_paths.meta_dir,
            PRODUCTS_DIR_ENV_VAR: container_paths.products_dir,
            NOTEBOOKS_DIR_ENV_VAR: container_paths.notebooks_dir,
            WORKFLOWS_DIR_ENV_VAR: container_paths.workflows_dir,
            WORKSPACE_ROOT_ENV_VAR: container_paths.workspace_root,
            WORKSPACES_MOUNT_ENV_VAR: container_paths.workspace_parent,
            WORKSPACE_CONFIG_DIR_ENV_VAR: container_paths.workspace_config_dir,
            "INSTALL_REQUIREMENTS": str(self.args.install_requirements),
            "REQUIREMENTS_FILE_PATH": container_paths.requirements_file,
            "MOUNT_WORKSPACE": str(self.args.mount_workspace),
            # Print env when the container starts
            "PRINT_ENV_ON_LOAD": str(self.args.print_env_on_load),
        }

        # Set aws env vars
        self.set_aws_env_vars(env_dict=container_env)

        # Set container env using env_dict, env_file or secrets_file
        self.set_container_env(container_env=container_env)

        # Container Volumes
        # container_volumes is a dictionary which configures the volumes to mount
        # inside the container. The key is either the host path or a volume name,
        # and the value is a dictionary with 2 keys:
        #   bind - The path to mount the volume inside the container
        #   mode - Either rw to mount the volume read/write, or ro to mount it read-only.
        # For example:
        # {
        #   '/home/user1/': {'bind': '/mnt/vol2', 'mode': 'rw'},
        #   '/var/www': {'bind': '/mnt/vol1', 'mode': 'ro'}
        # }
        container_volumes = self.args.container_volumes_docker or {}
        # Create a volume for the workspace dir
        if self.args.mount_workspace:
            workspace_volume_container_path_str = container_paths.workspace_root

            if (
                self.args.workspace_volume_type is None
                or self.args.workspace_volume_type == WorkspaceVolumeType.HostPath
            ):
                workspace_volume_host_path = (
                    self.args.workspace_volume_host_path
                    or str(self.workspace_root_path)
                )
                logger.debug(f"Mounting: {workspace_volume_host_path}")
                logger.debug(f"\tto: {workspace_volume_container_path_str}")
                container_volumes[workspace_volume_host_path] = {
                    "bind": workspace_volume_container_path_str,
                    "mode": "rw",
                }
            elif self.args.workspace_volume_type == WorkspaceVolumeType.EmptyDir:
                workspace_volume_name = self.args.workspace_volume_name
                if workspace_volume_name is None:
                    if workspace_name is not None:
                        workspace_volume_name = get_default_volume_name(
                            f"spark-{workspace_name}-ws"
                        )
                    else:
                        workspace_volume_name = get_default_volume_name("spark-ws")
                logger.debug(f"Mounting: {workspace_volume_name}")
                logger.debug(f"\tto: {workspace_volume_container_path_str}")
                container_volumes[workspace_volume_name] = {
                    "bind": workspace_volume_container_path_str,
                    "mode": "rw",
                }
            else:
                logger.error(f"{self.args.workspace_volume_type.value} not supported")
                return None

        # Container Ports
        # container_ports is a dictionary which configures the ports to bind
        # inside the container. The key is the port to bind inside the container
        #   either as an integer or a string in the form port/protocol
        # and the value is the corresponding port to open on the host.
        # For example:
        #   {'2222/tcp': 3333} will expose port 2222 inside the container as port 3333 on the host.
        container_ports: Dict[str, int] = self.args.container_ports_docker or {}

        # if open_container_port = True
        if self.args.open_container_port:
            container_ports[
                str(self.args.container_port)
            ] = self.args.container_host_port

        # Create the container
        docker_container = DockerContainer(
            name=self.get_container_name(),
            image=self.get_image_str(),
            entrypoint=self.args.entrypoint,
            command=self.args.command,
            detach=self.args.container_detach,
            auto_remove=self.args.container_auto_remove,
            healthcheck=self.args.container_healthcheck,
            hostname=self.args.container_hostname,
            labels=self.args.container_labels,
            environment=container_env,
            network=docker_build_context.network,
            platform=self.args.container_platform,
            ports=container_ports if len(container_ports) > 0 else None,
            remove=self.args.container_remove,
            restart_policy=self.get_container_restart_policy_docker(),
            stdin_open=self.args.container_stdin_open,
            tty=self.args.container_tty,
            user=self.args.container_user,
            volumes=container_volumes if len(container_volumes) > 0 else None,
            working_dir=self.args.container_working_dir,
            use_cache=self.args.use_cache,
        )

        docker_rg = DockerResourceGroup(
            name=app_name,
            enabled=self.args.enabled,
            network=DockerNetwork(name=docker_build_context.network),
            containers=[docker_container],
            images=[self.args.image] if self.args.image else None,
        )
        return docker_rg

    def init_docker_resource_groups(self, docker_build_context: Any) -> None:
        docker_rg = self.get_docker_rg(docker_build_context)
        if docker_rg is not None:
            from collections import OrderedDict

            if self.docker_resource_groups is None:
                self.docker_resource_groups = OrderedDict()
            self.docker_resource_groups[docker_rg.name] = docker_rg

    ######################################################
    ## K8s Resources
    ######################################################

    def get_k8s_rg(self, k8s_build_context: Any) -> Optional[Any]:
        app_name = self.args.name
        logger.debug(f"Building {app_name} K8sResourceGroup")

        from phidata.constants import (
            PYTHONPATH_ENV_VAR,
            PHIDATA_RUNTIME_ENV_VAR,
            SCRIPTS_DIR_ENV_VAR,
            STORAGE_DIR_ENV_VAR,
            META_DIR_ENV_VAR,
            PRODUCTS_DIR_ENV_VAR,
            NOTEBOOKS_DIR_ENV_VAR,
            WORKFLOWS_DIR_ENV_VAR,
            WORKSPACE_ROOT_ENV_VAR,
            WORKSPACES_MOUNT_ENV_VAR,
            WORKSPACE_CONFIG_DIR_ENV_VAR,
        )
        from phidata.k8s.create.common.port import CreatePort
        from phidata.k8s.create.core.v1.container import CreateContainer
        from phidata.k8s.create.core.v1.volume import (
            CreateVolume,
            HostPathVolumeSource,
            VolumeType,
        )
        from phidata.k8s.create.group import (
            CreateK8sResourceGroup,
            CreateNamespace,
            CreateServiceAccount,
            CreateClusterRole,
            CreateClusterRoleBinding,
            CreateSecret,
            CreateConfigMap,
            CreateStorageClass,
            CreateService,
            CreateDeployment,
            CreateCustomObject,
            CreateCustomResourceDefinition,
            CreatePersistentVolume,
            CreatePVC,
        )
        from phidata.k8s.resource.group import K8sBuildContext
        from phidata.types.context import ContainerPathContext
        from phidata.utils.common import get_default_volume_name

        if k8s_build_context is None or not isinstance(
            k8s_build_context, K8sBuildContext
        ):
            logger.error("k8s_build_context must be a K8sBuildContext")
            return None

        # Workspace paths
        if self.workspace_root_path is None:
            logger.error("Invalid workspace_root_path")
            return None

        workspace_name = self.workspace_root_path.stem
        container_paths: Optional[ContainerPathContext] = self.get_container_paths()
        if container_paths is None:
            logger.error("Could not build container paths")
            return None
        logger.debug(f"Container Paths: {container_paths.json(indent=2)}")

        # Init K8s resources for the CreateK8sResourceGroup
        ns: Optional[CreateNamespace] = self.args.namespace
        sa: Optional[CreateServiceAccount] = self.args.service_account
        cr: Optional[CreateClusterRole] = self.args.cluster_role
        crb: Optional[CreateClusterRoleBinding] = self.args.cluster_role_binding
        secrets: List[CreateSecret] = self.args.extra_secrets or []
        config_maps: List[CreateConfigMap] = self.args.extra_configmaps or []
        services: List[CreateService] = self.args.extra_services or []
        deployments: List[CreateDeployment] = self.args.extra_deployments or []
        pvs: List[CreatePersistentVolume] = self.args.extra_pvs or []
        pvcs: List[CreatePVC] = self.args.extra_pvcs or []
        containers: List[CreateContainer] = self.args.extra_containers or []
        init_containers: List[CreateContainer] = self.args.extra_init_containers or []
        ports: List[CreatePort] = self.args.extra_ports or []
        volumes: List[CreateVolume] = self.args.extra_volumes or []
        storage_classes: List[CreateStorageClass] = (
            self.args.extra_storage_classes or []
        )
        custom_objects: List[CreateCustomObject] = self.args.extra_custom_objects or []
        crds: List[CreateCustomResourceDefinition] = self.args.extra_crds or []

        # Common variables used by all resources
        # Use the Namespace provided with the App or
        # use the default Namespace from the k8s_build_context
        ns_name: str = self.args.ns_name or k8s_build_context.namespace
        sa_name: Optional[str] = (
            self.args.sa_name or k8s_build_context.service_account_name
        )
        common_labels: Optional[Dict[str, str]] = k8s_build_context.labels

        # -*- Use K8s RBAC
        # If use_rbac is True, use separate RBAC for this App
        # Create a namespace, service account, cluster role and cluster role binding
        if self.args.use_rbac:
            # Create Namespace for this App
            if ns is None:
                ns = CreateNamespace(
                    ns=ns_name,
                    app_name=app_name,
                    labels=common_labels,
                )
            ns_name = ns.ns

            # Create Service Account for this App
            if sa is None:
                sa = CreateServiceAccount(
                    sa_name=sa_name or self.get_sa_name(),
                    app_name=app_name,
                    namespace=ns_name,
                )
            sa_name = sa.sa_name

            # Create Cluster Role for this App
            from phidata.k8s.create.rbac_authorization_k8s_io.v1.cluster_role import (
                PolicyRule,
            )

            if cr is None:
                cr = CreateClusterRole(
                    cr_name=self.args.cr_name or self.get_cr_name(),
                    rules=[
                        PolicyRule(
                            api_groups=[""],
                            resources=[
                                "pods",
                                "secrets",
                                "configmaps",
                            ],
                            verbs=[
                                "get",
                                "list",
                                "watch",
                                "create",
                                "update",
                                "patch",
                                "delete",
                            ],
                        ),
                        PolicyRule(
                            api_groups=[""],
                            resources=[
                                "pods/logs",
                            ],
                            verbs=[
                                "get",
                                "list",
                            ],
                        ),
                        # PolicyRule(
                        #     api_groups=[""],
                        #     resources=[
                        #         "pods/exec",
                        #     ],
                        #     verbs=[
                        #         "get",
                        #         "create",
                        #     ],
                        # ),
                    ],
                    app_name=app_name,
                    labels=common_labels,
                )

            # Create ClusterRoleBinding for this App
            if crb is None:
                crb = CreateClusterRoleBinding(
                    crb_name=self.args.crb_name or self.get_crb_name(),
                    cr_name=cr.cr_name,
                    service_account_name=sa.sa_name,
                    app_name=app_name,
                    namespace=ns_name,
                    labels=common_labels,
                )

        # Container pythonpath
        python_path = self.args.python_path
        if python_path is None:
            python_path = "{}{}".format(
                container_paths.workspace_root,
                f":{self.args.add_python_path}" if self.args.add_python_path else "",
            )

        # Container Environment
        container_env: Dict[str, Any] = {
            # Env variables used by data workflows and data assets
            PYTHONPATH_ENV_VAR: python_path,
            PHIDATA_RUNTIME_ENV_VAR: "kubernetes",
            SCRIPTS_DIR_ENV_VAR: container_paths.scripts_dir,
            STORAGE_DIR_ENV_VAR: container_paths.storage_dir,
            META_DIR_ENV_VAR: container_paths.meta_dir,
            PRODUCTS_DIR_ENV_VAR: container_paths.products_dir,
            NOTEBOOKS_DIR_ENV_VAR: container_paths.notebooks_dir,
            WORKFLOWS_DIR_ENV_VAR: container_paths.workflows_dir,
            WORKSPACE_ROOT_ENV_VAR: container_paths.workspace_root,
            WORKSPACES_MOUNT_ENV_VAR: container_paths.workspace_parent,
            WORKSPACE_CONFIG_DIR_ENV_VAR: container_paths.workspace_config_dir,
            "INSTALL_REQUIREMENTS": str(self.args.install_requirements),
            "REQUIREMENTS_FILE_PATH": container_paths.requirements_file,
            "MOUNT_WORKSPACE": str(self.args.mount_workspace),
            # Print env when the container starts
            "PRINT_ENV_ON_LOAD": str(self.args.print_env_on_load),
        }

        # Set aws env vars
        self.set_aws_env_vars(env_dict=container_env)

        # Update the container env using env_file
        env_data_from_file = self.get_env_data()
        if env_data_from_file is not None:
            container_env.update(env_data_from_file)

        # Update the container env with user provided env, this overwrites any existing variables
        if self.args.env is not None and isinstance(self.args.env, dict):
            container_env.update(self.args.env)

        # Create a ConfigMap to set the container env variables which are not Secret
        container_env_cm = CreateConfigMap(
            cm_name=self.args.configmap_name or self.get_configmap_name(),
            app_name=app_name,
            namespace=ns_name,
            data=container_env,
            labels=common_labels,
        )
        config_maps.append(container_env_cm)

        # Create a Secret to set the container env variables which are Secret
        _secret_data = self.get_secret_data()
        if _secret_data is not None:
            container_env_secret = CreateSecret(
                secret_name=self.args.secret_name or self.get_secret_name(),
                app_name=app_name,
                string_data=_secret_data,
                namespace=ns_name,
                labels=common_labels,
            )
            secrets.append(container_env_secret)

        # Container Volumes
        if self.args.mount_workspace:
            workspace_volume_name = self.args.workspace_volume_name
            if workspace_volume_name is None:
                if workspace_name is not None:
                    workspace_volume_name = get_default_volume_name(
                        f"spark-{workspace_name}-ws"
                    )
                else:
                    workspace_volume_name = get_default_volume_name("spark-ws")

            # Mount workspace volume as EmptyDir then use git-sync to sync the workspace from github
            if (
                self.args.workspace_volume_type is None
                or self.args.workspace_volume_type == WorkspaceVolumeType.EmptyDir
            ):
                workspace_parent_container_path_str = container_paths.workspace_parent
                logger.debug(f"Creating EmptyDir")
                logger.debug(f"\tat: {workspace_parent_container_path_str}")
                workspace_volume = CreateVolume(
                    volume_name=workspace_volume_name,
                    app_name=app_name,
                    mount_path=workspace_parent_container_path_str,
                    volume_type=VolumeType.EMPTY_DIR,
                )
                volumes.append(workspace_volume)

                if self.args.create_git_sync_sidecar:
                    if self.args.git_sync_repo is not None:
                        git_sync_env = {
                            "GIT_SYNC_REPO": self.args.git_sync_repo,
                            "GIT_SYNC_ROOT": workspace_parent_container_path_str,
                            "GIT_SYNC_DEST": workspace_name,
                        }
                        if self.args.git_sync_branch is not None:
                            git_sync_env["GIT_SYNC_BRANCH"] = self.args.git_sync_branch
                        if self.args.git_sync_wait is not None:
                            git_sync_env["GIT_SYNC_WAIT"] = str(self.args.git_sync_wait)
                        git_sync_container = CreateContainer(
                            container_name="git-sync",
                            app_name=app_name,
                            image_name=self.args.git_sync_image_name,
                            image_tag=self.args.git_sync_image_tag,
                            env=git_sync_env,
                            envs_from_configmap=[cm.cm_name for cm in config_maps]
                            if len(config_maps) > 0
                            else None,
                            envs_from_secret=[secret.secret_name for secret in secrets]
                            if len(secrets) > 0
                            else None,
                            volumes=[workspace_volume],
                        )
                        containers.append(git_sync_container)

                        if self.args.create_git_sync_init_container:
                            git_sync_init_env: Dict[str, Any] = {
                                "GIT_SYNC_ONE_TIME": True
                            }
                            git_sync_init_env.update(git_sync_env)
                            _git_sync_init_container = CreateContainer(
                                container_name="git-sync-init",
                                app_name=git_sync_container.app_name,
                                image_name=git_sync_container.image_name,
                                image_tag=git_sync_container.image_tag,
                                env=git_sync_init_env,
                                envs_from_configmap=git_sync_container.envs_from_configmap,
                                envs_from_secret=git_sync_container.envs_from_secret,
                                volumes=git_sync_container.volumes,
                            )
                            init_containers.append(_git_sync_init_container)
                    else:
                        logger.error("GIT_SYNC_REPO invalid")

            elif self.args.workspace_volume_type == WorkspaceVolumeType.HostPath:
                workspace_root_path_str = str(self.workspace_root_path)
                workspace_root_container_path_str = container_paths.workspace_root
                logger.debug(f"Mounting: {workspace_root_path_str}")
                logger.debug(f"\tto: {workspace_root_container_path_str}")
                workspace_volume = CreateVolume(
                    volume_name=workspace_volume_name,
                    app_name=app_name,
                    mount_path=workspace_root_container_path_str,
                    volume_type=VolumeType.HOST_PATH,
                    host_path=HostPathVolumeSource(
                        path=workspace_root_path_str,
                    ),
                )
                volumes.append(workspace_volume)

        # Create the ports to open
        if self.args.open_container_port:
            container_port = CreatePort(
                name=self.args.container_port_name,
                container_port=self.args.container_port,
                service_port=self.args.service_port,
                target_port=self.args.service_target_port
                or self.args.container_port_name,
            )
            ports.append(container_port)

        container_labels: Dict[str, Any] = common_labels or {}
        if self.args.container_labels is not None and isinstance(
            self.args.container_labels, dict
        ):
            container_labels.update(self.args.container_labels)

        # Create the Spark container
        spark_container = CreateContainer(
            container_name=self.get_container_name(),
            app_name=app_name,
            image_name=self.args.image_name,
            image_tag=self.args.image_tag,
            # Equivalent to docker images CMD
            args=[self.args.command]
            if isinstance(self.args.command, str)
            else self.args.command,
            # Equivalent to docker images ENTRYPOINT
            command=[self.args.entrypoint]
            if isinstance(self.args.entrypoint, str)
            else self.args.entrypoint,
            image_pull_policy=self.args.image_pull_policy
            or ImagePullPolicy.IF_NOT_PRESENT,
            envs_from_configmap=[cm.cm_name for cm in config_maps]
            if len(config_maps) > 0
            else None,
            envs_from_secret=[secret.secret_name for secret in secrets]
            if len(secrets) > 0
            else None,
            ports=ports if len(ports) > 0 else None,
            volumes=volumes if len(volumes) > 0 else None,
            labels=container_labels,
        )
        containers.insert(0, spark_container)

        # Set default container for kubectl commands
        # https://kubernetes.io/docs/reference/labels-annotations-taints/#kubectl-kubernetes-io-default-container
        pod_annotations = {
            "kubectl.kubernetes.io/default-container": spark_container.container_name,
        }
        if self.args.pod_annotations is not None and isinstance(
            self.args.pod_annotations, dict
        ):
            pod_annotations.update(self.args.pod_annotations)

        deploy_labels: Dict[str, Any] = common_labels or {}
        if self.args.deploy_labels is not None and isinstance(
            self.args.deploy_labels, dict
        ):
            deploy_labels.update(self.args.deploy_labels)

        # Create the deployment
        spark_deployment = CreateDeployment(
            deploy_name=self.get_deploy_name(),
            pod_name=self.get_pod_name(),
            app_name=app_name,
            namespace=ns_name,
            service_account_name=sa_name,
            replicas=self.args.replicas,
            containers=containers,
            init_containers=init_containers if len(init_containers) > 0 else None,
            pod_node_selector=self.args.pod_node_selector,
            restart_policy=self.args.deploy_restart_policy or RestartPolicy.ALWAYS,
            termination_grace_period_seconds=self.args.termination_grace_period_seconds,
            volumes=volumes if len(volumes) > 0 else None,
            labels=deploy_labels,
            pod_annotations=pod_annotations,
            topology_spread_key=self.args.topology_spread_key,
            topology_spread_max_skew=self.args.topology_spread_max_skew,
            topology_spread_when_unsatisfiable=self.args.topology_spread_when_unsatisfiable,
        )
        deployments.append(spark_deployment)

        # Create the services
        if self.args.create_service:
            service_labels: Dict[str, Any] = common_labels or {}
            if self.args.service_labels is not None and isinstance(
                self.args.service_labels, dict
            ):
                service_labels.update(self.args.service_labels)

            _service = CreateService(
                service_name=self.get_service_name(),
                app_name=app_name,
                namespace=ns_name,
                service_account_name=sa_name,
                service_type=self.args.service_type,
                deployment=spark_deployment,
                ports=ports if len(ports) > 0 else None,
                labels=service_labels,
            )
            services.append(_service)

        # Create the K8sResourceGroup
        k8s_resource_group = CreateK8sResourceGroup(
            name=app_name,
            enabled=self.args.enabled,
            ns=ns,
            sa=sa,
            cr=cr,
            crb=crb,
            secrets=secrets if len(secrets) > 0 else None,
            config_maps=config_maps if len(config_maps) > 0 else None,
            storage_classes=storage_classes if len(storage_classes) > 0 else None,
            services=services if len(services) > 0 else None,
            deployments=deployments if len(deployments) > 0 else None,
            custom_objects=custom_objects if len(custom_objects) > 0 else None,
            crds=crds if len(crds) > 0 else None,
            pvs=pvs if len(pvs) > 0 else None,
            pvcs=pvcs if len(pvcs) > 0 else None,
        )

        return k8s_resource_group.create()

    def init_k8s_resource_groups(self, k8s_build_context: Any) -> None:
        k8s_rg = self.get_k8s_rg(k8s_build_context)
        if k8s_rg is not None:
            from collections import OrderedDict

            if self.k8s_resource_groups is None:
                self.k8s_resource_groups = OrderedDict()
            self.k8s_resource_groups[k8s_rg.name] = k8s_rg

    ######################################################
    ## Aws Resources
    ######################################################

    def get_aws_rg(self, aws_build_context: Any) -> Optional[Any]:
        app_name = self.args.name
        logger.debug(f"Building {app_name} AwsResourceGroup")

        from phidata.constants import (
            PYTHONPATH_ENV_VAR,
            PHIDATA_RUNTIME_ENV_VAR,
            SCRIPTS_DIR_ENV_VAR,
            STORAGE_DIR_ENV_VAR,
            META_DIR_ENV_VAR,
            PRODUCTS_DIR_ENV_VAR,
            NOTEBOOKS_DIR_ENV_VAR,
            WORKFLOWS_DIR_ENV_VAR,
            WORKSPACE_ROOT_ENV_VAR,
            WORKSPACES_MOUNT_ENV_VAR,
            WORKSPACE_CONFIG_DIR_ENV_VAR,
        )
        from phidata.aws.resource.group import (
            AwsResourceGroup,
            EcsCluster,
            EcsContainer,
            EcsTaskDefinition,
            EcsService,
            LoadBalancer,
            TargetGroup,
            Listener,
            Subnet,
        )
        from phidata.types.context import ContainerPathContext

        # Workspace paths
        if self.workspace_root_path is None:
            logger.error("Invalid workspace_root_path")
            return None

        workspace_name = self.workspace_root_path.stem
        container_paths: Optional[ContainerPathContext] = self.get_container_paths(
            add_ws_name_to_container_path=False
        )
        if container_paths is None:
            logger.error("Could not build container paths")
            return None
        logger.debug(f"Container Paths: {container_paths.json(indent=2)}")

        # Container pythonpath
        # python_path = self.args.python_path
        # if python_path is None:
        #     python_path = "{}{}".format(
        #         container_paths.workspace_root,
        #         f":{self.args.add_python_path}" if self.args.add_python_path else "",
        #     )

        # Container Environment
        container_env: Dict[str, Any] = {
            # Env variables used by data workflows and data assets
            # PYTHONPATH_ENV_VAR: python_path,
            PHIDATA_RUNTIME_ENV_VAR: "ecs",
            SCRIPTS_DIR_ENV_VAR: container_paths.scripts_dir,
            STORAGE_DIR_ENV_VAR: container_paths.storage_dir,
            META_DIR_ENV_VAR: container_paths.meta_dir,
            PRODUCTS_DIR_ENV_VAR: container_paths.products_dir,
            NOTEBOOKS_DIR_ENV_VAR: container_paths.notebooks_dir,
            WORKFLOWS_DIR_ENV_VAR: container_paths.workflows_dir,
            WORKSPACE_ROOT_ENV_VAR: container_paths.workspace_root,
            WORKSPACES_MOUNT_ENV_VAR: container_paths.workspace_parent,
            WORKSPACE_CONFIG_DIR_ENV_VAR: container_paths.workspace_config_dir,
            "INSTALL_REQUIREMENTS": str(self.args.install_requirements),
            "REQUIREMENTS_FILE_PATH": container_paths.requirements_file,
            "MOUNT_WORKSPACE": str(self.args.mount_workspace),
            # Print env when the container starts
            "PRINT_ENV_ON_LOAD": str(self.args.print_env_on_load),
        }

        # Set aws env vars
        self.set_aws_env_vars(env_dict=container_env)

        # Set container env using env_dict, env_file or secrets_file
        self.set_container_env(container_env=container_env)

        # -*- Create ECS cluster
        ecs_cluster = self.args.ecs_cluster
        if ecs_cluster is None:
            ecs_cluster = EcsCluster(
                name=f"{app_name}-cluster",
                ecs_cluster_name=app_name,
                capacity_providers=[self.args.ecs_launch_type],
                skip_create=self.args.skip_create,
                skip_delete=self.args.skip_delete,
                wait_for_creation=self.args.wait_for_creation,
                wait_for_deletion=self.args.wait_for_deletion,
            )

        # -*- Create Load Balancer
        load_balancer = self.args.elb
        if load_balancer is None:
            load_balancer = LoadBalancer(
                name=f"{app_name}-lb",
                subnets=self.args.aws_subnets,
                security_groups=self.args.aws_security_groups,
                skip_create=self.args.skip_create,
                skip_delete=self.args.skip_delete,
                wait_for_creation=self.args.wait_for_creation,
                wait_for_deletion=self.args.wait_for_deletion,
            )

        # Get VPC ID from subnets
        vpc_ids = set()
        for subnet in self.args.aws_subnets:
            _vpc = Subnet(id=subnet).get_vpc_id()
            vpc_ids.add(_vpc)
            if len(vpc_ids) != 1:
                raise ValueError("Subnets must be in the same VPC")
        vpc_id = vpc_ids.pop()

        # -*- Create Target Group
        target_group = TargetGroup(
                name=f"{app_name}-tg",
                port=self.get_container_port(),
                protocol="HTTP",
                vpc_id=vpc_id,
                target_type="ip",
                skip_create=self.args.skip_create,
                skip_delete=self.args.skip_delete,
                wait_for_creation=self.args.wait_for_creation,
                wait_for_deletion=self.args.wait_for_deletion,
            )

        # -*- Create Listener
        listener = Listener(
            name=f"{app_name}-listener",
            protocol="HTTP",
            port=80,
            load_balancer=load_balancer,
            target_group=target_group,
            skip_create=self.args.skip_create,
            skip_delete=self.args.skip_delete,
            wait_for_creation=self.args.wait_for_creation,
            wait_for_deletion=self.args.wait_for_deletion,
        )

        # -*- Create ECS Container
        ecs_container = EcsContainer(
            name=app_name,
            image=self.get_image_str(),
            port_mappings=[{"containerPort": self.get_container_port()}],
            command=self.args.command,
            environment=[{"name": k, "value": v} for k, v in container_env.items()],
            log_configuration={
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": app_name,
                    "awslogs-region": self.aws_region,
                    "awslogs-create-group": "true",
                    "awslogs-stream-prefix": app_name,
                },
            },
            skip_create=self.args.skip_create,
            skip_delete=self.args.skip_delete,
            wait_for_creation=self.args.wait_for_creation,
            wait_for_deletion=self.args.wait_for_deletion,
        )

        # -*- Create ECS Task Definition
        ecs_task_definition = EcsTaskDefinition(
            name=f"{app_name}-td",
            family=app_name,
            network_mode="awsvpc",
            cpu=self.args.ecs_task_cpu,
            memory=self.args.ecs_task_memory,
            containers=[ecs_container],
            requires_compatibilities=[self.args.ecs_launch_type],
            skip_create=self.args.skip_create,
            skip_delete=self.args.skip_delete,
            wait_for_creation=self.args.wait_for_creation,
            wait_for_deletion=self.args.wait_for_deletion,
        )

        aws_vpc_config = {}
        if self.args.aws_subnets is not None:
            aws_vpc_config["subnets"] = self.args.aws_subnets
        if self.args.aws_security_groups is not None:
            aws_vpc_config["securityGroups"] = self.args.aws_security_groups
        if self.args.assign_public_ip:
            aws_vpc_config["assignPublicIp"] = "ENABLED"

        # -*- Create ECS Service
        ecs_service = EcsService(
            name=f"{app_name}-service",
            desired_count=self.args.ecs_service_count,
            launch_type=self.args.ecs_launch_type,
            cluster=ecs_cluster,
            task_definition=ecs_task_definition,
            target_group=target_group,
            target_container_name=ecs_container.name,
            target_container_port=self.get_container_port(),
            network_configuration={"awsvpcConfiguration": aws_vpc_config},
            # Force delete the service.
            force_delete=True,
            # Force a new deployment of the service on update.
            force_new_deployment=True,
            skip_create=self.args.skip_create,
            skip_delete=self.args.skip_delete,
            wait_for_creation=self.args.wait_for_creation,
            wait_for_deletion=self.args.wait_for_deletion,
        )

        # -*- Create AwsResourceGroup
        return AwsResourceGroup(
            name=app_name,
            enabled=self.enabled,
            ecs_clusters=[ecs_cluster],
            ecs_task_definitions=[ecs_task_definition],
            ecs_services=[ecs_service],
            load_balancers=[load_balancer],
            target_groups=[target_group],
            listeners=[listener],
        )

    def init_aws_resource_groups(self, aws_build_context: Any) -> None:
        aws_rg = self.get_aws_rg(aws_build_context)
        if aws_rg is not None:
            from collections import OrderedDict

            if self.aws_resource_groups is None:
                self.aws_resource_groups = OrderedDict()
            self.aws_resource_groups[aws_rg.name] = aws_rg
