package resilience;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;

import ilog.concert.*;
import ilog.cplex.*;
import resilience.SCUCDataReader;
import resilience.SCUCDataReader.Data;

import java.util.logging.Level;
import java.util.logging.Logger;

import inputOutput.WriteToFile;

/**
 * <h1>Security-Constrained Unit Commitment</h1> this is an implementation of
 * the Security-Constrained Unit Commitment the original paper is: Yong Fu,
 * Mohammad Shahidehpour, and Zuyi Li, 2005 Security-Constrained Unit Commitment
 * With AC Constraints, EEE TRANSACTIONS ON POWER SYSTEMS, VOL. 20, NO. 3,
 * AUGUST 2005
 * <p>
 * <b>The constraints are</b><br>
 * 
 * 1) Power balance <br>
 * 2) Hourly generation bids <br>
 * 3) Must-on and area protection constraints <br>
 * 4) System spinning and operating reserve requirements <br>
 * 5) Minimum up and down time limits <br>
 * 6) Ramp rate limits <br>
 * 7) Startup and shutdown characteristics of units<br>
 * 8) Fuel and multiple emission constraints <br>
 * 9) Transmission flow and bus voltage limits <br>
 * 10)Load shedding and bilateral contracts <br>
 * 11)Limits on state and control variables including real and reactive power
 * generation, controlled voltages, and set- tings of tap-changing and
 * phase-shifting transformers<br>
 * 12) Scheduled outages <br>
 * 
 * @author Mohammad Najarian
 * @version 1.0
 * @since October 13 2016
 * 
 */

public class UnitCommitmentMultiThread implements Runnable {
	public static int objecCounter = 0;

	public enum variableType {
		binary, positiveInteger, negativeInteger, positiveContinuous, negativeContinuous, unrestrictedInteger,
		unrestrictedContinuouus
	}

	public String caseName;
	public String genScenarioID;
	public String gasScenarioID;
	public static double VOLL = 1000;

//	public static void main(String[] args) throws FileNotFoundException {
//		if (args.length > 0) {
//			try {
//				if (!args[0].isEmpty()) {
//					VOLL = Double.parseDouble(args[0]);
//				}
////				File broken = new File("Data/bus118/Broken.txt");
////				File gas = new File("Data/bus118/gasScenarios/gas901.txt");
//				if (!args[1].isEmpty()) {
//				} else {
//
//				}
//			} catch (NumberFormatException e) {
//				e.printStackTrace();
//			}
//		}
//
//		System.exit(0);
//	}

	/**
	 * This coefficient is just for the case that the demand is too low and we just
	 * have load shedding in severe cases it increases the input demand to the value
	 * of this variable
	 */
	public static String outputDirectory;
	public static String date;
	/**
	 * index: <br>
	 * number of time periods
	 */
	int nT; // NT Number of periods under study (24 h).

	/**
	 * index: <br>
	 * number of buses
	 */
	int nB; // NB Number of buses.
	/**
	 * index: <br>
	 * number of units
	 */
	int nG; // NG Number of units.
	/**
	 * index: <br>
	 * number of lines
	 */
	int nL; // NL Number of lines.

	/**
	 * index: <br>
	 * number of segments <br>
	 * the original cost function is not linear, so using line segments we use the
	 * linear estimates which is a piecewise linear function the same as g in the
	 * GAMS
	 */
	int nLineSegments; // NL Number of lines.

	IloCplex cplex;
	SCUCDataReader.Data data;
	double[][] lsVals;
	// < editor-fold defaultstate="collapsed" desc="Variables">

	// variable declaration
	// binary variables
	/**
	 * Binary variabl <br>
	 * 
	 * u is binary, if the unit works it is set to 1 and if it is not working it is
	 * set to 0
	 */
	IloNumVar[][] u; // Commitment state of unit at time - binary variable

	/**
	 * * Binary variable:<br>
	 * generator start up indicator<br>
	 * y(t)=u(t-1)(1-u(t))
	 */
	IloNumVar[][] y; // start up - binary variable

	/**
	 * *Binary variable:<br>
	 * generator shut down indicator
	 */
	IloNumVar[][] z; // shut down - binary variable
	IloNumVar[][] v; // - binary variable
	IloNumVar[][] w; // - binary variable

	/**
	 * Variable: <br>
	 * Production of generation unit b at bus i at time t
	 */
	IloNumVar[][][] p;

	/**
	 * urs variable : load shedding
	 */
	IloNumVar[][] ls; // load shedding- positive variable

	/**
	 * positive Variable <br>
	 * off time for unit i at time t equals 1 <br>
	 * the sane as sd
	 */
	IloNumVar[][] dt;

	/**
	 * positive variable:<br>
	 * up time for unit i at time t<br>
	 * same as su
	 */
	IloNumVar[][] ut;
	/**
	 * Positive variable <br>
	 * spinning reserve
	 */
	IloNumVar[][] sr;

	/**
	 * Positive variable <br>
	 * operating reserve
	 */
	IloNumVar[][] or;

	/**
	 * unrestricted-in-sign variable
	 */
	IloNumVar[][] flow;

	IloNumVar[][] theta;

	// </editor-fold>
	/**
	 * Range: <br>
	 * list of constraint sets
	 */
	double[][] genBrokenScen;
	double[][] lineBroken;
	double[][] gasSupplyScen;

	ArrayList<IloRange[]> constraints;

	int id = 0;
	public static boolean headerNotWritten=true;
	
	
	public UnitCommitmentMultiThread(String[] caseNameArg, Data data, double[][] genBrokenScen,
			double[][] lineBrokenScen, double[][] gasSupplyScen, int scID) {

		this.caseName = caseNameArg[0];
		this.genScenarioID = caseNameArg[1];
		this.gasScenarioID = caseNameArg[2];
		this.id = scID;
		this.data = data;
		this.genBrokenScen = genBrokenScen;
		this.gasSupplyScen = gasSupplyScen;
		this.lineBroken = lineBrokenScen;
		nT = data.demandHourlyTotal.length;
		nB = data.percentload.length;
		nG = data.bus.length;
		nLineSegments = data.cseg[0].length;
		nL = data.line.length;

		if (date == null) {
			DateFormat df = new SimpleDateFormat("yyyyMMddhhmm");
			Date d = Calendar.getInstance().getTime();

			date = df.format(d);
			System.out.println(date);
		}
		if (outputDirectory == null) {
			outputDirectory = "output" + File.separator + date;
			makeDir(outputDirectory);
			makeDir(outputDirectory+File.separator+"details");
		}
		String pathCase = outputDirectory + File.separator + caseName;
		makeDir(pathCase);

	}

	public void makeDir(String path) {
		File od = new File(path);
		if (!od.exists()) {
			if (od.mkdir()) {

				System.out.println("Output directory is : " + od.getAbsolutePath());
			} else {
				System.out.println("Failed to create outupt folder");
			}
		}
	}

	private void buildModel() throws FileNotFoundException, IOException {
		try {
			System.out.println(
					"\nbegin Thread number " + this.objecCounter + " for: " + caseName + "\t" + genScenarioID + "\n");
			cplex = new IloCplex();
			cplex.setParam(IloCplex.IntParam.Threads, 8);
//			cplex.setParam(IloCplex.Param.MIP.Tolerances.MIPGap, 0.3);
//			cplex.setOut(null);
			constraints = new ArrayList<IloRange[]>();
			variableDeclaration();
			objectiveDeclaration();

			maxProductionSegments();

			powerMaxMinConstraint();
			unitCommitmentConstraint(); //start up shut down indicators
			minDownTime();
			minUpTime();
			unitRampUpConstraint();
			unitRampDownConstraint();	
			
			unitSRCapacityConstraint();
			unitPSRConstraint();
			unitORSRrelationship();
			systemMinumumSRConstraint();
			systemMinimumORConstraint();
			flowCapacityConstraint();
			flowPhaseConstraint();			
			loadBalanceConstraint();

			gasSupplyConstrait();

			// System.out.println(" \n\n\n solve cplex for: " + caseName
			// +"\t"+genScenarioID+"\t"+gasScenarioID+"\n\n\n" );
			WriteToFile.writeLog("solve cplex for: " + caseName + "\t" + genScenarioID + "\t" + gasScenarioID);
			cplex.exportModel(outputDirectory +"/" +"model"+caseName + ".lp");

			if (cplex.solve()) {
				
				WriteToFile.writeLog(caseName + "." + genScenarioID + "." + gasScenarioID + " solution status: "
						+ cplex.getStatus());
				cplex.output().println(cplex.getStatus());
				cplex.output().println(cplex.getObjValue());

				lsVals = new double[ls.length][];
				for (int b = 0; b < lsVals.length; b++) {
					lsVals[b] = cplex.getValues(ls[b]);

				}
//				WriteToFile.write(lsVals, outputDirectory + File.separator + caseName + File.separator + gasScenarioID);


				if (UnitCommitmentMultiThread.headerNotWritten) {
					WriteToFile.writeHeader(outputDirectory, caseName + "_" + date, this.nT);
//					WriteToFile.writeDetailHeader(outputDirectory, caseName + "_" + date, this.nT,this.id);
					UnitCommitmentMultiThread.headerNotWritten=false;
				}
				WriteToFile.writeDetails(cplex.getObjValue(), lsVals, data.demand, outputDirectory,caseName + "_" + date, 
						this.id, genScenarioID);
				WriteToFile.writeSummary(cplex.getObjValue(), weightedCount(genBrokenScen, data.pmax),
						weightedSum(genBrokenScen, data.pmax), lsVals, data.demand, outputDirectory,
						caseName + "_" + date, genScenarioID,
						gasScenarioID.substring(0, gasScenarioID.length() - 4), "" + this.id);
//						
			} else {
				WriteToFile.writeLog(
						caseName + "." + genScenarioID + "." + gasScenarioID + " solution status: not successful");
			}
			cplex.clearModel();
			cplex.end();
			constraints = null;
			System.out.println("End scenario no: " + objecCounter++);
		} catch (IloException e) {
			e.printStackTrace();
		}
	}

	private double weightedCount(double[][] a, double[] w) {
		double wCount = 0;
		for (int i = 0; i < a.length; i++) {
			wCount += a[i].length * w[i];
		}
		return wCount;
	}

	private double weightedCount(int[][] a, double[] w) {
		double wCount = 0;
		for (int i = 0; i < a.length; i++) {
			wCount += a[i].length * w[i];
		}
		return wCount;
	}

	private double weightedSum(double[][] a, double[] w) {
		double sum = 0;
		for (int i = 0; i < a.length; i++) {
			sum += sum(a[i]) * w[i];
		}
		return sum;
	}

	private double weightedSum(int[][] a, double[] w) {
		double sum = 0;
		for (int i = 0; i < a.length; i++) {
			sum += sum(a[i]) * w[i];
		}
		return sum;
	}

	private double sum(double[] a) {
		double sum = 0;
		for (int i = 0; i < a.length; i++) {
			sum += a[i];
		}
		return sum;
	}

	private int sum(int[] a) {
		int sum = 0;
		for (int i = 0; i < a.length; i++) {
			sum += a[i];
		}
		return sum;
	}
//	private double sum(double [][]a) {
//		double sum=0;
//		for (int i=0; i<a.length; i++){
//			sum+=sum(a[i]);
//		}
//		return sum;
//	}

	private void gasSupplyConstrait() {
		try {
			for (int i = 0; i < data.ccGenIndex.length; i++) {
				IloRange[] gasHelper = new IloRange[nT];
				for (int t = 0; t < nT; t++) {
					IloLinearNumExpr helperExp = cplex.linearNumExpr();
					for (int j = 0; j < nLineSegments; j++) {
						helperExp.addTerm(p[data.ccGenIndex[i]][j][t], 1);
					}
					// System.out.println("["+ i + "]["+ t + "] gas "
					// +data.gasSupply[data.gasNodeID[i]][t] + "\t ccgenIndex " + data.ccGenIndex[i]
					// );
					gasHelper[t] = cplex.addLe(helperExp,
							data.pmax[data.ccGenIndex[i]] * this.gasSupplyScen[data.gasNodeID[i]][t],
							"Gas Supply limit [" + data.ccGenIndex[i] + "][" + t + "]");
				}
				constraints.add(gasHelper);
			}
		} catch (IloException e) {
			e.printStackTrace();
		}
	}

	/**
	 * con2uc(i,g,t).. pseg1(i,g,t) =l= psegmax(i,g);
	 * 
	 * @throws IloException
	 */
	private void maxProductionSegments() throws IloException {
		for (int i = 0; i < nG; i++)
			for (int j = 0; j < nLineSegments; j++) {
				IloRange[] mpg = new IloRange[nT];
				for (int t = 0; t < nT; t++)
					mpg[t] = cplex.addLe(cplex.prod(1, p[i][j][t]), data.psegmax[i][j],
							"production segment limit  [" + i + "][" + j + "][" + t + "]");
			}
	}

	private void minDownTime() {
		try {

			// con16uc(i,t)$(ord(t)>1).. sd(i,t) =g= md(i)*y(i,t+1);
			for (int i = 0; i < nG; i++) {

				IloRange[] mdt = new IloRange[nT];
				for (int t = 0; t < nT - 1; t++) {
					IloLinearNumExpr expHelpermdt = cplex.linearNumExpr();
					expHelpermdt.addTerm(1, dt[i][t]);
					expHelpermdt.addTerm(-data.minDownTime[i], y[i][t + 1]);
					mdt[t] = cplex.addGe(expHelpermdt, 0, "min down time  [" + i + "][" + t + "]");
				}
				constraints.add(mdt);
			}
			// con10uc(i,t)$(ord(t)>1).. sd(i,t) =l= mf(i)*(1-u(i,t));
			for (int i = 0; i < nG; i++) {
				IloRange[] dtUC = new IloRange[nT];
				for (int t = 0; t < nT; t++) {
					IloLinearNumExpr exHelperDTUC = cplex.linearNumExpr();
					exHelperDTUC.addTerm(1, dt[i][t]);
					exHelperDTUC.addTerm(data.bigMDownTime[i], u[i][t]);
					dtUC[t] = cplex.addLe(exHelperDTUC, data.bigMDownTime[i], "minDown [" + i + "][" + t + "]");
				}
				constraints.add(dtUC);
			}

			// con11uc(i,t)$(ord(t)>1).. sd(i,t)-sd(i,t-1) =l= 1;
			for (int i = 0; i < nG; i++) {
				IloRange[] deltaDTUpperBound = new IloRange[nT];

				for (int t = 1; t < nT; t++) {
					IloLinearNumExpr exHelperDelta = cplex.linearNumExpr();
					exHelperDelta.addTerm(1, dt[i][t]);
					exHelperDelta.addTerm(-1, dt[i][t - 1]);
					deltaDTUpperBound[t] = cplex.addLe(exHelperDelta, 1, "delta down time ub [" + i + "][" + t + "]");
				}
				constraints.add(deltaDTUpperBound);
			}
			// con12uc(i,t)$(ord(t)>1).. sd(i,t)-sd(i,t-1) =g= 1-(mf(i)+1)*u(i,t);
			for (int i = 0; i < nG; i++) {

				IloRange[] deltaDTLowerBound = new IloRange[nT];
				for (int t = 1; t < nT; t++) {
					IloLinearNumExpr exHelperDelta = cplex.linearNumExpr();
					exHelperDelta.addTerm(1, dt[i][t]);
					exHelperDelta.addTerm(-1, dt[i][t - 1]);
					exHelperDelta.addTerm(data.bigMDownTime[i] + 1, u[i][t]);
					deltaDTLowerBound[t] = cplex.addGe(exHelperDelta, 1, " down time LB  [" + i + "][" + t + "]");
				}

				constraints.add(deltaDTLowerBound);
			}

		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	private void minUpTime() {
		try {
			// con17uc(i,t)$(ord(t)>1).. su(i,t) =g= mu(i)*z(i,t+1);
			for (int i = 0; i < nG; i++) {
				IloRange[] mut = new IloRange[nT];
				for (int t = 0; t < nT - 1; t++) {
					IloLinearNumExpr expHelper = cplex.linearNumExpr();
					expHelper.addTerm(1, ut[i][t]);
					expHelper.addTerm(-data.mu[i], z[i][t + 1]);
					mut[t] = cplex.addGe(expHelper, 0, "min up time  [" + i + "][" + t + "]");
				}
				constraints.add(mut);
			}

			// con13uc(i,t)$(ord(t)>1).. su(i,t) =l= mn(i)*u(i,t);
			for (int i = 0; i < nG; i++) {
				IloRange[] utUC = new IloRange[nT];
				for (int t = 0; t < nT; t++) {
					IloLinearNumExpr exHelperUTUC = cplex.linearNumExpr();
					exHelperUTUC.addTerm(1, ut[i][t]);
					exHelperUTUC.addTerm(-data.bigMUPTime[i], u[i][t]);
					utUC[t] = cplex.addLe(exHelperUTUC, 0, "minUP [" + i + "][" + t + "]");
				}
				constraints.add(utUC);
			}

			// con14uc(i,t)$(ord(t)>1).. su(i,t)-su(i,t-1) =l= 1;
			for (int i = 0; i < nG; i++) {
				IloRange[] deltaUTUpperBound = new IloRange[nT];
				for (int t = 1; t < nT; t++) {
					IloLinearNumExpr exHelperDelta = cplex.linearNumExpr();
					exHelperDelta.addTerm(1, ut[i][t]);
					exHelperDelta.addTerm(-1, ut[i][t - 1]);
					deltaUTUpperBound[t] = cplex.addLe(exHelperDelta, 1, "delta up time ub [" + i + "][" + t + "]");
				}
				constraints.add(deltaUTUpperBound);
			}
			// con15uc(i,t)$(ord(t)>1).. su(i,t)-su(i,t-1) =g= (mn(i)+1)*u(i,t)-mn(i);
			for (int i = 0; i < nG; i++) {
				IloRange[] deltaUTLowerBound = new IloRange[nT];
				for (int t = 1; t < nT; t++) {
					IloLinearNumExpr exHelperDelta = cplex.linearNumExpr();
					exHelperDelta.addTerm(1, ut[i][t]);
					exHelperDelta.addTerm(-1, ut[i][t - 1]);
					exHelperDelta.addTerm(-(data.bigMUPTime[i] + 1), u[i][t]);
					deltaUTLowerBound[t] = cplex.addGe(exHelperDelta, -data.bigMUPTime[i],
							"delta up time LB  [" + i + "][" + t + "]");
				}
				constraints.add(deltaUTLowerBound);
			}

		} catch (Exception e) {
			e.printStackTrace();
		}

	}

	private void unitRampDownConstraint() {
		try {

			for (int i = 0; i < nG; i++) {

				IloRange[] urdc = new IloRange[nT];

				for (int t = 1; t < nT; t++) {
					IloLinearNumExpr lhs = cplex.linearNumExpr();

					for (int j = 0; j < nLineSegments; j++) {
						lhs.addTerm(-1, p[i][j][t]);
						lhs.addTerm(1, p[i][j][t - 1]);
					}
					lhs.addTerm(-data.pmin[i], z[i][t]);
					lhs.addTerm(data.rd[i], z[i][t]);

					urdc[t] = cplex.addLe(lhs, data.rd[i], "rampdown constraint  [" + i + "][" + t + "]");
				}
				constraints.add(urdc);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}

	}

	/**
	 * ramp up constraint
	 */
	private void unitRampUpConstraint() {

		try {

			for (int i = 0; i < nG; i++) {

				IloRange[] uruc = new IloRange[nT];

				for (int t = 1; t < nT; t++) {
					IloLinearNumExpr lhs = cplex.linearNumExpr();

					for (int j = 0; j < nLineSegments; j++) {
						lhs.addTerm(1, p[i][j][t]);
						lhs.addTerm(-1, p[i][j][t - 1]);
					}
					lhs.addTerm(-data.pmin[i], y[i][t]);
					lhs.addTerm(data.ru[i], y[i][t]);

					uruc[t] = cplex.addLe(lhs, data.ru[i], "ramp up constraint [" + i + "][" + t + "]");
				}
				constraints.add(uruc);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	private void unitORSRrelationship() {
		try {
			for (int i = 0; i < nG; i++) {
				IloRange[] ORSR = new IloRange[nT];

				for (int t = 0; t < nT; t++) {
					IloLinearNumExpr xprHelper = cplex.linearNumExpr();
					xprHelper.addTerm(1, or[i][t]);

					xprHelper.addTerm(-1, sr[i][t]);
					xprHelper.addTerm(data.qsc[i], u[i][t]);
					ORSR[t] = cplex.addEq(xprHelper, data.qsc[i],
							" relationship between or and sr [" + i + "][" + t + "]");
				}
				constraints.add(ORSR);
			}
		} catch (IloException e) {
			e.printStackTrace();
		}
	}

	/**
	 * <b> minimum required spinning reserve constraint </b><br>
	 * The spinning reserve is the extra generating capacity that is available by
	 * increasing the power output of generators that are already connected to the
	 * power system
	 */
	private void systemMinumumSRConstraint() {
		try {
			IloRange[] msrc = new IloRange[nT];
			for (int t = 0; t < nT; t++) {
				IloLinearNumExpr xprHelper = cplex.linearNumExpr();
				for (int i = 0; i < nG; i++)
					xprHelper.addTerm(1, sr[i][t]);
				// System.out.println("ssr ["+t+"] = " + data.ssr[t]);
				msrc[t] = cplex.addGe(xprHelper, data.ssr[t], " required spinning reserve  constraint [" + t + "]");
			}
			constraints.add(msrc);
		} catch (IloException e) {
			e.printStackTrace();
		}
	}

	/**
	 * minimum required operating reserve constraint operating reserve is the
	 * generating capacity available to the system operator within a short interval
	 * of time to meet demand in case a generator goes down or there is another
	 * disruption to the supply.
	 */
	private void systemMinimumORConstraint() {
		try {
			IloRange[] morc = new IloRange[nT];
			for (int t = 0; t < nT; t++) {
				IloLinearNumExpr xprHelper = cplex.linearNumExpr();
				for (int i = 0; i < nG; i++)
					xprHelper.addTerm(1, or[i][t]);
				morc[t] = cplex.addGe(xprHelper, data.sor[t], " required operating reserve  constraint [" + t + "]");
			}
			constraints.add(morc);
		} catch (IloException e) {
			e.printStackTrace();
		}
	}

	private void unitSRCapacityConstraint() {
		try {
			for (int i = 0; i < nG; i++) {
				IloRange[] src = new IloRange[nT];

				for (int t = 0; t < nT; t++) {
					IloLinearNumExpr xprHelper = cplex.linearNumExpr();
					xprHelper.addTerm(1, sr[i][t]);
					xprHelper.addTerm(-10 * data.msr[i], u[i][t]);
					src[t] = cplex.addLe(xprHelper, 0, "unit spinning capacity constraint [" + i + "][" + t + "]");
				}
				constraints.add(src);
			}

		} catch (IloException e) {
			e.printStackTrace();
		}
	}

	/**
	 * given the upper production limit (pmax) and spinning reserve (sr) for unit i
	 * the production can't exceed the difference of pmax and spinning reserve
	 */
	private void unitPSRConstraint() {
		try {
			for (int i = 0; i < nG; i++) {
				IloRange[] src = new IloRange[nT];

				for (int t = 0; t < nT; t++) {
					IloLinearNumExpr xprHelper = cplex.linearNumExpr();
					for (int j = 0; j < nLineSegments; j++)
						xprHelper.addTerm(1, p[i][j][t]);
					xprHelper.addTerm(1, sr[i][t]);

					src[t] = cplex.addLe(xprHelper, data.pmax[i],
							"production capacity constraint [" + i + "][" + t + "]");
				}
				constraints.add(src);
			}

		} catch (IloException e) {
			e.printStackTrace();
		}

	}

	/**
	 * Startup and Shutdown Indicators relationship
	 */
	private void unitCommitmentConstraint() {

		try {
			for (int i = 0; i < nG; i++) {
				IloRange[] ucc = new IloRange[nT];
				for (int t = 1; t < nT; t++) {
					IloLinearNumExpr xprHelper = cplex.linearNumExpr();
					xprHelper.addTerm(1, u[i][t]);
					xprHelper.addTerm(-1, u[i][t - 1]);
					xprHelper.addTerm(-1, y[i][t]);
					xprHelper.addTerm(1, z[i][t]);
					ucc[t] = cplex.addEq(xprHelper, 0, "unitCommitmentConstraint [" + i + "][" + t + "]");
				}
				constraints.add(ucc);
			}
		} catch (IloException e) {
			e.printStackTrace();
		}
	}

	/**
	 * the power generation has a max and min
	 */
	private void powerMaxMinConstraint() {

		IloLinearNumExpr xprHelper;
		try {
			if (genBrokenScen == null) {
				throw new Exception("thread " + Thread.currentThread().getId() + " : broken is null");
			}

			// for each unit constraints are generated and added to constraints
			// set
			for (int i = 0; i < nG; i++) {

				IloRange[] pmaxc = new IloRange[nT];
				IloRange[] pminc = new IloRange[nT];
				for (int t = 0; t < nT; t++) {
					xprHelper = cplex.linearNumExpr();
					for (int j = 0; j < nLineSegments; j++) {
						xprHelper.addTerm(1., p[i][j][t]);
					}
					IloLinearNumExpr xprHelperMax = cplex.linearNumExpr();
					IloLinearNumExpr xprHelperMin = cplex.linearNumExpr();
					xprHelperMax.addTerm(data.pmax[i] * genBrokenScen[i][t], u[i][t]);
					xprHelperMin.addTerm(data.pmin[i] * genBrokenScen[i][t], u[i][t]);
					pmaxc[t] = (IloRange) cplex.addLe(xprHelper, xprHelperMax,
							"max power constraint [" + i + "][" + t + "]");
					pminc[t] = (IloRange) cplex.addGe(xprHelper, xprHelperMin,
							"min power constraint[" + i + "][" + t + "]");
				}
				constraints.add(pmaxc);
				constraints.add(pminc);
			}
		} catch (IloException e1) {
			e1.printStackTrace();
		}

		catch (Exception e) {
			e.printStackTrace();
		}
	}

	/**
	 * composed of fuel costs for producing electric power and startup and shutdown
	 * costs of individual units over the given period<br>
	 * con1ucs
	 */
	private void objectiveDeclaration() {
		try {
			IloLinearNumExpr obj;

			obj = cplex.linearNumExpr();

			// adding the fixed cost of generation
			// cost of supplying the load
			for (int i = 0; i < nG; i++) {
				for (int t = 0; t < nT; t++) {
					obj.addTerm(data.cnl[i], u[i][t]);
				}
			}
			// adding the other cost of generation
			for (int i = 0; i < nG; i++) {
				for (int j = 0; j < nLineSegments; j++) {
					for (int t = 0; t < nT; t++) {
						obj.addTerm(data.cseg[i][j], p[i][j][t]);
					}
				}
			}

			// adding the cost of start up
			for (int i = 0; i < nG; i++) {
				for (int t = 0; t < nT; t++) {
					obj.addTerm(data.suc[i], y[i][t]);
				}
			}

			// adding the cost of shut down
			for (int i = 0; i < nG; i++) {
				for (int t = 0; t < nT; t++) {
					obj.addTerm(data.sdc[i], z[i][t]);
				}
			}

			// cost of load shedding (loss of load)
			for (int i = 0; i < nB; i++) {
				for (int t = 0; t < nT; t++) {
					obj.addTerm(ls[i][t], VOLL);
				}
			}

			cplex.addMinimize(obj);
		} catch (IloException e) {
			e.printStackTrace();
		}
	}

	/*
	 * private IloNumVar[][] numVarArrayDef(int m, int n, int lowerBound, double
	 * upperBound, String varName) throws IloException { IloNumVar[][] var = new
	 * IloNumVar[nB][nT]; for (int i = 0; i < m; i++) { for (int t = 0; t < n; t++)
	 * { var[i][t] = cplex.numVar(lowerBound, upperBound, varName + i + "." + t); }
	 * } return var; } private IloNumVar[][] boolVarArrayDef(int m, int n, String
	 * varName) { IloNumVar[][] var = null; try { var = new IloNumVar[m][n]; for
	 * (int i = 0; i < m; i++) { for (int t = 0; t < n; t++) { var[i][t] =
	 * cplex.boolVar(varName + i + "." + t); } } } catch (IloException e) {
	 * e.printStackTrace(); } return var; }
	 */

	/**
	 * flow = production -demand + load shedding con2dc(b,t).. utm(l,
	 * A(l,b)*flow(l,t))=e= pg1(b,t) - pd(b,t)+ LS(b,t);
	 */
	private void loadBalanceConstraint() {

		try {
			if (data.demand == null) {
				throw new Exception("error in thread " + Thread.currentThread().getName());
			}
			// System.out.println("thread: "+Thread.currentThread().getId()+"demand size =
			// "+data.demand.length);

			for (int b = 0; b < nB; b++) {
				IloRange[] flowBalance = new IloRange[nB];
				// System.out.println(" by " + data.demand[0].length);
				for (int t = 0; t < nT; t++) {

					IloLinearNumExpr xprHelperFlow = cplex.linearNumExpr();

					for (int ll = 0; ll < data.lineBus[b].size(); ll++) {
						// System.out.println("b= "+b +"\t t = " + t +"\t ll = " + ll + "\t linebus [b]"
						// + data.lineBus[b].get(ll) );
						int lineIndex = Math.abs(data.lineBus[b].get(ll)) - 1;
						double flowDirection = Math.signum(data.lineBus[b].get(ll));
						// System.out.println("b " + b + " - t " +t + " - ll " + ll + " = LI " +
						// lineIndex );
						xprHelperFlow.addTerm(flowDirection, flow[lineIndex][t]);
					}

					// checks if the bus is a generation unit or not
					// in the gen2bus wherever the bus is not a gu it is equal to -1 and
					// where bus is gu the row number of unit is returned
					if (data.gen2bus[b] != -1) {
						for (int j = 0; j < nLineSegments; j++) {
							xprHelperFlow.addTerm(-1, p[data.gen2bus[b]][j][t]);
						}
					}
					xprHelperFlow.addTerm(-1, ls[b][t]);

					// System.out.println("Thread" +Thread.currentThread().getId()+": demand[" + b +
					// "][" + t + "]="+data.demand[b][t]);
					flowBalance[b] = cplex.addEq(xprHelperFlow, -data.demand[b][t],
							"PowerBalanceConstraint[" + b + "][" + t + "]");
					xprHelperFlow.clear();
				}
				constraints.add(flowBalance);

			}
		} catch (IloException ex) {
			Logger.getLogger(UnitCommitment.class.getName()).log(Level.SEVERE, null, ex);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			System.out.println(e.getMessage());
			e.printStackTrace();
		}

	}

	private void flowCapacityConstraint() {
		try {
			for (int l = 0; l < nL; l++) {
				IloRange[] fcUpper = new IloRange[nT];
				IloRange[] fcLower = new IloRange[nT];
				for (int t = 0; t < nT; t++) {
					fcUpper[t] = cplex.addLe(flow[l][t], data.maxFlow[l] * this.lineBroken[l][t]);
					fcLower[t] = cplex.addGe(flow[l][t], -data.maxFlow[l] * this.lineBroken[l][t]);
				}
				constraints.add(fcLower);
				constraints.add(fcUpper);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	/**
	 * con5dc(l,t).. flow(l,t) =e= sum(b, (A(l,b)*theta(b,t))/x(l));
	 */
	private void flowPhaseConstraint() {
		try {
			for (int l = 0; l < nL; l++) {
				IloRange[] phc = new IloRange[nT];
				for (int t = 0; t < nT; t++) {
					IloLinearNumExpr expHelper = cplex.linearNumExpr();
					expHelper.addTerm(flow[l][t], 1);

					expHelper.addTerm(theta[data.line[l].startNode - 1][t], -1 / data.x[l]);
					expHelper.addTerm(theta[data.line[l].endNode - 1][t], +1 / data.x[l]);

					phc[t] = cplex.addEq(expHelper, 0, "flow theta [" + l + "][" + t + "]");
				}
				constraints.add(phc);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	private void variableDeclaration() {
		class VarMaker {
			public IloNumVar[][] numVarArrayDef(int m, int n, double lowerBound, double upperBound, String varName)
					throws IloException {
				IloNumVar[][] var = new IloNumVar[m][n];
				for (int i = 0; i < m; i++) {
					for (int t = 0; t < n; t++) {
						var[i][t] = cplex.numVar(lowerBound, upperBound, varName + i + "." + t);
					}
				}
				return var;
			}

			public IloNumVar[][] numVarArrayDef(int m, int n, double[] lowerBound, double[] upperBound, String varName)
					throws IloException {
				IloNumVar[][] var = new IloNumVar[m][n];
				for (int i = 0; i < m; i++) {
					for (int t = 0; t < n; t++) {
						var[i][t] = cplex.numVar(lowerBound[i], upperBound[i], varName + i + "." + t);
					}
				}
				return var;
			}

			public IloNumVar[][] boolVarArrayDef(int m, int n, String varName) {
				IloNumVar[][] var = null;
				try {
					var = new IloNumVar[m][n];
					for (int i = 0; i < m; i++) {
						for (int t = 0; t < n; t++) {
							var[i][t] = cplex.boolVar(varName + i + "." + t);
						}
					}
				} catch (IloException e) {
					e.printStackTrace();
				}
				return var;
			}
		}
		try {
			VarMaker vm = new VarMaker();

			u = vm.boolVarArrayDef(nG, nT, "u");
			y = vm.boolVarArrayDef(nG, nT, "y");
			z = vm.boolVarArrayDef(nG, nT, "z");

			p = new IloNumVar[nG][nLineSegments][nT];
			for (int i = 0; i < nG; i++) {
				for (int j = 0; j < nLineSegments; j++) {
					for (int t = 0; t < nT; t++) {
						p[i][j][t] = cplex.numVar(0, data.psegmax[i][j], "P" + i + "." + j + "." + t);
					}
				}
			}

			ls = vm.numVarArrayDef(nB, nT, 0, Double.POSITIVE_INFINITY, "ls");
			dt = vm.numVarArrayDef(nB, nT, 0, Double.POSITIVE_INFINITY, "dt");
			ut = vm.numVarArrayDef(nB, nT, 0, Double.POSITIVE_INFINITY, "ut");
			sr = vm.numVarArrayDef(nB, nT, 0, Double.POSITIVE_INFINITY, "sr");
			or = vm.numVarArrayDef(nB, nT, 0, Double.POSITIVE_INFINITY, "or");

			double[] maxFlowNegative = new double[data.maxFlow.length];
			for (int i = 0; i < maxFlowNegative.length; i++)
				maxFlowNegative[i] = -data.maxFlow[i];

			flow = vm.numVarArrayDef(nL, nT, maxFlowNegative, data.maxFlow, "flow");
			theta = vm.numVarArrayDef(nL, nT, -Double.POSITIVE_INFINITY, Double.POSITIVE_INFINITY, "Theta");

		} catch (IloException e) {
			e.printStackTrace();
		}
	}

	@Override
	public void run() {
		try {
			buildModel();
			cplex = null;

		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

}
