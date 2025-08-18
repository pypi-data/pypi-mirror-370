#!/usr/bin/python3

from PyQt5.QtCore import QSortFilterProxyModel, Qt

class CaseInsensitiveSortModel(QSortFilterProxyModel):
    def lessThan(self, left, right):
        # Comparação case-insensitive
        left_data = left.data(Qt.DisplayRole)
        right_data = right.data(Qt.DisplayRole)

        if isinstance(left_data, str) and isinstance(right_data, str):
            return left_data.lower() < right_data.lower()
        return left_data < right_data
