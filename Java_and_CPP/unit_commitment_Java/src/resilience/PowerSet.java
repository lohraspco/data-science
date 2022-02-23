package resilience;

import java.util.HashSet;
import java.util.Set;

/***
 * receives a number indicating the number of elements in a set then producing
 * the index from it for the subsets implemented as generator
 * 
 * @author User
 *
 */
public class PowerSet {
	private int binarySubset = 0;
	public final int numberOfElemenets;
	public final int totalNumberOfSubsets;

	public PowerSet(int numberofElements) {
		this.numberOfElemenets = numberofElements;
		this.totalNumberOfSubsets = 1 << numberofElements;
	}

	public Integer[] nextSubset() {
		Set<Integer> subset = new HashSet();

		if (binarySubset<this.totalNumberOfSubsets) {
			for(int i=0; i<this.numberOfElemenets;i++) {
				int mask = 1<<i;
				if ((binarySubset & mask) != 0)
					subset.add(i);
			}
		}
		Integer [] fin = (Integer[]) subset.toArray();
		return fin;

	}

	public <T> Set<Set<T>> powerSetGenerator(Set<T> set) {
		@SuppressWarnings("unchecked")
		T[] elements = (T[]) set.toArray();
		Set<Set<T>> powerset = new HashSet<Set<T>>();
		final int totalSubsets = 1 << elements.length;
		for (int binarySet = 0; binarySet < totalSubsets; binarySet++) {
			Set<T> subset = new HashSet<T>();
			for (int bit = 0; bit < elements.length; bit++) {

				// (1<<bit) is a number with jth bit 1. so when we & them with the
				// subset number we get which numbers are present in the subset
				int mask = 1 << bit;
				if ((binarySet & mask) != 0)
					subset.add(elements[bit]);
			}
			powerset.add(subset);
		}
		return powerset;

	}

	public static void main(String[] args) {

		int j = 3;
		System.out.println(1 << j);
		Set<String> items = new HashSet<String>();
		items.add("a1");
		items.add("b2");
		items.add("c3");

		PowerSet cis = new PowerSet(3);
		Set<Set<String>> results = cis.powerSetGenerator(items);
		System.out.print(results);
	}

}
