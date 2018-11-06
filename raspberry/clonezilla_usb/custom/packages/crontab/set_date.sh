#!/usr/bin/env bash
bifrost_date=$(ssh -XC -o "StrictHostKeyChecking=no" -o ConnectTimeout=15 -q gfx@10.219.106.111 'date +"%d %b %Y %H:%M:%S"') && sudo date --set="${bifrost_date}"

