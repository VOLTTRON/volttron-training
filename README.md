# Jupyter Notebooks for VOLTTRON

This repository contains source code and tools for setting up one or more
Docker (https://www.docker.com/) containers on a Linux server, each 
containing a VOLTTRON (https://www.energy.gov/eere/buildings/volttron) instance 
and a Jupyter (http://jupyter.org/) server. The goal is to create an environment 
in which end-users interact with a Jupyter web client to develop, install and test 
VOLTTRON agents.

This repository uses a Django (https://www.djangoproject.com/) user interface to
facilitate quick and easy user access to the Jupyter clients. The user of a Jupyter
client does not need to use SSH or log into the remote host directly.

The initial purpose of this environment is to host a Hackathon in September 2018
at Stanford Linear Accelerator Center (SLAC), but it has been designed to be
repurposed for other, similar uses.

# Step 1 (Administrator): Installation

Step 1 needs to be done only once, and must be done by an administrator with direct
access to the Linux host. If a Linux host server has already been set up, 
please advance to Step 2 or 3.

## Configure a Linux Host and Log In Via SSH

These instructions assume that a Linux host has been set up and is running
Ubuntu, and that its DNS host name is ```hackathon.ki-evi.com``` (substitute
a different host name below if appropriate).

First, ssh into the host:

    $ ssh ubuntu@hackathon.ki-evi.com


## Install Docker

Clone the repository and install Docker:

    $ cd ~
    $ git clone https://github.com/VOLTTRON/volttron-training.git
        (supply github credentials)
    $ cd volttron-training
    $ source install_docker.sh

VOLTTRON currently depends on Python 2.x, so the source code in this repository uses
Python 2.x and Django 1.x.

## Build a Docker Image

Adjust some file permissions to allow them to execute inside a Docker container,
and then build a Docker image that will be each container's starting point:

    $ source alter_file_ownership.sh
    $ source build_image.sh

build_image.sh creates a Docker image named "hackathon".

## Build a Virtual Environment and Install the Application's Dependencies

    $ cd ~/volttron-training
    $ source install_virtualenv.sh

Activate the virtual environment:

    $ source env/bin/activate

Install the application's library dependencies from requirements.txt:

    $ pip install -r requirements.txt

## Install and Set Up Postgres

Install Postgres:

    $ sudo apt-get install postgresql postgresql-contrib

Start postgres, create a postgres user and create a database:

    $ sudo systemctl start postgresql

Create a postgres user:

    $ sudo su postgres -c 'createuser -d -l -R -S -P django'
        Enter the new user's password: docker*1

Create a database:

    $ sudo su postgres -c 'createdb -O django volttron-training'

Ensure that local authentication is correct:

    Open the file /etc/postgresql/9.5/main/pg_hba.conf and change 'peer' to 'trust'
    Restart the server:
        $ sudo service postgresql restart

Log into psql and set your password:

    $ psql -U postgres
    # ALTER USER postgres with password 'docker*1';
    # \q

    Open the file /etc/postgresql/9.5/main/pg_hba.conf and change 'trust' to 'md5'

Restart the postgresql server:

    $ sudo service postgresql restart

## Initialize the application

    $ cd ~/volttron-training
    $ source env/bin/activate
    $ python hackathon/manage.py migrate
    $ python hackathon/manage.py createsuperuser
        # create superuser 'admin' with password 'port-1220'

Edit the Django settings file, settings.py, as follows:

    Change PUBLIC_URL to be the server’s DNS name
    (hackathon.ki-evi.com in this example).
    
    Adjust container and memory configuration parameters as needed.
    HOST_MEMORY for AWS T2 instances:
        micro   = 1000  MB (1 containers)
        small   = 2000  MB (3 containers)
        medium  = 4000  MB (7 containers)
        large   = 8000  MB (15 containers)
        xlarge  = 16000 MB (31 containers)
        2xlarge = 32000 MB (63 containers)

# Step 2 (Administrator): Start the Django Server

This step must be done by an administrator logged into the Linux host via SSH.

Activate the virtual environment and start Django:

    $ cd ~/volttron-training
    $ source env/bin/activate
    $ source run_server.sh

In addition to starting the django server, ```run_server.sh``` also loosens file
permissions on some script files, thus ensuring that they can still execute in a 
running container after the source code has been updated with a ```git pull```.

# Step 3 (Notebook User): Run a Notebook in a Container

In a web browser, navigate to a URL containing the PUBLIC_URL that was set above
in settings.py, along with the port number (8000) and app name (volttron):

    http://hackathon.ki-evi.com:8000/volttron

## Sign Up for a New Account

If the user has not yet obtained a login, get one as follows:

    Click signup.
    Enter a new ID and password.
    The server automatically assigns unique port numbers to the account.

## Log Into an Existing Account

To log into an existing account:

    Enter an existing ID and password.
    Click the Login button or the login link.
    The server displays the account's port numbers.

## Logged-In User

If the account's Docker container isn't already running, start it as follows:

    Click Start Volttron.
       (Wait... There is a delay while the container starts.)

If the Docker container is running:

    The page displays hyperlinks and a Stop Volttron button.
    Click the Jupyter Notebook link to open a Jupyter client web page.
    Click the Volttron Central link to display a VC client web page.

When ready to stop, stop the container and log out:

    Click logout.
    Logging out stops the container first, as a side-effect.
        (Wait... There is a delay while the container stops.)

## Jupyter Notebook

When prompted for a password, enter:

    volttron

## VOLTTRON Central

When prompted for an ID and password, enter:

    admin
    admin

Device metrics can be viewed in VOLTTRON Central by repeatedly 
clicking the triangle at the left.

# Django Web Admin (Administrator)

Use Django web administration to inspect and troubleshoot a user's
Docker container configuration.

In a web browser, navigate to the admin URL, for instance:

    hackathon.ki-evi.com:8000/admin
        (login / password: admin / port-1220)

There is a one-to-one correspondence between a django user and a “volttron” django object. 
An end-user’s “signup” action creates both a user and a “volttron” object.
Removing a user in admin does a cascade delete of its associated “volttron” object.

## Admin “volttron” Page

The IS RUNNING and ERROR status values can get outdated due to container 
activity not initiated from django (e.g., a container crash, or a scripted 
container start or stop). To sync the status display:

    Check the top checkbox (i.e., select all) and click Sync containers

An administrator can start/stop containers by selecting them and selecting the 
corresponding Action.
