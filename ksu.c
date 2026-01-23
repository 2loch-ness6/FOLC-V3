#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <string.h>

int main(int argc, char *argv[]) {
    if (setgid(0) != 0) { perror("setgid"); return 1; }
    if (setuid(0) != 0) { perror("setuid"); return 1; }
    
    if (argc > 1) {
        if (strcmp(argv[1], "-c") == 0 && argc > 2) {
            // Handle "su -c 'command'"
            char *args[] = {"/bin/sh", "-c", argv[2], NULL};
            execv("/bin/sh", args);
        } else {
            // Handle "su command args..."
            execvp(argv[1], &argv[1]);
        }
    } else {
        // Handle "su" (spawn root shell)
        char *args[] = {"/bin/sh", NULL};
        execv("/bin/sh", args);
    }
    perror("exec");
    return 1;
}