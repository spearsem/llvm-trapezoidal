
declare i32 @printf(i8* noalias nocapture, ...)
declare double @trapezoidal_rule(double (double)*, double, double, i32) 
@.str = private constant [18 x i8] c"Integral is: %f.\0A\00"

define double @my_function(double %x){
entry:
    %x_squared = fmul double %x, %x
    ret double %x_squared
}

define i32 @main() {

    %integral = call double @trapezoidal_rule(double (double)* @my_function,
                                              double 0.0,   
                                              double 1.0,
                                              i32 10001)

    %1 = getelementptr inbounds [18 x i8]* @.str, i32 0, i32 0
    %2 = call i32 (i8*, ...)* @printf(i8* %1, double %integral)

    ret i32 0

}