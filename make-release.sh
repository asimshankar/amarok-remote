#!/bin/bash
# Script to make a release out of the contents of the current directory

PROGNAME=`basename $0`
DIR=`dirname $0`
RELEASE_NAME=""
DRYRUN=0
TMPDIR=""

[ "${DIR:0:1}" == "." ] && DIR="`pwd`/$DIR"

function usage {
  cat <<EOF
Usage: $PROGNAME [options]
Where [options] are the following:
  -r, --release_name=RELEASE   Create a tarball with this name
                               Defaults to the current date
  -n, --dryrun                 Print the commands that need to be executed to
                               create the release, but don't actually run them
  -t, --tmpdir=TMPDIR          Use TMPDIR for staging files. If not specified,
                               creates its own using 'mktemp -d'
  -h, --help                   Prints this message
EOF
}

function runcmd {
  cmd=$@
  if [ "$DRYRUN" -eq 1 ]
  then
    echo $cmd
    echo
  else
    $cmd
  fi
}

# Parse command-line options
opts=`getopt -a -o r:t:nh --long release_name:,tmpdir:,dryrun,help -n \
  $PROGNAME -- "$@"`
eval set -- "$opts"
while true
do
  case "$1" in
    -r|--release_name)  RELEASE_NAME="$2"; shift 2;;
    -t|--tmpdir)        TMPDIR="$2";       shift 2;;
    -n|--dryrun)        DRYRUN=1;          shift;;
    -h|--help)          usage;  exit 0;;
    --)                 shift;  break;;
    *)                  usage;  exit 1;;
  esac
done

# Set default values for things not specified in the command-line
[ -z "$RELEASE_NAME" ] && RELEASE_NAME=`date +"%Y%m%d"`
[ -z "$TMPDIR"       ] && TMPDIR=`mktemp -d`

[ $DRYRUN -eq 1 ] && cat <<EOF
==============================================================================
The following commands will be run to create the release:

mkdir -p $TMPDIR

EOF

runcmd cd $DIR
runcmd cd $TMPDIR
runcmd mkdir amarok-remote
runcmd cp -R "$DIR/*" amarok-remote/
runcmd cd amarok-remote
runcmd rm -rf .git tmp *.pyc
runcmd cd ..
runcmd tar -cvzf $HOME/amarok-remote-$RELEASE_NAME.tar.gz amarok-remote/
runcmd rm -rf amarok-remote

[ $DRYRUN -eq 1 ] && cat <<EOF
rm -rf $TMPDIR
==============================================================================
EOF

rm -rf $TMPDIR

[ $DRYRUN -eq 0 ] && \
  echo "Release placed in: $HOME/amarok-remote-$RELEASE_NAME.tar.gz"
