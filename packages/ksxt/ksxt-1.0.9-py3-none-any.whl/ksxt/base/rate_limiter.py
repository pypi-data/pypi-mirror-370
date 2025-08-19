from abc import ABC, abstractmethod
import asyncio
import time


class RateLimiterStrategy(ABC):
    @abstractmethod
    async def async_acquire(self):
        pass

    @abstractmethod
    def acquire(self):
        pass

    @abstractmethod
    def release(self):
        pass


class RateLimiterContext:
    def __init__(self, strategy: RateLimiterStrategy):
        self._strategy = strategy

    async def async_acquire(self):
        await self._strategy.async_acquire()

    def acquire(self):
        self._strategy.acquire()

    def release(self):
        self._strategy.release()


class RequestRateLimiter(RateLimiterStrategy):
    def __init__(self, max_requests: int, period: float = 1.0):
        self.max_requests = max_requests
        self.period = period
        self.semaphore = asyncio.BoundedSemaphore(max_requests)
        self.last_reset_time = time.time()

    async def async_acquire(self):
        current_time = time.time()
        if current_time - self.last_reset_time > self.period:
            self.semaphore = asyncio.BoundedSemaphore(self.max_requests)
            self.last_reset_time = current_time

        await self.semaphore.acquire()

    def acquire(self):
        current_time = time.time()
        if current_time - self.last_reset_time > self.period:
            # 동기식 세마포어는 지원되지 않으므로, 대신에 현재 상황을 조정합니다.
            self.last_reset_time = current_time

        # 세마포어가 동기식으로 동작하지 않으므로, 대신 제한 시간을 체크하여 동기식으로 제한
        while self.semaphore._value <= 0:  # 내부 값이 0 이하라면, 대기
            if time.time() - self.last_reset_time > self.period:
                self.semaphore = asyncio.BoundedSemaphore(self.max_requests)
                break
            time.sleep(0.01)  # 동기식 대기

        self.semaphore._value -= 1  # 수동으로 세마포어 값을 감소시킴

    def release(self):
        self.semaphore.release()


class TimeBasedRateLimiter(RateLimiterStrategy):
    def __init__(self, period: float):
        self.period = period
        self.last_request_time = None

    async def async_acquire(self):
        current_time = time.time()
        if self.last_request_time and (current_time - self.last_request_time) < self.period:
            raise ValueError("요청이 너무 자주 발생했습니다. 잠시 후에 다시 시도해주세요.")

        self.last_request_time = current_time

    def acquire(self):
        current_time = time.time()
        if self.last_request_time and (current_time - self.last_request_time) < self.period:
            raise ValueError("요청이 너무 자주 발생했습니다. 잠시 후에 다시 시도해주세요.")

        self.last_request_time = current_time

    def release(self):
        pass  # 이 클래스에서는 release가 필요하지 않음
