def alphabet_position(letter):
    if letter.isupper():
        return ord(letter) - ord("A")
    elif letter.islower():
        return ord(letter) - ord("a")
    else:
        return 0

def rotate_character(char, rot):
    newLetter = (alphabet_position(char) + rot) % 26
    if char.isupper():
        return chr(newLetter + ord("A"))
    elif char.islower():
        return chr(newLetter + ord("a"))
    else:
        return char

def encrypt(m, n):
    newMessage = ""
    for letter in m:
        newMessage += rotate_character(letter, int(n))
    return newMessage

def main():
    from sys import argv, exit
    if len(argv) == 2 and argv[1].isdigit():
        message = input("Type a message:\n")
        print(encrypt(message, argv[1]))
    else:
        print("""usage: python3 caesar.py n
Arguments:
-n : The int to be used as a "key" to encrypt your message. Should be an integer-- no letters or special characters.""")
        exit()

if __name__ == "__main__":
    main()
