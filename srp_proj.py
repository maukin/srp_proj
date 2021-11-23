import hashlib
import random
import primesieve
from math import gcd
from random import choice
from string import ascii_uppercase


def RabinMiller(n, k=1):
    # False - составное, True - простое
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    r = n - 1
    s = 0
    while r % 2 == 0:
        r //= 2
        s += 1
    for i in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, r, n) # возведение в степень по модулю
        if x == 1 or x == n - 1:
            continue
        for j in range(s - 1):
            x = pow(x, 2, n)
            if x == 1:
                break
        else:
            return False
    return True


def RM_print(num):
    if RabinMiller(num):
        return (' - простое')
    else:
        return (' - составное')


def generator_mod(N_input): # генератор по модулю N
    initial_set = set()
    current_set = set()
    for num in range(1, N_input):
        if gcd(num, N_input) == 1:
            initial_set.add(num)
    # print(f'{initial_set = }')
    for g in range(1, N_input):
        for powers in range(1, N_input):
            current_set.add(pow(g, powers) % N_input)
        # print(f'{current_set = }')
        if initial_set == current_set:
            return g


def SRP():
    pas = "KTO YBIL MARKA"
    I = "maukin"
    N = 0
    k = 3

    print("Факторы протокола: ")
    # print("\t- хеш функция H = SHA-512")
    # print("\t- N - простое = 2*q+1, где q - простое")

    while not RabinMiller(N, 1):
        q = primesieve.nth_prime(random.randint(100, 1000))
        N = 2 * q + 1
        # print("q =", q, " N =", N)
        print(f'\t{q = }\t {N = }\t {RM_print(N)}')
        # https://calculatorium.ru/math/prime-number
        # RM_print(N)

    # print("\t- g - генератор по mod N: для любого 0 < X < N существует единственный x такой, что g^x mod N = X")
    g = generator_mod(N)
    print(f'\t{g = }')

    # print("\t - k - множитель (может быть хеш-функцией), для простоты и производительности примем его за константу = 3")
    print(f'\t{k = }')

    print("\nI. Регистрация.")
    print("\tВ процессе регистрации принимает участие два компонента - клиент и сервер.")
    print("\tНа клиенте генерируется:")

    salt = ''.join(choice(ascii_uppercase) for i in range(12))
    # from string import digits
    # salt = ''.join(choice(digits) for i in range(12))
    # https://ydalenka.ru/note/my-python-generaciya-sluchajnoj-stroki/

    # print("\t- s - соль (случайная строка)")
    print(f'\t{salt = }')

    x = int(hashlib.sha512(salt.encode() + pas.encode()).hexdigest(), 16)

    # print("\t- x = H(S, p)")
    print(f'\t{x = }')

    # print("\t- p - password")
    print(f'\t{pas = }')

    v = pow(g, x, N)

    # print("\t- v = g^x mod N")
    print(f'\t{v = }')


    print("\nII. Аутентификация.")
    print("\nII.I Фаза 1")
    print("\tКлиент отправляет на сервер A и I:")
    print(f'\t{I = }')

    a = random.randint(2, 100)
    print(f'\t{a = }')

    A = pow(g, a, N)
    print(f'\t{A = }')

    print('\tСервер должен убедиться, что A != 0')
    if A != 0:
        print("\tЗатем сервер генерирует случайное число b и вычисляет B")

        b = random.randint(2, 100)
        print(f'\t{b = }')

        B = (k * v + pow(g, b, N)) % N
        print(f'\t{B = }')

        print("\tЗатем сервер отсылает клиенту s и B")

        print("\tКлиент проверяет, что B != 0")
        if B != 0:
            print("\tЗатем обе стороны вычисляют u = H(A, B)")

            u = int(hashlib.sha512(str(A).encode() + str(B).encode()).hexdigest(), 16)
            print(f'\t{u = }')

            print("\tЕсли u = 0, то соединение прерывается")
            if u != 0:
                print("\tКлиент и сервер вычисляют общий ключ сессии(K)")
                s_cl = pow((B - k*(pow(g, x, N))), (a + u * x), N)
                print(f'\t{s_cl = }')

                k_cl = int(hashlib.sha512(str(s_cl).encode()).hexdigest(), 16)
                print(f'\t{k_cl = }')

                s_serv = pow(A * pow(v, u, N), b, N)
                print(f'\t{s_serv = }')

                k_serv = int(hashlib.sha512(str(s_serv).encode()).hexdigest(), 16)
                print(f'\t{k_serv = }')

                if k_serv == k_cl:
                    print("\t\tSuccess!\tК клиента = К сервера")
                else:
                    print("\t\tERROR: К клиента != К сервера")

                print("\tПосле этого сервер и клиент - оба имеют одинаковые К.")
                print("\nII.II  Фаза 2.")
                print("\tГенерация подтверждения")
                print("\tСервер и клиент вычисляют М")
                HN = int(hashlib.sha512(str(N).encode()).hexdigest(), 16)
                Hg = int(hashlib.sha512(str(g).encode()).hexdigest(), 16)
                HI = int(hashlib.sha512(str(I).encode()).hexdigest(), 16)

                M_cl = int(hashlib.sha512(str(HN ^ Hg).encode() + str(HI).encode() + str(s_cl).encode() + str(A).encode() + str(B).encode() + str(k).encode()).hexdigest(), 16)
                print(f'\t{M_cl = }')
                M_serv = int(hashlib.sha512(str(HN ^ Hg).encode() + str(HI).encode() + str(s_serv).encode() + str(A).encode() + str(B).encode() + str(k).encode()).hexdigest(), 16)
                print(f'\t{M_serv = }')
                if M_cl == M_serv:
                    print("\t\tSuccess!\tM клиента = M сервера")
                else:
                    print("\t\tERROR: M клиента != M сервера")

                print("\tКлиент и сервер вычисляют R")
                R_cl = int(hashlib.sha512(str(A).encode() + str(M_cl).encode() + str(k_cl).encode()).hexdigest(), 16)
                print(f'\t{R_cl = }')
                R_serv = int(hashlib.sha512(str(A).encode() + str(M_serv).encode() + str(k_serv).encode()).hexdigest(), 16)
                print(f'\t{R_serv = }')
                if R_cl == R_serv:
                    print("\t\tSuccess!\tR клиента = R сервера")
                else:
                    print("\t\tERROR: R клиента != R сервера")

                print("\tЕсли вычисленная клиентом R = R c сервера, то клиент и сервер те за кого себя выдают.")
            else:
                print("ERROR: u = 0!")
        else:
            print("ERROR: B = 0")
    else:
        print("ERROR: A = 0")


if __name__ == "__main__":
    SRP()
