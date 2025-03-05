package sampleCodes;

import ilog.concert.IloException;
import ilog.concert.IloLinearNumExpr;
import ilog.concert.IloRange;

import java.util.logging.Level;
import java.util.logging.Logger;

public class Main {

	public static void main(String[] args) {
		Pair<String, Integer> p1 = new Main().new OrderedPair<String, Integer>("Even", 8);
		Pair<String, String>  p2 = new Main().new OrderedPair<String, String>("hello", "world");
		OrderedPair<String, Integer> aa = new Main().new OrderedPair<String, Integer>("ggg", 2);
	}

	public interface Pair<K, V> {
	    public K getKey();
	    public V getValue();
	}

	public class OrderedPair<K, V> implements Pair<K, V> {

	    private K key;
	    private V value;

	    public OrderedPair(K key, V value) {
		this.key = key;
		this.value = value;
	    }

	    public K getKey()	{ return key; }
	    public V getValue() { return value; }
	}
}
/*
private <T extends Number> T sum(T[] values){
	double temp=0;
	for (T t:values){
		temp += t.doubleValue();
	}
	return (T) temp;
}

private void loadBalanceConstraint() {
	
	try {
		for (int t = 0; t < nT; t++) {
			IloRange[] flowBalance = new IloRange[nB];
			for (int b = 0; b < nB; b++) {
				IloLinearNumExpr xprHelperFlow = cplex.linearNumExpr();
				
				// checks if the bus is a generation unit or not 
				// in the gen2bus wherever the bus is not a gu it is equal to -1 and 
				// where bus is gu the row number of unit is returned
				if (data.gen2bus[b] != -1){

					for (int j = 0; j < nGU; j++) {
						xprHelperFlow.addTerm(p[data.gen2bus[b]][j][t] ,1);
					}
				}
				xprHelperFlow.addTerm(-1, ls[b][t]);
				flowBalance[t] = cplex.addEq(xprHelperFlow, data.demandHourlyTotal[t],
						"PowerBalanceConstraint[" + b + "][" + t + "]");
				xprHelperFlow.clear();
			}
			constraints.add(flowBalance);
			
		}
;
	} catch (IloException ex) {
		Logger.getLogger(UnitCommitment.class.getName()).log(Level.SEVERE,
				null, ex);
	}

}
*/