#include <cstring>

#include "Feature.hpp"

extern "C" {
#include <pbm.h>
}


Feature::Feature(const char* _filename)
{
  filename = strcpy(new char[std::strlen(_filename)+1], _filename);
  FILE* infile = fopen(filename, "rb");
  bit** bits = pbm_readpbm(infile, &cols, &rows);
  fclose(infile);
  cols32 = (cols + 31) / 32;
  right_mask = static_cast<unsigned int>(-1) << (32 - (cols % 32));
  // fprintf(stderr, "width %d height %d mask %x\n", cols, rows, right_mask);

  integers = new unsigned int[cols32 * rows];
  for (int y = 0; y < rows; y++) {
    int index = 0;
    for (int x = 0; x < cols32; x++) {
      int i = 0;
      for (int b = 0; b < 32; b++) {
	i = i << 1;
	if (index < cols && bits[y][index]) i++;
	index++;
      }
      integers[x + y * cols32] = i;
    }
  }
  pbm_freearray(bits, rows);
  /*
  fprintf(stderr, "%dx%d %s\n%x %x\n%x %x\n%x %x\n", cols, rows, filename,
	  integers[(rows - 3) * cols32], integers[(rows - 3) * cols32 + 1],
	  integers[(rows - 2) * cols32], integers[(rows - 2) * cols32 + 1],
	  integers[(rows - 1) * cols32], integers[(rows - 1) * cols32 + 1]);
  */
  if (getBottomLeft() == 0) {
    fprintf(stderr, "WARNING: bottom left in %s is zero\n", filename);
  }
}


Feature::~Feature()
{
  delete[] integers;
}


unsigned int Feature::getBottomLeft()
{
  return integers[(rows - 1) * cols32];
}


bool Feature::match(unsigned int input[][32][COLS32], int cycle_rows,
		    int offset, int column, int y)
{
  for (int row = 0; row < rows; row++) {
    int row_y = y - rows + row + 1;
    for (int col = 0; col < cols32; col++) {
      int i = input[row_y % cycle_rows][offset][column + col];
      if (col == cols32 - 1) i &= right_mask;
      if (i != integers[col + row * cols32]) return false;
    }
  }
  return true;
}
