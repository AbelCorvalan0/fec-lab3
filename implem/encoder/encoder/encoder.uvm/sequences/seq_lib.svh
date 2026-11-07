class word_count_sequence extends uvm_sequence;
    `uvm_object_utils(word_count_sequence)

    function new(string name="word_count_sequence");
        super.new(name);
    endfunction

    virtual task body();
        for (int i = 0; i < 2**NB_WORD; i++) begin
            seq_item item = seq_item::type_id::create("item");

            start_item(item);
            item.word = i;
            finish_item(item);
        end
    endtask
endclass

class bit_sweep_sequence extends uvm_sequence;
    `uvm_object_utils(bit_sweep_sequence)

    function new(string name="bit_sweep_sequence");
        super.new(name);
    endfunction

    virtual task body();
        for (int i = 0; i < NB_WORD; i++) begin
            seq_item item = seq_item::type_id::create("item");

            start_item(item);
            item.word = 1;
            item.word <<= i;
            finish_item(item);
        end
    endtask
endclass
