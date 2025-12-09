import asyncio


class DeterministicAsyncWrapper:
    """Wrapper za deterministične async operacije"""
    
    def __init__(self):
        self.execution_order = []
        self.deterministic_mode = True
    
    async def execute_deterministic(self, coro, order_id: int):
        """Izvedi async operacijo deterministično"""
        if self.deterministic_mode:
            # Počakaj na pravilni vrstni red
            while len(self.execution_order) != order_id:
                await asyncio.sleep(0.001)
        
        result = await coro
        self.execution_order.append(order_id)
        return result
