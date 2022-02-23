package resilience;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;

import resilience.Config;

public class GenScenarioOfLengthK extends GenScenario {
	public double[] nextScen;

	// i scen number and j component number
	// it doesn't have time and we will add it later
	double[][] wholeScenarios;

	// index of subsets length
	// for example subsetLengthSet = {2,5} so
	// lengthCounter=0 -> subsetLengthSet=2
	// lengthCounter=1 -> subsetLengthSet=5
	int[] genMTTR;
	int[] lineMTTR;
	double absorption;
	double rapidRecovery;
	int setLen;
	public GenScenarioOfLengthK(int n, int nOfGens, int nOfLines, int T, int subsetLength) {
		super(n, nOfGens, nOfLines, T);

		int nn = this.numGens + this.numLines;
		List<Integer> superset = new ArrayList<Integer>();
		for (int i = 0; i < nn; i++)
			superset.add(i);
		this.setLen=subsetLength;
		this.itemCounter = 0;
		this.wholeScenarios = getSubsets(superset, subsetLength);
		this.numberOfScenarios=this.wholeScenarios.length;
	}

	public void setGenLineAdjustedValue(int[] genMttrAdjusted, int[] lineMttrAdjusted, double rapidRecovery) {
		this.rapidRecovery = rapidRecovery;
		this.genMTTR = genMttrAdjusted;
		this.lineMTTR = lineMttrAdjusted;

	}

	@Override
	public double[][] nextGenScen() {
		double[][] genScen = null;
		try {
			// nextScen contains both lines and generators scenarios
			nextScen = this.wholeScenarios[this.itemCounter++];
			this.scenarioCounter++;

			double[] gens = Arrays.copyOfRange(nextScen, 0, this.numGens);
			genScen = new double[gens.length][this.T];
			for (int i = 0; i < gens.length; i++) {
				for (int t = 0; t < this.T; t++)
					genScen[i][t] = 1;
				for (int t = 0; t < (this.genMTTR[i]); t++) {
					genScen[i][t] = gens[i];
				}

			}
		} catch (Exception e) {
			System.out.print("exception at genscen at iteration ");
			e.printStackTrace();
			// TODO: handle exception
		}
		return genScen;

	}

	@Override
	public double[][] nextLineScen() {
		double[] lines = Arrays.copyOfRange(this.nextScen, this.numGens, this.numGens + this.numLines);
		double[][] lineScen = new double[this.numLines][this.T];
		for (int i = 0; i < lines.length; i++) {
			for (int t = 0; t < this.T; t++)
				lineScen[i][t] = 1;
			for (int t = 0; t < this.lineMTTR[i]; t++) {
				lineScen[i][t] = lines[i];
			}
		}

		return lineScen;
	}

	private void getSubsets(List<Integer> superSet, int k, int idx, Set<Integer> current, List<Set<Integer>> solution) {
		// successful stop clause
		if (current.size() == k) {
			solution.add(new HashSet<Integer>(current));
			return;
		}
		// unseccessful stop clause
		if (idx == superSet.size())
			return;
		Integer x = superSet.get(idx);
		current.add(x);
		// "guess" x is in the subset
		getSubsets(superSet, k, idx + 1, current, solution);
		current.remove(x);
		// "guess" x is not in the subset
		getSubsets(superSet, k, idx + 1, current, solution);
	}

	private double[][] getSubsets(List<Integer> superSet, int k) {
		List<Set<Integer>> res = new ArrayList<Set<Integer>>();
		getSubsets(superSet, k, 0, new HashSet<Integer>(), res);

		int m = res.size();
		int n = superSet.size();
		double[][] results = new double[m][n];
		for (int i = 0; i < m; i++) {
			for (int j = 0; j < n; j++) {
				results[i][j] = 1;
			}
		}

		Iterator<Integer> it;
		for (int i = 0; i < m; i++) {
			it = res.get(i).iterator();
			while (it.hasNext()) {
				results[i][it.next()] = this.absorption;
			}
		}
		return results;
	}

	/***
	 * this function generates the elements of a power set one at a time
	 * 
	 * @return
	 */
	public String toString() {
		String nam = "," + this.absorption + "," + this.rapidRecovery + ","+this.setLen+",";
		for (int i = 0; i < nextScen.length; i++) {
			if (i == this.numGens)
				nam += "_";
			if (nextScen[i] == 1)
				nam += 1;
			else
				nam += 0;

		}
		nam += ",";
		return nam;
	}

	@Override
	public void setAbsorption(double d) {
		// absorption is used in the [][] getsubsets() function
		this.absorption = d;
	}


}
