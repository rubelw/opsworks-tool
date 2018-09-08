"""
The command line interface to stackility.

Major help from: https://www.youtube.com/watch?v=kNke39OZ2k0
"""
import opsworkstool
from opsworkstool.opsworks_creator import OpsworksCreator
from opsworkstool.opsworks_deployer import OpsworksDeployer
import click
import boto3
import logging
import sys
import json
import os

default_stage = 'dev'
fresh_notes = '''A skeleton of the new opsworks stack, {}, has been created.

In {}/{}/config you will find a config.ini file that you should
fill in with parameters for your own account.

Develop the opsworks function as needed then you can deploy it with:
opsworkstool deploy. The opsworks has been started in template.json.
'''


@click.group()
@click.version_option(version='0.0.2')
def cli():
    pass


@cli.command()
@click.option('-d', '--directory', help='target directory for new Opsworks recipe, defaults to current directory')
@click.option('-n', '--name', help='name of the new opsworks skeleton', required=True)
@click.option('-p', '--profile', help='AWS CLI profile to use in the deployment, more details at http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html')
@click.option('-r', '--region', help='target region, defaults to your credentials default region')
@click.option('--debug', help='Turn on debugging', required=False, is_flag=True)
def new(directory, name, profile, region, debug):
    command_line = {}
    command_line['name'] = name


    command_line['template_directory'] = '{}/template/simple'.format(opsworkstool.__path__[0])

    command_line['cwd'] =  str(os.getcwd())
    if directory:
        command_line['directory'] = directory
    else:
        command_line['directory'] = '.'

    if profile:
        command_line['profile'] = profile
    else:
        command_line['profile'] = None

    if region:
        command_line['region'] = region
    else:
        command_line['region'] = None

    if debug:
        command_line['debug'] = True
    else:
        command_line['debug'] = False

    if start_new_opsworks(command_line):
        sys.exit(0)
    else:
        sys.exit(1)


@cli.command()
@click.option('-d', '--directory', help='scratch directory for deploy, defaults to /tmp')
@click.option('-p', '--profile', help='AWS CLI profile to use in the deployment, more details at http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html')
@click.option('-r', '--region', help='target region, defaults to your credentials default region')
@click.option('-s', '--stage', help='The /config/<stage>  with parameters for cloudformation. Default: config.ini')
@click.option('--debug', help='Turn on debugging', required=False, is_flag=True)
def deploy(directory, profile, region, stage, debug):
    command_line = {}

    command_line['cwd'] =  str(os.getcwd())

    if directory:
        command_line['work_directory'] = directory
    else:
        command_line['work_directory'] = '/tmp'

    if profile:
        command_line['profile'] = profile
    else:
        command_line['profile'] = None

    if region:
        command_line['region'] = region
    else:
        command_line['region'] = None

    if debug:
        command_line['debug'] = True
    else:
        command_line['debug'] = False

    if stage:
        command_line['stage'] = stage
    else:
        command_line['stage'] = default_stage


    command_line['template_directory'] = '{}/template'.format(opsworkstool.__path__[0])
    logging.info('command_line: {}'.format(json.dumps(command_line, indent=2)))

    if deploy_opsworks(command_line):
        sys.exit(0)
    else:
        sys.exit(1)


def start_new_opsworks(command_line):
    try:
        tool = OpsworksCreator(command_line)
    except Exception:
        sys.exit(1)

    if tool.create_opsworks():
        logging.info('create_new_opsworks() went well')
        print('\n\n\n\n')
        print('********************************************************************************')
        print(fresh_notes.format(
            command_line['name'],
            command_line['directory'],
            command_line['name'])
        )
    else:
        logging.error('create_new_opsworks() did not go well')
        sys.exit(1)


def deploy_opsworks(command_line):

    try:
        print('command_line: '+str(command_line))
        tool = OpsworksDeployer(command_line)
    except Exception as err:
        print('Error: '+str(err))
        sys.exit(1)

    if tool.deploy_opsworks():
        logging.info('deploy_opsworks() went well')
        return True
    else:
        logging.error('deploy_opsworks() did not go well')
        sys.exit(1)


def find_myself():
    s = boto3.session.Session()
    return s.region_name
