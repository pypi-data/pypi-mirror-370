#!/bin/bash
export TBBROOT="/project/build/lib.linux-x86_64-cpython-39/gloria/stan_models/cmdstan-2.36.0/stan/lib/stan_math/lib/tbb_2020.3" #
tbb_bin="/project/build/lib.linux-x86_64-cpython-39/gloria/stan_models/cmdstan-2.36.0/stan/lib/stan_math/lib/tbb" #
if [ -z "$CPATH" ]; then #
    export CPATH="${TBBROOT}/include" #
else #
    export CPATH="${TBBROOT}/include:$CPATH" #
fi #
if [ -z "$LIBRARY_PATH" ]; then #
    export LIBRARY_PATH="${tbb_bin}" #
else #
    export LIBRARY_PATH="${tbb_bin}:$LIBRARY_PATH" #
fi #
if [ -z "$LD_LIBRARY_PATH" ]; then #
    export LD_LIBRARY_PATH="${tbb_bin}" #
else #
    export LD_LIBRARY_PATH="${tbb_bin}:$LD_LIBRARY_PATH" #
fi #
 #
