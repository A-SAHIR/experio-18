#!/bin/bash

echo "**exp-cognitive**:"
if [ -z "${TAG}" ]; then
  cd exp-cognitive && git log $(git describe --tags --abbrev=0)..HEAD --oneline | grep -E "EXP15|HT" | sed 's/^/- /' && cd ..
else
  cd exp-cognitive && git log $(git describe --tags --abbrev=0 $TAG^)..HEAD --oneline | grep -E "EXP15|HT" | sed 's/^/- /' && cd ..
fi
echo "**exp-accounting**:"
if [ -z "${TAG}" ]; then
  cd exp-accounting && git log $(git describe --tags --abbrev=0)..HEAD --oneline | grep -E "EXP15|HT" | sed 's/^/- /' && cd ..
else
  cd exp-accounting && git log $(git describe --tags --abbrev=0 $TAG^)..HEAD --oneline | grep -E "EXP15|HT" | sed 's/^/- /' && cd ..
fi
echo "**exp-base**:"
if [ -z "${TAG}" ]; then
  cd exp-base && git log $(git describe --tags --abbrev=0)..HEAD --oneline | grep -E "EXP15|HT" | sed 's/^/- /' && cd ..
else
  cd exp-base && git log $(git describe --tags --abbrev=0 $TAG^)..HEAD --oneline | grep -E "EXP15|HT" | sed 's/^/- /' && cd ..
fi
echo "**odoo**:"
if [ -z "${TAG}" ]; then
  cd odoo && git log $(git describe --tags --abbrev=0)..HEAD --oneline | grep -E "EXP15|HT" | sed 's/^/- /' && cd ..
else
  cd odoo && git log $(git describe --tags --abbrev=0 $TAG^)..HEAD --oneline | grep -E "EXP15|HT" | sed 's/^/- /' && cd ..
fi

