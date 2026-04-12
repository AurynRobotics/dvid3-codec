#ifndef GRIFFIN_H
#define GRIFFIN_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

int griffin_encode_max_size(int width, int height);

int griffin_encode(const uint8_t* rgba, int width, int height, uint8_t* out, int out_capacity);

int griffin_read_header(const uint8_t* data, int size, int* width, int* height);

int griffin_decode(const uint8_t* data, int size, uint8_t* rgba, int rgba_capacity);

/* Timed variants — same as above but write the native codec time (seconds)
   to *elapsed_seconds, excluding any caller-side overhead. */
int griffin_encode_timed(
    const uint8_t* rgba, int width, int height, uint8_t* out, int out_capacity, double* elapsed_seconds);
int griffin_decode_timed(const uint8_t* data, int size, uint8_t* rgba, int rgba_capacity, double* elapsed_seconds);

#ifdef __cplusplus
}
#endif

#endif
