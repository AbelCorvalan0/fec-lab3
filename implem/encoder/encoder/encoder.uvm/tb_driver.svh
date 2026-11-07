// The UVM driver extends from uvm_driver and is parameterized to accept an object of type seq_item.
// It also recieves handle to a virtual interface that is used to toggle pins of the DUT.
// The driver uses standard method calls get_next_item and item_done to communicate with its sequencer.
class tb_driver extends uvm_driver#(seq_item);
    `uvm_component_utils(tb_driver)

    function new(string name = "tb_driver", uvm_component parent=null);
        super.new(name, parent);
    endfunction

    virtual dut_if vif;

    virtual function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        if (!uvm_config_db#(virtual dut_if)::get(this, "", "vif", vif))
            `uvm_fatal("DRV", "Could not get vif")
    endfunction

    virtual task run_phase(uvm_phase phase);
        super.run_phase(phase);
        
        forever begin
            seq_item item;
    
            `uvm_info("DRV", $sformatf("Wait for item from sequencer"), UVM_DEBUG)
                
            seq_item_port.get_next_item(item);
            
            repeat (7) @(posedge vif.i_clock);
            vif.i_word  <= item.word;
            vif.i_valid <= 1;

            // item.print();

            seq_item_port.item_done();
        end
    endtask

endclass