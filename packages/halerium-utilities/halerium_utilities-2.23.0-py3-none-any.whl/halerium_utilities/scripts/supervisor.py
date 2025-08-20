import argparse
import logging
import os
import re
import shlex
import shutil
import subprocess
import typing
import uuid


def add_app_to_supervisor(name: str, command: typing.List[str],
                          port: int = None,
                          route: str = None,
                          directory: typing.Union[str, os.PathLike] = None,
                          log_path: typing.Union[str, os.PathLike] = None,
                          startretries=1,
                          autorestart=True):
    """
    Adds an app to the stack of supervised processed.
    The app will not be started automatically. To start it utilize the runner menu.

    Parameters
    ----------
    name: str
        The name of the app
    command: typing.List[str]
        The command with which the app is started.
        For example ["streamlit", "hello"]
    port: int (optional)
        The port under which the app is reachable.
    route: str (optional)
        The route after the port under which the app is reachable.
        e.g. if the app is reachable under "https://<runner-url>:8501/login" the route is "login"
    directory: pathlike (optional)
        In which directory to execute the command
    log_path: pathlike (optional)
        Where to store the log files of the app.
        The default is "/var/log/"
    startretries: int (optional)
        How often startup of the app should be retried if the startup fails.
        The default is 1.
    autorestart: bool (optional)
        Whether to restart the app if it stops for any reason (apart from a supervisor stop).
        The default is True.
    Returns
    -------

    """

    # check availability of supervisor
    if ((not os.path.exists("/etc/supervisor/conf.d/"))
            or (not shutil.which("supervisorctl"))):
        raise RuntimeError("Supervisor is not available. Ensure that supervisor"
                           " is installed and started.\n"
                           "> sudo apt-get install supervisor\n"
                           "> sudo service supervisor start")

    command = list(command)
    # resolve application path, e.g. "python" -> "/opt/conda/bin/python"
    resolved_command = shutil.which(command[0])
    if resolved_command is None:
        raise RuntimeError(f"Could not resolve command {command[0]}. Ensure the program is installed.")
    command[0] = resolved_command

    route = str(route) if route else "root"

    extended_name = str(name)
    allowed_name_pattern = r'^(?!.*__.*)[A-Za-z0-9_]+$'
    if not re.match(allowed_name_pattern, extended_name):
        raise ValueError("The name must consist only of letters, numbers and (non-double) '_'.")

    if port:
        extended_name += f"__{port}"
        if route:
            extended_name += f"__{route}"

    directory = directory if directory else "."
    directory = os.path.abspath(directory)

    log_path = log_path if log_path else "/var/log/"
    log_path = os.path.abspath(log_path)
    err_log_file = os.path.join(log_path, extended_name + ".err.log")
    out_log_file = os.path.join(log_path, extended_name + ".out.log")

    environment_vars = ",".join(
        [f"{key}={shlex.quote(str(value))}" for key, value in os.environ.items()]
    )

    app_configuration = (
        f"[program:{extended_name}]",
        f"directory={directory}",
        f"command={shlex.join(command)}",
        f"environment={environment_vars}",
        "autostart=false",
        f"startretries={int(startretries)}",
        f"autorestart={'true' if autorestart else 'false'}",
        f"stderr_logfile={err_log_file}",
        f"stdout_logfile={out_log_file}",
        "user=jovyan"
    )
    app_configuration = "\n".join(app_configuration)

    temp_file = "temp_" + str(uuid.uuid4())
    while os.path.exists(temp_file):
        temp_file = "temp_" + str(uuid.uuid4())

    with open(temp_file, "w") as f:
        f.write(app_configuration)

    target_file_path = f"/etc/supervisor/conf.d/{extended_name}.conf"
    if os.path.exists(target_file_path):
        logging.warning(f"Overwriting {target_file_path}")
    cp_command = ["sudo", "cp", temp_file, target_file_path]

    with subprocess.Popen(cp_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as cp_proc:
        cp_stdout, cp_stderr = cp_proc.communicate()
        exit_code = cp_proc.returncode

    # clean up temp file
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    if exit_code != 0:
        raise RuntimeError(f"Could not add supervisor conf file, {cp_stdout}, {cp_stderr}")

    command = ["sudo", "supervisorctl", "update", extended_name]
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        _stdout, _stderr = proc.communicate()
        exit_code = proc.returncode
        if exit_code != 0:
            raise RuntimeError(f"Could not update supervisor conf, {_stdout}, {_stderr}")

    return extended_name


def register_app():

    arg_parser = argparse.ArgumentParser(
        prog="register_app",
        description="Register an app so that it can be controlled from the runners menu.",
    )

    arg_parser.add_argument("command", type=str,
                            help=('The command that starts the app, '
                                  'for example "streamlit hello --server.port 8501"'))
    arg_parser.add_argument("-n", "--name", type=str,
                            help=('The name you want to give to the app, '
                                  'for example "streamlit_app"'))
    arg_parser.add_argument("-p", "--port", type=str,
                            help=('The port under which the app will be available, '
                                  'must be consistent with the command, '
                                  'for example 8501'))
    arg_parser.add_argument("-r", "--route", type=str,
                            help=('The route under which the app will be available, '
                                  'must be consistent with the command. '
                                  'For example if the app is reachable under <base_app_url>/<port>/api '
                                  'the route argument would be "api".'))
    arg_parser.add_argument("-d", "--workdir", type=str,
                            help=('The directory in which the app will run, '
                                  'will default to current directory if not set.'))
    arg_parser.add_argument("-l", "--logdir", type=str,
                            help=('Where to store the logs of the app, '
                                  'will default to "/var/log/" if not set.'))
    arg_parser.add_argument("-t", "--startretries", type=int, default=1,
                            help=('How often to retry starting the app, '
                                  'will default to 1 if not set.'))
    arg_parser.add_argument("-a", "--no-autorestart", action='store_true',
                            help='Do not restart the app if it stops.')

    args = arg_parser.parse_args()

    command_list = shlex.split(args.command)

    name = args.name
    if name is None:
        name = command_list[0].split("/")[-1]

    port = args.port
    route = args.route
    directory = args.workdir
    log_path = args.logdir
    startretries = args.startretries
    autorestart = not args.no_autorestart

    extended_name = add_app_to_supervisor(
        name=name, command=command_list,
        port=port, route=route,
        directory=directory, log_path=log_path,
        startretries=startretries, autorestart=autorestart
    )

    print(f"app registered as {name} ({extended_name}).")
