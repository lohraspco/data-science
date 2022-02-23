/*
Mixed integer stochastic bilevel programming for optimal bidding
strategies in day-ahead electricity markets with indivisibilities


Stochastic 
minimize cT x +sigma(k=1 to s)[pk qTk yk]
subject to Ax = b ; T kx +W yk = hk ; 

At the first stage we optimize (minimize) the cost CT x of the first-stage decision plus the 
expected cost of the (optimal) second stage decision. We can view the second-stage problem 
simply as an optimization problem which describes onr supposedly optimal behavior when 
the uncertain data is revealed, or we can consider its solution as a recourse action where the 
term Wy compensates for a possible inconsistency of the system TT h and qTy is the cost 
of this recourse action. 
*/
/*
Bilevel stochastic
*/

#include <vector>
#include <windows.h>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>//str at
#include <stdlib.h> //atod
#include <ilcplex\ilocplex.h>
ILOSTLBEGIN 

#define EPSILON 1e-6
#define maxNumberOfIteration 40

void mixedIntegerSubProblem(IloNum p1, 	IloArray <IloNumArray> &primalValues, IloNumArray &primalStartups, IloNum &objectiveValue);
void LPSubProblem(IloNum p1, IloArray <IloNumArray> &primalValues, IloNumArray primalStartups, IloNumArray &dualValues, IloNum &objectiveValue);
bool isEqual(IloArray< IloNumArray> arr1, IloArray < IloNumArray> arr2);
int lineSearch (IloNum p1Min, IloNum p1Max);
void shadowPriceCheck(void);
void printVector2D(vector<vector<double>> A);
void inputData ();
int GetFileList(const char *searchkey, std::vector<std::string> &list);
string  getPathFile();
void readDataFromFile(string pathFile);
vector<string> get_all_files_names_within_folder(string folder);
bool ListDirectoryContents(const wchar_t *sDir);

//global variable definition
IloEnv env;
IloInt NumberOfScenarios, NumberOfParticipants;// data for participants include the data for the individual of interest
//data for the individual of interest is stored in first place of the array
IloNumArray prob(env); // the probability
IloArray <IloNumArray> price(env); // the bid price of competitors for in different NumberOfScenarioss
IloNum p1LowerBound; //Variable cost of the individual producer, i.e. of unit 1
IloNum p1UpperBound; // Price cap for the energy offer
IloNumArray s(env); // start  up cost 
IloNumArray D(env);//stochastic Demand
IloNumArray QMax(env), QMin(env); //Technical maximum and minimum of unit generation 

IloArray <IloNumArray> bestP1Record(env);
int iterationCounter;
IloArray <IloArray <IloNumArray>> xStar(env);
vector <vector<double>> optimumRecord;
vector <vector<double>> PrimalValuesRecord;
vector <vector<double>> DualValuesRecord;
vector <vector<double>> finalDecision;

// the column in optimumRecord in which the value for p1Star for that interval is located
//the columns strart from 0
const  int p1StarColInOptRecVect=2;
const  int p1MaxColNum=1;

void main (void)
{
	inputData();
	//const char* fileName = "dataStochastic.dat"; 
	const char* fileName = "dataStochastic 2.dat"; 
	
	iterationCounter=0;
	lineSearch (p1LowerBound, p1UpperBound);
	
	shadowPriceCheck();

	cout  << endl << endl << "optimum Q" << endl;
	
	printVector2D (optimumRecord);

	cout << endl << endl<< "dual Values " << endl;
	printVector2D (DualValuesRecord);
	//cout<<endl<< "primal Values: " << endl;
	//printVector2D(PrimalValuesRecord);
	//cout << " best p1 value " << bestP1Record << endl;

		cout << endl << endl<< "finalDecision Values " << endl;
	printVector2D (finalDecision);
	system("pause");
}

int lineSearch (IloNum p1Min, IloNum p1Max)
{
	iterationCounter++;
	//IloEnv env;
	cout << "#################################################################" << endl;
	cout << "iteration: " << iterationCounter << endl; 
	try{


		// calculating the subproblem optimal for p1=p1min in first iteration c1
		IloNum objP1Min,  objP1MinLP;
		IloArray <IloNumArray> primalValuesP1Min(env, NumberOfScenarios);
		IloArray <IloNumArray> primalValuesP1MinLP(env, NumberOfScenarios);
		IloNumArray primalStartupsC1(env);
		IloNumArray dualValuesP1Min(env);
		/*primalStartupsC1.clear();
		primalValuesP1Min.clear();*/
		env.out() <<"************************************************************" << endl;
		env.out() << "iteration for fixed p=" << p1Min << endl;

		mixedIntegerSubProblem(p1Min, primalValuesP1Min, primalStartupsC1, objP1Min);
		if (primalStartupsC1.getSize() <1)
		{
			env.out() << " primal startups c1 " << primalStartupsC1;
		}
		LPSubProblem(p1Min, primalValuesP1MinLP, primalStartupsC1, dualValuesP1Min, objP1MinLP);

		// calculating the subproblem optimal for p1=p1max
		IloNum  objP1Max, objP1MaxLP;
		IloArray <IloNumArray> primalValuesP1Max(env, NumberOfScenarios);
		IloArray <IloNumArray> primalValuesP1MaxLP(env, NumberOfScenarios);
		IloNumArray primalStartupsP1Max(env);
		env.out() << "************************************************************" << endl;
		env.out() << "iteration for fixed p = " << p1Max << endl;
		env.out() << " primal startups primalStartupsP1Max " << primalStartupsP1Max;
		
		/*primalValuesP1Max.clear();
		primalStartupsP1Max.clear();*/
		mixedIntegerSubProblem( p1Max, primalValuesP1Max, primalStartupsP1Max, objP1Max);
		env.out() << " primal startups primalStartupsP1Max " << primalStartupsP1Max;
		if (primalStartupsP1Max.getSize() <1)
		{
			env.out() << " primal startups primalStartupsP1Max " << primalStartupsP1Max;
		}
	
		IloNumArray dualValuesP1Max(env);
		dualValuesP1Max.clear();
		LPSubProblem(  p1Max, primalValuesP1MaxLP, primalStartupsP1Max , dualValuesP1Max, objP1MaxLP );

		env.out() << "primal values P1 Max: " << primalValuesP1MaxLP << endl;
		env.out() << "primal values P1 Max: " << primalValuesP1MaxLP << endl;
		//system("pause");
		bool areSolutionsEqual=isEqual(primalValuesP1Min , primalValuesP1Max);
		env.out() << "the solutions are equal? " << areSolutionsEqual <<endl;
		if (areSolutionsEqual==true)
		{
			//this interavl is done and the optimal solution for lower level problem is the same for all p1 values
			/*bestP1Record.add(IloNumArray (env,5));
			bestP1Record[bestP1Record.getSize()-1][0]=p1Min;
			bestP1Record[bestP1Record.getSize()-1][1]=p1Max;
			bestP1Record[bestP1Record.getSize()-1][2]=p1Min;
			bestP1Record[bestP1Record.getSize()-1][3]=p1Max;*/
			//bestP1Record[bestP1Record.getSize()-1][4]=objP1Max;

			vector <double> temp, tempDual;
			temp.push_back(p1Min);
			temp.push_back(p1Max);
			temp.push_back(p1Min);
			temp.push_back(p1Max);
			temp.push_back(objP1Max);
			for (int i=0;i<NumberOfScenarios ; i++)
			{
				temp.push_back(primalValuesP1Max[i][0]);
				tempDual.push_back(dualValuesP1Max [i]);
			}
			optimumRecord.push_back(temp );
			DualValuesRecord.push_back(tempDual);
			temp.clear();
			tempDual.clear();

			return 1;
		}
		else
		{
			IloNum objValueP1min;// the objectvive value for itereation in which p1 is variable
			IloNum Q1ExpectedP1Min=0;
			env.out() << "primal Values p1min" << primalValuesP1Min << endl;
			for (int i=0; i<NumberOfScenarios ;i++)
				Q1ExpectedP1Min += prob[i] * primalValuesP1Min[i][0];
			objValueP1min = objP1Min - p1Min * Q1ExpectedP1Min; //it is b in ax+b

			IloNum objValueP1max;
			IloNum Q1ExpectedP1Max=0;
			env.out() << "primal Values p1max" << primalValuesP1Max  << endl;
			for (int i=0;i<NumberOfScenarios ; i++)
				Q1ExpectedP1Max += prob[i] * primalValuesP1Max[i][0];
			objValueP1max = objP1Max  - p1Max * Q1ExpectedP1Max;//it is b in ax+b

			/*		it was just for test in the middle of programming
			areSolutionsEqual=isEqual(primalValuesP1Min , primalValuesP1Max);
			cout << endl << endl;
			cout << "areSolutionsEqual " << areSolutionsEqual << endl << endl;*/

			double intersection;
			if (abs(Q1ExpectedP1Min - Q1ExpectedP1Max) < EPSILON)//see if division by zero happens
			{
				cout << " division by zero in calculating the intersection" << endl;
			}
			else
			{
				intersection = (objValueP1max - objValueP1min )/(Q1ExpectedP1Min - Q1ExpectedP1Max);//calculate the intersection of two lines

				//calculate the value of the two line y=ax+b
				IloNum intersectionObjectiveValue = objValueP1max + intersection * Q1ExpectedP1Max;
				//IloNum intersectionObjectiveValue1 = objValueP1min + intersection * Q1ExpectedP1Min;
				//cout<<  "intersectionObjectiveValue1 == intersectionObjectiveValue " << (intersectionObjectiveValue1 == intersectionObjectiveValue) << endl;

				cout <<  "	c1: " << p1Min << "	intersection: " << intersection << "	P1max: " << p1Max << endl;
				env.out() << "trimmed objValueC1 " << objValueP1min << "	trimmed objValueP1max: "<< objValueP1max  <<endl;
				env.out() << "trimmed Q1ExpectedC1 " << Q1ExpectedP1Min <<"	trimmed Q1ExpectedP1Max: "<< Q1ExpectedP1Max  <<endl;

				env.out() << "objective value C1: " << objP1Min << "   " << objP1MinLP << endl;
				env.out() << "Objective value p1Max: " << objP1Max << "    " << objP1MaxLP << endl;

				if (abs(intersection-p1Min) < EPSILON)
				{
					//the p1Min is optimal
					/*			bestP1Record.add(IloNumArray (env,4));
					bestP1Record[bestP1Record.getSize()-1][0]=p1Min;
					bestP1Record[bestP1Record.getSize()-1][1]=p1Max;
					bestP1Record[bestP1Record.getSize()-1][2]=p1Min;
					bestP1Record[bestP1Record.getSize()-1][3]=p1Min;*/
					//		bestP1Record[bestP1Record.getSize()-1][4]=objP1Min ;

					vector <double> temp;
					vector <double> tempDual;
					temp.push_back(p1Min);
					temp.push_back(p1Max);
					temp.push_back(p1Min);
					temp.push_back(p1Min);
					temp.push_back(objP1Min);
					for (int i=0;i<NumberOfScenarios ; i++)
					{
						temp.push_back(primalValuesP1Min[i][0]);
						tempDual.push_back(dualValuesP1Min[i]);
					}
					optimumRecord.push_back(temp );
					DualValuesRecord.push_back(tempDual);
					temp.clear ();
					tempDual.clear();
					return 1;
				}
				else if (abs(intersection - p1Max ) < EPSILON)
				{
					/*			bestP1Record.add(IloNumArray (env,4));
					bestP1Record[bestP1Record.getSize()-1][0]=p1Min;
					bestP1Record[bestP1Record.getSize()-1][1]=p1Max;
					bestP1Record[bestP1Record.getSize()-1][2]=p1Max;
					bestP1Record[bestP1Record.getSize()-1][3]=p1Max;*/
					//	bestP1Record[bestP1Record.getSize()-1][4]=objP1Max ;
					vector <double> temp;
					vector <double> tempDual;
					temp.push_back(p1Min);
					temp.push_back(p1Max);
					temp.push_back(p1Max);
					temp.push_back(p1Max);
					temp.push_back(objP1Max);
					for (int i=0;i<NumberOfScenarios ; i++)
					{
						temp.push_back(primalValuesP1Max[i][0]);
						tempDual.push_back(dualValuesP1Max [i]);
					}
					optimumRecord.push_back(temp );
					DualValuesRecord.push_back(tempDual);
					temp.clear ();
					tempDual.clear();

					return 1;
				}
				else
				{

					IloArray <IloNumArray> primalValuesTeta(env, NumberOfScenarios);
					IloNumArray primalStartupsTeta(env);
					IloNum objTeta;
					mixedIntegerSubProblem( intersection, primalValuesTeta, primalStartupsTeta, objTeta);

					if (abs(intersectionObjectiveValue - objTeta) < EPSILON)
					{
						//this interval is done the optimal solution for c1<p1<teta is c1   
						/*bestP1Record.add(IloNumArray (env,4));
						bestP1Record[bestP1Record.getSize()-1][0]=p1Min;
						bestP1Record[bestP1Record.getSize()-1][1]=intersection;
						bestP1Record[bestP1Record.getSize()-1][2]=p1Min;
						bestP1Record[bestP1Record.getSize()-1][3]=p1Min;*/
						//		bestP1Record[bestP1Record.getSize()-1][4]=objP1Min ;
						vector <double> temp;
						vector <double> tempDual;
						temp.push_back(p1Min);
						temp.push_back(intersection);
						temp.push_back(p1Min);
						temp.push_back(p1Min);
						temp.push_back(objP1Min);
						for (int i=0;i<NumberOfScenarios ; i++)
						{
							temp.push_back(primalValuesP1Min [i][0]);
							tempDual.push_back(dualValuesP1Min [i]);
						}
						optimumRecord.push_back(temp );
						DualValuesRecord.push_back(tempDual);
						temp.clear ();
						tempDual.clear();

						//this interval is done the optimal solution ofr teta < p1 < p1max is p1max
						/*	bestP1Record.add(IloNumArray (env,4));
						bestP1Record[bestP1Record.getSize()-1][0]=intersection;
						bestP1Record[bestP1Record.getSize()-1][1]=p1Max;
						bestP1Record[bestP1Record.getSize()-1][2]=p1Max;
						bestP1Record[bestP1Record.getSize()-1][3]=p1Max;*/
						//	bestP1Record[bestP1Record.getSize()-1][4]=objP1Max ;
						vector <double> tempDual1;
						vector <double> temp1;
						temp1.push_back(intersection);
						temp1.push_back(p1Max);
						temp1.push_back(p1Max);
						temp1.push_back(p1Max);
						temp1.push_back(objP1Max);
						for (int i=0;i<NumberOfScenarios ; i++)
						{
							temp1.push_back(primalValuesP1Max[i][0]);
							tempDual1.push_back(dualValuesP1Max [i]);
						}
						//cout << endl << endl << endl;
						//env.out() << "errrrooooorrrr primalValuesP1Max " << primalValuesP1Max << endl;
						optimumRecord.push_back(temp1 );
						DualValuesRecord.push_back(tempDual1);
						temp1.clear ();
						tempDual1.clear();
						return 1;
					}
					else
					{
						if (iterationCounter < maxNumberOfIteration)
						{
							lineSearch (p1Min, intersection);
							lineSearch (intersection , p1Max);
						}
					}


					cout << "objective Teta : " << objTeta <<endl ;
				}
			}

		}
		//system("pause");


	}//end try
	catch (IloException &e)	{
		env.out()<<"Error: "<<e<<endl;
	}//end catch iloexception
	catch (std::exception &e){
		std::cerr << "standard exception: " << e.what() << endl;
	}//end catch std exception
	catch (...){
		env.out()<<"Unknown error"<<endl;
	}//end catch exception
}//end main

void shadowPriceCheck(void)
{
	vector <double> temp;
	for (unsigned int i=0; i<optimumRecord.size() ; i++)
	{
		for (int j=0; j<DualValuesRecord[i].size(); j++)
		{
			if ( abs ( optimumRecord[i][p1StarColInOptRecVect] - DualValuesRecord[i][j] ) < EPSILON)
			{
				//in this case the shadow price is equal to the price of individual producer
				temp.push_back(optimumRecord[i][p1MaxColNum]);
			}
			else
			{
				temp.push_back(optimumRecord[i][p1StarColInOptRecVect]);
			}
			
		}
		finalDecision.push_back(temp);
			temp.clear();
	}
}

void mixedIntegerSubProblem( IloNum p1, IloArray <IloNumArray> &primalValues, IloNumArray &primalStartups, IloNum &objectiveValue)
{

	try
	{
		IloModel model(env);

		//decision variables
		IloBoolVarArray u(env, NumberOfParticipants);//Binary variable that takes the value 1 if unit g produces a positive energy quantity, and 0 otherwise
		IloArray <IloNumVarArray> Q(env, NumberOfScenarios);//the amount that will be provided by each producer
		for (int i = 0; i < NumberOfScenarios ; i++){
			Q[i] = IloNumVarArray (env, NumberOfParticipants);
			for(int j = 0; j < NumberOfParticipants; j++)
				Q[i][j] = IloNumVar(env, QMin[j], QMax[j], ILOFLOAT );
		}
		// generating objective function
		IloExpr SecondLevelObjectiv(env);//expression to construct the second level objectvie
		SecondLevelObjectiv += IloScalProd (s,u);
		for (int i = 0; i < NumberOfScenarios; i++)
		{
			SecondLevelObjectiv += prob[i] * p1 * Q[i][0];// we use the algorithm in the paper, so we put p1 
			for (int j = 1; j < NumberOfParticipants; j++)//j starts from 1 because the first one is not stochastic
				SecondLevelObjectiv += prob[i] * price[i][j] * Q[i][j];
			// we have to revise this part
		}
		IloRangeArray constraints(env);
		for (int i = 0; i < NumberOfScenarios; i++)
		{
			IloExpr LHS(env);//left hand side of the constraints
			for ( int j = 0; j < NumberOfParticipants; j++)
				LHS += Q[i][j];
			constraints.add(LHS == D[i]);
			LHS.end();
		}

		IloRangeArray boundaryConstraints(env);
		for (int i = 0; i < NumberOfScenarios; i++)
		{
			for ( int j = 0; j < NumberOfParticipants; j++)
			{
				boundaryConstraints.add (  Q[i][j] - u[j]*QMax[j] <= 0);
				boundaryConstraints.add (  Q[i][j] - u[j]*QMin[j] >= 0);
			}
		}

		model.add(constraints);
		model.add(boundaryConstraints );
		model.add(IloMinimize(env,SecondLevelObjectiv));

		IloCplex cplex(model);
		cplex.setOut(env.getNullStream()); // to prevent the data that are printed with cplex
		const char* outPutFile="outPutSubMIP.lp";


		cplex.solve();
		//cplex.exportModel(outPutFile);
		cplex.out() << endl << "status: " << cplex.getStatus () << endl;
		objectiveValue=cplex.getObjValue();

		for (int i=0; i < NumberOfScenarios; i++)
		{
			primalValues[i]=IloNumArray (env);
			cplex.getValues(primalValues[i] , Q[i]);
		}
		cplex.getValues(primalStartups, u);

		for (int i=0; i< NumberOfScenarios ; i++)
		{
			vector <double> temp;
			for(int j=0 ;  j< NumberOfParticipants ; j++)
			{
				temp.push_back( primalValues [i][j]);
			}
			PrimalValuesRecord.push_back(temp);
		}

		cplex.out() << endl << "primal solution: " << primalValues << endl;
		cplex.out() << endl << "primal Startup decision: " << primalStartups << endl;

		model.end();
		cplex.end();
		//system("pause");


	}//end try
	catch (IloException &e)	{
		env.out()<<"Error: "<<e<<endl;
	}//end catch iloexception
	catch (std::exception &e){
		std::cerr << "standard exception: " << e.what() << endl;
	}//end catch std exception
	catch (...){
		env.out()<<"Unknown error"<<endl;
	}//end catch exception
}

void LPSubProblem( IloNum p1, IloArray <IloNumArray> &primalValues, IloNumArray primalStartups, IloNumArray &dualValues, IloNum &objectiveValue)
{

	try
	{
		cout<< " sssssssssssssssssssssssssssssssssss" << endl;
		env.out() << " primal startups : " << primalStartups << endl;

		IloModel model(env);

		//decision variables

		IloArray <IloNumVarArray> Q(env, NumberOfScenarios);//the amount that will be provided by each producer
		for (int i = 0; i < NumberOfScenarios ; i++){
			Q[i] = IloNumVarArray (env, NumberOfParticipants);
			for(int j = 0; j < NumberOfParticipants; j++)
				Q[i][j] = IloNumVar(env, QMin[j], QMax[j], ILOFLOAT );
		}
		// generating objective function
		IloExpr SecondLevelObjectiv(env);//expression to construct the second level objectvie
		for (int i = 0; i < NumberOfScenarios; i++)
		{
			SecondLevelObjectiv += prob[i] * p1 * Q[i][0];
			for (int j = 1; j < NumberOfParticipants; j++)//j starts from 1 because the first one is not stochastic
				SecondLevelObjectiv += prob[i] * price[i][j] * Q[i][j];
			// we have to revise this part
		}
		IloRangeArray constraints(env);
		for (int i = 0; i < NumberOfScenarios; i++)
		{
			IloExpr LHS(env);//left hand side of the constraints
			for ( int j = 0; j < NumberOfParticipants; j++)
				LHS += Q[i][j];
			constraints.add(LHS == D[i]);
			LHS.end();
		}

		IloRangeArray boundaryConstraints(env);
		for (int i = 0; i < NumberOfScenarios; i++)
		{
			for ( int j = 0; j < NumberOfParticipants; j++)
			{
				cout << "primalStartups[j] " << primalStartups[j] << endl;
				if (primalStartups[j]==0)
					boundaryConstraints.add (  Q[i][j] == 0);
			}
		}

		model.add(constraints);
		model.add(boundaryConstraints );
		model.add(IloMinimize(env,SecondLevelObjectiv));

		IloCplex cplex(model);
		cplex.setOut(env.getNullStream()); // to prevent the data that are printed with cplex
		const char* outPutFile="outPutSubLP.lp";
		cplex.exportModel(outPutFile);

		cplex.solve();
		cplex.out() << endl << "status: " << cplex.getStatus () << endl;
		objectiveValue=cplex.getObjValue();
		for (int i=0; i < NumberOfScenarios; i++)
		{
			primalValues[i]=IloNumArray (env);
			cplex.getValues(primalValues[i] , Q[i]);
		}
		cplex.out() << endl << "primal solution: " << primalValues << endl;

		cplex.getDuals(dualValues ,constraints);
		cplex.out() << " dual solution: " << dualValues << endl;


		//system("pause");


	}//end try
	catch (IloException &e)	{
		env.out()<<"Error: "<<e<<endl;
	}//end catch iloexception
	catch (std::exception &e){
		std::cerr << "standard exception: " << e.what() << endl;
	}//end catch std exception
	catch (...){
		env.out()<<"Unknown error"<<endl;
	}//end catch exception
}

bool isEqual(IloArray< IloNumArray> arr1, IloArray < IloNumArray> arr2)
{
	bool areEqualArrays=true;
	for (int i=0; i<arr1.getSize();i++){
		for (int j=0; j<arr1[i].getSize();j++)
			if (std::abs(arr1[i][j]- arr2[i][j]) > EPSILON )
			{
				cout << arr1[i][j] << "!="<<  arr2[i][j] << endl;
				areEqualArrays=false;
				//break;
			}
			else
			{
				cout << arr1[i][j] << "=" << arr2[i][j] << endl;
			}
	}
	return areEqualArrays;
}
void printVector2D(vector<vector<double>> A)
{
	for (unsigned int i=0;i<A.size();i++)
	{
		for(unsigned int j=0;j<A[0].size();j++)
			cout<<"\t"<<A[i][j];
		cout<<endl;
	}
}

void inputData ()
{
	string pathFile=getPathFile();
	readDataFromFile(pathFile);
	
}
// searchkey example  "c:\\kathir\\*.txt";
int GetFileList(const char *searchkey, std::vector<std::string> &list)
{
	WIN32_FIND_DATAA  fd;
	HANDLE h = FindFirstFileA(searchkey, &fd);

	if(h == INVALID_HANDLE_VALUE)
	{
		printf ("FindFirstFile failed (%d)\n", GetLastError());
		return 0; // no files found
	}
	
	while(1)
	{
		
		list.push_back( fd.cFileName);

		if(FindNextFileA(h, &fd) == FALSE)
			break;
	}
	return list.size();
}
string getPathFile()
{
	std::vector<std::string> exampleFileList;
	char* path="C:\\Users\\TEMP\\Dropbox\\MIP\\C++\\MIP project\\MIP project\\SampleData\\";
	char* pathExt="C:\\Users\\TEMP\\Dropbox\\MIP\\C++\\MIP project\\MIP project\\SampleData\\*.dat";
	int fileCount = GetFileList(pathExt, exampleFileList);
	cout<<"\n list of example files: \n";
	
	int index = 0;
	for(std::vector<std::string>::const_iterator it = exampleFileList.begin(); it != exampleFileList.end(); it++, index++)
    {
        cout<<"["<<index+1<<"]  "<<it ->c_str()<<endl;
	}
	
	int exapmpleNumber=-1;
	string pathFile;
	while (exapmpleNumber <1 || exapmpleNumber>fileCount)
	{
		cout<<"\n Please choose an example from our list: ";
		cin>>exapmpleNumber;
		if(exapmpleNumber >0 && exapmpleNumber<=fileCount)
		{
			pathFile=path+exampleFileList[exapmpleNumber-1];
			break;
		}
		else
			cout<<"\nThe number you entered is incorrect, please enter a correct one";
	}

	return pathFile;
}
void readDataFromFile(string pathFile)
{

	ifstream dataFile(pathFile);
	if (!dataFile){
		cerr << "ERROR: could not open file '" << pathFile << "' for reading" << endl;
		throw(-1);
	}
	dataFile >> NumberOfParticipants >> NumberOfScenarios >> p1LowerBound >> p1UpperBound >> prob >> price >> D >> QMin  >> QMax >> s;

	env.out() << price  << endl << prob << D << endl << QMin << endl;	
}

