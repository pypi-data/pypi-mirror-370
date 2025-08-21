#****************************************************************************
#*
#*                                 M U E S L I   v 1.5
#*
#*
#*     Copyright 2016 IMDEA Materials Institute, Getafe, Madrid, Spain
#*     Contact: muesli.materials@imdea.org
#*     Author: Ignacio Romero (ignacio.romero@imdea.org)
#*
#*     This file is part of MUESLI.
#*
#*     MUESLI is free software: you can redistribute it and/or modify
#*     it under the terms of the GNU General Public License as published by
#*     the Free Software Foundation, either version 3 of the License, or
#*     (at your option) any later version.
#*
#*     MUESLI is distributed in the hope that it will be useful,
#*     but WITHOUT ANY WARRANTY; without even the implied warranty of
#*     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#*     GNU General Public License for more details.
#*
#*     You should have received a copy of the GNU General Public License
#*     along with MUESLI.  If not, see <http://www.gnu.org/licenses/>.
#*
#****************************************************************************

INSTALL_BASE := /usr/local

export SOURCEDIR   = $(CURDIR)
export MUESLI_LIB  = libmuesli.a
export MUESLI_PATH = $(CURDIR)
export MUESLI_SRC  = $(SOURCEDIR)
export LIBPATH     = $(MUESLI_PATH)/lib

# to use EIGEN uncomment the next line
#export WITHEIGEN = true


ifdef WITHEIGEN
    export CPPFLAGS = -DWITHEIGEN -DNDEBUG
    export EIGEN_PATH = /usr/local
endif


# muesli is thread safe if each materialpoint is access only by one
# thread at a time. If the calling program is not programmed in this way,
# one must uncomment the next line to guarantee the thread-safety
# export CPPFLAGS += -DSTRICT_THREAD_SAFE


# detect operating system, set ARCH variable
OS:=$(shell uname)
ifeq ($(OS), Darwin)
#       Macs with intel processor
	ifeq ($(shell /usr/sbin/sysctl -n hw.optional.x86_64 2>/dev/null),1)
	     	export ARCH    := darwin_ia64
	else
	     	export ARCH    :=darwin_ia32
	endif
# 	linux 
else 
	ifeq ($(OS), Linux)
		export ARCH   := linux_ia64
	endif
endif


# maintenance functions
export REMOVE    = @rm
export TIDY      = @rm -f *.bak *~ .DS_Store *.o *.log
export CLEAN     = @rm -f *.bak *.o *~ .DS_Store


INCLUDEPATH      = -I$(SOURCEDIR)/..
AR               = /usr/bin/ar
ARFLAGS          = cr


ifeq ($(ARCH),darwin_ia64)
	export CPP       = /cluster/software/gcc-4.8.5/bin/g++
	export CPPFLAGS += -O3 -std=c++11 -fpic -Wall -m64 -arch x86_64 $(INCLUDEPATH)
	LINKER           = g++
	LINKERFLAGS     += -L/usr/local/lib
	RANLIB           = /usr/bin/ranlib $(RLIBFLAGS)
	ifndef WITHEIGEN
        LINKERFLAGS += -framework Accelerate
    else
        INCLUDEPATH += -I$(EIGEN_PATH)
    endif

else ifeq ($(ARCH),linux_ia64)
	export CPP       = /cluster/software/gcc-4.8.5/bin/g++
	export CPPFLAGS += -O3 -std=c++11 -fpic -march=native $(INCLUDEPATH)
	LINKER           = g++
	LINKERFLAGS     += -L$(LIBPATH)
	RANLIB           = ranlib $(RLIBFLAGS)
	ifndef WITHEIGEN
        LINKERFLAGS += -llapack -lblas
    else
        INCLUDEPATH += -I$(EIGEN_PATH)
    endif
endif

SUBDIRS = \
    $(SOURCEDIR)/Failure  \
    $(SOURCEDIR)/Finitestrain  \
    $(SOURCEDIR)/Fluid  \
    $(SOURCEDIR)/Fcoupled \
    $(SOURCEDIR)/Interface  \
    $(SOURCEDIR)/Math  \
    $(SOURCEDIR)/Smallstrain  \
    $(SOURCEDIR)/Sthermomechanical   \
    $(SOURCEDIR)/Thermal \
    $(SOURCEDIR)/Utils


MUESLI_FILES = \
    material.o   \
    tensor.o \
    Failure/brownmiller.o \
    Failure/jcfailure.o \
    Finitestrain/arrheniustype.o   \
    Finitestrain/arrudaboyce.o   \
    Finitestrain/finitestrain.o   \
    Finitestrain/fisotropic.o \
    Finitestrain/fplastic.o \
    Finitestrain/fplastic.o \
    Finitestrain/johnsoncook.o \
    Finitestrain/mooney.o \
    Finitestrain/neohook.o \
    Finitestrain/reducedfinitestrain.o \
    Finitestrain/svk.o \
    Finitestrain/yeoh.o \
    Finitestrain/zerilliarmstrong.o \
    Fluid/fluid.o   \
    Fluid/newtonian.o \
    Fcoupled/thermofinitestrain.o \
    Fcoupled/fmechmass.o \
    Interface/interface_abaqus.o \
    Interface/interface_lsdyna.o \
    Math/mtensor.o \
    Math/mmatrix.o \
    Math/mrealvector.o\
    Smallstrain/smallstrain.o   \
    Smallstrain/elastic.o \
    Smallstrain/reducedsmallstrain.o \
    Smallstrain/sdamage.o \
    Smallstrain/splastic.o \
    Smallstrain/viscoelastic.o \
    Smallstrain/viscoplastic.o \
    Sthermomechanical/smallthermo.o \
    Thermal/conductor.o \
    Utils/utils.o

ifndef WITHEIGEN
    MUESLI_FILE += 
endif

default: library

export TASKS_FILE = $(SOURCEDIR)/makefile.tasks
include $(TASKS_FILE)

library: material.o tensor.o
	@( \
	for f in $(SUBDIRS); \
	do \
		$(MAKE) -C $$f compile; \
	done );
	($(AR) $(ARFLAGS) $(LIBPATH)/$(MUESLI_LIB) $(MUESLI_FILES))
	$(RANLIB) $(LIBPATH)/$(MUESLI_LIB)


install: 
	test -d $(INSTALL_BASE) || mkdir $(INSTALL_BASE)
	test -d $(INSTALL_BASE)/lib || mkdir $(INSTALL_BASE)/lib
	test -d $(INSTALL_BASE)/include || mkdir $(INSTALL_BASE)/include
	rm -rf $(INSTALL_BASE)/include/muesli
	cp -p $(LIBPATH)/$(MUESLI_LIB) $(INSTALL_BASE)/lib
	find . -name '*.h' -print | cpio -pdlv $(INSTALL_BASE)/include/muesli

#	find . -name '*.h' -exec install -m 0755 '{}' $(INSTALL_BASE)/include/muesli ';'


all: library install
	rm -f Test/test.o
	@( $(MAKE) -C Test all );
	g++ Test/test.o -lmuesli -o testmuesli
	./testmuesli

example: Test/example.o
	@( $(MAKE) -C Test compile);
	g++ -L$(LIBPATH) Test/example.o -lmuesli -o Test/examplemuesli

test: Test/test.o
	@( $(MAKE) -C Test compile );
	g++ -L$(LIBPATH) -framework Accelerate Test/test.o -lmuesli -o testmuesli

# use this test if linking with a developing library, not installed yet
devtest: Test/test.o
	@( $(MAKE) -C Test compile );
	g++ Test/test.o -L$(LIBPATH) $(LINKERFLAGS) -lmuesli -o testmuesli

runexample: library example
	@( cd Test; ./examplemuesli; gnuplot generate.gnuplot; mpost example.mp; mptopdf example.0 example.1)
	@( cd Test; rm -f mpx* *.mp *.mpx example.0)


zip: clean
	(cd ..; tar czvf muesli.tgz muesli)

maintenance:
	find . -name '*.h' -print0 | xargs -0 sed -E -i '' 's/subdirs/SUBDIRS/g'

headers:
	find . -name "*.h" -exec replace_header.sh {} \;
	find . -name "*.cpp" -exec replace_header.sh {} \;
