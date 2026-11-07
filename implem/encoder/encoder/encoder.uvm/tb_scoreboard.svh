// Import model logic from python
import dpic_pkg::*;
// import pysv::*;

class tb_scoreboard extends uvm_scoreboard;
    `uvm_component_utils(tb_scoreboard)

    function new(string name="tb_scoreboard", uvm_component parent=null);
        super.new(name, parent);
    endfunction

    dut_model                                   model;
    uvm_analysis_imp#(seq_item, tb_scoreboard)  scb_analysis_imp;

    virtual function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        model               = new();
        scb_analysis_imp    = new("scb_analysis_imp", this);
    endfunction
  
    virtual function void write(seq_item item);
        seq_item model_output = seq_item::type_id::create("model_output");

        model_output.word       = item.word;
        model_output.codeword   = model.get_output(item.word);

        `uvm_info(get_name(), $sformatf("\nFrom UVM: %015b = model.get_output(%05b)", model_output.codeword, item.word), UVM_NONE)
        item.print();
        model_output.print();

        if (!item.compare(model_output)) begin
            if (item.codeword != model_output.codeword)
                `uvm_error("CODEWORD ERROR", $sformatf( "\nword=%05b : DUT=%015b, esperado=%015b",
                                                        item.word, item.codeword, model_output.codeword))
        end
    endfunction

    virtual function void check_phase(uvm_phase phase);
        super.check_phase(phase);
        // Terminate Python runtime context cleanly
        model.destroy();
    endfunction

endclass
