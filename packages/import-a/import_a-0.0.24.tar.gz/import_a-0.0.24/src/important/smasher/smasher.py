from typing import List, Tuple
import random

import numpy as np


class Smasher:
    """
    Some thing that can have people do pairwise comparison as label.
    
    smasher = Smasher(["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"])

    for i in range(20):
        item_id1, item_id2 = smasher.suggest()
        item1 = smasher[item_id1]
        item2 = smasher[item_id2]
        
        print(f"Which one is better? {item1} or {item2}")
        # collect the label
        better = input()
        
        # track the label
        self.judge(item_id1, item_id2, better)
        
    print(smasher.ordered_id)
    # this should be the same as
    print(smasher.score.argsort()[::-1])
    """
    def __init__(self, items:List[str],):
        self.items = items
        self.ordered_id = list(range(len(items)))
        self.score = np.arange(len(items))
        self.exist_pairs = set()
        self.scored = np.zeros(len(items), dtype=bool)
        self.records = []
        self.suggested_num = 0
        self.arange = np.arange(len(items))

    def __len__(self) -> int:
        return len(self.items)
    
    def __getitem__(self, index: int) -> str:
        return self.items[index]

    def judge(self, item_id1: int, item_id2: int, better: bool):
        self.exist_pairs.add((item_id1, item_id2))
        self.records.append([item_id1, item_id2, better])
        self.scored[item_id1] = True
        self.scored[item_id2] = True
        place_1 = self.ordered_id.index(item_id1)
        place_2 = self.ordered_id.index(item_id2)

        if better and place_1 > place_2:
            del self.ordered_id[place_1]
            self.ordered_id.insert(place_2, item_id1)
        
        if not better and place_1 < place_2:
            del self.ordered_id[place_2]
            self.ordered_id.insert(place_1, item_id2)

        self.set_score()

    @property
    def linear_random_weights(self) -> np.ndarray:
        weights = np.zeros(len(self))
        weights[self.score.argsort()] = (
            np.arange(len(self))
            / np.sum(np.arange(len(self)))
            )
        return weights

    def random_suggest(self) -> Tuple[int, int]:
        return tuple(list(random.choices(self.arange, k=2)))

    def mixing_suggest(self) -> Tuple[int, int]:
        item_id1 = random.choice(self.arange[self.scored])
        item_id2 = random.choice(self.arange[~self.scored])
        return item_id1, item_id2

    def adjust_suggest(self,) -> Tuple[int, int]:
        item_id1, item_id2 = np.random.choice(
            self.arange, 2,
            p=self.linear_random_weights,)
        return item_id1, item_id2

    def set_score(self):
        self.score[self.ordered_id] = np.arange(len(self))[::-1]

    def _suggest(self) -> Tuple[str, str]:
        self.suggested_num += 1
        
        if self.suggested_num < len(self):
            return self.random_suggest()
        elif not np.all(self.scored):
            return self.mixing_suggest()
        else:
            return self.adjust_suggest()

    def suggest(self, rec=0):
        item_id1, item_id2 = self._suggest()
        if (item_id1, item_id2) in self.exist_pairs:
            if rec > 100:
                raise StopIteration("Too many recursion")
            return self.suggest(rec+1)
        return item_id1, item_id2
    
    
class SmasherTester:
    """
    The wrapper to test the smasher.
    """
    def __init__(self, smasher: Smasher):
        self.smasher = smasher
        sample_size = len(smasher)
        self.items = np.random.rand(sample_size)
        self.right_order = np.argsort(self.items)[::-1]
        self.top_k_match = []

    def infer(self):
        items = self.smasher.suggest()
        if items is None:
            return False
        item_id1, item_id2 = items
        self.smasher.judge(item_id1, item_id2, self.items[item_id1] > self.items[item_id2])
        return True

    def mesaure_match(self) -> int:
        """
        Measure for the items and prediction,
        What's the top k match between them.
        And return the k where all top k are the same items.
        """
        target_order = np.argsort(self.items)[::-1]
        pred_order = np.argsort(self.smasher.score)[::-1]
        i = 0
        for i1, i2 in zip(target_order, pred_order):
            if i1 == i2:
                i += 1
            else:
                break
        return i

    def test(self, iters: int = 200):
        """
        Run iterations to label the smasher.
        """
        for i in range(iters):
            try:
                ongoing = self.infer()
            except StopIteration:
                print("Most of the items are judged")
                break
            self.top_k_match.append(self.mesaure_match())