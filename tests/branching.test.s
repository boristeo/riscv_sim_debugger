
test "jal x0" {{
    inputs  {{ t1 22 }}
    outputs {{ x0 0 t1 12 }}

    jal zero, l1
    addi t1, t1, 50
l1:
    addi t1, t1, -10
}}

test "j" {{
    inputs  {{ t1 22 }}
    outputs {{ t1 12 }}    

    j l1
    addi t1, t1, 50
l1:
    addi t1, t1, -10
}}

test "jal ra" {{
    inputs  {{ ra -1 t1 22 }}
    outputs {{ ra  4 t1 12 }}

    jal ra, l1
    addi t1, t1, 50
l1:
    addi t1, t1, -10
}}

test "beq" {{
    inputs  {{ a0 10 a1 10 a2 20 a3 -10 a4 -20 t1 101 t2 102 t3 103 t4 104 }}
    outputs {{ a0 10 a1 10 a2 20 t1 101 t2 22 t3 33 t4 44 }}

    beq a0, a1, l1
    addi t1, zero, 11
l1:
    beq a0, a2, l2
    addi t2, zero, 22
l2:
    beq a0, a2, l3
    addi t3, zero, 33
l3:
    beq a0, a2, l4
    addi t4, zero, 44
l4:
}}

test "bne" {{
    inputs  {{ a0 -10 a1 -10 a2 -20 a3 10 a4 20 t1 101 t2 102 t3 103 t4 104 }}
    outputs {{ a3 10 a4 20 t1 11 t2 102 t3 103 t4 104 }}

    bne a0, a1, l1
    addi t1, zero, 11
l1:
    bne a0, a2, l2
    addi t2, zero, 22
l2:
    bne a0, a2, l3
    addi t3, zero, 33
l3:
    bne a0, a2, l4
    addi t4, zero, 44
l4:
}}

test "bge 10 >= 12" {{
    inputs  {{ a0 10 a1 12 t1 1 }}
    outputs {{ a0 10 a1 12 t1 0 }}

    bge a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "bge 10 >= 10" {{
    inputs  {{ a0 10 a1 10 t1 1 }}
    outputs {{ a0 10 a1 10 t1 1 }}

    bge a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "bge 10 >= 9" {{
    inputs  {{ a0 10 a1 9 t1 1 }}
    outputs {{ a0 10 a1 9 t1 1 }}

    bge a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "bge 10 >= -10" {{
    inputs  {{ a0 10 a1 -10 t1 1 }}
    outputs {{ a0 10 t1 1 }}

    bge a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "bge 10 >= -9" {{
    inputs  {{ a0 10 a1 -9 t1 1 }}
    outputs {{ a0 10 t1 1 }}

    bge a0, a1, l1
    addi t1, zero, 0
l1:
}}


test "bgeu 10 >= 12" {{
    inputs  {{ a0 10 a1 12 t1 1 }}
    outputs {{ a0 10 a1 12 t1 0 }}

    bgeu a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "bgeu 10 >= 10" {{
    inputs  {{ a0 10 a1 10 t1 1 }}
    outputs {{ a0 10 a1 10 t1 1 }}

    bgeu a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "bgeu 10 >= 9" {{
    inputs  {{ a0 10 a1 9 t1 1 }}
    outputs {{ a0 10 a1 9 t1 1 }}

    bgeu a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "bgeu -10 >= -10" {{
    inputs  {{ a0 -10 a1 -10 t1 1 }}
    outputs {{ t1 1 }}

    bgeu a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "bgeu -10 >= -9" {{
    inputs  {{ a0 -10 a1 -9 t1 1 }}
    outputs {{ t1 0 }}

    bgeu a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "blt 10 < 12" {{
    inputs  {{ a0 10 a1 12 t1 1 }}
    outputs {{ a0 10 a1 12 t1 1 }}

    blt a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "blt 10 < 10" {{
    inputs  {{ a0 10 a1 10 t1 1 }}
    outputs {{ a0 10 a1 10 t1 0 }}

    blt a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "blt 10 < 9" {{
    inputs  {{ a0 10 a1 9 t1 1 }}
    outputs {{ a0 10 a1 9 t1 0 }}

    blt a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "blt -10 < -10" {{
    inputs  {{ a0 -10 a1 -10 t1 1 }}
    outputs {{ t1 0 }}

    blt a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "blt -10 < -9" {{
    inputs  {{ a0 -10 a1 -9 t1 1 }}
    outputs {{ t1 1 }}

    blt a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "bltu 10 < 12" {{
    inputs  {{ a0 10 a1 12 t1 1 }}
    outputs {{ a0 10 a1 12 t1 1 }}

    bltu a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "bltu 10 < 10" {{
    inputs  {{ a0 10 a1 10 t1 1 }}
    outputs {{ a0 10 a1 10 t1 0 }}

    bltu a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "bltu 10 < 9" {{
    inputs  {{ a0 10 a1 9 t1 1 }}
    outputs {{ a0 10 a1 9 t1 0 }}

    bltu a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "bltu -10 < -10" {{
    inputs  {{ a0 -10 a1 -10 t1 1 }}
    outputs {{ t1 0 }}

    bltu a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "bltu -10 < -9" {{
    inputs  {{ a0 -10 a1 -9 t1 1 }}
    outputs {{ t1 1 }}

    bltu a0, a1, l1
    addi t1, zero, 0
l1:
}}

test "fib bgt" {{
    inputs  {{ s0 0 s1 1 s2 2 s3 3 s4 4 s5 5 }}
    outputs {{ s0 0 s1 1 s2 1 s3 2 s4 3 s5 5 }}

    add a0, s0, zero
    call fib
    add s0, a0, zero

    add a0, s1, zero
    call fib
    add s1, a0, zero

    add a0, s2, zero
    call fib
    add s2, a0, zero

    add a0, s3, zero
    call fib
    add s3, a0, zero

    add a0, s4, zero
    call fib
    add s4, a0, zero

    add a0, s5, zero
    call fib
    add s5, a0, zero

    beq zero, zero, end
fib:
    addi t0, zero, 0
    addi t1, zero, 1
    bge zero, a0, fib_end
loop:
    add t2, t1, t0
    add t0, t1, zero
    add t1, t2, zero
    addi a0, a0, -1
    bgt a0, zero, loop
fib_end:
    add a0, t0, zero
    ret
end:
}}

