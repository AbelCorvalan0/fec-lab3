class tb_coverage extends uvm_subscriber#(seq_item);
    `uvm_component_utils(tb_coverage)

    // ADD COVERGROUP FOR CODE AND SEQUENCES
    // covergroup cov_dut;
    //     output_data : coverpoint c_item.output_data;
    //     flags : coverpoint c_item.flags {
    //         illegal_bins illegal_negative_zero = {4'b1xx1};
    //     }
    // endgroup

    // covergroup cov_sequences;
    //     A : coverpoint c_item.input_data[0];
    //     B : coverpoint c_item.input_data[1];
    //     opcode : coverpoint c_item.opcode;
    // endgroup

    function new(string name="tb_coverage", uvm_component parent=null);
        super.new(name, parent);
        cov_dut         = new();
        cov_sequences   = new();
    endfunction

    seq_item c_item;

    virtual function void write (seq_item item);
        c_item = item;
        cov_dut.sample();
        cov_sequences.sample();
    endfunction

    function void report_phase(uvm_phase phase);
        `uvm_info(get_name(), $sformatf("DUT Coverage = %.2f%%", cov_dut.get_inst_coverage()), UVM_NONE)
        `uvm_info(get_name(), $sformatf("Sequences Coverage = %.2f%%", cov_sequences.get_inst_coverage()), UVM_NONE)
    endfunction

endclass

// GENERATE REPORTS (from proj_dir)
// mkdir MODULE.coverage &&  xcrg -dir ./MODULE.sim/sim_1/behav/xsim/xsim.covdb -report_dir ./MODULE.coverage/func -cc_dir MODULE.sim/sim_1/behav/xsim/xsim.codeCov -cc_db tb_top_behav -cc_report ./MODULE.coverage/code

