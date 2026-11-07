// The UVM monitor is derived from uvm_monitor and has a virtual interface handle to listen to activity on the given interface.
// It tries to capture pin level activity into a seq_item object which it can send out to other testbench components.
// Since it has to decode and capture any activity happening on the DUT interface, it has to run for as long as the simulation is active
// and hence it is placed inside a forever loop.
class tb_monitor extends uvm_monitor;
    `uvm_component_utils(tb_monitor)

    function new(string name="tb_monitor", uvm_component parent=null);
        super.new(name, parent);
    endfunction

    virtual dut_if                  vif;
    uvm_analysis_port#(seq_item)    mon_analysis_port;

    virtual function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        if (!uvm_config_db#(virtual dut_if)::get(this, "", "vif", vif))
            `uvm_fatal("MON", "Could not get vif")
            
        mon_analysis_port = new("mon_analysis_port", this);
    endfunction

    virtual task run_phase(uvm_phase phase);
        super.run_phase(phase);
        
        forever begin
            seq_item item = seq_item::type_id::create("item", this);

            @(posedge vif.i_clock);
            if (!vif.i_reset) begin
                if (vif.o_valid) begin
                    item.word         = vif.i_word;
                    item.codeword     = vif.o_codeword;
                    // item.print();
                    mon_analysis_port.write(item);
                end
            end
        end
    endtask

endclass