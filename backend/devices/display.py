
from typing import List, Tuple
from backend.memory.bus import Bus


class Display:
    ROWS = 32 
    COLUMNS = 64
    def _compute_pixel(self, x, y) ->Tuple[int, int]:
        
        word_idx =  y*4 + x//16
        bit = 15 - x%16
        return word_idx, bit
    def pixels(self, words_array: List[int])->List[List[bool]]:
        pixel_matrix = []
        for x in range(0, 64):
            pixel_row = []
            for y in range(0, 32):  
                word_idx, bit = self._compute_pixel(x, y)
                word = words_array[word_idx]
                activation_status = bool(word & (2**bit))
                # print(word)
                pixel_row.append(activation_status)
            pixel_matrix.append(pixel_row)
        return pixel_matrix
