IDIR =./
CC=g++
CFLAGS=-I$(IDIR) -std=c++11

LIBS=-lpthread

_DEPS = *.hpp
DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

all: client server tcWrapper

client: Client.cpp
	$(CC) -o ${@}.a $^ $(CFLAGS) $(LIBS)

server: Server.cpp
	$(CC) -o ${@}.a $^ $(CFLAGS) $(LIBS)

tcWrapper: tcWrapper.cpp
	$(CC) -o ${@}.a $^ $(CFLAGS) $(LIBS)

.PHONY: clean

clean:
	rm -f *~ core $(INCDIR)/*~ *.a *Output*
