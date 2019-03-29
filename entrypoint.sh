#! /bin/bash -e

if id syncuser ; then
  userdel syncuser
  groupdel syncuser
fi

groupadd -g $PGID syncuser
useradd -l -u $PUID -g syncuser syncuser
chown syncuser:syncuser $TARGET_DIR
chmod $PERMISSIONS_MASK $TARGET_DIR

if [ "${SET_STICKY_BIT}" = true ]; then
  chmod g+s $TARGET_DIR
fi

if [ "${REMOVE_ORPHANS}" = true ]; then
  exec sudo -u syncuser -H python -c "/usr/src/app/terrasync.py --target=${TARGET_DIR} --quick --remove-orphan"
else
  exec sudo -u syncuser -H python /usr/src/app/vendor/terrasync.py --target=${TARGET_DIR} --quick
fi
