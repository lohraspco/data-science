package inputOutput;

import java.util.ArrayList;

public class DisplayData {
	public static  void printArray(double[] arr) {
		for (int i=0; i < arr.length; i++)
		{
			System.out.print(arr[i]+"\t");
		}
	}
	public static void printArray(double[][] arr) {
		// TODO Auto-generated method stub
		for (int i=0; i < arr.length; i++)
		{
			printArray(arr[i]);
			System.out.println();
		}
	}
	public static void printArraylist(ArrayList<String> s){
		for (String e:s)
			System.out.print(e + "\t");
		System.out.println();
	}
}
