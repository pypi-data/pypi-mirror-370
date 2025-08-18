import random
import string

def generate_referral_code(length=8):
    """Generate a random referral code"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length)) 