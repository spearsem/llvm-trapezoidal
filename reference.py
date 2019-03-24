import time

def trapezoidal(f, a, b, N):
    x, dx = a, float(b - a) / N
    integral = f(x)
    for i in range(1, N - 2):
        x += dx
        integral += 2.0 * f(x)
    return (0.5 * dx) * (integral + f(x + dx))


def my_function(x):
    return x * x


if __name__ == "__main__":
    a, b, N = 0, 1, 400001
    st = time.time()
    integral = trapezoidal(my_function, a, b, N)
    print(time.time() - st)
    print(integral)
