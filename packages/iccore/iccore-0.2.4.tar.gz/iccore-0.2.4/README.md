# iccore

This package is part of the [Common Tooling Project](https://ichec-handbook.readthedocs.io/en/latest/src/common_tools.html) at the [Irish Centre for High End Computing](https://www.ichec.ie).

It is a collection of common data structures, data types and low-level utilities used in other ICHEC 'common tools'.

# Features #

The package consists of:

* `data structures` (list, strings, dicts etc.) and utilities for working with them
* tooling for interacting with `system resources`, such as external processes, the filesystem and network.
* basic `data types` for describing people, organizations, projects and code repositories - to support `process automation` and Open Science and FAIR activites. 

# Usage #

## System Resources ##

### Filesystem ###

You can replace all occurences of a string with another recursively in files with:

``` shell
iccore filesystem replace_in_files --target $REPLACE_DIR --search $FILE_WITH_SEARCH_TERM --replace $FILE_WITH_REPLACE_TERM 
```

The `search` and `replace` terms are read from files. This can be handy to avoid shell escape sequences - as might be needed in `sed`.

### Networking ###

You can download a file with:

``` shell
iccore network download --url $RESOURCE_URL --download_dir $WHERE_TO_PUT_DOWNLOAD
```

## Process Automation ##

### Project Management ###

You can get Gitlab Milestones given a project id and access token with:

``` shell
iccore gitlab --token $GITLAB_TOKEN milestone $PROJECT_ID
```

where `$GITLAB_TOKEN` is an access token for the project obtainable through the Gitlab Web UI and `$PROJECT_ID` is a numerical identifier for the project, obtainable in the Settings->General view of the Gitlab UI. The `GITLAB_TOKEN` should have sufficient access permissions to read the project milestones.


You can get the version number of the most recent project release with:

``` shell
iccore gitlab --token $GITLAB_TOKEN latest_release $PROJECT_ID
```

or download a particular release asset with:


``` shell
iccore gitlab --token $GITLAB_TOKEN latest_release $PROJECT_ID --asset_name $ASSET_NAME
```

The token should have suitable permissions to download project release assets, in particular read api and repo access and Developer Role.

### Repo Info ###

You can get info about a git repo with:

``` shell
iccore git info 
```

run in the repo.

# Install  #

It is available on PyPI:

``` sh
pip install iccore
```

# License #

This project is licensed under the GPLv3+. See the incluced `LICENSE.txt` file for details.
