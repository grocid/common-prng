#include <iostream>
#include <thread>
#include <ctype.h>
#include <time.h>
#include <string>

#include "cuda_runtime.h"

#define MIN     1000000
#define MAX     1000000000
#define TARGET  638101650

__global__ void brute_kernel(int *result, int offset) {
    int seed = blockIdx.x * blockDim.x + threadIdx.x + offset;
    if(seed >= (INT_MAX-1)) {
        return;
    }
    int i, j, s, val, randnum;
    int seedarray[56];
    s = 161803398 - seed;
    seedarray[55] = s;
    i = val = 1;
    while(i < 55) {
        j = 21 * i % 55;
        seedarray[j] = val;
        val = s - val;
        if(val < 0) val += INT_MAX;
        s = seedarray[j];
        i++;
    }
    for(i = 1; i < 4; i++) {
        for(j = 1; j < 56; j++) {
            seedarray[j] -= seedarray[1 + (j + 30) % 55];
            if(seedarray[j] < 0) seedarray[j] += INT_MAX;
        }
    }
    for(j = 1; j < 23; j++) {
        seedarray[j] -= seedarray[1 + (j + 30) % 55];
        if(seedarray[j] < 0) seedarray[j] += INT_MAX;
    }
    randnum = seedarray[1] - seedarray[22];
    if (randnum == INT_MAX) randnum--;
    if (randnum < 0) randnum += INT_MAX;
    double rr = randnum*(1.0 / INT_MAX);

    long range = (long)(MAX - MIN);
    if ((int)(rr * range) + MIN == TARGET) {
        *result = seed;
    }
}

int main(int argc, char* argv[]){
    unsigned long long brute_size = INT_MAX;
    unsigned int brute_blocks = 512, brute_threads = 512;

    int *d_result, *result = (int *)malloc(sizeof(int));
    memset(result, 0, sizeof(int));
    clock_t start_t = clock();
    cudaMalloc((void**) &d_result, sizeof(int));

    for(int i = 0; i < (brute_size/(brute_blocks*brute_threads))+1; i++) {
        brute_kernel<<<brute_blocks,brute_threads>>>(
            d_result, i *(brute_blocks*brute_threads));
        cudaMemcpy(result, d_result, sizeof(int), cudaMemcpyDeviceToHost);
        if(*result != 0){
            std::cout << "Seed found:\t" << *result << std::endl;
            cudaFree(d_result);
            clock_t total_t = (clock() - start_t);
            std::cout << "Elapsed Time:\t"
                      << (double)total_t/((double)CLOCKS_PER_SEC)
                      << " seconds" << std::endl;
            return 0;
        }
    }
    cudaFree(d_result);
    free(result);
}