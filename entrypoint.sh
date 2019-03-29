#! /bin/bash -e

if id syncuser ; then
  userdel syncuser
  groupdel syncuser
fi

groupadd -g $PGID syncuser
useradd -l -u $PUID -g syncuser syncuser
chown syncuser:syncuser $TARGET_DIR

if [ "${REMOVE_ORPHANS}" = true ]; then
  exec sudo -u syncuser -H python /usr/src/app/terrasync.py --target=${TARGET_DIR} --quick --remove-orphan
else
  exec sudo -u syncuser -H python /usr/src/app/vendor/terrasync.py --target=${TARGET_DIR} --quick
fi
