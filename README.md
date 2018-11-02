RISC-V Simulator Debugger
=========================

## Installation
1. Somehow get ahold of the simulator.
This will be a challenge unless you are currently in my class since we are not allowed to share code.

2. Install riscv-tools: https://github.com/riscv/riscv-tools

   Or if you are using a mac like me: https://github.com/riscv/homebrew-riscv

3. Make sure you add the riscv gnu toolchain bin directory to PATH so that this program can call the assembler and other tools as needed.

   If you type `which riscv64-unknown-elf-as` into your terminal and it outputs a path, you're good.

4. Install Python 3 if you don't already have it.

5. Run

```
git clone https://github.com/boristeo/riscv_sim_debugger
```

6. Install any necessary packages. In theory I have a requirements file, but I suspect that there are a lot more packages necessary.

7. `chmod +x debug_tests.py` to allow execute.

And that should be it. If anyone actually tries this and finds issues, PLEASE tell me.
For every person who reports something as broken, ten others get frustrated and give up. I want people to actually try this out.

## Usage
At the moment, this program is slightly underdeveloped, so all you can do is pass in the path to your simulator executable and it will run any tests it finds in a `tests/` directory in your working directory.

```
./debug_tests.py ./path/to/simulator
```

Perfectly compatible with tests used by SeijiEmery in the rv-test project (https://github.com/seijiemery/rv-test). 
As a matter of fact, I literally use that project for the majority of what this program does at the moment.

## Features
* Step through execution in order, seeing what registers are changed in each instruction
* Dump all register values at any line in program execution
* Rigorous mode - verify that at most 1 register is being written to each cycle (off by default because it is SLOW)
* Verbose mode - All the same functionality of rigorous mode, but prints all 32 registers after each step

## Description
This is a work in progress (obviously), but the intent is to create a system for interactive debugging of the RISC-V simulator that I am currently working on as a project for my computer architecture course.

I was very excited to find that several of my classmates have built their own testing solutions for their groups. Here, I have adapted one that particularly stood out to me to be used for stepping through the simulator execution and finding errors as they occur.

The majority of what my program does is controlling the RISC-V simulator subprocess by effectively piping into stdin and reading stdout (I use the wonderful `pexpect` package for this). Unfortunately, this also makes my program run ridiculously slowly in some cases. This is good, because I don't have to worry too much about writing efficient code :)
