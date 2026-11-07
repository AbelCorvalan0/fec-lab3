// The role of a UVM agent is to encapsulate the sequencer, driver and monitor into a single container.
// The sequencer is responsible for acting on a given sequence and send the driver with data objects.
// It is parameterized to accept objects of type seq_item and its seq_item_port is connected to the driver's seq_item_export.
class tb_agent extends uvm_agent;
    `uvm_component_utils(tb_agent)

    function new(string name="tb_agent", uvm_component parent=null);
        super.new(name, parent);
    endfunction

    uvm_sequencer#(seq_item)	sequencer;
    tb_driver                   driver;
    tb_monitor                  monitor;

    virtual function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        sequencer   = uvm_sequencer#(seq_item)::type_id::create("sequencer", this);
        driver      = tb_driver::type_id::create("driver", this);
        monitor     = tb_monitor::type_id::create("monitor", this);
    endfunction

    virtual function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        driver.seq_item_port.connect(sequencer.seq_item_export);
    endfunction

endclass