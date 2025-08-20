import argparse
import psutil


def check_ports_available(ports):
    """Check whether the ports are available"""
    result = {int(p): True for p in ports}
    for conn in psutil.net_connections():
        port = conn.laddr.port
        if port in result:
            result[port] = False
    return result


def get_app_ports():

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

    args = arg_parser.parse_args()

    command_list = shlex.split(args.command)

    name = args.name
    if name is None:
        name = command_list[0].split("/")[-1]

    port = args.port
    route = args.route
    directory = args.workdir
    log_path = args.logdir

    extended_name = add_app_to_supervisor(
        name=name, command=command_list,
        port=port, route=route,
        directory=directory, log_path=log_path)

    print(f"app registered as {name} ({extended_name}).")
