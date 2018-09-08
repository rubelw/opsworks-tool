import logging
import traceback
import subprocess
import os
import sys
import shutil
from opsworkstool import utility
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(asctime)s (%(module)s) %(message)s',
                    datefmt='%Y/%m/%d-%H:%M:%S')

IGNORED_STUFF = ('template_template', '*.pyc')


class OpsworksCreator:
    """
    Opsworks utility is yet another tool create and deploy AWS opsworks stacks
    """
    _config = None
    _region = None
    _profile = None

    def __init__(self, config_block):
        """
        Lambda utility init method.

        Args:
            config_block - a dictionary created in the CLI driver. See that
                           script for the things that are required and
                           optional.

        Returns:
           not a damn thing

        Raises:
            SystemError - if everything isn't just right
        """
        if config_block:
            self._config = config_block
            self._profile = config_block['profile']
            self._region = config_block['region']
            self.debug = config_block['debug']
        else:
            logger.error('config block was garbage')
            raise SystemError

    def create_opsworks(self):
        """
        Write the template for a new opsworks to the indicated target directory.

        Args:
            None

        Returns:
            True if the opsworks is created
            False if the opsworks is not created for some odd reason
        """
        try:
            destination_directory = '{}/{}'.format(
                self._config['directory'],
                self._config['name']
            )

            if os.path.exists(destination_directory):
                print('{} already exists, exiting'.format(destination_directory))
                sys.exit(1)
            else:
                logger.info('     source_directory: {}'.format(self._config['template_directory']))
                logger.info('destination_directory: {}'.format(destination_directory))

            default_vpc_info = self._describe_opsworks_environment()

            logger.debug('default vpc info: '+str(default_vpc_info))
            logger.debug(json.dumps(self._config, indent=2))
            logger.debug(json.dumps(default_vpc_info, indent=2))
            logger.info('Copying template_directory: '+str(self._config['template_directory']))

            # Create Berksfile and recipe files before copying to directory
            self.create_recipe_files()



            shutil.copy2(
                str(self._config['template_directory'])+'/config/config.ini',
                str(self._config['cwd']) + '/' + str(self._config['name'])+'/config/',
            )

            shutil.copy2(
                str(self._config['template_directory'])+'/utility/__init__.py',
                str(self._config['cwd']) + '/' + str(self._config['name'])+'/utility/',
            )
            shutil.copy2(
                str(self._config['template_directory'])+'/utility/tools.py',
                str(self._config['cwd']) + '/' + str(self._config['name'])+'/utility/',
            )

            shutil.copy2(
                str(self._config['template_directory'])+'/requirements.txt',
                str(self._config['cwd']) + '/' + str(self._config['name'])+'/',
            )

            shutil.copy2(
                str(self._config['template_directory'])+'/.opsworkstool',
                str(self._config['cwd']) + '/' + str(self._config['name'])+'/',
            )

            shutil.copy2(
                str(self._config['template_directory'])+'/template.json',
                str(self._config['cwd']) + '/' + str(self._config['name'])+'/',
            )


            logger.info('Writing config ini file to '+str(destination_directory))
            self.write_config_ini(destination_directory, default_vpc_info)
            logger.info('Done writing config ini')

            dot_opsworkstool = '{}/.opsworkstool'.format(destination_directory)

            logger.info('dot_opsworkstool: '+str(dot_opsworkstool))
            meta_data = None

            with open(dot_opsworkstool, 'r') as f:
                meta_data = json.load(f)
                meta_data['name'] = self._config['name']

            logger.info('done writing '+str(dot_opsworkstool))

            with open(dot_opsworkstool, 'w') as f:
                json.dump(meta_data, f, indent=4)

            return True
        except Exception as x:
            logger.error('Exception caught in create_opsworks(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return False


    def create_recipe_files(self):

        print('creating recipe files')
        # Create recipe directory if it does not exist


        # Create base directory
        if not os.path.exists(self._config['cwd']+'/'+str(self._config['name'])):
            os.makedirs(self._config['cwd']+'/'+str(self._config['name']))
        # Create recipe directory
        if not os.path.exists(str(self._config['cwd'])+'/'+str(self._config['name'])+'/recipe'):
            os.makedirs(str(self._config['cwd'])+'/'+str(self._config['name'])+'/recipe')

        if not os.path.exists(str(self._config['cwd'])+'/'+str(self._config['name'])+'/config'):
            os.makedirs(str(self._config['cwd'])+'/'+str(self._config['name'])+'/config')

        if not os.path.exists(str(self._config['cwd'])+'/'+str(self._config['name'])+'/config/dev'):
            os.makedirs(str(self._config['cwd'])+'/'+str(self._config['name'])+'/config/dev')

        if not os.path.exists(str(self._config['cwd'])+'/'+str(self._config['name'])+'/utility'):
            os.makedirs(str(self._config['cwd'])+'/'+str(self._config['name'])+'/utility')

        # Create recipe directory
        if not os.path.exists(str(self._config['cwd'])+'/'+str(self._config['name'])+'/recipe/'+str(self._config['name'])):
            os.makedirs(str(self._config['cwd'])+'/'+str(self._config['name'])+'/recipe/'+str(self._config['name']))


        if not os.path.exists(str(self._config['cwd'])+'/'+str(self._config['name'])+'/recipe/'+str(self._config['name'])+'/attributes'):
            os.makedirs(str(self._config['cwd'])+'/'+str(self._config['name'])+'/recipe/'+str(self._config['name'])+'/attributes')

        if not os.path.exists(str(self._config['cwd'])+'/'+str(self._config['name'])+'/recipe/'+str(self._config['name'])+'/files'):
            os.makedirs(str(self._config['cwd'])+'/'+str(self._config['name'])+'/recipe/'+str(self._config['name'])+'/files')

        if not os.path.exists(str(self._config['cwd'])+'/'+str(self._config['name'])+'/recipe/'+str(self._config['name'])+'/recipes'):
            os.makedirs(str(self._config['cwd'])+'/'+str(self._config['name'])+'/recipe/'+str(self._config['name'])+'/recipes')


        file = open(str(self._config['cwd']) +'/'+str(self._config['name'])+ '/recipe/'+str(self._config['name'])+'/attributes/default.rb', "w")
        file.close()

        if not os.path.exists(str(self._config['cwd']) + '/'+str(self._config['name'])+'/config/dev/recipes/function.properties'):
            file = open(str(self._config['cwd']) + '/'+str(self._config['name'])+'/config/dev/function.properties',"w")
            file.write('ANSWER=43')
            file.close()

        if not os.path.exists(str(self._config['cwd']) + '/'+str(self._config['name'])+'/recipe/'+str(self._config['name'])  + '/recipes/default.rb'):
            file = open(str(self._config['cwd']) + '/'+str(self._config['name'])+'/recipe/'+str(self._config['name'])  + '/recipes/default.rb',"w")
            file.write('#')
            file.write('# Cookbook Name:: '+str(self._config['name']))
            file.write('# Recipe:: default')
            file.close()

        if not os.path.exists(str(self._config['cwd']) +'/'+str(self._config['name'])+ '/recipe/'+str(self._config['name']) + '/recipes/setup.rb'):
            file = open(str(self._config['cwd']) + '/'+str(self._config['name'])+'/recipe/'  +str(self._config['name'])+ '/recipes/setup.rb',"w")
            file.write('# Install services and dependencies')
            file.write('#')
            file.close()

        if not os.path.exists(self._config['cwd']+'/'+str(self._config['name'])+'/recipe/Berksfile'):

            file = open(self._config['cwd']+'/'+str(self._config['name'])+'/recipe/Berksfile', "w")
            file.write('source "https://supermarket.getchef.com"')
            file.write("")
            file.write("metadata")
            file.write('cookbook '+self._config['name'])
            file.close()


    def _describe_opsworks_environment(self):
        '''
        Find the default vpc for the given region

        Args:
            None

        Returns:
            a dictionary the contains the  vpc ID, list subnets and default
            security group
        '''
        try:
            vpc_info = {}
            ec2_client = utility.get_api_client(
                self._profile,
                self._region,
                'ec2'
            )

            response = ec2_client.describe_vpcs()

            for vpc in response['Vpcs']:
                if vpc['IsDefault']:
                    subnets = self._find_default_subnets(vpc['VpcId'])
                    if subnets:
                        vpc_info['subnets'] = subnets

                    security_group = self._find_default_security_group(vpc['VpcId'])
                    if security_group:
                        vpc_info['security_group'] = security_group

                    opsworks_role = self._find_opsworks_role()
                    if opsworks_role:
                        vpc_info['role'] = opsworks_role

                    logger.info(json.dumps(vpc_info, indent=2))
                    return vpc_info
        except Exception as wtf:
            logger.error('Exception caught in create_opsworks(): {}'.format(wtf))
            traceback.print_exc(file=sys.stdout)

        return {}

    def _find_opsworks_role(self):
        try:
            iam_client = utility.get_api_client(
                self._profile,
                self._region,
                'iam'
            )

            response = iam_client.list_roles(MaxItems=5)
            while response:
                for role in response['Roles']:
                    if role['RoleName'] == 'opsworks_basic_vpc_execution':
                        logger.info('found role: {}'.format(role['Arn']))
                        return role['Arn']

                if response['IsTruncated']:
                    response = iam_client.list_roles(
                        MaxItems=5,
                        Marker=response['Marker']
                    )
                else:
                    response = None
        except Exception as wtf:
            logger.error('Exception caught in create_opsworks(): {}'.format(wtf))
            traceback.print_exc(file=sys.stdout)

        return None

    def _find_default_security_group(self, vpc_id):
        try:
            ec2_client = utility.get_api_client(
                self._profile,
                self._region,
                'ec2'
            )

            response = ec2_client.describe_security_groups(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )

            for sg in response['SecurityGroups']:
                logger.info('found candidate security group: {}'.format(sg['GroupId']))
                if sg['GroupName'] == 'default':
                    logger.info('found security group: {}'.format(sg['GroupId']))
                    return sg['GroupId']
        except Exception as wtf:
            logger.error('Exception caught in create_opsworks(): {}'.format(wtf))
            traceback.print_exc(file=sys.stdout)

        return None

    def _find_default_subnets(self, vpc_id):
        try:
            subnets = []
            ec2_client = utility.get_api_client(
                self._profile,
                self._region,
                'ec2'
            )

            response = ec2_client.describe_subnets(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )

            for subnet in response['Subnets']:
                if subnet['DefaultForAz'] == True:
                    subnets.append(subnet['SubnetId'])

            logger.info('Found subnets: {}'.format(subnets))
            return subnets
        except Exception as wtf:
            logger.error('Exception caught in create_opsworks(): {}'.format(wtf))
            traceback.print_exc(file=sys.stdout)

        return None

    def deploy_opsworks(self):
        """
        Deploy an existing opsworks to the indicated by creating CF template...

        Args:
            None

        Returns:
            True if the opsworks is deployed
            False if the opsworks is not deployed for some odd reason
        """
        try:
            logger.info(self._config)
            cwd = os.getcwd()
            dirs = cwd.split('/')
            opsworks_name = dirs[-1]
            logger.info('opsworks_name: {}'.format(opsworks_name))
            return True
        except Exception as x:
            logger.error('Exception caught in deploy_opsworks(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return False

    def execute_command(self, command):
        buf = ""
        try:
            p = subprocess.Popen(command, stdout=subprocess.PIPE)
            out, err = p.communicate()
            for c in out:
                buf = buf + c
            return p.returncode, buf
        except subprocess.CalledProcessError as x:
            logger.error('Exception caught in create_opsworks(): {}'.format(x))
            traceback.print_exc(file=sys.stdout)
            return False
            return x.returncode, None

    def write_config_ini(self, destination_directory, env_info):
        file_name = '{}/config/config.ini'.format(destination_directory)

        logger.info('config ini file name: '+str(file_name))

        with open(file_name, 'w') as ini_file:
            ini_file.write('[dev]\n')
            if 'security_group' in env_info:
                ini_file.write('security_group={}\n'.format(env_info['security_group']))
            else:
                ini_file.write('security_group=ADD_SECURITY_GROUP\n')

            if 'subnets' in env_info:
                wrk = str()
                for subnet in env_info['subnets']:
                    if len(wrk) == 0:
                        wrk = subnet
                    else:
                        wrk = '{},{}'.format(wrk, subnet)

                ini_file.write('subnets={}\n'.format(wrk))
            else:
                ini_file.write('subnets=ADD_SUBNETS\n')

            if 'role' in env_info:
                ini_file.write('role={}\n'.format(env_info['role']))
            else:
                ini_file.write('role=ADD_YOUR_OPSWORKS_IAM_SERVICE_ROLE\n')

            ini_file.write('bucket=ADD_YOUR_ARTIFACT_BUCKET\n')
            ini_file.write('\n')
