#! /bin/bash -e

if id syncuser ; then
  userdel syncuser
  groupdel syncuser
fi

groupadd -g $PGID syncuser
useradd -l -u $PUID -g syncuser syncuser
chown syncuser:syncuser $TARGET_DIR

if [ "${REMOVE_ORPHANS}" = true ]; then
  exec sudo -E -u syncuser -H python /usr/src/app/wrapper.py --target=${TARGET_DIR} --remove-orphan
else
  exec sudo -E -u syncuser -H python /usr/src/app/wrapper.py --target=${TARGET_DIR}
fi
