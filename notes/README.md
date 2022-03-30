under development

# Accuracy Metrics 

For the confusion matrix below
</br>
<table>
 
  <tr>
  <td></td>
    <td style='text-align:center' colspan="2">Forecasts</td>
  </tr>  
  <td rowspan="2">Actuals</td>
    <td>TP (True Positive)</td>
    <td>FN (False Negative)</td>
  </tr>
  <tr>
    <td>FP (False Positive)</td>
    <td>TN (True Negative)</td>
  </tr>
</table>

</br>
here are mostly used accuracy metrics: 

<table>
 
  <tr>
  <td>True Positive Rate, Sensitivity, Recall, Hit Rate</td>
<td>TPR = TP/P whre p = TP+FN </td>
  </tr>
  <tr>
<td>True Negative Rate, Specifity, Selectivity</td>
<td>TNR = TN/N = 1-FPR whre N=FP+TN </td>
 </tr>
  <tr>
<td> Positive Predictivity Value, precision/td>
<td>PPV = TP/(TP+FP) = 1-FDR</td>
 </tr>
  <tr>
<td> False Discovery Rate, Fall Out </td>
<td>FDR = FP/N</td>
 </tr>
  <tr>
<td> False Negative Rate, Miss Rate</td>
<td>FNR = FN/P</td>
 </tr>
  <tr>
<td> False Omission Rate</td>
<td>FOR = FN/(FN+TN)</td>
 </tr>
 <tr>
<td> Prevalence Threshold</td>
<td><img src="https://render.githubusercontent.com/render/math?math=\sqrt{\frac{TPR(1-TNR)-(1-TNR)}{TPR-(1-TNR)}}"></td>
 </tr>

  <tr>
<td> Accuracy</td>
<td>acc = (TP+TN)/(P+N)</td>
 </tr>
</table>
Coolest formula : <img src="https://render.githubusercontent.com/render/math?math=e^{i \pi} = -1">
