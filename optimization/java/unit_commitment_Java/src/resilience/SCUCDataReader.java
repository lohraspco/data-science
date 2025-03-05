package resilience;

import inputOutput.InputDataReader;
import inputOutput.InputDataReader.InputDataReaderException;


import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;


public class SCUCDataReader {
	public static final int demandCoeff=1;

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

		
		String brokenFile;

		// read from unit.txt
		/**
		 * Parameter <br>
		 * the bus number
		 */
		int [] bus;


		/**
		 * the index of combined cycled generators
		 */
		int [] ccGenIndex;

		/**
		 * this contains the gas node corresponding a generator (bus) node
		 * This gas node supplies the corresponding generator  with gas
		 * for example gasNode={1, 1, 2} and ccGenIndex = {2, 4, 6} means that 
		 * gas node 1 supplies gas for generator at bus 2 and 4
		 * gas node 2 supplies gas for generator at bus 6}
		 */
		int [] gasNodeID;


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
		double[] minDownTime;// 8
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

		/**
		 * Parameter: <br>
		 * big m to set the value of up time to zero if the corresponding unit is off
		 */
		double[] bigMUPTime;// 14 mn(i) = 24+unit(i,'14');
		double[] lastp;// 15

		/**
		 * Parameter: <br>
		 * big m to set the value of down time to zero if the corresponding unit is on
		 */
		double[] bigMDownTime;// 16 mf = 24

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

		/**
		 * x[l]<br>
		 *array for line data
		 */
		double[] x;

		/**
		 * for each bus if line l enters then the -L (negative of the line number index) is added to that bus array list<br>
		 * if line l leaves then the L (the line number index)is added to that bus array list <br>
		 * linebus indices are from 0 to nL-1 to comply with array index
		 *  
		 */
		ArrayList<Integer>[] lineBus ;

		/**
		 * in the gen2bus wherever the bus is not a gu it is equal to -1 and 
		 * where bus is gu the row number of unit is returned
		 */
		int gen2bus [] ;

		int[] genMttr;
		int[] lineMttr;
		
	
		
		private double[][] lineTempData;
		// </editor-fold>
		public Data(String caseName) {
			readData(caseName);
		}

		private void readData(String caseName) {
			try {
				if (caseName == "")
					caseName = "unitData.txt";
				System.out.println("thread: "+Thread.currentThread().getId()+  caseName + " \t "  );
				String dataFile = "Data" + File.separator + caseName
				+ File.separator +  "unitData.txt";

				InputDataReader reader = new InputDataReader(dataFile);
				bus = reader.readIntArray();
				pmin = reader.readDoubleArray();
				pmax = reader.readDoubleArray();
				cnl = reader.readDoubleArray();
				sdc = reader.readDoubleArray();
				suc = reader.readDoubleArray();
				mu = reader.readDoubleArray();
				minDownTime = reader.readDoubleArray();
				ru = reader.readDoubleArray();
				rd = reader.readDoubleArray();
				msr = reader.readDoubleArray();
				qsc = reader.readDoubleArray();
				laststat = reader.readDoubleArray();
				bigMUPTime = reader.readDoubleArray();
				for (int i = 0; i < bigMUPTime.length; i++) {
					bigMUPTime[i] = 24 + bigMUPTime[i];
				}
				lastp = reader.readDoubleArray();
				bigMDownTime = reader.readDoubleArray();
				demandHourlyTotal = reader.readDoubleArray();
				percentload = reader.readDoubleArray();
				psegmax = reader.readDoubleArrayArray();
				cseg = reader.readDoubleArrayArray();

				lineTempData = reader.readDoubleArrayArray();
				ssr = reader.readDoubleArray();
				sor = reader.readDoubleArray();
				maxFlow = reader.readDoubleArray();
				x = reader.readDoubleArray();
				ccGenIndex = reader.readIntArray();
				gasNodeID = reader.readIntArray();
				genMttr = reader.readIntArray();
				
				
				
				lineMttr = reader.readIntArray();
				

				//DisplayData.printArray(broken);

				
				demandTotalToBus();
				calculateOtherData();
				



			} catch (IOException e) {
				e.printStackTrace();
			} catch (InputDataReaderException e) {
				e.printStackTrace();
			} catch (Exception e) {
				e.printStackTrace();
			}
		}

		@SuppressWarnings("unchecked")
		private void calculateOtherData() {

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
				lineBus[line[l].startNode-1].add(l+1);
				lineBus[line[l].endNode-1].add(-(l+1));
			}
			gen2bus = new int [nB];
			Arrays.fill(gen2bus, -1);
			for (int i=0;i<nG; i++)
			{
				gen2bus[bus[i]-1]=i;
			}

		}



		/**
		 * distributing the hourly total demand among different buses as the weight of percentload 
		 */
		private void demandTotalToBus() {
//			Double [] plTemp = new Double [percentload.length];
			//create a type to pass to the generic function sum
			// old data types cannot be passed to a generic class or function
			double totalLoad=0;
			for (int b = 0; b < percentload.length; b++){
				totalLoad +=percentload[b];
				System.out.println(percentload[b]);
//				plTemp[b] = new Double(percentload[b]);
			}

//			Double totalLoad = sum(plTemp);
			System.out.println(totalLoad);
			demand = new double [percentload.length][demandHourlyTotal.length];
			for (int b=0; b<percentload.length; b++){
				for (int t = 0; t < demandHourlyTotal.length; t++){

					demand[b][t]=demandCoeff*demandHourlyTotal[t]*percentload[b]/totalLoad;
					System.out.println(demandHourlyTotal[t]);
				}
			}
		}

		@SuppressWarnings("unchecked")
		private <E> E sum(E[] values){
			Double temp=new Double(0);
			for (E e:values){
				temp += ((Number) e).doubleValue();
			}
			return ((E) temp);
		}
	}
	public double[][] read2DMatrix( File sourceFile) {
		double[][] matrix = null;
		ArrayList<String[]> strMat = new ArrayList<String[]>();
		try {
//			System.out.println(sourceFile.getName());
			FileReader fr = new FileReader(sourceFile);
			BufferedReader br = new BufferedReader(fr);
			String line = null;
			while ((line = br.readLine()) != null) {
				strMat.add(line.trim().split("\t"));
			}
			br.close();
			int B = strMat.size();
			int T = strMat.get(0).length;
			matrix = new double[B][T];
			for (int i = 0; i < B; i++)
				for (int j = 0; j < T; j++)
					matrix[i][j] = Integer.parseInt(strMat.get(i)[j].trim());

			


			// System.out.println("it Exists");
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return matrix;
	}
}
