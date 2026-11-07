package dpic_pkg;

    // class Encapsulate raw DPI-C declarations inside the interface block
    import "DPI-C" function void model_create();
    import "DPI-C" function int model_get_output(int word);
    import "DPI-C" function void model_cleanup();

    class dut_model;

        // Public API methods exposed to the UVM Environment
        function new();
            model_create();
        endfunction

        function int get_output(int word);
            return model_get_output(word);
        endfunction

        function void destroy();
            model_cleanup();
        endfunction
    endclass

endpackage

