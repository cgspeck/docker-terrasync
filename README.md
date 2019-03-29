# Docker-Terrasync

This will sync down the entire world scenery database to the specified mount.

## Usage

### Docker

```bash
docker create \
    --name=terrasync
    -e PUID=1000 \
    -e PGID=1000 \
    -v </path/to/your/share>:/terrasync
    cgspeck/terrasync
```

### Docker-Compose

```yaml
version: "2"
services:
  nginx:
    image: cgspeck/terrasync
    container_name: terrasync
    environment:
      - PUID=1000
      - PGID=1000
    volumes:
      - </path/to/your/share>:/terrasync
```

## Parameters

Parameter | Function
--- | ---
-e PUID=1000 | User ID
-e PGID=1000 | Group ID

-e PERMISSIONS_MASK=755 | These permissions will be applied to the mount
-e REMOVE_ORPHANS=false | If true, will be passed to `terrasync.py` and cause it to delete orphaned files in the mount

### User / Group Identifiers

You can specify user ID and group IDs for use in the container to avoid permission issues between the container and the host.

Ensure any volume directories on the host are owned by the same user you specify.

You can use `id` to find your user id and group id:

```
$ id foo
uid=1000(foo) gid=1000(foo
```

###
https://rock-it.pl/how-to-write-excellent-dockerfiles/
https://sourceforge.net/p/flightgear/flightgear/ci/next/tree/scripts/python/
http://wiki.flightgear.org/TerraSync
