#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prune Docker Resources
This script provides commands to clean up unused Docker containers, images,
volumes, and networks. Each command includes filters to fine-tune the cleanup
process.
"""

import json
import sys
import re
import logging
from datetime import (
    datetime,
    timedelta,
    timezone
)
from functools import reduce
from typing import IO
import subprocess
import shlex

from dateutil.parser import parse
import click
import jsonschema
import yaml
import docker

from .version import __version__
from .click_types.bytes import (
    BytesTypeRange,
    bytes_to_human
)
from .click_types.timedelta import (
    TimeDeltaType,
    NullableTimeDeltaType
)
from .click_types.regex import (
    RegexType,
    NullableRegexType
)
from .click_types.intrange import (
    NullableIntRange
)
from .utils.list import (
    last
)


logging.basicConfig(format="%(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.INFO)
log = logging.getLogger(__name__)

##############################
###         CONST          ###
##############################

YAML_SCHEMA = yaml.load("""
type: array
items:
    type: string
""", Loader=yaml.FullLoader)

##############################
###      CLI Commands      ###
##############################


@click.group(
    context_settings={"auto_envvar_prefix": "DOCKER_PRUNE"},
    invoke_without_command=True,
    help="Manage and clean up unused Docker resources."
)
@click.option('--debug/--no-debug',
              is_flag=True,
              default=False,
              show_envvar=True,
              help='Enable debug logging')
@click.version_option(__version__)
@click.pass_context
def cli(ctx: click.Context = None, debug: bool = False):
    """Main entry point for the CLI."""
    if debug:
        log.setLevel(logging.DEBUG)
    client: docker.DockerClient = docker.from_env()
    ctx.obj = client


@cli.command('run', help='Load config and trigger')
@click.option('--validate/--no-validate',
              is_flag=True,
              default=False,
              show_envvar=True,
              help='Validate ')
@click.option('--exit/--no-exit', 'exit_now',
              is_flag=True,
              default=False,
              show_envvar=True,
              help='Exit immediately if a command exits with a non-zero status.'
              )
@click.argument('config', type=click.File('r'), required=True)
@click.pass_context
def cmd_run(
    ctx: click.Context = None,
    config: IO[str] = None,
    validate: bool | None = None,
    exit_now: bool = False
):  # pylint: disable=missing-function-docstring,unused-argument
    try:
        config_filename = config.name if hasattr(config, 'name') else '<stdin>'
        yml_config = yaml.load(config, Loader=yaml.FullLoader)
        jsonschema.validate(yml_config, YAML_SCHEMA)
        log.info('Loaded configuration file %s', config_filename)
        if validate:
            log.info('Configuration is valid')
            sys.exit(0)
        else:
            for cmd in yml_config:
                try:
                    args = shlex.split(cmd)
                    if len(args) == 0 or args[0] != 'docker-prune':
                        args = ['docker-prune'] + args
                        cmd = shlex.join(args)
                    log.debug('Executing command: %s', cmd)
                    subprocess.run(args=args, stdout=sys.stdout,
                                   stderr=sys.stderr, check=True)
                    log.info('Executed command: %s', cmd)
                except subprocess.CalledProcessError as e:
                    log.error(str(e))
                    if exit_now:
                        sys.exit(e.returncode)
    except jsonschema.ValidationError as e:
        log.error(str(e))
        sys.exit(1)
    except yaml.YAMLError as e:
        log.error('Error loading configuration file %s', e)
        sys.exit(1)
    return 0


@cli.result_callback()
def cmd_system(results, **kwargs):  # pylint: disable=unused-argument
    """Calculate and log the total reclaimed space after running commands."""
    if isinstance(results, int):
        log.info('Total reclaimed space: %s', bytes_to_human(results))
    return 0


@cli.command('info', help='Display storage usage information for Docker images and volumes.')
@click.pass_context
def cmd_info(ctx: click.Context = None):
    """Show detailed size information about Docker images and volumes."""
    client: docker.DockerClient = ctx.obj
    if docker.utils.version_gte(client.api.api_version, '1.25'):
        try:
            df = ctx.obj.df()
            image_usage = df['LayersSize']
            volume_usage = sum(
                volume['UsageData']['Size']
                for volume in df['Volumes']
                if volume['Scope'] == 'local'
            )
            log.info('Overall usage Images: %s Volumes: %s', bytes_to_human(
                image_usage), bytes_to_human(volume_usage))
        except docker.errors.APIError as e:
            log.error(e)
            sys.exit(1)
    return 0


@cli.group('containers',
           help='Manage and filter Docker containers. Filters are applied as an AND condition.'
           )
def cmd_containers():
    """Group for container-related commands."""
    return 0


@cmd_containers.command('stop',
                        help='Stop containers based on filters such as age' +
                        ', restart count, name, or labels.')
@click.option('--age', '--remove-age', '-ra', '-a',
              default=None,
              type=TimeDeltaType(),
              show_envvar=True,
              help='Stop containers older than the specified age (e.g., "2d 3h").'
              )
@click.option('--restart', '-r',
              default=100,
              type=NullableIntRange(min=0),
              show_envvar=True,
              help='Stop containers restarted more than the specified number of times.')
@click.option('--name', '-n',
              multiple=True,
              default=None,
              type=RegexType(),
              show_envvar=True,
              help='Stop containers with names matching the provided regex pattern.')
@click.option('--not-name', '-nn',
              multiple=True,
              default=None,
              type=RegexType(),
              show_envvar=True,
              help='Exclude containers with names matching the provided regex pattern.')
@click.option('--label', '-l',
              multiple=True,
              default=None,
              type=RegexType(),
              show_envvar=True,
              help='Stop containers with labels matching the provided regex pattern.')
@click.option('--not-label', '-nl',
              show_default=True,
              multiple=True,
              type=NullableRegexType(),
              default=[
                  '^(com.docker|io.podman).keep=(1|true|yes)?$'
              ],
              show_envvar=True,
              help='Exclude containers with labels matching the provided regex pattern.')
@click.option('--timeout', '-t',
              default=60,
              show_default=True,
              type=click.IntRange(min=0),
              show_envvar=True,
              help='Timeout in seconds before forcing a container to stop.')
@click.pass_context
def cmd_containers_stop(
    ctx: click.Context = None,
    age: timedelta | None = None,
    restart: int | None = None,
    name: list[re.Pattern] = None,
    not_name: list[re.Pattern] = None,
    label: list[re.Pattern] = None,
    not_label: list[re.Pattern] = None,
    timeout: int | None = None
):  # pylint: disable=R0913,R0914,R0917
    """Stop containers based on the provided filters."""
    client: docker.DockerClient = ctx.obj

    containers = client.containers.list(ignore_removed=True)

    if age is not None:
        now = datetime.now(tz=timezone.utc)
        target = now - age
        containers = filter(
            lambda container: parse(
                container.attrs['State']['StartedAt']) <= target,
            containers
        )

    if restart is not None:
        containers = filter(
            lambda container: container.attrs['RestartCount'] >= restart,
            containers
        )

    if len(name) > 0:
        def filter_name(regex):
            return lambda container: bool(regex.search(container.name))
        for regex in name:
            containers = filter(filter_name(regex), containers)

    if len(not_name) > 0:
        def filter_not_name(regex):
            return lambda container: not bool(regex.search(container.name))
        for regex in not_name:
            containers = filter(filter_not_name(regex), containers)

    if len(label) > 0:
        def filter_label(regex):
            return lambda container: container.attrs['Config']['Labels'] and any(
                bool(regex.search(label))
                for label in [
                    f'{k}={v}'
                    for k, v in container.attrs['Config']['Labels'].items()
                ]
            )
        for regex in label:
            containers = filter(filter_label(regex), containers)

    if len(not_label) > 0:
        def filter_not_label(regex):
            return lambda container: not container.attrs['Config']['Labels'] or all(
                (not bool(regex.search(label)))
                for label in [
                    f'{k}={v}'
                    for k, v in container.attrs['Config']['Labels'].items()
                ]
            )
        for regex in filter(lambda l: not l is None, not_label):
            containers = filter(filter_not_label(regex), containers)

    for container in containers:
        try:
            container.stop(timeout=timeout)
            log.info('Stopped container %s.', container.name)
        except docker.errors.APIError as e:
            log.error(
                'Error stopping container %s message %s', container.name, e)

    return 0


@cmd_containers.command('rm',
                        help='Remove stopped containers based on ' +
                        'filters such as age, name, or labels.'
                        )
@click.option('--age', '--remove-age', '-ra', '-a',
              default='1w',
              show_default=True,
              type=NullableTimeDeltaType(),
              show_envvar=True,
              help='Remove stopped containers older than the specified age.'
              )
@click.option('--name', '-n',
              multiple=True,
              default=None,
              type=RegexType(),
              show_envvar=True,
              help='Remove containers with names matching the provided regex pattern.'
              )
@click.option('--not-name', '-nn',
              multiple=True,
              default=None,
              type=RegexType(),
              show_envvar=True,
              help='Exclude containers with names matching the provided regex pattern.'
              )
@click.option('--label', '-l',
              multiple=True,
              default=None,
              type=RegexType(),
              show_envvar=True,
              help='Remove containers with labels matching the provided regex pattern.'
              )
@click.option('--not-label', '-nl',
              show_default=True,
              multiple=True,
              type=RegexType(),
              default=[
                  '^(com.docker|io.podman).keep=(1|true|yes)?$'
              ],
              show_envvar=True,
              help='Exclude containers with labels matching the provided regex pattern.')
@click.pass_context
def cmd_containers_rm(
    ctx: click.Context = None,
    age: timedelta | None = None,
    name: list[re.Pattern] | None = None,
    not_name: list[re.Pattern] | None = None,
    label: list[re.Pattern] | None = None,
    not_label: list[re.Pattern] | None = None
):  # pylint: disable=R0913,R0914,R0917
    """Remove containers based on the provided filters."""
    client: docker.DockerClient = ctx.obj

    containers = filter(
        lambda container: container.attrs['State']['Running'] is False,
        client.containers.list(
            all=True,
            ignore_removed=True
        ))

    if age is not None:
        now = datetime.now(tz=timezone.utc)
        target = now - age
        containers = filter(
            lambda container: parse(
                container.attrs['State']['StartedAt']) <= target,
            containers
        )

    if not name is None:
        def filter_name(regex):
            return lambda container: bool(regex.search(container.name))
        for regex in name:
            containers = filter(filter_name(regex), containers)

    if not not_name is None:
        def filter_not_name(regex):
            return lambda container: not bool(regex.search(container.name))
        for regex in not_name:
            containers = filter(filter_not_name(regex), containers)

    if not label is None:
        def filter_label(regex):
            return lambda container: container.attrs['Config']['Labels'] and any(
                bool(regex.search(label))
                for label in [
                    f'{k}={v}'
                    for k, v in container.attrs['Config']['Labels'].items()
                ]
            )
        for regex in label:
            containers = filter(filter_label(regex), containers)

    if not not_label is None:
        def filter_not_label(regex):
            return lambda container: not container.attrs['Config']['Labels'] or all(
                (not bool(regex.search(label)))
                for label in [
                    f'{k}={v}'
                    for k, v in container.attrs['Config']['Labels'].items()
                ]
            )
        for regex in not_label:
            containers = filter(filter_not_label(regex), containers)

    for container in containers:
        try:
            container.remove()
            log.info('Removed container %s.', container.name)
        except docker.errors.APIError as e:
            log.error(
                'Error removing container %s message %s', container.name, e)


@cli.command('images',
             help='Remove unused Docker images based on filters such as age, tags, or labels.'
             )
@click.option('--age', '-a',
              show_default=True,
              default='90d',
              type=TimeDeltaType(),
              show_envvar=True,
              help='Remove images older than the specified age.'
              )
@click.option('--tag', '-t',
              type=RegexType(),
              multiple=True,
              default=None,
              show_envvar=True,
              help='Remove images with tags matching the provided regex pattern.'
              )
@click.option('--not-tag', '-nt',
              type=RegexType(),
              multiple=True,
              default=None,
              show_envvar=True,
              help='Exclude images with tags matching the provided regex pattern.'
              )
@click.option('--label', '-l',
              type=RegexType(),
              multiple=True,
              default=None,
              show_envvar=True,
              help='Remove images with labels matching the provided regex pattern.'
              )
@click.option('--not-label', '-nl',
              type=RegexType(),
              multiple=True,
              default=None,
              show_envvar=True,
              help='Exclude images with labels matching the provided regex pattern.'
              )
@click.option('--keep-builds', '-k',
              type=BytesTypeRange(min=0),
              default=None,
              show_envvar=True,
              help='Keep build cache up to the specified size.'
              )
@click.pass_context
def cmd_images(
    ctx: click.Context = None,
    age: timedelta | None = None,
    tag: list[re.Pattern] | None = None,
    not_tag: list[re.Pattern] | None = None,
    label: list[re.Pattern] | None = None,
    not_label: list[re.Pattern] | None = None,
    keep_builds: int | None = None,
):  # pylint: disable=R0913,R0914,R0917,R0912
    """Remove unused images based on filters."""
    client: docker.DockerClient = ctx.obj

    _used_ids = set(map(
        lambda container: container.attrs['Image'],
        client.containers.list(all=True)
    ))

    images = filter(lambda image: not image.id in _used_ids,
                    client.images.list())

    if not age is None:
        target = datetime.now(tz=timezone.utc) - age
        images = filter(lambda image: parse(
            image.attrs['Created']) <= target, images)

    if not tag is None:
        def filter_tag(regex):
            return lambda image: image.attrs['RepoTags'] and any(
                bool(regex.search(t))
                for t in image.attrs['RepoTags']
            )
        for regex in tag:
            images = filter(filter_tag(regex), images)

    if not not_tag is None:
        def filter_not_tag(regex):
            return lambda image: not image.attrs['RepoTags'] or all(
                (not bool(regex.search(t)))
                for t in image.attrs['RepoTags']
            )
        for regex in not_tag:
            images = filter(filter_not_tag(regex), images)

    if not label is None:
        def filter_label(regex):
            return lambda image: image.attrs['Config']['Labels'] and any(
                bool(regex.search(label))
                for label in [
                    f'{k}={v}'
                    for k, v in image.attrs['Config']['Labels'].items()
                ]
            )
        for regex in label:
            images = filter(filter_label(regex), images)

    if not not_label is None:
        def filter_not_label(regex):
            return lambda image: not image.attrs['Config']['Labels'] or all(
                (not bool(regex.search(label)))
                for label in [
                    f'{k}={v}'
                    for k, v in image.attrs['Config']['Labels'].items()
                ]
            )
        for regex in not_label:
            images = filter(filter_not_label(regex), images)

    sum_space = 0
    for image in images:
        tag = last(image.attrs['RepoTags'], default='<none>')
        try:
            client.images.remove(image.id, force=True)
            saved_space = image.attrs['Size']
            sum_space += saved_space
            log.info('Removed image %s, saved %s.',
                     tag, bytes_to_human(saved_space))
        except docker.errors.APIError as e:
            log.error('Could not remove %s, %s', tag, e)

    try:
        # prune only unused and untagged images.
        result = client.images.prune(filters={
            'dangling': True
        })
        saved_space = result['SpaceReclaimed']
        if log.isEnabledFor(logging.DEBUG):
            for volume in result['ImagesDeleted'] or []:
                log.debug('Deleted: %s', volume)
        if saved_space > 0:
            sum_space += saved_space
            log.info('Removed unused and untagged images and saved %s.',
                     bytes_to_human(saved_space))
    except docker.errors.APIError as e:
        log.error('Could not prune images %s', e)

    try:
        # Delete the builder cache
        result = client.images.prune_builds(
            keep_storage=keep_builds,
            all=True
        )
        saved_space = result['SpaceReclaimed']
        if log.isEnabledFor(logging.DEBUG):
            for volume in result['CachesDeleted'] or []:
                log.debug('Deleted: %s', volume)
        if saved_space > 0:
            sum_space += saved_space
            log.info('Removed build cache and saved %s.',
                     bytes_to_human(saved_space))
    except docker.errors.APIError as e:
        log.error('Could not prune build cache %s', e)
    return sum_space


@cli.command('volumes',
             help='Remove unused Docker volumes based on filters such as age, name, or labels.')
@click.option('--age', '-a',
              show_default=True,
              default='30d',
              type=TimeDeltaType(),
              show_envvar=True,
              help='Remove volumes older than the specified age.')
@click.option('--name', '-n',
              type=RegexType(),
              multiple=True,
              default=None,
              show_envvar=True,
              help='Remove volumes with names matching the provided regex pattern.')
@click.option('--not-name', '-nn',
              type=RegexType(),
              multiple=True,
              default=None,
              show_envvar=True,
              help='Exclude volumes with names matching the provided regex pattern.')
@click.option('--label', '-l',
              type=RegexType(),
              multiple=True,
              default=None,
              show_envvar=True,
              help='Remove volumes with labels matching the provided regex pattern.')
@click.option('--not-label', '-nl',
              type=RegexType(),
              multiple=True,
              show_default=True,
              default=[
                  '^(com.docker|io.podman).compose.(project|volume)',
                  '^(com.docker|io.podman).keep=(1|true|yes)?$',
              ],
              show_envvar=True,
              help='Exclude volumes with labels matching the provided regex patterns.')
@click.pass_context
def cmd_volumes(
    ctx: click.Context = None,
    age: timedelta | None = None,
    name: list[re.Pattern] = None,
    not_name: list[re.Pattern] = None,
    label: list[re.Pattern] = None,
    not_label: list[re.Pattern] = None
):  # pylint: disable=R0913,R0914,R0917,R0912
    """Remove unused volumes based on the provided filters."""
    client: docker.DockerClient = ctx.obj
    volumes = client.volumes.list(filters={'dangling': True}) or []

    if not age is None:
        target = datetime.now(tz=timezone.utc) - age
        volumes = filter(lambda volume: parse(
            volume.attrs['CreatedAt']) <= target, volumes)

    if len(name) > 0:
        def filter_name(regex):
            return lambda volume: bool(regex.search(volume.name))
        for regex in name:
            volumes = filter(filter_name(regex), volumes)

    if len(not_name) > 0:
        def filter_not_name(regex):
            return lambda volume: not bool(regex.search(volume.name))
        for regex in not_name:
            volumes = filter(filter_not_name(regex), volumes)

    if len(label) > 0:
        def filter_label(regex):
            return lambda volume: volume.attrs['Labels'] and any(
                bool(regex.search(label))
                for label in [
                    f'{k}={v}'
                    for k, v in volume.attrs['Labels'].items()
                ]
            )
        for regex in label:
            volumes = filter(filter_label(regex), volumes)

    if len(not_label) > 0:
        def filter_not_label(regex):
            return lambda volume: not volume.attrs['Labels'] or all(
                (not bool(regex.search(label)))
                for label in [
                    f'{k}={v}'
                    for k, v in volume.attrs['Labels'].items()
                ]
            )
        for regex in not_label:
            volumes = filter(filter_not_label(regex), volumes)

    volume_sizes = {}
    if docker.utils.version_gte(client.api.api_version, '1.25'):
        _df = client.df()
        volume_sizes = {
            volume['Name']: volume['UsageData']['Size']
            for volume in _df['Volumes'] or []
            if volume['Scope'] == 'local'
        }

    if log.isEnabledFor(logging.DEBUG):
        log.debug('volume_sizes=%s', json.dumps(volume_sizes, indent=4))

    sum_space = 0
    for volume in volumes:
        try:
            client.api.remove_volume(
                volume.id,
                force=docker.utils.version_gte(
                    client.api.api_version, '1.25')
            )
            saved_space = volume_sizes.get(volume.name, 0)
            sum_space += saved_space
            log.info('Removed volume %s, saved %s.',
                     volume.name, bytes_to_human(saved_space))
        except docker.errors.APIError as e:
            log.error('Could not remove %s, %s', volume.name, e)
    try:
        if docker.utils.version_gte(client.api.api_version, '1.25'):
            result = client.volumes.prune()
            saved_space = result.get('SpaceReclaimed', 0)
            if log.isEnabledFor(logging.DEBUG):
                for volume in result.get('VolumesDeleted', []) or []:
                    log.debug('Deleted: %s', volume)
            sum_space += saved_space
            log.info('Removed anonymous volumes and saved %s.',
                     bytes_to_human(saved_space))
    except docker.errors.APIError as e:
        log.error('Could not prune volumes %s', e)

    return sum_space


@cli.command('networks',
             help='Remove unused Docker networks based on filters such as age, name, or labels.'
             )
@click.option('--age', '-a',
              show_default=True,
              default=None,
              type=TimeDeltaType(),
              show_envvar=True,
              help='Remove networks older than the specified age.'
              )
@click.option('--name', '-n',
              type=RegexType(),
              multiple=True,
              default=None,
              show_envvar=True,
              help='Remove networks with names matching the provided regex pattern.'
              )
@click.option('--not-name', '-nn',
              type=RegexType(),
              multiple=True,
              default=None,
              show_envvar=True,
              help='Exclude networks with names matching the provided regex pattern.'
              )
@click.option('--label', '-l',
              type=RegexType(),
              multiple=True,
              default=None,
              show_envvar=True,
              help='Remove networks with labels matching the provided regex pattern.'
              )
@click.option('--not-label', '-nl',
              type=RegexType(),
              multiple=True,
              show_default=True,
              default=[
                  '^(com.docker|io.podman).compose.(project|network)',
                  '^(com.docker|io.podman).keep=(1|true|yes)?$',
              ],
              show_envvar=True,
              help='Exclude networks with labels matching the provided regex patterns.'
              )
@click.pass_context
def cmd_networks(
    ctx: click.Context = None,
    age: timedelta | None = None,
    name: list[re.Pattern] | None = None,
    not_name: list[re.Pattern] | None = None,
    label: list[re.Pattern] | None = None,
    not_label: list[re.Pattern] | None = None
):  # pylint: disable=R0913,R0914,R0917
    """Remove unused networks based on the provided filters."""
    client: docker.DockerClient = ctx.obj

    networks = client.networks.list(filters={
        'type': 'custom',
        'dangling': True
    })

    # Filter networks attached to containers
    _network_ids = set(reduce(lambda x, y: x + y, map(
        lambda container: [network['NetworkID']
                           for network in container.attrs['NetworkSettings']['Networks'].values()],
        client.containers.list(all=True)
    ), []))
    networks = filter(lambda network: not network.id in _network_ids, networks)

    if not age is None:
        target = datetime.now(tz=timezone.utc) - age
        networks = filter(lambda network: parse(
            network.attrs['Created']) <= target, networks)

    if not name is None:
        def filter_name(regex):
            return lambda network: bool(regex.search(network.name))
        for regex in name:
            networks = filter(filter_name(regex), networks)

    if not not_name is None:
        def filter_not_name(regex):
            return lambda network: not bool(regex.search(network.name))
        for regex in not_name:
            networks = filter(filter_not_name(regex), networks)

    if not label is None:
        def filter_label(regex):
            return lambda network: network.attrs['Labels'] and any(
                bool(regex.search(label))
                for label in [
                    f'{k}={v}'
                    for k, v in network.attrs['Labels'].items()
                ]
            )
        for regex in label:
            networks = filter(filter_label(regex), networks)

    if not not_label is None:
        def filter_not_label(regex):
            return lambda network: not network.attrs['Labels'] or all(
                (not bool(regex.search(label)))
                for label in [
                    f'{k}={v}'
                    for k, v in network.attrs['Labels'].items()
                ]
            )
        for regex in not_label:
            networks = filter(filter_not_label(regex), networks)

    network: docker.models.networks.Network = None
    for network in networks:
        try:
            network.remove()
            log.info('Removed network %s', network.name)
        except docker.errors.APIError as e:
            log.error('Could not remove %s error %s', network.name, e)
    return 0
