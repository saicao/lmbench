/* Exercise actual permutations and pointer chains. Build without -DNDEBUG:
 * cc -std=gnu89 -O -Isrc tests/lat_mem_seed.c build/src/liblmbench_common.a -lm
 */
#include "bench.h"
#include <stdint.h>
#include <limits.h>

static uint64_t fingerprint(unsigned int seed, size_t len)
{
	struct mem_state state;
	char *p, *first;
	uint64_t hash = 1469598103934665603ULL;
	size_t i, off;
	char seed_text[32];
	memset(&state, 0, sizeof(state));
	state.width = 1;
	state.len = len;
	state.maxlen = 1024 * 1024;
	state.line = 64;
	state.pagesize = 4096;
	snprintf(seed_text, sizeof(seed_text), "%u", seed);
	assert(setenv("LMBENCH_SEED", seed_text, 1) == 0);
	thrash_initialize(0, &state);
	assert(state.initialized);
	first = p = state.p[0];
	for (i = 0; i < len / 64; ++i) {
		assert(p >= state.base && p < state.base + state.maxlen);
		off = (size_t)(p - state.base);
		assert(off % 64 == 0);
		hash = (hash ^ off) * 1099511628211ULL;
		p = *(char **)p;
		assert(p != first || i + 1 == len / 64);
	}
	assert(p == first);
	mem_cleanup(0, &state);
	return hash;
}

int main(void)
{
	unsigned int seeds[] = {0, 1, 2327, UINT_MAX};
	size_t i;
	uint64_t expected, other;
	pid_t pid;
	int status;
	for (i = 0; i < sizeof(seeds)/sizeof(seeds[0]); ++i) {
		expected = fingerprint(seeds[i], 65536);
		other = fingerprint(seeds[i] ^ 0x12345678U, 65536);
		assert(other != expected);
		(void)fingerprint(seeds[i], 32768);
		assert(fingerprint(seeds[i], 65536) == expected);
		pid = fork();
		assert(pid >= 0);
		if (pid == 0) _exit(fingerprint(seeds[i], 65536) == expected ? 0 : 1);
		assert(waitpid(pid, &status, 0) == pid);
		assert(WIFEXITED(status) && WEXITSTATUS(status) == 0);
	}
	puts("PASS: env seed 0/max, distinct seeds, complete chains, scan order, PID independence");
	return 0;
}
