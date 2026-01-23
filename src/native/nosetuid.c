#define _GNU_SOURCE
#include <unistd.h>
#include <sys/types.h>
#include <stdio.h>

typedef int (*setuid_t)(uid_t);
typedef int (*setgid_t)(gid_t);

// Override setuid
int setuid(uid_t uid) {
    // Always return success (0)
    // Do NOT actually change UID unless it's 0 (which is fine)
    // If adbd tries to drop to 2000, we ignore it.
    return 0;
}

int setgid(gid_t gid) {
    return 0;
}

int setgroups(size_t size, const gid_t *list) {
    return 0;
}

int setresuid(uid_t r, uid_t e, uid_t s) {
    return 0;
}

int setresgid(gid_t r, gid_t e, gid_t s) {
    return 0;
}

// Hook capset to prevent dropping capabilities if adbd tries to
// Prototype: int capset(cap_user_header_t hdrp, const cap_user_data_t datap);
// We use void* to avoid header dependencies
int capset(void *hdrp, const void *datap) {
    return 0;
}
