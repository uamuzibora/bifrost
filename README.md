## Bifrost

_Connects our puny dev machines with Amazon's giant cloud._

Command line interface for Uamuzi Bora test instances on EC2.

### Prerequisites

 * Python 2.7.x
 * Boto: `pip install boto`
 * Your AWS credentials available in your environment:
```shell
AWS_SECRET_ACCESS_KEY=xxxxxxxxxx
AWS_ACCESS_KEY_ID=xxxxxxxxxxx
export AWS_SECRET_ACCESS_KEY
export AWS_ACCESS_KEY_ID
```
or better: define them in your `.bash_profile` or `.zshrc`

### Usage

NB: `<commit id>` refers to the **first 7 letters** of the SHA hash of a Git commit in [Nafasi](https://github.com/uamuzibora/nafasi)

`bifrost --start <commit id>` Starts and returns the public DNS of an EC2 instance of that commit

`bifrost --stop <commit id>` Stops and terminates (if running) the instance with the specified commit

`bifrost --list` Lists all running Uamuzi Bora instances

`bifrost --ssh <commit id>` Starts an SSH session with the instance of that commit (if running)

`bifrost --dump <commit id>` Dumps the MySQL db of the instance associated with the commit and SCPs it to your current working directory as `openmrs.sql`. **Warning:** Will overwrite any existing openmrs.sql file in your directory.
