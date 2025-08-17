
# cf_dns_xethhung12

## Execution
The program requires two environment variables, 
* `py_cf_dns_zone` Zone ID can be found in cloudflare domain over view page (right bottom corner) 
* `py_cf_dns_token` generated in cloudflare profile > API Token page, the token require Zone:ZOne:read and Zone:DNS:read permission to the selected zone
Run through python interpreter:

### Help command
```shell
python -m cf_dns_xethhung12 -h
```

### Load cloudflare DNS records to tf file and then import the resource into tf state

```shell
# make sure the two environment variable is set
cf-dns-xethhung12 cf-dns as-tf > dns.tf
cf-dns-xethhung12 cf-dns import-tf -f dns.tf # check the script generated and execute it carefully

## result should be similar to below
# .
# .
# .
# tofu import cloudflare_record.{resource name} {zone id}/{resource id in cloudflare}
# tofu import cloudflare_record.{resource name} {zone id}/{resource id in cloudflare}
# tofu import cloudflare_record.{resource name} {zone id}/{resource id in cloudflare}
# .
# .
# .
```

Run through python project script
```shell
cf-dns-xethhung12 -h
```
## Development
The project requires `python` (3+ version) installed and `pip` ready for use on adding manage dependencies

#### Tools
|Name|Platform|Type|Description|
|---|---|---|---|
|install-dependencies.sh|shell|script| The scripts for installing depencies required|
|build.sh|shell|script| The scripts for build the package|
|build-and-deploy.sh|shell|script| The scripts for build and deploy the package|

* install-dependencies.sh
The script will install dependencies listed in `dev-requirements.txt` and `requirements.txt`. The first requirement file contains the dependencies for development like build and deploy tools. The second requirement file defined all required dependencies for the making the package works (**actual dependencies**).

## Useful Scripts
### Project Versioning
For version update in `pyproject.toml`.
This project use package [`xh-py-project-versioning`](https://github.com/xh-dev/xh-py-project-versioning) to manipulate the project version.

Simple usage includes:\
Base on current version, update the patch number with dev id
`python -m xh_py_project_versioning --patch` \
In case current version is `0.0.1`, the updated version will be `0.0.2-dev+000` 

To prompt the dev version to official version use command.
`python -m xh_py_project_versioning -r`.
Through the command, version `0.0.2-dev+000` will be prompt to `0.0.2` official versioning.

Base on current version, update the patch number directly
`python -m xh_py_project_versioning --patch -d` \
In case current version is `0.0.1`, the updated version will be `0.0.2` 

Base on current version, update the minor number directly
`python -m xh_py_project_versioning --minor -d` \
In case current version is `0.0.1`, the updated version will be `0.1.0` 

Base on current version, update the minor number directly
`python -m xh_py_project_versioning --minor -d` \
In case current version is `0.0.1`, the updated version will be `1.0.0` 