set positional-arguments

alias p := pre-commit
alias pa := pre-commit-all
alias t := test
alias b := bump

# pre-commit the current changes
pre-commit *ARGS:
    git add .
    pre-commit {{ARGS}}

# pre-commit all repo files
pre-commit-all:
    pre-commit run --all

# test all python versions and coverage the latest python version
test *ARGS:
    tox --parallel {{ARGS}}

# bump the version (major/minor/patch/alpha)
bump *ARGS:
    hatch version {{ARGS}}
