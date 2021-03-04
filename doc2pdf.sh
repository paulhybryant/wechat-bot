#!/usr/bin/env bash

scp "$1" paulhybryant@vps:/tmp/
bname="$(basename $1)"
fname="${bname%.*}"
ssh paulhybryant@vps soffice --headless --convert-to pdf "/tmp/${bname}" --outdir /tmp
scp paulhybryant@vps:/tmp/${fname}.pdf /tmp
