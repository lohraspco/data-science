\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  z
Subject To
 flow_conservation[1]: f[s,1] - f[1,2] = 0
 flow_conservation[2]: f[s,2] + f[1,2] - f[2,t] = 0
 capacityConst[s,1]: f[s,1] - 2 x[s,1] <= 0
 capacityConst[s,2]: f[s,2] - 2 x[s,2] <= 0
 capacityConst[1,2]: f[1,2] - x[1,2] <= 0
 capacityConst[2,t]: f[2,t] - 2 x[2,t] <= 0
 capacityConst[s,1]: f[s,1] - x[s,1] >= 0
 capacityConst[s,2]: f[s,2] - x[s,2] >= 0
 capacityConst[1,2]: f[1,2] - x[1,2] >= 0
 capacityConst[2,t]: f[2,t] - x[2,t] >= 0
 R10: x[s,1] + x[s,2] + x[1,2] + x[2,t] = 2
 R11: f[s,1] + f[s,2] - z <= 0
Bounds
Binaries
 x[s,1] x[s,2] x[1,2] x[2,t]
End
