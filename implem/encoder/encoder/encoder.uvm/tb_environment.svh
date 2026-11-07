// The UVM environment is responsible for instantiating and connecting all testbench components (monitor-scoreboard, analysis ports).
class tb_environment extends uvm_env;
    `uvm_component_utils(tb_environment)

    function new(string name="tb_environment", uvm_component parent=null);
        super.new(name, parent);
    endfunction

    tb_agent        agent;
    tb_scoreboard   scoreboard;
    // tb_coverage     cov;

    virtual function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        agent       = tb_agent::type_id::create("agent", this);
        scoreboard  = tb_scoreboard::type_id::create("scoreboard", this);
        // cov         = tb_coverage::type_id::create("cov", this);
    endfunction

    virtual function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        agent.monitor.mon_analysis_port.connect(scoreboard.scb_analysis_imp);
        // agent.monitor.mon_analysis_port.connect(cov.analysis_export);
    endfunction

endclass