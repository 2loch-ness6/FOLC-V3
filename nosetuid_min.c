#define _GNU_SOURCE
#include <unistd.h>
#include <sys/types.h>
#include <errno.h>
#include <sys/prctl.h>
#include <stdarg.h>

// Intercept setuid family
int setuid(uid_t uid) { return 0; }
int setgid(gid_t gid) { return 0; }
int seteuid(uid_t uid) { return 0; }
int setegid(gid_t gid) { return 0; }
int setreuid(uid_t ruid, uid_t euid) { return 0; }
int setregid(gid_t rgid, gid_t egid) { return 0; }
int setresuid(uid_t ruid, uid_t euid, uid_t suid) { return 0; }
int setresgid(gid_t rgid, gid_t egid, gid_t sgid) { return 0; }
int setgroups(size_t size, const gid_t *list) { return 0; }
int capset(void *header, void *data) { return 0; }

// Intercept prctl
int prctl(int option, ...) {
    // Always succeed, never drop anything
    return 0;
}