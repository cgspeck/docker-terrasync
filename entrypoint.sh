#! /bin/bash -e

if id syncuser ; then
  userdel syncuser
  groupdel syncuser
fi

groupadd -g $GID syncuser
useradd -l -u $UID -g syncuser syncuser
chown syncuser:syncuser $TARGET_DIR
chmod 755 $TARGET_DIR
chmod g+s $TARGET_DIR

exec sudo -u syncuser -H python /usr/src/app/vendor/terrasync.py --target=${TARGET_DIR} --quick
#exec sudo -u syncuser -H python -c "/usr/src/app/terrasync.py --target=${TARGET_DIR} --quick --remove-orphan"
