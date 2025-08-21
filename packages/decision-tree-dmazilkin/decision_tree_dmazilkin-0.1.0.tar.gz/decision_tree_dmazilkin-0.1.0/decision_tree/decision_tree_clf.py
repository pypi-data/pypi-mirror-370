import pandas as pd
import numpy as np
from typing import Tuple, Union, Dict
from dataclasses import dataclass

class MyTreeClf:
    
    @dataclass
    class BestSplit:
        left: np.ndarray = None
        right: np.ndarray = None
        gain: int = 0
        sep: float = 0.0
        column: str = ''
        
    @dataclass 
    class FeatureImportance:
        feature_size: int = 0
        values: Dict[str, float] = None
        
    @dataclass 
    class Container:
        type: str
        ptr: Union['MyTreeClf.Node', 'MyTreeClf.Leaf']
        
    @dataclass
    class Node:
        sep: float = None
        column: Union[str, int] = None
        left: Union['MyTreeClf.Node', 'MyTreeClf.Leaf'] = None
        right: Union['MyTreeClf.Node', 'MyTreeClf.Leaf'] = None
        
    @dataclass 
    class Leaf:
        value: np.ndarray
    
    def __init__(self, max_depth: int = 5, min_samples_split: int = 2, max_leafs: int = 20, bins: Union[None, int] = None, criterion: str = 'entropy') -> None:
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_leafs = max_leafs if max_leafs > 1 else 2
        self.leafs_cnt = 0
        self._depth = 0
        self._expanded = 0
        self._tree: 'MyTreeClf.Container' = None
        self.bins = bins
        self.criterion = criterion
        self._heuristics = {
            'entropy' : self.calc_entropy,
            'gini': self.calc_gini,
        }
        self._fi = self.FeatureImportance()
        
    def __str__(self) -> str:
        return f"MyTreeClf class: max_depth={self.max_depth}, min_samples_split={self.min_samples_split}, max_leafs={self.max_leafs}"        
        
    def calc_entropy(self, y: pd.Series) -> float:
        entropy = 0
        labels_count = y.size
            
        for label in y.unique():
            proba = np.sum(y == label) / labels_count
            
            if proba != 0:
                entropy += -1 * proba * np.log2(proba)
            
        return entropy
    
    def calc_gini(self, y: pd.Series) -> float:
        gini = 1
        labels_count = y.size
            
        for label in y.unique():
            proba = np.sum(y == label) / labels_count
            
            if proba != 0:
                gini -=  proba ** 2 
            
        return gini
    
    def get_best_split(self, X: pd.DataFrame, y: pd.Series, hist: Dict[Union[str, int], np.ndarray]) -> Tuple[str, float, float, pd.DataFrame, pd.DataFrame]:
        best_split = self.BestSplit()
        
        for column in X.columns:
            attr: pd.Series = X[column].sort_values()
            unqiue_values: np.ndarray = attr.unique()
            
            if hist is not None and column in hist:
                separators = hist[column]['edges']
            else:
                separators = np.array([(unqiue_values[i] + unqiue_values[i + 1]) / 2 for i in range(unqiue_values.size - 1)])
            
            origin_metric = self._heuristics[self.criterion](y)
        
            for sep in separators:
                left, right = y[attr <= sep], y[attr > sep]
                left_metric = left.size / y.size * self._heuristics[self.criterion](left) if left is not None else 0
                right_metric = right.size / y.size * self._heuristics[self.criterion](right) if right is not None else 0
                gain = origin_metric - left_metric - right_metric
                                
                if gain > best_split.gain:
                    best_split.gain = gain
                    best_split.sep = sep
                    best_split.column = column
                    best_split.left = left
                    best_split.right = right
            
        return best_split
    
    def _is_leaf(self, y: pd. Series) -> bool:
        label_count = np.sum([y == 1])
        is_homogeneous = label_count == y.size or label_count == 0
        
        return y.size < self.min_samples_split or is_homogeneous
    
    def _is_expandable(self) -> bool:
        return self._expanded + 2 <= self.max_leafs
    
    def _build_tree(self, cntr: Union['MyTreeClf.Node', 'MyTreeClf.Leaf'], level: int, leafs_sum: float) -> None:
        if cntr.type == 'node':
            column = cntr.ptr.column if isinstance(cntr.ptr.column, str) else str(cntr.ptr.column)
            print((level - 1) * '\t' + column + ': ')
            print((level - 1) * '\t', end='')
            print(cntr.ptr.sep)
            print((level - 1) * '\t' + 'left:')
            leafs_sum += self._build_tree(cntr.ptr.left, level+1, 0)
            print((level - 1) * '\t' + 'right:')
            leafs_sum += self._build_tree(cntr.ptr.right, level+1, 0)
            
            return leafs_sum
        
        if cntr.type == 'leaf':
            print(level * '\t' + 'proba: ')
            print(level * '\t', end='')
            proba = np.sum(cntr.ptr.value == 1) / cntr.ptr.value.size
            print(proba)
            
            return proba
            
    def build_tree(self) -> float:
        leafs_sum = 0.0
        return self._build_tree(self._tree, 1, leafs_sum)
    
    def _create_leaf(self, y: pd.Series) -> 'MyTreeClf.Container':
        self.leafs_cnt += 1
        return self.Container(type='leaf', ptr=self.Leaf(value=y))
    
    def _update_fi(self, y: pd.Series, best_split: 'MyTreeClf.BestSplit') -> None:
        left = best_split.left.size / y.size * self._heuristics[self.criterion](best_split.left)
        right = best_split.right.size / y.size * self._heuristics[self.criterion](best_split.right)
        self._fi.values[str(best_split.column)] += y.size / self._fi.feature_size * (self._heuristics[self.criterion](y) - left - right)
    
    def _fit(self, X: pd.DataFrame, y: pd.Series, hist: Dict[Union[str, int], np.ndarray]) -> Union[Node, pd.Series]:
        if (self._depth < self.max_depth):
            if not self._is_leaf(y) and self._is_expandable():
                best_split: 'MyTreeClf.BestSplit' = self.get_best_split(X, y, hist)

                if best_split.left is not None and best_split.right is not None:
                    cntr = self.Container(type='node', ptr=self.Node(sep=best_split.sep, column=best_split.column))
                    self._update_fi(y, best_split)
                    self._expanded += 1

                    self._depth += 1
                    cntr.ptr.left = self._fit(X.loc[best_split.left.index], best_split.left, hist)
                    cntr.ptr.right = self._fit(X.loc[best_split.right.index], best_split.right, hist)
                    self._depth -= 1
                    
                    return cntr
                else:
                    return self._create_leaf(y)
            else:
                return self._create_leaf(y)
        else:
            return self._create_leaf(y)
        
    def _check_bins(self, X: pd.DataFrame) -> Dict[Union[str, int], Dict[int, np.ndarray]]:
        hist = dict()
        
        for column in X.columns:
            attr: pd.Series = X[column].sort_values()
            unqiue_values: np.ndarray = attr.unique()
            
            if unqiue_values.size - 1 > self.bins - 1:
                count, edges = np.histogram(attr, bins=self.bins)
                hist[column] = {'count': count, 'edges': edges}
                
        return hist if len(hist) > 0 else None
    
    def _prepare_fi(self, X: pd.DataFrame) -> None:
        self._fi.values = dict()
        self._fi.feature_size = X.shape[0]
        
        for feature in X.columns:
            self._fi.values[str(feature)] = 0.0
        
    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        hist: Dict[Union[str, int], Dict[int, np.ndarray]] = None
        
        if self.bins is not None:
            hist = self._check_bins(X)
        
        self._prepare_fi(X)
        self._tree = self._fit(X, y, hist)
        
    def _calc_proba(self, cntr: 'MyTreeClf.Container') -> float:
        return np.sum(cntr.ptr.value == 1) / cntr.ptr.value.size
        
    def _predict(self, X: pd.DataFrame, cntr: Union['MyTreeClf.Node', 'MyTreeClf.Leaf']) -> int:
        if cntr.type == 'leaf':
            proba = self._calc_proba(cntr)
            return 1 if proba > 0.5 else 0
        
        if cntr.type == 'node':
            if X[cntr.ptr.column] <= cntr.ptr.sep and cntr.ptr.left is not None:
                return self._predict(X, cntr.ptr.left)
            if X[cntr.ptr.column] > cntr.ptr.sep and cntr.ptr.right is not None:
                return self._predict(X, cntr.ptr.right)
                    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        dataset = X.reset_index(drop=True)
        labels = np.zeros(dataset.shape[0], dtype='int')
        
        for index, row in dataset.iterrows():
            labels[index] = self._predict(row, self._tree)
        
        return labels
    
    def _predict_proba(self, X: pd.DataFrame, cntr: Union['MyTreeClf.Node', 'MyTreeClf.Leaf']) -> float:
        if cntr.type == 'leaf':
            return self._calc_proba(cntr)
        
        if cntr.type == 'node':
            if X[cntr.ptr.column] <= cntr.ptr.sep and cntr.ptr.left is not None:
                return self._predict_proba(X, cntr.ptr.left)
            if X[cntr.ptr.column] > cntr.ptr.sep and cntr.ptr.right is not None:
                return self._predict_proba(X, cntr.ptr.right)
            
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        dataset = X.reset_index(drop=True)
        labels_proba = np.zeros(dataset.shape[0], dtype='float')
        
        for index, row in dataset.iterrows():
            labels_proba[index] = self._predict_proba(row, self._tree)
        
        return labels_proba