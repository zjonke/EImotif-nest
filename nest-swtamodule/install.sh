#!/bin/sh
#
# build module, install, and run tests:
#   - expecting $NEST_INSTALL_DIR to be set
#   - will create build directory 'build'
#   - will install in $NEST_INSTALL_DIR
#

modname="swtamodule"

set -xe

# ----------------------------------------------------------------------
# check environment

if [ -z "$NEST_INSTALL_DIR"] ; then
  set +xe
  echo "$0: error: \$NEST_INSTALL_DIR not set"
  exit 1
fi

# ----------------------------------------------------------------------
# setup directories

cd $(dirname $0)
build="build"

[ ! -d ${build} ] && mkdir ${build}

cd $build

# ----------------------------------------------------------------------
# configure

cmake -Dwith-nest=${NEST_INSTALL_DIR}/bin/nest-config -Dwith-python=3 ../

if [ $? -ne 0 ]; then
  set +xe
  echo "cmake failed, aborting."
  exit -1
fi

# ----------------------------------------------------------------------
# make
make -j $(nproc)

if [ $? -ne 0 ]; then
  set +xe
  echo "make failed, aborting."
  exit -1
fi

# ----------------------------------------------------------------------
# install

make install

if [ $? -ne 0 ]; then
  set +xe
  echo "make install failed, aborting."
  exit -1
fi

# ----------------------------------------------------------------------
# print how to use

set +xe

echo ""
echo "----------------------------------------------------------------------"
echo "installation ran successfully."
echo ""

echo "to import module, use:"
echo ""
echo "    nest.Install(\"${modname}\")"
echo ""
