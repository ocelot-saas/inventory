#!/bin/sh

python setup.py sdist
curl -s -F package=@dist/`ls dist` https://vsRAKKMwEs5p1RhfMGiF@push.fury.io/ocelot-saas/ > result
if [ -z "$(grep -e ok result)" ]
then
    rm result
    exit 1
fi
rm result
