
define double @trapezoidal_rule(double(double)* %fn, 
                                double %a, 
                                double %b, 
                                i32 %N) {

entry:
    %N_double  = sitofp i32 %N to double
    %b_minus_a = fsub double %b, %a
    %dx        = fdiv double %b_minus_a, %N_double
    %loop_end  = sub i32 %N, 2

    br label %loop_body

loop_body:
    %index            = phi i32 [0, %entry], [%incremented_ctr, %loop_body]
    %multiplier       = phi double [1.0, %entry], [2.0, %loop_body]
    %starting_sum     = phi double [0.0, %entry], [%total_sum, %loop_body] 
    %index_double     = sitofp i32 %index to double
    %current_offset   = fmul double %index_double, %dx
    %current_x        = fadd double %a, %current_offset
    %current_fval     = call double %fn(double %current_x)
    %current_sum_term = fmul double %current_fval, %multiplier
    %total_sum        = fadd double %current_sum_term, %starting_sum 
    %incremented_ctr  = add i32 %index, 1
    %done             = icmp ult i32 %incremented_ctr, %loop_end

    br i1 %done, label %loop_body, label %final

final:
    %last_index   = fsub double %N_double, 1.0 
    %last_delta   = fmul double %last_index, %dx
    %last_x       = fadd double %last_delta, %a
    %last_f       = call double %fn(double %last_x)
    %final_sum    = fadd double %total_sum, %last_f
    %final_sum_dx = fmul double %final_sum, %dx
    %integral     = fmul double %final_sum_dx, 0.5

    ret double %integral

}



