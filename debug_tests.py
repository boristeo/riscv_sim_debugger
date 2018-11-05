#!/usr/bin/env python3

import sys
import os
import pexpect as pex

from riscv_run_command import *
sys.path.insert(0, './rv_test')
from rv_test.generate import generate_files_from_directory
from rv_test.run_tests import run_test


def validate_test_file():
    pass


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('At this time the program accepts only one argument - the simulator executable')
        print('Usage: ./%s <path/to/executable>' % os.path.split(sys.argv[0])[-1])
        exit(1)

    riscv_sim_dir = sys.argv[1]

    tests_dir = 'rv_test/tests'
    generated_dir = 'generated'
    results_dir = 'results'

    generate_files_from_directory(tests_dir,
                                  generated_dir,
                                  results_dir,
                                  None,
                                  riscv_as='riscv64-unknown-elf-as',
                                  riscv_ld='riscv64-unknown-elf-ld',
                                  riscv_objcopy='riscv64-unknown-elf-objcopy')

    tests_passed, tests_failed = 0, 0
    tests = [
        "%s.%s" % match.group(1, 2)
        for match in [
            re.match(r'([^\.]+)\.(\d+(?:\.[^\.]+)?)\.script', filename)
            for filename in os.listdir(generated_dir)
        ]
        if match is not None
    ]
    tests.sort()

    while True:
        print()
        print('Available tests:')
        for i, test in enumerate(tests):
            sys.stdout = None
            test_passed = run_test(riscv_sim_dir)(test)
            sys.stdout = sys.__stdout__
            result_marker = bcolors.OKGREEN + 'ok' + bcolors.ENDC if test_passed else bcolors.FAIL + '!!' + bcolors.ENDC
            print('%2s %3d | %s' % (result_marker, i, test))
        print()

        test_to_run = -1

        while test_to_run < 0 or test_to_run > len(tests) - 1:
            try:
                test_to_run = int(input('Which test number to run? > '))
            except ValueError:
                print('Invalid choice. Try again.')

        current_test_base_path = os.path.join(generated_dir, tests[test_to_run])

        print('Running test: %s' % tests[test_to_run])
        with open(current_test_base_path + '.script') as file:
            with pex.spawn(riscv_sim_dir) as sim:
                print('SIMULATOR PID = %d' % sim.pid)
                loaded = False

                regs = []

                for command in file.readlines():
                    if command.startswith('run'):
                        loaded = True
                        print('### BEGIN PROGRAM EXECUTION ###', end='\n\n')
                        regs = run_by_line(current_test_base_path, riscv_sim=sim)
                        print()
                        print('### END PROGRAM EXECUTION ###')
                        print('Actual:')

                    elif not loaded:
                        print(command, end='')
                        run_sim_command(command, riscv_sim=sim)

                with open(current_test_base_path + '.expected.txt') as expected:
                    print('REG   EXPECTED           ACTUAL')
                    for line in expected.readlines():
                        reg = int(re.match('R([0-9]+?)\s*=\s*(.+?)$', line).group(1))
                        val = int(re.match('R([0-9]+?)\s*=\s*(.+?)$', line).group(2))
                        print('R%4d 0x%16X 0x%16X' % (reg, val, next(get_reg_vals([reg], riscv_sim=sim))))

        print('\n')
        input('PRESS ENTER TO CONTINUE')
