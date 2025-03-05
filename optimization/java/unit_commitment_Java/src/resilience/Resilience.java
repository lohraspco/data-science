package resilience;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FilenameFilter;
import java.io.IOException;
import java.lang.Character.Subset;
import java.util.ArrayList;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import inputOutput.WriteToFile;
import resilience.SCUCDataReader.Data;
import ilog.concert.IloException;
import ilog.cplex.IloCplex.UnknownObjectException;
import java.awt.*;

import javax.swing.JFrame;
import javax.swing.JPanel;
import resilience.Config;

public class Resilience extends JFrame {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	public static void main(String[] args) throws UnknownObjectException,
			IloException {

		if (Config.useMultiThread == true)
			usemultiThreadMethod();
		else
			System.out.println("not now");
		// useSingleThreadMethid();

	}

	private static void usemultiThreadMethod() {
		// ArrayList<Thread> threads = new ArrayList<Thread>();
		ArrayList<Runnable> runnableThread = new ArrayList<Runnable>();
		ExecutorService pool = Executors.newFixedThreadPool(8);
		long startTime = System.currentTimeMillis();

		int scounter = 0;
		for (String testCase : Config.cases) {
			// data that are fixed for all the scenarios
			Data data = new SCUCDataReader.Data(testCase);
			int nT = data.demandHourlyTotal.length;
			int nG = data.bus.length;
			int nL = data.line.length;

			// type 1 get scenarios from file
			// type 2 generate powerset. each subset shows the elements that are
			// inoperable
			// type 3 generate subsets of lenght k
			if (Config.subsetCardinality == null) {
				System.out.println("please take a look at the Config.java, information is missing: Config.subsetCardinality");
			} else {
				for (int setLen : Config.subsetCardinality) {
					GenScenario gens = getGenScen(testCase, nG, nL, nT, setLen,
							Config.scenarioSource.someSubsets,
							Config.investmentPool.length);

					GasScenario gas;

					// TextArea jta = gui();

					int genScenCounter = 0;

					int[] genMttrAdjusted = new int[data.genMttr.length];
					int[] lineMttrAdjusted = new int[data.lineMttr.length];

					int invCoun = 0;
					for (double[] inv : Config.investmentPool) {
						gens.resetCounter();
						System.out.println(invCoun++);
						// adjustment for 24 hours instead of 96 hours
						// hence squeeze the MTTR by 2.5
						double genAdjCoeff = 2.5;
						genMttrAdjusted = adjust(data.genMttr, 1 / genAdjCoeff
								* (1 - inv[0]), nT);
						lineMttrAdjusted = adjust(data.lineMttr, (1 - inv[0]),
								nT);

						gens.setGenLineAdjustedValue(genMttrAdjusted,
								lineMttrAdjusted, inv[0]);
						gens.setAbsorption(inv[1]);
						while (gens.scenarioCounter < gens.numberOfScenarios) {
							if (genScenCounter == 83)
								System.out.println("sdfadsf");
							double[][] ge = gens.nextGenScen();
							double[][] lineBrokenScenario = gens.nextLineScen();
							System.out.println(genScenCounter);
							gas = new GasScenario(testCase);
							while (gas.counter < gas.n) {

								// System.out.println("invR " + inv[0] +
								// "_invA " + inv[1] + "_genscentotal "
								// + gens.numberOfScenarios + "_scenCounter " +
								// genScenCounter);
								String s1 = gens.toString();
								System.out.println(s1);
								String[] IDs = {
										testCase,
										s1,
										" inv_ttr " + inv[0] + " inv_abs "
												+ inv[1] };
								double[][] gasB = gas.next();
								runnableThread
										.add(new UnitCommitmentMultiThread(IDs,
												data, ge, lineBrokenScenario,
												gasB, scounter));
								pool.execute(runnableThread.get(runnableThread
										.size() - 1));
								scounter++;

							}
							genScenCounter++;
						}
					}
				}
			}
		}
		long totalRunTime = System.currentTimeMillis() - startTime;
		WriteToFile.writeLog("number of threads : ");
		WriteToFile.writeLog("elapsed time : " + totalRunTime / 1000
				+ " seconds");

	}

	private static GenScenario getGenScen(String caseName, int nG, int nL,
			int nT, int setLen,
			Config.scenarioSource componentcenarioGeneratorType, int invScenLen) {
		File[] genFiles = getGenScenFiles(caseName);
		GenScenario gens;
		int totalScenarioCounts = 0;
		switch (componentcenarioGeneratorType) {
		case fromFile:
			gens = new GenScenarioFromFile(genFiles, nG, nL, nT);
			break;
		case powerSet:
			gens = new GenScenarioFromPowerSet(nG, nL, nT, invScenLen);
			break;
		case someSubsets:

			int n = nG + nL;

			int comb = setLen;
			if ((n - setLen) > comb)
				comb = n - setLen;
			for (int it1 = comb + 1, it2 = 2; it1 < n; it1++, it2++)
				comb *= it1 / it2;

			totalScenarioCounts = comb;

			// totalScenarioCounts *= invScenLen;
			gens = new GenScenarioOfLengthK(totalScenarioCounts, nG, nL, nT,
					setLen);
			break;

		default:
			gens = new GenScenarioFromFile(genFiles, nG, nL, nT);
			break;
		}
		return gens;
	}

	/***
	 * it is the improvement in the MTTR and also absorption 0 means no
	 * investment and .25% means investment with 25% of the worth of the
	 * component according to linear improvement to MTTR and absorption the
	 * absorption after .25% investment will be .25% the MTTR adjusted after
	 * recover will reduce to (1-.25%) MTTR
	 */
	private static int[] adjust(int[] genMttr, double adjCoeff, int nT) {
		int[] genMttrAdjusted = new int[genMttr.length];
		for (int i1 = 0; i1 < genMttrAdjusted.length; i1++) {
			genMttrAdjusted[i1] = (int) (genMttr[i1] * adjCoeff);
			if (genMttrAdjusted[i1] > nT)
				genMttrAdjusted[i1] = nT;
		}
		return genMttrAdjusted;
	}

	static File[] getGenScenFiles(String folder) {

		File folderPath = new File("Data" + File.separator + folder);

		// scenarios for operable and inoperable generators
		File[] genBrokenScenario = folderPath.listFiles(new FilenameFilter() {
			@Override
			public boolean accept(File dir, String name) {
				return name.toLowerCase().contains("gen");
			}
		});
		return genBrokenScenario;
	}

	/***
	 * scenarios for gas supply.
	 * 
	 * @param folder
	 * @return return list of files containing gas supply scenarios
	 */

	static TextArea gui() {
		JFrame jf = new JFrame("output");
		jf.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		jf.setSize(500, 500);
		JPanel jp = new JPanel();

		TextArea jta = new TextArea(20, 50);
		jp.add(jta);
		jf.add(jp);
		jf.setVisible(true);
		return jta;
	}
}

// private static void useSingleThreadMethid() {
// UnitCommitment uc;
// for (String testCase : Config.cases) {
// // data that are fixed for all the scenarios
// Data data = new SCUCDataReader.Data(testCase);
// int nT = data.demandHourlyTotal.length;
// int nG = data.bus.length;
// int nL = data.line.length;
// GenScenario gens = getGenScen(testCase, nG, nL, nT, setLen,
// Config.scenarioSource.someSubsets,
// Config.investmentPool.length);
// // TextArea jta = gui();
//
// int genScenCounter = 0;
// GasScenario gas;
//
// /***
// * it is the improvement in the MTTR and also absorption 0 means no investment
// * and .25% means investment with 25% of the worth of the component according
// to
// * linear improvement to MTTR and absorption the absorption after .25%
// * investment will be .25% the MTTR adjusted after recover will reduce to
// * (1-.25%) MTTR
// */
//
// int[] genMttrAdjusted = new int[data.genMttr.length];
// int[] lineMttrAdjusted = new int[data.lineMttr.length];
// for (double[] inv : Config.investmentPool) {
//
// // adjustment for 24 hours instead of 96 hours
// // hence squeeze the MTTR by 2.5
// double genAdjCoeff = 2.5;
// genMttrAdjusted = adjust(data.genMttr, 1 / genAdjCoeff * (1 - inv[0]), nT);
// lineMttrAdjusted = adjust(data.lineMttr, (1 - inv[0]), nT);
//
// gens.setGenLineAdjustedValue(genMttrAdjusted, lineMttrAdjusted, inv[0]);
// gens.setAbsorption(inv[1]);
// while (genScenCounter < gens.numberOfScenarios) {
// double[][] ge = gens.nextGenScen();
// double[][] lineBrokenScenario = gens.nextLineScen();
// gas = new GasScenario(testCase);
// while (gas.counter < gas.n) {
// System.out.println("invR " + inv[0] + "_invA " + inv[1] + "_genscentotal "
// + gens.numberOfScenarios + "_scenCounter " + genScenCounter + "\n\n\n");
// String s1 = gens.toString();
// String[] IDs = { testCase, s1, " inv_ttr " + inv[0] + " inv_abs " + inv[1] };
// double[][] gasB = gas.next();
//
// uc = new UnitCommitment(IDs, data, ge, lineBrokenScenario, gasB);
// try {
// uc.buildModel();
// } catch (FileNotFoundException e) {
// e.printStackTrace();
// } catch (IOException e) {
// e.printStackTrace();
// }
// uc = null;
//
// genScenCounter++;
// }
// }
// }
//
// }
// }
