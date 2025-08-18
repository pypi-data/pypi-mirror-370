# Media-Mgr

**Media-Mgr** helps organize and search for media files on specified servers. Focus is currently PLEX based and includes PLEX server upgrade support on Ubuntu installs.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install **media-mgr**.

```bash
pip install media-mgr
```

## CLI Controls

The following CLI controls are provided in this package for keeping track of media server categories and media server coordinates.

* mm-mediacfg
* mm-srvcfg

The following CLI controls assist with media server contents for search, organization, PLEX upgrades and miscellaneous tools (EXIF renamer)

* mm-util
* mm-path
* mm-search
* mm-gather
* mm-exif
* mm-plex-upg

Finally, these next sets of CLI controls are task specific for media management

* mount-drives
* search-plex
* move-plex
* cons-plex
* upgrade-plex
* upgrade-plex-all

Each command has help syntax via CLI -h argument

For example:

```bash
╰─ mount-drives -h                                                                                                                                                                                                      ─╯
usage: mount-drives [-h] [-v] [--ipv4 <ipv4.addr>]

-.-.-. Mount Drives on Server utility

options:
  -h, --help          show this help message and exit
  -v, --verbose       run with verbosity hooks enabled
  --ipv4 <ipv4.addr>  Server IPV4

-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
```

or

```bash
╰─ search-plex -h                                                                                                                                                                                                       ─╯
usage: search-plex [-h] [-v] [--version] [--ipv4 <ipv4.addr>] [<term_1> .. <term_n> ...]

-.-.-. Search All Servers utility

positional arguments:
  <term_1> .. <term_n>  Search terms to match

options:
  -h, --help            show this help message and exit
  -v, --verbose         run with verbosity hooks enabled
  --version             top-level package version
  --ipv4 <ipv4.addr>    Server IPV4

-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
```

or

```bash
╰─ mm-gather -h                                                                                                                                                                                                         ─╯
usage: mm-gather [-h] [-v] [--version] {show.titles,show.all.titles,show.bundles,store.bundles,show.plex.n.worker.bundles,store.plex.n.worker.bundles} ...

-.-.-. Gathering for media manager

positional arguments:
  {show.titles,show.all.titles,show.bundles,store.bundles,show.plex.n.worker.bundles,store.plex.n.worker.bundles}
    show.titles         Show retrieved titles
    show.all.titles     Show ALL retrieved titles
    show.bundles        Show title bundles
    store.bundles       Store title bundles
    show.plex.n.worker.bundles
                        Show title bundles for Plex and Worker servers
    store.plex.n.worker.bundles
                        Store title bundles for Plex and Worker servers

options:
  -h, --help            show this help message and exit
  -v, --verbose         run with verbosity hooks enabled
  --version             top-level package version

-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
```

or

```bash
╰─ move-plex -h                                                                                                                                                                                                         ─╯
usage: move-plex [-h] [--version] [-v] [--ipv4 <ipv4.addr>] [--test] <from.dir> <to.dir> ...

-.-.-. Move for media manager

positional arguments:
  <from.dir>            FROM base directory name
  <to.dir>              TO base directory name
  <term_1> .. <term_n>  search terms for move operation

options:
  -h, --help            show this help message and exit
  --version             top-level package version
  -v, --verbose         run with verbosity hooks enabled
  --ipv4 <ipv4.addr>    Server IPV4
  --test                Test move operation

-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
```

## License

[MIT](https://choosealicense.com/licenses/mit/)

