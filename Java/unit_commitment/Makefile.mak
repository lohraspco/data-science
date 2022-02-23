SYSTEM     = x86-64_linux
LIBFORMAT  = static_pic

#------------------------------------------------------------
#
# When you adapt this makefile to compile your CPLEX programs
# please copy this makefile and set CPLEXDIR and CONCERTDIR to
# the directories where CPLEX and CONCERT are installed.
#
#------------------------------------------------------------

CPLEXDIR      = /usr/local/cplex/v12.6.3/opt/ibm/ILOG/CPLEX_Studio1263/cplex
CONCERTDIR    = /usr/local/cplex/v12.6.3/opt/ibm/ILOG/CPLEX_Studio1263/concert
PROJDIR       = /net/hydra2/home1/m/mnajaria/workspace/Resilience/
# ---------------------------------------------------------------------
# Compiler selection 
# ---------------------------------------------------------------------

JAVAC = javac 

# ---------------------------------------------------------------------
# Clear any default targets for building .class files from .java files; we 
# will provide our own target entry to do this in this makefile.
# make has a set of default targets for different suffixes (like .c.o) 
# Currently, clearing the default for .java.class is not necessary since 
# make does not have a definition for this target, but later versions of 
# make may, so it doesn't hurt to make sure that we clear any default 
# definitions for these
# ---------------------------------------------------------------------

.SUFFIXES: .java .class
# ---------------------------------------------------------------------
# Compiler options 
# ---------------------------------------------------------------------

JOPT  = -classpath $(CPLEXDIR)/lib/cplex.jar -O

# ---------------------------------------------------------------------
# Link options and libraries
# ---------------------------------------------------------------------

CPLEXBINDIR   = $(CPLEXDIR)/bin/$(BINDIST)
CPLEXJARDIR   = $(CPLEXDIR)/lib/cplex.jar
CPLEXLIBDIR   = $(CPLEXDIR)/lib/$(SYSTEM)/$(LIBFORMAT)
CONCERTLIBDIR = $(CONCERTDIR)/lib/$(SYSTEM)/$(LIBFORMAT)

CCLNDIRS  = -L$(CPLEXLIBDIR) -L$(CONCERTLIBDIR)
CLNDIRS   = -L$(CPLEXLIBDIR)
CCLNFLAGS = -lconcert -lilocplex -lcplex -lm -lpthread
CLNFLAGS  = -lcplex -lm -lpthread
JAVA      = java  -d64 -Djava.library.path=$(CPLEXDIR)/bin/x86-64_linux -classpath $(CPLEXJARDIR):


all:
	make all_java

execute: all
	make execute_java
CONCERTINCDIR = $(CONCERTDIR)/include
CPLEXINCDIR   = $(CPLEXDIR)/include

EXDIR         = $(CPLEXDIR)/examples
EXDATA        = $(EXDIR)/data
EXSRCJAVA     = $(EXDIR)/src/java

PROJDATA      =$(PROJDIR)/Data/bus57_96h
PROJSRCJAVA   = $(PROJDIR)/src/resilience

JCFLAGS = $(JOPT)


#------------------------------------------------------------
#  make all      : to compile the examples. 
#  make execute  : to compile and execute the examples.
#------------------------------------------------------------

JAVA_EX = Resilience.class  InputDataReader.java UnitCommitment.java

all_java: $(JAVA_EX)


execute_java: $(JAVA_EX)
	 $(JAVA) Resilience $(PROJDATA)/ unitData.txt

# ------------------------------------------------------------

clean :
	/bin/rm -rf *.o *~ *.class
	/bin/rm -rf *.mps *.ord *.sos *.lp *.sav *.net *.msg *.log *.clp

# ------------------------------------------------------------
#
# The files
#
Resilience.class: $(PROJSRCJAVA)/Resilience.java
	$(JAVAC) $(JCFLAGS) -d . $(PROJSRCJAVA)resilience/Resilience.java\
							 $(PROJSRCJAVA)resilience/UnitCommitment.java
							 $(PROJSRCJAVA)inputOutput/InputDataReader.java \
							 $(PROJSRCJAVA)inputOutput/WriteToFile.java

# Local Variables:
# mode: makefile
# End:
