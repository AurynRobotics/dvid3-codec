#ifndef PEGASUS_H
#define PEGASUS_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

int pegasus_encode_max_size(int width, int height);

int pegasus_encode(const uint8_t* rgba, int width, int height, uint8_t* out, int out_capacity);

int pegasus_read_header(const uint8_t* data, int size, int* width, int* height);

int pegasus_decode(const uint8_t* data, int size, uint8_t* rgba, int rgba_capacity);

/* Timed variants — same as above but write the native codec time (seconds)
   to *elapsed_seconds, excluding any caller-side overhead. */
int pegasus_encode_timed(
    const uint8_t* rgba, int width, int height, uint8_t* out, int out_capacity, double* elapsed_seconds);
int pegasus_decode_timed(const uint8_t* data, int size, uint8_t* rgba, int rgba_capacity, double* elapsed_seconds);

#ifdef __cplusplus
}
#endif

#endif
