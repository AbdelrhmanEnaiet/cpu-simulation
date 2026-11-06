
from typing import List, Tuple

class Display:
    ROWS = 32 
    COLUMNS = 64
    def _compute_pixel(self, x, y) ->Tuple[int, int]:
        
        word_idx =  y*4 + x//16
        bit = 15 - x%16
        return word_idx, bit
    def pixels(self, words_array: List[int])->List[List[bool]]:
        pixel_matrix = []
        for y in range(0, self.ROWS):
            pixel_row = []
            for x in range(0, self.COLUMNS):  
                word_idx, bit = self._compute_pixel(x, y)
                word = words_array[word_idx]
                activation_status = bool(word & (2**bit))
                pixel_row.append(activation_status)
            pixel_matrix.append(pixel_row)
        return pixel_matrix
