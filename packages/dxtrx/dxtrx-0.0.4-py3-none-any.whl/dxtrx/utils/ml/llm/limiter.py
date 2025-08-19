import time
import asyncio
import tiktoken

from typing import List

from dxtrx.utils.ml.llm.domain import Message

class RateLimitManager:
    def __init__(
        self,
        tpm: int,
        rpm: int,
        rpd: int,
        model: str,
        window_seconds: int = 60,
        high_pressure_threshold: float = 0.9,
        soft_pressure_threshold: float = 0.75,
        base_sleep: float = 0.5,
        max_sleep: float = 10.0,
    ):
        self.tpm = tpm
        self.rpm = rpm
        self.rpd = rpd
        self.model = model
        self.window = window_seconds

        self.tokenizer = tiktoken.encoding_for_model(model)
        self.tokens_used = 0
        self.calls_made = 0
        self.last_reset = time.monotonic()
        self.lock = asyncio.Lock()

        self.high_pressure_threshold = high_pressure_threshold
        self.soft_pressure_threshold = soft_pressure_threshold
        self.base_sleep = base_sleep
        self.max_sleep = max_sleep

    def _reset_window_if_needed(self):
        now = time.monotonic()
        if now - self.last_reset > self.window:
            self.tokens_used = 0
            self.calls_made = 0
            self.last_reset = now

    def count_tokens(self, messages: List[Message], max_response_tokens: int = 0) -> int:
        tokens = 0
        for m in messages:
            tokens += len(self.tokenizer.encode(m.role))
            tokens += len(self.tokenizer.encode(m.content))
            tokens += 3  # Overhead per message
        tokens += 3  # Final reply priming
        tokens += max_response_tokens
        return tokens

    def pressure_level(self) -> float:
        """Return pressure as a float between 0.0 and 1.0 (maxed out)"""
        token_pressure = self.tokens_used / self.tpm
        rpm_pressure = self.calls_made / self.rpm
        return max(token_pressure, rpm_pressure)

    async def acquire(self, messages: List[Message], max_response_tokens: int = 0):
        tokens_needed = self.count_tokens(messages, max_response_tokens)

        while True:
            async with self.lock:
                self._reset_window_if_needed()

                now = time.monotonic()
                time_remaining = self.window - (now - self.last_reset)

                token_ok = self.tokens_used + tokens_needed <= self.tpm
                rpm_ok = self.calls_made + 1 <= self.rpm

                if token_ok and rpm_ok:
                    self.tokens_used += tokens_needed
                    self.calls_made += 1
                    return  # ✅ Proceed with request

                # System under pressure
                pressure = self.pressure_level()

                if pressure >= self.high_pressure_threshold:
                    sleep_time = max(self.base_sleep, time_remaining)
                elif pressure >= self.soft_pressure_threshold:
                    sleep_time = min(self.base_sleep * 4, self.max_sleep)
                else:
                    sleep_time = self.base_sleep

            print(f"⏳ Pressure {pressure*100:.1f}%, sleeping {sleep_time:.2f}s...")
            await asyncio.sleep(sleep_time)
