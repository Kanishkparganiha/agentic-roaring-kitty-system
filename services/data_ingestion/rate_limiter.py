"""
Token Bucket Rate Limiter


Example:
    limiter = TokenBucketRateLimiter(max_tokens=5, refill_rate=2)
    limiter.acquire()     # True - 4 tokens left
    limiter.acquire(3)    # True - 1 token left
    limiter.acquire(2)    # False - not enough!
    time.sleep(1)         # Wait, 2 new tokens added
    limiter.acquire(2)    # True - now we have enough
"""

import time


class TokenBucketRateLimiter:

    def __init__(self, max_tokens: int, refill_rate: float):
        """
        Initialize the rate limiter.

        Args:
            max_tokens: Maximum tokens the bucket can hold (burst capacity)
            refill_rate: Tokens added per second
        """
        self.max_tokens = max_tokens          # Jar capacity
        self.refill_rate = refill_rate        # Coins added per second
        self.tokens = max_tokens              # Start with full jar
        self.last_refill_time = time.time()   # Track last refill time

    def _refill(self):
        """
        Refill tokens based on time elapsed since last refill.

        Like mom adding coins to the jar every hour.
        """
        # How much time passed since last refill?
        now = time.time()
        time_elapsed = now - self.last_refill_time

        # Calculate new tokens (time * rate)
        new_tokens = time_elapsed * self.refill_rate

        # Add tokens but don't exceed max (jar can't overflow)
        self.tokens = min(self.max_tokens, self.tokens + new_tokens)

        # Update last refill time
        self.last_refill_time = now

    def acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens.

        Args:
            tokens: Number of tokens needed (default 1)

        Returns:
            True if tokens acquired, False if not enough tokens
        """
        # First, refill based on time passed
        self._refill()

        # Check if we have enough tokens
        if self.tokens >= tokens:
            self.tokens -= tokens  # Take the tokens
            return True            # Purchase allowed!
        else:
            return False           # Not enough coins, denied!


# Test the implementation
if __name__ == "__main__":
    print("Testing Token Bucket Rate Limiter")
    print("=" * 40)

    # Create limiter: max 5 tokens, refill 2 per second
    limiter = TokenBucketRateLimiter(max_tokens=5, refill_rate=2)

    # Test 1: Should allow first 5 requests
    print("\nTest 1: Burst of 5 requests")
    for i in range(5):
        result = limiter.acquire()
        print(f"  Request {i+1}: {'Allowed' if result else 'Denied'}")

    # Test 2: 6th request should be denied
    print("\nTest 2: 6th request (should be denied)")
    result = limiter.acquire()
    print(f"  Request 6: {'Allowed' if result else 'Denied'}")

    # Test 3: Wait 2 seconds, should allow more
    print("\nTest 3: Wait 2 seconds, then request 3 tokens")
    time.sleep(2)
    result = limiter.acquire(3)
    print(f"  Request for 3 tokens: {'Allowed' if result else 'Denied'}")

    print("\n" + "=" * 40)
    print("Tests complete!")
