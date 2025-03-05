package resilience;

public abstract class GenScenario {
	public int numberOfScenarios = 0;
	public int numGens = 0;
	public int numLines = 0;
	public int T = 0;
	int scenarioCounter; // for total scenario cases
	int itemCounter; // items within each subsetLengthSet

	public GenScenario(int numberOfScenarios, int numG, int numL, int T) {
		this.numberOfScenarios = numberOfScenarios;
		this.numGens = numG;
		this.numLines = numL;
		this.T = T;
	}

	public abstract double[][] nextGenScen();

	public abstract double[][] nextLineScen();

	public abstract void setGenLineAdjustedValue(int[] genMttrAdjusted,
			int[] lineMttrAdjusted, double rapidRecovery);

	public abstract void setAbsorption(double d);

	public void resetCounter() {
		this.scenarioCounter = 0;
		this.itemCounter=0;

	}

}
