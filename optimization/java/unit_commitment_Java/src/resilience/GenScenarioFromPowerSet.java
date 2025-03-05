package resilience;

import java.util.Arrays;

public class GenScenarioFromPowerSet extends GenScenario {

	public int subsetCounter;
	public double[] nextScen;

	public GenScenarioFromPowerSet(int nOfGens, int nOfLines, int T, int nInv) {
		super(1 << (nOfGens + nOfLines) , nOfGens, nOfLines, T);
		// TODO Auto-generated constructor stub
	}

	@Override
	public double[][] nextGenScen() {

		// nextScen contains both lines and generators scenarios

		nextScen = powerSubsetGenerator();

		double[] gens = Arrays.copyOfRange(nextScen, 0, this.numGens);
		double[][] genScen = new double[gens.length][this.T];
		for (int i = 0; i < gens.length; i++) {
			for (int t = 0; t < this.T; t++) {
				genScen[i][t] = gens[i];
			}
		}
		return genScen;
	}

	@Override
	public double[][] nextLineScen() {
		double[] lines = Arrays.copyOfRange(this.nextScen, this.numGens,
				this.numGens + this.numLines);
		double[][] lineScen = new double[this.numLines][this.T];
		for (int i = 0; i < lines.length; i++) {
			for (int t = 0; t < this.T; t++) {
				lineScen[i][t] = lines[i];
			}
		}

		return lineScen;
	}

	/***
	 * this function generates the elements of a power set one at a time
	 * 
	 * @return
	 */
	public double[] powerSubsetGenerator() {
		int n = this.numGens + this.numLines;
		double[] subset = new double[n];
		for (int bit = 0; bit < n; bit++) {
			subset[bit] = 1;
			// (1<<bit) is a number with jth bit 1. so when we & them with the
			// subset number we get which numbers are present in the subset
			int mask = 1 << bit;
			if ((this.subsetCounter & mask) != 0)
				subset[bit] = 0;
		}
		this.subsetCounter++;
		return subset;

	}

	public String toString() {
		String nam = "";
		for (int i = 0; i < nextScen.length; i++) {
			if (i == this.numGens)
				nam += "_";
			if (nextScen[i] == 1)
				nam += 1;
			else
				nam += 0;

		}
		return nam;
	}

	@Override
	public void setGenLineAdjustedValue(int[] genMttrAdjusted,
			int[] lineMttrAdjusted, double rapidR) {
		// TODO Auto-generated method stub

	}

	@Override
	public void setAbsorption(double d) {
		// TODO Auto-generated method stub

	}
}
