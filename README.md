## Bifrost

_Connects our puny dev machines with Amazon's giant cloud._

Command line interface for Uamuzi Bora test instances on EC2.

### Prerequisites

 * [Python](http://www.python.org/download/) 2.7.x (tested on 2.7.2)
  * _Protip: Consider using [Pythonz](https://github.com/saghul/pythonz) if this means you'll end up with multiple Python installs._
 * [Pip](http://www.pip-installer.org/en/latest/installing.html) - in order to install Boto & PyGithub.
  * `$ curl http://python-distribute.org/distribute_setup.py | python`
  * `$ curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python`
 * [Boto](https://github.com/boto/boto): `$ pip install boto`
 * [PyGithub](https://github.com/jacquev6/PyGithub): `$ pip install PyGithub`
 * _Optional:_ [Mosh](http://mosh.mit.edu) - If you want to use Mosh over SSH to connect to instances.
 * Your AWS credentials available in your environment:

```shell
AWS_SECRET_ACCESS_KEY=xxxxxxxxxx
AWS_ACCESS_KEY_ID=xxxxxxxxxxx
export AWS_SECRET_ACCESS_KEY
export AWS_ACCESS_KEY_ID
```

or better: define them in your `.bash_profile` or `.zshrc` e.g.
```shell
# AWS config
export AWS_ACCESS_KEY_ID='xxxxxxxxxx'
export AWS_SECRET_ACCESS_KEY='xxxxxxx'
```

### Usage

NB: `<commit id>` refers to the **first 7 letters** of the SHA hash of a Git commit in [Nafasi](https://github.com/uamuzibora/nafasi)

`$ bifrost --start=<commit id>` Starts of an EC2 instance of that commit. You may specify 'head'.

`$ bifrost --stop` Stops and terminates (if running) all instances belonging to you.

`$ bifrost --list` Lists all running Uamuzi Bora instances belonging to you.

`$ bifrost --ssh` Starts an SSH session with your instance.

`$ bifrost --mosh` Starts a [Mosh](http://mosh.mit.edu) session with your instance. Especially for @andrewlkho.

`$ bifrost --dump` Dumps the MySQL db of the instance associated with the commit and SCPs it to your current working directory as `openmrs.sql`.

`$ bifrost --view` Opens your system's default browser at the root URL of your OpenMRS install on the instance.
