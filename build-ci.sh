#!/usr/bin/sh

if [ -n "${WORKSPACE:+1}" ]; then
    # Path to virtualenv cmd installed by pip
    # /usr/local/bin/virtualenv
    PATH=$WORKSPACE/venv/bin:/usr/local/bin:$PATH
    if [ ! -d "venv" ]; then
            virtualenv venv
    fi
    . venv/bin/activate

fi

sh build.sh

docker-compose -f docker-compose-ci.yml up -d

python setup.py test