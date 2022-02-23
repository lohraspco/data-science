package resilience;

import java.io.File;

public class GenScenarioFromFile extends GenScenario {
	File[] genBrokenScenario;
	public GenScenarioFromFile(File[] genBrokenSce,int numGens, int numLine, int T) {
		super(genBrokenSce.length, numGens, numLine,T);
		this.genBrokenScenario = genBrokenSce;
	}

	public int counter = 0;

	@Override
	public double [][] nextGenScen() {
		double [][] gs = null;
		if (this.counter < this.numberOfScenarios) {
			SCUCDataReader dr = new SCUCDataReader();
			gs = dr.read2DMatrix(genBrokenScenario[this.counter]);
			
			this.counter++;
		}
		return gs;
	}
	
	public double  [][] nextLineScen(){
		double [][] lines = new double [this.numLines][this.T];
		for (int i=0;i<this.numLines;i++)
			for (int j=0;j<this.T;j++)
				lines[i][j]=1;
		return lines;
		
	}
	 public String toString() {
		 return genBrokenScenario[this.counter-1].getName();
	 }
	/***
	 * scenarios for operable and inoperable generators
	 * 
	 * @param folder
	 * @return list of files containing inoperable generator scenarios
	 *
	 *         this code can be run in two mode True: the first mode is where we
	 *         want to find the component importance using the anova and eta it uses
	 *         the power set generator for all nodes and lines
	 * 
	 *         False: second mode is where we want to use the scenario files
	 *         generated. it is just for lines
	 */



	@Override
	public void setGenLineAdjustedValue(int[] genMttrAdjusted,
			int[] lineMttrAdjusted, double rapidRecovery) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void setAbsorption(double d) {
		// TODO Auto-generated method stub
		
	}


	
	

}