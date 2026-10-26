// ============================================================
//  fifo.sv  --  CRAFT V&V unifying example #2 : synchronous FIFO
//  First-word fall-through (FWFT): rd_data shows the head whenever !empty.
//  Active-low reset. Used Weeks 4-8 and Project 1. Spec: dut/specs/fifo.md
//  Synthesizable; runs under Verilator 5.020 and Icarus.
// ============================================================
module fifo #(
    parameter int WIDTH = 8,
    parameter int DEPTH = 8
) (
    input  logic                    clk,
    input  logic                    rst_n,
    input  logic                    wr_en,
    input  logic [WIDTH-1:0]        wr_data,
    input  logic                    rd_en,
    output logic [WIDTH-1:0]        rd_data,
    output logic                    full,
    output logic                    empty,
    output logic [$clog2(DEPTH):0]  count
);
    localparam int ADDRW = $clog2(DEPTH);

    logic [WIDTH-1:0] mem [0:DEPTH-1];
    logic [ADDRW-1:0] wr_ptr, rd_ptr;
    logic [ADDRW:0]   cnt;

    assign full    = (cnt == DEPTH);
    assign empty   = (cnt == 0);
    assign count   = cnt;
    assign rd_data = mem[rd_ptr];               // FWFT: head visible when !empty

    logic do_wr, do_rd;
    assign do_wr = wr_en & ~full;
    assign do_rd = rd_en & ~empty;

    always_ff @(posedge clk) begin
        if (!rst_n) begin
            wr_ptr <= '0;
            rd_ptr <= '0;
            cnt    <= '0;
        end else begin
            if (do_wr) begin
                mem[wr_ptr] <= wr_data;
                wr_ptr      <= (wr_ptr == ADDRW'(DEPTH-1)) ? '0 : wr_ptr + 1'b1;
            end
            if (do_rd) begin
                rd_ptr <= (rd_ptr == ADDRW'(DEPTH-1)) ? '0 : rd_ptr + 1'b1;
            end
            case ({do_wr, do_rd})
                2'b10:   cnt <= cnt + 1'b1;      // write only
                2'b01:   cnt <= cnt - 1'b1;      // read only
                default: cnt <= cnt;             // idle, or simultaneous r+w
            endcase
        end
    end
endmodule
