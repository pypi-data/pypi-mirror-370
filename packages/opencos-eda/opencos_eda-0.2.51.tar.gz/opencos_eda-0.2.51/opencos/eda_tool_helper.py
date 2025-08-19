''' opencos.eda_tool_helper -- used by pytests and other checks to see if tools are loaded

which helps determine if a pytest is runnable for a given tool, or should be skipped.
Does this without calling `eda` or eda.main(..)

Example uses:
    from opencos import eda_tool_helper
    cfg, tools_loaded = eda_tool_helper.get_config_and_tools_loaded()
    assert 'verilator' in tools_loaded

'''


from opencos import eda, eda_config, util

# Used by pytest, so we can skip tests if tools aren't present.

def get_config_and_tools_loaded( # pylint: disable=dangerous-default-value
        quiet: bool = False, args: list = []
) -> (dict, set):
    '''Returns config dict and set tools_loaded, given the found config.

    Can BYO args such as --config-yml=MY_OWN_EDA_CONFIG.yml
    '''

    # We have to figure out what tools are avaiable w/out calling eda.main,
    # so we can get some of these using eda_config.get_eda_config()
    config, _ = eda_config.get_eda_config(args=args, quiet=quiet)
    config = eda.init_config(config=config, quiet=quiet)
    tools_loaded = config.get('tools_loaded', set()).copy()
    return config, tools_loaded


def get_all_handler_commands(config=None, tools_loaded=None) -> dict:
    '''Given a config and tools_loaded (or if not supplied uses defaults) returns a dict

    of { <command>: [list of tools that run that command, in auto-tool-order] }.

    For example:
       { "sim": ["verilator", "vivado"],
         "elab": ["slang", "verilator", ...], ...
       }
    '''
    all_handler_commands = {}

    if config is None or tools_loaded is None:
        config, tools_loaded = get_config_and_tools_loaded()

    assert isinstance(config, dict)
    assert isinstance(tools_loaded, set)

    # Let's re-walk auto_tools_order to get this ordered per eda command:
    for tool, table in config.get('auto_tools_order', [{}])[0].items():
        if tool not in tools_loaded:
            continue

        if table.get('disable-tools-multi', False):
            # Flagged as do-not-add when running eda command: tools-multi
            util.debug(f'eda_tool_helper.py -- skipping {tool=} it is set with flag',
                       'disable-tools-multi in config')
            continue

        for command in table.get('handlers', {}).keys():
            if command not in all_handler_commands:
                # create ordered list from config.
                all_handler_commands[command] = list([tool])
            else:
                all_handler_commands[command].append(tool)

    return all_handler_commands
