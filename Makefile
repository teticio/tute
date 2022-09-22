OPEN_SPIEL := ../open_spiel

tute_test: build/libopen_spiel.so
	clang++ -I. -I$(OPEN_SPIEL) -I$(OPEN_SPIEL)/open_spiel/abseil-cpp \
		-Lbuild -lopen_spiel -std=c++17 -g -Og \
		-o tute_test open_spiel/games/tute.cc open_spiel/games/tute_test.cc
	chmod +x tute_test

build/libopen_spiel.so:
	cd build; BUILD_TYPE=Debug BUILD_SHARED_LIB=ON CXX=clang++ cmake \
		-DPython3_EXECUTABLE=$(which python3) -DCMAKE_CXX_COMPILER=${CXX} \
		../$(OPEN_SPIEL)/open_spiel
	cd build; make -j$(nproc) open_spiel

run: tute_test
	LD_LIBRARY_PATH=build ./tute_test