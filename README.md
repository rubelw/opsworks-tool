# Opsworks Tool
A tool to create and deploy Opsworks stacks to AWS.


## Current version - 0.0.1:

* Create a new Python 2.7 AWS Opsworks from included template.
* Deploy AWS Opsworks created with this tool. It generates a CloudFormation file and creates a stack from that template.

## Usage:
Create a new opsworks stack:
```
Usage: opsworkstool new [OPTIONS]

Options:
  -d, --directory TEXT  target directory for new Opsworks recipe, defaults to
                        current directory
  -n, --name TEXT       name of the new opsworks skeleton  [required]
  -p, --profile TEXT    AWS CLI profile to use in the deployment, more details
                        at http://docs.aws.amazon.com/cli/latest/userguide
                        /cli-chap-getting-started.html
  -r, --region TEXT     target region, defaults to your credentials default
                        region
  --debug               Turn on debugging
  --help                Show this message and exit.

Example:
opsworkstool -sn example --region us-east-2 # make a Flask webservice in example/main.py
```

Create a new opsworks template:
```
Usage: opsworkstool deploy [OPTIONS]

Options:
  -d, --directory TEXT  scratch directory for deploy, defaults to /tmp
  -p, --profile TEXT    AWS CLI profile to use in the deployment
  -r, --region TEXT     target region, defaults to your credentials default
                        region
  --help                Show this message and exit.
  
Example:
opsworkstool new --name test --profile will --directory /tmp/junk --region us-east-1
```
*More details on AWS profile credentials [here](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html).*


## What just happened

* This just created the needed files
```
├── config
│   ├── config.ini
│   └── dev
│       └── function.properties
├── recipe
│   ├── Berksfile
│   └── test
│       ├── attributes
│       │   └── default.rb
│       ├── files
│       └── recipes
│           ├── default.rb
│           └── setup.rb
├── template.json
└── utility
    ├── __init__.py
    └── tools.py
```

## The next steps
* Edit the template.json as needed, and edit the config/config.ini for the parameters for the needed stage.  Note: The default state is dev
* Edit the recipe/test/recipe/setup.rb recipe


## Deploying the Opswork template

```
opsworkstool deploy --profile will -s dev
```



## What you will need:

* An AWS account
* A VPC setup in that account (or access to create one). See more about AWS default VPC [here](http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/default-vpc.html). 
* At least one subnet in that account (or access to create one)
* An IAM role to assign to the opsworks instance. If you do not have a suitable IAM role you can get some idea [here](http://docs.aws.amazon.com/lambda/latest/dg/vpc-rds-create-iam-role.html).
* A very simple security group
* An S3 bucket where you can put build/deployment artifacts. This bucket **must** be in the same AWS region as your function.
* A minimal Python 2.7 development environment including virtualenv or virtualenv wrapper



