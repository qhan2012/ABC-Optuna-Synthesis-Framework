module sort_16x16b_bitonic_l3(
    input [255:0] data_in,
    output [255:0] data_out
);

// Bitonic sorting network implementation
genvar i, j, k;
wire [15:0] level0[0:0];
assign level0[0] = data_in[15:0];
wire [15:0] level0[1:0];
assign level0[1] = data_in[31:16];
wire [15:0] level0[2:0];
assign level0[2] = data_in[47:32];
wire [15:0] level0[3:0];
assign level0[3] = data_in[63:48];
wire [15:0] level0[4:0];
assign level0[4] = data_in[79:64];
wire [15:0] level0[5:0];
assign level0[5] = data_in[95:80];
wire [15:0] level0[6:0];
assign level0[6] = data_in[111:96];
wire [15:0] level0[7:0];
assign level0[7] = data_in[127:112];
wire [15:0] level0[8:0];
assign level0[8] = data_in[143:128];
wire [15:0] level0[9:0];
assign level0[9] = data_in[159:144];
wire [15:0] level0[10:0];
assign level0[10] = data_in[175:160];
wire [15:0] level0[11:0];
assign level0[11] = data_in[191:176];
wire [15:0] level0[12:0];
assign level0[12] = data_in[207:192];
wire [15:0] level0[13:0];
assign level0[13] = data_in[223:208];
wire [15:0] level0[14:0];
assign level0[14] = data_in[239:224];
wire [15:0] level0[15:0];
assign level0[15] = data_in[255:240];


// Bitonic sorting stages for 16 elements
wire [7:0] level1[0:15];
assign {level1[1], level1[0]} = (level0[0] > level0[1]) ? {level0[0], level0[1]} : {level0[1], level0[0]};
assign {level1[3], level1[2]} = (level0[2] > level0[3]) ? {level0[2], level0[3]} : {level0[3], level0[2]};
assign {level1[5], level1[4]} = (level0[4] > level0[5]) ? {level0[4], level0[5]} : {level0[5], level0[4]};
assign {level1[7], level1[6]} = (level0[6] > level0[7]) ? {level0[6], level0[7]} : {level0[7], level0[6]};
assign {level1[9], level1[8]} = (level0[8] > level0[9]) ? {level0[8], level0[9]} : {level0[9], level0[8]};
assign {level1[11], level1[10]} = (level0[10] > level0[11]) ? {level0[10], level0[11]} : {level0[11], level0[10]};
assign {level1[13], level1[12]} = (level0[12] > level0[13]) ? {level0[12], level0[13]} : {level0[13], level0[12]};
assign {level1[15], level1[14]} = (level0[14] > level0[15]) ? {level0[14], level0[15]} : {level0[15], level0[14]};

wire [7:0] level2[0:15];
assign {level2[3], level2[2], level2[1], level2[0]} = (level1[0] > level1[2]) ? 
    {level1[0], level1[1], level1[2], level1[3]} : {level1[2], level1[3], level1[0], level1[1]};
assign {level2[7], level2[6], level2[5], level2[4]} = (level1[4] > level1[6]) ? 
    {level1[4], level1[5], level1[6], level1[7]} : {level1[6], level1[7], level1[4], level1[5]};
assign {level2[11], level2[10], level2[9], level2[8]} = (level1[8] > level1[10]) ? 
    {level1[8], level1[9], level1[10], level1[11]} : {level1[10], level1[11], level1[8], level1[9]};
assign {level2[15], level2[14], level2[13], level2[12]} = (level1[12] > level1[14]) ? 
    {level1[12], level1[13], level1[14], level1[15]} : {level1[14], level1[15], level1[12], level1[13]};

wire [7:0] level3[0:15];
assign {level3[7], level3[6], level3[5], level3[4], level3[3], level3[2], level3[1], level3[0]} = 
    (level2[0] > level2[4]) ? 
    {level2[0], level2[1], level2[2], level2[3], level2[4], level2[5], level2[6], level2[7]} : 
    {level2[4], level2[5], level2[6], level2[7], level2[0], level2[1], level2[2], level2[3]};
assign {level3[15], level3[14], level3[13], level3[12], level3[11], level3[10], level3[9], level3[8]} = 
    (level2[8] > level2[12]) ? 
    {level2[8], level2[9], level2[10], level2[11], level2[12], level2[13], level2[14], level2[15]} : 
    {level2[12], level2[13], level2[14], level2[15], level2[8], level2[9], level2[10], level2[11]};

wire [7:0] level4[0:15];
assign {level4[15], level4[14], level4[13], level4[12], level4[11], level4[10], level4[9], level4[8], 
        level4[7], level4[6], level4[5], level4[4], level4[3], level4[2], level4[1], level4[0]} = 
    (level3[0] > level3[8]) ? 
    {level3[0], level3[1], level3[2], level3[3], level3[4], level3[5], level3[6], level3[7], 
     level3[8], level3[9], level3[10], level3[11], level3[12], level3[13], level3[14], level3[15]} : 
    {level3[8], level3[9], level3[10], level3[11], level3[12], level3[13], level3[14], level3[15], 
     level3[0], level3[1], level3[2], level3[3], level3[4], level3[5], level3[6], level3[7]};

// Output assignment
assign data_out = {level4[15], level4[14], level4[13], level4[12], level4[11], level4[10], level4[9], level4[8], 
                   level4[7], level4[6], level4[5], level4[4], level4[3], level4[2], level4[1], level4[0]};
endmodule