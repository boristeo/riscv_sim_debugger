import sys
import os
import pexpect as pex

from riscv_run_command import *
sys.path.insert(0, './rv_test')
from rv_test.generate import generate_files_from_directory


def validate_test_file():
    pass


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('At this time the program accepts only one argument - the simulator executable')
        print('Usage: ./%s <path/to/executable>' % os.path.split(sys.argv[0])[-1])
        exit(1)

    riscv_sim_dir = sys.argv[1]

    tests_dir = 'tests'
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
    print("Found tests: '%s'" % tests)

    for test in tests:
        current_test_base_path = os.path.join(generated_dir, test)

        print('Running test: %s' % test)
        with open(current_test_base_path + '.script') as file:
            with pex.spawn(riscv_sim_dir) as sim:
                loaded = False

                for command in file.readlines():
                    if command.startswith('run'):
                        loaded = True
                        print('### BEGIN PROGRAM EXECUTION ###', end='\n\n')
                        run_by_line(current_test_base_path, riscv_sim=sim)
                        print('### END PROGRAM EXECUTION ###')

                    elif not loaded:
                        print(command, end='')
                        run_sim_command(command, riscv_sim=sim)

                    else:
                        print(run_sim_command(command, riscv_sim=sim))
