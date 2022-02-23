package blockchain;

import java.util.Date;

public class Block {
	public String hash;
	public String previousHash;
	private String data; // here a simple message
	private long timeStamp; // number of millisecondssince 1/1/1970
	private int nonce;
	public Block(String data, String previousHash) {
		this.data = data;
		this.previousHash = previousHash;
		this.timeStamp = new Date().getTime();
		this.hash = calculateHash();
	}

	public String calculateHash() {
		String calculatedHash = StringUtil.applySha256(previousHash + Long.toString(timeStamp)+Integer.toString(nonce));
		return calculatedHash;
	}
	public void mineBlock(int difficulty) {
		String target = new String(new char[difficulty]).replace('\0','0'); //Create a string with difficulty * "0"
		while(!hash.substring(0,difficulty).equals(target)) {
			nonce++;
			hash=calculateHash();
		}
		System.out.println("Block mined!!! : "+ hash);
	}
}
