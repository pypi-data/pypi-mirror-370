# Bitergia Analytics GrimoireELK backends

GrimoireELK backends available in Bitergia Analytics:
### public-inbox

Software for efficiently managing and archiving public mailing
lists using Git repositories.
- `projects.json`
```
{
    "linux": {
        "public_inbox": [
            "linux /path/to/mirror/repository"
        ]
    }
}
```

- `setup.cfg`
```
[public_inbox]
raw_index = public_inbox_raw
enriched_index = public_inbox_enriched
latest-items = false
```

### Topicbox

Email discussion platform that facilitates organized group
communication through dedicated email groups.

- `projects.json`
```
{
    "Example": {
        "topicbox": [
            "https://example.topicbox.com/groups/group-1",
            "https://example.topicbox.com/groups/group-2"
        ]
    }
}
```

- `setup.cfg`
```
[topicbox]
raw_index = topicbox_raw
enriched_index = topicbox_enriched
account-id = xxxx  # Look into the Perceval backend
studies = [ enrich_demography:topicbox ]  # (optional)

[enrich_demography:topicbox]  # (optional)
```

### Pontoon

Web-based localization platform that facilitates collaborative
translation of software and documentation

- `projects.json`
```
{
    "Example": {
        "pontoon": [
            "https://pontoon.mozilla.org af",
            "https://pontoon.mozilla.org es"
        ]
    }
}
```

- `setup.cfg`
```
[pontoon]
raw_index = pontoon_raw
enriched_index = pontoon_enriched
studies = [ enrich_demography:pontoon ]  # (optional)

[enrich_demography:pontoon]  # (optional)
```


## Requirements

 * Python >= 3.9

You will also need some other libraries for running the tool, you can find the
whole list of dependencies in [pyproject.toml](pyproject.toml) file.

## Installation

There are several ways to install grimoire-elk-public-inbox on your system: packages or source 
code using Poetry or pip.

### PyPI

grimoire-elk-public-inbox can be installed using pip, a tool for installing Python packages. 
To do it, run the next command:
```
$ pip install grimoire-elk-public-inbox
```

### Source code

To install from the source code you will need to clone the repository first:
```
$ git clone https://github.com/bitergia-analytics/grimoirelab-elk-public-inbox
$ cd grimoirelab-elk-public-inbox
```

Then use pip or Poetry to install the package along with its dependencies.

#### Pip
To install the package from local directory run the following command:
```
$ pip install .
```
In case you are a developer, you should install grimoire-elk-public-inbox in editable mode:
```
$ pip install -e .
```

#### Poetry
We use [poetry](https://python-poetry.org/) for dependency management and 
packaging. You can install it following its [documentation](https://python-poetry.org/docs/#installation).
Once you have installed it, you can install grimoire-elk-public-inbox and the dependencies in 
a project isolated environment using:
```
$ poetry install
```
To spaw a new shell within the virtual environment use:
```
$ poetry shell
```

## License

Licensed under GNU General Public License (GPL), version 3 or later.
