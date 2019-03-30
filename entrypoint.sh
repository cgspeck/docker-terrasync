#! /bin/bash -e

if id syncuser &> /dev/null; then
  echo "Removing existing user"
  userdel syncuser
fi

if ! grep $PGID /etc/group &> /dev/null; then
  if grep syncuser /etc/group &> /dev/null; then
    echo "Deleting existing syncuser group"
    groupdel syncuser
  fi
  echo "Creating syncuser group"
  groupadd -g $PGID syncuser
fi

echo "Creating syncuser"
useradd -l -u $PUID -g $PGID syncuser
chown syncuser:$PGID $TARGET_DIR

if [ "${REMOVE_ORPHANS}" = true ]; then
  echo "Starting sync with remove orphans flag"
  exec sudo -E -u syncuser -H python /usr/src/app/wrapper.py --target=${TARGET_DIR} --remove-orphan
else
  echo "Starting sync without removing orphans"
  exec sudo -E -u syncuser -H python /usr/src/app/wrapper.py --target=${TARGET_DIR}
fi
