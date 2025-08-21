#!/usr/bin/env bash

source ./migenv/bin/activate

# the argument should be specified as just a testfile or 
# whatever semantics unittest uses
# i.e. "test_cleaner.py" instead of "tests/test_cleaner.py"
testfile="$1"

tests=$PWD/tests

cd "$tests" || return

sudo $tests/start-it.sh

cd ".."

if [ -z "${PYTHONPATH}" ];
  then
	echo 1;
    srcPythonPath=$PWD/src
  else
	echo 1;
    srcPythonPath=$PWD/src:$PYTHONPATH
fi
export PYTHONPATH=$srcPythonPath

testsPythonPath=$tests:$PYTHONPATH
export PYTHONPATH=$testsPythonPath

cd "$tests" || return

if [ -z "$testfile" ];
	then
		# python -m unittest discover -s "$tests" -t "$tests"
		pytest $tests
	else
		# python -m unittest $testfile
		pytest $tests/$testfile -v
fi

sudo $tests/stop-it.sh

exit 0
