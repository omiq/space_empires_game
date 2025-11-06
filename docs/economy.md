# space_empires.economy

Simulates markets, goods, and trading operations.

```python
"""space_empires.economy"""
import random
from dataclasses import dataclass, field

@dataclass
class Good:
    name: str
    base_price: float
    quantity: int

@dataclass
class Market:
    goods: dict[str, Good] = field(default_factory=dict)

    def fluctuate(self):
        for good in self.goods.values():
            change = random.uniform(-0.1, 0.1)
            good.base_price = max(1, good.base_price * (1 + change))

def generate_market() -> Market:
    items = ["food", "metals", "fuel", "technology"]
    return Market({name: Good(name, random.randint(10, 100), random.randint(5, 50)) for name in items})

def trade_buy(agent, market: Market, good: str, amount: int):
    item = market.goods[good]
    total_cost = amount * item.base_price
    if agent.credits >= total_cost and item.quantity >= amount:
        agent.credits -= total_cost
        agent.cargo[good] = agent.cargo.get(good, 0) + amount
        item.quantity -= amount
```
