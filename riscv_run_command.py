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
    reg_vals = [0 for _ in range(len(regs_to_get))]

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

        reg_vals[i] = int(reg_val_str)

    return reg_vals


rigorous_mode = False
verbose_mode = False
minimal_mode = False


def run_by_line(current_test_base_path, *, riscv_sim: pex.pty_spawn) -> []:

    if riscv_sim.closed:
        raise ConnectionError('Simulator process is not running.')

    # MAIN EXECUTE LOOP #
    with open(current_test_base_path + '.s') as asm_file:
        asm_instrs = [l for l in (line.strip() for line in asm_file.readlines()) if l]
        pc = 0
        ic = 0

        print_reg_header()
        last_reg_vals = [[(v, 0)] for v in get_reg_vals(riscv_sim=riscv_sim)]
        for i, reg in enumerate(last_reg_vals):
            print_reg(i, reg[-1][ic])
        print()
        print_pc(0)

        while pc / 4 < len(asm_instrs) and not asm_instrs[int(pc / 4)].startswith('ebreak'):
            print(asm_instrs[int(pc / 4)])
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

            else:
                affected_str = re.search('\s+(.*?),', asm_instrs[int(pc / 4)]).group(1)
                affected = REGISTER_MAPPINGS[affected_str]
                affected_new_val = get_reg_vals([affected], riscv_sim=riscv_sim)[0]
                print_reg(affected, affected_new_val)
                last_reg_vals[affected].append((affected_new_val, ic))

            new_pc_str = re.search('\(PC=(.+?)\)', riscv_sim.match.group(0).decode()).group(1)
            pc = int(new_pc_str, 16)
            ic += 1

            # Do additional stuff if user wants to or break
            if config_util_subloop(pc, riscv_sim):
                break

        return last_reg_vals


# HELPERS #
def config_util_subloop(pc: int, riscv_sim: pex.pty_spawn) -> bool:
    global rigorous_mode
    global verbose_mode
    global minimal_mode

    times_typed_exit = 0
    while True:
        print()
        print_pc(pc)
        next_action = input()
        if next_action == 'stop':
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

        elif next_action == 'help':
            options = [('<ENTER> , "s"', 'Step once.'),
                       ('"regdump"', 'Print all reg values.'),
                       ('"[!]rigorous"', 'Check all reg values for changes. WARNING: SLOW'),
                       ('"[!]verbose"', 'Print all reg values after each instruction (also enables rigorous).'),
                       ('"[!]minimal"', 'Reduce printed clutter.'),
                       ('"stop"', 'End test.'),
                       ('"quit"', 'Exit program.')]

            print('Options:')
            for option in options:
                print('\t%-20s: %s' % option)

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

        elif next_action == '':
            break

        else:
            print('Invalid command. Type "help" for help')


def print_pc(pc):
    global minimal_mode
    if minimal_mode:
        print(bcolors.OKGREEN + '> ' + bcolors.ENDC, end='')
    else:
        print(bcolors.OKGREEN + 'PC 0x%X > ' % pc + bcolors.ENDC, end='')


def print_reg_header():
    if not minimal_mode:
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
