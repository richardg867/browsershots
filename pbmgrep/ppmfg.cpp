#include <iostream>
#include <map>
#include <algorithm>
using namespace std;

extern "C" {
#include <ppm.h>
#include <pbm.h>
}

#define SQUARE_SIZE 12


void grayscale(pixel* input, char* gray, int pixels)
{
  for (int i = 0; i < pixels; i++) {
    gray[i] = char(PPM_LUMIN(input[i]));
  }
}


char most_frequent(std::map<char, int> counter)
{
  int max = 0;
  char result;
  std::map<char, int>::iterator iter;
  for (iter = counter.begin(); iter != counter.end(); iter++) {
    if ((*iter).second > max) {
      result = (*iter).first;
      max = (*iter).second;
    }
  }
  return result;
}


void foreground(pixel* input, bit* output,
		char* gray, int rows, int cols)
{
  std::map<char, int> counter;
  int x = 0;
  while (x < cols) {
    int rest = min(SQUARE_SIZE, cols - x);
    counter.clear();
    for (int y = 0; y < rows; y++) {
      int index = x + y * cols;
      for (int r = 0; r < rest; r++) {
	counter[gray[index]]++;
	index++;
      }
    }
    char most = most_frequent(counter);
    for (int y = 0; y < rows; y++) {
      int index = x + y * cols;
      for (int r = 0; r < rest; r++) {
	output[index] = gray[index] == most ? 0 : 1;
	index++;
      }
    }
    x += rest;
  }
}


int main(int argc, char* argv[])
{
  ppm_init(&argc, argv);
  pbm_init(&argc, argv);
  int cols;
  int rows;
  pixval maxval;
  int format;
  ppm_readppminit(stdin, &cols, &rows, &maxval, &format);
  pbm_writepbminit(stdout, cols, rows, 0);
  pixel* input = ppm_allocrow(cols * SQUARE_SIZE);
  bit* output = pbm_allocrow(cols * SQUARE_SIZE);
  char* gray = new char[cols * SQUARE_SIZE];
  int y = 0;
  while (y < rows) {
    // fprintf(stderr, "%d\r", y);
    int rest = min(SQUARE_SIZE, rows - y);
    ppm_readppmrow(stdin, input, cols * rest, maxval, format);
    grayscale(input, gray, cols * rest);
    foreground(input, output, gray, rest, cols);
    pbm_writepbmrow(stdout, output, cols * rest, 0);
    y += rest;
  }
  ppm_freerow(input);
  pbm_freerow(output);
  delete[] gray;
}
