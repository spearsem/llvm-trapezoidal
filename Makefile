.PHONY: run clean

run: llvm_main
	time -f'%e' ./llvm_main

llvm_main : single.s
	clang single.s -o llvm_main

single.s : single.ll
	llc single.ll -o single.s

single.ll : llvm_main.ll trapezoidal_rule.ll
	llvm-link -S -v trapezoidal_rule.ll llvm_main.ll -o single.ll

clean :
	rm single.ll single.s llvm_main
