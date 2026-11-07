interface dut_if#()
(
    input   logic   i_clock
);
    logic   [tb_pkg::NB_CODEWORD    -1:0]   o_codeword  ;
    logic                                   o_valid     ;
    logic   [tb_pkg::NB_WORD        -1:0]   i_word      ;
    logic                                   i_valid     ;
    logic                                   i_reset     ;

endinterface