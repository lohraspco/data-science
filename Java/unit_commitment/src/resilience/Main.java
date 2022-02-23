package resilience;

import java.awt.BorderLayout;

import javax.swing.JFrame;
import javax.swing.JPanel;

public class Main extends JFrame{
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	public static void main(String [] args){
		Main m = new Main();
		
	}
	
	JFrame frame;
	JPanel panel;
	Main(){
		frame = new JFrame("Resilience Metric");
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		panel = new JPanel();
		panel.setSize(500, 500);
		frame.getContentPane().add(panel, BorderLayout.CENTER);
		frame.setSize(300,300);
		
		frame.setVisible(true);
	}
	

}
