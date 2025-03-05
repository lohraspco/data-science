package sampleCodes;
import java.io.IOException;
import java.util.ArrayList;

import ilog.concert.*;
import ilog.cplex.*;
import inputOutput.DisplayData;
import inputOutput.InputDataReader;
import inputOutput.InputDataReader.InputDataReaderException;


public class TestCplex {

	public static void main(String[] args) {
		// TODO Auto-generated method stub

		double [] c;
		double [][] a;
		double [] b;
		double [] val;
		try {
			
			InputDataReader reader = new InputDataReader("sampleLP2.txt");
			c=reader.readDoubleArray();
			a=reader.readDoubleArrayArray();
			b=reader.readDoubleArray();
			ArrayList<String> s = reader.getParamName();
			DisplayData.printArraylist(s);
			IloCplex cplex = new IloCplex();
			IloNumVar [] x = cplex.numVarArray(c.length	, 0.0, Double.MAX_VALUE);
			
			IloLinearNumExpr obj = cplex.linearNumExpr();
			obj.addTerms(c, x);
			cplex.addMaximize(obj);
			IloLinearNumExpr [] cExpr = new IloLinearNumExpr [a.length];
			IloRange [] constraint = new IloRange [cExpr.length]; 
			for (int i=0; i<cExpr.length;i++){
				cExpr[i]= cplex.linearNumExpr();
				cExpr[i].addTerms(a[i], x);
				constraint[i]=cplex.addLe(cExpr[i], b[i]);
				
			}
			if(cplex.solve()){
				System.out.println(cplex.getObjValue());
				val=cplex.getValues(x);
				DisplayData.printArray(val);
			}
			
			
		} catch (IloException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();}
	catch (InputDataReaderException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
		// TODO Auto-generated catch block
		e.printStackTrace();
	}
		
		
	}

}
