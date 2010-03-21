from fabric.api import *
from fabric.contrib.console import confirm

####################################################
# On a fresh server you must first set up a sudo user

# START SERVER

# 1) login to the server and change the root password
# passwd

# 2) update apt-get
# apt-get update

# 3) install database (mysql)
# apt-get install mysql-server

# 4) add new user
# adduser <user>
# passwd <user>

# 5) add www-data to the <user>'s group
# usermod -a -G <user> www-data

# 6) add <user> to the sudo group
# usermod -a -G sudo <user>

# 7) if wanted, remove password prompt for sudo
# visudo

# 8) login as <user> and set up .ssh keys. Add private keys to authorized_keys to disable ssh pasword prompts
# touch .ssh/authorized_keys
# ssh-keygen -t rsa -C "<server>"

# 9) initialization is complete. Set the <env> variables in the GLOBALS section of this file, and run fabric to set up the environment
# fab server

# POST INITIALIAZION

# 1) create a new database user
# mysql -u root -p
# CREATE DATABASE django_project;
# CREATE USER user IDENTIFIED BY 'pass';
# GRANT ALL ON django_project.* TO user;

# 2) nginx
# copy the example.com script to create the domain specific nginx script

# 3) apache
# copy the example.com script to create the domain specific apache script

# 4) crate any main directories that don't exist, and chwon to user
# mkdir DJANGO_PATH
# mkdir HTML_PATH
# mkdir ENVS_PATH
# mkdir BACKUPS_PATH
# chown user:user .

# DEPLOY

# 1) with the server initialized and prepped, deploy the project
# fab deploy

# 1) django project
# setup local_settings.py
# syncdb

# 2) cron
# link any cron scripts

# 3) restart servers
# fab restart_servers

####################################################

# GLOBALS 
# overwrite most of these in local_settings.py

env.hosts = ['example.com']
env.user = 'root'
env.user_home = '/root'

DOMAIN = None
PROJECT = None

DJANGO_PATH = '/var/www/django'
HTML_PATH = '/var/www/html'
ENVS_PATH = '/var/www/envs'
BACKUPS_PATH = '/var/www/backups'

GITHUB_PROJECT = PROJECT
GITHUB_USER = None
GITHUB_TOKEN = None
GITHUB_EMAIL = None

try:
	from local_settings import *
except ImportError:
	pass

PROJECT_PATH = '%s/%s' % (DJANGO_PATH, PROJECT)


def test():
	run('touch hello_world.py')


def server():
	"""
	(1) Sets up a server after you initialized it. Read the instructions at the top of this document to see how to prep the server.
	"""
	print("Executing on %(host)s as %(user)s" % env)

	# locale
	sudo('locale-gen en_US.UTF-8')
	sudo('/usr/sbin/update-locale LANG=en_US.UTF-8')

	# server
	_apt_get('build-essential')
	_apt_get('emacs')
	_apt_get('git-core')
	_apt_get('nginx')
	_apt_get('apache2')
	_apt_get('libapache2-mod-wsgi')
	_apt_get('python-dev')
	_apt_get('python-setuptools')
	_apt_get('python-imaging')
	_apt_get('python-mysqldb')
	_apt_get('sqlite3')
	_apt_get('mercurial')
	_apt_get('memcached')

	# global python environment
	_easy_install('virtualenv')

	github()

	print('Server initialzation complete. Perform post initialzation steps before running deploy_project')


def deploy():
	"""
	(2) Deploys the project on the server. Make sure you've run init_server and performed the post initialzation steps before running this.
	"""
	nginx()
	apache()

	django()
	html()
	virtualenv()
	cron()


def django():
	"""
	set up django project from github repository, edit local_settings.py
	"""
	if not DJANGO_PATH or not PROJECT_PATH or not GITHUB_USER or not GITHUB_PROJECT:
		print('ERROR: project vars not set. exiting django')
		return False

	with cd(DJANGO_PATH):
		run('git clone git@github.com:%s/%s.git' % (GITHUB_USER, GITHUB_PROJECT))

	with cd(PROJECT_PATH):
		run('touch local_settings.py')


def html():
	"""
	set up html static file directory from django project
	"""
	if not HTML_PATH or not PROJECT_PATH or not DOMAIN:
		print('ERROR: project vars not set. exiting html')
		return False

	with cd(HTML_PATH):
		run('mkdir %s' % DOMAIN)
		run('ln -s %s/media %s/%s/media' % (PROJECT_PATH, HTML_PATH, DOMAIN))


def virtualenv():
	"""
	set up virtualenv for django project
	"""
	if not ENVS_PATH or not PROJECT_PATH or not PROJECT:
		print('ERROR: project vars not set. exiting virtualenv')
		return False

	with cd(ENVS_PATH):
		run('virtualenv %s' % PROJECT)
		_virtualenv('pip install -r %s/utils/requirements.txt' % PROJECT_PATH)


def cron():
	"""
	set up backup directory for cron

	must manually link cron scripts
	"""
	if not BACKUPS_PATH or not PROJECT:
		print('ERROR: project vars not set. exiting cron')
		return False

	with cd(BACKUPS_PATH):
		run('mkdir %s' % PROJECT)


def github():
	"""
	Sets up global variables for github.
	"""
	if not GITHUB_USER or not GITHUB_TOKEN or not GITHUB_EMAIL:
		print('ERROR: github vars not set. exiting')
		return False

	run('git config --global github.user %s' % GITHUB_USER)
	run('git config --global github.token %s' % GITHUB_TOKEN)
	run('git config --global github.email %s' % GITHUB_EMAIL)


def nginx():
	"""
	Coppies default nginx files into /etc/nginx/sites-available and links /etc/nginx/sites-enabled

	You must have created the file for the specific domain.
	"""
	if not DOMAIN:
		print('ERROR: project vars not set. exiting nginx')
		return False
	require('user_home')

	put('nginx/%s' % DOMAIN, env.user_home)
	sudo('mv ~/%s /etc/nginx/sites-available/%s' % (DOMAIN, DOMAIN))
	sudo('ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s' % (DOMAIN, DOMAIN))


def apache():
	"""
	Coppies default apache files into /etc/apache/sites-available and links /etc/apache/sites-enabled

	You must have created the file for the specific domain.
	"""
	if not DOMAIN:
		print('ERROR: project vars not set. exiting apache')
		return False
	require('user_home')

	put('apache/%s' % DOMAIN, env.user_home)
	sudo('mv ~/%s /etc/apache2/sites-available/%s' % (DOMAIN, DOMAIN))
	sudo('ln -s /etc/apache2/sites-available/%s /etc/apache2/sites-enabled/%s' % (DOMAIN, DOMAIN))


def restart_servers():
	sudo('/etc/init.d/nginx restart')
	sudo('/etc/init.d/apache2 restart')


# utilities
def _apt_get(package):
	"""
	Install a single package on the remote server with Apt.
	"""
	sudo('apt-get install -y %s' % package)
 

def _easy_install(package):
	"""
	Install a single package on the remote server with easy_install.
	"""
	sudo('easy_install %s' % package)


def _virtualenv(command):
	"""
	Executes a command in this project's virtual environment.
	"""
	if not ENVS_PATH or not PROJECT:
		print('ERROR: project vars not set. exiting virtialenv')
		return False

	run('source %s/%s/bin/activate && %s' % (ENVS_PATH, PROJECT, command))
