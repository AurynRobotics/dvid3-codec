#ifndef CHIMERA_H
#define CHIMERA_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

int chimera_encode_max_size(int width, int height);

/* Encode RGBA pixels to Chimera format (valid PNG).
   Returns encoded size, or 0 on failure.
   Fails for images with non-constant alpha. */
int chimera_encode(const uint8_t* rgba, int width, int height, uint8_t* out, int out_capacity);

/* Read width/height from a Chimera-encoded stream (PNG IHDR).
   Returns 1 on success, 0 on failure. */
int chimera_read_header(const uint8_t* data, int size, int* width, int* height);

int chimera_decode(const uint8_t* data, int size, uint8_t* rgba, int rgba_capacity);

/* Timed variants — same as above but write the native codec time (seconds)
   to *elapsed_seconds, excluding any caller-side overhead. */
int chimera_encode_timed(
    const uint8_t* rgba, int width, int height, uint8_t* out, int out_capacity, double* elapsed_seconds);
int chimera_decode_timed(const uint8_t* data, int size, uint8_t* rgba, int rgba_capacity, double* elapsed_seconds);

#ifdef __cplusplus
}
#endif

#endif
