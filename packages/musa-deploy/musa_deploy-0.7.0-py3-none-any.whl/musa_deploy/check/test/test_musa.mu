#include <cmath>
#include <iostream>

__global__ void axpy(float* x, float* y, float a) {
  y[threadIdx.x] = a * x[threadIdx.x];
}

#define CHECK(call)                                                     \
do {                                                                    \
    const musaError_t error_code = call;                                \
    if (error_code != musaSuccess) {                                    \
        printf("MUSA Error:\n");                                        \
        printf("    Error code: %d\n", error_code);                     \
        printf("    Error text: %s\n", musaGetErrorString(error_code)); \
        return 1;                                                       \
    }                                                                   \
} while (0)

int main(int argc, char* argv[]) {
  bool isSuccess = true;
  const int kDataLen = 4;
  float a = 2.0f;
  float host_x[kDataLen] = {1.0f, 2.0f, 3.0f, 4.0f};
  float host_y[kDataLen];
  // Copy input data to device.
  float* device_x;
  float* device_y;
  CHECK(musaMalloc(&device_x, kDataLen * sizeof(float)));
  CHECK(musaMalloc(&device_y, kDataLen * sizeof(float)));
  CHECK(musaMemcpy(
      device_x, host_x, kDataLen * sizeof(float), musaMemcpyHostToDevice));
  // Launch the kernel.
  axpy<<<1, kDataLen>>>(device_x, device_y, a);
  musaError_t err = musaGetLastError();
  if (err != musaSuccess) {
      printf("MUSA Error: %s\n", musaGetErrorString(err));
      return 1;
  }
  // Copy output data to host.
  CHECK(musaDeviceSynchronize());
  CHECK(musaMemcpy(
      host_y, device_y, kDataLen * sizeof(float), musaMemcpyDeviceToHost));
  // Check the results.
  for (int i = 0; i < kDataLen; ++i) {
    if (std::fabs(host_y[i] - a * host_x[i]) > 1e-6) {
      isSuccess = false;
    }
  }
  if (isSuccess == false) {
    std::cout << "simple demo target value:" << a * host_x[0] << ","
              << a * host_x[1] << "," << a * host_x[2] << "," << a * host_x[3]
              << std::endl;
    std::cout << "simple demo calculated value:" << host_y[0] << ","
              << host_y[1] << "," << host_y[2] << "," << host_y[3] << std::endl;
  }
  CHECK(musaFree(device_x));
  CHECK(musaFree(device_y));
  CHECK(musaDeviceReset());
  if (isSuccess == false) {
    return 1;
  }
  return 0;
}
