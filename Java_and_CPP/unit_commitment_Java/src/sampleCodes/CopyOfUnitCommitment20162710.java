package sampleCodes;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import ilog.concert.*;
import ilog.cplex.*;
import inputOutput.DisplayData;
import inputOutput.InputDataReader;
import inputOutput.InputDataReader.InputDataReaderException;

import java.util.logging.Level;
import java.util.logging.Logger;

import javax.sound.sampled.Line;

import sampleCodes.CopyOfUnitCommitment20162710.Data.lineItemsClass;

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

public class CopyOfUnitCommitment20162710 {
	public enum variableType {
		binary, positiveInteger, negativeInteger, positiveContinuous, negativeContinuous, unrestrictedInteger, unrestrictedContinuouus
	}

	public static String caseName;
	public static double VOLL = 1000;

	public static void main(String[] args) throws FileNotFoundException {
		if (args.length > 0) {
			try {
				if (!args[0].isEmpty()) {
					VOLL = Double.parseDouble(args[0]);
				}
				if (!args[1].isEmpty()) {
					caseName = args[1];
				}

				new CopyOfUnitCommitment20162710();

			} catch (NumberFormatException e) {
				e.printStackTrace();
			}
		}

		System.exit(0);
	}

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
	 * number of ????? <br>
	 * the same as g in the gams
	 */
	int nGU; // NL Number of lines.

	IloCplex cplex;
	Data data;

	// <editor-fold defaultstate="collapsed" desc="Variables">

	// variable declaration
	// binary variables
	/**
	 * Binary variabl <br>
	 * 
	 * u is binary, if the unit works it is set to 1 and if it is not working it
	 * is set to 0
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

	IloNumVar [][] flow;
	// </editor-fold>
	/**
	 * Range: <br>
	 * list of constraint sets
	 */
	ArrayList<IloRange[]> constraints;

	public CopyOfUnitCommitment20162710(String caseNameArg) {

	}

	public CopyOfUnitCommitment20162710() {

		data = new Data(caseName);
		nT = data.demandHourlyTotal.length;
		nB = data.percentload.length;
		nG = data.bus.length;
		nGU = data.cseg[0].length;
		nL = data.line.length;
		buildModel();
	}

	private void buildModel() {
		try {
			cplex = new IloCplex();
			constraints = new ArrayList<IloRange[]>();
			variableDeclaration();
			objectiveDeclaration();

			maxProductionSegments();

			loadBalanceConstraint();
			powerMaxMinConstraint();
			unitCommitmentConstraint();

			unitSRCapacityConstraint();
			unitPSRConstraint();
			systemMinumumSRConstraint();
			systemMinimumORConstraint();
			unitORSRrelationship();

			unitRampUpConstraint();
			unitRampDownConstraint();

			minUpTime();
			minDownTime();

			cplex.exportModel("model" + caseName + ".lp");
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
			for (int j = 0; j < nGU; j++) {
				IloRange[] mpg = new IloRange[nT];
				for (int t = 0; t < nT; t++)
					mpg[t] = cplex.addLe(cplex.prod(1, p[i][j][t]),
							data.psegmax[i][j]);
			}
	}

	private void minDownTime() {
		try {
			for (int i = 0; i < nG; i++) {

				IloRange[] mdt = new IloRange[nT];
				for (int t = 0; t < nT - 1; t++) {
					IloLinearNumExpr expHelpermdt = cplex.linearNumExpr();
					expHelpermdt.addTerm(1, dt[i][t]);
					expHelpermdt.addTerm(-data.md[i], y[i][t + 1]);
					mdt[t] = cplex.addGe(expHelpermdt, 0, "min down time  ["
							+ i + "][" + t + "]");
				}

				IloRange[] dtUC = new IloRange[nT];
				for (int t = 0; t < nT; t++) {
					IloLinearNumExpr exHelperDTUC = cplex.linearNumExpr();
					exHelperDTUC.addTerm(1, dt[i][t]);
					exHelperDTUC.addTerm(data.mf[i], u[i][t]);
					dtUC[t] = cplex.addLe(exHelperDTUC, data.mf[i], "minDown ["
							+ i + "][" + t + "]");
				}

				IloRange[] deltaDTUpperBound = new IloRange[nT];
				IloRange[] deltaDTLowerBound = new IloRange[nT];
				for (int t = 1; t < nT; t++) {
					IloLinearNumExpr exHelperDelta = cplex.linearNumExpr();
					exHelperDelta.addTerm(1, dt[i][t]);
					exHelperDelta.addTerm(-1, dt[i][t - 1]);
					deltaDTUpperBound[t] = cplex.addLe(exHelperDelta, 1,
							"delta down time ub [" + i + "][" + t + "]");

					exHelperDelta.addTerm(data.mf[i] + 1, u[i][t]);
					deltaDTLowerBound[t] = cplex.addGe(exHelperDelta, 1,
							"delta down time LB  [" + i + "][" + t + "]");
				}

				constraints.add(mdt);
				constraints.add(dtUC);
				constraints.add(deltaDTLowerBound);
				constraints.add(deltaDTUpperBound);
			}

		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	private void minUpTime() {
		try {
			for (int i = 0; i < nG; i++) {

				IloRange[] mut = new IloRange[nT];
				for (int t = 0; t < nT - 1; t++) {
					IloLinearNumExpr expHelper = cplex.linearNumExpr();
					expHelper.addTerm(1, ut[i][t]);
					expHelper.addTerm(-data.mu[i], z[i][t + 1]);
					mut[t] = cplex.addGe(expHelper, 0, "min up time  [" + i
							+ "][" + t + "]");
				}

				IloRange[] utUC = new IloRange[nT];
				for (int t = 0; t < nT; t++) {
					IloLinearNumExpr exHelperUTUC = cplex.linearNumExpr();
					exHelperUTUC.addTerm(1, ut[i][t]);
					exHelperUTUC.addTerm(data.mn[i], u[i][t]);
					utUC[t] = cplex.addLe(exHelperUTUC, data.mn[i], "minUP ["
							+ i + "][" + t + "]");
				}

				IloRange[] deltaUTUpperBound = new IloRange[nT];
				IloRange[] deltaUTLowerBound = new IloRange[nT];
				for (int t = 1; t < nT; t++) {
					IloLinearNumExpr exHelperDelta = cplex.linearNumExpr();
					exHelperDelta.addTerm(1, ut[i][t]);
					exHelperDelta.addTerm(-1, ut[i][t - 1]);
					deltaUTUpperBound[t] = cplex.addLe(exHelperDelta, 1,
							"delta down time ub [" + i + "][" + t + "]");

					exHelperDelta.addTerm(-(data.mn[i] + 1), u[i][t]);
					deltaUTLowerBound[t] = cplex.addGe(exHelperDelta,
							data.mn[i], "delta down time LB  [" + i + "][" + t
							+ "]");
				}
				constraints.add(mut);
				constraints.add(utUC);
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

					for (int j = 0; j < nGU; j++) {
						lhs.addTerm(-1, p[i][j][t]);
						lhs.addTerm(1, p[i][j][t - 1]);
					}
					lhs.addTerm(-data.pmin[i], z[i][t]);
					lhs.addTerm(data.rd[i], z[i][t]);

					urdc[t] = cplex.addLe(lhs, data.rd[i],
							"rampdown constraint  [" + i + "][" + t + "]");
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

					for (int j = 0; j < nGU; j++) {
						lhs.addTerm(1, p[i][j][t]);
						lhs.addTerm(-1, p[i][j][t - 1]);
					}
					lhs.addTerm(-data.pmin[i], y[i][t]);
					lhs.addTerm(data.ru[i], y[i][t]);

					uruc[t] = cplex.addLe(lhs, data.ru[i],
							"ramp up constraint [" + i + "][" + t + "]");
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
							" relationship between or and sr [" + i + "][" + t
							+ "]");
				}
				constraints.add(ORSR);
			}
		} catch (IloException e) {
			e.printStackTrace();
		}
	}

	/**
	 * <b> minimum required spinning reserve constraint </b><br>
	 * The spinning reserve is the extra generating capacity that is available
	 * by increasing the power output of generators that are already connected
	 * to the power system
	 */
	private void systemMinumumSRConstraint() {
		try {
			IloRange[] msrc = new IloRange[nT];
			for (int t = 0; t < nT; t++) {
				IloLinearNumExpr xprHelper = cplex.linearNumExpr();
				for (int i = 0; i < nG; i++)
					xprHelper.addTerm(1, sr[i][t]);
				msrc[t] = cplex.addGe(xprHelper, data.ssr[t],
						" required spinning reserve  constraint [" + t + "]");
			}
			constraints.add(msrc);
		} catch (IloException e) {
			e.printStackTrace();
		}
	}

	/**
	 * minimum required operating reserve constraint operating reserve is the
	 * generating capacity available to the system operator within a short
	 * interval of time to meet demand in case a generator goes down or there is
	 * another disruption to the supply.
	 */
	private void systemMinimumORConstraint() {
		try {
			IloRange[] morc = new IloRange[nT];
			for (int t = 0; t < nT; t++) {
				IloLinearNumExpr xprHelper = cplex.linearNumExpr();
				for (int i = 0; i < nG; i++)
					xprHelper.addTerm(1, or[i][t]);
				morc[t] = cplex.addGe(xprHelper, data.sor[t],
						" required operating reserve  constraint [" + t + "]");
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
					src[t] = cplex.addLe(xprHelper, 0,
							"unit spinning capacity constraint [" + i + "]["
							+ t + "]");
				}
				constraints.add(src);
			}

		} catch (IloException e) {
			e.printStackTrace();
		}
	}

	/**
	 * given the upper production limit (pmax) and spinning reserve (sr) for
	 * unit i the production can't exceed the difference of pmax and spinning
	 * reserve
	 */
	private void unitPSRConstraint() {
		try {
			for (int i = 0; i < nG; i++) {
				IloRange[] src = new IloRange[nT];

				for (int t = 0; t < nT; t++) {
					IloLinearNumExpr xprHelper = cplex.linearNumExpr();
					for (int j = 0; j < nGU; j++)
						xprHelper.addTerm(1, p[i][j][t]);
					xprHelper.addTerm(1, sr[i][t]);

					src[t] = cplex.addLe(xprHelper, data.pmax[i],
							"production capacity constraint [" + i + "][" + t
							+ "]");
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
					ucc[t] = cplex.addEq(xprHelper, 0,
							"unitCommitmentConstraint [" + i + "][" + t + "]");
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

			// for each unit constraints are generated and added to constraints
			// set
			for (int i = 0; i < nG; i++) {

				IloRange[] pmaxc = new IloRange[nT];
				IloRange[] pminc = new IloRange[nT];
				for (int t = 0; t < nT; t++) {
					xprHelper = cplex.linearNumExpr();
					for (int j = 0; j < nGU; j++) {
						xprHelper.addTerm(1., p[i][j][t]);
					}
					IloLinearNumExpr xprHelperMax = cplex.linearNumExpr();
					IloLinearNumExpr xprHelperMin = cplex.linearNumExpr();
					xprHelperMax.addTerm(data.pmax[i] * data.broken[i][t],
							u[i][t]);
					xprHelperMin.addTerm(data.pmin[i] * data.broken[i][t],
							u[i][t]);
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
	 * composed of fuel costs for producing electric power and startup and
	 * shutdown costs of individual units over the given period<br>
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
				for (int j = 0; j < nGU; j++) {
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
					obj.addTerm(ls[i][t], 1);
				}
			}

			cplex.addMinimize(obj);
		} catch (IloException e) {
			e.printStackTrace();
		}
	}

	private void variableDeclaration() {
		class VarMaker {
			public IloNumVar[][] numVarArrayDef(int m, int n, int lowerBound,
					double upperBound, String varName) throws IloException {
				IloNumVar[][] var = new IloNumVar[nB][nT];
				for (int i = 0; i < m; i++) {
					for (int t = 0; t < n; t++) {
						var[i][t] = cplex.numVar(lowerBound, upperBound,
								varName + i + "." + t);
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

			p = new IloNumVar[nG][nGU][nT];
			for (int i = 0; i < nG; i++) {
				for (int j = 0; j < nGU; j++) {
					for (int t = 0; t < nT; t++) {
						p[i][j][t] = cplex.numVar(0, data.psegmax[i][j], "P"
								+ i + "." + j + "." + t);
					}
				}
			}

			ls = vm.numVarArrayDef(nB, nT, 0, Double.POSITIVE_INFINITY, "ls");
			dt = vm.numVarArrayDef(nB, nT, 0, Double.POSITIVE_INFINITY, "dt");
			ut = vm.numVarArrayDef(nB, nT, 0, Double.POSITIVE_INFINITY, "ut");
			sr = vm.numVarArrayDef(nB, nT, 0, Double.POSITIVE_INFINITY, "sr");
			or = vm.numVarArrayDef(nB, nT, 0, Double.POSITIVE_INFINITY, "or");
			
			flow = vm.numVarArrayDef(nB, nT, 0, Double.POSITIVE_INFINITY, "flow");
		} catch (IloException e) {
			e.printStackTrace();
		}
	}

	// private IloNumVar[][] numVarArrayDef(int m, int n, int lowerBound,
	// double upperBound, String varName) throws IloException {
	// IloNumVar[][] var = new IloNumVar[nB][nT];
	// for (int i = 0; i < m; i++) {
	// for (int t = 0; t < n; t++) {
	// var[i][t] = cplex.numVar(lowerBound, upperBound, varName + i + "." + t);
	// }
	// } return var;
	// }
	// private IloNumVar[][] boolVarArrayDef(int m, int n, String varName) {
	// IloNumVar[][] var = null;
	// try {
	// var = new IloNumVar[m][n];
	// for (int i = 0; i < m; i++) {
	// for (int t = 0; t < n; t++) {
	// var[i][t] = cplex.boolVar(varName + i + "." + t);
	// }
	// }
	// } catch (IloException e) {
	// e.printStackTrace();
	// }
	// return var;
	// }
	static class Data {
		// parameter declaration
		// <editor-fold defaultstate="collapsed" desc="Parameters">

		public static class lineItemsClass {
			int startNode;
			int endNode;
			double lineCapacity;
			double x;

			public lineItemsClass(int startNode, int endNode,
					double lineCapacity, double x) {
				super();
				this.startNode = startNode;
				this.endNode = endNode;
				this.lineCapacity = lineCapacity;
				this.x = x;
			}

		}

		lineItemsClass[] line;
		double[] demandHourlyTotal;
		double[][] demand;
		double[] percentload;

		/**
		 * Segment Generation Upper Limit for Convex Curves
		 */
		double[][] psegmax;
		double[][] cseg;

		double[][] broken;
		String brokenFile;

		// read from unit.txt
		/**
		 * Parameter <br>
		 * the bus number
		 */
		int [] bus;

		/**
		 * Parameter: <br>
		 * Lower limit of real power generation of unit i
		 */
		double[] pmin;// 2

		/**
		 * Parameter: <br>
		 * upper limit of real power generation of unit i
		 */
		double[] pmax;// 3

		/**
		 * <b>parameter: </b><br>
		 * cost of supplying the load<br>
		 * cost of generation
		 */
		double[] cnl;// 4 production cost

		/**
		 * parameter: shut down cost
		 */
		double[] sdc;// 5

		/**
		 * parameter:<br>
		 * start up cost
		 */
		double[] suc;// 6

		/**
		 * parameter:<br>
		 * minimum up time
		 */
		double[] mu;// 7

		/**
		 * parameter:<br>
		 * minumum down time
		 */
		double[] md;// 8
		double[] ru;// 9
		double[] rd;// 10

		/**
		 * 
		 * Parameter: <br>
		 * max unit spinning reserver
		 */
		double[] msr;// 11

		/**
		 * parameter:<br>
		 * quick start capability
		 */
		double[] qsc;// 12
		double[] laststat;// 13
		double[] mn;// 14 mn(i) = 24+unit(i,'14');
		double[] lastp;// 15

		/**
		 * Parameter: <br>
		 * minimum up time
		 */
		double[] mf;// 16 mf = 24

		/**
		 * Parameter: <br>
		 * required total system's spinning reserve at time t
		 */
		double[] ssr;

		/**
		 * Parameter: <br>
		 * required total system's operating reserve at time t
		 */
		double[] sor;

		// dc parameters:

		double[] maxFlow;

		double[] x;

		ArrayList<Integer>[] lineBus ;
		
		/**
		 * in the gen2bus wherever the bus is not a gu it is equal to -1 and 
		 * where bus is gu the row number of unit is returned
		 */
		int gen2bus [] ;
		
		
		private double[][] lineTempData;
		// </editor-fold>
		public Data(String caseName) {
			readData(caseName);
		}

		private void readData(String caseName) {
			try {
				if (caseName == "")
					caseName = "unit118bus.txt";
				System.out.println(caseName);
				String dataFile = "Data" + File.separator + caseName
				+ File.separator + "unit" + caseName + ".txt";
				InputDataReader reader = new InputDataReader(dataFile);
				bus = reader.readIntArray();
				pmin = reader.readDoubleArray();
				pmax = reader.readDoubleArray();
				cnl = reader.readDoubleArray();
				sdc = reader.readDoubleArray();
				suc = reader.readDoubleArray();
				mu = reader.readDoubleArray();
				md = reader.readDoubleArray();
				ru = reader.readDoubleArray();
				rd = reader.readDoubleArray();
				msr = reader.readDoubleArray();
				qsc = reader.readDoubleArray();
				laststat = reader.readDoubleArray();
				mn = reader.readDoubleArray();
				for (int i = 0; i < mn.length; i++) {
					mn[i] = 24 + mn[i];
				}
				lastp = reader.readDoubleArray();
				mf = reader.readDoubleArray();
				demandHourlyTotal = reader.readDoubleArray();
				percentload = reader.readDoubleArray();
				psegmax = reader.readDoubleArrayArray();
				cseg = reader.readDoubleArrayArray();

				lineTempData = reader.readDoubleArrayArray();
				ssr = reader.readDoubleArray();
				sor = reader.readDoubleArray();
				maxFlow = reader.readDoubleArray();
				x = reader.readDoubleArray();
				broken = readBroken();
				DisplayData.printArray(broken);
				
				calculateOtherData();
				
				

			} catch (IOException e) {
				e.printStackTrace();
			} catch (InputDataReaderException e) {
				e.printStackTrace();
			} catch (Exception e) {
				e.printStackTrace();
			}
		}

		private void calculateOtherData() {
			// TODO Auto-generated method stub

			int nB = percentload.length;
			int nL = lineTempData.length;
			int nG = bus.length;
			
			line = new lineItemsClass[nL];
			for (int l = 0; l < nL; l++) {
				int k1 = (int) lineTempData[l][0];
				int k2 = (int) lineTempData[l][1];
				line[l]=new lineItemsClass(k1, k2, lineTempData[l][2], lineTempData[l][3]);
			}
			
			lineBus = new ArrayList[nB];
			for (int b = 0; b < nB; b++)
				lineBus[b] = new ArrayList<Integer>();
			for (int l = 0; l < nL; l++) {
				lineBus[line[l].startNode-1].add(l);
				lineBus[line[l].endNode-1].add(-l);
			}
			 gen2bus = new int [nB];
			Arrays.fill(gen2bus, -1);
			for (int i=0;i<nG; i++)
			{
				gen2bus[bus[i]-1]=i;
			}

		}

		private double[][] readBroken() {
			double[][] matrix = null;
			ArrayList<String[]> strMat = new ArrayList<String[]>();
			try {
				String filePath = "Data" + File.separator + caseName
				+ File.separator + "Broken.txt";
				// String filePath="Data"+File.separator+"Broken.txt";
				File file = new File(filePath);

				if (file.exists()) {
					System.out.println(file.getAbsolutePath());
					System.out.println(file.canRead());
					System.out.println(file.getAbsoluteFile().exists());
				} else
					return null;
				FileReader fr = new FileReader(file);
				BufferedReader br = new BufferedReader(fr);
				String line = null;
				while ((line = br.readLine()) != null) {
					strMat.add(line.trim().split("\t"));
				}
				br.close();

				matrix = new double[strMat.size()][strMat.get(0).length];
				for (int i = 0; i < strMat.size(); i++)
					for (int j = 0; j < strMat.get(i).length; j++)
						matrix[i][j] = Double.parseDouble(strMat.get(i)[j]);
		
				demandTotalToBus();
				
				
				// System.out.println("it Exists");
			} catch (FileNotFoundException e) {
				e.printStackTrace();
			} catch (IOException e) {
				e.printStackTrace();
			}
			return matrix;
		}
		
		/**
		 * distributing the hourly total demand among different buses as the weight of percentload 
		 */
		private void demandTotalToBus() {
			Double [] plTemp = new Double [percentload.length];
			for (int b = 0; b < percentload.length; b++)
				plTemp[b] = new Double(percentload[b]);
			
			Double totalLoad = sum(plTemp);
			demand = new double [percentload.length][demandHourlyTotal.length];
			for (int t = 0; t < demandHourlyTotal.length; t++)
				for (int b=0; b<percentload.length; b++){
					demand[b][t]=demandHourlyTotal[t]*percentload[b]/totalLoad.doubleValue();
				}
		}

		private <E> E sum(E[] values){
			Double temp=new Double(0);
			for (E e:values){
				temp += ((Number) e).doubleValue();
			}
			return ((E) temp);
		}
	}

	/**
	 * flow = production -demand + load shedding
	 * con2dc(b,t).. utm(l, A(l,b)*flow(l,t))=e= pg1(b,t) - pd(b,t)+ LS(b,t);
	 */
	private void loadBalanceConstraint() {
		
		try {
			for (int t = 0; t < nT; t++) {
				
				IloRange[] flowBalance = new IloRange[nB];
				
				for (int b = 0; b < nB; b++) {
					IloLinearNumExpr xprHelperFlow = cplex.linearNumExpr();
					
					for (int ll=0; ll<data.lineBus[b].size(); ll++){
						int lineIndex = Math.abs(data.lineBus[b].get(ll));
						double flowDirection = Math.signum(data.lineBus[b].get(ll)); 
						xprHelperFlow.addTerm(flowDirection, flow[lineIndex][t]);
					}
					
					
					// checks if the bus is a generation unit or not 
					// in the gen2bus wherever the bus is not a gu it is equal to -1 and 
					// where bus is gu the row number of unit is returned
					if (data.gen2bus[b] != -1){

						for (int j = 0; j < nGU; j++) {
							xprHelperFlow.addTerm(-1, p[data.gen2bus[b]][j][t]);
						}
					}
					xprHelperFlow.addTerm(-1, ls[b][t]);
					flowBalance[b] = cplex.addEq(xprHelperFlow, data.demand[b][t],
							"PowerBalanceConstraint[" + b + "][" + t + "]");
					xprHelperFlow.clear();
				}
				constraints.add(flowBalance);
				
			}
		} catch (IloException ex) {
			Logger.getLogger(CopyOfUnitCommitment20162710.class.getName()).log(Level.SEVERE,
					null, ex);
		}

	}
}
