import re
import pexpect as pex
import os

from rv_test.registers import REGISTER_TO_STR

RISCV_INPUT_HEADER = 'RISCV \(PC=0x.*\)> '
RISCV_REG_COUNT = 32


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

    for reg in regs_to_get:
        riscv_sim.sendline('readreg %d' % reg)
        riscv_sim.expect(RISCV_INPUT_HEADER)
        response = riscv_sim.before.decode()
        try:
            reg_index_str = re.search('R(.+?) =', response).group(1)
            reg_val_str = re.search('= (.+?)\n', response).group(1)

            assert reg_index_str == str(reg)

        except AttributeError:
            raise RuntimeError

        reg_vals[reg] = int(reg_val_str)

    return reg_vals


def run_by_line(current_test_base_path, *, riscv_sim: pex.pty_spawn) -> []:
    if riscv_sim.closed:
        raise ConnectionError('Simulator process is not running.')

    with open(current_test_base_path + '.expected.txt') as expected_reg_file:
        final_reg_vals = [0 for _ in range(RISCV_REG_COUNT)]
        for line in expected_reg_file:
            try:
                reg_index_str = re.search('R(.+?) =', line).group(1)
                reg_val_str = re.search('= (.+?)\n', line).group(1)
            except AttributeError:
                continue

            final_reg_vals[int(reg_index_str)] = int(reg_val_str)

    with open(current_test_base_path + '.s') as asm_file:
        asm_instrs = [l for l in (line.strip() for line in asm_file.readlines()) if l]
        last_reg_vals = [-1 for _ in range(RISCV_REG_COUNT)]
        pc = 0
        while pc / 4 < len(asm_instrs) and not asm_instrs[int(pc / 4)].startswith('ebreak'):
            print('PC=0x%x' % pc)
            print(asm_instrs[int(pc / 4)])
            riscv_sim.sendline('run %d 1' % pc)
            riscv_sim.expect(RISCV_INPUT_HEADER)
            new_pc_str = re.search('\(PC=(.+?)\)', riscv_sim.match.group(0).decode()).group(1)
            pc = int(new_pc_str, 16)
            new_reg_vals = get_reg_vals(riscv_sim=riscv_sim)
            changed = False
            for reg, new_val in enumerate(new_reg_vals):
                if last_reg_vals[reg] != new_val:
                    print('R%-2d %-6s = 0x%x   ' % (reg, '(' + REGISTER_TO_STR[reg] + ')', new_val))
                    changed = True
            if not changed:
                print('No registers changed')

            last_reg_vals = new_reg_vals
            print()
            if input('(Press ENTER to continue or type "quit" to stop) > ') == 'quit':
                break

        return last_reg_vals
