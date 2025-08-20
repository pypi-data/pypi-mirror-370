#!/bin/bash
set -e

BOOK=../book/docs
if [ -d $BOOK ] ; then
  echo "Updating shared docs from $BOOK ..."
  cp -au $BOOK/shared docs/
  cp -au $BOOK/copyright.rst docs/
fi
