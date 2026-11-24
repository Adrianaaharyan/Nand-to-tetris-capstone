
// Nand2Tetris Capstone - Keyboard Controlled Box
// Roll Number: 2501730153
// K = 53
// Starting row = 53
// Height = 20 rows
// Width = 32 pixels = 2 words per row

(START)
    @KBD
    D=M
    @75
    D=D-A
    @BLACK
    D;JEQ

    @0
    D=A
    @FILL
    M=D
    @FILLBOX
    0;JMP

(BLACK)
    @0
    D=A
    D=D-1
    @FILL
    M=D

(FILLBOX)
    @18080
    D=A
    @PTR
    M=D

    @20
    D=A
    @ROWS
    M=D

(ROWLOOP)
    @2
    D=A
    @COLS
    M=D

(COLLOOP)
    @FILL
    D=M
    @PTR
    A=M
    M=D

    @PTR
    M=M+1

    @COLS
    M=M-1
    D=M
    @COLLOOP
    D;JGT

    // Move to the beginning of the next screen row.
    // Two words were written; add 30 to reach the next row.
    @PTR
    D=M
    @30
    D=D+A
    @PTR
    M=D

    @ROWS
    M=M-1
    D=M
    @ROWLOOP
    D;JGT

    @START
    0;JMP
