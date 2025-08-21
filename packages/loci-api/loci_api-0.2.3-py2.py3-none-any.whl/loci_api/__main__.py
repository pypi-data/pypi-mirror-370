# pylint:disable=line-too-long,too-many-arguments,too-many-positional-arguments
"""
LOCI CLI
"""

import argparse
import json
import sys
import os

from loci_api import api_helper

def parse_args():
    program_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    parser = argparse.ArgumentParser(prog=program_name, description="LOCI CLI")
    subparsers = parser.add_subparsers(dest="command", required=False)

    subparsers.add_parser("list-projects", help="List all projects")

    list_versions_parser = subparsers.add_parser("list-versions", help="List all versions of a project")
    list_versions_parser.add_argument("project-name", help="Project name", type=str)

    last_version_parser = subparsers.add_parser("last-version", help="Get last version of a project")
    last_version_parser.add_argument("project-name", help="Project name", type=str)

    upload_parser = subparsers.add_parser("upload", help="Upload a new version")
    upload_parser.add_argument("path-to-binary", help="Binary file", type=str)
    upload_parser.add_argument("project-name", help="Project name", type=str)
    upload_parser.add_argument("new-version-name", help="Version name", type=str)
    upload_parser.add_argument("--compare-version-name", help="Version to compare", type=str)
    upload_parser.add_argument("--wait", help="wait for processing to finish", type=str, default='True')
    upload_parser.add_argument("--event-id", help="id of object event initiating the action", type=str, default='')

    upload_last_parser = subparsers.add_parser("upload-last", help="Upload a new version using latest")
    upload_last_parser.add_argument("path-to-binary", help="Binary file", type=str)
    upload_last_parser.add_argument("project-name", help="Project name", type=str)
    upload_last_parser.add_argument("new-version-name", help="Version name", type=str)
    upload_last_parser.add_argument("--wait", help="wait for processing to finish", type=str, default='True')
    upload_last_parser.add_argument("--event-id", help="id of object event initiating the action", type=str, default='')

    func_insights_parser = subparsers.add_parser("func-insights", help="Get function insights")
    func_insights_parser.add_argument("project-name", help="Project name", type=str)
    func_insights_parser.add_argument("version-name", help="Version name", type=str)
    func_insights_parser.add_argument("--version-name-base", help="Base version name", type=str, default=None)
    func_insights_parser.add_argument("--perc-resp-limit", help="Response time limit (percentage)", type=float, default=None)
    func_insights_parser.add_argument("--perc-thro-limit", help="Throughput limit (percentage)", type=float, default=None)
    func_insights_parser.add_argument("--perc-bott-limit", help="Bottleneck limit (percentage)", type=float, default=None)
    func_insights_parser.add_argument("--pairs", nargs='*', default=[],
                                      help="Pairs of function_name and binary_name, e.g. --pairs func1 bin1 func2 bin2")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    return args

def output_success_result(res) -> int:
    print(json.dumps(res, indent=2))
    return 0

def cmd_list_projects() -> int:
    projects = api_helper.get_projects()
    if projects is None:
        return 1
    res = [project['name'] for project in projects]
    return output_success_result(res)

def cmd_list_versions(project_name) -> int:
    project_id, _ = api_helper.get_project_id(project_name)
    if project_id is None:
        return 1
    versions = api_helper.get_versions(project_id)
    if versions is None:
        return 1
    res = [version['properties']['version_name'] for version in versions]
    return output_success_result(res)

def cmd_last_version(project_name) -> int:
    project_id, _ = api_helper.get_project_id(project_name)
    if project_id is None:
        return 1
    _, version_name = api_helper.get_last_version_id(project_id)
    if version_name is None:
        return 1
    return output_success_result([version_name])

def cmd_upload(file_path, project_name, version_name, cmp_ver_name, wait, event_id) -> int:
    compare_version_id = ''
    if cmp_ver_name:
        project_id, _ = api_helper.get_project_id(project_name)
        versions = api_helper.get_versions(project_id)
        for version in versions:
            if cmp_ver_name == version['properties']['version_name']:
                compare_version_id = version['properties']['version_id']
    return api_helper.full_upload(file_path, version_name, project_name, use_latest=False, compare_version_id=compare_version_id, wait=wait, event_id=event_id)

def cmd_upload_last(file_path, project_name, version_name, wait, event_id) -> int:
    return api_helper.full_upload(file_path, version_name, project_name, use_latest=True, compare_version_id='', wait=wait, event_id=event_id)

def cmd_function_insights(project_name, version_name, version_name_base, perc_resp_limit, perc_thro_limit, perc_bott_limit, pairs) -> int:
    if pairs:
        if len(pairs) % 2 != 0:
            print(f'uneven number of pairs: {len(pairs)}')
            return 1
        pairs = [{"function_name": pairs[i], "binary_name": pairs[i + 1]} for i in range(0, len(pairs), 2)]

    project_id, _ = api_helper.get_project_id(project_name)
    if not project_id:
        return 1

    versions = api_helper.get_versions(project_id)
    if not versions:
        return 1

    version_id = None
    version_id_base = None

    for version in versions:
        if version_name == version['properties']['version_name']:
            version_id = version['properties']['version_id']
        if version_name_base == version['properties']['version_name']:
            version_id_base = version['properties']['version_id']

    if not version_id:
        print('Version not found')
        return 1

    insights = api_helper.get_function_insights(version_id, version_id_base, perc_resp_limit, perc_thro_limit, perc_bott_limit, pairs)
    if insights is None:
        return 1

    res = [{'total_count': x['total_count'],
            'binary_name': x['binary_name'],
            'function_long_name': x['function_long_name'],
            'function_name': x['function_name'],
            'source_location': x['src_location'],
            'mean_bottleneck': x['mean_bottleneck'],
            'std_bottleneck': x['std_bottleneck'],
            'mean_throughput': x['mean_throughput'],
            'std_throughput': x['std_throughput'],
            'mean_response': x['mean_resp'],
            'std_response': x['std_resp'],
            'mean_bottleneck_base': x['mean_bottleneck_base'],
            'std_bottleneck_base': x['std_bottleneck_base'],
            'mean_throughput_base': x['mean_throughput_base'],
            'std_throughput_base': x['std_throughput_base'],
            'mean_response_base': x['mean_resp_base'],
            'std_response_base': x['std_resp_base'],
            'perc_throughput': x['perc_thro'],
            'perc_response': x['perc_resp'],
            'perc_bottleneck': x['perc_bott']
            } for x in insights['message']]

    return output_success_result(res)

def main():
    args = parse_args()

    if args.command == "list-projects":
        sys.exit(cmd_list_projects())

    if args.command == "list-versions":
        sys.exit(cmd_list_versions(project_name=getattr(args, 'project-name')))

    if args.command == "last-version":
        sys.exit(cmd_last_version(project_name=getattr(args, 'project-name')))

    if args.command == "upload":
        sys.exit(cmd_upload(file_path=getattr(args, 'path-to-binary'),
                            project_name=getattr(args, 'project-name'),
                            version_name=getattr(args, 'new-version-name'),
                            cmp_ver_name=getattr(args, 'compare_version_name', None),
                            wait=getattr(args, 'wait', None),
                            event_id=getattr(args, 'event_id', None)))

    if args.command == "upload-last":
        sys.exit(cmd_upload_last(file_path=getattr(args, 'path-to-binary'),
                                 project_name=getattr(args, 'project-name'),
                                 version_name=getattr(args, 'new-version-name'),
                                 wait=getattr(args, 'wait', None),
                                 event_id=getattr(args, 'event_id', None)))

    if args.command == "func-insights":
        sys.exit(cmd_function_insights(project_name=getattr(args, 'project-name'),
                                       version_name=getattr(args, 'version-name'),
                                       version_name_base=getattr(args, 'version_name_base', None),
                                       perc_resp_limit=getattr(args, 'perc_resp_limit', None),
                                       perc_thro_limit=getattr(args, 'perc_thro_limit', None),
                                       perc_bott_limit=getattr(args, 'perc_bott_limit', None),
                                       pairs=getattr(args, 'pairs', None)))

if __name__ == "__main__":
    main()
