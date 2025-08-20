module sort_32x8b_bitonic_l2(
    input [255:0] data_in,
    output [255:0] data_out
);

// Bitonic sorting network implementation
genvar i, j, k;
wire [7:0] level0[0:0];
assign level0[0] = data_in[7:0];
wire [7:0] level0[1:0];
assign level0[1] = data_in[15:8];
wire [7:0] level0[2:0];
assign level0[2] = data_in[23:16];
wire [7:0] level0[3:0];
assign level0[3] = data_in[31:24];
wire [7:0] level0[4:0];
assign level0[4] = data_in[39:32];
wire [7:0] level0[5:0];
assign level0[5] = data_in[47:40];
wire [7:0] level0[6:0];
assign level0[6] = data_in[55:48];
wire [7:0] level0[7:0];
assign level0[7] = data_in[63:56];
wire [7:0] level0[8:0];
assign level0[8] = data_in[71:64];
wire [7:0] level0[9:0];
assign level0[9] = data_in[79:72];
wire [7:0] level0[10:0];
assign level0[10] = data_in[87:80];
wire [7:0] level0[11:0];
assign level0[11] = data_in[95:88];
wire [7:0] level0[12:0];
assign level0[12] = data_in[103:96];
wire [7:0] level0[13:0];
assign level0[13] = data_in[111:104];
wire [7:0] level0[14:0];
assign level0[14] = data_in[119:112];
wire [7:0] level0[15:0];
assign level0[15] = data_in[127:120];
wire [7:0] level0[16:0];
assign level0[16] = data_in[135:128];
wire [7:0] level0[17:0];
assign level0[17] = data_in[143:136];
wire [7:0] level0[18:0];
assign level0[18] = data_in[151:144];
wire [7:0] level0[19:0];
assign level0[19] = data_in[159:152];
wire [7:0] level0[20:0];
assign level0[20] = data_in[167:160];
wire [7:0] level0[21:0];
assign level0[21] = data_in[175:168];
wire [7:0] level0[22:0];
assign level0[22] = data_in[183:176];
wire [7:0] level0[23:0];
assign level0[23] = data_in[191:184];
wire [7:0] level0[24:0];
assign level0[24] = data_in[199:192];
wire [7:0] level0[25:0];
assign level0[25] = data_in[207:200];
wire [7:0] level0[26:0];
assign level0[26] = data_in[215:208];
wire [7:0] level0[27:0];
assign level0[27] = data_in[223:216];
wire [7:0] level0[28:0];
assign level0[28] = data_in[231:224];
wire [7:0] level0[29:0];
assign level0[29] = data_in[239:232];
wire [7:0] level0[30:0];
assign level0[30] = data_in[247:240];
wire [7:0] level0[31:0];
assign level0[31] = data_in[255:248];


// Bitonic sorting stages for 32 elements
wire [7:0] level1[0:31];
assign {level1[1], level1[0]} = (level0[0] > level0[1]) ? {level0[0], level0[1]} : {level0[1], level0[0]};
assign {level1[3], level1[2]} = (level0[2] > level0[3]) ? {level0[2], level0[3]} : {level0[3], level0[2]};
assign {level1[5], level1[4]} = (level0[4] > level0[5]) ? {level0[4], level0[5]} : {level0[5], level0[4]};
assign {level1[7], level1[6]} = (level0[6] > level0[7]) ? {level0[6], level0[7]} : {level0[7], level0[6]};
assign {level1[9], level1[8]} = (level0[8] > level0[9]) ? {level0[8], level0[9]} : {level0[9], level0[8]};
assign {level1[11], level1[10]} = (level0[10] > level0[11]) ? {level0[10], level0[11]} : {level0[11], level0[10]};
assign {level1[13], level1[12]} = (level0[12] > level0[13]) ? {level0[12], level0[13]} : {level0[13], level0[12]};
assign {level1[15], level1[14]} = (level0[14] > level0[15]) ? {level0[14], level0[15]} : {level0[15], level0[14]};
assign {level1[17], level1[16]} = (level0[16] > level0[17]) ? {level0[16], level0[17]} : {level0[17], level0[16]};
assign {level1[19], level1[18]} = (level0[18] > level0[19]) ? {level0[18], level0[19]} : {level0[19], level0[18]};
assign {level1[21], level1[20]} = (level0[20] > level0[21]) ? {level0[20], level0[21]} : {level0[21], level0[20]};
assign {level1[23], level1[22]} = (level0[22] > level0[23]) ? {level0[22], level0[23]} : {level0[23], level0[22]};
assign {level1[25], level1[24]} = (level0[24] > level0[25]) ? {level0[24], level0[25]} : {level0[25], level0[24]};
assign {level1[27], level1[26]} = (level0[26] > level0[27]) ? {level0[26], level0[27]} : {level0[27], level0[26]};
assign {level1[29], level1[28]} = (level0[28] > level0[29]) ? {level0[28], level0[29]} : {level0[29], level0[28]};
assign {level1[31], level1[30]} = (level0[30] > level0[31]) ? {level0[30], level0[31]} : {level0[31], level0[30]};

// Additional stages for 32-element bitonic sort
wire [7:0] level2[0:31];
wire [7:0] level3[0:31];
wire [7:0] level4[0:31];
wire [7:0] level5[0:31];

// Level 2: 4-element bitonic merges
genvar i;
generate
    for (i = 0; i < 8; i = i + 1) begin : level2_gen
        assign {level2[4*i+3], level2[4*i+2], level2[4*i+1], level2[4*i]} = 
            (level1[4*i] > level1[4*i+2]) ? 
            {level1[4*i], level1[4*i+1], level1[4*i+2], level1[4*i+3]} : 
            {level1[4*i+2], level1[4*i+3], level1[4*i], level1[4*i+1]};
    end
endgenerate

// Level 3: 8-element bitonic merges
generate
    for (i = 0; i < 4; i = i + 1) begin : level3_gen
        assign {level3[8*i+7], level3[8*i+6], level3[8*i+5], level3[8*i+4], 
                level3[8*i+3], level3[8*i+2], level3[8*i+1], level3[8*i]} = 
            (level2[8*i] > level2[8*i+4]) ? 
            {level2[8*i], level2[8*i+1], level2[8*i+2], level2[8*i+3], 
             level2[8*i+4], level2[8*i+5], level2[8*i+6], level2[8*i+7]} : 
            {level2[8*i+4], level2[8*i+5], level2[8*i+6], level2[8*i+7], 
             level2[8*i], level2[8*i+1], level2[8*i+2], level2[8*i+3]};
    end
endgenerate

// Level 4: 16-element bitonic merges
generate
    for (i = 0; i < 2; i = i + 1) begin : level4_gen
        assign {level4[16*i+15], level4[16*i+14], level4[16*i+13], level4[16*i+12], 
                level4[16*i+11], level4[16*i+10], level4[16*i+9], level4[16*i+8], 
                level4[16*i+7], level4[16*i+6], level4[16*i+5], level4[16*i+4], 
                level4[16*i+3], level4[16*i+2], level4[16*i+1], level4[16*i]} = 
            (level3[16*i] > level3[16*i+8]) ? 
            {level3[16*i], level3[16*i+1], level3[16*i+2], level3[16*i+3], 
             level3[16*i+4], level3[16*i+5], level3[16*i+6], level3[16*i+7], 
             level3[16*i+8], level3[16*i+9], level3[16*i+10], level3[16*i+11], 
             level3[16*i+12], level3[16*i+13], level3[16*i+14], level3[16*i+15]} : 
            {level3[16*i+8], level3[16*i+9], level3[16*i+10], level3[16*i+11], 
             level3[16*i+12], level3[16*i+13], level3[16*i+14], level3[16*i+15], 
             level3[16*i], level3[16*i+1], level3[16*i+2], level3[16*i+3], 
             level3[16*i+4], level3[16*i+5], level3[16*i+6], level3[16*i+7]};
    end
endgenerate

// Level 5: 32-element bitonic merge
assign {level5[31], level5[30], level5[29], level5[28], level5[27], level5[26], level5[25], level5[24], 
        level5[23], level5[22], level5[21], level5[20], level5[19], level5[18], level5[17], level5[16], 
        level5[15], level5[14], level5[13], level5[12], level5[11], level5[10], level5[9], level5[8], 
        level5[7], level5[6], level5[5], level5[4], level5[3], level5[2], level5[1], level5[0]} = 
    (level4[0] > level4[16]) ? 
    {level4[0], level4[1], level4[2], level4[3], level4[4], level4[5], level4[6], level4[7], 
     level4[8], level4[9], level4[10], level4[11], level4[12], level4[13], level4[14], level4[15], 
     level4[16], level4[17], level4[18], level4[19], level4[20], level4[21], level4[22], level4[23], 
     level4[24], level4[25], level4[26], level4[27], level4[28], level4[29], level4[30], level4[31]} : 
    {level4[16], level4[17], level4[18], level4[19], level4[20], level4[21], level4[22], level4[23], 
     level4[24], level4[25], level4[26], level4[27], level4[28], level4[29], level4[30], level4[31], 
     level4[0], level4[1], level4[2], level4[3], level4[4], level4[5], level4[6], level4[7], 
     level4[8], level4[9], level4[10], level4[11], level4[12], level4[13], level4[14], level4[15]};

// Output assignment
assign data_out = {level5[31], level5[30], level5[29], level5[28], level5[27], level5[26], level5[25], level5[24], 
                   level5[23], level5[22], level5[21], level5[20], level5[19], level5[18], level5[17], level5[16], 
                   level5[15], level5[14], level5[13], level5[12], level5[11], level5[10], level5[9], level5[8], 
                   level5[7], level5[6], level5[5], level5[4], level5[3], level5[2], level5[1], level5[0]};
endmodule