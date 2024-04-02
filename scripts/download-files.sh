#!/usr/bin/env bash
cd backend/run/
mkdir -p geoip
cd geoip
wget -O GeoLite2-City.mmdb "https://git.io/GeoLite2-City.mmdb"
wget -O GeoLite2-ASN.mmdb "https://git.io/GeoLite2-ASN.mmdb"
