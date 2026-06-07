from typing import Union, Tuple, List, Dict

Point = Union[Tuple[int, int], str]   # Either (x, y) or "O"


def is_prime(p: int) -> bool:
    """
    Basic primality check.
    This script assumes p is prime because we are working over F_p.
    """
    if p < 2:
        return False
    if p == 2:
        return True
    if p % 2 == 0:
        return False

    i = 3
    while i * i <= p:
        if p % i == 0:
            return False
        i += 2

    return True


def is_valid_curve(a: int, b: int, p: int) -> bool:
    """
    Checks whether the elliptic curve

        y^2 = x^3 + ax + b mod p

    is non-singular.

    The curve is valid if:

        4a^3 + 27b^2 != 0 mod p
    """
    discriminant = (4 * a**3 + 27 * b**2) % p
    return discriminant != 0


def find_points_on_curve(a: int, b: int, p: int) -> List[Point]:
    """
    Finds all points (x, y) on the elliptic curve:

        y^2 = x^3 + ax + b mod p

    over the finite field F_p.
    """

    points = []

    for x in range(p):
        rhs = (x**3 + a * x + b) % p

        for y in range(p):
            lhs = (y**2) % p

            if lhs == rhs:
                points.append((x, y))

    points.append("O")
    return points


def inverse_mod(k: int, p: int) -> int:
    """
    Returns the modular inverse of k mod p.
    """
    return pow(k % p, -1, p)


def point_add(P: Point, Q: Point, a: int, p: int) -> Point:
    """
    Adds two points P and Q on the elliptic curve:

        y^2 = x^3 + ax + b mod p

    The value b is not needed for point addition.
    """

    if P == "O":
        return Q

    if Q == "O":
        return P

    x1, y1 = P
    x2, y2 = Q

    # Vertical line case:
    # P + (-P) = O
    if x1 == x2 and (y1 + y2) % p == 0:
        return "O"

    # Point doubling
    if P == Q:
        numerator = (3 * x1**2 + a) % p
        denominator = (2 * y1) % p
        m = (numerator * inverse_mod(denominator, p)) % p

    # Point addition
    else:
        numerator = (y2 - y1) % p
        denominator = (x2 - x1) % p
        m = (numerator * inverse_mod(denominator, p)) % p

    x3 = (m**2 - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p

    return (x3, y3)


# -----------------------------------------------------------
# Scalar multiplication (double-and-add)
# -----------------------------------------------------------
def scalar_mult(k: int, P: Point, a: int, p: int) -> Point:
    """
    Computes kP using the double-and-add method.

    This is the elliptic curve equivalent of repeated addition:
        kP = P + P + ... + P

    Instead of adding P exactly k times, double-and-add uses the binary
    representation of k to make the calculation much faster.
    """

    if k < 0:
        raise ValueError("Scalar k must be non-negative.")

    result = "O"
    addend = P

    while k > 0:
        if k % 2 == 1:
            result = point_add(result, addend, a, p)

        addend = point_add(addend, addend, a, p)
        k //= 2

    return result


def point_order(P: Point, a: int, p: int, group_size: int) -> int:
    """
    Finds the order of point P.

    The order of P is the smallest positive integer n such that:

        nP = O

    group_size is used as a safety bound because every point order must divide
    the total number of points in the elliptic curve group.
    """

    if P == "O":
        return 1

    result = P

    for order in range(1, group_size + 1):
        if result == "O":
            return order

        result = point_add(result, P, a, p)

    raise ValueError(f"Could not find order for point {P}. Something is wrong.")


def calculate_all_orders(a: int, b: int, p: int) -> Dict[Point, int]:
    """
    Finds every point on the curve and calculates its order.
    """

    points = find_points_on_curve(a, b, p)
    group_size = len(points)

    orders = {}

    for P in points:
        orders[P] = point_order(P, a, p, group_size)

    return orders

def find_best_base_points(a: int, b: int, p: int):
    """
    Finds the best candidate base points for ECC-style use.

    A good base point G should:
    - not be the point at infinity,
    - lie on the curve,
    - have prime order n,
    - have the largest possible prime order,
    - have small cofactor h = #E(F_p) / n.
    """

    points = find_points_on_curve(a, b, p)
    group_size = len(points)
    orders = calculate_all_orders(a, b, p)

    candidates = []

    for point, order in orders.items():
        if point == "O":
            continue

        if is_prime(order):
            cofactor = group_size // order

            candidates.append({
                "point": point,
                "order": order,
                "cofactor": cofactor
            })

    if not candidates:
        return []

    max_prime_order = max(candidate["order"] for candidate in candidates)

    best_candidates = [
        candidate for candidate in candidates
        if candidate["order"] == max_prime_order
    ]

    return best_candidates


# -----------------------------------------------------------
# Curve suitability assessment (ECC-style rules)
# -----------------------------------------------------------

def assess_curve_suitability(a: int, b: int, p: int):
    """
    Applies simple ECC-style suitability rules to the curve.

    For real cryptographic use, the field size and subgroup order must be much
    larger than this toy script can practically brute-force. These checks are
    therefore educational rather than a replacement for real curve standards.
    """

    points = find_points_on_curve(a, b, p)
    group_size = len(points)
    orders = calculate_all_orders(a, b, p)
    base_point_candidates = find_best_base_points(a, b, p)

    max_order = max(orders.values())
    max_prime_order = 0
    best_cofactor = None

    if base_point_candidates:
        max_prime_order = base_point_candidates[0]["order"]
        best_cofactor = base_point_candidates[0]["cofactor"]

    rules = []

    rules.append({
        "rule": "Field modulus p is prime",
        "passed": is_prime(p),
        "detail": f"p = {p}"
    })

    rules.append({
        "rule": "Curve is non-singular",
        "passed": is_valid_curve(a, b, p),
        "detail": f"4a^3 + 27b^2 mod p = {(4 * a**3 + 27 * b**2) % p}"
    })

    rules.append({
        "rule": "Base point is not the point at infinity",
        "passed": len(base_point_candidates) > 0,
        "detail": "Candidate base points exclude O."
    })

    rules.append({
        "rule": "There exists a prime-order base point",
        "passed": max_prime_order > 0,
        "detail": f"Largest prime order found: {max_prime_order}"
    })

    rules.append({
        "rule": "Largest prime order is large enough for real ECC",
        "passed": max_prime_order >= 2**256,
        "detail": f"Largest prime order found: {max_prime_order}; real ECC usually targets roughly 256-bit subgroup order or higher."
    })

    rules.append({
        "rule": "Cofactor is small",
        "passed": best_cofactor is not None and best_cofactor <= 4,
        "detail": f"Best cofactor h = {best_cofactor}; preferred values are usually 1, 2, or 4."
    })

    rules.append({
        "rule": "Maximum point order is prime",
        "passed": is_prime(max_order),
        "detail": f"Maximum point order found: {max_order}"
    })

    suitable_for_real_ecc = all(rule["passed"] for rule in rules)

    return {
        "group_size": group_size,
        "max_order": max_order,
        "max_prime_order": max_prime_order,
        "best_cofactor": best_cofactor,
        "rules": rules,
        "suitable_for_real_ecc": suitable_for_real_ecc
    }

def print_curve_summary(a: int, b: int, p: int):
    """
    Prints:
    - curve information,
    - total number of points,
    - all point orders,
    - highest-order points,
    - best ECC-style base point candidates.
    """

    if not is_prime(p):
        raise ValueError("p must be prime for this script.")

    if not is_valid_curve(a, b, p):
        raise ValueError(
            "Invalid elliptic curve: the curve is singular because "
            "4a^3 + 27b^2 ≡ 0 mod p."
        )

    points = find_points_on_curve(a, b, p)
    orders = calculate_all_orders(a, b, p)

    max_order = max(orders.values())
    highest_order_points = [
        point for point, order in orders.items()
        if order == max_order
    ]

    print("=" * 60)
    print("Elliptic curve:")
    print(f"    y^2 = x^3 + {a}x + {b} mod {p}")
    print("=" * 60)
    print()

    print(f"Total number of points including O: {len(points)}")
    # print()

    # print("Point orders:")
    # print("=" * 60)

    #for point, order in orders.items():
    #    print(f"{point}: order {order}")

    # print()
    # print("=" * 60)
    # print("Highest-order points:")
    # print("=" * 60)
    print(f"Maximum order: {max_order}")
    print("=" * 60)
    print()

    # for point in highest_order_points:
    #     print(point)

    # print()
    # print("=" * 60)
    # print("ECC-style base point candidates:")
    # print("=" * 60)

    base_point_candidates = find_best_base_points(a, b, p)

    if not base_point_candidates:
        print("No valid prime-order base point candidates found.")
        return

    best_prime_order = base_point_candidates[0]["order"]
    best_cofactor = base_point_candidates[0]["cofactor"]

    print(f"Largest prime order n: {best_prime_order}")
    print(f"Cofactor h = #E(F_p) / n = {len(points)} / {best_prime_order} = {best_cofactor}")
    print()

    if best_cofactor > 4:
        print("Warning: cofactor is large. This curve is not suitable for real cryptographic use.")
        print()

    print("Best base point candidates:")

    for candidate in base_point_candidates:
        print(candidate["point"])

    print()
    print("=" * 60)
    print("Curve suitability rules:")
    print("=" * 60)

    suitability = assess_curve_suitability(a, b, p)

    for rule in suitability["rules"]:
        status = "PASS" if rule["passed"] else "FAIL"
        print(f"[{status}] {rule['rule']}")
        print(f"       {rule['detail']}")

    print()
    if suitability["suitable_for_real_ecc"]:
        print("Conclusion: This curve passes the simplified ECC suitability checks.")
    else:
        print("Conclusion: This curve is useful for learning, but it is not suitable for real cryptographic use.")

    print()
    print("=" * 60)
    print("Toy ECC key generation and ECDH demonstration:")
    print("=" * 60)

    G = base_point_candidates[0]["point"]
    n = base_point_candidates[0]["order"]

    print(f"Selected base point G: {G}")
    print(f"Base point order n: {n}")
    print()

    alice_private = 17 % n
    bob_private = 43 % n

    if alice_private == 0:
        alice_private = 1
    if bob_private == 0:
        bob_private = 1

    alice_public = scalar_mult(alice_private, G, a, p)
    bob_public = scalar_mult(bob_private, G, a, p)

    alice_shared_secret = scalar_mult(alice_private, bob_public, a, p)
    bob_shared_secret = scalar_mult(bob_private, alice_public, a, p)

    print("Alice private key d_A:", alice_private)
    print("Alice public key Q_A = d_A G:", alice_public)
    print()

    print("Bob private key d_B:", bob_private)
    print("Bob public key Q_B = d_B G:", bob_public)
    print()

    print("Alice computes shared secret S_A = d_A Q_B:", alice_shared_secret)
    print("Bob computes shared secret S_B = d_B Q_A:", bob_shared_secret)
    print()

    if alice_shared_secret == bob_shared_secret:
        print("ECDH success: both parties computed the same shared secret.")
    else:
        print("ECDH failed: the shared secrets do not match.")

def main():
    print("Enter elliptic curve parameters for:")
    print("    y^2 = x^3 + ax + b mod p")
    print()

    a = int(input("Enter a: "))
    b = int(input("Enter b: "))
    p = int(input("Enter prime p: "))

    print_curve_summary(a, b, p)


if __name__ == "__main__":
    main()