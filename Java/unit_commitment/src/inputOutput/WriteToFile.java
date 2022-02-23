package inputOutput;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

public class WriteToFile {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub

	}

	public static void write(double[][] matrix, String filePath) throws FileNotFoundException {
		String fileName = filePath;
		fileName = fileName.substring(0, fileName.length() - 4) + ".csv";
		PrintWriter pw = new PrintWriter(new File(fileName));
		for (int i = 0; i < matrix.length; i++) {
			pw.write(i + ",");
			for (int j = 0; j < matrix[i].length; j++) {
				pw.write(Double.toString(matrix[i][j]) + ",");
			}
			pw.println();
		}
		pw.close();
	}

	public static void writeDetailHeader(String outputDirectory, String filename,
			int nT,int id) throws IOException {
		String filePath = outputDirectory +File.separator+filename+id+ "detail.csv";
		FileWriter fw = new FileWriter(filePath, true);
		BufferedWriter bw = new BufferedWriter(fw);
		PrintWriter pw = new PrintWriter(bw);

		pw.write("counter, absorption, recovery,IOLen ,genScenID,");
		for (int i = 0; i < nT; i++) 
			pw.write("dst" + i + ",");
		
	}
	public static void writeDetails(double objective, double[][] matrixLS, double[][] matrixDemand, String filePath,
			String filename,  int objCounter, String genScenarioID) throws IOException {
		filePath = filePath +File.separator+"details"+File.separator+filename+"_"+objCounter+ "detail.csv";

		FileWriter fw = new FileWriter(filePath, true);
		BufferedWriter bw = new BufferedWriter(fw);
		PrintWriter pw = new PrintWriter(bw);
		pw.write("counter, absorption, recovery ,IOLen,genScenID,, objective");
		for (int i = 0; i < matrixDemand[0].length; i++) 
			pw.write("dst" + i + ",");
		for (int r = 0; r < matrixDemand.length; r++) {

			pw.write("" + objCounter  + genScenarioID + "," + objective+",");

			for (int t = 0; t < matrixDemand[r].length; t++) {
				pw.write(Double.toString(matrixDemand[r][t] - matrixLS[r][t]) + ",");
			}
			pw.write("\n");

		}
		pw.println();

		pw.close();
	}

//	public static void writeSummary(double objective, double[][] matrixLS, double[][] matrixDemand, String filePath,
//			String dateandScenario) throws IOException {
//		String filePath1 = filePath + "detail.csv";
//		filePath = filePath + ".csv";
//
//		FileWriter fw = new FileWriter(filePath, true);
//		BufferedWriter bw = new BufferedWriter(fw);
//		PrintWriter pw = new PrintWriter(bw);
//
//		double[] totalHourlyLS = sumCol(matrixLS);
//		double[] totalHourlyDemand = sumCol(matrixDemand);
//
//		pw.write(dateandScenario + "," + objective);
//
//		pw.write(", , demandSatisfied, ");
//		for (int i = 0; i < totalHourlyDemand.length; i++) {
//			pw.write(Double.toString(totalHourlyDemand[i] - totalHourlyLS[i]) + ",");
//		}
//
//		pw.write(", , demand,");
//		for (int i = 0; i < totalHourlyDemand.length; i++) {
//			pw.write(Double.toString(totalHourlyDemand[i]) + ",");
//		}
//
//		pw.write(", , ls, ");
//		for (int i = 0; i < totalHourlyLS.length; i++) {
//			pw.write(Double.toString(totalHourlyLS[i]) + ",");
//		}
//
//		pw.println();
//
//		pw.close();
//	}

//	public static void writeSummary(double objective, double numberOfGens, double numberOfOperableGens,
//			double[][] matrixLS, double[][] matrixDemand, String filePath, String dateandScenario) throws IOException {
//
//		filePath = filePath + ".csv";
//
//		FileWriter fw = new FileWriter(filePath, true);
//		BufferedWriter bw = new BufferedWriter(fw);
//		PrintWriter pw = new PrintWriter(bw);
//
//		double[] totalHourlyLS = sumCol(matrixLS);
//		double[] totalHourlyDemand = sumCol(matrixDemand);
//
//		pw.write(dateandScenario + "," + objective);
//		pw.write("," + numberOfGens + "," + numberOfOperableGens + ",");
//
//		pw.write(", , demandSatisfied, ");
//		for (int i = 0; i < totalHourlyDemand.length; i++) {
//			pw.write(Double.toString(totalHourlyDemand[i] - totalHourlyLS[i]) + ",");
//		}
//
//		pw.write(", , demand,");
//		for (int i = 0; i < totalHourlyDemand.length; i++) {
//			pw.write(Double.toString(totalHourlyDemand[i]) + ",");
//		}
//
//		pw.write(", , ls, ");
//		for (int i = 0; i < totalHourlyLS.length; i++) {
//			pw.write(Double.toString(totalHourlyLS[i]) + ",");
//		}
//
//		pw.println();
//
//		pw.close();
//	}

	public static double[] sumCol(double[][] matrix) {
		double[] summary = new double[matrix[0].length];
		for (int i = 0; i < matrix.length; i++) {
			for (int j = 0; j < matrix[i].length; j++) {
				summary[j] += matrix[i][j];
			}
		}
		return summary;
	}

	/**
	 * main writesmmary
	 * 
	 * @param objValue
	 * @param weightedCount
	 * @param weightedSum
	 * @param lsVals
	 * @param demand
	 * @param outputDirectory
	 * @param caseName2
	 * @param genScenarioID
	 * @param gasScenarioID
	 * @param ucCounter
	 * @throws IOException
	 */
	public static void writeSummary(double objValue, double weightedCount, double weightedSum, double[][] lsVals,
			double[][] demand, String outputDirectory, String caseName2, String genScenarioID, String gasScenarioID,
			String ucCounter) throws IOException {
		/*
		 * double objective,double numberOfGens, double numberOfOperableGens, double
		 * [][] matrixLS, double [][] matrixDemand, String filePath, String
		 * dateandScenario
		 */
		outputDirectory = outputDirectory + File.separator + caseName2 + ".csv";
		FileWriter fw = new FileWriter(outputDirectory, true);
		BufferedWriter bw = new BufferedWriter(fw);
		PrintWriter pw = new PrintWriter(bw);

		double[] totalHourlyLS = sumCol(lsVals);
		double[] totalHourlyDemand = sumCol(demand);

		pw.write(ucCounter + genScenarioID +  gasScenarioID + "," + objValue);
		pw.write("," + weightedCount + "," + weightedSum + ",");

//		pw.write(", demandSatisfied, " + gasScenarioID + ",");
		for (int i = 0; i < totalHourlyDemand.length; i++) {
			pw.write(Double.toString(totalHourlyDemand[i] - totalHourlyLS[i]) + ",");
		}

//		pw.write(", demand,");
		for (int i = 0; i < totalHourlyDemand.length; i++) {
			pw.write(Double.toString(totalHourlyDemand[i]) + ",");
		}

//		pw.write(", ls, ");
		for (int i = 0; i < totalHourlyLS.length; i++) {
			pw.write(Double.toString(totalHourlyLS[i]) + ",");
		}

		pw.println();

		pw.close();

	}

	public static void writeHeader(String outputDirectory, String caseName2, int T) throws IOException {
//		double objValue, double weightedCount, double weightedSum, double[][] lsVals,
//		double[][] demand,  String genScenarioID, String gasScenarioID,
//		String dateFoldName
		/*
		 * double objective,double numberOfGens, double numberOfOperableGens, double
		 * [][] matrixLS, double [][] matrixDemand, String filePath, String
		 * dateandScenario
		 */
		outputDirectory = outputDirectory + File.separator + caseName2 + ".csv";
		FileWriter fw = new FileWriter(outputDirectory, true);
		BufferedWriter bw = new BufferedWriter(fw);
		PrintWriter pw = new PrintWriter(bw);

		pw.write("counter, absorption, recovery, ioCount , genScenarioID  , gasScen, objValue");
		pw.write(", weightedCount , weightedSum ,");

//		pw.write(", demandSatisfied,  gasScenarioID ,");
		for (int i = 0; i < T; i++) {
			pw.write("dst" + i + ",");
		}

//		pw.write(", demand,");
		for (int i = 0; i < T; i++) {
			pw.write("dt" + i + ",");
		}

//		pw.write(", ls, ");
		for (int i = 0; i < T; i++) {
			pw.write("lst" + i + ",");
		}

		pw.println();

		pw.close();

	}

	public static void writeLog(String s) {
		FileWriter fw;
		try {
			fw = new FileWriter("output" + File.separator + "LOG.txt", true);
			BufferedWriter bw = new BufferedWriter(fw);
			PrintWriter pw = new PrintWriter(bw);
			pw.println(s);

			pw.close();
			bw.close();
			fw.close();

		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}

}
