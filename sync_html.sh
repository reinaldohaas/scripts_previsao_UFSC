#!/bin/bash

# Variáveis
LOCAL_DIR="/var/www/html/"
REMOTE_DIR="/public_html"
SFTP_HOST="nfs.sites.ufsc.br"
SFTP_PORT=2200
USER="tempo"
PASS="Rtzof3uK"

# Comando de sincronização com lftp
lftp -u "$USER","$PASS" -p $SFTP_PORT sftp://$SFTP_HOST <<EOF
mirror -R --delete --verbose $LOCAL_DIR $REMOTE_DIR
bye
EOF

