import llvmlite.ir as ll
import llvmlite.binding as llvm

from ctypes import c_int32, c_double, POINTER, CFUNCTYPE

# llvm boilerplate initialization
llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()

module = ll.Module()
builder = ll.IRBuilder()

#####
# Create the trapezoidal rule function
#####

# Function prototype stuff:
t_return_type = ll.DoubleType()
t_double_function_type = ll.FunctionType(ll.DoubleType(), [ll.DoubleType()]) 
t_argument_types = [t_double_function_type.as_pointer(), 
                    ll.DoubleType(), 
                    ll.DoubleType(), 
                    ll.IntType(32)]

t_function_type = ll.FunctionType(t_return_type, t_argument_types)
t_func = ll.Function(module, t_function_type, name="trapezoidal_rule")

# Function body blocks
t_entry     = t_func.append_basic_block()
t_loop_body = t_func.append_basic_block()
t_final     = t_func.append_basic_block()

# "entry" block
builder.position_at_end(t_entry)
N_double = builder.sitofp(t_func.args[3], ll.DoubleType())
b_minus_a = builder.fsub(t_func.args[2], t_func.args[1])
dx = builder.fdiv(b_minus_a, N_double)
loop_end = builder.sub(t_func.args[3], ll.Constant(t_func.args[3].type, 2))

builder.branch(t_loop_body)

# "loop_body" block
builder.position_at_end(t_loop_body)

index = builder.phi(ll.IntType(32))
index.add_incoming(ll.Constant(index.type, 0), t_entry)

multiplier = builder.phi(ll.DoubleType())
multiplier.add_incoming(ll.Constant(multiplier.type, 1.0), t_entry)
multiplier.add_incoming(ll.Constant(multiplier.type, 2.0), t_loop_body)

starting_sum = builder.phi(ll.DoubleType())
starting_sum.add_incoming(ll.Constant(starting_sum.type, 0), t_entry)

index_double = builder.sitofp(index, ll.DoubleType())
current_offset = builder.fmul(index_double, dx)
current_x = builder.fadd(t_func.args[1], current_offset)
current_fval = builder.call(t_func.args[0], [current_x])
current_sum_term = builder.fmul(current_fval, multiplier)

total_sum = builder.fadd(current_sum_term, starting_sum)
starting_sum.add_incoming(total_sum, t_loop_body)

incremented_ctr = builder.add(index, ll.Constant(index.type, 1))
index.add_incoming(incremented_ctr, t_loop_body)

done = builder.icmp_unsigned('<', incremented_ctr, loop_end)
builder.cbranch(done, t_loop_body, t_final)

# "final" block
builder.position_at_end(t_final)

last_index = builder.fsub(N_double, ll.Constant(N_double.type, 1.0))
last_delta = builder.fmul(last_index, dx)
last_x = builder.fadd(last_delta, t_func.args[1])
last_f = builder.call(t_func.args[0], [last_x])
final_sum = builder.fadd(total_sum, last_f)
final_sum_dx = builder.fmul(final_sum, dx)
integral = builder.fmul(final_sum_dx, ll.Constant(final_sum_dx.type, 0.5))

builder.ret(integral)
#####


#####
# Create a toy function, x^2, in the same module, for testing.
#####
# Function prototype stuff:
x2_return_type = ll.DoubleType()
x2_argument_types = [ll.DoubleType()]
x2_function_type = ll.FunctionType(x2_return_type, x2_argument_types)
x2_func = ll.Function(module, x2_function_type, name="my_function")

# Function body blocks
x2_entry = x2_func.append_basic_block()

# "entry" block -- only one needed for this simple function.
builder.position_at_end(x2_entry)
result = builder.fmul(x2_func.args[0], x2_func.args[0])
builder.ret(result)
#####


# Boiler plate for the LLVM compiler's pass manager
# and setting optimization or compiler options.
strmod = str(module)
llmod = llvm.parse_assembly(strmod)
pmb = llvm.create_pass_manager_builder()
pmb.opt_level = 2
pm = llvm.create_module_pass_manager()
pmb.populate(pm)
pm.run(llmod)

print(strmod)

# LLVM obtains a handle to the target machine (e.g. this CPU)
target = llvm.Target.from_default_triple().create_target_machine()

# Context manager creates ExecutionEngine "ee" which contains
# the function pointer from compiling the above.
with llvm.create_mcjit_compiler(llmod, target) as ee:
    ee.finalize_object()
   
    target.emit_assembly(llmod)

    # Obtain the function pointer of the compiled LLVM function.
    trapezoidal_rule_ptr = ee.get_function_address("trapezoidal_rule")
    func_arg_type = CFUNCTYPE(c_double, c_double)
    t_cfunc = CFUNCTYPE(
        c_double, 
        func_arg_type, 
        c_double, 
        c_double, 
        c_int32
    )(trapezoidal_rule_ptr)

    # Obtain a function pointer to the test function:
    my_function_ptr = ee.get_function_address("my_function")
    x2_cfunc = CFUNCTYPE(c_double, c_double)(my_function_ptr)

    # Test it out.
    import time
    st = time.time()
    res = t_cfunc(x2_cfunc, c_double(0.0), c_double(1.0), c_int32(400001))
    print(time.time() - st)
    print(res)
