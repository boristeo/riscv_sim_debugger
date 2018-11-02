import re
import pexpect as pex
import os

from rv_test.registers import REGISTER_TO_STR, REGISTER_MAPPINGS

RISCV_INPUT_HEADER = 'RISCV \(PC=0x.*\)> '
RISCV_REG_COUNT = 32


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def run_sim_command(command_to_exec: str, *, riscv_sim: pex.pty_spawn):
    if riscv_sim.closed:
        raise ConnectionError('Simulator process is not running.')

    riscv_sim.sendline(command_to_exec)

    riscv_sim.expect(RISCV_INPUT_HEADER)
    output = riscv_sim.before.decode()
    if len(output) != 0:
        output = output.split('\n', 1)[1]
    filtered = ''.join(filter(lambda x: not re.match(r'^\s*$', x), output.split()))

    return str(filtered)


def get_reg_vals(regs_to_get=[i for i in range(RISCV_REG_COUNT)], *, riscv_sim: pex.pty_spawn) -> []:
    for i, reg in enumerate(regs_to_get):
        riscv_sim.sendline('readreg %d' % reg)
        riscv_sim.expect(RISCV_INPUT_HEADER)
        response = riscv_sim.before.decode()
        try:
            reg_index_str = re.search('R([0-9]+?)\s*=', response).group(1)
            reg_val_str = re.search('=\s*(.+?)\n', response).group(1)

            assert reg_index_str == str(reg)

        except AttributeError:
            raise RuntimeError

        yield int(reg_val_str)


rigorous_mode = False
verbose_mode = False
minimal_mode = False
headers_on = True
runthrough_mode = False


def run_by_line(current_test_base_path, *, riscv_sim: pex.pty_spawn) -> []:
    global runthrough_mode

    if riscv_sim.closed:
        raise ConnectionError('Simulator process is not running.')

    # MAIN EXECUTE LOOP #
    with open(current_test_base_path + '.s') as asm_file:
        # Preload assembly to show alongside results
        asm_instrs = asm_file.readlines()
        i = 0
        while i < len(asm_instrs):
            asm_instrs[i] = asm_instrs[i].strip('\n')
            if asm_instrs[i] == '':
                asm_instrs.pop(i)
                continue
            if asm_instrs[i].endswith(':'):
                # This can and will fail if the label is at the last line
                # but that should never happen
                asm_instrs[i + 1] = asm_instrs[i + 1].strip('\n') + ' [' + asm_instrs[i].strip(':') + ']'
                asm_instrs.pop(i)
                continue
            i += 1

        pc = 0
        ic = 0
        last_reg_vals = []

        print_reg_header()

        for i, val in enumerate(get_reg_vals(riscv_sim=riscv_sim)):
            last_reg_vals.append([(val, ic)])
            print_reg(i, val)

        print()
        config_util_subloop(pc, riscv_sim, **{'show': 'help'})

        while pc / 4 < len(asm_instrs) and not asm_instrs[int(pc / 4)].startswith('ebreak'):

            # Do additional stuff if user wants to or break
            if not runthrough_mode:
                if config_util_subloop(pc, riscv_sim):
                    break

            instr_text = asm_instrs[int(pc / 4)]

            print(instr_text)
            riscv_sim.sendline('run %d 1' % pc)
            riscv_sim.expect(RISCV_INPUT_HEADER)

            print_reg_header()
            if rigorous_mode or verbose_mode:
                new_reg_vals = get_reg_vals(riscv_sim=riscv_sim)
                changed = False
                for reg, new_val in enumerate(new_reg_vals):
                    if verbose_mode:
                        if last_reg_vals[reg][-1][0] != new_val:
                            changed = True
                            print('* ', end='')
                        else:
                            print('  ', end='')
                        print_reg(reg, new_val)

                    elif last_reg_vals[reg][-1][0] != new_val:
                        changed = True
                        print_reg(reg, new_val)

                    last_reg_vals[reg].append((new_val, ic))

                if not changed:
                    print('No registers changed')

            elif not instr_text.startswith(('j ', 's', 'b')):
                    affected_str = re.search('\s+([a-z0-9]*?),', instr_text).group(1)
                    affected = REGISTER_MAPPINGS[affected_str]
                    affected_new_val = next(get_reg_vals([affected], riscv_sim=riscv_sim))
                    print_reg(affected, affected_new_val)
                    last_reg_vals[affected].append((affected_new_val, ic))

            new_pc_str = re.search('\(PC=(.+?)\)', riscv_sim.match.group(0).decode()).group(1)
            pc = int(new_pc_str, 16)
            ic += 1

        runthrough_mode = False
        return last_reg_vals


# HELPERS #
def config_util_subloop(pc: int, riscv_sim: pex.pty_spawn, **kwargs) -> bool:
    global rigorous_mode
    global verbose_mode
    global minimal_mode
    global runthrough_mode
    global headers_on

    times_typed_exit = 0
    while True:
        print()

        if 'show' not in kwargs:
            print_pc(pc)
            next_action = input()
        else:
            next_action = kwargs['show']

        if next_action == 'stop' or next_action == 'skip':
            return True

        elif next_action == 'quit':
            exit(0)

        elif next_action == 'exit':
            times_typed_exit += 1
            if times_typed_exit < 3:
                print('No, this program uses "quit". Try again.')
                continue
            else:
                print('Fine.')
                exit(0)

        elif next_action == 'help' or next_action == 'h':
            options = [('<ENTER> , "s"', 'Step once.'),
                       ('"regdump"', 'Print all reg values.'),
                       ('"[!]rigorous"', 'Check all reg values for changes. WARNING: SLOW'),
                       ('"[!]verbose"', 'Print all reg values after each instruction (also enables rigorous).'),
                       ('"[!]minimal"', 'Reduce printed clutter.'),
                       ('"[!]headers"', 'Print [or not] register value headers.'),
                       ('"run"', 'Run through remaining portion of test, continue to next.'),
                       ('"stop", "skip"', 'End test, continue to next.'),
                       ('"help", "h"', 'Show this help message.'),
                       ('"quit"', 'Exit program.')]

            print('Options:')
            for option in options:
                print('\t%-20s: %s' % option)
            if 'show' in kwargs:
                break

        elif next_action == 'regdump':
            for i, reg in enumerate(get_reg_vals(riscv_sim=riscv_sim)):
                print_reg(i, reg)

        elif next_action == 'rigorous':
            rigorous_mode = True

        elif next_action == '!rigorous':
            rigorous_mode = False

        elif next_action == 'verbose':
            verbose_mode = True

        elif next_action == '!verbose':
            verbose_mode = False

        elif next_action == 'minimal':
            minimal_mode = True

        elif next_action == '!minimal':
            minimal_mode = False

        elif next_action == 'headers':
            headers_on = True

        elif next_action == '!headers':
            headers_on = False

        elif next_action == 'run':
            runthrough_mode = True
            break

        elif next_action == '' or next_action == 's':
            break

        else:
            print('Invalid command. Type "help" for help')


def print_pc(pc):
    if minimal_mode:
        print(bcolors.OKGREEN + '> ' + bcolors.ENDC, end='')
    else:
        print(bcolors.OKGREEN + 'PC 0x%X > ' % pc + bcolors.ENDC, end='')


def print_reg_header():
    if not minimal_mode and headers_on:
        if not verbose_mode:
            print('%-3s %-6s    %18s    %20s    %20s' % ('r#', 'name', 'hexadecimal', 'unsigned decimal', 'signed decimal'))
            print('___ ______    __________________    ____________________    ____________________')
        else:
            print('? %-3s %-6s    %18s    %20s    %20s' % ('r#', 'name', 'hexadecimal', 'unsigned decimal', 'signed decimal'))
            print('_ ___ ______    __________________    ____________________    ____________________')


def print_reg(reg, value):
    if not minimal_mode:
        print('R%-2d %-6s    0x%16X    %20d    %20d' %
              (reg,
               '(' + REGISTER_TO_STR[reg] + ')',
               value,
               value,
               value if value <= 0x7fffffffffffffff else -(value - 0x8000000000000000)))
    else:
        print('%-4s  0x%X' % (REGISTER_TO_STR[reg], value))
