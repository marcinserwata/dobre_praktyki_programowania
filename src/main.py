import re

def is_palindrome(text: str) -> bool:
    """
    Sprawdza, czy dany ciąg znaków jest palindromem (ignorując wielkość liter i spacje).
    """    
    cleaned_text = ''.join(char.lower() for char in text if char.isalnum())
    return cleaned_text == cleaned_text[::-1]

def fibonacci(n: int) -> int:
    """
    Zwraca n-ty element ciągu Fibonacciego.
    fibonacci(0) == 0, fibonacci(1) == 1.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return 0
    if n == 1:
        return 1
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def count_vowels(text: str) -> int:
    """
    Zlicza liczbę samogłosek w podanym ciągu (a, e, i, o, u, y – wielkość liter bez znaczenia).
    """    
    vowels = {'a', 'e', 'i', 'o', 'u', 'y', 'ą', 'ę', 'ó'}
    return sum(1 for char in text.lower() if char in vowels)

def calculate_discount(price: float, discount: float) -> float:
    """
    Zwraca cenę po uwzględnieniu zniżki.
    Jeśli discount jest spoza zakresu 0–1, ma zostać zgłoszony wyjątek ValueError.
    """
    if not (0 <= discount <= 1):
        raise ValueError("Discount must be between 0 and 1")
    return price * (1 - discount)

def flatten_list(nested_list: list) -> list:
    """
    Przyjmuje listę (mogącą zawierać zagnieżdżone listy) i zwraca ją „spłaszczoną”.
    """
    flat = []
    for item in nested_list:
        if isinstance(item, list):
            flat.extend(flatten_list(item))
        else:
            flat.append(item)
    return flat

def word_frequencies(text: str) -> dict:
    """
    Zwraca słownik z częstością występowania słów w tekście (ignorując wielkość liter i interpunkcję).
    """    
    words = re.findall(r'\b\w+\b', text.lower())
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    return freq

def is_prime(n: int) -> bool:
    """
    Sprawdza, czy liczba jest pierwsza.
    Jeśli n < 2, zwraca False.
    """
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
