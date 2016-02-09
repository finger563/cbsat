IDIR =./
CC=g++
CFLAGS=-I$(IDIR) -std=c++11

LIBS=-lpthread

_DEPS = *.hpp
DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

all: client server tcWrapper

client: Client.cpp
	$(CC) -o ${@} $^ $(CFLAGS) $(LIBS)

server: Server.cpp
	$(CC) -o ${@} $^ $(CFLAGS) $(LIBS)

tcWrapper: tcWrapper.cpp
	$(CC) -o ${@} $^ $(CFLAGS) $(LIBS)

.PHONY: clean

clean:
	rm -f *~ core $(INCDIR)/*~ *.a *Output*
test:
	g++ recursive.cpp -o recursive -std=c++11
