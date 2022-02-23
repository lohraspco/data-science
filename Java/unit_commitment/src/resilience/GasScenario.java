package resilience;

import java.io.File;
import java.io.FilenameFilter;

public class GasScenario {
	public int n;
	File [] gasFiles;
	public int counter=0;
	public GasScenario(String folder) {
		gasFiles = getGasScenFiles(folder);
		this.n = gasFiles.length;
	}
	
	public double[][] next(){
		double[][] gasscen=null;
		if (this.counter<this.n) {
			SCUCDataReader dr = new SCUCDataReader();
			gasscen = dr.read2DMatrix(gasFiles[this.counter++]);
		}
		return gasscen;
		
	}
	
	
	
	
	static File[] getGasScenFiles(String folder) {

		File gasFolder = new File("Data" + File.separator + folder + File.separator + "gasScenarios");
		File[] gasFiles = gasFolder.listFiles(new FilenameFilter() {

			@Override
			public boolean accept(File dir, String name) {
				return name.toLowerCase().contains("gas");
			}
		});
		return gasFiles;
	}
	public String toString(){
		return gasFiles[this.counter-1].getName();
		
	}

}
