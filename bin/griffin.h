#ifndef GRIFFIN_H
#define GRIFFIN_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

enum griffin_level {
  GRIFFIN_AUTO = 0,  /* Auto-select best strategy per image (default) */
  GRIFFIN_FAST = 1,  /* Fastest encode */
  GRIFFIN_BEST = 2,  /* Best compression */
};

int griffin_encode_max_size(int width, int height);

int griffin_encode(const uint8_t* rgba, int width, int height, uint8_t* out, int out_capacity);

int griffin_read_header(const uint8_t* data, int size, int* width, int* height);

int griffin_decode(const uint8_t* data, int size, uint8_t* rgba, int rgba_capacity);

/* Level-aware encode — pass a griffin_level value. */
int griffin_encode_level(const uint8_t* rgba, int width, int height, uint8_t* out, int out_capacity, int level);

/* Timed variants — same as above but write the native codec time (seconds)
   to *elapsed_seconds, excluding any caller-side overhead. */
int griffin_encode_timed(
    const uint8_t* rgba, int width, int height, uint8_t* out, int out_capacity, double* elapsed_seconds);
int griffin_encode_level_timed(
    const uint8_t* rgba, int width, int height, uint8_t* out, int out_capacity, int level, double* elapsed_seconds);
int griffin_decode_timed(const uint8_t* data, int size, uint8_t* rgba, int rgba_capacity, double* elapsed_seconds);

#ifdef __cplusplus
}
#endif

#endif
