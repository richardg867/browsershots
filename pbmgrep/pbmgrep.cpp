#include <map>
#include <algorithm>
using namespace std;

#include "Feature.hpp"

extern "C" {
#include <pbm.h>
}

#define BOTTOM_ROWS 8


void read_integers(bit* input, unsigned int integers[32][COLS32], int cols)
{
  unsigned int i = 0;
  for (int x = 0; x < 31; x++) {
    i = i << 1;
    if (input[x]) i++;
  }
  int offset = 0;
  int col = 0;
  for (int x = 31; x < cols; x++) {
    i = i << 1;
    if (input[x]) i++;
    integers[offset][col] = i;
    if (offset < 31) {
      offset++;
    } else {
      offset = 0;
      col++;
    }
  }
}


int main(int argc, char* argv[])
{
  pbm_init(&argc, argv);
  if (argc < 2) {
    fprintf(stderr, "usage: pbmgrep <feature.pbm> ...\n");
    return 1;
  }
  typedef std::multimap<unsigned int, Feature*> FeatureMap;
  typedef FeatureMap::const_iterator MapIter;
  FeatureMap features;
  int cycle_rows = BOTTOM_ROWS;
  for (int i = 1; i < argc; i++) {
    Feature* feature = new Feature(argv[i]);
    unsigned int bottom_left = feature->getBottomLeft();
    features.insert(std::pair<unsigned int, Feature*>(bottom_left, feature));
    cycle_rows = max(cycle_rows, feature->rows);
  }
  // fprintf(stderr, "features %d\n", features.size());
  // fprintf(stderr, "cycle_rows %d \n", cycle_rows);

  int cols;
  int rows;
  int format;
  pbm_readpbminit(stdin, &cols, &rows, &format);
  if (cols > MAX_WIDTH) {
    fprintf(stderr, "image is too wide (%d > %d pixels)\n", cols, MAX_WIDTH);
    return 2;
  }
  const int cols32 = cols / 32;
  unsigned int integers[cycle_rows][32][COLS32];
  bit* input = pbm_allocrow(cols);

  unsigned int vertical[cols32];
  for (int column = 0; column < cols32; column++) {
    vertical[column] = 0;
  }
  bool pattern_background = true;
  bool left_background = true;
  bool right_background = true;

  for (int y = 0; y < rows; y++) {
    // fprintf(stderr, "%d\r", y);
    pbm_readpbmrow(stdin, input, cols, format);
    read_integers(input, integers[y % cycle_rows], cols);
    if (y >= 4 && pattern_background) {
      for (int column = 0; column < cols32; column++) {
	if (integers[y % cycle_rows][0][column] !=
	    integers[(y - 4) % cycle_rows][0][column]) {
	  pattern_background = false;
	  break;
	}
      }
    }
    if (y > 4 && y < rows - 40) { // Ignore task bar.
      for (int column = 0; column < cols32; column++) {
	vertical[column] |= integers[y % cycle_rows][0][column];
      }
      left_background = left_background and
	integers[y % cycle_rows][0][0] ==
	integers[(y - 4) % cycle_rows][0][0];
      right_background = right_background and
	integers[y % cycle_rows][0][cols32 - 1] ==
	integers[(y - 4) % cycle_rows][0][cols32 - 1];
    }
    for (int column = 0; column < cols32; column++) {
      for (int offset = 0; offset < 32; offset++) {
	unsigned int bottom_left = integers[y % cycle_rows][offset][column];
	if (!bottom_left) continue;
	MapIter found = features.find(bottom_left);
	if (found == features.end()) continue;
	std::pair<MapIter, MapIter> range = features.equal_range(bottom_left);
	// if (found != range.first) printf("features.find() is incorrect\n");
	for (MapIter iter = range.first; iter != range.second; iter++) {
	  Feature* feature = iter->second;
	  if (y >= feature->rows - 1 and column < cols32 - feature->cols32) {
	    if (feature->match(integers, cycle_rows, offset, column, y)) {
	      printf("%d\t%d\t%d\t%d\t%s\n",
		     offset + column * 32, y - feature->rows + 1,
		     feature->cols, feature->rows,
		     feature->filename);
	      return 1;
	    }
	    // printf("no match\n");
	  }
	}
      }
    }
  }
  pbm_freerow(input);

  bool totally_blank = rows > 40;
  for (int column = 0; column < cols32; column++) {
    if (vertical[column]) totally_blank = false;
  }
  if (totally_blank or pattern_background) {
    printf("%d\t%d\t%d\t%d\t%s\n", 0, 0, cols, rows,
	   "701_The_screen_is_blank.pbm");
    return 1;
  }
  if (rows > 40 and (vertical[0] == 0 or left_background)) {
    printf("%d\t%d\t%d\t%d\t%s\n", 0, 0, 32, rows,
	   "702_The_left_side_of_the_screen_is_blank.pbm");
    return 1;
  }
  if (rows > 40 and (vertical[cols32 - 1] == 0 or right_background)) {
    printf("%d\t%d\t%d\t%d\t%s\n", 32 * (cols32 - 1), 0, 32, rows,
	   "703_The_right_side_of_the_screen_is_blank.pbm");
    return 1;
  }
  // printf("%08x %08x ... %08x %08x\n",
  // vertical[0], vertical[1], vertical[cols32 - 2], vertical[cols32 - 1]);

  bool found_something = false;
  for (int y = rows - BOTTOM_ROWS; y < rows; y++) {
    for (int column = 0; column < cols32; column++) {
      switch (integers[y % cycle_rows][0][column]) {
      case 0x00000000:
      case 0x11111111:
      case 0x22222222:
      case 0x44444444:
      case 0x88888888:
      case 0x55555555:
      case 0xAAAAAAAA:
	break;
      default:
	found_something = true;
      }
      if (found_something) break;
    }
    if (found_something) break;
  }
  if (not found_something) {
    printf("%d\t%d\t%d\t%d\t%s\n", 0, rows - 4, cols, 4,
	   "704_The_bottom_of_the_screen_is_blank.pbm");
    return 1;
  }

  return 0;
}
