// The main sequence that forms the stimulus and randomizer aspect of the testbench.
// The sequence when started on a sequencer gets the body method executed wich create/randomize seq_item objects and send them to the driver.
class tb_sequence extends uvm_sequence;
    `uvm_object_utils(tb_sequence)

    function new(string name="tb_sequence");
        super.new(name);
    endfunction

    // NUMBER OF TRANSACTION ITEMS FOR THE TEST
    int N_ITEMS = 1000;

    virtual task body();
        for (int i = 0; i < N_ITEMS; i++) begin
            seq_item item_s   = seq_item::type_id::create("item_s");
            start_item(item_s);
            item_s.randomize();

            `uvm_info("SEQ", $sformatf("Generate new item: "), UVM_DEBUG)
            // item_s.print();
            finish_item(item_s);
        end
        `uvm_info("SEQ", $sformatf("Done generation of %0d items", N_ITEMS), UVM_LOW)
    endtask

endclass