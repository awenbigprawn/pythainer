#!/usr/bin/env python3
"""
This script runs a ursim in docker
"""
from pythainer.builders import DockerBuilder
from pythainer.runners import ConcreteDockerRunner
import time


def ursim_runner(robot_model: str = "UR10") -> ConcreteDockerRunner:
    """
    Creates and returns a Docker runner for running URsim with the specified robot model.

    @param robot_model: The model of the UR robot to simulate. Valid options are "UR3", "UR5", "UR10", "UR16", "UR20".
    @return: Configured ConcreteDockerRunner instance.
    @raises ValueError: If an invalid robot model is provided.
    """
    if robot_model not in ["UR3", "UR5", "UR10", "UR16", "UR20"]:
        raise ValueError(f"Invalid robot model: {robot_model}")

    docker_runner = ConcreteDockerRunner(
        image="universalrobots/ursim_e-series:5.19",
        name="ursim",
        environment_variables={"ROBOT_MODEL": robot_model},
        other_options=[
            "--publish",
            "5900:5900",
            "--publish",
            "6080:6080",
            "--publish",
            "29999:29999",
        ],
        root=True,
    )
    return docker_runner


def ursim_runner2(robot_model: str = "UR10") -> ConcreteDockerRunner:
    """
    Creates and returns a Docker runner for running URsim with the specified robot model.
    This function builds a custom Docker image with additional configurations.

    @param robot_model: The model of the UR robot to simulate. Valid options are "UR3", "UR5", "UR10", "UR16", "UR20".
    @return: Configured ConcreteDockerRunner instance.
    """
    docker_builder = DockerBuilder(tag="urtest", package_manager="apt")
    docker_builder.from_image(tag="universalrobots/ursim_e-series")

    docker_builder.run("mkdir /ursim/.polyscope/")
    docker_builder.run("echo '# test' >> /ursim/.polyscope/security.properties")
    docker_builder.run("echo '#' >> /ursim/.polyscope/security.properties")
    docker_builder.run(
        "echo '#Mon Apr 08 00:12:42 CEST 2024' >> /ursim/.polyscope/security.properties"
    )
    # docker_builder.run("echo 'uiUserProfile=
    # docker_builder.run("echo 'safetyUiUserProfile=
    # docker_builder.run("echo 'dashboardUserProfile=

    docker_builder.build()

    docker_runner = ConcreteDockerRunner(
        image="urtest",
        name="urtest",
        environment_variables={"ROBOT_MODEL": robot_model},
        other_options=[
            "--publish",
            "5900:5900",
            "--publish",
            "6080:6080",
            "--publish",
            "29999:29999",
        ],
        root=True,
        tty=False,
        interactive=False,
    )

    docker_runner.run()  # TODO this must be a background process
    # time.sleep(10)
    # docker_runner.exec(cmd="echo 'safetyUiUserProfile=' >> /ursim/.polyscope/security.properties")
    # time.sleep(1000)

    return docker_runner


if __name__ == "__main__":
    ursim_runner().run()
    # ursim_runner2().run()
