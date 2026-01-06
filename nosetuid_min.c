typedef unsigned int uid_t;
typedef unsigned int gid_t;
typedef unsigned int size_t;

int setuid(uid_t uid) { return 0; }
int setgid(gid_t gid) { return 0; }
int setgroups(size_t size, const gid_t *list) { return 0; }
int setresuid(uid_t r, uid_t e, uid_t s) { return 0; }
int setresgid(gid_t r, gid_t e, gid_t s) { return 0; }
int capset(void *hdrp, const void *datap) { return 0; }
