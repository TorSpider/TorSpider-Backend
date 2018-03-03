#!/bin/sh
echo "Letsencrypt renewal hook running..."
echo "RENEWED_DOMAINS=$RENEWED_DOMAINS"
echo "RENEWED_LINEAGE=$RENEWED_LINEAGE"

cat $RENEWED_LINEAGE/privkey.pem > /etc/nginx/certs/torspider/backend-key.pem
chown REPLACE_THE_USER: /etc/nginx/certs/torspider/backend-key.pem
cat $RENEWED_LINEAGE/fullchain.pem > /etc/nginx/certs/torspider/backend.pem
chown REPLACE_THE_USER: /etc/nginx/certs/torspider/backend.pem
systemctl restart torspider-backend
echo "TorSpider Backend key and cert chain updated and restarted"