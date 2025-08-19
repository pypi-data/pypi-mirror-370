#!/bin/bash
this="${BASH_SOURCE[0]:-$0}"
top="$(dirname ${this})/.."

mod_name="py-encase"
mod_path="py_encase"
mng_name="mng_encase"
mng_opt="--manage"

dest="${dest:-${TMPDIR:-${HOME}/tmp}/test_${mod_path}}"

export PYTHON="${PYTHON:-python3.13}" PYTHON3="${PYTHON3:-python3.13}"
export PIP="${PIP:-pip-3.13}"         PIP3="${PIP3:-pip-3.13}"

src="${top%/}/src/${mod_path}/${mod_path}.py"

if [ -d "${dest}" ]; then
    echo rm -rf "${dest}"
    rm -rf "${dest}"
fi

if [ "x${1}" == 'xclean' ]; then
    exit
fi

"${src}" "${mng_opt}" init --prefix="${dest}" -g -r -v -m pytz -m tzlocal -S trial1.py

"${dest}"/bin/trial1 -d
"${dest}"/bin/"${mng_name}" add    -v -r trial2
"${dest}"/bin/"${mng_name}" addlib -v -r trial3

echo "Test output under: ${dest}"
