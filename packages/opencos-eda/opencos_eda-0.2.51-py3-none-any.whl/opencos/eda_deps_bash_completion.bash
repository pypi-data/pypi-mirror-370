#!/usr/bin/env bash

# How to use?
# 1) copy this script locally and source it.
#    For example:
#    > source ~/sh/eda_deps_bash_completion.bash
#    You can put this in your .bashrc.
# 2) From you venv activate script:
#    (bottom of activate script, assuming python3.10):
#     script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
#     . $script_dir/../lib/python3.10/site-packages/opencos/eda_deps_bash_completion.bash


# scripts via pyproject.toml:
# what we want to add target completion to:
SCRIPT_NAME="eda"
# how we get the completion targets:
EXTRACTION_SCRIPT_NAME="eda_targets"

_eda_script_completion() {

    # Set up for additional completions
    local cur="${COMP_WORDS[COMP_CWORD]}"

    # If we have a DEPS markup file and the current word starts with a key indicator
    local completions=""
    local keys=""
    if [[ $(type -P "$EXTRACTION_SCRIPT_NAME") ]]; then
        keys=$("$EXTRACTION_SCRIPT_NAME" "$cur")
        if [[ -n "$keys" ]]; then
            completions=($(compgen -W "$keys" -- "$cur"))
        fi
    fi

    if [ -z "${completions}" ]; then
        # If we didn't find anything in a DEPS.[yml|yaml|toml|json], then use:
        # 1. a bunch of known eda words or args.
        eda_words="multi sim elab flist build synth waves proj waves targets \
                    +define+ +incdirs+ \
                    --help --quiet --verbose --debug \
                    --tool --seed --top --keep --force --fake --lint --work-dir \
                    --stop-before-compile --stop-after-compile --stop-before-elaborate \
                    --export --export-run --export-json \
                    "
        # 2. a glob the current word to mimic normal bash:
        completions=($(compgen -W "${eda_words}" -G "${cur}*" -- "$cur"))
    fi

    COMPREPLY=("${completions[@]}")
}


if [[ $(type -P "$EXTRACTION_SCRIPT_NAME") ]]; then
    complete -F _eda_script_completion "$SCRIPT_NAME"
fi
