from pathlib import Path
from pythainer.examples.installs import realsense2_lib_install_from_src, \
                                        opencv_lib_install_from_src
from pythainer.builders import DockerBuilder, UbuntuDockerBuilder
from pythainer.examples.builders import get_user_gui_builder
from pythainer.examples.runners import camera_runner, gui_runner
from pythainer.runners import ConcreteDockerRunner, DockerRunner


def install_packages_for_opencv(
    builder: DockerBuilder,
) -> None:
    """
    Installs additional packages required for building OpenCV.

    @param builder: The DockerBuilder instance to which the packages will be added.
    """
    builder.add_packages(packages=[
        "libtbb-dev",
        "libgtk2.0-dev",
        "libgtk-3-dev",
        "pkg-config",
    ])

def get_builder_with_realsense(
    image_name: str,
    base_image: str = "ubuntu:22.04",
) -> UbuntuDockerBuilder:
    """
    Creates a DockerBuilder instance with the necessary libraries installed for using RealSense cameras.

    @param base_image: The base image to use for the Docker container. Default is "ubuntu:20.04".
    @return: A DockerBuilder instance with the required libraries installed.
    """
    user_name = "user"
    work_dir = "/home/${USER_NAME}/workspace"
    lib_dir = f"{work_dir}/libraries"
    debug_mode = False

    docker_builder = get_user_gui_builder(
        image_name=image_name,
        base_ubuntu_image=base_image,
        user_name=user_name,
        lib_dir=lib_dir,
    )
    docker_builder.space()

    # install realsense
    realsense2_lib_install_from_src(
        builder=docker_builder,
        workdir=lib_dir,
        debug=debug_mode,
    )
    docker_builder.space()

    # install python
    docker_builder.root()
    docker_builder.add_packages(packages=[
        "python3", "python3-venv", "python3-pip", "python3-wheel",
        "python3-numpy",
    ])
    docker_builder.user()
    docker_builder.space()

    # Install dependencies for OpenCV
    docker_builder.root()
    install_packages_for_opencv(docker_builder)
    docker_builder.user()
    # Install OpenCV from source
    opencv_cmake_options = {
        "BUILD_TESTS": "OFF",
        "BUILD_EXAMPLES": "OFF",
        "WITH_NVCUVID": "OFF",
        "WITH_NVCUVENC": "OFF",
    }
    opencv_lib_install_from_src(
        builder=docker_builder,
        workdir=work_dir,
        debug=False,
        commit_main="4.10.0",
        commit_contrib="4.10.0",
        extra_cmake_options=opencv_cmake_options,
    )


    return docker_builder

def buildrun(
    batch: bool
) -> None:
    """
    Builds and runs the Docker container.

    @param batch: Boolean indicating whether to run in batch mode.
    @param gpu_enabled: Boolean indicating whether GPU support is enabled.
    """
    print("BuildRunning:")
    print(f"  batch={batch}")

    docker_workdir_path = Path("/home/user/workspace/workdir/")

    image_name = "camera-realsense-opencv"
    docker_builder = get_builder_with_realsense(
        image_name=image_name
    )

    docker_builder.build()

    docker_runner = ConcreteDockerRunner(
        image=image_name,
        name=image_name,
        environment_variables={},
        volumes={},
        devices=[],
        network="host",
        workdir=docker_workdir_path,
    )
    docker_runner |= camera_runner()
    docker_runner |= gui_runner()
    volume_run_user = {
        "/run/user/1000": "/run/user/1000",
        "/run/dbus/system_bus_socket": "/run/dbus/system_bus_socket",
        "/etc/localtime": "/etc/localtime:ro",
        "/etc/timezone": "/etc/timezone:ro"
    }
    docker_runner |= DockerRunner(
        volumes=volume_run_user
    )

    cmd = docker_runner.get_command()
    print(" ".join(cmd))

    docker_runner.generate_script()

    if not batch:
        docker_runner.run()


if __name__ == "__main__":
    buildrun(
        batch=False
    )
