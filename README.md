# Docker-Terrasync

This will sync down the entire world scenery database to the specified mount.

The script itself is cloned directly from the [Flightgear](https://sourceforge.net/p/flightgear/flightgear/ci/next/tree/scripts/python/) repository and is licensed under the GNU GPLv2.

You can read about the script on its wiki [here](http://wiki.flightgear.org/TerraSync).

## Usage

### Docker

```bash
docker run \
    --rm \
    --name=terrasync \
    -e URL="https://dream.t3r.de/fgscenery/" \
    -e PUID=1000 \
    -e PGID=1000 \
    -v </path/to/your/share>:/terrasync \
    cgspeck/terrasync:latest
```

## Parameters

Parameter | Function
--- | ---
-e URL="https://dream.t3r.de/fgscenery/" | Which Flightgear URL to use
-e PUID=1000 | User ID
-e PGID=1000 | Group ID
-e REMOVE_ORPHANS=false | If true, will be passed to `terrasync.py` and cause it to delete orphaned files in the mount

### User / Group Identifiers

You can specify user ID and group IDs for use in the container to avoid permission issues between the container and the host.

Ensure any volume directories on the host are owned by the same user you specify.

You can use `id` to find your user id and group id:

```
$ id foo
uid=1000(foo) gid=1000(foo)
```

### Known Flightgear URLS

The full list of mirrors [is here](https://toolbox.googleapps.com/apps/dig/#ANY/):

* https://dream.t3r.de/fgscenery/
* https://mpserver16.flightgear.org/scenery/
* http://ns334561.ip-5-196-65.eu/terrasync/
* https://ukmirror.flightgear.org/fgscenery/
* http://flightgear.sourceforge.net/scenery

Linked from [this part](https://toolbox.googleapps.com/apps/dig/#ANY/terrasync.flightgear.org) of the Terrasync wiki entry. 
