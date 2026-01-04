
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>

int main(int argc, char *argv[]) {
    if (setgid(0) != 0) { perror("setgid"); return 1; }
    if (setuid(0) != 0) { perror("setuid"); return 1; }
    if (argc > 1) {
        execvp(argv[1], &argv[1]);
    } else {
        char *args[] = {"/bin/sh", NULL};
        execv("/bin/sh", args);
    }
    perror("exec");
    return 1;
}

