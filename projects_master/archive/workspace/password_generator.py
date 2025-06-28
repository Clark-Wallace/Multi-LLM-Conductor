import random
import string
import secrets
import re
import math
import argparse
from typing import List, Tuple, Optional


class PasswordGenerator:
    """Advanced password generator with multiple features and security options."""
    
    def __init__(self):
        self.password_history = []
        self.word_list = [
            "correct", "horse", "battery", "staple", "purple", "monkey", 
            "dishwasher", "dragon", "hammer", "laptop", "mountain", "river",
            "sunset", "coffee", "phoenix", "thunder", "crystal", "nebula",
            "quantum", "velocity", "spectrum", "galaxy", "electron", "photon"
        ]
        self.ambiguous_chars = "0O1lI"
        
    def calculate_entropy(self, password: str, charset_size: int) -> float:
        """Calculate password entropy in bits."""
        return len(password) * math.log2(charset_size)
    
    def check_password_strength(self, password: str) -> Tuple[str, int]:
        """Check password strength and return rating with score."""
        score = 0
        feedback = []
        
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
            
        if re.search(r'[a-z]', password):
            score += 1
        else:
            feedback.append("Add lowercase letters")
            
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            feedback.append("Add uppercase letters")
            
        if re.search(r'\d', password):
            score += 1
        else:
            feedback.append("Add numbers")
            
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', password):
            score += 1
        else:
            feedback.append("Add special characters")
            
        if len(set(password)) / len(password) > 0.7:
            score += 1
        else:
            feedback.append("Avoid repeating characters")
            
        common_patterns = ['123', 'abc', 'password', 'qwerty', '111']
        if not any(pattern in password.lower() for pattern in common_patterns):
            score += 1
        else:
            feedback.append("Avoid common patterns")
            
        strength_levels = {
            (0, 3): ("Weak", feedback),
            (3, 5): ("Fair", feedback),
            (5, 7): ("Good", feedback),
            (7, 9): ("Strong", feedback),
            (9, 10): ("Very Strong", [])
        }
        
        for (min_score, max_score), (level, _) in strength_levels.items():
            if min_score <= score < max_score:
                return level, score
                
        return "Very Strong", score
    
    def generate_password(self, length: int = 12, include_uppercase: bool = True,
                         include_lowercase: bool = True, include_digits: bool = True,
                         include_symbols: bool = True, exclude_ambiguous: bool = False,
                         ensure_all_types: bool = True) -> str:
        """Generate a random password with specified criteria."""
        characters = ""
        char_types = []
        
        if include_uppercase:
            chars = string.ascii_uppercase
            if exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in self.ambiguous_chars)
            characters += chars
            char_types.append(chars)
            
        if include_lowercase:
            chars = string.ascii_lowercase
            if exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in self.ambiguous_chars)
            characters += chars
            char_types.append(chars)
            
        if include_digits:
            chars = string.digits
            if exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in self.ambiguous_chars)
            characters += chars
            char_types.append(chars)
            
        if include_symbols:
            characters += string.punctuation
            char_types.append(string.punctuation)
            
        if not characters:
            raise ValueError("At least one character type must be included")
            
        if ensure_all_types and len(char_types) > 1 and length >= len(char_types):
            password_chars = []
            for char_type in char_types:
                password_chars.append(secrets.choice(char_type))
            
            remaining_length = length - len(password_chars)
            password_chars.extend(secrets.choice(characters) for _ in range(remaining_length))
            
            secrets.SystemRandom().shuffle(password_chars)
            password = ''.join(password_chars)
        else:
            password = ''.join(secrets.choice(characters) for _ in range(length))
            
        self.password_history.append(password)
        return password
    
    def generate_pronounceable(self, length: int = 12) -> str:
        """Generate a pronounceable password using alternating consonants and vowels."""
        consonants = 'bcdfghjklmnpqrstvwxyz'
        vowels = 'aeiou'
        digits = '0123456789'
        symbols = '!@#$%'
        
        password = []
        
        for i in range(length - 4):
            if i % 2 == 0:
                char = secrets.choice(consonants)
            else:
                char = secrets.choice(vowels)
            
            if secrets.randbelow(3) == 0:
                char = char.upper()
                
            password.append(char)
            
        password.extend([
            secrets.choice(digits),
            secrets.choice(digits),
            secrets.choice(symbols),
            secrets.choice(symbols)
        ])
        
        secrets.SystemRandom().shuffle(password)
        result = ''.join(password)
        
        self.password_history.append(result)
        return result
    
    def generate_passphrase(self, word_count: int = 4, separator: str = '-',
                           capitalize: bool = True, add_number: bool = True) -> str:
        """Generate a passphrase using random words."""
        words = []
        
        for _ in range(word_count):
            word = secrets.choice(self.word_list)
            if capitalize:
                word = word.capitalize()
            words.append(word)
            
        passphrase = separator.join(words)
        
        if add_number:
            passphrase += separator + str(secrets.randbelow(100))
            
        self.password_history.append(passphrase)
        return passphrase
    
    def generate_pattern_based(self, pattern: str) -> str:
        """Generate password based on pattern.
        Pattern symbols:
        - L: uppercase letter
        - l: lowercase letter
        - d: digit
        - s: symbol
        - *: any character
        Example: "LLll-dddd-ss" generates "ABcd-1234-!@"
        """
        password = []
        
        for char in pattern:
            if char == 'L':
                password.append(secrets.choice(string.ascii_uppercase))
            elif char == 'l':
                password.append(secrets.choice(string.ascii_lowercase))
            elif char == 'd':
                password.append(secrets.choice(string.digits))
            elif char == 's':
                password.append(secrets.choice(string.punctuation))
            elif char == '*':
                password.append(secrets.choice(string.ascii_letters + string.digits + string.punctuation))
            else:
                password.append(char)
                
        result = ''.join(password)
        self.password_history.append(result)
        return result
    
    def get_recent_passwords(self, count: int = 10) -> List[str]:
        """Get recent password history."""
        return self.password_history[-count:]
    
    def clear_history(self):
        """Clear password history."""
        self.password_history = []


def main():
    parser = argparse.ArgumentParser(description='Advanced Password Generator')
    parser.add_argument('-l', '--length', type=int, default=16,
                       help='Password length (default: 16)')
    parser.add_argument('-t', '--type', choices=['standard', 'pronounceable', 'passphrase', 'pattern'],
                       default='standard', help='Password type')
    parser.add_argument('--no-uppercase', action='store_true', help='Exclude uppercase letters')
    parser.add_argument('--no-lowercase', action='store_true', help='Exclude lowercase letters')
    parser.add_argument('--no-digits', action='store_true', help='Exclude digits')
    parser.add_argument('--no-symbols', action='store_true', help='Exclude symbols')
    parser.add_argument('--exclude-ambiguous', action='store_true', 
                       help='Exclude ambiguous characters (0O1lI)')
    parser.add_argument('--pattern', type=str, help='Pattern for pattern-based generation')
    parser.add_argument('--words', type=int, default=4, help='Number of words for passphrase')
    parser.add_argument('--check', type=str, help='Check password strength')
    parser.add_argument('-n', '--count', type=int, default=1, 
                       help='Number of passwords to generate')
    
    args = parser.parse_args()
    
    generator = PasswordGenerator()
    
    if args.check:
        strength, score = generator.check_password_strength(args.check)
        print(f"Password: {args.check}")
        print(f"Strength: {strength} (Score: {score}/9)")
        return
    
    for i in range(args.count):
        if args.type == 'standard':
            password = generator.generate_password(
                length=args.length,
                include_uppercase=not args.no_uppercase,
                include_lowercase=not args.no_lowercase,
                include_digits=not args.no_digits,
                include_symbols=not args.no_symbols,
                exclude_ambiguous=args.exclude_ambiguous
            )
        elif args.type == 'pronounceable':
            password = generator.generate_pronounceable(length=args.length)
        elif args.type == 'passphrase':
            password = generator.generate_passphrase(word_count=args.words)
        elif args.type == 'pattern' and args.pattern:
            password = generator.generate_pattern_based(args.pattern)
        else:
            print("Pattern type requires --pattern argument")
            return
            
        print(f"Password {i+1}: {password}")
        
        strength, score = generator.check_password_strength(password)
        print(f"Strength: {strength} (Score: {score}/9)")
        
        charset_size = 0
        if not args.no_uppercase:
            charset_size += 26
        if not args.no_lowercase:
            charset_size += 26
        if not args.no_digits:
            charset_size += 10
        if not args.no_symbols:
            charset_size += 32
            
        if charset_size > 0:
            entropy = generator.calculate_entropy(password, charset_size)
            print(f"Entropy: {entropy:.2f} bits")
        
        print()


if __name__ == "__main__":
    main()