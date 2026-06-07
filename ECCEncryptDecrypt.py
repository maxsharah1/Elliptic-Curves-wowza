from hashlib import sha256
from typing import Union, Tuple

Point = Union[Tuple[int, int], str]


# -----------------------------------------------------------
# Curve parameters
# -----------------------------------------------------------

# Toy curve:
# y^2 = x^3 + ax + b mod p

a = 1
b = 32
p = 101

# Selected base point from your previous program
G = (4, 10)

# Order of G
n = 101


# -----------------------------------------------------------
# Elliptic curve arithmetic
# -----------------------------------------------------------

def inverse_mod(k: int, p: int) -> int:
    """
    Returns the modular inverse of k mod p.
    """
    return pow(k % p, -1, p)


def point_add(P: Point, Q: Point, a: int, p: int) -> Point:
    """
    Adds two points P and Q on the curve:

        y^2 = x^3 + ax + b mod p
    """

    if P == "O":
        return Q

    if Q == "O":
        return P

    x1, y1 = P
    x2, y2 = Q

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


def scalar_mult(k: int, P: Point, a: int, p: int) -> Point:
    """
    Computes kP using double-and-add.
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


# -----------------------------------------------------------
# Toy key derivation and XOR encryption
# -----------------------------------------------------------

def derive_key(shared_point: Point, length: int) -> bytes:
    """
    Derives a byte stream from the shared elliptic curve point.

    This is a simplified educational KDF.
    For a real system, use a proper KDF such as HKDF.
    """

    if shared_point == "O":
        raise ValueError("Shared point cannot be the point at infinity.")

    x, y = shared_point

    key_stream = b""
    counter = 0

    while len(key_stream) < length:
        data = f"{x},{y},{counter}".encode()
        key_stream += sha256(data).digest()
        counter += 1

    return key_stream[:length]


def xor_bytes(data: bytes, key: bytes) -> bytes:
    """
    XORs data with a key stream.
    """
    return bytes(d ^ k for d, k in zip(data, key))


# -----------------------------------------------------------
# ECC encryption and decryption
# -----------------------------------------------------------

def encrypt_message(message: str, recipient_public_key: Point, ephemeral_private_key: int):
    """
    Encrypts a message using a simplified ECIES-style process.

    Sender computes:

        C1 = kG
        S = kQ_B

    where:
        k is the ephemeral private key,
        G is the base point,
        Q_B is the recipient public key.

    The shared point S is used to derive a symmetric key.
    """

    plaintext = message.encode()

    C1 = scalar_mult(ephemeral_private_key, G, a, p)

    shared_secret = scalar_mult(ephemeral_private_key, recipient_public_key, a, p)

    key = derive_key(shared_secret, len(plaintext))

    ciphertext = xor_bytes(plaintext, key)

    return C1, ciphertext


def decrypt_message(C1: Point, ciphertext: bytes, recipient_private_key: int):
    """
    Decrypts the message.

    Receiver computes:

        S = d_B C1

    where:
        d_B is recipient private key,
        C1 is sender's ephemeral public key.

    This gives the same shared secret used during encryption.
    """

    shared_secret = scalar_mult(recipient_private_key, C1, a, p)

    key = derive_key(shared_secret, len(ciphertext))

    plaintext = xor_bytes(ciphertext, key)

    return plaintext.decode()


# -----------------------------------------------------------
# Demonstration
# -----------------------------------------------------------

def main():
    print("=" * 60)
    print("Toy ECC Encryption/Decryption Demo")
    print("=" * 60)

    print()
    print("Curve:")
    print(f"    y^2 = x^3 + {a}x + {b} mod {p}")
    print(f"Base point G = {G}")
    print(f"Order n = {n}")

    print()
    print("=" * 60)
    print("Receiver key generation")
    print("=" * 60)

    # Receiver's private key
    receiver_private_key = 17

    # Receiver's public key
    receiver_public_key = scalar_mult(receiver_private_key, G, a, p)

    print("Receiver private key d_B:", receiver_private_key)
    print("Receiver public key Q_B = d_B G:", receiver_public_key)

    print()
    print("=" * 60)
    print("Message encryption")
    print("=" * 60)

    message = input("Enter message to encrypt: ")

    # Sender chooses a temporary private key
    ephemeral_private_key = 43

    C1, ciphertext = encrypt_message(
        message,
        receiver_public_key,
        ephemeral_private_key
    )

    print()
    print("Sender ephemeral private key k:", ephemeral_private_key)
    print("Ephemeral public key C1 = kG:", C1)
    print("Ciphertext in hex:", ciphertext.hex())

    print()
    print("=" * 60)
    print("Message decryption")
    print("=" * 60)

    decrypted_message = decrypt_message(
        C1,
        ciphertext,
        receiver_private_key
    )

    print("Decrypted message:", decrypted_message)

    print()
    if decrypted_message == message:
        print("Success: decrypted message matches original message.")
    else:
        print("Failure: decrypted message does not match original message.")


if __name__ == "__main__":
    main()