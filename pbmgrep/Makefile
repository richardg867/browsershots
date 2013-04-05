CPP_FLAGS=-O3 -I/opt/local/include
LD_FLAGS=-lnetpbm -L/opt/local/lib

all : pbmgrep ppmfg

pbmgrep : pbmgrep.o Feature.o
	g++ $(LD_FLAGS) -o $@ $^
	strip $@

ppmfg : ppmfg.o
	g++ $(LD_FLAGS) -o $@ $<
	strip $@

%.o : %.cpp *.hpp
	g++ $(CPP_FLAGS) -c $<

install :
	cp -f ppmfg pbmgrep /usr/local/bin
