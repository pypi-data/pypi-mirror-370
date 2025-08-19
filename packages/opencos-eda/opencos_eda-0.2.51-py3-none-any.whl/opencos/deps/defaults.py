''' opencos.deps.defaults -- pymodule for defaults referenced by other modules here'''


DEPS_FILE_EXTS = set([
    '.yml', '.yaml', '.toml', '.json',
    # Treat no extension DEPS as YAML.
    ''
])

ROOT_TABLE_KEYS_NOT_TARGETS = set([
    "DEFAULTS",
    "METADATA",
])

KNOWN_EDA_COMMANDS = set([
    "sim",
    "elab",
    "synth",
    "flist",
    "proj",
    "multi",
    "tools-multi",
    "sweep",
    "build",
    "waves",
    "upload",
    "open",
    "export",
])

SUPPORTED_TARGET_TABLE_KEYS = set([
    'args',
    'defines',
    'incdirs',
    'top',
    'deps',
    'reqs',
    'multi',
    'tags',
    'commands'] + list(KNOWN_EDA_COMMANDS))

SUPPORTED_DEP_KEYS_BY_TYPE = {
    dict: set(['commands']),
    str: set(['*']),
}

SUPPORTED_TAG_KEYS = set([
    'with-tools',
    'with-args',
    'args',
    'deps',
    'reqs',
    'defines',
    'incdirs',
    'replace-config-tools',
    'additive-config-tools',
])

SUPPORTED_COMMAND_KEYS = set([
    'shell',
    'work-dir-add-srcs', 'work-dir-add-sources',
    'peakrdl',
    'run-from-work-dir',     # default True
    'filepath-subst-target-dir', # default True
    'dirpath-subst-target-dir',  # default False
    'var-subst-args',
    'var-subst-os-env',
    'tee',
])
